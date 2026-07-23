# 18 — Security Standards

Permanent rules for every feature added to FastForge, by humans or AI.
These encode the decisions from the 2026-07 audit (docs/19). If a change
violates one of these, it does not merge.

## Authentication & sessions

- Passwords: argon2id only, via the `PasswordHasher` interface. 12–128 chars enforced in schemas. Never log, never echo back (including in validation errors — the error handler strips Pydantic `input`).
- JWTs: HS256 with `JWT_SECRET_KEY` (≥32 random chars in production — startup enforces this), 15-min access / 30-day refresh, `type` claim checked, `ver` claim must equal `users.token_version`.
- **Revocation rule**: any event that should end existing sessions (password reset, future "log out everywhere", suspected compromise) bumps `user.token_version`. Never add a parallel revocation mechanism.
- Email tokens (verification, reset): `secrets.token_urlsafe(32)`, stored SHA-256-hashed, single-use, TTL'd, superseded on re-issue. New single-use credentials must follow the same pattern via `fastforge_common.tokens`.
- Login must stay enumeration-safe: identical error + comparable timing for unknown email vs wrong password; password-reset request always returns the same 202.

## Authorization

- Every non-public endpoint depends on `get_current_user` (or a dependency built on it). Public endpoints are the explicit exception, not the default.
- Admin access = `ADMIN_EMAILS` allowlist **and** verified email (`require_admin`). Any future role system must keep the verified-email requirement.
- Ownership checks live in services (e.g. revoke_key checks `user_id`); a resource id in a path is never trusted alone.

## Rate limiting

- Any new unauthenticated endpoint that triggers work (auth, email, expensive queries) gets a `rate_limit(...)` dependency (`app/core/rate_limit.py`). Authenticated programmatic access is covered by per-API-key limits.
- Production must run Redis (`CACHE_PROVIDER=redis`) — the in-memory cache is per-process and resets on restart.
- Behind a proxy, run uvicorn with `--proxy-headers --forwarded-allow-ips=<proxy>` so limits key on real client IPs.

## Input/output

- All request schemas: Pydantic with `extra="forbid"`. All responses: explicit response schemas — never return ORM models or raw dicts.
- SQL only through repositories with SQLAlchemy expressions; string-built SQL is forbidden.
- Anything rendered into email HTML goes through the escaping renderer (`fastforge_mail.rendering`).
- Request bodies are capped at 1 MiB by middleware; mirror the cap at the reverse proxy. Endpoints needing more (uploads) must stream to storage, not buffer.

## Secrets & config

- Config only via Pydantic Settings; `os.getenv` in logic is forbidden.
- Secrets are `SecretStr`, never logged (the logging redactor also catches key-name patterns — keep sensitive keys named so it does: `*password*`, `*token*`, `*secret*`, `*api_key*`).
- `.env*` is gitignored except `.env.example`, which holds placeholders only. Production refuses placeholder/short secrets at startup — never weaken those validators.
- Generate secrets with `openssl rand -hex 32`. Rotate on any suspected exposure; `token_version` + API-key revocation make rotation cheap.

## HTTP

- Security headers come from `app/middleware/security.py` (API) and `next.config.mjs` (web) — new responses inherit them; don't bypass the middleware.
- CORS stays a single explicit origin. Widening to a list is a deliberate config change; `*` with credentials is forbidden.
- Errors: raise `AppError` subclasses; unhandled exceptions return a generic 500. Never include stack traces, SQL, or internal identifiers in responses.

## Billing & webhooks

- Webhooks are trusted only after signature verification; state changes are idempotent and drop out-of-order events (`last_event_at`). Any new webhook consumer (other providers) must follow the same three rules.
- Client redirects (checkout success/cancel pages) never mutate state.

## Dependencies & CI

- CI blocks on: ruff, mypy, pytest, `pip-audit`, `pnpm audit --prod`, and the Next production build. Do not mark these advisory.
- New dependencies need a reason the stdlib/an existing dep can't cover (see AGENTS.md philosophy). Lockfiles (`uv.lock`, `pnpm-lock.yaml`) are always committed.

## Security review checklist (PRs touching auth/billing/admin/config)

- [ ] New endpoints authenticated (or explicitly, deliberately public) and rate-limited if unauthenticated
- [ ] Request schemas `extra="forbid"`; responses via explicit schemas
- [ ] No secret can appear in logs, errors, or responses (check validation paths)
- [ ] Session-ending events bump `token_version`
- [ ] DB changes have a migration; destructive migrations have a downgrade
- [ ] Tests cover the failure paths (401/403/429), not just the happy path
- [ ] `pip-audit`/`pnpm audit` still clean

## AI development guidelines

AGENTS.md governs structure and style. For security specifically, AI agents
must: (1) copy the existing pattern for the nearest equivalent feature
(auth token issuance, API-key hashing, webhook verification) instead of
inventing a new mechanism; (2) never relax a validator, TTL, length limit, or
startup guard to make a test pass; (3) treat anything user-supplied as
hostile at every layer, not just the schema; (4) run the checklist above
before declaring a security-adjacent task done; (5) when a requested change
conflicts with this document, say so instead of silently complying.
