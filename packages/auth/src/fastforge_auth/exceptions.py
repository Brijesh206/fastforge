"""Authentication exceptions.

These extend the shared application exception hierarchy from
``fastforge_common`` so routers and error handlers do not need auth-specific
handling logic.
"""

from fastforge_common.exceptions import AuthenticationError, ConflictError, NotFoundError


class UserAlreadyExistsError(ConflictError):
    """Raised when registering an email that is already in use."""

    message = "A user with this email already exists."


class UserNotFoundError(NotFoundError):
    """Raised when a user cannot be found."""

    message = "User not found."


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    message = "Invalid email or password."


class InactiveUserError(AuthenticationError):
    """Raised when an inactive user attempts to authenticate."""

    message = "This account is inactive."


class InvalidTokenError(AuthenticationError):
    """Raised when a token is invalid, expired, or malformed."""

    message = "Invalid or expired token."
