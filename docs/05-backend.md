# Backend Development Guide

> Complete backend engineering standards for FastForge.

---

# Purpose

This document defines how every backend feature should be designed and implemented.

Following these standards ensures:

- Consistent architecture
- Easier maintenance
- Better AI-generated code
- Predictable codebase
- Faster onboarding

This document is the source of truth for backend development.

---

# Technology Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | HTTP API |
| SQLAlchemy 2 | ORM |
| Alembic | Migrations |
| PostgreSQL | Database |
| Pydantic v2 | Validation |
| Redis | Cache & Broker |
| Celery | Background Jobs |
| uv | Package Management |

---

# Backend Architecture

Every request follows the same lifecycle.

```text
Request

↓

Router

↓

Dependency Injection

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

Schema

↓

Response
```

Business logic should never escape the Service layer.

---

# Design Principles

The backend follows several strict principles.

## Thin Routers

Routers should:

- Validate requests
- Call services
- Return responses

Routers should **not**:

- Execute SQL
- Contain business logic
- Perform calculations
- Access Redis
- Call external APIs

---

## Fat Services

Services own business logic.

Examples:

- Registration workflow
- Subscription management
- Permission checks
- API key generation
- Password reset
- Email verification

Whenever you're unsure where code belongs, it probably belongs in the service.

---

## Thin Repositories

Repositories are responsible only for persistence.

Allowed:

- CRUD
- Queries
- Pagination
- Filtering

Not allowed:

- Permission checks
- Validation
- Billing logic
- Email sending
- API requests

---

# Directory Structure

A feature should follow this layout:

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

Every feature should follow this convention.

---

# FastAPI Application Layout

```text
apps/api/

app/

api/

core/

middleware/

dependencies/

startup/

lifespan/

health/

main.py
```

Each directory has one responsibility.

---

# API Design

The API is REST-first.

Standard endpoints:

```
GET

POST

PATCH

DELETE
```

Examples:

```
GET /users

GET /users/{id}

POST /users

PATCH /users/{id}

DELETE /users/{id}
```

Avoid action-based routes.

Bad:

```
POST /create-user

POST /update-profile

POST /delete-user
```

Good:

```
POST /users

PATCH /users/{id}

DELETE /users/{id}
```

---

# Versioning

Every API is versioned.

```
/api/v1/
```

Future versions:

```
/api/v2/

/api/v3/
```

Never introduce breaking changes inside the same version.

---

# Request Validation

Every request must use Pydantic.

Example:

```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str
```

Never manually validate request payloads inside routes.

---

# Response Models

Always return response schemas.

Never expose SQLAlchemy models.

Good:

```python
UserResponse
```

Bad:

```python
return user_model
```

This prevents leaking internal fields.

---

# Dependency Injection

Use FastAPI dependencies consistently.

Example:

```python
@router.get("/")
async def list_users(
    service: UserService = Depends(get_user_service),
):
    ...
```

Never instantiate services inside routes.

Bad:

```python
service = UserService()
```

Good:

```python
service: UserService = Depends(get_user_service)
```

---

# Services

Services orchestrate the application.

Responsibilities:

- Validation
- Authorization
- Transactions
- Calling repositories
- Calling external providers
- Business rules

Services should not know:

- HTTP
- JSON
- FastAPI
- SQL

They operate on Python objects.

---

# Repository Layer

Repositories abstract SQLAlchemy.

Example:

```python
UserRepository

ProjectRepository

ApiKeyRepository
```

Responsibilities:

- Insert
- Update
- Delete
- Query
- Pagination

Nothing else.

---

# Models

Models represent tables.

Every model should inherit from Base.

Every model should include:

- id
- created_at
- updated_at

Example:

```python
class User(Base):
    ...
```

Keep models lightweight.

---

# UUID Policy

Primary keys use UUID.

Prefer:

UUIDv7

Fallback:

UUIDv4

Foreign keys also use UUID.

Never mix integer IDs and UUIDs.

---

# Relationships

Relationships should be explicit.

Good:

```python
relationship(
    "Project",
    back_populates="owner"
)
```

Avoid implicit loading surprises.

Use eager loading where appropriate.

---

# Database Sessions

Sessions are managed by dependency injection.

Repositories receive sessions.

