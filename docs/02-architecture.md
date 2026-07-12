# Architecture

> The Architecture Bible for FastForge

---

# Overview

FastForge is an opinionated monorepo designed to build multiple SaaS products using a shared engineering foundation.

The architecture emphasizes:

- Simplicity
- Reusability
- Modularity
- AI-assisted development
- Vendor independence
- Rapid product development

Every architectural decision should reduce the amount of work required for the next product.

---

# High-Level Architecture

```text
                    Browser
                       │
                       │
                Next.js Frontend
                       │
          REST / WebSocket / SSE
                       │
                FastAPI Backend
                       │
        ┌──────────────┼──────────────┐
        │              │              │
 PostgreSQL         Redis         Storage Adapter
 (Supabase)       (Upstash)    (Supabase/R2/S3)
        │              │
        │              │
        └────── Celery Workers ───────┘
```

---

# Design Principles

The platform follows several architectural principles.

## Modular

Everything reusable belongs inside packages.

Applications should remain thin.

---

## Layered

Every request follows the same path.

```
HTTP Request

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Repository

↓

Service

↓

Response
```

Every feature follows this pattern.

---

## Vendor Independent

Never expose third-party SDKs outside adapters.

Examples:

```
Stripe

↓

Billing Package

↓

Application
```

```
Supabase

↓

Storage Adapter

↓

Application
```

This allows changing providers without touching business logic.

---

## AI Friendly

Predictable folder structures.

Predictable naming.

Predictable dependencies.

AI should never have to guess.

---

# Monorepo Structure

```
fastforge/

apps/

packages/

docs/

docker/

scripts/

.github/
```

The repository contains two categories:

Applications

and

Packages.

---

# Applications

Applications are deployable services.

They contain minimal business logic.

They primarily orchestrate reusable packages.

```
apps/

api/

web/

worker/

docs/
```

---

## apps/api

FastAPI application.

Responsibilities:

- HTTP API
- Authentication
- Validation
- Dependency Injection
- OpenAPI
- Route registration

Should contain almost no business logic.

---

## apps/web

Next.js application.

Responsibilities:

- Landing Pages
- Dashboard
- Authentication UI
- Settings
- Billing
- Documentation UI

Uses APIs exposed by apps/api.

---

## apps/worker

Background processing.

Responsibilities:

- Celery workers
- Email processing
- Scheduled jobs
- Webhooks
- Cleanup tasks
- Long-running jobs

Workers should never expose HTTP endpoints.

---

## apps/docs

Documentation application.

Future enhancement.

Could expose documentation as a website.

---

# Packages

Packages contain reusable modules.

Applications consume packages.

Packages never depend on applications.

```
packages/

analytics/

api_keys/

auth/

billing/

cache/

common/

database/

logging/

mail/

notifications/

storage/

ui/
```

---

# Dependency Rule

Dependencies always point downward.

```
Application

↓

Package

↓

Common Package

↓

Infrastructure
```

Never invert dependencies.

Packages must remain reusable.

---

# Package Responsibilities

## auth

Responsible for:

- Login
- Registration
- OAuth
- JWT
- Refresh Tokens
- Password Reset
- Email Verification
- Sessions

Authentication logic should never exist outside this package.

---

## database

Responsible for:

- Base models
- SQLAlchemy configuration
- Session management
- Migrations
- Pagination
- Repository base classes

Every model should inherit from the shared BaseModel.

---

## billing

Responsible for:

- Stripe Checkout
- Customer Portal
- Webhooks
- Subscriptions
- Plans
- Invoices

No application should directly call the Stripe SDK.

---

## storage

Provides:

```
upload()

delete()

get_url()

generate_signed_url()
```

The implementation may change.

The interface should not.

---

## mail

Responsible for:

- SMTP
- Templates
- Queuing
- Future providers

Applications should only call MailService.

---

## analytics

Tracks:

- Signups
- Logins
- Purchases
- API Usage
- Product Metrics

Analytics providers remain replaceable.

---

## logging

Provides:

- Structured Logging
- Request Logging
- Audit Logging
- Error Logging

No module should implement logging independently.

---

## api_keys

Responsible for:

- Generation
- Rotation
- Validation
- Scopes
- Quotas
- Usage Metrics

Designed primarily for developer products.

---

## notifications

Supports:

- Email
- Slack
- Discord
- Webhooks

Future providers should be easy to add.

---

## cache

Responsible for:

- Redis
- Rate Limiting
- Session Cache
- Temporary Data
- OTP Storage

Applications should never directly interact with Redis.

---

