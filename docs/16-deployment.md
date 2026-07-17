# Deployment Guide

> Standard deployment architecture for every product built on FastForge.

---

# Quick Deploy (the concrete path)

FastForge ships as a **portable Docker image** — it runs anywhere a container
runs (a plain VPS, Railway, Fly, Render, AWS ECS). There is no vendor lock-in;
the platform recipes below are just examples of running the same image.

Reference topology (cheap and enough for launch):

```text
Web (Next.js)  →  Vercel        (free; builds there, off your server)
API (FastAPI)  →  1 small VPS   (Docker Compose + Caddy for auto-HTTPS)
Database       →  Supabase      (managed Postgres, external)
```

A 1 vCPU / 1 GB VPS is enough, because the web app builds on Vercel and the
database is Supabase — only the API + Caddy run on the box (~300–400 MB).

## API on a VPS (Docker Compose)

Prereqs: Docker + Compose on the VPS, a domain, and a DNS **A-record** for
`api.yourdomain.com` → the VPS IP.

```bash
# 1. Get the code onto the box
git clone <your-repo> fastforge && cd fastforge

# 2. Configure secrets
cp .env.production.example .env
#    edit .env — set API_DOMAIN, APP_SECRET_KEY, JWT_SECRET_KEY,
#    DATABASE_URL (Supabase pooler), Stripe keys, mail creds, FRONTEND_BASE_URL
#    generate secrets with:  openssl rand -hex 32

# 3. (1 GB box) add swap headroom so builds don't OOM
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile \
  && sudo mkswap /swapfile && sudo swapon /swapfile

# 4. Build + run. The API container runs `alembic upgrade head` on start,
#    then uvicorn. Caddy fetches a Let's Encrypt cert for API_DOMAIN.
docker compose -f docker-compose.prod.yml up -d --build

# 5. Verify
curl https://api.yourdomain.com/api/v1/health   # -> {"status":"ok"}
```

Migrations run automatically on every deploy (the container's entrypoint runs
`alembic upgrade head` before serving — see `docker/api/entrypoint.sh`). To
ship an update: `git pull && docker compose -f docker-compose.prod.yml up -d --build`.

## Web on Vercel

Import the repo in Vercel, set **Root Directory** to `apps/web`, and add env
vars (at minimum `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`). Point
`app.yourdomain.com` at the Vercel project. Set the API's `FRONTEND_BASE_URL`
to that URL so email links and CORS match.

## Stripe webhook

In the Stripe dashboard add an endpoint at
`https://api.yourdomain.com/api/v1/billing/webhook`, then put its signing
secret in the API's `.env` as `STRIPE_WEBHOOK_SECRET` and redeploy.

## Health / uptime

