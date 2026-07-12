# Folder Structure

> Canonical repository layout for FastForge.

This document defines **where every file belongs**.

A predictable folder structure makes the project easier to navigate, easier to maintain, and significantly improves AI-generated code quality.

If there is uncertainty about where code belongs, this document is the source of truth.

---

# Principles

The repository follows five principles.

1. Feature First
2. Modular Design
3. Separation of Concerns
4. Predictable Structure
5. Reusable Packages

The same feature should always look the same regardless of who implemented it.

---

# Repository Structure

```text
fastforge/

├── apps/
│
├── packages/
│
├── docs/
│
├── docker/
│
├── scripts/
│
├── .github/
│
├── turbo.json
├── docker-compose.yml
├── pyproject.toml
├── package.json
├── pnpm-workspace.yaml
├── README.md
└── AGENTS.md
```

---

# apps/

Applications are deployable software.

Applications should contain as little reusable logic as possible.

```text
apps/

├── api/
├── web/
├── worker/
└── docs/
```

---

# apps/api

FastAPI application.

```text
apps/api/

├── app/
│
├── tests/
│
├── migrations/
│
├── pyproject.toml
│
├── Dockerfile
│
└── .env.example
```

---

# app/

```text
app/

├── api/
├── core/
├── dependencies/
├── middleware/
├── lifespan/
├── startup/
├── health/
├── config/
├── main.py
└── __init__.py
```

Responsibilities:

## api/

Contains routers only.

No business logic.

Example:

```text
api/

users.py

projects.py

billing.py

auth.py
```

---

## core/

Application bootstrap.

Examples:

- exception handlers
- logging configuration
- security
- OpenAPI customization

---

## dependencies/

Shared FastAPI dependencies.

Examples:

- Current User
- Database Session
- Pagination
- API Key Authentication

---

## middleware/

Examples:

- Logging
- CORS
- Request ID
- Authentication
- Rate Limiting

---

## lifespan/

Application startup/shutdown events.

---

## startup/

Startup tasks.

Examples:

- Verify configuration
- Connect Redis
- Register metrics

---

## health/

Health endpoints.

Examples:

```text
GET /health

GET /ready

GET /live
```

---

# apps/web

```text
apps/web/

src/

public/

components/

hooks/

lib/

styles/

tests/

package.json

Dockerfile
```

---

# src/

```text
src/

app/

actions/

features/

providers/

types/
```

---

## app/

Next.js App Router.

Contains:

- layouts
- pages
- route groups

Avoid placing business logic here.

---

## actions/

Server Actions.

Only if necessary.

Prefer backend APIs for reusable business logic.

---

## features/

Feature-based frontend organization.

Example:

```text
features/

auth/

dashboard/

billing/

projects/

settings/
```

Each feature owns:

```text
auth/

components/

hooks/

api/

types/

utils/
```

---

## providers/

React providers.

Examples:

- Theme
- Query Client
- Authentication

---

## hooks/

Reusable hooks.

Examples:

```text
useCurrentUser()

useDebounce()

useClipboard()

useDarkMode()
```

---

## lib/

Frontend utilities.

Examples:

```text
api.ts

constants.ts

env.ts

utils.ts

validators.ts
```

---

# apps/worker

```text
apps/worker/

tasks/

workers/

scheduler/

config/

main.py
```

---

## tasks/

Each task should be isolated.

Example:

```text
send_email.py

cleanup.py

retry_webhooks.py

generate_report.py
```

---

# packages/

Packages contain reusable platform modules.

```text
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

Packages never depend on application code.

---

# Package Structure

Every package should follow the same layout.

```text
package/

src/

tests/

README.md

pyproject.toml
```

---

# src/

```text
src/

models/

repositories/

services/

schemas/

routers/

dependencies/

exceptions/

constants/

utils/

adapters/

interfaces/
```

Not every package requires every folder.

Only create folders that are needed.

---

# models/

Database models.

Only SQLAlchemy models belong here.

---

# repositories/

Database access.

Never place business logic here.

---

# services/

Business logic.

The most important layer.

Responsible for:

- validation
- orchestration
- workflows
- permissions

---

# schemas/

Pydantic models.

Examples:

```text
UserCreate

