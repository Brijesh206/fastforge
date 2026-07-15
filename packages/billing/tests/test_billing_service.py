"""Tests for BillingService checkout, portal, and webhook sync."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from fastforge_billing.exceptions import BillingNotConfiguredError
from fastforge_billing.models.subscription import Subscription
from fastforge_billing.services.billing_service import BillingService

if TYPE_CHECKING:
    from conftest import FakeBillingProvider, FakeSubscriptionRepository, SubEventFactory


async def test_start_checkout_creates_customer_then_session(
    billing_service: BillingService,
    fake_subscriptions: FakeSubscriptionRepository,
    fake_provider: FakeBillingProvider,
) -> None:
    user_id = uuid4()

    url = await billing_service.start_checkout(
        user_id=user_id,
        email="a@b.com",
        success_url="https://app/success",
        cancel_url="https://app/cancel",
    )

    assert url.startswith("https://checkout.stripe.test/")
    assert fake_provider.created_customers == [("a@b.com", str(user_id))]
    assert fake_provider.checkout_calls[0]["price_id"] == "price_test_123"
    # The customer row was persisted for the webhook to find later.
    assert await fake_subscriptions.get_by_user_id(user_id) is not None


async def test_start_checkout_reuses_existing_customer(
    billing_service: BillingService,
    fake_subscriptions: FakeSubscriptionRepository,
    fake_provider: FakeBillingProvider,
) -> None:
    user_id = uuid4()
    await fake_subscriptions.create(
        Subscription(user_id=user_id, stripe_customer_id="cus_existing")
    )

    await billing_service.start_checkout(
        user_id=user_id, email="a@b.com", success_url="s", cancel_url="c"
    )

    assert fake_provider.created_customers == []
    assert fake_provider.checkout_calls[0]["customer_id"] == "cus_existing"


async def test_start_checkout_raises_without_a_configured_price(
    fake_subscriptions: FakeSubscriptionRepository, fake_provider: FakeBillingProvider
) -> None:
    service = BillingService(fake_subscriptions, fake_provider, price_id="")

    with pytest.raises(BillingNotConfiguredError):
        await service.start_checkout(
            user_id=uuid4(), email="a@b.com", success_url="s", cancel_url="c"
        )


async def test_open_portal_returns_url(
    billing_service: BillingService, fake_provider: FakeBillingProvider
) -> None:
    url = await billing_service.open_portal(
        user_id=uuid4(), email="a@b.com", return_url="https://app/account"
    )

    assert url.startswith("https://portal.stripe.test/")
    assert fake_provider.portal_calls[0]["return_url"] == "https://app/account"


async def test_handle_event_syncs_subscription_state(
    billing_service: BillingService,
    fake_subscriptions: FakeSubscriptionRepository,
    make_sub_event: SubEventFactory,
) -> None:
    user_id = uuid4()
    await fake_subscriptions.create(
        Subscription(user_id=user_id, stripe_customer_id="cus_1")
    )

    await billing_service.handle_event(make_sub_event(customer_id="cus_1", status="active"))

    row = await fake_subscriptions.get_by_user_id(user_id)
    assert row is not None
    assert row.status == "active"
    assert row.stripe_subscription_id == "sub_1"
    assert billing_service.is_active(row) is True


async def test_handle_event_is_idempotent(
    billing_service: BillingService,
    fake_subscriptions: FakeSubscriptionRepository,
    make_sub_event: SubEventFactory,
) -> None:
    user_id = uuid4()
    await fake_subscriptions.create(
        Subscription(user_id=user_id, stripe_customer_id="cus_1")
    )

    event = make_sub_event(customer_id="cus_1", status="active")
    await billing_service.handle_event(event)
    await billing_service.handle_event(event)

    assert len(fake_subscriptions.rows) == 1
    row = await fake_subscriptions.get_by_user_id(user_id)
    assert row is not None and row.status == "active"


async def test_handle_event_marks_canceled(
    billing_service: BillingService,
    fake_subscriptions: FakeSubscriptionRepository,
    make_sub_event: SubEventFactory,
) -> None:
    user_id = uuid4()
    await fake_subscriptions.create(
        Subscription(user_id=user_id, stripe_customer_id="cus_1", status="active")
    )

    await billing_service.handle_event(
        make_sub_event(
            customer_id="cus_1",
            status="canceled",
            event_type="customer.subscription.deleted",
        )
    )

    row = await fake_subscriptions.get_by_user_id(user_id)
    assert row is not None
    assert row.status == "canceled"
    assert billing_service.is_active(row) is False


async def test_handle_event_ignores_unknown_customer(
    billing_service: BillingService,
    fake_subscriptions: FakeSubscriptionRepository,
    make_sub_event: SubEventFactory,
) -> None:
    await billing_service.handle_event(make_sub_event(customer_id="cus_unknown"))

    assert fake_subscriptions.rows == []


async def test_handle_event_ignores_non_subscription_events(
    billing_service: BillingService, fake_subscriptions: FakeSubscriptionRepository
) -> None:
    from fastforge_billing.schemas import BillingEvent

    await billing_service.handle_event(BillingEvent(type="invoice.paid"))

    assert fake_subscriptions.rows == []


def test_is_active_is_false_for_none(billing_service: BillingService) -> None:
    assert billing_service.is_active(None) is False
