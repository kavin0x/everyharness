"""Public plugin SDK."""

from everyharness.plugin.host import PluginHost, PluginLoadResult
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    DetectorPlugin,
    HarnessPlugin,
    LoaderPlugin,
    ModelRef,
    PluginInfo,
    TemplatePack,
    TemplateRef,
    TrainOpts,
    is_api_compatible,
)

__all__ = [
    "PLUGIN_API_VERSION",
    "DetectorPlugin",
    "HarnessPlugin",
    "LoaderPlugin",
    "ModelRef",
    "PluginHost",
    "PluginInfo",
    "PluginLoadResult",
    "TemplatePack",
    "TemplateRef",
    "TrainOpts",
    "is_api_compatible",
]
