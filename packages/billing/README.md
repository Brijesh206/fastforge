# fastforge-billing

Subscription billing for FastForge. Stripe today, provider-independent by
design.

## Architecture

```text
Application → BillingService → BillingProvider (interface) → Stripe
```

The application depends on `BillingService` only. `StripeBillingProvider` is
the single module that imports the Stripe SDK; nothing above the
`BillingProvider` interface sees a Stripe type — webhooks come back as the
normalized `BillingEvent`.

## What it does (v1)

- Create a Stripe customer and a hosted **checkout** session for one plan
- Open the Stripe **billing portal** for self-service management
- Verify and process **webhooks**, syncing subscription state to the local DB
- `is_active` / `require_active_subscription` as the entitlement primitive

Stripe is the source of truth. Local subscription state is written **only** from
a verified webhook — never trusted from the checkout redirect (per the Stripe
docs and `docs/09-billing.md`). Webhook handling is idempotent, so Stripe's
retries are safe.

Subscriptions are **user-scoped** for v1. When organizations land (post-v1),
this moves to `organization_id` with history rows instead of an in-place update.

## Usage

```python
from fastforge_billing import BillingService, StripeBillingProvider, BillingSettings
from fastforge_billing import SubscriptionRepository

settings = BillingSettings()
provider = StripeBillingProvider(settings)
service = BillingService(SubscriptionRepository(session), provider, price_id=settings.price_id)

url = await service.start_checkout(
    user_id=user.id, email=user.email,
    success_url="https://app/billing/success", cancel_url="https://app/billing/cancel",
)
```

Webhook (already wired in `apps/api/app/billing/router.py`):

```python
event = provider.parse_webhook(payload=raw_body, signature=stripe_signature_header)
await service.handle_event(event)  # idempotent
```

## Configuration

`BillingSettings` reads `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and
`STRIPE_PRICE_ID` from the environment. All default to empty so the API boots
without billing configured; the adapter raises `BillingNotConfiguredError` if a
credential is actually needed at call time.

Local development uses the Stripe CLI to forward webhooks:

```bash
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
```

## Not implemented yet

Deliberately out of scope until there's a consumer:

- **Feature-level entitlements / usage limits** — v1 gates on a single active
  plan; no features are defined yet.
- **Invoice sync, coupons, trials config, tax** — Stripe handles these; we
  don't mirror them locally until something reads them.
- **Scheduled reconciliation** and **subscription history** — needs the worker
  and organizations respectively (post-v1).

See `docs/09-billing.md` for the full target design.
