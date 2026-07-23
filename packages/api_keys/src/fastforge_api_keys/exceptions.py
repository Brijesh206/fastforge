"""API key exceptions.

These extend the shared application exception hierarchy from
``fastforge_common`` so routers and error handlers do not need
api_keys-specific handling logic.
"""

from fastforge_common.exceptions import AuthenticationError, NotFoundError


class InvalidApiKeyError(AuthenticationError):
    """Raised when a presented API key is unknown, malformed, or revoked."""

    message = "Invalid or revoked API key."


class ApiKeyNotFoundError(NotFoundError):
    """Raised when an API key cannot be found for the requesting user."""

    message = "API key not found."
