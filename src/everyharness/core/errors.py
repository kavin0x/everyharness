"""Core error types."""


class EveryharnessError(Exception):
    """Base error for everyharness."""


class ConfigError(EveryharnessError):
    """Configuration is invalid or missing."""


class RegistryError(EveryharnessError):
    """Model registry operation failed."""


class PluginError(EveryharnessError):
    """Plugin loading or execution failed."""


class OfflineError(EveryharnessError):
    """Operation blocked because offline mode is enabled."""


class TemplateError(EveryharnessError):
    """Template rendering or application failed."""
