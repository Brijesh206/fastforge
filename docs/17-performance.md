# 17 — Performance Engineering Guidelines

Rules every new page, API, and module follows by default so the codebase stays
fast as it grows. These come from a measured audit (see the "Measured" notes).

## The one that dwarfs the rest: where is your dev DB?

The app code is thin and clean. In development the dominant cost is **network
distance to the database**. Measured: ~330ms round-trip to Supabase `us-east-1`
from India, vs <1ms to local Postgres. Every query, every `SELECT 1`, pays it.

- **Develop against local Postgres.** `docker compose up -d postgres` — it is
  already wired, migrations run against it, `.env.example` defaults to it. Point
  `DATABASE_URL` at Supabase only when you specifically need its data.
- When you *do* use a remote DB, set `DATABASE_POOL_PRE_PING=false` to drop the
  per-request `SELECT 1` round-trip (`pool_recycle` keeps connections fresh).
- **Never fix "slow API" by adding caching before you have checked how far away
  the DB is and how many round-trips the endpoint makes.** Distance × round-trips
  is almost always the answer.

## The other environmental one: OneDrive

This repo lives under `OneDrive\Desktop`. OneDrive's sync filter intercepts
every file read/write and can re-upload `.next/` and `node_modules/` churn while
the dev server is running — it slows file watching, HMR, and installs.

- **Move the working copy out of any synced folder** (e.g. `C:\dev\indie-platform`),
  or at minimum exclude `node_modules/`, `.next/`, `.venv/` from OneDrive sync
  and from Windows Defender real-time scanning.

---

## Frontend

**Server vs Client Components**
- Default to a **Server Component**. Add `"use client"` only for a file that
  actually uses hooks, browser APIs, or event handlers.
- This app uses a localStorage Bearer-token SPA model, so auth/dashboard pages
  are legitimately client — that's an architecture choice, not a default. New
  pages that only render data (marketing, static content) stay server.
- Push `"use client"` **down the tree**: a mostly-static page with one
  interactive widget makes the *widget* a client component, not the whole page.

**Compilation / DX**
- Dev runs on **Turbopack** (`next dev --turbopack`). Measured: route recompiles
  ~2–3× faster than webpack (`/login` 1.31s → 0.42s), startup 4.8s → 2.3s.
- Keep the dependency graph lean. Before adding a UI library, check whether the
  existing primitives in `components/ui/` + Tailwind cover it.

**Imports & bundle**
- Import icons/utilities by name (`import { Check } from "lucide-react"`), never
  `import * as`. Avoid barrel files that re-export a whole directory — they defeat
  tree-shaking and slow compile.
- daisyUI is scoped to `.ff-admin` (admin only); don't pull daisyUI classes into
  brand pages. The 20 admin themes are a shipped feature — leave them.

**Data fetching**
- Fetch independent resources in **parallel** (`Promise.all`), never a waterfall
  of awaited calls. Each serial call to a remote-backed API is a full RTT.

## Backend

**Async & round-trips**
- Everything on the request path is `async`. Never call a sync/blocking client in
  a handler.
- **Count your round-trips.** The cost of an endpoint ≈ (DB RTT) × (number of
  sequential queries). Minimise the count before optimising anything else.
- Sequential independent queries against a shared `AsyncSession` cannot simply be
  `gather`ed (the session isn't concurrency-safe). Prefer **one query** (a
  combined `SELECT` / subqueries) over N. Example: `AdminService.stats()` issues
  3 counts — fold into one round-trip if it ever gets hot.

**Dependencies & services**
- Process-wide singletons (hashers, token service, email service, engine) are
  built once at startup and read off `app.state` — never construct them per
  request. Follow this for any new shared client.
- Services own business logic; the DB dependency owns the transaction boundary
  (`get_db_session` read-scoped, `get_db_transaction` for writes). Don't commit
  inside a service.

**Connection pool**
- `pool_pre_ping` is configurable and defaults on for prod safety; off for a far
  DB. Don't hardcode engine options — thread them through `DatabaseSettings`.

**Middleware & logging**
- Middleware runs on **every** request — keep it allocation-light and never let
  it touch the DB or do blocking I/O. The request-logging middleware is the model:
  bind context, time, log, clear.

## Database

- **No N+1.** Loading a parent then looping child queries is banned; use a join
  or `selectinload`. Default to explicit loading, not lazy (`expire_on_commit`
  is already off).
- **Paginate every list endpoint** (`PaginationParams`) — never `SELECT *` an
  unbounded table.
- **Index every column you filter or sort on** (e.g. the user email lookup).
  Add the index in the same migration as the query that needs it.
- Wrap multi-write operations in a single transaction (`get_db_transaction`); one
  commit, not one per write.

## Performance checklist for every new feature

- [ ] New page: is it a Server Component? If `"use client"`, is it justified?
- [ ] Independent fetches run in parallel, not a waterfall.
- [ ] New endpoint: how many DB round-trips? Can it be fewer?
- [ ] List endpoint is paginated and its filter columns are indexed.
- [ ] No new dependency that existing primitives + stdlib already cover.
- [ ] No blocking I/O in a handler or middleware.
- [ ] Dev pointed at local Postgres, not the remote DB.
