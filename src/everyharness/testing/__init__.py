"""Contract test helpers for plugin authors."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from everyharness.plugin.protocols import (
    DetectorPlugin,
    HarnessPlugin,
    LoaderPlugin,
    ModelRef,
    TemplatePack,
    is_api_compatible,
)

__all__ = [
    "assert_detector_plugin",
    "assert_harness_plugin",
    "assert_loader_plugin",
    "assert_template_pack",
    "render_smoke",
]


def _sample_model() -> ModelRef:
    return ModelRef(id="test", uri="./fixtures/model.bin", kind="generic")


def assert_harness_plugin(plugin: HarnessPlugin) -> None:
    assert hasattr(plugin, "name") and isinstance(plugin.name, str)
    assert hasattr(plugin, "api_version") and isinstance(plugin.api_version, str)
    assert is_api_compatible(plugin.api_version), "api_version must match core major version"
    model = _sample_model()
    score = plugin.matches(model)
    assert isinstance(score, (int, float))
    code = plugin.run_cli(model, [])
    assert isinstance(code, int)
    plugin.templates()
    info = plugin.describe()
    assert info.kind == "harness"


def assert_loader_plugin(plugin: LoaderPlugin) -> None:
    assert hasattr(plugin, "name") and isinstance(plugin.name, str)
    assert is_api_compatible(plugin.api_version)
    assert isinstance(plugin.can_load("./model.bin"), (int, float))
    ref = plugin.load("./model.bin")
    assert isinstance(ref, ModelRef)
    assert plugin.describe().kind == "loader"


def assert_detector_plugin(plugin: DetectorPlugin) -> None:
    assert hasattr(plugin, "name") and isinstance(plugin.name, str)
    assert is_api_compatible(plugin.api_version)
    assert isinstance(plugin.score(_sample_model()), (int, float))
    assert plugin.describe().kind == "detector"


def assert_template_pack(pack: TemplatePack) -> None:
    assert hasattr(pack, "name") and isinstance(pack.name, str)
    assert is_api_compatible(pack.api_version)
    templates = pack.list_templates()
    assert isinstance(templates, list)
    assert pack.describe().kind in {"templates", "template"}


def render_smoke(pack: TemplatePack, dest: Path, vars: dict[str, Any] | None = None) -> Path:
    """Render a template pack into dest for smoke tests."""
    return pack.render(_sample_model(), dest, vars or {})
