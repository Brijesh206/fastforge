"""Authentication foundation for FastForge."""

from fastforge_auth.adapters.argon2_password_hasher import Argon2PasswordHasher
from fastforge_auth.adapters.jwt_token_service import JwtTokenService
from fastforge_auth.config import AuthSettings
from fastforge_auth.enums import AuthProvider, TokenType
from fastforge_auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from fastforge_auth.interfaces.password_hasher import PasswordHasher
from fastforge_auth.interfaces.token_service import TokenService
from fastforge_auth.models.user import User
from fastforge_auth.repositories.user import UserRepository
from fastforge_auth.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from fastforge_auth.schemas.user import UserCreate, UserResponse
from fastforge_auth.services.auth_service import AuthService

__all__ = [
    "Argon2PasswordHasher",
    "AuthProvider",
    "AuthService",
    "AuthSettings",
    "InactiveUserError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "JwtTokenService",
    "LoginRequest",
    "PasswordHasher",
    "RefreshRequest",
    "TokenPair",
    "TokenService",
    "TokenType",
    "User",
    "UserAlreadyExistsError",
    "UserCreate",
    "UserNotFoundError",
    "UserRepository",
    "UserResponse",
]
