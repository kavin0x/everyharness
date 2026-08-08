"""Doctor diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field

from everyharness.core.cache import cache_size_bytes
from everyharness.core.config import cache_dir, config_dir, data_dir, is_offline
from everyharness.core.update import current_version
from everyharness.plugin import PLUGIN_API_VERSION, PluginHost


@dataclass
class DoctorReport:
    version: str
    plugin_api_version: str
    offline: bool
    config_dir: str
    cache_dir: str
    data_dir: str
    cache_bytes: int
    plugins_ok: int
    plugins_broken: int
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def run_doctor() -> DoctorReport:
    host = PluginHost.discover()
    broken = host.broken_plugins()
    warnings = [r.warning for r in broken if r.warning]
    errors = [f"{r.group}/{r.name}: {r.error}" for r in broken if r.error]

    return DoctorReport(
        version=current_version(),
        plugin_api_version=PLUGIN_API_VERSION,
        offline=is_offline(),
        config_dir=str(config_dir()),
        cache_dir=str(cache_dir()),
        data_dir=str(data_dir()),
        cache_bytes=cache_size_bytes(),
        plugins_ok=len(host.all_plugin_info()),
        plugins_broken=len([r for r in broken if r.error]),
        warnings=[w for w in warnings if w],
        errors=errors,
    )
