"""Transactional email for FastForge."""

from fastforge_mail.adapters.console_provider import ConsoleEmailProvider
from fastforge_mail.adapters.smtp_provider import SmtpEmailProvider
from fastforge_mail.config import MailSettings
from fastforge_mail.exceptions import EmailSendError, TemplateNotFoundError
from fastforge_mail.interfaces.email_provider import EmailProvider
from fastforge_mail.rendering import render
from fastforge_mail.schemas import EmailMessage
from fastforge_mail.service import EmailService, create_email_provider

__all__ = [
    "ConsoleEmailProvider",
    "EmailMessage",
    "EmailProvider",
    "EmailSendError",
    "EmailService",
    "MailSettings",
    "SmtpEmailProvider",
    "TemplateNotFoundError",
    "create_email_provider",
    "render",
]
