"""Auth routes.

Routers stay thin: validate the request, call the service, return the
response. All business logic lives in ``fastforge_auth.AuthService``.
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastforge_auth import (
    AuthService,
    LoginRequest,
    RefreshRequest,
    TokenPair,
    User,
    UserCreate,
    UserResponse,
)

from app.auth.dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def register(
    payload: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user."""
    user = await service.register_user(payload)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """Authenticate with email and password and receive a token pair."""
    return await service.authenticate_user(payload)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """Exchange a valid refresh token for a new token pair."""
    return await service.refresh_tokens(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user."""
    return UserResponse.model_validate(current_user)
