"""Tests for the Stripe adapter's webhook verification and normalization.

These exercise the real ``stripe.Webhook.construct_event`` crypto path with a
correctly computed signature — no network, no mocking of the verification.
"""

import hashlib
import hmac
import json
import time

import pytest
from fastforge_billing.adapters.stripe_provider import StripeBillingProvider
from fastforge_billing.config import BillingSettings
from fastforge_billing.exceptions import WebhookVerificationError

WEBHOOK_SECRET = "whsec_test_secret"


def _provider() -> StripeBillingProvider:
    return StripeBillingProvider(
        BillingSettings(STRIPE_WEBHOOK_SECRET=WEBHOOK_SECRET, _env_file=None)
    )


def _sign(payload: bytes) -> str:
    """Build a valid Stripe-Signature header for the payload."""
    timestamp = int(time.time())
    signed = f"{timestamp}.".encode() + payload
    signature = hmac.new(WEBHOOK_SECRET.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


def _subscription_event_payload() -> bytes:
    event = {
        "id": "evt_1",
        "object": "event",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "object": "subscription",
                "customer": "cus_123",
                "status": "active",
                "cancel_at_period_end": False,
                "current_period_end": 1893456000,
                "items": {"data": [{"price": {"id": "price_123"}}]},
            }
        },
    }
    return json.dumps(event).encode()


def test_parse_webhook_verifies_and_normalizes_subscription_event() -> None:
    payload = _subscription_event_payload()

    event = _provider().parse_webhook(payload=payload, signature=_sign(payload))

    assert event.type == "customer.subscription.updated"
    assert event.subscription is not None
    assert event.subscription.customer_id == "cus_123"
    assert event.subscription.subscription_id == "sub_123"
    assert event.subscription.status == "active"
    assert event.subscription.price_id == "price_123"
    assert event.subscription.current_period_end is not None
    assert event.subscription.cancel_at_period_end is False


def test_parse_webhook_ignores_non_subscription_events() -> None:
    payload = json.dumps(
        {
            "id": "evt_2",
            "object": "event",
            "type": "invoice.paid",
            "data": {"object": {"id": "in_1", "object": "invoice"}},
        }
    ).encode()

    event = _provider().parse_webhook(payload=payload, signature=_sign(payload))

    assert event.type == "invoice.paid"
    assert event.subscription is None


def test_parse_webhook_rejects_a_bad_signature() -> None:
    payload = _subscription_event_payload()

    with pytest.raises(WebhookVerificationError):
        _provider().parse_webhook(payload=payload, signature="t=1,v1=deadbeef")
