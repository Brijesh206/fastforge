# Observability Guide

> Reusable observability architecture for every product built on FastForge.

---

# Purpose

Logging alone is not sufficient for operating production systems.

Observability combines:

- Metrics
- Logs
- Traces
- Health Checks
- Alerting

Together, these provide visibility into system behavior and enable rapid detection and resolution of issues.

Every product should inherit the same observability infrastructure.

---

# Design Principles

The observability system should be:

- Vendor independent
- Low overhead
- Consistent
- Actionable
- Production ready

Applications should emit telemetry through platform abstractions rather than directly integrating monitoring vendors.

---

# Components

The platform consists of five observability pillars:

```text
Metrics

Logs

Traces

Health Checks

Alerts
```

These components should work together using shared context.

---

# Architecture

```text
Application

↓

ObservabilityService

↓

Metrics

Logs

Traces

↓

Backend

↓

Dashboard
```

Applications should communicate only with the Observability package.

---

# Metrics

Metrics provide numerical measurements over time.

Examples:

- Request count
- Response time
- Error rate
- Queue length
- Database latency
- Cache hit rate

Metrics should be inexpensive to collect.

---

# Metric Types

Support:

```text
Counter

Gauge

Histogram

Summary
```

Use the appropriate metric type for each measurement.

---

# Counters

Counters only increase.

Examples:

- HTTP requests
- Jobs processed
- Emails sent
- Notifications delivered

Never decrement a counter.

---

# Gauges

Gauges move up and down.

Examples:

- Active users
- Queue size
- Redis connections
- Memory usage

Use gauges for current state.

---

# Histograms

Histograms measure distributions.

Examples:

- Request duration
- Query duration
- Job execution time
- API latency

Histograms enable percentile analysis.

---

# Naming Convention

Metrics should follow a consistent format.

Recommended:

```text
application_http_requests_total

application_http_request_duration_ms

application_jobs_processed_total

application_cache_hits_total
```

Names should be descriptive and stable.

---

# Labels

Use labels sparingly.

Example:

```text
method=GET

status=200

endpoint=/projects
```

Avoid high-cardinality labels.

Never use:

- User IDs
- Email addresses
- UUIDs

High-cardinality labels can overwhelm monitoring systems.

---

# HTTP Metrics

Collect:

- Request count
- Request duration
- Status code distribution
- Active requests

These metrics form the baseline for API monitoring.

---

# Database Metrics

Track:

- Query duration
- Connection pool usage
- Failed queries
- Slow queries
- Transaction duration

Database performance directly affects user experience.

---

# Cache Metrics

Track:

- Hit rate
- Miss rate
- Latency
- Memory usage
- Evictions

Cache metrics should complement logging.

---

# Queue Metrics

Track:

- Jobs queued
- Jobs running
- Jobs failed
- Retry count
- Processing duration

These metrics are essential for worker health.

---

# Storage Metrics

Examples:

- Upload count
- Download count
- Storage usage
- Upload duration

Useful for capacity planning.

---

# Billing Metrics

Examples:

- Active subscriptions
- Trial conversions
- Failed payments
- Monthly recurring revenue (MRR)

Business metrics should remain separate from infrastructure metrics.

---

# Tracing

Distributed tracing follows requests across services.

Example:

```text
HTTP Request

↓

Database

↓

Redis

↓

Email

↓

Background Worker
```

Tracing simplifies debugging complex workflows.

---

# Trace Context

Each trace should include:

```text
trace_id

span_id

parent_span_id
```

These identifiers should propagate across services and workers.

---

# Instrumentation

Instrument:

- HTTP requests
- Database queries
- Redis operations
- External APIs
- Background jobs
- Storage operations

Instrumentation should be automatic where possible.

---

# Health Checks

Every service should expose health endpoints.

Recommended:

```text
/health

/ready

/live
```

Each endpoint has a distinct purpose.

---

# Liveness Probe

Purpose:

Determine whether the application process is alive.

Should verify only that the application can respond.

Avoid expensive dependency checks.

---

# Readiness Probe

Purpose:

Determine whether the application is ready to receive traffic.

Verify:

- Database connection
- Redis connection
- Critical configuration
- Queue availability (if required)

---

# Startup Probe

Optional.

Useful for applications with slow startup times.

Allows orchestration platforms to wait before sending traffic.

---

# Dependency Health

Track external dependencies.

Examples:

- PostgreSQL
- Redis
- Supabase
- SMTP
- Stripe

Dependency failures should be visible immediately.

---

# Service Level Indicators (SLIs)

Recommended SLIs:

- Availability
- Latency
- Error Rate
- Throughput

These measurements describe service quality.

---

# Service Level Objectives (SLOs)

Example objectives:

Availability:

```text
99.9%
```

API latency:

```text
95% of requests under 300ms
```

Error rate:

```text
<1%
```

SLOs provide measurable operational goals.

---

# Dashboards

Every product should expose reusable dashboards.

Recommended dashboards:

- API
- Workers
- Database
- Cache
- Billing
- Storage
- Authentication

Dashboards should answer operational questions quickly.

---

