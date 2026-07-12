#!/usr/bin/env bash
# TODO: Bootstrap script for new product clones.
# Should be idempotent — safe to run multiple times.

set -euo pipefail

echo "FastForge — Bootstrap"
echo "=============================="

echo "→ Installing Python dependencies..."
uv sync --all-packages

echo "→ Installing Node dependencies..."
pnpm install

echo "→ Starting Docker services..."
docker compose up -d postgres redis mailpit

echo "→ Running database migrations..."
cd packages/database && uv run alembic upgrade head && cd ../..

echo ""
echo "Bootstrap complete."
echo "Copy .env.example to .env and configure your environment."
