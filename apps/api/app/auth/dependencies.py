"""Auth dependencies for the API application."""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastforge_api_keys import API_KEY_PREFIX
from fastforge_auth import (
    AuthService,
    AuthSettings,
    AuthTokenRepository,
    PasswordHasher,
    TokenService,
    User,
    UserRepository,
)
from fastforge_common.exceptions import AuthenticationError
from fastforge_mail import EmailService
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_keys.dependencies import authenticate_via_api_key
from app.dependencies.database import get_db_session, get_db_transaction

_bearer_scheme = HTTPBearer(auto_error=False)


def get_password_hasher(request: Request) -> PasswordHasher:
    """Return the process-wide password hasher created during startup."""
    return request.app.state.password_hasher


def get_token_service(request: Request) -> TokenService:
    """Return the process-wide token service created during startup."""
    return request.app.state.token_service


def get_auth_settings(request: Request) -> AuthSettings:
    """Return the auth settings resolved during startup."""
    return request.app.state.auth_settings


def get_email_service(request: Request) -> EmailService:
    """Return the process-wide email service created during startup."""
    return request.app.state.email_service


def get_auth_service(
    session: AsyncSession = Depends(get_db_transaction),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    settings: AuthSettings = Depends(get_auth_settings),
) -> AuthService:
    """Build the auth service for write endpoints (transactional session)."""
    return AuthService(
        UserRepository(session),
        password_hasher,
        token_service,
        AuthTokenRepository(session),
        email_verification_expire_hours=settings.email_verification_expire_hours,
        password_reset_expire_minutes=settings.password_reset_expire_minutes,
    )


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    """Resolve the authenticated user from a Bearer token — a JWT access
    token or an API key (``ffk_...``), either is accepted in the same header.

    Raises AuthenticationError when the token is missing or invalid,
    RateLimitError if an API key has exceeded its rate limit, and
    AuthenticationError if the resolved user is missing or inactive.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing bearer token.")

    token = credentials.credentials
    required_version: int | None = None
    if token.startswith(API_KEY_PREFIX):
        # Only requests actually presenting an API key pay for the extra
        # transactional session this needs — the JWT path below does not.
        user_id = await authenticate_via_api_key(request, token)
    else:
        claims = token_service.decode_access_token(token)
        user_id = claims.user_id
        required_version = claims.token_version

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("User is inactive or does not exist.")

    # A bumped token_version (e.g. after a password reset) revokes every
    # previously issued JWT. API keys are revoked via their own table.
    if required_version is not None and required_version != user.token_version:
        raise AuthenticationError("Token has been revoked.")

    return user


def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """Like get_current_user, but require a verified email.

    Use this to guard endpoints that must not run for an unverified account.
    """
    if not current_user.is_verified:
        raise AuthenticationError("Email address is not verified.")
    return current_user
