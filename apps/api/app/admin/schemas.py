"""Admin panel response schemas."""

from datetime import datetime
from uuid import UUID

from fastforge_billing import ACTIVE_STATUSES, Subscription
from pydantic import BaseModel, ConfigDict


class AdminUserItem(BaseModel):
    """A user row in the admin list."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None
    created_at: datetime


class AdminUserList(BaseModel):
    """Paginated user list."""

    items: list[AdminUserItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminSubscriptionInfo(BaseModel):
    """A user's subscription, as shown in the admin detail view."""

    status: str | None
    price_id: str | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    stripe_customer_id: str
    is_active: bool

    @classmethod
    def from_model(cls, subscription: Subscription) -> "AdminSubscriptionInfo":
        """Build from a Subscription row, deriving the access-granting flag."""
        return cls(
            status=subscription.status,
            price_id=subscription.price_id,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            stripe_customer_id=subscription.stripe_customer_id,
            is_active=subscription.status in ACTIVE_STATUSES,
        )


class AdminUserDetail(AdminUserItem):
    """A user plus their subscription (if any)."""

    avatar_url: str | None
    updated_at: datetime
    subscription: AdminSubscriptionInfo | None


class AdminStats(BaseModel):
    """Headline counts for the panel."""

    total_users: int
    total_subscriptions: int
    active_subscriptions: int
