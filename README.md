# FastForge

> **Build Once. Reuse Forever. Ship Fast.**

A production-ready SaaS foundation: FastAPI + Next.js monorepo with
authentication, billing, email, caching, API keys, an admin panel, background
workers, and a one-command Docker deploy already wired together.

You clone it, run one setup script, and start writing your product's business
logic. Everything below the business logic is done.

| | |
| --- | --- |
| **Backend** | FastAPI · SQLAlchemy 2 (async) · Pydantic v2 · Alembic · Taskiq/Celery · Python 3.13 |
| **Frontend** | Next.js 15 (App Router) · React 19 · TypeScript · Tailwind 4 · daisyUI |
| **Data** | PostgreSQL (Supabase or self-hosted) · Redis |
| **Deploy** | Docker Compose + Caddy (auto-HTTPS) on any VPS |

---

## Table of contents

1. [What you get](#what-you-get)
2. [Prerequisites](#prerequisites)
3. [Quick start (local)](#quick-start-local)
4. [Configuration](#configuration)
5. [Everyday commands](#everyday-commands)
6. [Project layout](#project-layout)
7. [Production deploy](#production-deploy)
8. [Troubleshooting](#troubleshooting)
9. [Documentation](#documentation)

---

## What you get

Already built and wired — not stubs:

- **Authentication** — email/password (argon2id), JWT access + refresh tokens,
  email verification, password reset, Google & GitHub OAuth.
- **Billing** — Stripe checkout, subscriptions, customer portal, signature-verified webhooks.
- **Admin panel** — `/admin`: user search, pagination, activate/deactivate, subscription overview.
- **API keys** — scoped developer keys with per-key rate limiting.
- **Email** — SMTP + templates, with a `console` provider so nothing sends by accident in dev.
- **Background jobs** — swappable queue: in-memory (zero setup), **Taskiq** or **Celery**, chosen with one env var.
- **Cache** — Redis-backed sessions, rate limiting, OTPs, token revocation (in-memory fallback for dev).
- **Logging** — structured JSON logs, request IDs, secret redaction.
- **Infra** — Dockerfiles, Compose for dev and prod, Caddy auto-HTTPS, GitHub Actions CI.

Scaffolded but not implemented yet: the `storage` / `notifications` /
`analytics` packages.

---

## Prerequisites

| Tool | Version | Why | Install |
| --- | --- | --- | --- |
| **Python** | 3.13+ | Backend runtime | Comes with `uv python install 3.13` |
| **uv** | latest | Python deps + workspace | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| **Node.js** | 20+ | Frontend runtime | [nodejs.org](https://nodejs.org/) |
| **pnpm** | 9.15 | Frontend deps (via corepack) | `corepack enable` |
| **Docker** | with Compose v2 | Postgres, Redis, Mailpit — and production | [docs.docker.com](https://docs.docker.com/get-docker/) |
| **Git** | any | — | — |

`make` is optional (shortcuts only). On Windows, use **WSL2** or Git Bash — the
shell scripts and Makefile assume a POSIX shell.

Verify:

```bash
uv --version && node -v && corepack pnpm -v && docker compose version
```

### Accounts you'll need

Only two are required to run locally — the rest are optional and stay disabled
while blank.

| Service | Required? | Used for |
| --- | --- | --- |
| — | — | **Nothing is required for local dev.** Postgres, Redis and mail all run locally via Docker. |
| [Supabase](https://supabase.com) | Production | Managed PostgreSQL (free tier is fine) |
| [Stripe](https://stripe.com) | Optional | Billing. Blank keys disable the billing endpoints. |
| [Google Cloud](https://console.cloud.google.com/apis/credentials) | Optional | Google sign-in. Blank = provider off. |
| [GitHub OAuth App](https://github.com/settings/developers) | Optional | GitHub sign-in. Blank = provider off. |
| Resend / Postmark | Production | Sending real email. Dev logs to console instead. |

---

## Quick start (local)

From a clean clone to a working app in five steps.

### 1. Install dependencies

```bash
uv sync --all-packages     # Python workspace (apps/api + packages/*)
corepack pnpm install      # Node workspace (apps/web)
```

### 2. Start the backing services

```bash
docker compose up -d       # Postgres :5432, Redis :6379, Mailpit :8025
```

These three run in Docker; the API and web app run on your host so you keep hot
reload and a working debugger.

### 3. Scaffold your product

```bash
python scripts/init_product.py
```

Interactive. It asks for a **product name** and which optional **modules** to
keep, then:

- creates `.env` from `.env.example` if you don't have one,
- rebrands `APP_NAME`, mail sender names, the database name, and `package.json`,
- comments out the routers of modules you disabled and blanks their env keys.

It deliberately does **not** rename the `fastforge_*` Python packages or the
`@fastforge/web` scope — those are the vendored platform, and renaming them
would conflict on every future `git merge fastforge/main`. See
[docs/20-creating-a-new-product.md](docs/20-creating-a-new-product.md).

> Run this **once**, in a fresh clone. It edits files in place.

### 4. Fill in `.env` and migrate

Open `.env` and set at minimum:

```bash
APP_SECRET_KEY=<openssl rand -hex 32>
JWT_SECRET_KEY=<openssl rand -hex 32>
ADMIN_EMAILS=you@example.com        # the email you'll sign up with, to reach /admin
```

The defaults for `DATABASE_URL` and mail already point at the Docker services
from step 2, so you don't need to touch them.

Then create the schema:

```bash
cd packages/database && uv run alembic upgrade head && cd ../..
# or: make migrate
```

### 5. Run it

Two terminals, both from the repo root:

```bash
# Terminal 1 — API
uv run uvicorn app.main:app --port 8000 --reload

# Terminal 2 — web
corepack pnpm --filter @fastforge/web dev
```

| | URL |
| --- | --- |
| Web app | http://localhost:3000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/v1/health |
| Mailpit (caught emails) | http://localhost:8025 |

**Verify it works:** sign up at http://localhost:3000/signup using the email in
`ADMIN_EMAILS` → open Mailpit and click the verification link → then open
http://localhost:3000/admin. If the admin dashboard loads, the whole stack —
database, auth, mail, cache — is working.

> Settings are read **once at startup**. Restart the API after editing `.env`.

---

## Configuration

All configuration is environment variables. Two annotated templates:

| File | For |
| --- | --- |
| [`.env.example`](.env.example) | Local development — copy to `.env` |
| [`.env.production.example`](.env.production.example) | Production — copy to `.env` on the server |

Never commit a real `.env`; `.gitignore` already blocks every variant except
the examples.

### The variables that matter most

| Variable | Notes |
| --- | --- |
| `APP_ENV` | `development` or `production`. Production **refuses to boot** with debug on or a short/placeholder secret, and hides `/docs`. This guard is intentional. |
| `APP_SECRET_KEY`, `JWT_SECRET_KEY` | Must be real 32-byte values in production: `openssl rand -hex 32`. |
| `DATABASE_URL` | Local Docker by default. For Supabase use the **pooler** URL with `sslmode=require`. |
| `CACHE_PROVIDER` | `memory` (dev default, no Redis needed) or `redis`. **Use `redis` in production** — on `memory`, rate limits and token revocation are per-worker and reset on restart. |
| `JOBS_PROVIDER` | `memory` (dev default, no broker or worker needed), `taskiq`, or `celery`. **Don't use `memory` in production** — jobs run in the API process with no retries, and a deploy drops whatever is in flight. |
| `ADMIN_EMAILS` | Comma-separated. Empty means nobody can reach `/admin`, which is the safe default. |
| `MAIL_PROVIDER` | `console` logs emails instead of sending. Switch to `smtp` for real delivery. |
| `STRIPE_*`, `GOOGLE_*`, `GITHUB_*` | Blank disables that feature cleanly — the app still boots. |
| `NEXT_PUBLIC_API_URL` | Include the `/api/v1` suffix. **Baked into the frontend at build time**, not read at runtime. |

---

## Everyday commands

```bash
make install     # uv sync --all-packages && pnpm install
make up          # start Postgres/Redis/Mailpit
make down        # stop them
make migrate     # alembic upgrade head
make test        # uv run pytest
make lint        # ruff + mypy + eslint
make format      # ruff format + autofix
```

Without `make`:

```bash
uv run pytest                                  # all Python tests
uv run pytest -m "not integration" packages    # skip tests needing live services
uv run ruff check . && uv run ruff format .
corepack pnpm --filter @fastforge/web build    # also runs eslint + tsc
python scripts/init_product.py --selftest      # self-check for the setup script
```

### Background jobs

Work that shouldn't block a request (email today, more later) goes through a
task queue. Which backend runs it is one env var — the code never changes:

| `JOBS_PROVIDER` | Broker | Worker needed? | Use it for |
| --- | --- | --- | --- |
| `memory` *(default)* | none | no | Local dev and tests. Jobs run in the API process — **no retries, and a restart drops them.** |
| `taskiq` | Redis | yes | Production. Async-native, matches this codebase. |
| `celery` | Redis / RabbitMQ | yes | Production. Familiar, big ecosystem, retries + Beat. |

Run the worker (not needed on `memory`):

```bash
cd apps/worker && python -m worker_app.main   # picks the right CLI for JOBS_PROVIDER
```

Adding a task is one function anywhere in a package, plus an import in
[apps/worker/worker_app/main.py](apps/worker/worker_app/main.py) so the worker
loads it:

```python
from fastforge_jobs import task

@task("reports.rebuild_daily")
async def rebuild_daily(*, account_id: str) -> None:
    ...   # a plain async function — no Celery or Taskiq decorator
```

Enqueue it from anywhere holding the queue:

```python
await task_queue.enqueue("reports.rebuild_daily", account_id=str(user.id))
```

Arguments must be JSON-serializable — every backend except `memory` sends them
across a process boundary. An unregistered name raises `UnknownTaskError` at
the call site rather than disappearing into the broker.

### Creating a migration

```bash
cd packages/database
uv run alembic revision --autogenerate -m "add widgets table"
uv run alembic upgrade head
```

Always read the generated migration before applying it — autogenerate guesses.

---

## Project layout

```
apps/
  api/          FastAPI app — thin routers, wiring only
  web/          Next.js app (App Router)
  worker/       Background job worker (taskiq or celery)
packages/       Reusable platform packages, vendored not published
  auth/  billing/  database/  cache/  common/  jobs/  logging/  mail/
  api_keys/  storage/  notifications/  analytics/  ui/
docker/         Dockerfiles (api, web, worker) + Caddyfile
docs/           Engineering handbook, 01–20
scripts/        init_product.py, seed.py, bootstrap.sh
```

Two files are the on/off switchboard for the whole platform:

- `apps/api/app/api/router.py` — which routers are registered
- `apps/api/app/lifespan/__init__.py` — which providers are wired

**The rule:** your product's code goes in `apps/`. Leave `packages/` alone so
`git merge fastforge/main` keeps merging cleanly. If you write the same thing
twice across two products, promote it into `packages/`.

---

## Production deploy

The whole stack — web, API, Redis, and Caddy with automatic HTTPS — is one
Compose file. **Deploying is a single command; nothing gets started by hand on
the server.** The API container runs `alembic upgrade head` before it serves,
and every service is `restart: unless-stopped`, so a reboot brings the product
back up on its own.

```
                    Internet
                       │
                  Caddy (:80/:443, auto TLS)
                   ├── app.yourdomain.com → web  (Next.js :3000)
                   └── api.yourdomain.com → api  (FastAPI :8000)
                                              │
                                    ┌─────────┼─────────┐
                                  Redis    worker   PostgreSQL
                              (same host)  (jobs)  (Supabase, external)
```

### What you need

- A VPS with Docker + Compose v2. **2 GB RAM recommended** — 1 GB works but the
  Next.js build needs swap (see below).
- A domain with two **A-records** pointing at the VPS IP:
  `api.yourdomain.com` and `app.yourdomain.com`.
- A PostgreSQL database (Supabase free tier is fine).

### Steps

```bash
# 1. Get the code on the box
git clone <your-repo> myproduct && cd myproduct

# 2. Configure
cp .env.production.example .env
nano .env      # see the checklist below

# 3. Brand it (skip if you already ran this before committing)
python scripts/init_product.py

# 4. (1 GB box only) add swap so the web build doesn't get OOM-killed
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile \
  && sudo mkswap /swapfile && sudo swapon /swapfile

# 5. Deploy — this is the whole thing
docker compose -f docker-compose.prod.yml up -d --build
```

**`.env` checklist** — the deploy fails fast if these are wrong, by design:

- [ ] `API_DOMAIN` and `WEB_DOMAIN` — both with live DNS A-records
- [ ] `APP_ENV=production` and `APP_DEBUG=false`
- [ ] `APP_SECRET_KEY` and `JWT_SECRET_KEY` — real values from `openssl rand -hex 32`
- [ ] `DATABASE_URL` — Supabase **pooler** URL, `DATABASE_SSL_MODE=require`
- [ ] `CACHE_PROVIDER=redis` and `REDIS_URL=redis://redis:6379/0` (service name, not `localhost`)
- [ ] `JOBS_PROVIDER=taskiq` (or `celery`) and `JOBS_BROKER_URL=redis://redis:6379/1` — **not `memory`**
- [ ] `FRONTEND_BASE_URL=https://<WEB_DOMAIN>` — email links and CORS depend on it
- [ ] `ADMIN_EMAILS` — or `/admin` stays locked to everyone
- [ ] `MAIL_*` — a real SMTP provider
- [ ] `STRIPE_*` — **live** keys, if you're billing

### Verify

```bash
curl https://api.yourdomain.com/api/v1/health    # -> {"status":"ok"}
open https://app.yourdomain.com
docker compose -f docker-compose.prod.yml ps     # all services healthy
```

### Shipping updates

```bash
git pull && docker compose -f docker-compose.prod.yml up -d --build
```

Same single command. Migrations run automatically on start.

> ⚠️ **The first deploy migrates your live database.** The entrypoint applies
> every pending revision against whatever `DATABASE_URL` points at, before
> serving a request. **Take a Supabase snapshot first.** If a migration fails
> the container exits rather than serve a stale schema — correct behaviour, but
> it means a bad revision takes the API down instead of degrading it.

### Two things that need a rebuild, not a restart

1. **`NEXT_PUBLIC_*` changes.** Next.js inlines these into the browser bundle at
   build time. Changing `WEB_DOMAIN` or `API_DOMAIN` means `up -d --build`.
2. **Any frontend code change.** Same reason.

Backend `.env` changes only need `docker compose -f docker-compose.prod.yml restart api`.

### Stripe webhook

Add an endpoint in the Stripe dashboard at
`https://api.yourdomain.com/api/v1/billing/webhook`, put its signing secret in
`.env` as `STRIPE_WEBHOOK_SECRET`, then restart the API.

### Other hosts

`docker/api/Dockerfile` and `docker/web/Dockerfile` are the units of
portability — no lock-in. On Railway / Render / Fly, point the platform at the
Dockerfile and set the same env vars. Prefer Vercel for the frontend? Import
the repo with **Root Directory = `apps/web`**, set `NEXT_PUBLIC_API_URL`, and
drop the `web` service from the compose file. See
[docs/16-deployment.md](docs/16-deployment.md).

---

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| API won't start: secret key error | `APP_ENV=production` rejects short or placeholder secrets. Generate real ones with `openssl rand -hex 32`. |
| `.env` edits do nothing | Settings load once at startup. Restart the API. |
| `DATABASE_SSL_MODE` validation error | An empty value is invalid — comment the line out for local, don't set it to `""`. |
| Connection refused on :5432 / :6379 | `docker compose up -d`, then `docker compose ps` to confirm they're healthy. |
| "Admin access required" | Your email isn't in `ADMIN_EMAILS`, the account's email isn't verified, or the API wasn't restarted after editing `.env`. |
| No emails arriving | Dev default is `MAIL_PROVIDER=console` — they're in the API logs. For a real inbox use Mailpit at http://localhost:8025. |
| Frontend calls `localhost` in production | `NEXT_PUBLIC_API_URL` is build-time. Rebuild: `up -d --build`. |
| Caddy won't issue a certificate | DNS A-records must resolve to the VPS **before** Caddy starts, and ports 80/443 must be open. Check `docker compose -f docker-compose.prod.yml logs caddy`. |
| Emails never arrive in production | `JOBS_PROVIDER` is still `memory`, or the `worker` container isn't running. Check `docker compose -f docker-compose.prod.yml logs worker`. |
| `UnknownTaskError` from the worker | The worker didn't import the module defining that task. Add the import to `apps/worker/worker_app/main.py`. |
| Celery worker starts but runs nothing on Windows | Prefork needs `fork()`. `python -m worker_app.main` adds `--pool=solo` automatically; a hand-written `celery` command needs it too. |
| Web build killed on a 1 GB VPS | Out of memory — add swap (step 4 above), or build the image elsewhere. |
| Port 3000/8000 already in use | Another stack is running. Stop it, or change the port. |

---

## Documentation

The `docs/` directory is the engineering handbook.

| | |
| --- | --- |
| **Start here** | [20-creating-a-new-product.md](docs/20-creating-a-new-product.md) — the product runbook: clone, scaffold, toggle modules, pull upstream updates |
| Architecture | [01-vision](docs/01-vision.md) · [02-architecture](docs/02-architecture.md) · [03-tech-stack](docs/03-tech-stack.md) · [04-folder-structure](docs/04-folder-structure.md) |
| Application | [05-backend](docs/05-backend.md) · [06-frontend](docs/06-frontend.md) · [07-database](docs/07-database.md) |
| Modules | [08-authentication](docs/08-authentication.md) · [09-billing](docs/09-billing.md) · [10-storage](docs/10-storage.md) · [11-email](docs/11-email.md) · [12-notifications](docs/12-notifications.md) · [13-cache](docs/13-cache.md) |
| Operations | [14-logging](docs/14-logging.md) · [15-observability](docs/15-observability.md) · [16-deployment](docs/16-deployment.md) · [17-performance](docs/17-performance.md) |
| Security | [18-security](docs/18-security.md) · [19-security-audit-2026-07](docs/19-security-audit-2026-07.md) — full audit with fixed and open findings |

[`AGENTS.md`](AGENTS.md) holds the coding conventions, written for AI coding
agents (Claude Code, Codex, Cursor) but equally the human style guide.

---

## License

Commercial. See your purchase terms.
