# FastForge — Local Dev Runbook

Two **separate** projects are involved. They are different apps with different
jobs — don't confuse them:

| Project | Path | What it is |
| --- | --- | --- |
| **Product boilerplate** | `indie-platform` (this repo) | The FastForge product: FastAPI API + Next.js web app + the **admin panel** |
| **Storefront + delivery** | `../fastforge-landing` | Marketing site + **Dodo payments** + GitHub repo delivery (Firebase auth) |

> ⚠️ **Port clash:** both stacks default to **API :8000** and **web :3000**.
> Run **one stack at a time**, or change the ports. You can't run both as-is.

---

## A. Product boilerplate (`indie-platform`) — API + web + admin panel

### Prerequisites (once)
- [uv](https://docs.astral.sh/uv/) and Node with `corepack` enabled.
- `uv sync --all-packages` and `corepack pnpm install` at the repo root.
- A root `.env` (copy from `.env.example`) with at least:
  `DATABASE_URL` (Supabase), `APP_SECRET_KEY`, `JWT_SECRET_KEY`, and
  **`ADMIN_EMAILS=your@email.com`** ← the email you'll log in with.
- Be on the branch that has the admin code: `git checkout feat/admin-dashboard`.

### 1. Backend (FastAPI) — from the repo root
```bash
uv run uvicorn app.main:app --port 8000 --reload
```
Runs on http://localhost:8000, docs at http://localhost:8000/docs.
It reads the **root** `.env` (that's why you run from the repo root).
Settings are read once at startup — **restart after editing `.env`**
(e.g. after adding `ADMIN_EMAILS`).

### 2. Frontend (Next.js) — separate terminal
```bash
corepack pnpm --filter @fastforge/web dev
```
Runs on http://localhost:3000. It talks to the API at
`http://localhost:8000/api/v1` by default (no env needed).

### 3. See the admin panel
1. Sign up / log in at http://localhost:3000/login with the email in
   `ADMIN_EMAILS`.
2. Open **http://localhost:3000/admin**.
   - **Overview** — total users, active/total subscriptions.
   - **Users** — search, paginate, view detail, activate/deactivate.
   - **Settings** — **theme selector** (daisyUI themes, applies to the admin
     panel only; saved to your browser).
3. Logging in with a **non-admin** email shows an "Admin access required"
   screen — that's the gate working.

> The admin theme (daisyUI) is scoped to `/admin` only — the landing, auth, and
> dashboard pages keep the FastForge brand theme.

---

## B. Storefront + Dodo payments (`../fastforge-landing`)

This is where the **Dodo payment → GitHub delivery** flow lives.

### Prerequisites (once)
- `backend/venv` created and deps installed; `frontend/` `npm install` done.
- `backend/.env` with Dodo keys (`DODO_API_KEY`, product IDs, `GITHUB_TOKEN`,
  `GITHUB_REPO`) — and `DODO_WEBHOOK_SECRET` (filled in step 4).
- `frontend/.env.local` with Firebase config + `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- Firebase Console → Authentication → enable **Email/Password** + **Google**.
- [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
  installed (for the webhook tunnel).

### 1. Backend (FastAPI) — from `../fastforge-landing/backend`
```bash
# bash
PYTHONPATH=. venv/Scripts/python.exe -m uvicorn app.main:app --port 8000 --reload
# PowerShell
$env:PYTHONPATH="."; venv/Scripts/python.exe -m uvicorn app.main:app --port 8000 --reload
```

### 2. Frontend (Next.js) — from `../fastforge-landing/frontend`
```bash
npm run dev            # http://localhost:3000
```

### 3. Tunnel for the Dodo webhook — separate terminal
The browser calls the backend directly at `localhost:8000`; the tunnel exists
**only** so Dodo can POST the webhook back to your machine.
```bash
cloudflared tunnel --url http://localhost:8000
# prints https://<random>.trycloudflare.com  — copy it
```

### 4. Register the webhook in the Dodo dashboard (test mode)
- **Developer → Webhooks → Add endpoint**
- URL = `https://<your-tunnel>.trycloudflare.com/api/webhooks/dodo`
- Subscribe to **`payment.succeeded`**
- Save → copy the **signing secret** → put it in `backend/.env` as
  `DODO_WEBHOOK_SECRET=…` → **restart the backend** (step 1).

### 5. Run the purchase flow
1. Open **http://localhost:3000/access** → it redirects to `/login` → sign up
   or sign in.
2. Back on `/access`: enter a **GitHub username you do NOT own** (⚠️ not the
   repo owner — GitHub can't add the owner as a collaborator, it 422s). Use a
   second/throwaway GitHub account you can accept the invite on.
3. Pick region → **Buy** → pay on Dodo with test card
   **`4242 4242 4242 4242`** (any future expiry / CVC).
4. You land on `/access?checkout=success`. Watch:
   - the **tunnel terminal** for `POST /api/webhooks/dodo`,
   - the **backend log** for a `200`.
5. The webhook grants repo access → the invited GitHub account gets an invite,
   and `/access` flips to **"You're in"** with the repo + clone command.

### Dodo gotchas
- **Restart the backend** after setting `DODO_WEBHOOK_SECRET` — until it's set,
  every webhook returns 400 (signature can't be verified).
- Use a GitHub username you can actually accept the invite on (not the repo
  owner).
- The Dodo key in use is **test mode** — live key + live products are needed for
  production.

---

## Quick reference

| Task | Command | Where |
| --- | --- | --- |
| Product API | `uv run uvicorn app.main:app --port 8000 --reload` | `indie-platform/` (root) |
| Product web | `corepack pnpm --filter @fastforge/web dev` | `indie-platform/` (root) |
| Admin panel | open `http://localhost:3000/admin` | browser |
| Storefront API | `PYTHONPATH=. venv/Scripts/python.exe -m uvicorn app.main:app --port 8000 --reload` | `fastforge-landing/backend/` |
| Storefront web | `npm run dev` | `fastforge-landing/frontend/` |
| Webhook tunnel | `cloudflared tunnel --url http://localhost:8000` | anywhere |
