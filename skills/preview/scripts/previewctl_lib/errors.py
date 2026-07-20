class PreviewctlError(Exception):
    """An expected, user-actionable previewctl failure."""


class ConfigurationError(PreviewctlError):
    """A manifest or command configuration is invalid."""


class RegistryError(PreviewctlError):
    """The on-disk registry cannot be used safely."""


class AdapterError(PreviewctlError):
    """An adapter failed or is unavailable."""
