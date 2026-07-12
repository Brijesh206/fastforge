# Logging Guide

> Reusable structured logging architecture for every product built on FastForge.

---

# Purpose

Logging is one of the most important infrastructure services.

Good logs make debugging, monitoring, auditing, and incident response significantly easier.

Every product should use the same logging infrastructure and conventions.

Applications should never call the Python logging library directly.

Instead, all logging should go through `LoggingService`.

---

# Design Principles

The logging system should be:

- Structured
- Consistent
- Machine-readable
- Human-readable
- Searchable
- Low overhead

Logs are written for both humans and automated systems.

---

# Responsibilities

The Logging package owns:

- Structured logging
- Request logging
- Error logging
- Audit logging
- Correlation IDs
- Request IDs
- Log formatting
- Log filtering
- Log export

Applications should only emit log events.

---

# Architecture

```text
Application

↓

LoggingService

↓

Logger

↓

Formatter

↓

Output

↓

Console / File / External Service
```

Logging destinations should be configurable.

---

# Log Format

Use structured JSON logs in production.

Example:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "api",
  "request_id": "...",
  "message": "User logged in"
}
```

Use human-readable logs for local development.

---

# Log Levels

Supported levels:

```text
DEBUG

INFO

WARNING

ERROR

CRITICAL
```

Every log should use the appropriate level.

---

# DEBUG

Use for:

- Development
- Internal state
- Variable inspection
- Troubleshooting

DEBUG logging should be disabled in production by default.

---

# INFO

Use for:

- Successful operations
- Startup
- Shutdown
- User actions
- Background job completion

INFO logs describe normal application behavior.

---

# WARNING

Use for:

- Recoverable issues
- Unexpected input
- Retry events
- Slow operations

Warnings indicate something worth investigating but not an immediate failure.

---

# ERROR

Use for:

- Failed requests
- Exceptions
- Provider failures
- Database errors
- Queue failures

Errors should include sufficient context for debugging.

---

# CRITICAL

Use only for severe failures.

Examples:

- Database unavailable
- Application startup failure
- Configuration corruption
- Data integrity failures

Critical logs should trigger alerts.

---

# Structured Fields

Every log should include common fields.

Recommended:

```text
timestamp

level

service

environment

request_id

correlation_id

user_id

organization_id

message
```

Optional fields:

```text
metadata

duration_ms

exception
```

---

# Request ID

Every incoming HTTP request should receive a unique request ID.

Workflow:

```text
Client

↓

API

↓

Generate Request ID

↓

Attach to Context

↓

Include in All Logs
```

This simplifies request tracing.

---

# Correlation ID

A correlation ID links multiple services and background jobs.

Example:

```text
HTTP Request

↓

Queue Job

↓

Email

↓

Webhook

↓

Background Worker
```

Every component should share the same correlation ID where possible.

---

# Contextual Logging

Avoid:

```python
logger.info("User created")
```

Prefer:

```python
logger.info(
    "User created",
    user_id=user.id,
    organization_id=org.id
)
```

Context makes logs significantly more useful.

---

# Exception Logging

Always log exceptions with stack traces.

Example fields:

```text
Exception Type

Message

Stack Trace

Request ID

Correlation ID
```

Avoid swallowing exceptions silently.

---

# HTTP Request Logging

Log every request.

Fields:

```text
Method

Path

Status Code

Duration

Request ID

Client IP

User Agent
```

Sensitive data should be excluded.

---

# HTTP Response Logging

Capture:

- Status code
- Response time
- Response size (optional)

Avoid logging entire response bodies.

---

# Sensitive Data

Never log:

- Passwords
- Tokens
- API Keys
- Credit card data
- Session cookies
- Private keys
- OAuth secrets

Sensitive values should always be masked or omitted.

---

# PII Handling

Personally identifiable information should be logged only when necessary.

Examples:

Allowed:

- User ID
- Organization ID

Avoid:

- Passwords
- Full payment details
- Authentication tokens

Email addresses should be logged only when required for debugging and in compliance with privacy requirements.

---

# Audit Logs

Audit logs differ from application logs.

Audit logs record important business events.

Examples:

- User login
- Password change
- Subscription upgrade
- API key creation
- Organization invitation
- Permission changes

Audit logs should be immutable.

---

# Audit Log Model

Recommended fields:

```text
id

event

actor_id

organization_id

resource_type

resource_id

metadata

