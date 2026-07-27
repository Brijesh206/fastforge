"""Auth routes.

Routers stay thin: validate the request, call the service, return the
response. Business logic lives in ``fastforge_auth.AuthService``; composing
email links and queuing delivery is app-layer glue in ``app.auth.emails``.
"""

import secrets
from http import HTTPStatus

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastforge_auth import (
    AccountDeleteRequest,
    AuthService,
    AuthSettings,
    LoginRequest,
    MessageResponse,
    OAuthEmailNotVerifiedError,
    OAuthNotConfiguredError,
    OAuthProvider,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    TokenPair,
    User,
    UserCreate,
    UserResponse,
    UserUpdate,
    VerifyEmailRequest,
)
from fastforge_billing import BillingService
from fastforge_common.exceptions import AuthenticationError
from fastforge_jobs import TaskQueue

from app.auth.dependencies import (
    get_auth_service,
    get_auth_settings,
    get_current_user,
    get_github_oauth_provider,
    get_google_oauth_provider,
    get_task_queue,
)
from app.auth.emails import schedule_password_reset_email, schedule_verification_email
from app.billing.dependencies import get_billing_service
from app.config import get_settings
from app.core.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])

# Brute-force / abuse protection for the unauthenticated entry points.
_login_limit = rate_limit("login", limit=10, window_seconds=60)
_register_limit = rate_limit("register", limit=10, window_seconds=3600)
_reset_limit = rate_limit("password_reset", limit=5, window_seconds=900)
_resend_limit = rate_limit("resend_verification", limit=5, window_seconds=900)
_oauth_limit = rate_limit("oauth", limit=20, window_seconds=60)

_OAUTH_STATE_TTL_SECONDS = 300
_OAUTH_STATE_COOKIE = "oauth_state"


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(_register_limit)],
)
async def register(
    payload: UserCreate,
    service: AuthService = Depends(get_auth_service),
    task_queue: TaskQueue = Depends(get_task_queue),
    settings: AuthSettings = Depends(get_auth_settings),
) -> UserResponse:
    """Register a new user and send a verification email."""
    user = await service.register_user(payload)
    raw_token = await service.issue_email_verification_token(user)
    await schedule_verification_email(
        task_queue,
        frontend_base_url=get_settings().frontend_base_url,
        settings=settings,
        to=user.email,
        raw_token=raw_token,
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenPair, dependencies=[Depends(_login_limit)])
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


def _me_response(user: User) -> UserResponse:
    """Serialize a user for its owner, including the derived admin flag.

    ``is_admin`` mirrors the admin router's own gate exactly (verified *and*
    listed in ADMIN_EMAILS) — if it were merely the email check, an unverified
    admin would see the panel link and then be refused by the API.
    """
    response = UserResponse.model_validate(user)
    response.is_admin = user.is_verified and get_settings().is_admin(user.email)
    return response


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user."""
    return _me_response(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Update the authenticated user's own profile."""
    user = await service.update_profile(current_user, payload)
    return _me_response(user)


