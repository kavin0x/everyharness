"""Plugin host: discovery, loading, and failure isolation."""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from importlib.metadata import entry_points
from typing import Any, cast

from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    DetectorPlugin,
    HarnessPlugin,
    LoaderPlugin,
    PluginInfo,
    TemplatePack,
    is_api_compatible,
)

logger = logging.getLogger(__name__)

ENTRYPOINT_GROUPS = {
    "harness": "everyharness.harnesses",
    "loader": "everyharness.loaders",
    "detector": "everyharness.detectors",
    "template": "everyharness.templates",
}


@dataclass
class PluginLoadResult:
    """Outcome of loading a single entry point."""

    name: str
    group: str
    plugin: Any | None = None
    error: str | None = None
    warning: str | None = None

    @property
    def ok(self) -> bool:
        return self.plugin is not None and self.error is None


@dataclass
class PluginHost:
    """Loads and caches plugins from entry points."""

    harnesses: list[HarnessPlugin] = field(default_factory=list)
    loaders: list[LoaderPlugin] = field(default_factory=list)
    detectors: list[DetectorPlugin] = field(default_factory=list)
    templates: list[TemplatePack] = field(default_factory=list)
    load_results: list[PluginLoadResult] = field(default_factory=list)

    @classmethod
    def discover(cls) -> PluginHost:
        host = cls()
        host.harnesses = cast(list[HarnessPlugin], host._load_group("harness", HarnessPlugin))
        host.loaders = cast(list[LoaderPlugin], host._load_group("loader", LoaderPlugin))
        host.detectors = cast(list[DetectorPlugin], host._load_group("detector", DetectorPlugin))
        host.templates = cast(list[TemplatePack], host._load_group("template", TemplatePack))
        return host

    def _load_group(self, kind: str, protocol: Any) -> list[Any]:
        group = ENTRYPOINT_GROUPS[kind]
        loaded: list[Any] = []
        eps = entry_points()
        if hasattr(eps, "select"):
            group_eps = eps.select(group=group)
        else:
            group_eps = cast(Any, eps).get(group, ())
        for ep in group_eps:
            result = self._load_entrypoint(kind, ep.name, ep.value, protocol)
            self.load_results.append(result)
            if result.plugin is not None:
                loaded.append(result.plugin)
        return loaded

    def _load_entrypoint(
        self,
        kind: str,
        name: str,
        target: str,
        protocol: Any,
    ) -> PluginLoadResult:
        try:
            obj = self._resolve_target(target)
        except Exception as exc:
            logger.warning("Failed to import plugin %s (%s): %s", name, target, exc)
            return PluginLoadResult(name=name, group=kind, error=str(exc))

        plugin = obj() if isinstance(obj, type) else obj
        api_version = getattr(plugin, "api_version", None)
        if api_version is None:
            return PluginLoadResult(
                name=name,
                group=kind,
                error="Plugin missing api_version attribute",
            )

        info = None
        try:
            describe = getattr(plugin, "describe", None)
            if callable(describe):
                info = describe()
        except Exception:
            info = None

        requires_api = getattr(info, "requires_api", None) if info else None
        if not is_api_compatible(str(api_version), requires_api):
            return PluginLoadResult(
                name=name,
                group=kind,
                warning=(
                    f"Incompatible API version {api_version} "
                    f"(core {PLUGIN_API_VERSION}); plugin skipped"
                ),
            )

        if not isinstance(plugin, protocol):
            return PluginLoadResult(
                name=name,
                group=kind,
                error=f"Plugin does not implement {protocol.__name__}",
            )

        return PluginLoadResult(name=name, group=kind, plugin=plugin)

    @staticmethod
    def _resolve_target(target: str) -> Any:
        module_name, _, attr = target.partition(":")
        if not attr:
            raise ImportError(f"Invalid entry point target: {target}")
        module = importlib.import_module(module_name)
        return getattr(module, attr)

    def all_plugin_info(self) -> list[PluginInfo]:
        infos: list[PluginInfo] = []
        for plugins in (self.harnesses, self.loaders, self.detectors, self.templates):
            for plugin in plugins:
                try:
                    infos.append(plugin.describe())
                except Exception:
                    continue
        return infos

    def broken_plugins(self) -> list[PluginLoadResult]:
        return [r for r in self.load_results if not r.ok]
