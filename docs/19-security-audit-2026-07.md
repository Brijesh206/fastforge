# Security & Production-Readiness Audit — 2026-07-19

Full-repository audit of FastForge (backend, frontend, packages, infra, CI,
dependencies). Every finding is listed with severity and status. Fixes marked
**FIXED** were applied in this audit; **OPEN** items are recommendations with
a described path.

## Executive summary

The codebase is in good shape for its age: argon2id password hashing, hashed
single-use tokens, Stripe-webhook signature verification with out-of-order
protection, parameterized queries everywhere, a clean layered architecture
(router → service → repository), strict Pydantic schemas (`extra="forbid"`),
secret redaction in logging, and per-key API-key rate limiting. No dependency
has a known CVE after this audit.

The audit found **no remote-code-execution, injection, or data-exposure
vulnerability**. The significant gaps were: no brute-force protection on auth
endpoints, stateless refresh tokens that survived a password reset, admin
access grantable to an unverified account, validation errors echoing
submitted secrets, and missing production guards (debug mode, placeholder
secrets, open docs). All of those are fixed.

## Risk assessment & vulnerability report

### High — all fixed

| # | Finding | Status |
|---|---------|--------|
| H1 | **No rate limiting on login/register/password-reset/resend** — unlimited credential stuffing and email bombing. | **FIXED** — per-IP fixed-window limiter (`app/core/rate_limit.py`) backed by the platform Cache, applied to all four endpoints. Returns 429 + `Retry-After`. |
| H2 | **Refresh tokens survive password reset** — an attacker holding a stolen refresh token (30-day TTL) kept access after the owner recovered the account. | **FIXED** — `users.token_version` (migration 0007) embedded in every JWT as `ver`; checked on access-token use and refresh; bumped on password reset, revoking all outstanding tokens. |
| H3 | **Admin allowlist matched unverified accounts** — if an `ADMIN_EMAILS` address had no account yet, whoever registered it first got admin without proving inbox ownership. | **FIXED** — `require_admin` now also requires `is_verified`. |
| H4 | **`.env.supabase.bak` (live Supabase credentials) not gitignored** — one `git add .` from a public leak. | **FIXED** — `.gitignore` now ignores `.env.*` (except `.env.example`) and `*.bak`. **Action for you: rotate the Supabase password if that file ever left this machine.** |

### Medium — all fixed