@router.post("/password", response_model=TokenPair, dependencies=[Depends(_reset_limit)])
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """Set or change the authenticated user's password.

    Returns a fresh token pair: changing the password bumps token_version,
    which revokes every outstanding token, so the caller needs new ones to
    stay signed in. Every *other* device is signed out, which is the point.
    """
    return await service.change_password(current_user, payload)


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
    dependencies=[Depends(_resend_limit)],
)
async def resend_verification(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
    task_queue: TaskQueue = Depends(get_task_queue),
    settings: AuthSettings = Depends(get_auth_settings),
) -> MessageResponse:
    """Send a fresh verification email to the authenticated user."""
    if current_user.is_verified:
        return MessageResponse(detail="Email is already verified.")

    raw_token = await service.issue_email_verification_token(current_user)
    await schedule_verification_email(
        task_queue,
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
    dependencies=[Depends(_reset_limit)],
)
async def request_password_reset(
    payload: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
    task_queue: TaskQueue = Depends(get_task_queue),
    settings: AuthSettings = Depends(get_auth_settings),
) -> MessageResponse:
    """Send a password-reset link if an account exists for the email.

    Always returns the same response so the endpoint cannot be used to probe
    which addresses are registered.
    """
    result = await service.issue_password_reset_token(payload.email)
    if result is not None:
        user, raw_token = result
        await schedule_password_reset_email(
            task_queue,
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


@router.delete("/me", status_code=HTTPStatus.NO_CONTENT)
async def delete_account(
    payload: AccountDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
    billing_service: BillingService = Depends(get_billing_service),
) -> None:
    """Permanently delete the authenticated user's account.

    Verifies the password first (no side effects on a wrong password), then
    cancels any active Stripe subscription so deletion doesn't leave the user
    being billed, then deletes the account. auth_tokens and the subscription
    row cascade via foreign keys.
    """
    service.verify_current_password(current_user, payload.password)
    await billing_service.cancel_active_subscription(current_user.id)
    await service.delete_account(current_user.id)


async def _oauth_login_redirect(
    request: Request, provider: OAuthProvider, *, provider_name: str, callback_route: str
) -> RedirectResponse:
    """Stash a one-time state token in the cache and send the user to the provider.

    The same state is also set as an HttpOnly cookie on this response, so the
    callback can verify the browser completing the flow is the one that
    started it — the cache lookup alone only proves *some* browser started
    *a* flow, not this one, which is what makes OAuth login-CSRF possible
    (an attacker feeds a victim their own valid code+state, logging the
    victim into the attacker's account).

    request.url_for resolves the callback's absolute URL from the incoming
    request — behind a reverse proxy, run uvicorn with --proxy-headers (and a
    trusted proxy) so it reflects the public host, not an internal one.
    """
    state = secrets.token_urlsafe(24)
    await request.app.state.cache.set(
        f"oauth_state:{state}", provider_name, ttl_seconds=_OAUTH_STATE_TTL_SECONDS
    )
    redirect_uri = str(request.url_for(callback_route))
    response = RedirectResponse(provider.authorization_url(state=state, redirect_uri=redirect_uri))
    response.set_cookie(
        _OAUTH_STATE_COOKIE,
        state,
        max_age=_OAUTH_STATE_TTL_SECONDS,
        httponly=True,
        secure=get_settings().is_production,
        samesite="lax",
    )
    return response


async def _oauth_callback_redirect(
    request: Request,
    *,
    code: str | None,
    state: str | None,
    error: str | None,
    provider: OAuthProvider,
    provider_name: str,
    callback_route: str,
    service: AuthService,
) -> RedirectResponse:
    """Complete the provider handshake and hand tokens to the frontend.

    Every failure path redirects back to /login with an ?error= code instead
    of raising, since this endpoint is only ever reached via a browser
    navigation — a raw JSON error would strand the user mid-redirect.
    """
    frontend_base_url = get_settings().frontend_base_url.rstrip("/")

    def _failure(error_code: str) -> RedirectResponse:
        response = RedirectResponse(f"{frontend_base_url}/login?error={error_code}")
        response.delete_cookie(_OAUTH_STATE_COOKIE)
        return response

    if error or not code or not state:
        return _failure("oauth_failed")

    # The cookie proves this is the same browser /login redirected; the cache
    # entry proves the state itself is genuine and unused. Both are required.
    if request.cookies.get(_OAUTH_STATE_COOKIE) != state:
        return _failure("oauth_failed")

    cached_provider = await request.app.state.cache.get(f"oauth_state:{state}")
    await request.app.state.cache.delete(f"oauth_state:{state}")
    if cached_provider != provider_name:
        return _failure("oauth_failed")

    redirect_uri = str(request.url_for(callback_route))
    try:
        info = await provider.fetch_user_info(code=code, redirect_uri=redirect_uri)
        tokens = await service.login_or_register_oauth_user(info)
    except OAuthEmailNotVerifiedError:
        return _failure("oauth_email_unverified")
    except AuthenticationError:
        return _failure("oauth_account_inactive")
    except (OAuthNotConfiguredError, httpx.HTTPError):
        # A code can legitimately fail to exchange (expired, already used,
        # user took too long, provider hiccup) — not just on a malicious
        # request, so this redirects rather than raising a raw 500.
        return _failure("oauth_failed")

    # Tokens travel in the URL fragment, not the query string: fragments never
    # reach this (or any) server's access logs or Referer headers. The
    # frontend's /callback page reads window.location.hash client-side.
    fragment = f"access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
    response = RedirectResponse(f"{frontend_base_url}/callback#{fragment}")
    response.delete_cookie(_OAUTH_STATE_COOKIE)
    return response


@router.get("/google/login", name="google_login", dependencies=[Depends(_oauth_limit)])
async def google_login(
    request: Request, provider: OAuthProvider = Depends(get_google_oauth_provider)
) -> RedirectResponse:
    """Redirect to Google's consent screen."""
    return await _oauth_login_redirect(
        request, provider, provider_name="google", callback_route="google_callback"
    )


@router.get("/google/callback", name="google_callback", dependencies=[Depends(_oauth_limit)])
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    provider: OAuthProvider = Depends(get_google_oauth_provider),
    service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """Exchange Google's authorization code for tokens and sign the user in."""
    return await _oauth_callback_redirect(
        request,
        code=code,
        state=state,
        error=error,
        provider=provider,
        provider_name="google",
        callback_route="google_callback",
        service=service,
    )


@router.get("/github/login", name="github_login", dependencies=[Depends(_oauth_limit)])
async def github_login(
    request: Request, provider: OAuthProvider = Depends(get_github_oauth_provider)
) -> RedirectResponse:
    """Redirect to GitHub's consent screen."""
    return await _oauth_login_redirect(
        request, provider, provider_name="github", callback_route="github_callback"
    )


@router.get("/github/callback", name="github_callback", dependencies=[Depends(_oauth_limit)])
async def github_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    provider: OAuthProvider = Depends(get_github_oauth_provider),
    service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """Exchange GitHub's authorization code for tokens and sign the user in."""
    return await _oauth_callback_redirect(
        request,
        code=code,
        state=state,
        error=error,
        provider=provider,
        provider_name="github",
        callback_route="github_callback",
        service=service,
    )
