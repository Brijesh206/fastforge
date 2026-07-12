# Billing Guide

> Reusable billing architecture for every SaaS built on FastForge.

---

# Purpose

Billing is one of the most reusable modules in the platform.

It should be implemented once and reused across all future products.

The billing package is responsible for:

- Stripe integration
- Products
- Plans
- Customers
- Subscriptions
- Checkout
- Customer Portal
- Webhooks
- Trials
- Coupons
- Invoices
- Usage tracking (future)
- Entitlements
- Billing events

Applications should never communicate directly with Stripe.

Everything must go through the Billing package.

---

# Design Principles

The billing system should be:

- Vendor independent
- Event driven
- Idempotent
- Testable
- Extensible

Business logic should never depend on Stripe-specific APIs.

---

# Architecture

```
Application

↓

BillingService

↓

Billing Provider

↓

Stripe Adapter

↓

Stripe API
```

Future providers:

- Lemon Squeezy
- Paddle
- Polar
- Custom billing providers

The application layer should remain unchanged when providers change.

---

# Responsibilities

The Billing package owns:

- Customer creation
- Subscription lifecycle
- Checkout Sessions
- Customer Portal
- Invoice synchronization
- Webhook processing
- Plan lookup
- Feature entitlements

Applications consume BillingService.

---

# Subscription Model

Every subscription should include:

```text
id

organization_id

provider

provider_subscription_id

provider_customer_id

plan_id

status

trial_ends_at

current_period_start

current_period_end

cancel_at

canceled_at

created_at

updated_at
```

Provider IDs should always be stored.

Never rely solely on local state.

---

# Billing Providers

Define a common interface.

Example:

```python
BillingProvider
```

Required methods:

```
create_customer()

create_checkout()

create_portal()

cancel_subscription()

resume_subscription()

get_subscription()

verify_webhook()

list_products()
```

Every provider implements this interface.

---

# Plans

Plans represent application pricing.

Example:

```
Free

Starter

Pro

Business
```

Plans belong to the application.

Pricing belongs to the provider.

---

# Plan Model

Recommended fields:

```text
id

slug

name

description

is_active

sort_order

created_at
```

Avoid storing duplicated pricing locally.

Treat Stripe as the pricing authority.

---

# Customer Model

Each organization should map to one billing customer.

Fields:

```text
id

organization_id

provider

provider_customer_id

created_at
```

One customer.

Many subscriptions over time.

---

# Subscription Status

Supported states:

```
trialing

active

past_due

paused

canceled

incomplete

unpaid
```

Do not invent custom statuses.

Map provider statuses into platform statuses.

---

# Checkout Flow

```
User

↓

Select Plan

↓

BillingService

↓

Stripe Checkout Session

↓

Stripe Hosted Checkout

↓

Payment

↓

Webhook

↓

Update Subscription

↓

Enable Features
```

Always trust webhook events.

Do not trust redirect URLs for payment success.

---

# Customer Portal

Use Stripe Billing Portal.

Flow:

```
Dashboard

↓

Manage Billing

↓

BillingService

↓

Portal Session

↓

Stripe Portal
```

Users should manage:

- Payment methods
- Invoices
- Subscription
- Billing address

without leaving the provider-supported flow.

---

# Trial Support

Support optional free trials.

Example:

```
7 Days

14 Days

30 Days
```

Trial configuration belongs to plans.

The application should not hardcode trial lengths.

---

# Free Plan

Every product should define whether a free plan exists.

Benefits:

- Easier onboarding
- Product-led growth
- Lower acquisition friction

Feature access should be determined by entitlements rather than checking plan names.

---

# Coupons

Support provider-managed coupons.

Applications should not implement coupon logic independently.

Coupon validation remains the provider's responsibility.

---

# Invoices

Store invoice metadata.

Example fields:

```text
provider_invoice_id

subscription_id

status

amount

currency

invoice_url

created_at
```

Invoices should remain synchronized from webhook events.

---

# Payment Methods

Users should manage payment methods through the provider portal.

Avoid implementing custom payment method UIs.

---

# Currency

Support multiple currencies.

Store amounts in the smallest currency unit.

Example:

```
USD

1000

=

$10.00
```

Never store floating-point currency values.

---

# Taxes

Initially rely on provider-managed tax calculation.

Future enhancements may include:

- VAT
- GST
- Sales Tax

Applications should remain tax-provider agnostic.

---

# Billing Events

Important billing events include:

- Subscription created
- Subscription updated
- Subscription canceled
- Trial started
- Trial ended
- Invoice paid
- Invoice failed
- Payment succeeded
- Payment failed

These events drive application state.

---

# Event Flow

```
Stripe

↓

Webhook

↓

Webhook Verification

↓

BillingService

↓

Database Update

↓

Business Events

↓

Notifications
```

The webhook is the source of truth.

---

# Webhook Verification

Every webhook must:

- Verify signature
- Validate payload
- Reject invalid requests

Never trust unauthenticated webhook payloads.

---

# Idempotency

Webhook handlers must be idempotent.

Duplicate webhook deliveries should never create duplicate records or inconsistent state.

Store processed webhook event IDs where appropriate.

---

# Retry Strategy

Webhook processing should support retries.

Temporary failures:

- Retry

Permanent failures:

- Log
- Alert
- Require manual review if necessary

Never silently discard failed webhook events.

---

# Entitlements

Applications should never check plan names directly.

Bad:

```python
if subscription.plan == "pro":
```

Good:

