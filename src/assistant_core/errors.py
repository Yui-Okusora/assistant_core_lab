class AssistantError(Exception):
    """Base class for all assistant errors."""


class ConfigError(AssistantError):
    """Configuration is missing or invalid."""


class DataError(AssistantError):
    """A knowledge file is missing or malformed."""


class InvalidRequest(AssistantError):
    """The user's request cannot be processed as given."""


class ProviderError(AssistantError):
    """The AI provider failed (timeout, outage, bad response)."""