| # | Finding | Status |
|---|---------|--------|
| M1 | Validation errors echoed submitted values (Pydantic `input`) — a too-short password came back in the response body and could land in logs. | **FIXED** — handler now returns only `loc`/`msg`/`type`. |
| M2 | No production startup guards — `APP_DEBUG=true` or `change-me-in-production` secrets would boot in production. | **FIXED** — `BaseAppSettings` and `AuthSettings` refuse to start with `APP_ENV=production` + debug on, placeholder-looking secrets, or secrets < 32 chars. |
| M3 | Swagger/`/docs`/`/openapi.json` exposed in production. | **FIXED** — disabled when `APP_ENV=production`. |
| M4 | Login timing oracle — unknown emails skipped the argon2 verify, so response time revealed whether an address is registered. | **FIXED** — dummy hash burns equivalent time on the unknown-user path. |
| M5 | No security headers on either app. | **FIXED** — API middleware sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control: no-store`, HSTS in production; Next.js sets the equivalent via `headers()` and drops `X-Powered-By`. |
| M6 | No request body size limit (memory-exhaustion DoS on JSON parse). | **FIXED** — 1 MiB Content-Length cap in the same middleware (413). Streamed bodies without Content-Length are the reverse proxy's job — enforce `client_max_body_size` there too. |
| M7 | `postcss@8.4.31` (transitive via Next) had a moderate advisory (GHSA-qx2v-qp2m-jg93). | **FIXED** — pnpm override to ≥ 8.5.10 (resolved 8.5.19); web build verified green. |
| M8 | `uvicorn` dev entry hardcoded `0.0.0.0:8000, reload=True`; `API_RELOAD` defaulted true. | **FIXED** — `run()` now uses settings; reload defaults off and is forced off in production. |

### Low / informational

| # | Finding | Status |
|---|---------|--------|
| L1 | Tokens in `localStorage` (XSS-readable). Mitigated by 15-min access TTL + revocation via token_version. | **OPEN** — the hardening upgrade is httpOnly-cookie sessions + CSRF protection; a deliberate, breaking API change. See "Remaining recommendations". |
| L2 | No server-side logout (client clears storage; refresh token lives until expiry). | **OPEN** — bump `token_version` on logout if "log out everywhere" is wanted; costs all sessions, which is acceptable for a boilerplate. |
| L3 | Registration reveals whether an email exists (409). Standard tradeoff; password-reset flow is already enumeration-safe. | Accepted. |
| L4 | Rate limiting keys on `request.client.host`; behind a proxy all clients share the proxy IP until uvicorn runs with `--proxy-headers` behind a trusted proxy. | Documented in `rate_limit.py` and docs/18. |
| L5 | Frontend error parser only read FastAPI's `detail`, never the platform `{error:{message}}` envelope — users saw "Request failed (409)" instead of real messages. | **FIXED** in `messageFrom`. |
| L6 | CI ran no dependency vulnerability scanning. | **FIXED** — `pip-audit` (Python) and `pnpm audit --prod` (JS) steps added. |
| L7 | `uv.lock` listed in `.gitignore` while tracked. | **FIXED** — removed from `.gitignore` (lockfiles must be committed). |
| L8 | Untracked AI-tooling dirs (`.agents/`, `.continue/`, `.windsurf/`, `skills-lock.json`) polluted the tree and ruff output. | **FIXED** — gitignored. |
| L9 | Admin email search passes `%`/`_` into `ILIKE` as wildcards. Parameterized (no injection), admin-only; cosmetic. | Accepted. |
| L10 | API-key auth writes `last_used_at` on every request (1 write/request). | **OPEN** — debounce (update only if older than N minutes) if API-key traffic grows. |

### Explicitly checked, no issue found

SQL injection (all queries parameterized via SQLAlchemy), XSS (React escaping;
email templates HTML-escape all variables before `string.Template`
substitution — no Jinja SSTI surface), CSRF (bearer-token API, no cookie
auth), SSRF (no user-supplied URL fetching), open redirect (no redirect
endpoints), path traversal (no file-serving endpoints), command injection (no
subprocess use), mass assignment (`extra="forbid"` on all request schemas;
responses built from explicit schemas), JWT algorithm confusion (algorithm
pinned from settings, `decode` restricted to that list, token `type` claim
checked), webhook forgery (Stripe signature verified before parsing; unknown
customers ignored; out-of-order events dropped via `last_event_at`), IDOR
(API-key revoke and admin endpoints check ownership/allowlist), replay of
email tokens (single-use, hashed, TTL'd, superseded on re-issue), secrets in
git history (none found — `.env` never tracked), unsafe deserialization
(none — JSON only), CORS (single explicit origin, credentials scoped to it).

## Architecture review

Verdict: **sound, and appropriately sized**. Clean dependency direction
(apps → packages; packages never import apps; cross-feature orchestration
like AdminService lives in the app). Interfaces exist exactly where a second
implementation is real (Cache: memory/redis; EmailProvider: console/smtp;
BillingProvider, PasswordHasher, TokenService). Settings are per-package
Pydantic Settings; no `os.getenv` in logic. Transaction boundaries are owned
by FastAPI dependencies (`get_db_transaction`), services stay commit-free.

Over-engineering scan (ponytail-audit), ranked, **not applied** — these are
listed for a conscious decision since several are deliberate placeholders:

- `delete:` empty stub packages `packages/analytics`, `packages/notifications`, `packages/storage`, `packages/ui`, `apps/worker`, `apps/docs`, `scripts/seed.py`, `app/startup/` — all TODO one-liners. Recreate when actually built; empty scaffolding invites drift. [packages/, apps/]
- `delete:` soft-delete machinery (`SoftDeleteMixin`, `soft_delete`/`restore`/`include_deleted` in BaseRepository) — no model uses it. [packages/database]
- `stdlib:`-adjacent duplicate: `fastforge_auth/tokens.py` re-implements `fastforge_common.tokens` (generate + SHA-256 hash). Use the common module. [packages/auth]
- `yagni:` `AuthProvider` enum — exported, never used (OAuth future). [packages/auth/enums.py]
- `yagni:` `SortParams`/`sorting.py` — no caller passes a sort; BaseRepository's default ordering covers everything today. [packages/database]
- `yagni:` `options: list[ORMOption]` params on `get_by_id`/`list_paginated` — never passed. [packages/database]
- `shrink:` `/health` duplicates `/ready` (`health()` just calls `ready()`). Keep `/live` + `/ready`, drop `/health` or alias it. [apps/api/app/health]

net: ~-600 lines possible, -0 deps. Correctness/security items were handled
in the main audit, not here.

## Performance review

- Biggest lever is documented already: local Postgres in dev vs remote Supabase (~330 ms/query tax).
- `pool_pre_ping` + `pool_recycle` correctly configured and documented; connection pool sized (5+10 overflow) sanely for a small deployment.
- API-key auth costs an extra transaction + a write per request (L10 above).
- Email sends run in `BackgroundTasks` off the request path; SMTP runs in a thread. Acceptable until volume demands a queue (documented in code).
- Admin list endpoint paginates with capped `page_size` (≤100) — no unbounded queries anywhere.
- Frontend: static prerender for all pages, 102 kB shared JS — fine.

## Production-readiness checklist

| Area | State |
|------|-------|
| Env validation at startup | ✅ Pydantic Settings, fail-fast; production guards added |
| Migrations | ✅ Alembic, linear chain 0001–0007 |
| Health endpoints | ✅ `/live`, `/ready` (DB-checked) |
| Structured logging + request IDs + redaction | ✅ |
| Error envelope, no internals leaked | ✅ (unhandled → generic 500, logged with stack) |
| Graceful shutdown | ✅ cache + engine disposed in lifespan |
| Rate limiting | ✅ auth endpoints (per-IP) + per-API-key |
| Security headers | ✅ both apps |
| CI: lint, types, tests, dep audit | ✅ (audit steps added) |
| Dockerfiles | ❌ **still TODO stubs** — write real multi-stage, non-root images before selling this as deploy-ready |
| docker-compose app services | ❌ commented out pending Dockerfiles |
| Monitoring/alerting hooks | ❌ `SENTRY_DSN` env exists, nothing wired |
| Background jobs | ❌ worker is a stub; email retry depends on it |

## Dependency audit

- **Python**: `pip-audit` against the full uv lock export — no known vulnerabilities. Versions current (FastAPI 0.115+, SQLAlchemy 2, PyJWT 2.x, argon2-cffi, stripe 12.x, redis 6). No unnecessary or duplicate packages found; every declared dependency is imported.
- **JS**: `pnpm audit --prod` clean after the postcss override. Dependency count is admirably small (next, react, lucide-react + dev tooling).
- Both audits now run in CI on every push/PR.

## Code quality

Consistently high: full type hints (mypy strict-ish, clean), docstrings that
explain *why*, `ponytail:` comments marking deliberate ceilings, tests for
every package (129 passing). The only quality bug found (frontend error
envelope mismatch, L5) is fixed. Test gap worth closing next: `apps/api` has
zero endpoint tests — the auth flows are tested at service level but no
FastAPI TestClient coverage exists (see recommendations).

## Changes made in this audit

Backend: `app/core/rate_limit.py` (new), `app/middleware/security.py` (new),
`app/core/errors.py`, `app/main.py`, `app/config/__init__.py`,
`app/auth/router.py`, `app/auth/dependencies.py`, `app/admin/dependencies.py`,
`fastforge_common/config.py`, `fastforge_auth/{config,models/user,schemas/auth,
interfaces/token_service,adapters/jwt_token_service,services/auth_service,
__init__}.py`, migration `0007_add_user_token_version.py`.
Frontend: `lib/api.ts`, `next.config.mjs`. Infra: `.gitignore`, `.env.example`,
`package.json` (postcss override), `.github/workflows/ci.yml`.
Tests: auth fakes/tests updated for token versioning + new regression test
`test_password_reset_revokes_outstanding_token_pairs`.

Verified: 129 Python tests pass, ruff clean, mypy clean, API app constructs,
Next.js production build succeeds, both dependency audits clean.

## Remaining recommendations (priority order)

1. **Run migration 0007 against the live Supabase DB** (see memory/runbook) before deploying this branch.
2. **Rotate the Supabase password** if `.env.supabase.bak` ever synced anywhere.
3. **Write the real Dockerfiles** (multi-stage, non-root `USER`, healthcheck, uv/pnpm layer caching) and un-comment the compose services — the one production-readiness gap that blocks "deploy directly".
4. **Add API endpoint tests** (httpx `AsyncClient` + TestClient against the app with a test DB): register→verify→login→refresh→delete happy path, 401/403/429 paths.
5. **httpOnly-cookie session upgrade** (removes L1/L2): API sets `Secure; HttpOnly; SameSite=Lax` cookies, CORS stays single-origin, add CSRF token on state-changing routes, Next middleware reads the session cookie server-side. Do it as one deliberate PR.
6. Wire **Sentry** (env var already exists) in `lifespan` + log handler.
7. Decide on the ponytail-audit deletions above (stubs, soft-delete, sorting).
8. When the worker lands, move email sends to it with retry/backoff.

## Long-term maintenance

- Dependency audits are now CI-blocking; renovate/dependabot would close the loop on upgrades.
- Re-run this audit checklist (docs/18-security.md has the standards) whenever a new package is added or an auth-adjacent change lands.
- Keep `docs/` numbered files in sync with new packages — they are the product being sold as much as the code.
