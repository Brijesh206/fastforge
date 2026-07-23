"""Authentication foundation for FastForge."""

from fastforge_auth.adapters.argon2_password_hasher import Argon2PasswordHasher
from fastforge_auth.adapters.github_oauth_provider import GitHubOAuthProvider
from fastforge_auth.adapters.google_oauth_provider import GoogleOAuthProvider
from fastforge_auth.adapters.jwt_token_service import JwtTokenService
from fastforge_auth.config import AuthSettings, OAuthSettings
from fastforge_auth.enums import AuthProvider, AuthTokenPurpose, TokenType
from fastforge_auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    OAuthEmailNotVerifiedError,
    OAuthNotConfiguredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from fastforge_auth.interfaces.oauth_provider import OAuthProvider, OAuthUserInfo
from fastforge_auth.interfaces.password_hasher import PasswordHasher
from fastforge_auth.interfaces.token_service import TokenService
from fastforge_auth.models.auth_token import AuthToken
from fastforge_auth.models.user import User
from fastforge_auth.repositories.auth_token import AuthTokenRepository
from fastforge_auth.repositories.user import UserRepository
from fastforge_auth.schemas.auth import (
    AccountDeleteRequest,
    LoginRequest,
    RefreshRequest,
    TokenClaims,
    TokenPair,
)
from fastforge_auth.schemas.user import UserCreate, UserResponse
from fastforge_auth.schemas.verification import (
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    VerifyEmailRequest,
)
from fastforge_auth.services.auth_service import AuthService

__all__ = [
    "AccountDeleteRequest",
    "Argon2PasswordHasher",
    "AuthProvider",
    "AuthService",
    "AuthSettings",
    "AuthToken",
    "AuthTokenPurpose",
    "AuthTokenRepository",
    "GitHubOAuthProvider",
    "GoogleOAuthProvider",
    "InactiveUserError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "JwtTokenService",
    "LoginRequest",
    "MessageResponse",
    "OAuthEmailNotVerifiedError",
    "OAuthNotConfiguredError",
    "OAuthProvider",
    "OAuthSettings",
    "OAuthUserInfo",
    "PasswordHasher",
    "PasswordResetConfirm",
    "PasswordResetRequest",
    "RefreshRequest",
    "TokenClaims",
    "TokenPair",
    "TokenService",
    "TokenType",
    "User",
    "UserAlreadyExistsError",
    "UserCreate",
    "UserNotFoundError",
    "UserRepository",
    "UserResponse",
    "VerifyEmailRequest",
]
