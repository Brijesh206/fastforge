"""Billing schemas.

``SubscriptionData`` is the provider-independent shape the service works with;
the Stripe adapter is responsible for translating Stripe's objects into it, so
no Stripe type ever crosses into the service or application.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionData(BaseModel):
    """Normalized subscription state extracted from a provider webhook."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    customer_id: str
    subscription_id: str
    status: str
    price_id: str | None
    current_period_end: datetime | None
    cancel_at_period_end: bool


class BillingEvent(BaseModel):
    """A verified provider webhook event.

    ``subscription`` is populated only for events the platform acts on
    (subscription lifecycle); it is None for events the service ignores.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str
    subscription: SubscriptionData | None = None


class SubscriptionResponse(BaseModel):
    """Public subscription state for the current user.

    ``status`` is None when the user has never started a subscription.
    """

    model_config = ConfigDict(extra="forbid")

    status: str | None
    price_id: str | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    is_active: bool


class CheckoutSessionResponse(BaseModel):
    """A hosted Stripe Checkout URL to redirect the user to."""

    model_config = ConfigDict(extra="forbid")

    url: str


class PortalSessionResponse(BaseModel):
    """A Stripe Billing Portal URL to redirect the user to."""

    model_config = ConfigDict(extra="forbid")

    url: str
