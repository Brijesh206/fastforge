"""Wiring between auth tokens and the email task queue.

The auth package issues raw tokens; the mail package sends email. Neither
depends on the other — this app-layer module composes the link and hands the
send to the task queue, so the HTTP request never waits on SMTP.

Jobs are enqueued by *name*, so which backend actually runs them (in-process,
Taskiq or Celery) is a JOBS_PROVIDER setting and nothing here changes.
"""

from urllib.parse import urlencode

from fastforge_auth import AuthSettings
from fastforge_jobs import TaskQueue
from fastforge_mail.tasks import SEND_PASSWORD_RESET_EMAIL, SEND_VERIFICATION_EMAIL


def _link(base_url: str, path: str, token: str) -> str:
    return f"{base_url.rstrip('/')}/{path}?{urlencode({'token': token})}"


async def schedule_verification_email(
    task_queue: TaskQueue,
    *,
    frontend_base_url: str,
    settings: AuthSettings,
    to: str,
    raw_token: str,
) -> None:
    """Queue the email-verification message for delivery."""
    await task_queue.enqueue(
        SEND_VERIFICATION_EMAIL,
        to=to,
        verification_url=_link(frontend_base_url, "verify-email", raw_token),
        expires_in=f"{settings.email_verification_expire_hours} hours",
    )


async def schedule_password_reset_email(
    task_queue: TaskQueue,
    *,
    frontend_base_url: str,
    settings: AuthSettings,
    to: str,
    raw_token: str,
) -> None:
    """Queue the password-reset message for delivery."""
    await task_queue.enqueue(
        SEND_PASSWORD_RESET_EMAIL,
        to=to,
        reset_url=_link(frontend_base_url, "reset-password", raw_token),
        expires_in=f"{settings.password_reset_expire_minutes} minutes",
    )
