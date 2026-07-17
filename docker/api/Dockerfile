# syntax=docker/dockerfile:1
#
# FastForge API image. Build context = monorepo root:
#   docker build -f docker/api/Dockerfile -t fastforge-api .
#
# Multi-stage: the builder resolves the uv workspace into a venv; the runtime
# stage ships only that venv + the Python source it references (editable
# workspace installs point back at packages/ and apps/api/).

# ---------- builder ----------
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# Only what the API package needs to resolve — keeps the build cache tight.
COPY pyproject.toml uv.lock ./
COPY packages ./packages
COPY apps/api ./apps/api

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package fastforge-api

# ---------- runtime ----------
FROM python:3.13-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WEB_CONCURRENCY=2
WORKDIR /app

# The venv holds editable installs that reference these source paths, so they
# must live at the same location as in the builder.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
COPY --from=builder /app/apps/api /app/apps/api
COPY docker/api/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh \
    && useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin app \
    && chown -R app:app /app
USER app

EXPOSE 8000
# Migrations run, then uvicorn — see entrypoint.sh.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
