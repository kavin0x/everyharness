"""Plugins and templates browser."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, Static, TabbedContent, TabPane

from everyharness.plugin.catalog import search_catalog
from everyharness.tui.panels.base import PanelBody, PanelHeader
from everyharness.tui.state import AppState


class PluginsPanel(Vertical):
    """Browse installed plugins, templates, and catalog entries."""

    DEFAULT_CSS = """
    PluginsPanel {
        height: 1fr;
    }

    PluginsPanel TabbedContent {
        height: 1fr;
        margin: 0 2;
    }

    PluginsPanel DataTable {
        height: 1fr;
    }

    PluginsPanel #catalog-search-row {
        height: auto;
        padding: 0 1 1 1;
    }

    PluginsPanel #catalog-search-row Input {
        width: 1fr;
    }

    PluginsPanel #catalog-detail {
        height: auto;
        padding: 1;
        color: $text-muted;
    }
    """

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state

    def compose(self) -> ComposeResult:
        yield PanelHeader("Plugins / Templates")
        with PanelBody(), TabbedContent():
            with TabPane("Installed", id="tab-installed"):
                yield DataTable(id="installed-table", zebra_stripes=True)
            with TabPane("Templates", id="tab-templates"):
                yield DataTable(id="templates-table", zebra_stripes=True)
            with TabPane("Catalog", id="tab-catalog"), Vertical():
                with Horizontal(id="catalog-search-row"):
                    yield Input(placeholder="Search catalog…", id="catalog-search")
                yield DataTable(id="catalog-table", zebra_stripes=True)
                yield Static("", id="catalog-detail")

    def on_mount(self) -> None:
        installed = self.query_one("#installed-table", DataTable)
        installed.add_columns("Kind", "Name", "Version", "Summary")

        templates = self.query_one("#templates-table", DataTable)
        templates.add_columns("Pack", "Template", "Description")

        catalog = self.query_one("#catalog-table", DataTable)
        catalog.add_columns("Name", "PyPI", "Kind", "Summary")

        self.refresh_plugins()
        self.refresh_templates()
        self.refresh_catalog("")

    def refresh_plugins(self) -> None:
        table = self.query_one("#installed-table", DataTable)
        table.clear()
        for info in self.state.host.all_plugin_info():
            table.add_row(info.kind, info.name, info.version, info.summary)
        broken = self.state.host.broken_plugins()
        for result in broken:
            if result.error:
                table.add_row(
                    result.group,
                    f"{result.name} [red]broken[/red]",
                    "—",
                    result.error,
                )
            elif result.warning:
                table.add_row(
                    result.group,
                    f"{result.name} [yellow]skipped[/yellow]",
                    "—",
                    result.warning,
                )

    def refresh_templates(self) -> None:
        table = self.query_one("#templates-table", DataTable)
        table.clear()
        for pack in self.state.host.templates:
            try:
                refs = pack.list_templates()
            except Exception as exc:
                table.add_row(pack.name, "—", f"Error: {exc}")
                continue
            if not refs:
                table.add_row(pack.name, "—", "No templates")
                continue
            for ref in refs:
                table.add_row(ref.pack, ref.name, ref.description)

    def refresh_catalog(self, query: str) -> None:
        table = self.query_one("#catalog-table", DataTable)
        table.clear()
        entries = search_catalog(query)
        for entry in entries:
            table.add_row(entry.name, entry.pypi_name, entry.kind, entry.summary)
        detail = self.query_one("#catalog-detail", Static)
        if not entries:
            detail.update("No catalog matches. Try everyharness plugin search <query> from CLI.")
        else:
            detail.update(
                f"{len(entries)} catalog entr{'y' if len(entries) == 1 else 'ies'}. "
                "Install via: everyharness plugin install <pypi-name>"
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "catalog-search":
            self.refresh_catalog(event.value)

    def on_show(self) -> None:
        self.refresh_plugins()
        self.refresh_templates()
