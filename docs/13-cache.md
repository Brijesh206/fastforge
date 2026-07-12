# Cache Guide

> Reusable caching architecture for every product built on FastForge.

---

# Purpose

Caching improves application performance, reduces database load, and enables several infrastructure features.

The Cache package should provide a single, provider-independent interface that every application uses.

Applications should never communicate directly with Redis or another cache provider.

Instead, they should communicate with `CacheService`.

---

# Design Principles

The cache system should be:

- Provider independent
- Fast
- Predictable
- Observable
- Easy to replace
- Safe to invalidate

Caching should improve performance without changing application behavior.

---

# Responsibilities

The Cache package owns:

- Cache operations
- TTL management
- Cache invalidation
- Distributed locks
- Rate limiting storage
- Session storage
- Temporary data
- Feature caching

Applications should never import Redis clients directly.

---

# Architecture

```text
Application

↓

CacheService

↓

CacheProvider

↓

Provider Adapter

↓

Redis
```

Future providers:

- Redis
- KeyDB
- DragonflyDB
- Valkey
- In-Memory Cache (development)

Changing providers should require configuration changes only.

---

# Supported Providers

Initial:

- Redis

Future:

- DragonflyDB
- KeyDB
- Valkey
- Memory Cache

Applications should not depend on provider-specific features.

---

# Cache Provider Interface

Every provider implements:

```python
get()

set()

delete()

exists()

expire()

increment()

decrement()

clear()

lock()

unlock()
```

Applications communicate only with this interface.

---

# Cache Categories

The platform should distinguish between different cache types.

Examples:

```text
Application Cache

Session Cache

Rate Limit Cache

Temporary Data

Query Cache

Distributed Locks
```

Each category should have its own namespace.

---

# Key Naming Convention

Keys should follow a consistent structure.

Recommended format:

```text
<namespace>:<resource>:<identifier>
```

Examples:

```text
user:profile:123

project:list:456

billing:subscription:789
```

Avoid random or inconsistent key names.

---

# Namespaces

Recommended namespaces:

```text
auth

users

projects

billing

storage

notifications

analytics
```

Namespaces simplify debugging and bulk invalidation.

---

# TTL Strategy

Every cached value should define a TTL.

Examples:

User Profile:

```text
15 minutes
```

Project List:

```text
5 minutes
```

Feature Flags:

```text
1 minute
```

Avoid permanent cache entries unless explicitly required.

---

# Cache Levels

The platform should support multiple cache levels.

Examples:

```text
Request Cache

↓

Application Cache

↓

Redis Cache

↓

Database
```

Each layer has a different purpose.

---

# Cache Flow

```text
Request

↓

Cache Lookup

↓

Hit?

↓

Yes

↓

Return Cached Data

↓

No

↓

Database

↓

Cache Result

↓

Return Response
```

Applications should treat the cache as an optimization, not the source of truth.

---

# Cache Aside Pattern

Preferred caching strategy:

```text
Application

↓

Cache Lookup

↓

Cache Miss

↓

Database

↓

Store in Cache

↓

Return Data
```

This pattern keeps the implementation simple and predictable.

---

# Write Strategy

Preferred approach:

```text
Database Updated

↓

Invalidate Cache

↓

Future Reads Repopulate Cache
```

Avoid updating cache and database independently.

Cache invalidation should happen immediately after successful writes.

---

# Cache Invalidation

Invalidation should be explicit.

Examples:

```text
User Updated

↓

Delete

user:profile:<id>
```

```text
Project Deleted

↓

Delete

project:list:*
```

Stale cache is often worse than no cache.

---

# Session Storage

Sessions may be stored in Redis.

Examples:

- Active sessions
- Refresh token metadata
- Device information

Redis should never become the permanent storage for user accounts.

---

# Rate Limiting

Rate limiting should use Redis.

Examples:

```text
Login Attempts

Password Reset

API Requests

Webhook Endpoints
```

Redis provides atomic counters suitable for these workloads.

---

# Temporary Data

Store short-lived data in cache.

Examples:

- Email verification codes
- OTPs
- Password reset tokens
- Import progress
- Export progress

Temporary data should always expire automatically.

---

# Distributed Locks

Support distributed locks for critical operations.

Examples:

- Billing synchronization
- Scheduled jobs
- Import workers
- Data migrations

Locks prevent duplicate processing across multiple workers.

---

# Feature Flags

Frequently accessed feature flags may be cached.

Recommended TTL:

```text
60 seconds
```

Changes should propagate quickly without excessive database reads.

---

# Query Caching

Cache expensive read operations.

Examples:

- Dashboard statistics
- Analytics summaries
- Public configuration

Avoid caching rapidly changing transactional data.

---

# Serialization

Use JSON for most cached values.

Complex objects should be converted into plain data structures before caching.

Avoid storing ORM models directly.

---

# Compression

Large cached values may be compressed.

Apply compression only when the performance benefit outweighs the CPU cost.

Measure before enabling compression.

---

# Configuration

Cache configuration should include:

```text
Provider

Host

Port

Database

Password

Default TTL

Maximum Connections

Key Prefix
```

