# FastForge - Project Progress

Last updated: 2026-07-15

## Current Status

The initial monorepo scaffold is in place and ready for continued package-by-package development.

Core structure exists:

- `apps/api`
- `apps/web`
- `apps/worker`
- `packages/database`
- `packages/common`
- `packages/logging`
- `packages/auth`
- placeholder packages for billing, cache, storage, mail, analytics, notifications, API keys, and UI
- `docs`
- `docker`
- `scripts`

The repository is being built as a reusable SaaS platform, not a one-off boilerplate.

## Completed This Session (2026-07-12)

### Auth Package

Package path:

```text
packages/auth
```

First-pass authentication foundation implemented:

- `User` SQLAlchemy model (UUIDv7 primary key, nullable `password_hash` for
  OAuth-only users, `is_active`/`is_verified`/`last_login_at`)
- `AuthProvider` and `TokenType` enums
- Auth-specific exceptions (`UserAlreadyExistsError`, `UserNotFoundError`,
  `InvalidCredentialsError`, `InactiveUserError`, `InvalidTokenError`) built
  on the shared `fastforge_common` exception hierarchy
- Pydantic v2 schemas: `UserCreate`, `UserResponse`, `LoginRequest`,
  `TokenPair` (with email normalization and password length validation)
- `PasswordHasher` interface + `Argon2PasswordHasher` adapter (Argon2id)
- `TokenService` interface + `JwtTokenService` adapter (HS256 access/refresh
  token pair, type-checked on decode)
- `AuthSettings` (Pydantic Settings) for JWT secret/algorithm/expirations
- `UserRepository` (get by id via inherited `BaseRepository`, get by email,
  create, update) extending `fastforge_database.BaseRepository`
- `AuthService` skeleton: `register_user`, `authenticate_user` — depends only
  on the `PasswordHasher`/`TokenService` interfaces, never on Argon2 or PyJWT
  directly
- Alembic migration `0002_create_users_table` in the shared
  `packages/database/migrations/versions` directory, hand-written to match
  naming conventions (`pk_users`, `uq_users_email`)
- `packages/database/migrations/env.py` now imports `fastforge_auth.models.user`
  so the `users` table is registered on the shared metadata for future
  autogenerate runs
- `packages/auth/README.md`
- 26 focused unit tests (exceptions, schemas, password hasher, JWT token
  service, `AuthService` with an in-memory fake repository)

Not yet implemented (left for future passes): OAuth, sessions, email
verification, password reset, roles/permissions, organizations, API keys.

### API Auth Routes + Secrets (2026-07-12)

The `fastforge_auth` package is now wired into `apps/api` over HTTP:

- New HTTP layer in `apps/api/app/auth/` (`router.py`, `dependencies.py`) —
  routers stay thin and delegate to `AuthService`; all business logic remains
  in the package.
- Endpoints:
  - `POST /api/v1/auth/register` → 201, returns `UserResponse`
  - `POST /api/v1/auth/login` → `TokenPair`
  - `POST /api/v1/auth/refresh` → `TokenPair`
  - `GET  /api/v1/auth/me` → `UserResponse` (Bearer access token)
- `get_current_user` dependency resolves a Bearer access token to a `User`
  (via `HTTPBearer` + `TokenService` + `UserRepository`), raising the shared
  `AuthenticationError` (401) on missing/invalid/inactive.
- Added `get_db_transaction` session dependency (commits on success, rolls
  back on error) for write endpoints; read endpoints use `get_db_session`.
- `Argon2PasswordHasher` and `JwtTokenService` are created once in the app
  lifespan and stored on `app.state`.
- Package additions: `RefreshRequest` schema and `AuthService.refresh_tokens`
  (+ 3 unit tests). Auth suite is now 29 tests.
- Generated strong 48-byte `JWT_SECRET_KEY` and `APP_SECRET_KEY` into the real
  `.env` (replacing the placeholder that PyJWT warned about).

## Completed Previous Session (2026-07-08)

### Database Package

Package path:

```text
packages/database
```

Implemented or hardened:

- SQLAlchemy async database settings
- `DatabaseManager`
- async session factory
- transaction/session context managers
- SQLAlchemy base model
- timestamp mixin
- soft delete mixin
- audit mixin
- UUID primary key support
- real UUIDv7 generator
- Alembic naming conventions
- base repository
- pagination helpers
- sorting helpers
- Supabase PostgreSQL support
- local PostgreSQL support
- database package README
- focused database tests

