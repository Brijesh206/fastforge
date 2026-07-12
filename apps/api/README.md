# API Application

FastAPI application shell for FastForge.

## Responsibilities

- Compose shared platform packages
- Register versioned API routes
- Register middleware
- Register exception handlers
- Manage application lifespan
- Expose health endpoints

## Current Endpoints

```text
GET  /api/v1/health
GET  /api/v1/live
GET  /api/v1/ready

POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me        (Bearer access token)
```

## Current Wiring

- `fastforge-common` for settings, constants, and error envelopes
- `fastforge-logging` for structured request/error logs
- `fastforge-database` for database manager and sessions
- `fastforge-auth` for the user model, `AuthService`, password hashing, and JWTs

The auth HTTP layer lives in `app/auth/` (router + dependencies). All auth
business logic stays in the `fastforge-auth` package. Write endpoints use a
transactional session dependency (`get_db_transaction`); `get_current_user`
resolves the Bearer access token to a `User`.

## Rules

- Routes stay thin.
- Services own behavior.
- Database access goes through shared dependencies and repositories.
- Application errors use the shared `AppError` hierarchy.
- Request logs include request ID, method, path, status code, duration, IP, and user agent.
