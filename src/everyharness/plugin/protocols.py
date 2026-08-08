"""Public plugin SDK protocols and types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

PLUGIN_API_VERSION = "1.0.0"


@dataclass(frozen=True)
class ModelRef:
    """Reference to a model known to the registry or passed inline."""

    id: str
    uri: str
    kind: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PluginInfo:
    """Metadata returned by plugins for discovery and doctor."""

    name: str
    version: str
    api_version: str
    kind: str
    summary: str = ""
    requires_api: str | None = None


@dataclass(frozen=True)
class TemplateRef:
    """Reference to a template within a pack."""

    pack: str
    name: str
    description: str = ""


@dataclass(frozen=True)
class TrainOpts:
    """Fine-tune options (stub for later phases)."""

    epochs: int = 1
    learning_rate: float = 1e-4
    output_dir: Path | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class HarnessPlugin(Protocol):
    name: str
    api_version: str

    def matches(self, model: ModelRef) -> float: ...

    def run_cli(self, model: ModelRef, argv: list[str]) -> int: ...

    def serve(self, model: ModelRef, host: str, port: int) -> None: ...

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef: ...

    def templates(self) -> list[TemplateRef]: ...

    def describe(self) -> PluginInfo: ...


@runtime_checkable
class LoaderPlugin(Protocol):
    name: str
    api_version: str

    def can_load(self, uri: str) -> float: ...

    def load(self, uri: str) -> ModelRef: ...

    def describe(self) -> PluginInfo: ...


@runtime_checkable
class DetectorPlugin(Protocol):
    name: str
    api_version: str

    def score(self, model: ModelRef) -> float: ...

    def describe(self) -> PluginInfo: ...


@runtime_checkable
class TemplatePack(Protocol):
    name: str
    api_version: str

    def list_templates(self) -> list[TemplateRef]: ...

    def render(self, model: ModelRef, dest: Path, vars: dict[str, Any]) -> Path: ...

    def describe(self) -> PluginInfo: ...


def is_api_compatible(plugin_api_version: str, requires_api: str | None = None) -> bool:
    """Check plugin API version against core PLUGIN_API_VERSION."""
    from packaging.version import Version

    plugin_ver = Version(plugin_api_version.split(",", 1)[0].strip())
    core_major = Version(PLUGIN_API_VERSION).major
    if plugin_ver.major != core_major:
        return False
    if requires_api:
        # Minimal support: ">=1,<2" style
        req = requires_api.strip()
        if req.startswith(">="):
            min_part = req.split(",", 1)[0].replace(">=", "").strip()
            if Version(plugin_api_version) < Version(min_part):
                return False
    return True
