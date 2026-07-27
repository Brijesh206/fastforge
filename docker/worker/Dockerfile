# syntax=docker/dockerfile:1
#
# FastForge worker image. Build context = monorepo root:
#   docker build -f docker/worker/Dockerfile -t fastforge-worker .
#
# Same two-stage shape as the API image: the builder resolves the uv workspace
# into a venv, the runtime stage ships that venv plus the source it references.
# The image carries both taskiq and celery, so JOBS_PROVIDER can be switched
# with a restart rather than a rebuild.

# ---------- builder ----------
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages ./packages
COPY apps/worker ./apps/worker

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package fastforge-worker

# ---------- runtime ----------
FROM python:3.13-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
COPY --from=builder /app/apps/worker /app/apps/worker

RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin app \
    && chown -R app:app /app
USER app

# worker_app lives here, and main.py execs the right CLI for JOBS_PROVIDER.
WORKDIR /app/apps/worker

# No healthcheck: a queue consumer exposes no port, and "process alive" is
# already what Docker restarts on. Monitor queue depth instead.
CMD ["python", "-m", "worker_app.main"]