## common

Shared code.

Examples:

- Exceptions
- Utilities
- Configuration
- Constants
- Enums
- Helpers
- Base Classes

Avoid duplicating utilities elsewhere.

---

## ui

Reusable frontend components.

Examples:

- Dashboard Layout
- Cards
- Tables
- Dialogs
- Form Components
- Navigation

Applications consume these components.

---

# Request Lifecycle

Every request follows the same lifecycle.

```
Browser

↓

Router

↓

Request Validation

↓

Authentication

↓

Authorization

↓

Service

↓

Repository

↓

Database

↓

Repository

↓

Service

↓

Response Model

↓

JSON Response
```

No business logic should exist before the Service layer.

---

# Service Layer

Services own business logic.

Responsibilities:

- validation
- permissions
- workflows
- orchestration
- calling repositories
- calling external providers
- transactions

Services should not know HTTP.

Services should not know SQL.

They coordinate work.

---

# Repository Layer

Repositories own persistence.

Responsibilities:

- CRUD
- Queries
- Pagination
- Filtering
- Transactions (where appropriate)

Repositories should never contain business rules.

Business rules belong in services.

---

# Model Layer

Models represent database tables.

Models should remain lightweight.

Avoid embedding business logic inside SQLAlchemy models.

Models define:

- columns
- relationships
- constraints
- indexes

Nothing more.

---

# Schema Layer

Pydantic schemas define:

- requests
- responses
- validation

Never expose SQLAlchemy models directly through the API.

Always return response schemas.

---

# Dependency Injection

Dependency Injection (DI) is the standard mechanism for connecting components.

Every dependency should be injected instead of instantiated directly.

Example:

```
Router

↓

Service

↓

Repository

↓

Database Session
```

Benefits:

- Easier testing
- Better modularity
- Lower coupling
- Easier mocking
- Consistent architecture

Never instantiate repositories or services directly inside routes.

Bad:

```python
service = UserService()
```

Good:

```python
service: UserService = Depends(get_user_service)
```

---

# Configuration Architecture

Configuration should have a single source of truth.

```
Environment Variables

↓

Pydantic Settings

↓

Application
```

Rules:

- Never use `os.getenv()` in application code.
- Never hardcode configuration values.
- Validate all configuration at startup.
- Fail fast if required settings are missing.

Example settings include:

- Database URL
- Redis URL
- JWT secrets
- Stripe keys
- SMTP credentials
- Storage configuration
- OAuth credentials

---

# Database Architecture

The platform uses PostgreSQL as the only relational database.

Initially:

- Supabase PostgreSQL

Future migration options:

- Neon
- Self-hosted PostgreSQL
- AWS RDS

Business logic should not be aware of the hosting provider.

---

# Database Design Principles

Every table should:

- Use UUID primary keys (prefer UUIDv7 when practical)
- Include timestamps
- Be normalized
- Define indexes explicitly
- Use foreign key constraints
- Support future growth

Standard columns:

```
id
created_at
updated_at
```

Optional columns:

```
deleted_at
created_by
updated_by
```

---

# UUID Strategy

UUIDs are the standard identifier across the platform.

Reasons:

- Globally unique
- Difficult to guess
- Easy data merging
- Distributed-friendly
- Better suited for APIs

Foreign keys also use UUIDs.

Example:

```
User

id (UUID)

↓

Project.owner_id (UUID)
```

Never mix integer IDs and UUIDs.

---

# Authentication Flow

Authentication is application-managed.

Providers:

- Email/Password
- Google OAuth
- GitHub OAuth

Future providers:

- Microsoft
- GitLab
- Apple

Authentication flow:

```
Login Request

↓

Credential Validation

↓

User Lookup

↓

Password Verification

↓

JWT Generation

↓

Refresh Token

↓

Response
```

Protected requests:

```
JWT

↓

Middleware

↓

User Resolution

↓

Permission Check

↓

Route
```

---

# Authorization

Authentication answers:

> Who is the user?

Authorization answers:

> What is the user allowed to do?

Authorization should be handled in the service layer.

Support for:

- Roles
- Permissions
- Organizations
- Teams
- Resource ownership

---

# API Key Architecture

Developer products require API-first authentication.

Flow:

```
Request

↓

API Key

↓

Hash Lookup

↓

User Resolution

↓

Rate Limit

↓

Quota Check

↓

Service
```

Keys should never be stored in plaintext.

Only hashes are persisted.

---

# Storage Architecture

Applications never communicate directly with storage providers.

Instead:

```
Application

↓

Storage Service

↓

Storage Adapter

↓

Provider
```

