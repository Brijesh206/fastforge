# Notification Guide

> Reusable notification architecture for every product built on FastForge.

---

# Purpose

Notifications are a cross-cutting platform service.

Applications should never send notifications directly through email, SMS, push, or in-app channels.

Instead, every notification should pass through a unified `NotificationService`.

This allows:

- Multiple delivery channels
- User preferences
- Retry handling
- Analytics
- Future channel expansion

Build it once and reuse it across every product.

---

# Design Principles

The notification system should be:

- Channel independent
- Event driven
- Extensible
- Reliable
- Observable

Applications emit notification events.

The Notification package decides how those events are delivered.

---

# Responsibilities

The Notification package owns:

- Notification routing
- Channel selection
- User preferences
- Delivery orchestration
- Scheduling
- Retry logic
- Notification history
- Event logging

Applications should never call Email, SMS, or Push providers directly.

---

# Architecture

```text
Application

↓

NotificationService

↓

Notification Router

↓

Channel

↓

Provider

↓

Recipient
```

Each channel has its own provider implementation.

---

# Supported Channels

Initial:

- Email
- In-App

Future:

- SMS
- Push Notifications
- Slack
- Discord
- Microsoft Teams
- Webhooks

Applications should not change when new channels are added.

---

# Notification Flow

```text
Business Event

↓

NotificationService

↓

Resolve User Preferences

↓

Determine Channels

↓

Queue Notifications

↓

Workers

↓

Providers

↓

Delivery
```

Notifications should always be asynchronous.

---

# Notification Types

Examples:

Authentication:

- Verify Email
- Password Reset
- Login Alert

Billing:

- Payment Success
- Payment Failed
- Trial Ending
- Subscription Updated

Projects:

- Project Created
- Project Deleted
- API Key Created

System:

- Maintenance
- Security Alert
- Feature Announcement

Each notification type should be defined centrally.

---

# Notification Model

Recommended fields:

```text
id

type

recipient_id

organization_id

title

body

status

created_at

sent_at

read_at
```

Optional:

```text
metadata

priority

expires_at
```

---

# Notification Status

Supported states:

```text
Queued

Processing

Sent

Delivered

Read

Failed
```

Not every channel supports every state.

---

# Notification Channels

Each notification may use one or more channels.

Example:

```text
Security Alert

↓

Email

+

In-App
```

Another example:

```text
Weekly Digest

↓

Email Only
```

Routing belongs to the Notification package.

---

# Channel Providers

Each channel implements a common interface.

Example:

```python
NotificationChannel
```

Methods:

```python
send()

validate()

supports()
```

Applications never import channel providers directly.

---

# User Preferences

Users should control non-critical notifications.

Example preferences:

```text
Billing

Security

Projects

Marketing

System Updates
```

Preferences should be stored centrally.

---

# Critical Notifications

Critical notifications should bypass user preferences where appropriate.

Examples:

- Password Reset
- Login Alert
- Payment Failure
- Email Verification

Security and compliance requirements take precedence over preferences.

---

# Notification Templates

Templates should be reusable.

Structure:

```text
notifications/

billing/

security/

projects/

system/
```

Avoid hardcoded notification content.

---

# Template Variables

Pass structured data.

Example:

```python
{
    "project_name": "...",
    "user_name": "...",
    "billing_url": "...",
}
```

Avoid exposing database models directly.

---

# Notification Priority

Recommended priorities:

```text
Low

Normal

High

Critical
```

Priority may influence:

- Delivery order
- Retry policy
- Channels

---

# Scheduling

Support scheduled notifications.

Examples:

- Trial ending tomorrow
- Weekly digest
- Monthly usage summary

Scheduling belongs to workers.

---

# Delayed Notifications

Examples:

```text
User Registers

↓

Wait 3 Days

↓

Send Tips Email
```

The Notification package should support delayed execution.

---

# Batch Notifications

Examples:

- Daily summary
- Weekly report
- Multiple project updates

Avoid spamming users with repetitive notifications.

---

# In-App Notifications

Store in the database.

Users should be able to:

- View notifications
- Mark as read
- Mark all as read
- Delete (optional)

In-app notifications should remain available across devices.

---

# Notification Center

Every product should have a reusable notification center.

Capabilities:

- List notifications
- Filter unread
- Search (future)
- Pagination
- Mark as read

The UI should be reusable across products.

---

# Read Tracking

Store:

```text
read_at
```

Avoid:

```text
is_read
```

A timestamp provides more useful audit information.

---

# Expiration

Some notifications may expire.

Examples:

- Temporary alerts
- Invitations
- Promotional announcements

Expired notifications may be archived or hidden.

---

# Event Driven Design

Applications emit events.

Examples:

```text
UserCreated

SubscriptionUpdated

ProjectDeleted

ApiKeyGenerated
```

The Notification package subscribes to these events and decides how to notify users.

This keeps business logic clean and decoupled.

