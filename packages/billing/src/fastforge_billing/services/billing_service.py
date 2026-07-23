"""Billing service — checkout, portal, and webhook-driven subscription sync."""

from uuid import UUID

from fastforge_logging import get_logger

from fastforge_billing.enums import ACTIVE_STATUSES
from fastforge_billing.exceptions import BillingNotConfiguredError
from fastforge_billing.interfaces.billing_provider import BillingProvider
from fastforge_billing.models.subscription import Subscription
from fastforge_billing.repositories.subscription import SubscriptionRepository
from fastforge_billing.schemas import BillingEvent

logger = get_logger("fastforge_billing.service")


class BillingService:
    """Owns billing business logic.

    Takes user primitives (id, email) rather than an auth model, so the
    billing package never depends on the auth package. Talks to Stripe only
    through the BillingProvider interface. Stripe is the source of truth:
    local subscription state is written from verified webhooks, never from a
    checkout redirect.
    """

    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        provider: BillingProvider,
        *,
        price_id: str,
    ) -> None:
        self._subscriptions = subscription_repository
        self._provider = provider
        self._price_id = price_id

    async def get_subscription(self, user_id: UUID) -> Subscription | None:
        """Return the user's subscription row, if any."""
        return await self._subscriptions.get_by_user_id(user_id)

    @staticmethod
    def is_active(subscription: Subscription | None) -> bool:
        """Return True if the subscription currently grants access."""
        return subscription is not None and subscription.status in ACTIVE_STATUSES

    async def start_checkout(
        self, *, user_id: UUID, email: str, success_url: str, cancel_url: str
    ) -> str:
        """Return a hosted checkout URL for the configured plan."""
        if not self._price_id:
            raise BillingNotConfiguredError("STRIPE_PRICE_ID is not set.")
        subscription = await self._get_or_create_customer(user_id, email)
        return await self._provider.create_checkout_session(
            customer_id=subscription.stripe_customer_id,
            price_id=self._price_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

    async def open_portal(self, *, user_id: UUID, email: str, return_url: str) -> str:
        """Return a billing portal URL for the user to manage their subscription."""
        subscription = await self._get_or_create_customer(user_id, email)
        return await self._provider.create_portal_session(
            customer_id=subscription.stripe_customer_id, return_url=return_url
        )

    async def cancel_active_subscription(self, user_id: UUID) -> None:
        """Cancel the user's Stripe subscription immediately, if one is active.

        No-op if the user has no subscription or it isn't active. Used by
        account deletion so a removed account doesn't keep being billed —
        the local row is left for the webhook (or the caller) to clean up.
        """
        subscription = await self._subscriptions.get_by_user_id(user_id)
        if subscription is None or subscription.stripe_subscription_id is None:
            return
        if subscription.status not in ACTIVE_STATUSES:
            return
        await self._provider.cancel_subscription(
            subscription_id=subscription.stripe_subscription_id
        )

    async def handle_event(self, event: BillingEvent) -> None:
        """Apply a verified webhook event to local subscription state.

        Idempotent: syncing the same event twice yields the same row. Events
        the platform does not act on (``event.subscription is None``) are
        ignored. Events older than the last-applied one are also ignored —
        Stripe retries and redeliveries are not guaranteed to arrive in
        order, and applying a stale event after a newer one would clobber
        fresher state with old data.
        """
        if event.subscription is None:
            return

        data = event.subscription
        subscription = await self._subscriptions.get_by_customer_id(data.customer_id)
        if subscription is None:
            logger.warning(
                "Webhook for unknown customer; ignoring",
                stripe_customer_id=data.customer_id,
                event_type=event.type,
            )
            return

        last_event_at = subscription.last_event_at
        if last_event_at is not None and event.created_at <= last_event_at:
            logger.warning(
                "Out-of-order webhook event; ignoring",
                stripe_customer_id=data.customer_id,
                event_type=event.type,
                event_created_at=event.created_at.isoformat(),
                last_event_at=last_event_at.isoformat(),
            )
            return

        subscription.last_event_at = event.created_at
        subscription.stripe_subscription_id = data.subscription_id
        subscription.status = data.status
        subscription.price_id = data.price_id
        subscription.current_period_end = data.current_period_end
        subscription.cancel_at_period_end = data.cancel_at_period_end
        await self._subscriptions.update(subscription)

    async def _get_or_create_customer(self, user_id: UUID, email: str) -> Subscription:
        subscription = await self._subscriptions.get_by_user_id(user_id)
        if subscription is not None:
            return subscription

        customer_id = await self._provider.create_customer(email=email, user_id=str(user_id))
        return await self._subscriptions.create(
            Subscription(user_id=user_id, stripe_customer_id=customer_id)
        )
