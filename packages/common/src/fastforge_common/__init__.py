"""Shared foundation utilities for FastForge."""

from fastforge_common.config import BaseAppSettings
from fastforge_common.constants import DEFAULT_API_PREFIX, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from fastforge_common.enums import AppEnvironment
from fastforge_common.exceptions import (
    AppError,
    AppValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ErrorCode,
    NotFoundError,
    RateLimitError,
)
from fastforge_common.schemas import ErrorDetail, ErrorResponse

__all__ = [
    "DEFAULT_API_PREFIX",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "AppEnvironment",
    "AppError",
    "AppValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "BaseAppSettings",
    "ConflictError",
    "ErrorCode",
    "ErrorDetail",
    "ErrorResponse",
    "NotFoundError",
    "RateLimitError",
]
