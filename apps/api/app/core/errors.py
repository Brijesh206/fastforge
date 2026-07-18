"""Application exception handlers."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastforge_common.exceptions import AppError, ErrorCode, RateLimitError
from fastforge_common.schemas import ErrorDetail, ErrorResponse
from fastforge_logging import get_logger

logger = get_logger("app.errors")


def register_exception_handlers(app: FastAPI) -> None:
    """Register platform-standard exception handlers."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors."""
    logger.warning(
        "Application error",
        error_code=exc.code,
        status_code=exc.status_code,
    )
    headers = None
    if isinstance(exc, RateLimitError) and exc.retry_after_seconds is not None:
        headers = {"Retry-After": str(exc.retry_after_seconds)}
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response().model_dump(mode="json"),
        headers=headers,
    )


async def request_validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle FastAPI request validation errors."""
    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed.",
            details={"errors": exc.errors()},
        )
    )
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=response.model_dump(mode="json"),
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions without leaking internals."""
    logger.exception("Unhandled exception", exception_type=type(exc).__name__)
    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred.",
        )
    )
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )
