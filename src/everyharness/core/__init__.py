"""Core package."""

from everyharness.core.cache import cache_size_bytes, get_cache_root, prune_cache
from everyharness.core.config import Config, cache_dir, config_dir, data_dir, is_offline
from everyharness.core.detect import detect_kind
from everyharness.core.errors import (
    ConfigError,
    EveryharnessError,
    OfflineError,
    PluginError,
    RegistryError,
    TemplateError,
)
from everyharness.core.registry import ModelRecord, ModelRegistry
from everyharness.core.update import check_for_update, current_version

__all__ = [
    "Config",
    "ConfigError",
    "ModelRecord",
    "ModelRegistry",
    "EveryharnessError",
    "OfflineError",
    "PluginError",
    "RegistryError",
    "TemplateError",
    "cache_dir",
    "cache_size_bytes",
    "check_for_update",
    "config_dir",
    "current_version",
    "data_dir",
    "detect_kind",
    "get_cache_root",
    "is_offline",
    "prune_cache",
]