Routes never interact with sessions directly.

Example:

```text
Request

↓

Session Dependency

↓

Repository
```

---

# Transactions

Services control transactions.

Example:

```
Create User

↓

Create Workspace

↓

Send Welcome Email

↓

Commit
```

Repositories should not manage transaction boundaries.

---

# Soft Deletes

Only implement soft deletes where business requirements justify them.

Use:

```
deleted_at
```

Avoid boolean flags like:

```
is_deleted
```

Timestamp-based soft deletes provide more information.

---

# Pagination

Every list endpoint should support pagination.

Standard query parameters:

```
page

page_size
```

Future enhancement:

Cursor pagination.

Do not return unbounded datasets.

---

# Filtering

Filtering should be handled by repositories.

Example:

```
status

created_after

created_before

search
```

Never duplicate filtering logic across routes.

---

# Sorting

Allow controlled sorting.

Example:

```
sort_by=name

sort_by=created_at

sort_order=asc

sort_order=desc
```

Never expose arbitrary SQL ordering.

Validate allowed fields.

---

# Searching

Search should remain explicit.

Avoid dynamically building SQL.

Prefer well-defined search methods inside repositories.

---

# Error Handling

Use application exceptions.

Example hierarchy:

```
AppError

ValidationError

AuthenticationError

AuthorizationError

NotFoundError

ConflictError

PaymentError

StorageError
```

Never raise raw SQLAlchemy exceptions from services.

Convert infrastructure errors into application errors.

---

# HTTP Status Codes

Use standard status codes.

Examples:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

Be consistent across every endpoint.

---

# Authentication

Authentication is owned by the application.

It should never depend directly on a hosting provider.

Supported methods:

- Email & Password
- Google OAuth
- GitHub OAuth

Future providers:

- Microsoft
- GitLab
- Apple

Every provider should implement the same interface.

```
Login Request

↓

Authentication Service

↓

Provider

↓

User

↓

JWT

↓

Response
```

---

# JWT Strategy

Use:

- Access Token
- Refresh Token

Access Token

- Short-lived
- Sent with every request

Refresh Token

- Longer lifetime
- Used only to obtain new access tokens

Never store JWTs in localStorage.

Prefer secure, HttpOnly cookies for web applications.

---

# Password Storage

Passwords must never be encrypted.

Passwords must always be hashed.

Recommended:

```
Argon2id
```

Acceptable alternative:

```
bcrypt
```

Never:

- store plaintext passwords
- log passwords
- expose password hashes

---

# Authorization

Authentication identifies the user.

Authorization determines what the user can do.

Authorization checks belong inside services.

Examples:

```
Can edit project?

Can delete API key?

Can access organization?

Can manage billing?
```

Do not implement authorization in repositories.

---

# Redis

Redis should only be accessed through the Cache package.

Use cases:

- Session cache
- OTP storage
- Rate limiting
- Celery broker
- Temporary cache

Avoid treating Redis as a primary database.

---

# Background Jobs

Anything expected to take more than a few hundred milliseconds should be considered for asynchronous execution.

Examples:

- Sending emails
- Importing CSV files
- Image processing
- Webhook retries
- Report generation
- Data cleanup

Request flow:

```
HTTP Request

↓

Service

↓

Queue Task

↓

Return Response

↓

Celery Worker

↓

Execute Task
```

Users should not wait for background work.

---

# Celery

Celery is responsible for asynchronous execution.

Each task should perform one responsibility.

Good:

```
send_verification_email()

generate_invoice()

cleanup_expired_sessions()
```

Bad:

```
process_everything()
```

Tasks should be:

- Small
- Idempotent
- Retryable

---

# Scheduled Jobs

Scheduled jobs belong in the worker application.

Examples:

- Delete expired tokens
- Clean temporary uploads
- Generate daily reports
- Sync analytics
- Retry failed webhooks

Avoid cron jobs on individual servers.

Scheduling should be centralized.

---

# Email Architecture

Emails are never sent directly.

Flow:

```
Service

↓

MailService

↓

Queue

↓

Worker

↓

SMTP Provider
```

Benefits:

- Faster requests
- Automatic retries
- Better monitoring

---

# External APIs

Never call third-party SDKs directly from services.

Always use adapters.