```python
if current_user.has_feature("api_keys"):
```

Every feature should be enabled through entitlements.

Example:

```
Free

↓

Projects (3)

API Calls (10,000/month)

No Team Members
```

```
Pro

↓

Unlimited Projects

Unlimited API Calls

Team Members

Priority Support
```

The application only checks features.

The Billing package decides which features are available.

---

# Feature Flags vs Entitlements

Feature Flags:

- Rollout control
- A/B testing
- Experimental features

Entitlements:

- Paid access
- Plan limits
- Subscription features

Never mix these concepts.

---

# Usage Limits

The billing system should support usage limits.

Examples:

```
API Calls

Projects

Storage

Team Members

Workspaces

Uploads
```

Usage should be measured independently from billing.

Billing only evaluates whether usage exceeds limits.

---

# Usage Tracking

Recommended flow:

```
API Request

↓

Usage Service

↓

Increment Counter

↓

Persist Usage

↓

Billing Service

↓

Evaluate Limits
```

Usage collection should remain lightweight.

---

# Overage Support

Future products may allow paid overages.

Example:

```
Plan Limit

↓

Exceeded

↓

Additional Charges
```

The architecture should support this without redesigning the billing module.

---

# Subscription Synchronization

Never assume local subscription data is always correct.

Synchronization sources:

- Webhooks
- Scheduled reconciliation jobs
- Manual admin sync

Stripe remains the billing authority.

---

# Scheduled Reconciliation

Run periodic reconciliation jobs.

Examples:

- Missing invoices
- Subscription mismatch
- Failed webhook recovery

Frequency:

```
Daily
```

This provides resilience against webhook failures.

---

# Billing Middleware

Provide reusable helpers.

Examples:

```python
require_active_subscription()

require_feature("projects")

require_usage_available("api_calls")
```

Applications should never duplicate subscription checks.

---

# Plan Changes

Upgrade flow:

```
Current Plan

↓

Checkout or Portal

↓

Provider

↓

Webhook

↓

Subscription Updated

↓

Entitlements Updated
```

Downgrades follow the same event-driven flow.

---

# Subscription Cancellation

Support:

- Immediate cancellation
- Cancel at period end

Never delete subscription history.

Historical data is valuable for analytics and support.

---

# Grace Period

Optionally support a grace period for failed payments.

Example:

```
Payment Failure

↓

3 Days Grace

↓

Suspend Premium Features
```

This behavior should be configurable.

---

# Notifications

Billing-related notifications include:

- Trial ending
- Payment failed
- Subscription renewed
- Subscription canceled
- Invoice available

Notifications should be queued through the Notification package.

---

# Background Jobs

Billing workers may process:

- Webhook retries
- Invoice synchronization
- Subscription reconciliation
- Trial reminders
- Usage resets

Billing should never block HTTP requests.

---

# Security

Protect:

- Customer IDs
- Subscription IDs
- Invoice URLs
- Billing metadata

Never expose provider secrets.

Verify every incoming webhook.

---

# Logging

Log important billing events.

Examples:

- Checkout created
- Subscription updated
- Payment succeeded
- Payment failed
- Portal opened

Avoid logging sensitive payment information.

---

# Analytics

Track:

- Trial conversions
- Monthly recurring revenue
- Churn
- Upgrades
- Downgrades
- Failed payments

These metrics belong to analytics, not billing logic.

---

# Testing Strategy

Billing requires multiple testing layers.

Unit Tests:

- BillingService
- Entitlement logic
- Feature checks

Integration Tests:

- Stripe adapter
- Webhook processing
- Subscription synchronization

End-to-End Tests:

- Checkout
- Upgrade
- Downgrade
- Cancellation
- Trial conversion

Mock external providers where appropriate.

---

# Local Development

Use:

```
Stripe CLI
```

Capabilities:

- Local webhook forwarding
- Test events
- Simulated payments

Never develop billing directly against production data.

---

# Sandbox Environment

Maintain separate environments.

```
Development

↓

Stripe Test Mode
```

```
Production

↓

Stripe Live Mode
```

Never mix credentials between environments.

---

# Billing Checklist

Before shipping billing functionality:

- [ ] Provider adapter implemented
- [ ] Checkout flow tested
- [ ] Customer portal configured
- [ ] Webhooks verified
- [ ] Idempotency implemented
- [ ] Entitlements configured
- [ ] Usage limits tested
- [ ] Retry strategy implemented
- [ ] Tests passing
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Checking plan names throughout the application
- Trusting redirect URLs for payment success
- Storing payment card information
- Ignoring webhook verification
- Duplicating Stripe SDK usage outside the Billing package
- Hardcoding feature limits
- Blocking HTTP requests during billing operations
- Silent webhook failures

---

# Billing Definition of Done

A billing feature is complete only when:

- Provider integration is isolated.
- Webhooks are verified.
- Subscription state is synchronized.
- Entitlements are enforced.
- Usage limits are respected.
- Background jobs are configured.
- Tests pass.
- Documentation is updated.

---

# Summary

The Billing package provides a reusable, provider-independent foundation for monetizing every SaaS product built on FastForge.

Applications should never contain provider-specific billing logic.

Instead, they consume a stable BillingService interface that manages:

- Customers
- Plans
- Subscriptions
- Checkout
- Portals
- Webhooks
- Entitlements
- Usage limits

This architecture allows future migration from Stripe to another provider with minimal changes to application code, preserving long-term flexibility while enabling rapid product development today.