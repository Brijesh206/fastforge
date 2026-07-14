"""Email provider adapters."""

from fastforge_mail.adapters.console_provider import ConsoleEmailProvider
from fastforge_mail.adapters.smtp_provider import SmtpEmailProvider

__all__ = ["ConsoleEmailProvider", "SmtpEmailProvider"]