Example:

```
Billing Service

↓

Stripe Adapter

↓

Stripe API
```

This makes provider replacement straightforward.

---

# Logging

Every request should produce structured logs.

Required fields:

- Timestamp
- Request ID
- User ID
- Route
- HTTP Method
- Status Code
- Duration

Optional fields:

- API Key ID
- Organization ID
- Worker ID

Never use `print()`.

Always use the shared logging package.

---

# Configuration

Configuration is centralized.

```
Environment Variables

↓

Pydantic Settings

↓

Application
```

Never call:

```python
os.getenv()
```

inside services.

Inject configuration where needed.

---

# Secrets

Secrets include:

- JWT secret
- Stripe keys
- SMTP password
- Database URL
- Redis URL
- OAuth secrets

Never:

- Commit secrets
- Log secrets
- Hardcode secrets

Every secret should come from configuration.

---

# File Uploads

Applications communicate only with StorageService.

Never upload files directly to Supabase SDK inside routes.

Flow:

```
Route

↓

Storage Service

↓

Storage Adapter

↓

Provider
```

Future providers should require no business logic changes.

---

# Rate Limiting

Rate limiting should be configurable.

Examples:

Anonymous users:

```
60 requests/minute
```

Authenticated users:

```
300 requests/minute
```

API Keys:

Plan-dependent.

Implementation should use Redis.

---

# Idempotency

Endpoints creating external side effects should support idempotency.

Examples:

- Payments
- Webhooks
- Subscription changes

Duplicate requests should not create duplicate resources.

---

# Webhooks

Webhook processing should be asynchronous.

Flow:

```
Receive Webhook

↓

Verify Signature

↓

Queue Processing

↓

Worker

↓

Business Logic
```

Never perform heavy work during the initial webhook request.

Respond quickly.

---

# Performance Guidelines

Prefer:

- Bulk queries
- Pagination
- Proper indexes
- Async I/O
- Eager loading when appropriate

Avoid:

- N+1 queries
- Loading unnecessary columns
- Repeated database queries
- Blocking I/O inside async routes

Measure before optimizing.

---

# Testing Strategy

Three levels of testing:

## Unit Tests

Test:

- Services
- Utilities
- Validators

Mock infrastructure.

---

## Integration Tests

Test:

- Database
- Repositories
- External adapters (where practical)

---

## API Tests

Test:

- Routes
- Authentication
- Authorization
- Validation
- Response schemas

Critical user flows should always have API tests.

---

# Exception Handling

Every application exception should include:

- Error code
- Human-readable message
- Optional details

Example response:

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User does not exist."
  }
}
```

Avoid leaking implementation details.

---

# Observability

Every production deployment should include:

- Structured logs
- Error monitoring
- Request metrics
- Health checks

Health endpoints:

```
GET /health

GET /ready

GET /live
```

---

# Code Quality

Every backend contribution should satisfy:

- Type hints
- Docstrings where useful
- Small functions
- Clear naming
- Minimal duplication
- Explicit dependencies

Readable code is preferred over clever code.

---

# Backend Checklist

Before merging a backend feature:

- [ ] Models created
- [ ] Migration added
- [ ] Repository implemented
- [ ] Service implemented
- [ ] Router added
- [ ] Schemas created
- [ ] Dependency injection configured
- [ ] Logging included
- [ ] Error handling implemented
- [ ] Tests written
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Business logic in routers
- SQL in routers
- SQL in middleware
- Global mutable state
- Circular imports
- Large utility modules
- Hidden side effects
- Hardcoded configuration
- Catch-all exception handlers
- Duplicate repository logic

---

# Backend Definition of Done

A backend feature is complete only when:

- Architecture is respected.
- Business logic is isolated.
- Validation is implemented.
- Authorization is enforced.
- Tests pass.
- Documentation is updated.
- Logging is included.
- Errors are standardized.

Shipping incomplete infrastructure creates long-term maintenance costs.

---

# Summary

The backend architecture is intentionally opinionated.

Every feature should follow the same patterns so that:

- Developers can navigate the codebase easily.
- AI agents generate consistent code.
- Business logic remains isolated.
- Infrastructure remains reusable.

The backend should feel predictable regardless of which feature is being developed.

Consistency is the primary objective.