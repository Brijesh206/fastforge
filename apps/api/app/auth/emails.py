"""Wiring between auth tokens and the email service.

The auth package issues raw tokens; the mail package sends email. Neither
depends on the other — this app-layer module composes the link and schedules
the send so the HTTP request never waits on SMTP.
"""

from urllib.parse import urlencode

from fastapi import BackgroundTasks
from fastforge_auth import AuthSettings
from fastforge_mail import EmailService


def _link(base_url: str, path: str, token: str) -> str:
    return f"{base_url.rstrip('/')}/{path}?{urlencode({'token': token})}"


def schedule_verification_email(
    background_tasks: BackgroundTasks,
    email_service: EmailService,
    *,
    frontend_base_url: str,
    settings: AuthSettings,
    to: str,
    raw_token: str,
) -> None:
    """Queue the email-verification message for delivery after the response."""
    background_tasks.add_task(
        email_service.send_verification_email,
        to=to,
        verification_url=_link(frontend_base_url, "verify-email", raw_token),
        expires_in=f"{settings.email_verification_expire_hours} hours",
    )


def schedule_password_reset_email(
    background_tasks: BackgroundTasks,
    email_service: EmailService,
    *,
    frontend_base_url: str,
    settings: AuthSettings,
    to: str,
    raw_token: str,
) -> None:
    """Queue the password-reset message for delivery after the response."""
    background_tasks.add_task(
        email_service.send_password_reset_email,
        to=to,
        reset_url=_link(frontend_base_url, "reset-password", raw_token),
        expires_in=f"{settings.password_reset_expire_minutes} minutes",
    )
