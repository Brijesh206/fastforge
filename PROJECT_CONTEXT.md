# FastForge — Project Context

You are helping me build **FastForge**, a reusable SaaS boilerplate/framework that will be the foundation for all of my future products.

## Goal

I am an indie developer.

My goal is to launch **2–3 SaaS products every month**.

The philosophy is:

* Ship fast
* Validate quickly
* Kill unsuccessful products
* Reuse as much code as possible
* Everything should be modular and replaceable

This is **not** a boilerplate for one project.

It is a platform that will generate many future SaaS products.

---

# Tech Stack

## Frontend

* Next.js (App Router)
* React
* TypeScript
* Tailwind CSS
* shadcn/ui
* Magic UI
* React Hook Form
* Zod
* TanStack Query
* Zustand (only when needed)

## Backend

* FastAPI
* Pydantic v2
* SQLAlchemy 2.0
* Alembic
* uv
* Celery
* Redis
* SMTP
* JWT
* Python 3.13+

## Database

* PostgreSQL
* UUIDv7 primary keys
* Supabase PostgreSQL initially

## Storage

Initially:

* Supabase Storage

Future:

* Cloudflare R2
* AWS S3

Provider abstraction is required.

## Authentication

Initially:

* Supabase Auth

Architecture must allow migration later.

Support:

* Email/password
* OAuth
* Sessions
* JWT
* Refresh Tokens
* Organizations
* Roles
* Permissions
* API Keys

## Payments

Initially:

* Stripe

Architecture must allow:

* Paddle
* Lemon Squeezy
* Polar

using adapters.

## Cache

Redis

Used for:

* Celery
* Sessions
* Rate limiting
* Cache
* Temporary data
* Distributed locks

## Deployment

Frontend

* Vercel

Backend

* Railway or Fly.io

Database

* Supabase

Redis

* Upstash

Everything should work on free tiers initially.

---

# Architecture

Use a monorepo.

Example:

```
apps/
    web/
    api/

packages/
    shared/
    database/
    auth/
    billing/
    cache/
    storage/
    email/
    notifications/
    logging/
    observability/

docker/

scripts/

docs/
```

The codebase must be optimized for AI coding agents like:

* Claude Code
* Codex
* Cursor
* Gemini CLI

Everything should be modular.

Never tightly couple external providers.

Always use adapter interfaces.

---

# Coding Philosophy

Follow:

* Clean Architecture
* Domain Driven Design (lightweight)
* SOLID
* Repository Pattern where appropriate
* Service Layer
* Dependency Injection
* Async first
* Type safety
* High testability

Avoid unnecessary enterprise complexity.

The goal is speed while keeping the architecture maintainable.

---

# Completed Documentation

The following documentation files are already complete:

```
README.md
AGENTS.md

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
12-notifications.md
13-cache.md
14-logging.md
15-observability.md
16-deployment.md
```

Do not regenerate these.

Assume they already exist.

Continue from the next document.

---

# Remaining Documents

Continue with:

```
17-ci-cd.md
18-testing.md
19-security.md
20-api-design.md
21-background-jobs.md
22-configuration.md
23-error-handling.md
24-events.md
25-sdk.md
26-cli.md
27-ai-coding-guidelines.md
28-product-launch-checklist.md
29-product-template.md
30-roadmap.md
31-contributing.md
```

Each document should be written in the same style as the previous ones:

* Comprehensive
* Production ready
* Markdown
* Clear headings
* Reusable across products
* No unnecessary explanations
* Designed as engineering documentation

Large documents should be split into two parts when necessary.

Always provide the file path before the markdown.

Example:

```
docs/17-ci-cd.md
```

Continue exactly where we left off.

Do not repeat previous documentation.

Do not change the architecture unless I explicitly request it.