UserUpdate

UserResponse
```

Never expose SQLAlchemy models.

---

# routers/

Some packages may expose reusable routers.

Example:

Authentication package.

---

# adapters/

External providers.

Examples:

```text
StripeAdapter

SupabaseStorageAdapter

SMTPAdapter
```

Business logic communicates with adapters.

Adapters communicate with vendors.

---

# interfaces/

Contracts.

Example:

```python
StorageProvider

PaymentProvider

MailProvider
```

This makes vendor replacement easy.

---

# common/

Shared utilities.

Example structure:

```text
common/

config/

exceptions/

constants/

enums/

types/

utils/

validators/
```

Avoid creating duplicate helper functions elsewhere.

---

# docs/

Engineering handbook.

```text
docs/

01-vision.md

02-architecture.md

...

adr/
```

Documentation is version-controlled.

Treat it as production code.

---

# docker/

Docker configuration.

```text
docker/

api/

web/

worker/

nginx/
```

Each service has its own Dockerfile.

---

# scripts/

Automation scripts.

Examples:

```text
bootstrap.sh

release.sh

seed.py

backup.py

lint.sh
```

Scripts should be idempotent whenever possible.

---

# tests/

Testing mirrors application structure.

Backend:

```text
tests/

unit/

integration/

api/

fixtures/
```

Frontend:

```text
tests/

components/

e2e/
```

---

# Feature Structure (Backend)

Every feature should look similar.

Example:

```text
users/

models.py

schemas.py

repository.py

service.py

router.py

dependencies.py

exceptions.py

constants.py
```

Responsibilities:

| File | Responsibility |
|------|----------------|
| models.py | Database models |
| schemas.py | Request/Response models |
| repository.py | Database access |
| service.py | Business logic |
| router.py | HTTP endpoints |
| dependencies.py | FastAPI dependencies |
| exceptions.py | Feature-specific exceptions |
| constants.py | Constants |

---

# Import Rules

Allowed:

```
Router

↓

Service

↓

Repository

↓

Model
```

Forbidden:

```
Router

↓

Repository
```

Forbidden:

```
Repository

↓

Service
```

Forbidden:

```
Model

↓

Service
```

Dependencies always point downward.

---

# Naming Conventions

Folders:

```
snake_case
```

Python files:

```
snake_case.py
```

Classes:

```
PascalCase
```

Variables:

```
snake_case
```

Constants:

```
UPPER_CASE
```

Interfaces:

```
StorageProvider

PaymentProvider
```

Adapters:

```
StripeAdapter

SMTPAdapter

SupabaseStorageAdapter
```

Services:

```
UserService

BillingService
```

Repositories:

```
UserRepository

ProjectRepository
```

---

# File Size Guidelines

Recommended maximum sizes:

| File | Target |
|------|--------|
| Router | <300 lines |
| Service | <500 lines |
| Repository | <300 lines |
| Model | <200 lines |
| Utility | <200 lines |

If a file grows beyond these limits, consider refactoring.

---

# Creating a New Feature

When adding a feature:

1. Create the feature directory.
2. Add models.
3. Add schemas.
4. Add repository.
5. Add service.
6. Add router.
7. Register router.
8. Add tests.
9. Update documentation if reusable.

---

# Anti-Patterns

Avoid:

- Utility folders with unrelated code
- Generic helpers without ownership
- Circular imports
- Massive service classes
- Business logic in routers
- Database queries in services
- Shared mutable state
- Deeply nested folder structures

---

# Checklist

Before creating a new file:

- Does a similar file already exist?
- Does this belong in a shared package?
- Does the folder follow the standard layout?
- Does the dependency direction remain correct?
- Will another developer immediately know where to find this code?

If any answer is "no", reconsider the implementation.

---

# Summary

A consistent folder structure is one of the highest-leverage investments in this platform.

It improves:

- Developer onboarding
- AI-generated code quality
- Maintainability
- Reusability
- Navigation
- Long-term scalability

The structure should evolve slowly and intentionally. Consistency is more valuable than novelty.