created_at
```

Audit logs should be stored in PostgreSQL.

---

# Background Job Logging

Every worker should log:

- Job started
- Job completed
- Job failed
- Retry attempt
- Execution duration

Background jobs should preserve correlation IDs when possible.

---

# Startup Logging

On application startup, log:

- Environment
- Version
- Configuration summary
- Enabled modules

Do not log secrets or credentials.

---

# Shutdown Logging

Log graceful shutdown events.

Examples:

- Workers stopping
- HTTP server stopping
- Database disconnecting

Graceful shutdown logs simplify operational debugging.

---

# Log Rotation

Local log files should support automatic rotation.

Recommended policies:

```text
Rotate Daily
```

or

```text
100 MB per file
```

Retention should be configurable.

Production deployments should generally stream logs to a centralized logging platform instead of relying on local files.

---

# Centralized Logging

Production logs should be aggregated into a centralized system.

Examples:

- Loki
- Elasticsearch
- Better Stack
- Datadog
- Grafana Cloud
- OpenSearch

The Logging package should expose configurable log handlers rather than depending on a specific vendor.

---

# OpenTelemetry Readiness

The logging system should be compatible with OpenTelemetry.

Correlation between:

- Logs
- Metrics
- Traces

should be possible without changing application code.

OpenTelemetry support should be optional but easy to enable.

---

# Trace Context

Whenever tracing is enabled, include:

```text
trace_id

span_id
```

These values allow developers to navigate between traces and logs during incident investigations.

---

# Performance Logging

Measure slow operations.

Examples:

- Database queries
- External API calls
- Storage uploads
- Redis operations
- Background jobs

Example:

```text
Database Query

Duration: 850ms

Level: WARNING
```

Thresholds should be configurable.

---

# Database Logging

Log:

- Query duration
- Connection failures
- Retry attempts
- Migration execution

Avoid logging raw SQL with sensitive parameters in production.

---

# External Service Logging

For outbound requests, capture:

- Provider
- Endpoint
- HTTP method
- Status code
- Duration
- Retry count

Never log:

- Authorization headers
- API secrets
- Access tokens

---

# Worker Logging

Background workers should include:

```text
job_id

queue

attempt

duration_ms

status
```

This simplifies debugging failed jobs.

---

# Configuration

Logging configuration should include:

```text
Log Level

Output Format

Output Destination

Enable JSON

Enable Console

Enable File

Sampling Rate (future)
```

Configuration should be managed through Pydantic Settings.

---

# Environment Behavior

Development:

- Human-readable logs
- DEBUG enabled
- Colored output (optional)

Production:

- Structured JSON
- INFO level or higher
- Centralized aggregation

Behavior should be determined by environment configuration.

---

# Monitoring Integration

Logs should integrate with the monitoring platform.

Examples:

- Error alerts
- Slow request alerts
- Worker failure alerts
- Authentication failure spikes

Logs should support automated alerting.

---

# Error Reporting

Unhandled exceptions should be reported automatically.

Future integrations:

- Sentry
- Bugsnag
- Rollbar

The application should continue using `LoggingService`; provider integration belongs to infrastructure.

---

# Retention Policy

Application logs:

```text
30 Days
```

Audit logs:

```text
1 Year (or business requirement)
```

Retention should comply with organizational and legal requirements.

---

# Sampling

High-volume events may use sampling.

Examples:

- Health checks
- Metrics endpoints
- Static asset requests

Critical events should never be sampled.

---

# Local Development

Developers should be able to:

- View readable console logs
- Search logs easily
- Filter by level
- Filter by request ID

Logging should aid development without excessive noise.

---

# Testing Strategy

## Unit Tests

Test:

- LoggingService
- Structured field generation
- Context propagation
- Log formatting

Mock external logging providers.

---

## Integration Tests

Test:

- Request ID propagation
- Correlation ID propagation
- Audit log persistence
- Worker logging

---

## End-to-End Tests

Verify:

- Request logging
- Error logging
- Audit events
- Background job logs

Ensure log output contains expected metadata.

---

# Documentation

Document:

- Log levels
- Structured fields
- Correlation strategy
- Audit events
- Retention policy

Documentation should remain synchronized with implementation.

---

# Logging Checklist

Before shipping logging functionality:

- [ ] Structured logging enabled
- [ ] Request IDs implemented
- [ ] Correlation IDs propagated
- [ ] Audit logging configured
- [ ] Sensitive fields masked
- [ ] Monitoring integration verified
- [ ] Retention policy defined
- [ ] Tests passing
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Using print statements in production
- Logging passwords or secrets
- Logging entire request/response bodies
- Swallowing exceptions without logging
- Mixing structured and unstructured formats
- Hardcoding provider-specific logging logic
- Logging excessive DEBUG information in production
- Creating inconsistent log messages

---

# Logging Definition of Done

A logging feature is complete only when:

- Structured logging is used.
- Context is included.
- Sensitive data is protected.
- Audit events are recorded where appropriate.
- Monitoring integration is supported.
- Tests pass.
- Documentation is updated.

---

# Summary

The Logging package provides a unified, structured logging system for every product built on FastForge.

Applications interact only with `LoggingService`, ensuring consistent log formatting, contextual metadata, and provider-independent integrations.

This architecture enables:

- Faster debugging
- Reliable auditing
- Production monitoring
- Distributed tracing readiness
- Centralized log aggregation
- Long-term maintainability

A consistent logging strategy is essential for operating multiple SaaS products efficiently and should be considered part of the platform's core infrastructure rather than an application-specific concern.