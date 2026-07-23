"""Stripe billing provider.

The only module in the platform that imports the Stripe SDK. Everything above
the BillingProvider interface stays Stripe-agnostic.
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

import stripe

from fastforge_billing.config import BillingSettings
from fastforge_billing.exceptions import (
    BillingNotConfiguredError,
    WebhookVerificationError,
)
from fastforge_billing.interfaces.billing_provider import BillingProvider
from fastforge_billing.schemas import BillingEvent, SubscriptionData

_SUBSCRIPTION_EVENT_PREFIX = "customer.subscription."


class StripeBillingProvider(BillingProvider):
    """Implements BillingProvider against the Stripe API."""

    def __init__(self, settings: BillingSettings) -> None:
        self._settings = settings

    def _client(self) -> stripe.StripeClient:
        secret = self._settings.secret_key.get_secret_value()
        if not secret:
            raise BillingNotConfiguredError("STRIPE_SECRET_KEY is not set.")
        return stripe.StripeClient(secret)

    async def create_customer(self, *, email: str, user_id: str) -> str:
        client = self._client()
        customer = await asyncio.to_thread(
            client.v1.customers.create,
            params={"email": email, "metadata": {"user_id": user_id}},
        )
        return customer.id

    async def create_checkout_session(
        self, *, customer_id: str, price_id: str, success_url: str, cancel_url: str
    ) -> str:
        client = self._client()
        session = await asyncio.to_thread(
            client.v1.checkout.sessions.create,
            params={
                "mode": "subscription",
                "customer": customer_id,
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": success_url,
                "cancel_url": cancel_url,
            },
        )
        if session.url is None:
            raise BillingNotConfiguredError("Stripe returned a checkout session without a URL.")
        return session.url

    async def create_portal_session(self, *, customer_id: str, return_url: str) -> str:
        client = self._client()
        session = await asyncio.to_thread(
            client.v1.billing_portal.sessions.create,
            params={"customer": customer_id, "return_url": return_url},
        )
        return session.url

    async def cancel_subscription(self, *, subscription_id: str) -> None:
        client = self._client()
        await asyncio.to_thread(client.v1.subscriptions.cancel, subscription_id)

    def parse_webhook(self, *, payload: bytes, signature: str) -> BillingEvent:
        secret = self._settings.webhook_secret.get_secret_value()
        if not secret:
            raise BillingNotConfiguredError("STRIPE_WEBHOOK_SECRET is not set.")
        try:
            # Verifies the signature; raises on tampering or a stale timestamp.
            # construct_event lacks type hints in the Stripe SDK.
            stripe.Webhook.construct_event(payload, signature, secret)  # type: ignore[no-untyped-call]
        except (ValueError, stripe.SignatureVerificationError) as exc:
            raise WebhookVerificationError(str(exc)) from exc

        # The payload is now authenticated; parse it as plain JSON rather than
        # navigating Stripe's object wrappers.
        event = json.loads(payload)
        event_type: str = event["type"]
        created_at = datetime.fromtimestamp(event["created"], UTC)
        if not event_type.startswith(_SUBSCRIPTION_EVENT_PREFIX):
            return BillingEvent(type=event_type, created_at=created_at)
        return BillingEvent(
            type=event_type,
            created_at=created_at,
            subscription=_subscription_from(event["data"]["object"]),
        )


def _subscription_from(obj: Any) -> SubscriptionData:
    """Translate a Stripe Subscription object into the normalized shape."""
    items = obj.get("items", {}).get("data", [])
    price_id = items[0]["price"]["id"] if items else None
    period_end = obj.get("current_period_end")
    return SubscriptionData(
        customer_id=obj["customer"],
        subscription_id=obj["id"],
        status=obj["status"],
        price_id=price_id,
        current_period_end=(
            datetime.fromtimestamp(period_end, UTC) if period_end is not None else None
        ),
        cancel_at_period_end=bool(obj.get("cancel_at_period_end", False)),
    )
