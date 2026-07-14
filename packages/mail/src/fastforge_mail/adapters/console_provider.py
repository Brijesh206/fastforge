"""Console email provider for local development."""

from fastforge_logging import get_logger

from fastforge_mail.interfaces.email_provider import EmailProvider
from fastforge_mail.schemas import EmailMessage


class ConsoleEmailProvider(EmailProvider):
    """Logs emails instead of delivering them.

    Development only. The plain text body is logged so verification and reset
    links can be followed without a mail server.
    """

    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    async def send(self, message: EmailMessage) -> None:
        """Log the message rather than sending it."""
        self._logger.info(
            f"Email not sent (console provider): {message.subject} -> {message.to}\n"
            f"{message.text}"
        )