---

# Queue Integration

Every notification should be queued before delivery.

Workers process notifications independently from web requests.

This improves reliability and scalability.

---

# Retry Strategy

Notification delivery should automatically retry temporary failures.

Recommended strategy:

```text
Attempt 1

↓

30 seconds

↓

Attempt 2

↓

2 minutes

↓

Attempt 3

↓

10 minutes

↓

Attempt 4

↓

1 hour

↓

Mark Failed
```

Use exponential backoff.

Permanent failures should not be retried indefinitely.

---

# Dead Letter Queue

Notifications that repeatedly fail should be moved to a Dead Letter Queue (DLQ).

Benefits:

- Prevent endless retries
- Allow manual inspection
- Enable replay after fixes

Critical notifications should be reviewed periodically.

---

# Failure Handling

Possible failure reasons:

- Provider unavailable
- Invalid recipient
- Rate limit exceeded
- Network timeout
- Template rendering failure

Failures should be logged with enough context for debugging.

---

# Provider Adapters

Each delivery channel should expose an adapter.

Examples:

```text
Email Adapter

↓

Email Provider
```

```text
SMS Adapter

↓

SMS Provider
```

```text
Push Adapter

↓

Push Provider
```

Adapters isolate provider-specific implementations.

---

# Notification Routing

Routing decisions should consider:

- User preferences
- Notification priority
- Available channels
- Provider availability

The application should never decide delivery channels directly.

---

# Deduplication

Avoid sending duplicate notifications.

Examples:

- Multiple identical webhook events
- Repeated background jobs
- Duplicate retries

Deduplication should be configurable by notification type.

---

# Analytics

Track notification metrics.

Examples:

- Notifications sent
- Delivery success rate
- Open/read rate
- Click-through rate (future)
- Delivery latency

These metrics support product improvements.

---

# Monitoring

Monitor:

- Queue depth
- Worker health
- Provider failures
- Retry count
- Failed notifications
- Delivery latency

Monitoring should trigger alerts for persistent failures.

---

# Audit Logging

Log significant events.

Examples:

- Notification queued
- Notification delivered
- Notification failed
- Notification read
- Notification dismissed

Avoid logging sensitive notification content.

---

# Security

Protect notification data.

Never expose:

- Verification tokens
- Password reset tokens
- Internal metadata
- Sensitive business information

Notifications should contain only the information necessary for the recipient.

---

# Localization

Support localized notification content.

Structure:

```text
en/

fr/

de/

es/
```

Language selection should follow user preferences where available.

---

# Configuration

Notification configuration should include:

```text
Enabled Channels

Default Channel

Retry Policy

Queue Name

Priority Rules

Digest Schedule
```

Configuration should be centralized using Pydantic Settings.

---

# Local Development

Support local testing using:

- Console provider
- Local email provider
- Mock push provider

Developers should be able to verify notification flows without external services.

---

# Testing Strategy

## Unit Tests

Test:

- NotificationService
- Routing logic
- Preference resolution
- Template rendering

Mock channel providers.

---

## Integration Tests

Test:

- Queue integration
- Channel adapters
- Retry logic
- Notification persistence

---

## End-to-End Tests

Critical workflows:

- User registration
- Password reset
- Billing events
- Project invitations
- Security alerts

Verify that notifications reach the expected channels.

---

# Performance

Optimize:

- Batch processing
- Queue throughput
- Provider connection reuse
- Template caching

Notification processing should scale horizontally.

---

# Documentation

Each notification type should document:

- Trigger event
- Supported channels
- Priority
- Required template variables
- User preference category

Documentation should remain synchronized with implementation.

---

# Notification Checklist

Before shipping a notification feature:

- [ ] Notification type defined
- [ ] Template created
- [ ] Routing configured
- [ ] Queue integration complete
- [ ] Retry policy configured
- [ ] User preferences respected
- [ ] Logging added
- [ ] Monitoring enabled
- [ ] Tests passing
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Calling providers directly from application code
- Synchronous notification delivery
- Duplicating notification templates
- Ignoring user preferences
- Logging sensitive notification content
- Hardcoding delivery channels
- Retrying permanent failures indefinitely
- Embedding business logic in notification templates

---

# Notification Definition of Done

A notification feature is complete only when:

- Notification type is defined.
- Templates are reusable.
- Routing is centralized.
- Delivery is asynchronous.
- Retries are configured.
- User preferences are respected.
- Monitoring is enabled.
- Tests pass.
- Documentation is updated.

---

# Summary

The Notification package provides a unified, event-driven system for delivering messages across multiple channels.

Applications emit business events, while the Notification package determines:

- Who should be notified
- Which channels should be used
- When notifications should be delivered
- How failures should be handled

This architecture keeps products decoupled from delivery providers and allows new channels to be added without changing application logic.

Every future SaaS product should reuse this notification infrastructure to ensure consistency, scalability, and maintainability.