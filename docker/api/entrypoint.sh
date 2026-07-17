#!/bin/sh
# Release step: apply migrations, then start the API. If migrations fail the
# container exits (set -e) instead of serving against a stale schema.
set -e

echo "[entrypoint] Applying database migrations..."
cd /app/packages/database
alembic upgrade head

echo "[entrypoint] Starting API (workers=${WEB_CONCURRENCY:-2})..."
cd /app/apps/api
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${WEB_CONCURRENCY:-2}"
