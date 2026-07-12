# Email Guide

> Reusable email architecture for every product built on FastForge.

---

# Purpose

Email is a core platform service.

Every product needs transactional emails.

Examples:

- Welcome emails
- Email verification
- Password reset
- Login alerts
- Organization invitations
- Billing notifications
- API key notifications
- Product notifications

The Email package should be implemented once and reused everywhere.

---

# Design Principles

The email system should be:

- Provider independent
- Asynchronous
- Template driven
- Easy to test
- Easy to extend

Applications should never communicate directly with an email provider.

---

# Responsibilities

The Email package owns:

- Sending emails
- Rendering templates
- Provider adapters
- Queue integration
- Attachments
- Retry handling
- Email logging

Applications communicate only with `EmailService`.

---

# Architecture

```text
Application

↓

EmailService

↓

EmailProvider

↓

Provider Adapter

↓

SMTP / API Provider

↓

Recipient
```

The application layer never imports provider SDKs.

---

# Supported Providers

Initial:

- SMTP

Future:

- Resend
- Postmark
- SendGrid
- Amazon SES
- Mailgun

Changing providers should require only configuration changes.

---

# Email Provider Interface

Every provider implements the same interface.

Required methods:

```python
send()

send_batch()

validate_configuration()
```

Applications should never depend on provider-specific methods.

---

# Transactional Emails

Examples:

- Verify Email
- Reset Password
- Welcome
- Magic Link
- Organization Invitation
- Billing Receipt
- Subscription Changed
- Payment Failed

Transactional emails are sent automatically by the application.

---

# Marketing Emails

Marketing emails belong to a separate system.

Examples:

- Product updates
- Feature announcements
- Newsletters
- Promotions

Do not mix transactional and marketing email logic.

---

# Email Flow

```text
Application

↓

EmailService

↓

Queue

↓

Worker

↓

Provider

↓

Recipient
```

HTTP requests should never wait for email delivery.

---

# Background Jobs

Every email should be queued.

Examples:

- Welcome email
- Verification email
- Invoice email
- Notification digest

Sending emails synchronously increases request latency and failure risk.

---

# Templates

Emails should be template-driven.

Examples:

```text
welcome

verify_email

password_reset

invite

invoice

subscription_updated
```

Avoid constructing HTML inside application code.

---

# Template Organization

Recommended structure:

```text
templates/

emails/

welcome/

verify-email/

password-reset/

billing/

notifications/
```

Keep templates organized by purpose.

---

# Template Variables

Pass structured data to templates.

Example:

```python
{
    "name": "John",
    "organization": "Acme",
    "verification_url": "...",
}
```

Avoid passing raw database models.

---

# Email Layout

Every email should share a common layout.

Common sections:

- Logo
- Header
- Body
- Primary Action
- Footer
- Support Information

Consistency improves user experience.

---

# Plain Text Version

Every HTML email should include a plain text alternative.

Benefits:

- Accessibility
- Better spam scores
- Legacy client support

---

# Branding

Branding should be configurable.

Examples:

- Logo
- Primary color
- Product name
- Support email
- Website URL

Avoid hardcoding branding into templates.

---

# Sender Configuration

Configuration should include:

```text
From Name

From Address

Reply-To

Support Address
```

Sender information should come from configuration.

---

# Attachments

Support optional attachments.

Examples:

- PDF invoices
- CSV exports
- Reports

Large attachments should be generated before queuing the email.

---

# Email Validation

Validate recipient addresses before sending.

Reject:

- Invalid syntax
- Empty addresses

Application-specific rules may perform additional validation.

---

# Retry Strategy

Temporary failures:

- Retry automatically

Permanent failures:

- Log
- Mark as failed
- Alert if necessary

Retries should use exponential backoff.

---

# Idempotency

Sending the same event multiple times should not generate duplicate emails unnecessarily.

Examples:

- Duplicate webhook
- Queue retry

Use idempotency where repeated emails would confuse users.

---

# Logging

Log email events.

Examples:

- Queued
- Sent
- Failed
- Retried
- Delivered (future)

Do not log email bodies containing sensitive information.

---

# Delivery Status

Track delivery lifecycle.

Possible states:

```text
Queued

Sending

Sent

Delivered

Failed

Bounced

Complained
```

Provider capabilities may vary.

---

# Bounce Handling

Support provider webhooks for:

- Hard bounce
- Soft bounce

Repeated hard bounces should disable future deliveries to that address until corrected.

---

# Complaint Handling

Support spam complaint notifications.

Future logic may:

- Unsubscribe marketing emails
- Alert administrators
- Suspend delivery

Transactional email policies may differ.

---

# Security

Never include secrets inside email links.

Use secure, expiring tokens for:

