class ShowroomError(Exception):
    """An expected, user-actionable showroom failure."""


class ConfigurationError(ShowroomError):
    """A config or command configuration is invalid."""


class RegistryError(ShowroomError):
    """The on-disk registry cannot be used safely."""


class AdapterError(ShowroomError):
    """An adapter failed or is unavailable."""
