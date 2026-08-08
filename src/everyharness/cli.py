"""Typer CLI entry point."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from everyharness.agents import AGENT_IDS, prepare_ui_bridge
from everyharness.core.cache import prune_cache
from everyharness.core.config import is_offline
from everyharness.core.errors import EveryharnessError, OfflineError, RegistryError
from everyharness.core.registry import ModelRegistry
from everyharness.core.resolve import (
    load_model_ref,
    pick_harness,
    refine_kind,
    require_pickle_trust,
    resolve_for_run,
)
from everyharness.core.update import (
    check_for_update,
    current_version,
    fetch_latest_version,
    upgrade_command,
)
from everyharness.doctor import run_doctor
from everyharness.plugin import PluginHost
from everyharness.plugin.catalog import get_catalog_entry, search_catalog
from everyharness.plugin.init_scaffold import PluginKind, scaffold_plugin
from everyharness.plugin.protocols import TrainOpts
from everyharness.tui import launch_tui

app = typer.Typer(
    name="everyharness",
    help="everyharness — offline-first model harness platform",
    no_args_is_help=False,
    add_completion=False,
)
plugin_app = typer.Typer(help="Discover, install, and scaffold plugins.")
template_app = typer.Typer(help="List and apply harness templates.")
app.add_typer(plugin_app, name="plugin")
app.add_typer(template_app, name="template")

console = Console()


def _host() -> PluginHost:
    return PluginHost.discover()


@app.command("tui")
def tui_cmd() -> None:
    """Launch the Textual TUI."""
    launch_tui()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option("--version", "-V", help="Show version and exit."),
    ] = None,
) -> None:
    """Launch TUI when no subcommand is given."""
    if version:
        from everyharness import __version__

        console.print(f"everyharness {__version__}")
        raise typer.Exit(0)
    if ctx.invoked_subcommand is None:
        launch_tui()


@app.command("doctor")
def doctor_cmd() -> None:
    """Check install health, plugin entry points, and directories."""
    report = run_doctor()
    console.print(
        f"[bold]everyharness[/bold] {report.version} "
        f"(plugin API {report.plugin_api_version})"
    )
    console.print(f"Offline mode: {'yes' if report.offline else 'no'}")
    console.print(f"Config:  {report.config_dir}")
    console.print(f"Cache:   {report.cache_dir} ({report.cache_bytes} bytes)")
    console.print(f"Data:    {report.data_dir}")
    console.print(f"Plugins: {report.plugins_ok} loaded, {report.plugins_broken} broken")
    for warning in report.warnings:
        console.print(f"[yellow]warning[/yellow]: {warning}")
    for error in report.errors:
        console.print(f"[red]error[/red]: {error}")
    if report.errors:
        raise typer.Exit(1)


@app.command("add")
def add_cmd(
    ref: Annotated[str, typer.Argument(help="Model reference (path, URI, etc.)")],
    kind: Annotated[
        str | None,
        typer.Option("--type", "-t", help="Override detected kind."),
    ] = None,
    trust_pickle: Annotated[
        bool,
        typer.Option("--trust-pickle", help="Allow loading pickle/joblib models."),
    ] = False,
) -> None:
    """Add a model to the local registry."""
    try:
        require_pickle_trust(ref, trust_pickle)
        host = _host()
        model = load_model_ref(ref, host.loaders, kind=kind)
        resolved_kind = refine_kind(model, host.detectors) or kind
        registry = ModelRegistry()
        record = registry.add(
            model.uri,
            kind=resolved_kind,
            metadata=dict(model.metadata),
        )
    except (RegistryError, EveryharnessError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    console.print(
        f"Added model [cyan]{record.id}[/cyan] "
        f"({record.kind or 'unknown'}) -> {record.ref}"
    )


@app.command("list")
def list_cmd() -> None:
    """List registered models."""
    registry = ModelRegistry()
    table = Table("ID", "Ref", "Kind")
    for rec in registry.list():
        table.add_row(rec.id, rec.ref, rec.kind or "-")
    console.print(table)


@app.command("show")
def show_cmd(
    model_id: Annotated[str, typer.Argument(help="Registered model id")],
) -> None:
    """Show details for a registered model."""
    registry = ModelRegistry()
    record = registry.get(model_id)
    if record is None:
        console.print(f"[red]Unknown model id: {model_id}[/red]")
        raise typer.Exit(1)
    host = _host()
    model = record.to_model_ref()
    harness = pick_harness(model, host.harnesses)
    console.print(f"ID:      {record.id}")
    console.print(f"Ref:     {record.ref}")
    console.print(f"Kind:    {record.kind or '-'}")
    console.print(f"Harness: {harness.name}")
    if record.metadata:
        console.print(f"Meta:    {record.metadata}")


@app.command("rm")
def rm_cmd(
    model_id: Annotated[str, typer.Argument(help="Registered model id")],
) -> None:
    """Remove a model from the registry."""
    registry = ModelRegistry()
    if not registry.remove(model_id):
        console.print(f"[red]Unknown model id: {model_id}[/red]")
        raise typer.Exit(1)
    console.print(f"Removed [cyan]{model_id}[/cyan]")


@app.command("run")
def run_cmd(
    model_id: Annotated[str, typer.Argument(help="Registered model id")],
    args: Annotated[
        list[str] | None,
        typer.Argument(help="Arguments passed to the harness CLI."),
    ] = None,
    trust_pickle: Annotated[
        bool,
        typer.Option("--trust-pickle", help="Allow pickle/joblib model execution."),
    ] = False,
) -> None:
    """Run a model through its matching harness."""
    host = _host()
    try:
        model, harness = resolve_for_run(model_id, host)
        require_pickle_trust(model.uri, trust_pickle)
        argv = list(args or [])
        if trust_pickle and "--trust-pickle" not in argv:
            argv.append("--trust-pickle")
        code = harness.run_cli(model, argv)
    except (RegistryError, EveryharnessError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    raise typer.Exit(code)


@app.command("serve")
def serve_cmd(
    model_id: Annotated[str, typer.Argument(help="Registered model id")],
    host: Annotated[str, typer.Option("--host", help="Bind host.")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", "-p", help="Bind port.")] = 8000,
) -> None:
    """Serve a model via its harness HTTP endpoint."""
    plugin_host = _host()
    try:
        model, harness = resolve_for_run(model_id, plugin_host)
        harness.serve(model, host, port)
    except NotImplementedError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(1) from exc
    except (RegistryError, EveryharnessError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


@app.command("train")
def train_cmd(
    model_id: Annotated[str, typer.Argument(help="Registered model id")],
    dataset: Annotated[Path, typer.Argument(help="Training dataset path (.json/.jsonl)")],
    epochs: Annotated[int, typer.Option("--epochs", "-e", help="Training epochs.")] = 1,
    learning_rate: Annotated[
        float,
        typer.Option("--lr", help="Learning rate."),
    ] = 1e-4,
    method: Annotated[
        str | None,
        typer.Option("--method", "-m", help="Fine-tune method override."),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory."),
    ] = None,
) -> None:
    """Fine-tune a model when the harness supports it."""
    host = _host()
    try:
        model, harness = resolve_for_run(model_id, host)
        opts = TrainOpts(
            epochs=epochs,
            learning_rate=learning_rate,
            output_dir=output,
            extra={"method": method} if method else {},
        )
        result = harness.finetune(model, dataset, opts)
    except NotImplementedError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(1) from exc
    except (RegistryError, EveryharnessError, FileNotFoundError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    registry = ModelRegistry()
    record = registry.add(
        result.uri,
        kind=result.kind,
        metadata=dict(result.metadata),
    )
    console.print(f"Trained model saved as [cyan]{record.id}[/cyan] -> {record.ref}")


@app.command("cache")
def cache_cmd(
    prune: Annotated[bool, typer.Option("--prune", help="Remove empty cache directories.")] = False,
) -> None:
    """Inspect or prune the offline cache."""
    if prune:
        removed = prune_cache()
        console.print(f"Pruned {len(removed)} empty cache directories.")
    else:
        from everyharness.core.cache import get_cache_root

        console.print(f"Cache root: {get_cache_root()}")


@plugin_app.command("list")
def plugin_list() -> None:
    """List discovered plugins from entry points."""
    host = _host()
    table = Table("Kind", "Name", "Version", "Summary")
    for info in host.all_plugin_info():
        table.add_row(info.kind, info.name, info.version, info.summary)
    console.print(table)
    broken = host.broken_plugins()
    for result in broken:
        if result.error:
            console.print(f"[red]broken[/red] {result.group}/{result.name}: {result.error}")
        elif result.warning:
            console.print(
                f"[yellow]skipped[/yellow] {result.group}/{result.name}: {result.warning}"
            )


@plugin_app.command("search")
def plugin_search(query: Annotated[str, typer.Argument(help="Search query")]) -> None:
    """Search the curated plugin catalog (local index)."""
    if is_offline() and query.startswith("http"):
        console.print("[red]Online search blocked in offline mode.[/red]")
        raise typer.Exit(1)
    results = search_catalog(query)
    if not results:
        console.print("No catalog matches.")
        raise typer.Exit(0)
    table = Table("Name", "PyPI", "Kind", "Summary")
    for entry in results:
        table.add_row(entry.name, entry.pypi_name, entry.kind, entry.summary)
    console.print(table)


@plugin_app.command("info")
def plugin_info(name: Annotated[str, typer.Argument(help="Plugin or PyPI package name")]) -> None:
    """Show catalog metadata for a plugin."""
    entry = get_catalog_entry(name)
    if entry is None:
        console.print(f"No catalog entry for [cyan]{name}[/cyan].")
        raise typer.Exit(1)
    console.print(f"{entry.pypi_name} ({entry.kind})\n{entry.summary}")


@plugin_app.command("install")
def plugin_install(
    package: Annotated[str, typer.Argument(help="PyPI package name (e.g. everyharness-foo)")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation.")] = False,
) -> None:
    """Install a plugin package via pip."""
    if is_offline():
        console.print("[red]Plugin install blocked: EVERYHARNESS_OFFLINE=1[/red]")
        raise typer.Exit(1)
    if not yes:
        typer.confirm(f"Install {package} into the active environment?", abort=True)
    cmd = [sys.executable, "-m", "pip", "install", package]
    console.print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    console.print("Re-scan with: everyharness plugin list")


@plugin_app.command("init")
def plugin_init(
    name: Annotated[str, typer.Argument(help="Plugin short name (e.g. mymodel)")],
    kind: Annotated[
        PluginKind,
        typer.Option("--kind", "-k", help="Plugin kind to scaffold."),
    ] = "harness",
    dest: Annotated[
        Path,
        typer.Option("--dest", "-d", help="Destination directory.", dir_okay=True, writable=True),
    ] = Path("."),
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing scaffold.")] = False,
) -> None:
    """Scaffold a publishable everyharness-* plugin package."""
    try:
        package_dir = scaffold_plugin(name, kind, dest, force=force)
    except FileExistsError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    console.print(f"Scaffolded {kind} plugin at [cyan]{package_dir}[/cyan]")
    console.print("Next: pip install -e . && pytest")


@plugin_app.command("doctor")
def plugin_doctor() -> None:
    """Check plugin API compatibility and broken entry points."""
    doctor_cmd()


@template_app.command("list")
def template_list() -> None:
    """List available template packs."""
    host = _host()
    table = Table("Pack", "Template", "Description")
    for pack in host.templates:
        try:
            for ref in pack.list_templates():
                table.add_row(ref.pack, ref.name, ref.description)
        except Exception as exc:
            console.print(f"[yellow]warning[/yellow]: {pack.name}: {exc}")
    console.print(table)


@template_app.command("apply")
def template_apply(
    pack_name: Annotated[str, typer.Argument(help="Template pack name")],
    model_id: Annotated[str, typer.Option("--model", "-m", help="Registered model id")],
    out: Annotated[Path, typer.Option("--out", "-o", help="Output directory", dir_okay=True)],
    template: Annotated[str | None, typer.Option("--template", "-t", help="Template name")] = None,
) -> None:
    """Apply a template pack to a model."""
    registry = ModelRegistry()
    record = registry.get(model_id)
    if record is None:
        console.print(f"[red]Unknown model id: {model_id}[/red]")
        raise typer.Exit(1)
    model = record.to_model_ref()
    host = _host()
    pack = next((p for p in host.templates if p.name == pack_name), None)
    if pack is None:
        console.print(f"[red]Unknown template pack: {pack_name}[/red]")
        raise typer.Exit(1)
    vars: dict[str, object] = {}
    if template:
        vars["template_name"] = template
    dest = pack.render(model, out, vars)
    console.print(f"Rendered template to [cyan]{dest}[/cyan]")


@app.command("ui")
def ui_cmd(
    model_id: Annotated[str, typer.Argument(help="Registered model id")],
    agent: Annotated[
        str,
        typer.Option("--agent", "-a", help="Coding agent: cursor|claude|copilot|pi|codex"),
    ] = "cursor",
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Output directory (default: ./harness-ui/<id>)"),
    ] = None,
) -> None:
    """Generate a coding-agent prompt pack to scaffold a web/GUI wrapper."""
    if agent not in AGENT_IDS:
        console.print(f"[red]Unknown agent: {agent}[/red]")
        console.print(f"Choose from: {', '.join(AGENT_IDS)}")
        raise typer.Exit(1)

    registry = ModelRegistry()
    record = registry.get(model_id)
    if record is None:
        console.print(f"[red]Unknown model id: {model_id}[/red]")
        raise typer.Exit(1)

    model = record.to_model_ref()
    dest, status = prepare_ui_bridge(model, agent, dest=out)
    console.print(f"Wrote agent prompt pack to [cyan]{dest}[/cyan]")
    console.print("Files: AGENT_PROMPT.md, model-card.json, manifest.json, README.md")

    if status.available:
        console.print(f"Agent CLI detected: [green]{status.command}[/green]")
    else:
        console.print(f"[yellow]Agent CLI not found for {agent}[/yellow]")
        if status.notes:
            console.print(status.notes)
        console.print(f"Install hint: {status.install_hint}")


@app.command("update")
def update_cmd(
    check: Annotated[bool, typer.Option("--check", help="Only check for updates.")] = False,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Run pip upgrade without prompting."),
    ] = False,
) -> None:
    """Check PyPI (and GitHub Releases) for newer everyharness releases."""
    try:
        latest_known = fetch_latest_version()
        newer = check_for_update()
    except OfflineError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(0) from exc

    console.print(f"everyharness {current_version()} (installed)")
    if latest_known is None:
        console.print("[yellow]Could not reach PyPI or GitHub Releases.[/yellow]")
        raise typer.Exit(1)

    if newer is None:
        console.print(f"Up to date (latest: {latest_known}).")
        raise typer.Exit(0)

    console.print(f"Update available: [cyan]{newer}[/cyan]")
    cmd = upgrade_command(newer)
    if check:
        console.print(f"Upgrade with: {cmd}")
        raise typer.Exit(0)

    if yes:
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "everyharness"], check=True)
        console.print("Upgrade complete.")
    else:
        console.print(f"Run: {cmd}")


if __name__ == "__main__":
    app()