Supabase support is now first-class:

- accepts Supabase direct database URLs
- accepts Supabase pooler URLs
- normalizes `postgresql://` to `postgresql+asyncpg://`
- handles `sslmode=require`
- auto-enables SSL for Supabase hosts
- supports `DATABASE_SSL_MODE=require`

### Common Package

Package path:

```text
packages/common
```

Implemented:

- `BaseAppSettings`
- `AppEnvironment`
- shared constants
- standard application exception hierarchy
- standard error codes
- standard error response schemas
- common package README
- focused common tests

The common package is intentionally framework-agnostic.

It should not import:

- FastAPI
- SQLAlchemy
- Celery
- Redis
- Stripe
- Supabase SDKs
- provider-specific SDKs

### Logging Package

Package path:

```text
packages/logging
```

Implemented:

- `LoggingSettings`
- log format enum
- structured JSON formatter
- local text formatter
- context propagation with `contextvars`
- request ID and correlation ID support
- user, organization, API key, trace, and span context fields
- recursive sensitive metadata redaction
- `LoggingService`
- root logger configuration helper
- logger factory helper
- logging package README
- focused logging tests

The logging package is intentionally framework-agnostic.

It should not import:

- FastAPI
- Celery
- Redis
- SQLAlchemy
- provider-specific logging or monitoring SDKs

### API App Shell

Application path:

```text
apps/api
```

Implemented:

- FastAPI app factory
- versioned root API router
- API settings
- application lifespan
- logging setup during startup
- database manager initialization during startup
- database manager disposal during shutdown
- database session dependency
- request ID middleware
- request logging middleware
- standard application exception handlers
- FastAPI validation error handler
- unhandled exception handler
- health service
- health router
- liveness endpoint
- readiness endpoint
- API README

Current endpoints:

```text
GET /api/v1/health
GET /api/v1/live
GET /api/v1/ready
```

## Important Decisions

- Supabase PostgreSQL is the primary hosted database target.
- Local PostgreSQL remains supported for development and testing.
- Packages must remain reusable and must not depend on application code.
- Business logic belongs in services.
- Database access belongs in repositories.
- Routes must stay thin.
- Provider SDKs should be hidden behind adapters.
- Common primitives should live in `packages/common`.
- Shared logging primitives should live in `packages/logging`.
- API routes should remain thin and call services.
- Health database checks live in `app.health.service`, not directly in routes.
- Auth is application-managed, not tightly coupled to Supabase Auth; `AuthService`
  depends only on the `PasswordHasher`/`TokenService` interfaces.
- Feature packages (starting with auth) add their tables as new revisions inside
  the shared `packages/database/migrations` directory rather than owning their
  own separate migrations folder. `packages/database/migrations/env.py` imports
  each feature package's models so they register on the shared metadata.

## Platform Rename: Indie Platform OS → FastForge (2026-07-12)

The platform was rebranded to **FastForge**. This was a full rename, including
the code namespace:

- Python import packages `indie_*` → `fastforge_*` (directories under
  `packages/*/src/` renamed, all imports updated, Alembic `env.py` updated).
- Distribution names `indie-*` → `fastforge-*` in every `pyproject.toml`, plus
  `[tool.uv.sources]` and inter-package dependencies.
- Display strings "Indie Platform" / "Indie Platform OS" → "FastForge" across
  docs, READMEs, `APP_NAME` default, and docker container names.
- Environment variable names are intentionally unchanged (`APP_NAME`, `JWT_*`,
  `DATABASE_URL`, etc.), so existing `.env` files keep working.
- A safety backup of the pre-rename repo was taken before the change.
- After renaming, `uv sync --all-packages` reinstalled all 13 packages under
  the new names and the full test suite still passed.
- Legitimate English uses of the word "indie" (e.g. "indie developer") were
  left untouched.
- The on-disk repo folder is still literally `indie-platform`; rename it
  separately if desired (it does not affect the build).

## Environment / Tooling Fixes (2026-07-12)

- Installed `uv` (0.11.28) and ran `uv sync --all-packages`; the workspace now
  builds on CPython 3.13.13 in `.venv`.
