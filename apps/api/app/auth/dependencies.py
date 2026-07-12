"""Auth dependencies for the API application."""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session, get_db_transaction
from fastforge_auth import (
    AuthService,
    PasswordHasher,
    TokenService,
    User,
    UserRepository,
)
from fastforge_common.exceptions import AuthenticationError

_bearer_scheme = HTTPBearer(auto_error=False)


def get_password_hasher(request: Request) -> PasswordHasher:
    """Return the process-wide password hasher created during startup."""
    return request.app.state.password_hasher


def get_token_service(request: Request) -> TokenService:
    """Return the process-wide token service created during startup."""
    return request.app.state.token_service


def get_auth_service(
    session: AsyncSession = Depends(get_db_transaction),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    """Build the auth service for write endpoints (transactional session)."""
    return AuthService(UserRepository(session), password_hasher, token_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    """Resolve the authenticated user from a Bearer access token.

    Raises AuthenticationError when the token is missing, invalid, or the
    resolved user is missing or inactive.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing bearer token.")

    user_id = token_service.decode_access_token(credentials.credentials)

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("User is inactive or does not exist.")

    return user
