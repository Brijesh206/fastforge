"""Billing routes.

Thin: checkout and portal delegate to ``BillingService``; the webhook verifies
the signature through the provider, then hands the normalized event to the
service. Stripe is trusted only after signature verification — never the
checkout redirect.
"""

from fastapi import APIRouter, Depends, Header, Request
from fastforge_auth import User
from fastforge_billing import (
    BillingProvider,
    BillingService,
    CheckoutSessionResponse,
    PortalSessionResponse,
    SubscriptionResponse,
)

from app.auth.dependencies import get_current_user
from app.billing.dependencies import get_billing_provider, get_billing_service
from app.config import get_settings

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> CheckoutSessionResponse:
    """Start a checkout session for the configured plan."""
    base = get_settings().frontend_base_url.rstrip("/")
    url = await service.start_checkout(
        user_id=current_user.id,
        email=current_user.email,
        success_url=f"{base}/billing/success",
        cancel_url=f"{base}/billing/cancel",
    )
    return CheckoutSessionResponse(url=url)


@router.post("/portal", response_model=PortalSessionResponse)
async def open_portal(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> PortalSessionResponse:
    """Open the Stripe billing portal for the user to manage their subscription."""
    base = get_settings().frontend_base_url.rstrip("/")
    url = await service.open_portal(
        user_id=current_user.id, email=current_user.email, return_url=f"{base}/account"
    )
    return PortalSessionResponse(url=url)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> SubscriptionResponse:
    """Return the current user's subscription state."""
    subscription = await service.get_subscription(current_user.id)
    return SubscriptionResponse(
        status=subscription.status if subscription else None,
        price_id=subscription.price_id if subscription else None,
        current_period_end=subscription.current_period_end if subscription else None,
        cancel_at_period_end=subscription.cancel_at_period_end if subscription else False,
        is_active=service.is_active(subscription),
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    provider: BillingProvider = Depends(get_billing_provider),
    service: BillingService = Depends(get_billing_service),
) -> dict[str, bool]:
    """Receive and process a verified Stripe webhook.

    The signature is verified before any state changes; handling is idempotent
    so Stripe's retries are safe.
    """
    payload = await request.body()
    event = provider.parse_webhook(payload=payload, signature=stripe_signature)
    await service.handle_event(event)
    return {"received": True}
