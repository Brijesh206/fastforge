"""Background task handlers for transactional email.

Mail owns its own tasks — fastforge_jobs stays generic infrastructure and
never imports mail. Both the API (to enqueue) and the worker (to execute)
import this module; importing it is what registers the handlers.

Handlers take only JSON-serializable arguments, because every backend except
the in-memory one serializes them across a process boundary. They build their
own EmailService from settings rather than receiving one: a worker process has
no app.state to pull it from.
"""

from functools import lru_cache

from fastforge_jobs import task

from fastforge_mail.config import MailSettings
from fastforge_mail.service import EmailService, create_email_provider

SEND_VERIFICATION_EMAIL = "mail.send_verification_email"
SEND_PASSWORD_RESET_EMAIL = "mail.send_password_reset_email"


@lru_cache(maxsize=1)
def _email_service() -> EmailService:
    """Build the process's EmailService once and reuse it across jobs."""
    settings = MailSettings()
    return EmailService(create_email_provider(settings), settings)


@task(SEND_VERIFICATION_EMAIL)
async def send_verification_email(*, to: str, verification_url: str, expires_in: str) -> None:
    """Deliver the address-confirmation email for a new account."""
    await _email_service().send_verification_email(
        to=to, verification_url=verification_url, expires_in=expires_in
    )


@task(SEND_PASSWORD_RESET_EMAIL)
async def send_password_reset_email(*, to: str, reset_url: str, expires_in: str) -> None:
    """Deliver the password-reset email."""
    await _email_service().send_password_reset_email(
        to=to, reset_url=reset_url, expires_in=expires_in
    )
