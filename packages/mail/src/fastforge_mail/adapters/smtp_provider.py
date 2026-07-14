"""SMTP email provider."""

import asyncio
import smtplib
from email.message import EmailMessage as MimeMessage
from email.utils import formataddr

from fastforge_mail.config import MailSettings
from fastforge_mail.exceptions import EmailSendError
from fastforge_mail.interfaces.email_provider import EmailProvider
from fastforge_mail.schemas import EmailMessage


class SmtpEmailProvider(EmailProvider):
    """Delivers email over SMTP using the standard library.

    smtplib is blocking, so each send runs in a worker thread to keep the
    event loop free.
    """

    def __init__(self, settings: MailSettings) -> None:
        self._settings = settings

    def build_mime_message(self, message: EmailMessage) -> MimeMessage:
        """Build the multipart/alternative message handed to the SMTP server."""
        settings = self._settings
        mime = MimeMessage()
        mime["From"] = formataddr((settings.from_name, settings.from_address))
        mime["To"] = message.to
        mime["Subject"] = message.subject
        if settings.reply_to:
            mime["Reply-To"] = settings.reply_to
        mime.set_content(message.text)
        mime.add_alternative(message.html, subtype="html")
        return mime

    def _send_blocking(self, mime: MimeMessage) -> None:
        settings = self._settings
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
        ) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password.get_secret_value())
            smtp.send_message(mime)

    async def send(self, message: EmailMessage) -> None:
        """Deliver the message over SMTP."""
        # ponytail: no retry/backoff. Callers send via BackgroundTasks, so a
        # transient failure loses the email rather than the request. Add a
        # queue + retry when a dropped verification email actually hurts.
        try:
            await asyncio.to_thread(self._send_blocking, self.build_mime_message(message))
        except (smtplib.SMTPException, OSError) as exc:
            raise EmailSendError(f"SMTP delivery to {message.to} failed.") from exc
