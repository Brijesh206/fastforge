# 🚀 FastForge

> **Build Once. Reuse Forever. Ship Fast.**

An opinionated, AI-first monorepo platform for building and launching developer tools and SaaS products quickly.

The goal of this platform is to eliminate repetitive engineering work by providing reusable modules for authentication, billing, storage, emails, background jobs, API keys, analytics, logging, and deployment.

This repository is not a generic boilerplate.

It is an evolving internal platform that becomes more valuable with every product built on top of it.

---

# Vision

This platform exists to solve one problem:

> **Reduce the time required to launch a production-ready SaaS from weeks to days.**

Instead of rebuilding authentication, payments, user management, dashboards, Docker configuration, deployment pipelines, and integrations for every new idea, we invest once in a reusable platform.

Every product improves the platform.

Every improvement benefits future products.

---

# Core Principles

## Ship Fast

Shipping is more important than perfect architecture.

Launch early.

Collect feedback.

Improve based on real users.

---

## Build Once, Reuse Forever

If something has been implemented twice, it probably belongs in a shared package.

Examples include:

- Authentication
- Billing
- User Management
- API Keys
- Storage
- Emails
- Logging
- Analytics
- Notifications
- Rate Limiting

---

## AI First

The repository is designed for AI coding agents.

Every architectural decision should make it easier for tools such as Claude Code, Codex, Cursor, Gemini CLI, and future coding assistants to understand the project and generate consistent code.

Documentation is treated as part of the product.

---

## Simplicity Over Complexity

Avoid unnecessary complexity.

Do not introduce technology unless there is a clear benefit.

Examples of technologies intentionally excluded:

- Kubernetes
- Microservices
- Event Sourcing
- CQRS
- GraphQL
- Service Mesh
- Multiple Databases

The platform should remain easy for a solo developer to maintain.

---

## Modular Design

Every reusable feature lives in its own package.

Applications consume packages.

Packages should not depend on application code.

---

# Goals

- Launch multiple SaaS products every month
- Reduce development time for new ideas
- Keep maintenance costs low
- Minimize vendor lock-in
- Build portable infrastructure
- Maintain clean architecture
- Enable AI-assisted development
- Scale only when products require it

---

# Technology Stack

## Frontend

- Next.js (App Router)
- TypeScript
- TailwindCSS
- shadcn/ui
- Magic UI
- TanStack Query
- React Hook Form
- Zod
- Framer Motion

---

## Backend

- FastAPI
- SQLAlchemy 2
- Pydantic v2
- Alembic
- uv
- Celery
- Redis

---

## Database

PostgreSQL

Initially hosted on Supabase.

Future migration should require zero application changes.

---

## Authentication

Application managed.

Not Supabase Auth.

Supports:

- Email/Password
- Google OAuth
- GitHub OAuth
- JWT
- Refresh Tokens
- API Keys

---

## Billing

Stripe

Supports:

- Subscriptions
- One-time payments
- Checkout
- Customer Portal
- Coupons
- Usage Billing (future)

---

## Storage

Initially

Supabase Storage

Future

Cloudflare R2

Accessed only through the Storage Adapter.

---

## Cache

Redis

Used for:

- Sessions
- OTP
- Rate Limiting
- Celery
- Caching

---

## Deployment

Frontend

Vercel

Backend

Railway

Database

Supabase PostgreSQL

Redis

Upstash

Monitoring

Sentry

Analytics

PostHog

DNS

Cloudflare

---

# Repository Structure

```
fastforge/

├── apps/
│   ├── api/
│   ├── web/
│   ├── worker/
│   └── docs/
│
├── packages/
│   ├── analytics/
│   ├── api_keys/
│   ├── auth/
│   ├── billing/
│   ├── cache/
│   ├── common/
│   ├── database/
│   ├── logging/
│   ├── mail/
│   ├── notifications/
│   ├── storage/
│   └── ui/
│
├── docker/
├── scripts/
├── docs/
├── .github/
├── README.md
└── AGENTS.md
```

---

# Architecture

```
                +---------------------+
                |     Next.js App     |
                +----------+----------+
                           |
                           |
                    REST / WebSocket
                           |
                           v
                +---------------------+
                |      FastAPI        |
                +----------+----------+
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     PostgreSQL         Redis         Object Storage
     (Supabase)      (Upstash)       (Supabase/R2)
          |
          v
      SQLAlchemy
```

---

# Shared Packages

Every reusable feature should exist as an independent package.

Current packages:

## auth

Authentication

Authorization

OAuth

JWT

API Keys

---

## billing

Stripe integration

Subscriptions

Invoices

Checkout

Customer Portal

---

## database

Database models

Repositories

Migrations

Pagination

Soft Delete

Base classes

---

## storage

File uploads

Signed URLs

Storage adapters

---

## mail

SMTP

Templates

Queue integration

---

## analytics

Application events

Business metrics

Usage tracking

---

## logging

Structured logging

Request logging

Audit logs

---

## api_keys

Developer API authentication

Scopes

Usage

Rate Limits

---

## notifications

Email

Slack

Discord

Webhook

---

## common

Shared utilities

Configuration

Exceptions

Helpers

Constants

---

# Development Workflow

1. Find an idea.
2. Validate demand.
3. Clone the platform.
4. Rename the project.
5. Configure branding.
6. Build only the business logic.
7. Deploy.
8. Launch.
9. Measure.
10. Iterate or archive.

The platform should already provide everything else.

---

# Development Philosophy

Every new feature should answer one question:

> **Will another product need this?**

If yes:

Move it into a package.

If no:

Keep it inside the application.

---

# Documentation

The documentation directory acts as the engineering handbook.

```
docs/

01-vision.md

02-architecture.md

03-tech-stack.md

04-folder-structure.md

05-backend.md

06-frontend.md

07-database.md

08-authentication.md

09-billing.md

10-storage.md

11-email.md

12-workers.md

13-api-keys.md

14-deployment.md

15-roadmap.md

16-product-workflow.md

coding-standards.md

feature-template.md

product-checklist.md
```

---

# Coding Standards

The repository follows strict engineering conventions.

Highlights:

- UUID primary keys (UUIDv7 when practical)
- UTC timestamps
- Service layer architecture
- Repository pattern
- Dependency Injection
- Type hints everywhere
- Async where appropriate
- No business logic in routes
- No direct database access from routes
- Configuration via Pydantic Settings
- Structured logging
- Consistent error handling

Detailed rules are documented in `AGENTS.md`.

---

# Product Lifecycle

```
Idea
   │
Validate
   │
Clone Platform
   │
Implement Business Logic
   │
Deploy
   │
Launch
   │
Collect Feedback
   │
Iterate
   │
or
   │
Archive
```

---

# Long-Term Vision

The platform should eventually become capable of creating a production-ready SaaS with:

- Authentication
- Billing
- Dashboard
- Landing Page
- API
- Background Workers
- Storage
- Email
- Analytics
- Monitoring
- CI/CD

already configured.

At that point, launching a new product should require writing only the domain-specific business logic.

---

# Success Metrics

The platform is successful if:

- A new SaaS can be started in less than one day.
- Shared modules continuously improve.
- AI coding agents produce consistent code.
- Products share architecture and conventions.
- Engineering effort is focused on product differentiation rather than infrastructure.

---

# License

Private Internal Platform

This repository is intended to serve as the foundation for all future products developed using the FastForge architecture.