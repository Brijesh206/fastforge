"""Email provider interface."""

from abc import ABC, abstractmethod

from fastforge_mail.schemas import EmailMessage


class EmailProvider(ABC):
    """Delivers a rendered email.

    Services depend on this interface only. Swapping SMTP for a provider API
    must not require a change above this line.
    """

    @abstractmethod
    async def send(self, message: EmailMessage) -> None:
        """Deliver the message, raising EmailSendError if the provider rejects it."""
