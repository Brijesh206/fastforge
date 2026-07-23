"""Authentication exceptions.

These extend the shared application exception hierarchy from
``fastforge_common`` so routers and error handlers do not need auth-specific
handling logic.
"""

from http import HTTPStatus

from fastforge_common.exceptions import AppError, AuthenticationError, ConflictError, NotFoundError


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


class OAuthError(AppError):
    """Base for OAuth sign-in failures."""

    message = "OAuth sign-in failed."


class OAuthNotConfiguredError(OAuthError):
    """Raised when a provider's client id/secret is missing."""

    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    message = "This sign-in provider is not configured."


class OAuthEmailNotVerifiedError(OAuthError):
    """Raised when the provider can't vouch that the account's email is verified."""

    status_code = HTTPStatus.BAD_REQUEST
    message = "Your email address is not verified with this provider."
