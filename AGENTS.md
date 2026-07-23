# AGENTS.md

> AI Engineering Guide for FastForge

This document defines the engineering standards, architectural principles, and coding rules that **all AI coding agents** (Claude Code, Codex, Cursor, Gemini CLI, etc.) must follow when contributing to this repository.

The goal is to ensure that every piece of generated code is consistent, maintainable, and production-ready.

---

# Project Overview

FastForge is an opinionated monorepo for building developer tools and SaaS products rapidly.

This repository is **not** a generic boilerplate.

It is an internal engineering platform that grows stronger with every product built on top of it.

Every reusable feature should eventually become a shared package.

---

# Primary Goal

Reduce the time required to launch a production-ready SaaS from **weeks** to **days**.

The platform should provide everything except business logic.

---

# Engineering Philosophy

Always optimize for:

1. Simplicity
2. Reusability
3. Maintainability
4. AI Readability
5. Developer Experience
6. Shipping Speed

Never optimize for unnecessary complexity.

---

# Golden Rules

## Rule 1

Never duplicate business logic.

If similar logic appears twice, extract it into a shared package.

---

## Rule 2

Routes must never contain business logic.

Routes only:

- Validate request
- Call service
- Return response

Nothing else.

---

## Rule 3

Services own business logic.

Services are responsible for:

- validation
- permissions
- workflows
- orchestration
- calling repositories
- emitting events

---

## Rule 4

Repositories own database access.

Repositories are the only layer allowed to interact with SQLAlchemy.

Never execute queries directly inside:

- Routes
- Services
- Middleware

---

## Rule 5

Packages must never depend on application code.

Applications consume packages.

Packages remain reusable.

---

## Rule 6

Always write code that another future product can reuse.

---

# Architecture

Every request should follow:

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

Never bypass layers.

---

# Monorepo Structure

```
apps/

packages/

docs/

docker/

scripts/
```

Applications should remain thin.

Reusable logic belongs inside packages.

---

# Backend Stack

- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic v2
- Redis
- Celery
- uv

Do not introduce new frameworks without strong justification.

---

# Frontend Stack

- Next.js
- App Router
- TypeScript
- TailwindCSS
- shadcn/ui
- Magic UI
- React Hook Form
- TanStack Query
- Zod

Do not introduce Redux unless explicitly requested.

---

# Folder Rules

Every feature should have a predictable structure.

Example:

```
users/

router.py

service.py

repository.py

schemas.py

models.py

dependencies.py

exceptions.py

constants.py
```

Avoid mixing responsibilities.

---

# Naming Conventions

Use consistent names.

Good:

```
UserService

UserRepository

UserRouter

UserSchema

UserCreateSchema

UserUpdateSchema

UserResponseSchema
```

Avoid abbreviations.

---

# Python Rules

Use:

- Python 3.13+
- Type hints everywhere
- Async where appropriate
- Dataclasses only when appropriate
- Pydantic for validation

Never use:

```
Any
```

unless absolutely necessary.

---

# Database Rules

Use:

UUID primary keys.

Prefer UUIDv7 whenever ecosystem support is stable.

Otherwise use UUIDv4.

Every model should inherit from BaseModel.

Every table should contain:

```
id

created_at

updated_at
```

Soft delete should be supported where appropriate.

---

# SQLAlchemy Rules

Always use SQLAlchemy 2 syntax.

Never use deprecated APIs.

Relationships should always be explicit.

Avoid lazy loading surprises.

Use eager loading when appropriate.

---

# Migrations

Every database change requires:

- Alembic migration
- Model update
- Tests (if applicable)

Never modify production tables manually.

---

# API Rules

REST first.

Consistent endpoints.

Example:

```
GET

POST

PATCH

DELETE
```

Avoid action-based routes.

Good:

```
PATCH /users/{id}
```

Bad:

```
POST /update-user
```

---

# Validation

Always validate using Pydantic.