# Alerting

Monitoring without alerts is incomplete.

Alerts should notify engineers only when action is required.

Examples:

- API unavailable
- Error rate spike
- Database connection failures
- Queue backlog
- Worker failures
- Payment webhook failures
- Storage provider failures

Avoid noisy alerts.

---

# Alert Severity

Recommended levels:

```text
Info

Warning

Critical
```

Only critical alerts should wake operators outside business hours.

---

# Incident Response

Every production incident should include:

- Detection time
- Root cause
- Impact
- Resolution
- Follow-up actions

Major incidents should result in a postmortem document.

---

# OpenTelemetry

The platform should be compatible with OpenTelemetry.

OpenTelemetry should collect:

- Metrics
- Logs
- Traces

Instrumentation should be added through middleware and shared libraries whenever possible.

---

# Prometheus

Prometheus should be the default metrics backend.

Expose metrics at:

```text
/metrics
```

Metrics should be scrape-friendly and follow Prometheus naming conventions.

---

# Grafana

Grafana should visualize:

- API metrics
- Database metrics
- Redis metrics
- Queue metrics
- Storage metrics
- Worker metrics
- Business metrics

Dashboards should be reusable across products.

---

# Error Reporting

Unhandled exceptions should be captured automatically.

Preferred integrations:

- Sentry
- Rollbar
- Bugsnag

Exception reporting should include:

- Stack trace
- Request ID
- Correlation ID
- Environment
- Application version

Never include secrets.

---

# Performance Monitoring

Measure:

- Slow endpoints
- Slow database queries
- External API latency
- Worker execution time
- Cache latency

Performance regressions should be visible before users notice them.

---

# Capacity Planning

Monitor long-term trends.

Examples:

- CPU usage
- Memory usage
- Disk usage
- Database growth
- Storage growth
- Queue throughput

Capacity metrics help prevent outages.

---

# Availability Monitoring

Track:

- Uptime
- Downtime
- Failed deployments
- Dependency outages

Availability should be monitored continuously.

---

# Synthetic Monitoring

Future enhancement:

Automated probes should periodically test:

- Login
- Registration
- Billing
- API endpoints
- Health endpoints

Synthetic monitoring detects failures before users report them.

---

# Business Monitoring

Track key business events.

Examples:

- New users
- Active organizations
- Subscription conversions
- Churn
- Daily active users
- API usage

Business metrics belong in analytics dashboards, not infrastructure dashboards.

---

# Environment Separation

Each environment should report independently.

Examples:

```text
Development

Staging

Production
```

Never mix telemetry across environments.

---

# Configuration

Observability configuration should include:

```text
Metrics Enabled

Tracing Enabled

Sampling Rate

Metrics Endpoint

Error Reporting DSN

Log Level

Environment
```

Use Pydantic Settings.

---

# Local Development

Developers should be able to:

- View metrics locally
- View traces locally (optional)
- Access health endpoints
- Test alerts safely

Local observability should require minimal setup.

---

# Security

Protect telemetry endpoints.

Examples:

- Restrict `/metrics` access
- Avoid exposing internal topology
- Remove secrets from traces
- Mask sensitive metadata

Observability data should be treated as production data.

---

# Testing Strategy

## Unit Tests

Test:

- Metric creation
- Health checks
- Trace propagation

---

## Integration Tests

Test:

- Metrics endpoint
- Health endpoints
- Error reporting
- Trace generation

---

## End-to-End Tests

Verify:

- Requests generate metrics
- Requests generate traces
- Errors are logged
- Health endpoints respond correctly

Observability should be validated as part of release testing.

---

# Documentation

Document:

- Available metrics
- Health endpoints
- Alert rules
- Dashboard links
- SLO definitions

Documentation should evolve alongside the platform.

---

# Observability Checklist

Before shipping observability:

- [ ] Metrics exposed
- [ ] Health endpoints implemented
- [ ] Tracing configured
- [ ] Error reporting integrated
- [ ] Dashboards created
- [ ] Alerts configured
- [ ] Sensitive data masked
- [ ] Tests passing
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Logging without metrics
- Metrics without alerts
- High-cardinality labels
- Exposing sensitive telemetry
- Ignoring failed health checks
- Alerting on every warning
- Mixing environments
- Manual instrumentation everywhere

Prefer reusable middleware and shared platform components.

---

# Observability Definition of Done

An observability feature is complete only when:

- Metrics are exposed.
- Health checks are implemented.
- Traces propagate correctly.
- Error reporting is configured.
- Dashboards are available.
- Alerts are actionable.
- Tests pass.
- Documentation is updated.

---

# Summary

The Observability package provides a unified platform for understanding, monitoring, and operating every SaaS product built on FastForge.

By combining:

- Metrics
- Logs
- Traces
- Health checks
- Alerting

the platform enables rapid diagnosis of issues, proactive monitoring, and data-driven operational improvements.

Applications should emit telemetry through shared platform abstractions, allowing monitoring providers and tooling to evolve without requiring changes to business logic.

A strong observability foundation is essential for confidently shipping multiple products quickly while maintaining reliability at scale.