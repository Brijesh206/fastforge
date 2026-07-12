# Technology Stack

> Technology decisions, rationale, and standards for FastForge.

---

# Purpose

This document defines the approved technology stack for FastForge.

The objective is **not** to use the newest technologies.

The objective is to maximize:

- Development Speed
- Stability
- AI Compatibility
- Community Support
- Long-Term Maintainability

Every technology listed here has been intentionally selected.

Introducing new technologies requires strong justification.

---

# Design Philosophy

When choosing technologies we prioritize:

1. Simplicity
2. Excellent Documentation
3. Large Community
4. Active Maintenance
5. AI Familiarity
6. Long-Term Stability

Never adopt a technology simply because it is trending.

---

# Overall Stack

| Layer | Technology |
|---------|------------|
| Monorepo | Turborepo |
| Frontend | Next.js |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Components | shadcn/ui + Magic UI |
| Backend | FastAPI |
| Python | Python 3.13+ |
| Package Manager | uv |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Validation | Pydantic v2 |
| Cache | Redis |
| Queue | Celery |
| Storage | Supabase Storage |
| Payments | Stripe |
| Emails | SMTP (initially) |
| Authentication | Application Managed |
| Deployment | Docker |
| Reverse Proxy | Optional (Nginx/Caddy) |
| Monitoring | Sentry |
| Analytics | PostHog |
| CI/CD | GitHub Actions |

---

# Monorepo

## Turborepo

Why:

- Fast builds
- Task caching
- Monorepo support
- Easy package sharing
- Excellent Next.js integration

Responsibilities:

- Build orchestration
- Task execution
- Caching
- Workspace management

---

# Frontend

## Next.js

Version:

Latest stable App Router.

Reasons:

- Server Components
- SEO
- Excellent React ecosystem
- API routes if needed
- Vercel integration
- AI familiarity

The frontend should remain mostly responsible for UI.

Business logic belongs in FastAPI.

---

## React

Use functional components only.

Avoid class components.

Prefer composition over inheritance.

---

## TypeScript

Always enabled.

Avoid JavaScript.

Use strict mode.

Never disable type checking.

---

## Tailwind CSS

Tailwind is the only styling system.

Reasons:

- Speed
- Consistency
- Small bundle
- AI friendliness

Avoid writing custom CSS unless necessary.

---

## shadcn/ui

Primary component library.

Reasons:

- Copy-paste components
- No vendor lock-in
- Accessible
- Excellent customization

Never install another UI framework without discussion.

---

## Magic UI

Used for:

- Marketing pages
- Landing pages
- Hero sections
- Animations

Not for core business components.

---

## TanStack Query

Purpose:

Server state management.

Responsibilities:

- API requests
- Cache
- Refetching
- Synchronization

Avoid storing server data in React state.

---

## React Hook Form

Standard form library.

Reasons:

- Excellent performance
- Easy validation
- Zod integration

All forms should use React Hook Form.

---

## Zod

Frontend validation.

Never rely on frontend validation alone.

Backend validation is mandatory.

---

## Framer Motion

Used only for:

- Micro interactions
- Dashboard animations
- Landing page polish

Avoid excessive animations.

---

# Backend

## FastAPI

Primary backend framework.

Reasons:

- Performance
- Async support
- Type hints
- OpenAPI
- Pydantic integration
- AI familiarity

FastAPI should remain the only backend framework.

---

## Python

Version:

Python 3.13+

Reasons:

- Modern typing
- Performance improvements
- Better tooling

---

## uv

Standard package manager.

Reasons:

- Extremely fast
- Lockfile support
- Modern dependency management

Never use pip directly.

---

## SQLAlchemy 2

Reasons:

- Mature
- Flexible
- Production proven
- Excellent async support

Always use SQLAlchemy 2 syntax.

Avoid deprecated APIs.

---

## Alembic

Migration tool.

Every schema change requires a migration.

Never modify production databases manually.

---

## Pydantic v2

Responsible for:

- Validation
- Serialization
- Configuration

Every request and response should use Pydantic models.

---

# Database

## PostgreSQL

Chosen because:

- Mature
- Reliable
- Rich ecosystem
- JSON support
- Excellent indexing
- Widely supported

Initially hosted on Supabase.

Migration should be transparent.

---

## UUID

Primary keys use UUID.

Prefer UUIDv7.

Fallback:

UUIDv4.

Reasons:

- Security
- Global uniqueness
- Easier data merging

---

# Cache

## Redis

Responsibilities:

- Sessions
- OTP
- Rate limiting
- Celery broker
- Temporary cache

Applications should access Redis through shared abstractions.

---

# Background Jobs

## Celery

Reasons:

- Mature
- Reliable
- Scalable

Responsibilities:

- Email sending
- Cleanup
- Reports
- Webhooks
- Long-running jobs

Never perform long-running work inside HTTP requests.

---

# Authentication

Authentication is application-managed.

Providers:

- Email
- Google
- GitHub

Reasons:

- Vendor independence
- Easier migrations
- Full control

Avoid Supabase Auth.

---

# Storage

Initially:

Supabase Storage.

Future:

- Cloudflare R2
- AWS S3
- MinIO

Applications communicate only through StorageService.

---

# Payments

Stripe.

Reasons:

- Mature
- Excellent API
- Subscription support
- Global adoption

Future providers should be implemented through adapters.

---

# Email

Initially:

SMTP.

Future:

- Resend
- Postmark

Applications call MailService only.

---

# Monitoring

## Sentry

Responsibilities:

- Exceptions
- Stack traces
- Performance

Every production deployment should include Sentry.

---

# Analytics

## PostHog

Tracks:

- Signups
- Activation
- Purchases
- Retention
- Feature usage

Business analytics should remain provider-independent.

---

# Deployment

## Docker

Every service must run inside Docker.

Development and production should remain as similar as possible.

---

## Docker Compose

Development orchestration.

Responsible for:

- API
- Frontend
- Redis
- Celery
- Mailpit

Database is hosted externally.

---

# CI/CD

GitHub Actions.

Standard workflow:

```
Lint

↓

Tests

↓

Build

↓

Deploy
```

Every pull request should pass CI before merge.

---

# Hosting

| Service | Provider |
|----------|----------|
| Frontend | Vercel |
| Backend | Railway |
| Database | Supabase |
| Redis | Upstash |
| Storage | Supabase |
| DNS | Cloudflare |
| Monitoring | Sentry |
| Analytics | PostHog |

---

# Libraries to Avoid

Avoid introducing:

- Redux
- MobX
- GraphQL
- Django
- Flask
- Prisma (Python)
- Kubernetes
- Microservices

Unless there is a documented architectural decision.

---

# Technology Upgrade Policy

Dependencies should only be upgraded when:

- Security fixes
- Performance improvements
- Long-term support
- Breaking issues

Avoid upgrading simply because a newer version exists.

---

# Decision Checklist

Before introducing a new dependency, ask:

- Does it simplify development?
- Is it actively maintained?
- Is it well documented?
- Is it AI-friendly?
- Does it reduce long-term maintenance?
- Can it be replaced easily?

If most answers are "no", do not adopt it.

---

# Summary

The technology stack is intentionally conservative.

The goal is not to chase trends.

The goal is to build products quickly, maintain them easily, and maximize long-term engineering leverage.

Technology should disappear into the background so that development effort can focus on solving customer problems.