Current provider:

- Supabase Storage

Future providers:

- Cloudflare R2
- AWS S3
- MinIO

Migration should require changing only the adapter.

---

# Billing Architecture

Billing follows the same adapter pattern.

```
Application

↓

Billing Service

↓

Stripe Adapter

↓

Stripe API
```

Future providers:

- Paddle
- Lemon Squeezy

Business logic remains unchanged.

---

# Email Architecture

Email sending is asynchronous.

```
Application

↓

Mail Service

↓

Queue

↓

Worker

↓

SMTP Provider
```

Benefits:

- Faster API responses
- Automatic retries
- Better reliability

---

# Background Workers

Long-running tasks should never execute during an HTTP request.

Workers process:

- Emails
- Reports
- Image processing
- Cleanup jobs
- Scheduled tasks
- Webhook retries

Architecture:

```
HTTP Request

↓

Create Task

↓

Redis Queue

↓

Celery Worker

↓

Task Execution
```

Workers should be stateless.

---

# Caching Strategy

Redis is the shared cache.

Typical use cases:

- Sessions
- OTP
- Rate limiting
- Frequently accessed data
- Background task coordination

Avoid caching prematurely.

Cache only after identifying bottlenecks.

---

# Logging Architecture

Every request should generate structured logs.

Minimum fields:

- Timestamp
- Request ID
- User ID
- API Key ID
- Route
- HTTP Method
- Status Code
- Duration

Logs should be machine-readable.

---

# Error Handling

Errors should follow a consistent hierarchy.

```
AppError

├── ValidationError
├── AuthenticationError
├── AuthorizationError
├── NotFoundError
├── ConflictError
├── PaymentError
├── StorageError
└── ExternalServiceError
```

Never expose internal exceptions to clients.

Always return standardized error responses.

---

# Frontend Architecture

The frontend follows Next.js App Router conventions.

Responsibilities:

- UI
- Routing
- Forms
- Client state
- Server rendering
- API consumption

Business logic remains in the backend.

---

# State Management

Prefer server state over client state.

Priority:

1. Server Components
2. TanStack Query
3. React State
4. Zustand (only when necessary)

Avoid Redux unless a future product has a clear need.

---

# Package Dependency Graph

```
              apps/web
                  │
              apps/api
                  │
      ┌───────────┼───────────┐
      │           │           │
   auth      billing     storage
      │           │           │
      └────── common ─────────┘
                  │
        Infrastructure Layer
```

Dependencies should always point downward.

Circular dependencies are forbidden.

---

# Deployment Architecture

Development:

```
Docker Compose

↓

FastAPI

↓

Next.js

↓

Redis

↓

Celery

↓

Mailpit
```

Production:

```
Next.js

↓

Vercel

↓

FastAPI

↓

Railway

↓

Supabase PostgreSQL

↓

Upstash Redis

↓

Supabase Storage
```

Every component should be independently replaceable.

---

# Scalability Strategy

The platform is intentionally optimized for a solo developer.

Scaling priorities:

1. Better code reuse
2. Better automation
3. Better documentation
4. Better developer experience

Do not introduce microservices until there is a demonstrated operational need.

---

# Technology Evolution

Technology should evolve conservatively.

New dependencies require clear justification.

Questions to ask before adopting a new library:

- Does it reduce complexity?
- Is it actively maintained?
- Is it well documented?
- Will AI agents understand it?
- Does it reduce long-term maintenance?

If the answer is "no" to most of these, do not adopt it.

---

# Architecture Decision Process

Every significant architectural decision should be recorded as an ADR (Architecture Decision Record).

Examples:

```
ADR-001-use-fastapi.md
ADR-002-use-sqlalchemy.md
ADR-003-use-uuid.md
ADR-004-monorepo.md
```

This preserves context for future contributors and AI agents.

---

# Architecture Checklist

Every new feature should satisfy the following:

- [ ] Fits the existing folder structure
- [ ] Uses dependency injection
- [ ] Uses the service layer
- [ ] Uses the repository layer
- [ ] Includes request/response schemas
- [ ] Updates documentation if reusable
- [ ] Includes structured logging
- [ ] Includes proper error handling
- [ ] Adds tests where appropriate
- [ ] Follows naming conventions

---

# Summary

The architecture of FastForge is intentionally opinionated.

It prioritizes:

- Simplicity
- Reusability
- Consistency
- AI-assisted development
- Fast product delivery

Every design decision should support one overarching objective:

> **Build infrastructure once so future products require only business logic to be implemented.**