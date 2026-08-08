"""Built-in CLI stub template pack."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from everyharness.plugin.protocols import PLUGIN_API_VERSION, ModelRef, PluginInfo, TemplateRef
from everyharness.plugin.templates import (
    load_template_manifest,
    render_template_pack,
    template_ref_from_manifest,
)


class CliStubTemplatePack:
    name = "cli-stub"
    api_version = PLUGIN_API_VERSION

    def __init__(self) -> None:
        self._root = Path(__file__).resolve().parent / "cli_stub"

    def list_templates(self) -> list[TemplateRef]:
        manifest = load_template_manifest(self._root)
        return template_ref_from_manifest(self.name, manifest)

    def render(self, model: ModelRef, dest: Path, vars: dict[str, Any]) -> Path:
        return render_template_pack(self._root, model=model, dest=dest, vars=vars)

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="templates",
            summary="Minimal CLI stub scaffold around a model.",
            requires_api=">=1,<2",
        )