Use Pydantic Settings for configuration.

Never hardcode connection details.

---

# Redis Pub/Sub

Redis Pub/Sub may be used for lightweight event distribution.

Examples:

- Cache invalidation
- Worker coordination
- Live notifications (future)

Do not use Pub/Sub as a durable message queue.

Use Celery (or another queue) for guaranteed delivery.

---

# Distributed Coordination

Multiple application instances should coordinate through Redis when necessary.

Examples:

- Leader election (future)
- Scheduled jobs
- Lock acquisition
- Cache invalidation events

Distributed coordination should be encapsulated inside the Cache package.

---

# Fallback Strategy

The application must continue operating if the cache becomes unavailable.

Preferred behavior:

```text
Cache Failure

↓

Log Warning

↓

Read Database

↓

Continue Request
```

Cache failures should not become application failures.

The cache is an optimization layer.

---

# Error Handling

Standardized cache errors:

```text
CACHE_UNAVAILABLE

CACHE_TIMEOUT

LOCK_TIMEOUT

INVALID_CACHE_KEY
```

Do not expose provider-specific exceptions to application code.

---

# Monitoring

Track cache health.

Metrics:

- Cache hit rate
- Cache miss rate
- Average latency
- Connection count
- Memory usage
- Evictions
- Lock contention

These metrics help identify performance bottlenecks.

---

# Cache Hit Ratio

Recommended targets:

```text
Application Cache

> 90%
```

```text
Database Query Cache

> 70%
```

Low hit rates often indicate poor cache strategy or incorrect TTL values.

---

# Eviction Policy

Prefer provider-managed eviction.

Recommended policies depend on workload.

Examples:

- LRU (Least Recently Used)
- LFU (Least Frequently Used)

Choose a policy appropriate for the application's access patterns.

---

# Memory Management

Avoid storing excessively large values.

Recommendations:

- Cache identifiers instead of large objects where practical
- Split oversized payloads
- Compress only after measuring impact

Monitor memory growth continuously.

---

# Cache Warming

Some frequently accessed data may be preloaded.

Examples:

- Feature flags
- Application settings
- Public configuration

Cache warming should occur during startup or scheduled jobs where appropriate.

---

# Cold Cache

Applications must behave correctly with an empty cache.

The first request may be slower, but functionality must remain correct.

Never assume cached values already exist.

---

# Background Refresh

For expensive datasets, support background refresh.

Workflow:

```text
Cache Near Expiration

↓

Background Worker

↓

Refresh Data

↓

Replace Cache

↓

Users Continue Reading Cached Value
```

This minimizes latency spikes.

---

# Local Development

Support:

- Local Redis
- Docker Compose
- In-memory cache (optional)

Developers should be able to run the platform locally with minimal setup.

---

# Security

Do not cache sensitive information unless necessary.

Examples to avoid:

- Password hashes
- Payment secrets
- Private keys
- OAuth client secrets

Cached authentication metadata should always have short TTLs.

---

# Multi-Tenancy

Tenant-aware cache keys should include organization context.

Example:

```text
organization:<org_id>:projects
```

Avoid cache collisions between organizations.

---

# Testing Strategy

## Unit Tests

Test:

- CacheService
- Key generation
- TTL handling
- Lock behavior

Mock provider implementations.

---

## Integration Tests

Test:

- Redis integration
- Cache invalidation
- Distributed locks
- Expiration behavior

Use a local Redis instance where practical.

---

## Performance Tests

Benchmark:

- Read latency
- Write latency
- Lock acquisition
- Bulk invalidation

Measure before optimizing.

---

# Documentation

Document:

- Cache namespaces
- TTL values
- Invalidation strategy
- Key formats

Documentation should evolve with the platform.

---

# Cache Checklist

Before shipping cache functionality:

- [ ] Provider abstraction implemented
- [ ] TTL configured
- [ ] Invalidation strategy defined
- [ ] Fallback behavior implemented
- [ ] Monitoring configured
- [ ] Metrics exposed
- [ ] Security reviewed
- [ ] Tests passing
- [ ] Documentation updated

---

# Anti-Patterns

Avoid:

- Treating cache as the source of truth
- Hardcoded Redis usage outside the Cache package
- Infinite TTLs without justification
- Caching highly volatile data unnecessarily
- Storing ORM objects directly
- Ignoring cache invalidation
- Large unbounded cache entries
- Failing requests when cache is unavailable

---

# Cache Definition of Done

A cache feature is complete only when:

- Provider abstraction is respected.
- TTL is defined.
- Invalidation strategy exists.
- Fallback behavior is implemented.
- Monitoring is enabled.
- Tests pass.
- Documentation is updated.

---

# Summary

The Cache package provides a reusable, provider-independent caching layer for all products built on FastForge.

Applications interact only with `CacheService`, while provider-specific implementation details remain isolated.

This architecture supports:

- Fast reads
- Reduced database load
- Distributed coordination
- Rate limiting
- Session storage
- Temporary data
- Predictable cache invalidation

By treating the cache strictly as a performance optimization rather than a source of truth, every future product gains speed without sacrificing correctness or maintainability.