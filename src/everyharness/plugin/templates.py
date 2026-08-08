"""Built-in and plugin template rendering."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from everyharness.core.errors import TemplateError
from everyharness.plugin.protocols import ModelRef, TemplateRef


def load_template_manifest(pack_dir: Path) -> dict[str, Any]:
    manifest_path = pack_dir / "template.toml"
    if not manifest_path.exists():
        raise TemplateError(f"Missing template.toml in {pack_dir}")
    with manifest_path.open("rb") as fh:
        return tomllib.load(fh)


def render_template_pack(
    pack_dir: Path,
    *,
    model: ModelRef,
    dest: Path,
    vars: dict[str, Any] | None = None,
    template_name: str | None = None,
) -> Path:
    """Render a Jinja/TOML template pack into dest."""
    manifest = load_template_manifest(pack_dir)
    name = template_name or manifest.get("default_template", "main")
    templates_cfg = manifest.get("templates", {})
    if name not in templates_cfg:
        raise TemplateError(f"Unknown template '{name}' in pack {pack_dir.name}")

    dest.mkdir(parents=True, exist_ok=True)
    context: dict[str, Any] = {
        "model": model,
        "model_id": model.id,
        "model_uri": model.uri,
        "model_kind": model.kind or "unknown",
        **(vars or {}),
    }

    env = Environment(
        loader=FileSystemLoader(str(pack_dir)),
        autoescape=select_autoescape(enabled_extensions=()),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    for output_rel, template_rel in templates_cfg[name].items():
        template = env.get_template(str(template_rel))
        output_path = dest / output_rel
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(template.render(**context), encoding="utf-8")

    return dest


def template_ref_from_manifest(pack_name: str, manifest: dict[str, Any]) -> list[TemplateRef]:
    refs: list[TemplateRef] = []
    for tmpl_name, cfg in manifest.get("templates", {}).items():
        refs.append(
            TemplateRef(
                pack=pack_name,
                name=tmpl_name,
                description=str(cfg.get("description", "")) if isinstance(cfg, dict) else "",
            )
        )
    return refs
