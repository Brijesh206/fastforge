"""Billing dependencies for the API application."""

from fastapi import Depends, Request
from fastforge_auth import User
from fastforge_billing import (
    BillingProvider,
    BillingService,
    NoActiveSubscriptionError,
    SubscriptionRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.dependencies.database import get_db_transaction


def get_billing_provider(request: Request) -> BillingProvider:
    """Return the process-wide billing provider created during startup."""
    return request.app.state.billing_provider


def get_billing_service(
    request: Request,
    session: AsyncSession = Depends(get_db_transaction),
) -> BillingService:
    """Build the billing service for write endpoints (transactional session)."""
    return BillingService(
        SubscriptionRepository(session),
        request.app.state.billing_provider,
        price_id=request.app.state.billing_settings.price_id,
    )


async def require_active_subscription(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> User:
    """Guard an endpoint on an active subscription.

    The entitlement primitive for v1 — a single paid plan. Feature-level
    entitlements come later; for now access is subscription-gated.
    """
    subscription = await service.get_subscription(current_user.id)
    if not service.is_active(subscription):
        raise NoActiveSubscriptionError()
    return current_user
