"""Custom error handling."""


class FailedCommandError(Exception):
    """Indicates a missing / erroneous command response from relay board."""

    pass


class CommunicationError(Exception):
    """Indicates communication problem with relay board."""

    pass
