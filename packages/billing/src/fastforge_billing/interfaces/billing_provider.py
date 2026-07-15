"""Billing provider interface."""

from abc import ABC, abstractmethod

from fastforge_billing.schemas import BillingEvent


class BillingProvider(ABC):
    """A payment provider (Stripe today; Paddle/Lemon Squeezy later).

    The service depends on this interface only. No provider SDK type may
    appear in a method signature — webhooks come back as the normalized
    ``BillingEvent``.
    """

    @abstractmethod
    async def create_customer(self, *, email: str, user_id: str) -> str:
        """Create a provider customer and return its id."""

    @abstractmethod
    async def create_checkout_session(
        self, *, customer_id: str, price_id: str, success_url: str, cancel_url: str
    ) -> str:
        """Create a hosted checkout session and return its URL."""

    @abstractmethod
    async def create_portal_session(self, *, customer_id: str, return_url: str) -> str:
        """Create a billing portal session and return its URL."""

    @abstractmethod
    def parse_webhook(self, *, payload: bytes, signature: str) -> BillingEvent:
        """Verify a webhook's signature and return the normalized event.

        Raises WebhookVerificationError if the signature or payload is invalid.
        """
