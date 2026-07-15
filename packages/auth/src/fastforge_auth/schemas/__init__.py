"""Authentication schemas."""

from fastforge_auth.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from fastforge_auth.schemas.user import UserCreate, UserResponse
from fastforge_auth.schemas.verification import (
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    VerifyEmailRequest,
)

__all__ = [
    "LoginRequest",
    "MessageResponse",
    "PasswordResetConfirm",
    "PasswordResetRequest",
    "RefreshRequest",
    "TokenPair",
    "UserCreate",
    "UserResponse",
    "VerifyEmailRequest",
]