`GET /api/v1/health` is the liveness check. Wire it to an uptime monitor
(UptimeRobot free tier, or the platform's built-in check). Compose also has a
container `healthcheck` hitting the same path.

## Other hosts (same image, no lock-in)

The `docker/api/Dockerfile` is the unit of portability. On Railway/Render/Fly,
point the platform at that Dockerfile and set the same env vars; use the
platform's release command / pre-deploy hook to run
`cd packages/database && alembic upgrade head` (or keep it in the entrypoint).
On AWS, push the image to ECR and run it on ECS/Fargate.

---

# Purpose

Every SaaS product should share the same deployment process.

Deployment should be:

- Repeatable
- Automated
- Reliable
- Vendor independent
- Easy to migrate

The goal is to deploy a new product in minutes, not hours.

---

# Deployment Philosophy

For an indie developer shipping multiple products quickly:

1. Keep infrastructure simple.
2. Prefer managed services.
3. Minimize operational overhead.
4. Avoid Kubernetes initially.
5. Automate everything possible.

Infrastructure should never become the bottleneck for shipping.

---

# Initial Hosting Strategy

## Frontend

Recommended:

- Vercel

Alternatives:

- Cloudflare Pages
- Netlify

---

## Backend

Recommended:

- Railway
- Render
- Fly.io

Future:

- Hetzner VPS
- DigitalOcean
- AWS ECS

---

## Database

Recommended:

- Supabase PostgreSQL

Future:

- Neon
- AWS RDS
- Self-hosted PostgreSQL

---

## Cache

Recommended:

- Upstash Redis

Future:

- Railway Redis
- Redis Cloud
- Self-hosted Redis

---

## Object Storage

Recommended:

- Supabase Storage

Future:

- Cloudflare R2
- AWS S3

---

## Email

Development:

- SMTP
- Mailpit

Production:

- Resend
- Postmark

---

## Payments

Initial:

- Stripe

Future:

- Paddle
- Lemon Squeezy
- Polar

---

# Architecture

```text
Internet

↓

Vercel

↓

FastAPI

↓

Supabase

↓

Redis

↓

Celery Workers

↓

Storage

↓

SMTP

↓

Stripe
```

Each component should remain independently deployable.

---

# Docker

Every service must include:

- Dockerfile
- .dockerignore

Every repository should include:

```text
docker-compose.yml
```

for local development.

---

# Multi-Stage Builds

Use multi-stage Docker builds.

Benefits:

- Smaller images
- Faster deployments
- Better security

Avoid shipping build dependencies in production images.

---

# Environment Variables

Never hardcode configuration.

All secrets should come from environment variables.

Examples:

```text
DATABASE_URL

REDIS_URL

SUPABASE_URL

SUPABASE_KEY

JWT_SECRET

STRIPE_SECRET_KEY

SMTP_HOST
```

---

# Secrets

Secrets belong in:

- Railway Secrets
- Render Environment Variables
- Vercel Environment Variables
- GitHub Secrets

Never commit secrets to Git.

---

# Environments

Support:

```text
Development

Staging

Production
```

Each environment should have:

- Separate database
- Separate Redis
- Separate Stripe project
- Separate storage bucket

Never reuse production credentials.

---

# Branch Strategy

Recommended:

```text
main

develop

feature/*
```

Small solo projects may deploy directly from `main`.

---

# Deployment Flow

```text
Git Push

↓

GitHub Actions

↓

Run Tests

↓

Build Docker Image

↓

Deploy

↓

Health Check

↓

Success
```

Deployment should stop immediately if tests fail.

---

# Database Migrations

Deployment order:

```text
Deploy

↓

Run Migrations

↓

Start Application
```

Migrations should be automated.

Never modify production databases manually.

---

# Rollbacks

Every deployment should support rollback.

Rollback should include:

- Previous application version
- Previous container image

Database rollbacks should be planned separately.

---

# Health Checks

Every deployment should verify:

- API health
- Database connection
- Redis connection
- Critical dependencies

Traffic should only be routed after readiness checks pass.

---

# Static Assets

Frontend assets should be:

- Minified
- Compressed
- Cached

Use CDN delivery whenever possible.

---

# HTTPS

Production deployments must use HTTPS.

Certificates should be managed automatically.

Examples:

- Vercel
- Cloudflare
- Railway

---

# Custom Domains

Support:

```text
api.example.com

app.example.com
```

Avoid exposing provider-generated domains to end users.

---

# DNS

Recommended provider:

- Cloudflare

Benefits:

- DNS
- CDN
- SSL
- DDoS protection

Centralize DNS management where possible.

---

# CDN

Use CDN for:

- Frontend assets
- Images
- Static downloads

Dynamic API traffic should generally bypass CDN caching.

---

# Background Workers

Deploy workers independently.

Example:

```text
API

↓

Celery Worker

↓

Celery Beat
```

Workers should scale separately from API instances.

---

# Scheduled Jobs

Use Celery Beat for:

- Cleanup jobs
- Billing reconciliation
- Email digests
- Usage resets

Avoid relying on provider-specific cron implementations.

---

# Startup Order

Recommended:

```text
Database

↓

Redis

↓

API

↓

Workers
```

Applications should retry dependency connections during startup where appropriate.

---

# GitHub Actions

Every repository should include a standard CI/CD workflow.

Pipeline:

```text
Push

↓

Lint

↓

Format Check

↓

Unit Tests

↓

Integration Tests

↓

Build Docker Image

↓

Deploy

↓

Health Check
```

Deployments should occur only after all checks pass.

---

# Deployment Strategy

Preferred strategy:

```text
Rolling Deployment
```

Benefits:

- Minimal downtime
- Safer releases
- Easier rollback

Blue/Green deployments can be introduced later for larger products.

---

# Zero-Downtime Deployments

Deployments should avoid service interruption whenever possible.

Requirements:

- Graceful shutdown
- Readiness checks
- Connection draining
- Backward-compatible database migrations

---

# Database Backups

Every production database must have automatic backups.

Recommended:

- Daily backups
- Point-in-time recovery (if available)
- Regular restore verification

A backup that cannot be restored is not a backup.

---

# Storage Backups

Critical storage should be backed up.

Options:

- Cross-region replication
- Scheduled snapshots
- Secondary storage provider

Backup frequency should match business requirements.

---

# Disaster Recovery

Document recovery procedures.

Minimum requirements:

- Database restore
- Storage restore
- DNS recovery
- Environment variable restoration
- Third-party credential recovery

Recovery procedures should be tested periodically.

---

# Monitoring After Deployment

Immediately verify:

- Application health
- Error rate
- Response time
- Queue health
- Database connections
- Worker status

Do not assume a successful deployment means a healthy application.

---

# Smoke Tests

Run automated smoke tests after deployment.

Examples:

- Health endpoint
- User login
- Database query
- Cache access
- Background job execution

Smoke tests provide confidence before declaring a deployment successful.

---

# Rollback Strategy

Rollback should be fast.

Process:

```text
Detect Failure

↓

Stop Traffic

↓

Deploy Previous Version

↓

Verify Health

↓

Investigate
```

Keep previous container images readily available.

---

# Configuration Management

Configuration should be:

- Environment-specific
- Version controlled (excluding secrets)
- Documented
- Validated at startup

Missing required configuration should prevent startup.

---

# Cost Optimization

For early-stage products:

Frontend:

- Vercel Free

Backend:

- Railway Free (when available)
- Render Free (where appropriate)
- Fly.io (small workloads)

Database:

- Supabase Free

Cache:

- Upstash Free

Storage:

- Supabase Storage

Optimize for rapid validation rather than maximum scalability.

---

# Scaling Strategy

Scale gradually.

Recommended order:

1. Optimize code.
2. Add caching.
3. Increase instance size.
4. Add workers.
5. Scale horizontally.

Avoid premature infrastructure complexity.

---

# Resource Limits

Configure limits for:

- CPU
- Memory
- Request timeout
- Worker concurrency
- Queue size

Explicit limits improve stability and cost control.

---

# Security

Production deployments should enforce:

- HTTPS
- Secure headers
- Secret management
- Dependency scanning
- Image vulnerability scanning
- Least-privilege credentials

Security should be part of every deployment.

---

# Dependency Management

Pin dependency versions.

Regularly update:

- Python packages
- Node packages
- Docker base images

Automated dependency updates may be introduced later.

---

# Local Development

Developers should start the platform with:

```bash
docker compose up
```

The local environment should closely resemble production while remaining lightweight.

---

# Testing Strategy

Deployment pipelines should execute:

## Static Analysis

- Ruff
- MyPy
- ESLint
- TypeScript

---

## Unit Tests

Validate business logic.

---

## Integration Tests

Validate:

- Database
- Redis
- Storage
- Authentication

---

## End-to-End Tests

Critical flows:

- Registration
- Login
- Billing
- File upload
- Background jobs

Deployments should not proceed if critical flows fail.

---

# Documentation

Deployment documentation should include:

- Environment setup
- Secrets
- Deployment steps
- Rollback procedure
- Recovery procedure
- Monitoring checklist

Documentation should be updated whenever deployment architecture changes.

---

# Deployment Checklist

Before every production deployment:

- [ ] Tests passing
- [ ] Linting passing
- [ ] Docker image built
- [ ] Database migrations reviewed
- [ ] Secrets configured
- [ ] Monitoring enabled
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Rollback plan available
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Manual production deployments
- Hardcoded secrets
- Deploying without tests
- Editing production databases manually
- Skipping health checks
- Sharing environments
- Ignoring failed deployments
- Running background jobs inside API processes

---

# Deployment Definition of Done

A deployment process is complete only when:

- Infrastructure is reproducible.
- Deployments are automated.
- Health checks pass.
- Rollback is possible.
- Backups are configured.
- Monitoring is active.
- Tests pass.
- Documentation is updated.

---

# Summary

The Deployment package defines a repeatable, production-ready deployment workflow for every SaaS built on FastForge.

By standardizing infrastructure, CI/CD, secrets management, health checks, backups, and rollback procedures, new products can move from local development to production with minimal effort.

This approach prioritizes:

- Fast shipping
- Low operational overhead
- Vendor flexibility
- Incremental scaling
- Long-term maintainability

The result is a deployment process that supports launching multiple products each month while remaining reliable enough for production workloads.