- `AuthSettings` token-expiry fields now read `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
  / `JWT_REFRESH_TOKEN_EXPIRE_DAYS` to match the shipped `.env` names.
- `.env`: corrected `DATABASE_SSL_MODE=true` (invalid literal, would crash
  startup) → `require`.
- Made `packages/database/tests` hermetic via a `conftest.py` that isolates
  settings construction from the developer's `.env` and ambient env vars.
- Fixed `DatabaseSettings.connect_args` SSL semantics: `require` now returns an
  SSL context that encrypts **without** certificate verification (matching
  libpq `sslmode=require`), while `verify-ca`/`verify-full` verify. Previously
  `require` produced `{"ssl": True}` (full verification), which failed against
  Supabase's cert chain (`CERTIFICATE_VERIFY_FAILED`).
- Fixed Alembic `env.py` online migrations to pass `settings.connect_args`, so
  migrations connect to Supabase with the correct SSL context.

## Verification

Completed (via `uv run` on CPython 3.13.13 in the workspace `.venv`):

- `packages/auth/tests` — 29 passed (incl. 3 `refresh_tokens` tests).
- `packages/common/tests` — 6 passed.
- `packages/database/tests` — 16 passed (added a `verify-full` SSL test).
- `packages/logging/tests` — 7 passed.
- API app builds and both `AuthSettings`/`DatabaseSettings` load cleanly from
  the real `.env` (`fastforge_auth` + `app.main` import clean).
- Verified the `User` model maps to the expected `users` table (columns,
  `pk_users`, `uq_users_email`) via `Base.metadata`.
- Alembic revision chain (`0001_initial` → `0002_create_users_table`) applied
  successfully **against the live Supabase database** (`alembic upgrade head`).
- **End-to-end auth smoke test against Supabase passed**: register (argon2id
  hash stored, UUIDv7 PK) → login (access+refresh JWT issued) → decode access
  token maps back to the user → wrong password rejected → `last_login_at`
  recorded → test user deleted (DB left clean; `users` + `alembic_version`
  tables remain).
- **End-to-end HTTP route test against Supabase passed** (FastAPI TestClient,
  17 checks): `/health`, register→201, duplicate→409 (error envelope),
  weak-password→422, login→200, `/me` without token→401, `/me` with token→200,
  `/me` with refresh token→401 (token type enforced), refresh→200, wrong
  password→401; test user cleaned up afterwards.

Notes:

- **Security:** strong 48-byte `JWT_SECRET_KEY` and `APP_SECRET_KEY` are now set
  in the real `.env` (the PyJWT short-key warning is resolved). `.env` is
  gitignored and must never be committed.
- One-off smoke scripts (`smoke_auth.py`, `smoke_routes.py`) live in the
  session scratchpad (not committed).

Recommended setup on a fresh machine:

```bash
uv sync --all-packages
pnpm install
uv run pytest packages
cd packages/database && uv run alembic upgrade head
```

## Completed 2026-07-14 — Mail Package (issue #7)

Package path:

```text
packages/mail
```

Transactional email, built on the standard library — **no new dependencies**
(`smtplib` + `string.Template`, not aiosmtplib + Jinja2).

- `EmailProvider` interface; `SmtpEmailProvider` (blocking `smtplib` run in a
  worker thread via `asyncio.to_thread`) and `ConsoleEmailProvider` (logs the
  email instead of sending it)
- `EmailService` — the only class applications touch: `send_verification_email`,
  `send_password_reset_email`
- `MailSettings` (`MAIL_*` env vars). Defaults to the **console** provider, so a
  fresh checkout cannot email a real person by accident
- `EmailMessage` Pydantic schema — an invalid recipient is rejected before it
  reaches a provider
- Templates as `<name>.html`/`<name>.txt` pairs wrapped in a shared
  `_layout.html`. Values are HTML-escaped in the HTML part (no markup injection
  from a hostile URL or name); `$` inside a value is safe
- `verify_email` and `password_reset` templates, both with plain-text parts
- 16 tests, including **delivery over a real socket to a real SMTP server**
  (stdlib sink — proves the MIME bytes and connection work, no Docker needed)

Deliberately deferred (documented in `packages/mail/README.md`): retries/queue,
rate limiting, bounce webhooks, delivery tracking, localization, attachments.

### Fixes this surfaced

- **No package shipped a PEP 561 `py.typed` marker**, so mypy silently treated
  every cross-package import as untyped. Added markers to `common`, `logging`,
  `database`, `auth`, `mail`.
- With types now visible, mypy found a **real bug in the logging package**:
  `bind_log_context` accepted `UUID` for `request_id`/`correlation_id`/
  `trace_id`/`span_id`, which are `str`-only on `LogContext`. Now coerced.
- **CI was only checking `packages/database`.** It now type-checks all five
  implemented packages and runs every package's tests (16 tests → 70).
- Resolved the long-standing test-name collision with
  `--import-mode=importlib`, so one `uv run pytest packages` runs everything.

## Completed 2026-07-15 — Email Verification & Password Reset (issue #4)

Single-use, database-backed account-lifecycle tokens, now unblocked by the
mail package.

- `AuthTokenPurpose` enum, `AuthToken` model + `AuthTokenRepository`, and
  Alembic migration `0003_create_auth_tokens_table` (applied to Supabase)
- Tokens are `secrets.token_urlsafe(32)`; only the **SHA-256 hash** is stored,
  so a database leak never exposes a usable link. Single use is enforced via
  `used_at`; issuing a new token invalidates the previous one
- `AuthService` gained `issue_email_verification_token`, `verify_email`,
  `issue_password_reset_token`, `reset_password`. It still never imports the
  mail package — the issuing methods return the raw token and the **app**
  (`apps/api/app/auth/emails.py`) composes the link and schedules the send via
  FastAPI `BackgroundTasks`, so the HTTP request never waits on SMTP
- `issue_password_reset_token` returns `None` for unknown/inactive accounts;
  the endpoint responds identically either way (no account enumeration)
- New endpoints: `POST /auth/verify-email`, `POST /auth/verify-email/resend`
  (authenticated), `POST /auth/password-reset/request`,
  `POST /auth/password-reset/confirm`. Registration now sends a verification
  email automatically
- `get_current_verified_user` dependency to gate endpoints on `is_verified`
- 12 new service unit tests (hashing, single-use, expiry, enumeration-safety).
  Shared test fakes moved into `conftest.py` fixtures (importlib mode forbids
  cross-test-module imports)
- Fixed `apps/api/pyproject.toml`, which imported `fastforge_auth` without
  declaring it; added `fastforge-auth` and `fastforge-mail`. Added `httpx` as a
  dev dependency (FastAPI TestClient)

**Verified end-to-end against live Supabase** (in-process FastAPI app, email
service replaced with a capturing fake, 15/15 checks): register → unverified →
login works pre-verification → verify with emailed token → `/me` now verified →
reused verification token rejected (401) → reset request is enumeration-safe →
reset confirm → old password rejected, new accepted → reused reset token
rejected (401) → user cleaned up.

Deferred (documented): rate limiting on these endpoints (needs Redis, post-v1);
session/refresh-token revocation on password reset (JWT refresh is stateless
until a sessions table exists, post-v1).

## Completed 2026-07-15 — Stripe Billing (issue #6)

Subscription billing, provider-independent by design (Stripe today).

- `BillingProvider` interface; `StripeBillingProvider` is the **only** module
  importing the Stripe SDK. Blocking Stripe calls run in a worker thread
  (`asyncio.to_thread`). No Stripe type crosses the interface — webhooks return
  the normalized `BillingEvent`
- `Subscription` model (user-scoped for v1) + repository + migration
  `0004_create_subscriptions_table` (applied to Supabase)
- `BillingService`: `start_checkout`, `open_portal`, `handle_event` (webhook
  sync), `get_subscription`, `is_active`. Takes user primitives (id, email), so
  the billing package never depends on the auth package
- **Stripe is the source of truth**: local state is written only from a
  verified webhook, never from the checkout redirect. `handle_event` is
  idempotent, so Stripe retries are safe
- Endpoints: `POST /billing/checkout`, `POST /billing/portal`,
  `GET /billing/subscription`, `POST /billing/webhook` (signature-verified, no
  auth). `require_active_subscription` dependency as the v1 entitlement
- 13 unit tests, including the **real** `stripe.Webhook.construct_event` crypto
  path with a computed signature (no network, no mocked verification)

**Verified end-to-end against live Supabase** (12/12): billing routes
registered → new user starts inactive → tampered webhook rejected (400) →
correctly-signed subscription webhook activates the subscription → status/price
synced → cancellation webhook deactivates it (idempotent on replay) → cleaned
up. Checkout/portal call the Stripe API and are covered by unit tests with a
fake provider; end-to-end they need real Stripe test keys + the Stripe CLI.

Deferred (documented): feature-level entitlements/usage limits (v1 gates on one
active plan), invoice sync, coupons, trials config, tax, scheduled
reconciliation, subscription history — all post-v1.

## Next Development Steps

Tracked on the GitHub board: <https://github.com/users/Brijesh206/projects/3>
(milestone **v1 — Ship Week**, due 2026-07-19).

### v1 — required to ship

1. ~~**Email** (#7)~~ — done.
2. ~~**Email verification + password reset** (#4)~~ — done.
3. ~~**Stripe billing** (#6)~~ — done, above. (Needs your Stripe test keys +
   `STRIPE_PRICE_ID` in `.env` to exercise checkout/portal live.)
4. **Web app** (#10) — `apps/web` does not exist yet. Next.js: sign up, log in,
   verify, reset, pricing → checkout, one protected dashboard page.
5. **Deploy** (#11) — API + web deployed, migrations run on release, Stripe
   webhook reachable.

### Post-v1 (explicitly cut from the week)

Redis cache (#5), admin dashboard (#8), project-generator CLI (#9), OAuth,
session persistence/revocation, roles & permissions, storage, api_keys, worker,
analytics, notifications, observability, organizations/multi-tenancy.

### Cross-cutting hardening (not gating v1)

- `apps/api/tests/` (pytest + httpx) so route checks run in CI rather than as
  ad-hoc smoke scripts.
- Security headers middleware; CORS configuration.

## Next Development Steps

Two parallel tracks: **deepen auth** (highest leverage, security-critical) and
**add the next shared packages**. Suggested order:

### A. Finish the auth surface (recommended next)

1. **Password reset** — `PasswordResetToken` model + migration, request/confirm
   endpoints, single-use short-lived tokens (needs the mail package to send the
   email; can stub the sender first).
2. **Email verification** — verification token + `POST /auth/verify`, gate
   sensitive actions on `is_verified`.
3. **Refresh-token / session persistence + revocation** — a `sessions` (or
   `refresh_tokens`) table so logout and "revoke all sessions" actually
   invalidate tokens (JWT refresh is currently stateless).
4. **OAuth** — Google + GitHub via a provider adapter interface (account linking
   by verified email), per `docs/08-authentication.md`.
5. **Roles & permissions** — `role` on user + `require_permission(...)` helpers.
6. **Rate limiting + audit logging** on auth endpoints (depends on cache).

### B. Next shared packages (in order)

1. **cache** — Redis adapter (sessions, OTP, rate limiting, general cache).
2. **mail** — SMTP adapter + templates + queued send (unblocks reset/verify).
3. **storage** — Supabase Storage adapter behind a `StorageProvider` interface.
4. **billing** — Stripe behind a `BillingService`/adapter (subscriptions).
5. **api_keys** — hashed developer API keys with prefixes + scopes.
6. **worker** — Celery app + first tasks (send email, cleanup expired tokens).
7. **analytics**, **notifications**, **observability** (Sentry/PostHog).

### C. Cross-cutting hardening

- Add `apps/api/tests/` (pytest + httpx) so the route checks run in CI, not just
  ad-hoc smoke scripts.
- Add `organizations` + membership for multi-tenant products.
- Security headers middleware; CORS configuration.
- Resolve the `tests/` module-name collision (add `__init__.py` or configure
  `--import-mode=importlib`) so one `uv run pytest` runs everything.

## Pause Point

Development paused after completing the first pass of:

- `packages/database`
- `packages/common`
- `packages/logging`
- `packages/auth` (including HTTP routes in `apps/api`)
- `apps/api`

The platform is renamed to **FastForge**, auth works end-to-end against
Supabase over HTTP, and the codebase is ready to push to GitHub. Next session
can resume from the auth deepening track (A) or the cache package (B).