Never trust frontend validation.

Validate:

- request body
- query parameters
- headers
- path parameters

---

# Error Handling

Never expose internal exceptions.

Raise application exceptions.

Example hierarchy:

```
AppError

ValidationError

AuthenticationError

AuthorizationError

PaymentError

StorageError

NotFoundError
```

Every error should return a consistent API response.

---

# Logging

Every request should include:

- Request ID
- User ID
- Organization ID (future)
- API Key ID
- IP Address
- Execution Time

Never use print().

Always use structured logging.

---

# Configuration

Never access:

```
os.getenv()
```

inside business logic.

Always use:

```
settings.py
```

based on Pydantic Settings.

---

# Security Rules

**Full standards: docs/18-security.md — binding for every PR.**

Never:

- log passwords
- log tokens
- log API keys
- log secrets

Always hash:

- passwords
- API keys

Never store plaintext secrets.

Additionally:

- New unauthenticated endpoints get a `rate_limit(...)` dependency.
- Session-ending events bump `user.token_version` (never invent a parallel revocation mechanism).
- Request schemas use `extra="forbid"`; responses use explicit schemas.
- Never weaken a validator, TTL, length limit, or production startup guard to make something pass.
- Admin access requires the allowlist **and** a verified email.

---

# Authentication

Authentication should remain application-managed.

Do not tightly couple to Supabase Auth.

Supported providers:

- Email
- Google
- GitHub

Future providers should be easy to add.

---

# Storage

Never call Supabase directly.

Always use Storage Adapter.

Future migration to Cloudflare R2 should require zero business logic changes.

---

# Billing

Stripe must remain isolated.

Application code should never call Stripe SDK directly.

Always go through Billing Service.

---

# Emails

Never send email directly.

Always queue email jobs.

Application code should call:

```
MailService
```

---

# Background Jobs

Every long-running task belongs in Celery.

Examples:

- emails
- image processing
- cleanup
- reports
- webhook retries

Never block HTTP requests.

---

# Frontend Rules

Prefer:

Server Components

Use Client Components only when necessary.

Forms:

React Hook Form

Validation:

Zod

Data Fetching:

TanStack Query

---

# UI Rules

Use:

shadcn/ui

Then:

Magic UI

Only create custom components when necessary.

Consistency is more important than originality.

---

# CSS Rules

Tailwind only.

Avoid inline styles.

Avoid custom CSS unless unavoidable.

---

# Testing Rules

Every feature should include:

- unit tests
- API tests
- integration tests (where appropriate)

Critical business logic must be tested.

---

# Documentation

Whenever a new reusable module is created:

Update documentation.

Never allow docs to become outdated.

Documentation is treated as production code.

---

# AI Behaviour

Before generating code:

Understand:

- folder structure
- architecture
- existing patterns

Prefer extending existing modules instead of creating new patterns.

Consistency is more important than novelty.

---

# Feature Checklist

When implementing a feature, verify:

- Database model
- Migration
- Repository
- Service
- Router
- Schemas
- Tests
- Documentation
- Logging
- Analytics event (if applicable)

---

# Code Review Checklist

Before considering work complete:

- No duplicated logic
- Proper typing
- Proper validation
- Logging included
- Error handling included
- Tests added
- Documentation updated
- Naming consistent
- Folder structure respected
- Reusable where possible

---

# Forbidden Practices

Never:

- Put business logic in routers
- Execute SQL from routes
- Hardcode secrets
- Duplicate code
- Introduce unnecessary frameworks
- Skip validation
- Ignore type hints
- Mix frontend and backend responsibilities
- Bypass service layer
- Bypass repository layer

---

# Success Criteria

AI-generated code should:

- Feel like it was written by one senior engineer.
- Follow existing architecture.
- Require minimal manual cleanup.
- Be reusable across future products.
- Be production-ready by default.

When in doubt, prioritize simplicity, consistency, and reusability over cleverness.