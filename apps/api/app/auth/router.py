"""Auth routes.

Routers stay thin: validate the request, call the service, return the
response. Business logic lives in ``fastforge_auth.AuthService``; composing
email links and queuing delivery is app-layer glue in ``app.auth.emails``.
"""

from http import HTTPStatus

from fastapi import APIRouter, BackgroundTasks, Depends
from fastforge_auth import (
    AuthService,
    AuthSettings,
    LoginRequest,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    TokenPair,
    User,
    UserCreate,
    UserResponse,
    VerifyEmailRequest,
)
from fastforge_mail import EmailService

from app.auth.dependencies import (
    get_auth_service,
    get_auth_settings,
    get_current_user,
    get_email_service,
)
from app.auth.emails import schedule_password_reset_email, schedule_verification_email
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def register(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service),
    settings: AuthSettings = Depends(get_auth_settings),
) -> UserResponse:
    """Register a new user and send a verification email."""
    user = await service.register_user(payload)
    raw_token = await service.issue_email_verification_token(user)
    schedule_verification_email(
        background_tasks,
        email_service,
        frontend_base_url=get_settings().frontend_base_url,
        settings=settings,
        to=user.email,
        raw_token=raw_token,
    )
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


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Confirm an email address with a verification token."""
    await service.verify_email(payload.token)
    return MessageResponse(detail="Email verified.")


@router.post(
    "/verify-email/resend",
    response_model=MessageResponse,
    status_code=HTTPStatus.ACCEPTED,
)
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service),
    settings: AuthSettings = Depends(get_auth_settings),
) -> MessageResponse:
    """Send a fresh verification email to the authenticated user."""
    if current_user.is_verified:
        return MessageResponse(detail="Email is already verified.")

    raw_token = await service.issue_email_verification_token(current_user)
    schedule_verification_email(
        background_tasks,
        email_service,
        frontend_base_url=get_settings().frontend_base_url,
        settings=settings,
        to=current_user.email,
        raw_token=raw_token,
    )
    return MessageResponse(detail="Verification email sent.")


@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
    status_code=HTTPStatus.ACCEPTED,
)
async def request_password_reset(
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service),
    settings: AuthSettings = Depends(get_auth_settings),
) -> MessageResponse:
    """Send a password-reset link if an account exists for the email.

    Always returns the same response so the endpoint cannot be used to probe
    which addresses are registered.
    """
    result = await service.issue_password_reset_token(payload.email)
    if result is not None:
        user, raw_token = result
        schedule_password_reset_email(
            background_tasks,
            email_service,
            frontend_base_url=get_settings().frontend_base_url,
            settings=settings,
            to=user.email,
            raw_token=raw_token,
        )
    return MessageResponse(
        detail="If an account exists for that email, a reset link has been sent."
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Set a new password using a valid reset token."""
    await service.reset_password(payload.token, payload.new_password)
    return MessageResponse(detail="Password updated.")
