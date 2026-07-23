# Creating a New Product from FastForge

> How to spin up a new product on the FastForge platform, keep it updated, and
> turn modules on/off. This is the runbook — follow it top to bottom.

The mental model: FastForge is **not a library you install** — it's a monorepo
you **copy**. The `packages/*` (`fastforge_*`) and `apps/api` + `apps/web` are the
platform; **your product is new code you add on top**. The apps are deliberately
thin — `apps/api/app/lifespan/__init__.py` wires providers and
`apps/api/app/api/router.py` registers routers. Those two files are the on/off
switchboard.

---

## 1. Clone the platform

Copy FastForge into a fresh repo and keep FastForge as a remote so you can pull
updates later (step 4):

```bash
git clone <fastforge-repo-url> my-product
cd my-product
git remote rename origin fastforge           # FastForge stays as upstream
git remote add origin <your-new-empty-repo>  # your product's own remote
git push -u origin main
```

## 2. Scaffold: rebrand + pick modules

Install deps, then run the setup script **once**:

```bash
uv sync --all-packages     # or: make install
pnpm install
python scripts/init_product.py
```

The script (`scripts/init_product.py`) prompts for:

1. **Product name** — e.g. `Velorex`. Rebrands `APP_NAME`, `MAIL_FROM_NAME`,
   `MAIL_PRODUCT_NAME`, the DB name, and the `package.json` names/descriptions.
2. **Modules** — a `[Y/n]` per toggleable module. Disabling one comments its
   router lines and blanks its env keys.

It creates `.env` from `.env.example` if it doesn't exist yet.

**What it renames vs. keeps — and why it matters:**

| Renamed (branding, what users see) | Kept as-is (the platform) |
| --- | --- |
| `APP_NAME`, mail from/product name, DB name | `fastforge_*` Python packages + imports |
| `package.json` name + description | `@fastforge/web` workspace scope |

The `fastforge_*` names are **kept on purpose** — they're the vendored platform.
Renaming them (like renaming `react`) would make every future
`git merge fastforge/main` conflict on every import line. Branding is what the
world sees; packages are what you merge. Don't fight this.

If you want a fully clean git history for the product, optionally:
`rm -rf .git && git init && git remote add fastforge <url>`.

## 3. Run it

Two terminals, from the repo root:

```bash
uv run uvicorn app.main:app --port 8000 --reload
pnpm --filter @fastforge/web dev
```

Log in at http://localhost:3000/login with an email in `ADMIN_EMAILS`, open
`/admin` to confirm the platform is alive. See `LOCAL_DEV.md` for the full
local-dev runbook. Now auth, billing, API keys, mail, cache, and the admin panel
are already running — you only build your product's business logic.

## 4. Build your product's business logic

A backend feature is one folder (copy the shape of `apps/api/app/billing/`):

```
apps/api/app/<yourfeature>/
  models.py schemas.py repository.py service.py router.py dependencies.py
```

Register it with **one line** in `apps/api/app/api/router.py`
(`api_router.include_router(...)`). Frontend goes in
`apps/web/src/features/<yourfeature>/`. See `docs/04-folder-structure.md`.

Rule: if you write the same thing across two products, promote it into
`packages/`. Every product improves the platform.

---

## Pulling later FastForge updates

There's no built-in updater (packages are path deps, not published). Use the
`fastforge` git remote from step 1:

```bash
git fetch fastforge
git merge fastforge/main        # or: git cherry-pick <commit> for one fix
```

- **Merge, don't rebase** — your product has diverged; merge keeps history sane.
- Conflicts land almost entirely in `apps/` (files you edited), rarely in
  `packages/*` (which you leave alone). **This is exactly why you don't edit
  package source** — change behavior through config/adapters instead, and every
  update merges cleanly.
- Cherry-pick when you only want one fix (e.g. a security patch).

When you're running several products at once and want real versioned updates,
the upgrade path is publishing `packages/*` to a private registry and depending
on e.g. `fastforge-auth==1.2.0`. YAGNI until then.

---

## Turning modules on/off

Opt-out = **unwire, don't delete** (deleting a package makes every future merge
try to re-add it). `scripts/init_product.py` does this at scaffold time; to
change it afterwards, edit by hand.

**Currently toggleable** (what the switchboard actually supports today):

| Module | How it's disabled |
| --- | --- |
| Billing (Stripe) | comment its lines in `api/router.py` + blank `STRIPE_*` |
| API keys | comment its lines in `api/router.py` |
| Google OAuth | blank `GOOGLE_CLIENT_ID/SECRET` (already env-gated) |
| GitHub OAuth | blank `GITHUB_CLIENT_ID/SECRET` (already env-gated) |

**Core, not toggleable:** `database`, `common`, `auth`, `cache`, `logging`,
`mail` — the app won't boot without them, and `auth`/`admin` import
`fastforge_billing` internally (so billing's *package* stays even when its
*endpoints* are off).

To re-enable a module later, uncomment its lines in
`apps/api/app/api/router.py` and set its env keys. Restart the API so it
re-reads `.env`.

**Adding a new toggleable module:** when you wire storage / notifications /
analytics with their own routers, add an entry to the `MODULES` dict in
`scripts/init_product.py` (label, the router lines to comment, env keys to
blank) — one entry each.

---

## Swapping a provider (e.g. Stripe → Paddle)

Every provider routes through an interface (`BillingProvider`,
`StorageProvider`, OAuth providers, mail via `create_email_provider`, cache via
`create_cache`). To swap:

1. Write a new adapter implementing the interface (mirror the existing one, e.g.
   `packages/billing/.../adapters/stripe_provider.py`).
2. Change **one line** where it's constructed — for billing that's
   `apps/api/app/lifespan/__init__.py` (`app.state.billing_provider = ...`).
3. Add the new provider's keys to `.env`.

Your services, routers, models, and frontend stay untouched — they only know the
interface, never the SDK. See the adapter pattern in `docs/02-architecture.md`.

---

## TL;DR

```
clone repo → python scripts/init_product.py → fill .env → build your feature
updates:  git merge fastforge/main
opt-out:  unwire in api/router.py + blank env (never delete)
swap:     new adapter + one wiring line in lifespan
```
