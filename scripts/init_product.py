#!/usr/bin/env python3
"""Scaffold a new product from FastForge: rebrand + unwire unwanted modules.

Run once inside a fresh clone, from the repo root:

    python scripts/init_product.py

It renames the *branding* (not the fastforge_* packages — those stay vendored so
`git merge fastforge/main` keeps working) and comments out the routers for
modules you don't want (it never deletes packages). Self-check: --selftest.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Only what is genuinely toggleable today. Billing/api_keys own routers; OAuth is
# env-gated (blank = off). Everything else (db, auth, cache, mail) is core or
# imported internally by auth/admin — ripping it out would break the app.
MODULES: dict[str, dict] = {
    "billing": {
        "label": "Billing — Stripe checkout, subscriptions, customer portal endpoints",
        "router_lines": [
            "from app.billing.router import router as billing_router",
            "api_router.include_router(billing_router)",
        ],
        "env_blank": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "STRIPE_PRICE_ID"],
    },
    "api_keys": {
        "label": "API keys — developer API authentication endpoints",
        "router_lines": [
            "from app.api_keys.router import router as api_keys_router",
            "api_router.include_router(api_keys_router)",
        ],
        "env_blank": [],
    },
    "google_oauth": {
        "label": "Google OAuth sign-in",
        "router_lines": [],
        "env_blank": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
    },
    "github_oauth": {
        "label": "GitHub OAuth sign-in",
        "router_lines": [],
        "env_blank": ["GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"],
    },
}

MARKER = "  # disabled by init_product"
ROUTER_FILE = ROOT / "apps" / "api" / "app" / "api" / "router.py"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
ROOT_PKG = ROOT / "package.json"
WEB_PKG = ROOT / "apps" / "web" / "package.json"


# --- pure helpers (covered by --selftest) ------------------------------------

def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "product"


def set_env(text: str, key: str, value: str) -> str:
    out = [f"{key}={value}" if ln.startswith(f"{key}=") else ln for ln in text.splitlines()]
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def comment_out(text: str, needles: list[str]) -> str:
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped and not stripped.startswith("#") and any(n in line for n in needles):
            indent = line[: len(line) - len(stripped)]
            out.append(f"{indent}# {stripped}{MARKER}")
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def apply_env(text: str, name: str, slug: str, disabled: list[str]) -> str:
    for key in ("APP_NAME", "MAIL_FROM_NAME", "MAIL_PRODUCT_NAME"):
        text = set_env(text, key, name)
    text = text.replace("fastforge_platform", f"{slug}_platform")
    for mod in disabled:
        for key in MODULES[mod]["env_blank"]:
            text = set_env(text, key, "")
    return text


def apply_root_pkg(text: str, name: str, slug: str) -> str:
    return text.replace('"name": "fastforge"', f'"name": "{slug}"').replace("FastForge", name)


def apply_web_pkg(text: str, name: str) -> str:
    # Only the capitalized brand token; leaves the "@fastforge/web" scope intact.
    return text.replace("FastForge", name)


# --- interactive driver ------------------------------------------------------

def ask_name() -> str:
    while True:
        name = input("Product name (e.g. Velorex): ").strip()
        if name:
            return name
        print("  Name can't be empty.")


def ask_modules() -> list[str]:
    print("\nEnable these modules? (Enter = keep, 'n' = disable)")
    disabled = []
    for key, meta in MODULES.items():
        ans = input(f"  {meta['label']} [Y/n]: ").strip().lower()
        if ans in ("n", "no"):
            disabled.append(key)
    return disabled


def main() -> None:
    print("FastForge — new product setup\n")
    name = ask_name()
    slug = slugify(name)
    disabled = ask_modules()

    print(f"\nProduct: {name}  (slug: {slug})")
    print("Disabled:", ", ".join(disabled) if disabled else "none (all modules kept)")
    if input("\nApply? [y/N]: ").strip().lower() not in ("y", "yes"):
        print("Aborted. Nothing changed.")
        return

    # .env — create from example if missing, then rebrand + blank disabled keys.
    if not ENV_FILE.exists():
        if not ENV_EXAMPLE.exists():
            sys.exit("No .env and no .env.example to copy from.")
        shutil.copyfile(ENV_EXAMPLE, ENV_FILE)
        print("Created .env from .env.example")
    ENV_FILE.write_text(apply_env(ENV_FILE.read_text(), name, slug, disabled), encoding="utf-8")

    # Router — comment out the include + import lines of disabled modules.
    needles = [ln for m in disabled for ln in MODULES[m]["router_lines"]]
    if needles:
        ROUTER_FILE.write_text(comment_out(ROUTER_FILE.read_text(), needles), encoding="utf-8")

    # package.json branding (name + description only; workspace scope left alone).
    ROOT_PKG.write_text(apply_root_pkg(ROOT_PKG.read_text(), name, slug), encoding="utf-8")
    WEB_PKG.write_text(apply_web_pkg(WEB_PKG.read_text(), name), encoding="utf-8")

    print(f"\nDone. {name} is scaffolded.")
    print("Kept as-is on purpose: fastforge_* packages and the @fastforge/web scope")
    print("(so `git merge fastforge/main` stays clean). Re-enable a module by")
    print("uncommenting its lines in apps/api/app/api/router.py.")
    print("Next: restart the API so it re-reads .env.")


# --- self-check --------------------------------------------------------------

def _selftest() -> None:
    assert slugify("Velorex") == "velorex"
    assert slugify("My Product!") == "my_product"
    assert slugify("") == "product"

    env = "APP_NAME=FastForge\nSTRIPE_SECRET_KEY=sk_live_x\nDATABASE_URL=.../fastforge_platform\n"
    out = apply_env(env, "Velorex", "velorex", ["billing"])
    assert "APP_NAME=Velorex" in out
    assert "STRIPE_SECRET_KEY=\n" in out  # blanked
    assert "velorex_platform" in out and "fastforge_platform" not in out

    router = (
        "from app.billing.router import router as billing_router\n"
        "api_router.include_router(billing_router)\n"
        "api_router.include_router(auth_router)\n"
    )
    out = comment_out(router, MODULES["billing"]["router_lines"])
    assert sum(ln.lstrip().startswith("#") for ln in out.splitlines()) == 2  # both billing lines
    assert "include_router(auth_router)" in out
    assert "# api_router.include_router(auth_router)" not in out
    # idempotent: re-running doesn't double-comment
    assert comment_out(out, MODULES["billing"]["router_lines"]) == out

    assert apply_root_pkg('"name": "fastforge"', "Velorex", "velorex") == '"name": "velorex"'
    web_pkg = '"@fastforge/web" for FastForge'
    assert apply_web_pkg(web_pkg, "Velorex") == '"@fastforge/web" for Velorex'
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        main()
