"""Transactional email service."""

from fastforge_mail.adapters.console_provider import ConsoleEmailProvider
from fastforge_mail.adapters.smtp_provider import SmtpEmailProvider
from fastforge_mail.config import MailSettings
from fastforge_mail.interfaces.email_provider import EmailProvider
from fastforge_mail.rendering import render
from fastforge_mail.schemas import EmailMessage


class EmailService:
    """Renders and sends the platform's transactional emails.

    Applications depend on this class only. It talks to the EmailProvider
    interface, never to a provider SDK.
    """

    def __init__(self, provider: EmailProvider, settings: MailSettings) -> None:
        self._provider = provider
        self._settings = settings

    async def send_verification_email(
        self, *, to: str, verification_url: str, expires_in: str
    ) -> None:
        """Send the address-confirmation email for a new account."""
        await self._send(
            template="verify_email",
            to=to,
            subject=f"Verify your {self._settings.product_name} email",
            action_url=verification_url,
            expires_in=expires_in,
        )

    async def send_password_reset_email(self, *, to: str, reset_url: str, expires_in: str) -> None:
        """Send the password reset email."""
        await self._send(
            template="password_reset",
            to=to,
            subject=f"Reset your {self._settings.product_name} password",
            action_url=reset_url,
            expires_in=expires_in,
        )

    async def _send(
        self, *, template: str, to: str, subject: str, action_url: str, expires_in: str
    ) -> None:
        html, text = render(
            template,
            {
                "action_url": action_url,
                "expires_in": expires_in,
                "product_name": self._settings.product_name,
                "support_email": self._settings.support_email,
            },
        )
        await self._provider.send(EmailMessage(to=to, subject=subject, html=html, text=text))


def create_email_provider(settings: MailSettings) -> EmailProvider:
    """Build the provider named by configuration."""
    if settings.provider == "smtp":
        return SmtpEmailProvider(settings)
    return ConsoleEmailProvider()
