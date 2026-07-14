"""Mail-specific exceptions."""

from fastforge_common.exceptions import AppError


class EmailSendError(AppError):
    """Raised when a provider fails to accept an email for delivery."""

    message = "The email could not be sent."


class TemplateNotFoundError(AppError):
    """Raised when a requested email template does not exist."""

    message = "The email template was not found."
