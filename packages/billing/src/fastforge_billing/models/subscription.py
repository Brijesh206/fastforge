"""Subscription model.

One row per user for v1 (organizations do not exist yet). When organizations
land post-v1, this moves to ``organization_id`` and gains history rows instead
of being updated in place.
"""

from datetime import datetime
from uuid import UUID

from fastforge_database.models.base import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class Subscription(BaseModel):
    """A user's current billing state, synchronized from Stripe webhooks.

    Stripe is the source of truth. Local fields are only ever written from a
    verified webhook (or when creating the customer), never trusted from a
    checkout redirect.
    """

    __tablename__ = "subscriptions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    stripe_customer_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, default=None
    )
    status: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    price_id: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # The source event's Stripe-side `created` timestamp, not when we applied
    # it. Lets handle_event reject a redelivered/retried older event that
    # arrives after a newer one already landed, instead of clobbering fresher
    # state. None until the first webhook is applied.
    last_event_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
