"""Shared application exceptions."""

from enum import StrEnum
from http import HTTPStatus

from fastforge_common.schemas import ErrorDetail, ErrorResponse


class ErrorCode(StrEnum):
    """Standard platform error codes."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    """Base application error.

    Services and packages should raise this hierarchy instead of leaking
    infrastructure exceptions to HTTP handlers or workers.
    """

    code: str = ErrorCode.INTERNAL_ERROR
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details
        super().__init__(self.message)

    def to_detail(self) -> ErrorDetail:
        """Convert the exception into a serializable error detail."""
        return ErrorDetail(
            code=self.code,
            message=self.message,
            details=self.details,
        )

    def to_response(self) -> ErrorResponse:
        """Convert the exception into a serializable error response."""
        return ErrorResponse(error=self.to_detail())


class AppValidationError(AppError):
    """Raised when application-level validation fails."""

    code = ErrorCode.VALIDATION_ERROR
    status_code = HTTPStatus.BAD_REQUEST
    message = "Invalid request."


class AuthenticationError(AppError):
    """Raised when authentication fails."""

    code = ErrorCode.AUTHENTICATION_ERROR
    status_code = HTTPStatus.UNAUTHORIZED
    message = "Authentication is required."


class AuthorizationError(AppError):
    """Raised when a principal lacks permission for an action."""

    code = ErrorCode.AUTHORIZATION_ERROR
    status_code = HTTPStatus.FORBIDDEN
    message = "You do not have permission to perform this action."


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    code = ErrorCode.NOT_FOUND
    status_code = HTTPStatus.NOT_FOUND
    message = "The requested resource was not found."


class ConflictError(AppError):
    """Raised when a request conflicts with existing state."""

    code = ErrorCode.CONFLICT
    status_code = HTTPStatus.CONFLICT
    message = "The request conflicts with the current state."


class RateLimitError(AppError):
    """Raised when a caller exceeds a rate limit."""

    code = ErrorCode.RATE_LIMITED
    status_code = HTTPStatus.TOO_MANY_REQUESTS
    message = "Too many requests."