- Password reset
- Email verification
- Invitations
- Magic links

Tokens should always expire.

---

# Localization

Templates should support localization.

Structure example:

```text
en/

fr/

de/

es/
```

Language selection should depend on user preferences where available.

---

# Email Preferences

Users should be able to manage non-essential email preferences.

Examples:

- Product updates
- Weekly summaries
- Marketing emails
- Security notifications (optional where applicable)

Transactional emails should not be disabled if they are required for account security or legal compliance.

---

# Unsubscribe Handling

Marketing emails should always include an unsubscribe mechanism.

Flow:

```text
Email

↓

Unsubscribe Link

↓

Preference Updated

↓

Confirmation
```

Transactional emails should not contain unsubscribe links unless legally required.

---

# Notification Integration

The Email package should integrate with the Notification package.

Example:

```text
Application

↓

Notification Service

↓

Email Channel

↓

Email Service

↓

Queue

↓

Provider
```

Applications should not call multiple notification channels directly.

---

# Scheduling

Support scheduled email delivery.

Examples:

- Weekly digest
- Trial ending reminder
- Subscription renewal reminder
- Daily reports

Scheduling belongs to background workers.

---

# Digest Emails

Support batched notifications.

Examples:

- Daily summary
- Weekly activity
- Monthly usage report

Batching reduces email fatigue.

---

# Rate Limiting

Prevent excessive email sending.

Examples:

```text
Password Reset

3 emails/hour
```

```text
Verification Email

5 emails/day
```

Rate limiting should use Redis.

---

# Monitoring

Track operational metrics.

Examples:

- Emails queued
- Emails sent
- Failed deliveries
- Bounce rate
- Complaint rate
- Average delivery time

These metrics help maintain email reliability.

---

# Analytics

Measure business-related metrics.

Examples:

- Verification completion rate
- Welcome email engagement
- Trial reminder conversion
- Billing reminder effectiveness

Analytics should remain separate from delivery logic.

---

# Error Handling

Standardized errors:

```text
EMAIL_PROVIDER_UNAVAILABLE

INVALID_EMAIL

TEMPLATE_NOT_FOUND

SEND_FAILED

ATTACHMENT_TOO_LARGE
```

Do not expose provider-specific exceptions to application code.

---

# Configuration

Email configuration should include:

```text
Provider

SMTP Host

SMTP Port

Username

Password

TLS Enabled

From Name

From Address

Reply-To

Support Email
```

Use Pydantic Settings.

Never hardcode credentials.

---

# Local Development

For local development, support:

- Mailpit
- MailHog
- Local SMTP server

Developers should be able to inspect outgoing emails without using a real provider.

---

# Testing Strategy

## Unit Tests

Test:

- EmailService
- Template rendering
- Provider adapters

Mock external providers.

---

## Integration Tests

Test:

- Queue integration
- SMTP provider
- Template rendering
- Retry logic

---

## End-to-End Tests

Critical workflows:

- User registration
- Email verification
- Password reset
- Organization invitation
- Billing notifications

Verify that emails are generated correctly and contain expected links.

---

# Performance

Optimize:

- Queue throughput
- Template rendering
- Batch sending
- Provider connection reuse

Email sending should scale independently from web requests.

---

# Accessibility

Email templates should:

- Use semantic HTML
- Include meaningful alt text
- Support dark mode where practical
- Be readable without images

Accessibility improves deliverability and user experience.

---

# Documentation

Every email template should document:

- Purpose
- Trigger event
- Required template variables
- Expected recipient

Documentation should evolve with new templates.

---

# Email Checklist

Before shipping an email feature:

- [ ] Template created
- [ ] Plain text version included
- [ ] Localization supported (if applicable)
- [ ] Queue integration configured
- [ ] Retry strategy implemented
- [ ] Logging added
- [ ] Rate limiting applied
- [ ] Tests passing
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Sending emails synchronously
- Hardcoding HTML in services
- Duplicating templates
- Exposing provider SDKs to applications
- Logging sensitive email contents
- Embedding secrets in email links
- Skipping plain text versions
- Ignoring delivery failures

---

# Email Definition of Done

An email feature is complete only when:

- Template is reusable.
- Delivery is asynchronous.
- Provider abstraction is respected.
- Retries are implemented.
- Logging is enabled.
- Tests pass.
- Documentation is updated.

---

# Summary

The Email package provides a reusable, provider-independent system for transactional email delivery.

Applications communicate only with `EmailService`, while providers, queues, templates, retries, and delivery concerns remain encapsulated.

This architecture ensures:

- Consistent email behavior
- Fast HTTP responses
- Easy provider replacement
- Reliable delivery
- Reusable templates
- Maintainable code

Every future SaaS product should inherit this email infrastructure without modification.