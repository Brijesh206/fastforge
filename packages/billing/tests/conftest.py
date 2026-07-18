"""Shared in-memory fakes for billing service tests."""

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastforge_billing.interfaces.billing_provider import BillingProvider
from fastforge_billing.models.subscription import Subscription
from fastforge_billing.schemas import BillingEvent, SubscriptionData
from fastforge_billing.services.billing_service import BillingService


class FakeSubscriptionRepository:
    """In-memory stand-in for SubscriptionRepository."""

    def __init__(self) -> None:
        self.rows: list[Subscription] = []

    async def get_by_user_id(self, user_id: UUID) -> Subscription | None:
        return next((s for s in self.rows if s.user_id == user_id), None)

    async def get_by_customer_id(self, stripe_customer_id: str) -> Subscription | None:
        return next(
            (s for s in self.rows if s.stripe_customer_id == stripe_customer_id), None
        )

    async def create(self, instance: Subscription) -> Subscription:
        instance.id = uuid4()
        self.rows.append(instance)
        return instance

    async def update(self, instance: Subscription) -> Subscription:
        return instance


class FakeBillingProvider(BillingProvider):
    """Records calls and returns deterministic values."""

    def __init__(self) -> None:
        self.created_customers: list[tuple[str, str]] = []
        self.checkout_calls: list[dict[str, str]] = []
        self.portal_calls: list[dict[str, str]] = []
        self.canceled_subscriptions: list[str] = []
        self.next_event: BillingEvent | None = None

    async def create_customer(self, *, email: str, user_id: str) -> str:
        self.created_customers.append((email, user_id))
        return f"cus_{user_id[:8]}"

    async def create_checkout_session(
        self, *, customer_id: str, price_id: str, success_url: str, cancel_url: str
    ) -> str:
        self.checkout_calls.append({"customer_id": customer_id, "price_id": price_id})
        return f"https://checkout.stripe.test/{customer_id}"

    async def create_portal_session(self, *, customer_id: str, return_url: str) -> str:
        self.portal_calls.append({"customer_id": customer_id, "return_url": return_url})
        return f"https://portal.stripe.test/{customer_id}"

    async def cancel_subscription(self, *, subscription_id: str) -> None:
        self.canceled_subscriptions.append(subscription_id)

    def parse_webhook(self, *, payload: bytes, signature: str) -> BillingEvent:
        assert self.next_event is not None
        return self.next_event


@pytest.fixture
def fake_subscriptions() -> FakeSubscriptionRepository:
    """A fresh in-memory subscription repository."""
    return FakeSubscriptionRepository()


@pytest.fixture
def fake_provider() -> FakeBillingProvider:
    """A fresh fake billing provider."""
    return FakeBillingProvider()


@pytest.fixture
def billing_service(
    fake_subscriptions: FakeSubscriptionRepository, fake_provider: FakeBillingProvider
) -> BillingService:
    """BillingService wired to the in-memory fakes with a configured price."""
    return BillingService(fake_subscriptions, fake_provider, price_id="price_test_123")


SubEventFactory = Callable[..., BillingEvent]


@pytest.fixture
def make_sub_event() -> SubEventFactory:
    """Return a factory that builds a normalized subscription BillingEvent."""

    def _build(
        *,
        customer_id: str,
        subscription_id: str = "sub_1",
        status: str = "active",
        event_type: str = "customer.subscription.updated",
    ) -> BillingEvent:
        return BillingEvent(
            type=event_type,
            subscription=SubscriptionData(
                customer_id=customer_id,
                subscription_id=subscription_id,
                status=status,
                price_id="price_test_123",
                current_period_end=datetime(2030, 1, 1, tzinfo=UTC),
                cancel_at_period_end=False,
            ),
        )

    return _build
