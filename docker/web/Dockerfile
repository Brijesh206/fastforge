# syntax=docker/dockerfile:1
#
# FastForge web image (Next.js). Build context = monorepo root:
#   docker build -f docker/web/Dockerfile -t fastforge-web .
#
# NEXT_PUBLIC_* values are inlined into the client bundle at BUILD time, not
# read at runtime — so the API URL is a build arg. Changing it means a rebuild,
# which is why docker-compose.prod.yml passes it under build.args, not env_file.

FROM node:20-alpine AS base
ENV PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH \
    NEXT_TELEMETRY_DISABLED=1
RUN corepack enable

# ---------- deps ----------
# Only the manifests, so the install layer caches until a package.json changes.
# --frozen-lockfile validates every workspace member, so each manifest the
# lockfile knows about has to be present even if the web app doesn't use it.
FROM base AS deps
WORKDIR /repo
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/
COPY packages/ui/package.json ./packages/ui/
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --filter @fastforge/web...

# ---------- builder ----------
FROM base AS builder
WORKDIR /repo

# Defaults match apps/web/src/lib/config.ts — note the /api/v1 suffix.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ARG NEXT_PUBLIC_APP_NAME=FastForge
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_APP_NAME=$NEXT_PUBLIC_APP_NAME

COPY --from=deps /repo/node_modules ./node_modules
COPY --from=deps /repo/apps/web/node_modules ./apps/web/node_modules
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/ui ./packages/ui
COPY apps/web ./apps/web

RUN pnpm --filter @fastforge/web build

# ---------- runtime ----------
FROM base AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# standalone carries its own pruned node_modules; static/ and public/ are not
# traced into it and have to be copied alongside.
COPY --from=builder /repo/apps/web/.next/standalone ./
COPY --from=builder /repo/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /repo/apps/web/public ./apps/web/public

RUN addgroup -g 1001 -S nodejs \
    && adduser -u 1001 -G nodejs -S -H nextjs \
    && chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000
CMD ["node", "apps/web/server.js"]
