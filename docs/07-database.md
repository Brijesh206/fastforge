# Database Guide

> Database architecture, standards, conventions, and best practices for FastForge.

---

# Purpose

The database is one of the few parts of the platform that every product depends on.

This document defines:

- Schema design
- Naming conventions
- UUID strategy
- Relationships
- Migrations
- Indexes
- Performance guidelines
- Repository conventions

Every product should follow these standards.

---

# Database Stack

| Component | Technology |
|-----------|------------|
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Validation | Pydantic |
| Driver | asyncpg |

Initially hosted on Supabase.

Future migration should require zero business logic changes.

---

# Design Principles

The database should be:

- Predictable
- Explicit
- Normalized
- Performant
- Easy to migrate

The schema should evolve slowly.

Frequent schema changes indicate poor modeling.

---

# UUID Strategy

Every table uses UUID as the primary key.

Preferred:

```
UUIDv7
```

Fallback:

```
UUIDv4
```

Reasons:

- Global uniqueness
- Better API security
- Easier data migration
- Distributed-friendly
- No sequential IDs exposed

Example:

```text
users

id UUID PRIMARY KEY
```

---

# Foreign Keys

Foreign keys also use UUID.

Example:

```text
projects

id UUID

owner_id UUID REFERENCES users(id)
```

UUID has full support for foreign key constraints.

There is no limitation compared to integer primary keys.

---

# Base Model

Every SQLAlchemy model should inherit from a shared base class.

Minimum fields:

```text
id

created_at

updated_at
```

Optional fields:

```text
deleted_at

created_by

updated_by
```

Avoid duplicating these columns across models.

---

# Timestamp Rules

Every table should include:

```
created_at

updated_at
```

Use UTC.

Database timestamps should be timezone-aware.

Never store local time.

---

# Naming Conventions

Tables:

```
snake_case
```

Examples:

```
users

projects

api_keys

subscriptions
```

Columns:

```
snake_case
```

Examples:

```
first_name

created_at

owner_id
```

Indexes:

```
ix_<table>_<column>
```

Examples:

```
ix_users_email

ix_projects_owner_id
```

Foreign keys:

```
fk_<table>_<column>
```

Unique constraints:

```
uq_<table>_<column>
```

---

# Primary Keys

Always:

```
id UUID PRIMARY KEY
```

Never:

```
user_id PRIMARY KEY
```

Reserve `user_id` for foreign keys.

---

# Relationships

Use explicit relationships.

Example:

```
User

↓

Project

↓

API Key
```

One-to-many:

```
User

↓

Projects
```

Many-to-many:

Use a join table.

Never store arrays of IDs.

---

# One-to-One

Example:

```
User

↓

UserProfile
```

Implement with a unique foreign key.

---

# Many-to-Many

Example:

```
Users

↓

Organization Members

↓

Organizations
```

Join tables should be first-class tables.

Avoid hidden many-to-many abstractions.

---

# Cascade Rules

Be conservative with cascade deletes.

Good candidates:

- Temporary tokens
- Sessions
- Verification codes

Avoid cascading deletion of important business data.

Prefer soft deletion where appropriate.

---

# Soft Deletes

Only implement soft deletes when necessary.

Standard column:

```
deleted_at
```

Avoid:

```
is_deleted
```

Timestamp-based deletion preserves audit information.

---

# Unique Constraints

Use database constraints.

Do not rely only on application validation.

Examples:

```
email

username

slug
```

The database should enforce uniqueness.

---

# Check Constraints

Use check constraints for important invariants.

Examples:

```
price >= 0

quantity >= 0
```

Validation belongs in both the application and the database.

---

# Indexing

Indexes should be intentional.

Always index:

- Foreign keys
- Frequently searched columns
- Unique columns

Examples:

```
email

owner_id

organization_id

created_at
```

Avoid indexing every column.

Indexes increase write cost.

---

# Composite Indexes

Use composite indexes for common query patterns.

Example:

```
organization_id

created_at
```

instead of two separate indexes if queries commonly use both.

Measure before adding indexes.

---

# JSON Columns

Use JSONB only when appropriate.

Good use cases:

- Provider metadata
- Configuration
- Flexible settings

Avoid storing structured relational data inside JSON.

Normalize when relationships exist.

---

# Enums

Use PostgreSQL enums for stable values.

Examples:

```
SubscriptionStatus

Role

Plan

Provider
```

Avoid free-form strings for controlled values.

---

# Migrations

Every schema change requires a migration.

Never modify production schemas manually.

Migration workflow:

```
Model Change

↓

Generate Migration

↓

Review

↓

Apply

↓

Commit
```

Always review generated migrations before applying.

---

# Migration Rules

One logical change per migration.

Good:

```
Add api_keys table
```

Bad:

```
Update everything
```

Migration names should clearly describe their purpose.

---

# Repository Pattern

Repositories own persistence.

Responsibilities:

- CRUD
- Queries
- Pagination
- Filtering

Repositories should never contain:

- Permission checks
- Billing
- Email sending
- Business workflows

---

# Query Guidelines

Prefer explicit queries.

Avoid hidden magic.

Good:

```
get_user_by_email()
```

Better than:

```
find()
```

Method names should communicate intent.

---

# Pagination

Every list endpoint should support pagination.

Standard parameters:

```
page

page_size
```

Future support:

Cursor pagination.

Never return unlimited datasets.

---

# Filtering

Repositories should support filtering.

Examples:

```
status

created_after

created_before

organization_id

search
```

Filtering logic should not be duplicated in services.

---

# Sorting

Allow only predefined sort fields.

Examples:

```
created_at

updated_at

name
```

Reject unknown sort fields.

Prevent arbitrary SQL generation.

---

# Transactions

Transactions should be managed by the Service layer.

Repositories should not commit or rollback transactions.

Example:

```
Create User

↓

Create Workspace

↓

Create Default Project

↓

Commit Transaction
```

If any operation fails:

```
Rollback
```

The entire workflow should succeed or fail as one unit.

---

# Optimistic Locking

For records that may be edited concurrently, use optimistic locking.

Recommended approach:

- `updated_at` comparison for simple cases
- Version column (`version`) for high-contention resources

Avoid pessimistic locking unless absolutely necessary.

---

# Audit Fields

Where auditability is important, include:

```text
created_by

updated_by
```

These fields should reference the `users` table.

Use them for:

- Administrative actions
- Team collaboration
- Compliance requirements

---

# Multi-Tenancy

The platform should be ready for organization-based products.

Preferred approach:

```
organization_id UUID
```

Every tenant-owned resource includes:

```
organization_id
```

Examples:

- Projects
- API Keys
- Subscriptions
- Members

Never rely solely on frontend filtering for tenant isolation.

Authorization must always enforce ownership.

---

# Ownership

Every resource should clearly define its owner.

Example:

```
Project

↓

owner_id

organization_id
```

This supports both personal and organization-owned resources.

---

# Seed Data

Provide repeatable seed scripts.

Examples:

- Demo user
- Admin user
- Default plans
- Feature flags
- Sample projects

Seed scripts should be idempotent.

Running them multiple times should not create duplicates.

---

# Development Data

Keep development fixtures realistic.

Include:

- Multiple users
- Different plans
- Active subscriptions
- Expired subscriptions
- API keys
- Organizations

Realistic data improves development and testing.

---

# Backup Strategy

Production databases should support regular backups.

Minimum requirements:

- Daily automated backups
- Point-in-time recovery (if supported)
- Backup verification

The application should not depend on backup implementation details.

---

# Restore Strategy

Backups are only useful if restoration is tested.

Periodically verify that backups can be restored successfully.

Document the restoration process.

---

# Performance Guidelines

Measure before optimizing.

Focus on:

- Query count
- Query duration
- Index usage
- Connection pool utilization

Avoid premature optimization.

---

# N+1 Queries

Avoid N+1 query patterns.

Bad:

```
Load Users

↓

Loop

↓

Load Projects
```

Better:

Use eager loading where appropriate.

Review generated SQL during development.

---

# Eager vs Lazy Loading

Use eager loading for:

- Frequently accessed relationships
- Dashboard views
- Detail pages

Use lazy loading for:

- Rarely accessed relationships
- Large collections

Choose intentionally.

---

# Bulk Operations

Prefer bulk operations when processing many records.

Examples:

- Import users
- Archive projects
- Update statuses

Avoid one database query per record.

---

# Connection Pooling

Configure a sensible connection pool.

Monitor:

- Pool size
- Wait time
- Timeouts

Adjust based on production usage.

---

# SQLAlchemy Conventions

Use SQLAlchemy 2 style APIs.

Always use:

- Typed models
- Mapped columns
- Explicit relationships

Avoid deprecated SQLAlchemy patterns.

Keep ORM usage modern and consistent.

---

# Alembic Workflow

Schema changes follow this workflow:

```
Modify Model

↓

Generate Migration

↓

Review Migration

↓

Apply Locally

↓

Run Tests

↓

Commit
```

Never edit the production database directly.

---

# Database Testing

Database tests should run against an isolated test database.

Tests should never reuse production data.

Each test should:

- Create required data
- Execute assertions
- Clean up automatically

Tests should be independent.

---

# Fixtures

Create reusable fixtures for common entities.

Examples:

- User
- Organization
- Project
- API Key

Fixtures should reduce duplication in tests.

---

# Repository Testing

Repositories should be tested with a real database where practical.

Verify:

- CRUD operations
- Filtering
- Sorting
- Pagination
- Constraints

Mocking the database is insufficient for repository tests.

---

# Data Integrity

Protect integrity with:

- Foreign keys
- Unique constraints
- Check constraints
- Transactions

Never rely solely on application code.

The database is the final authority.

---

# Schema Evolution

Schema evolution should prioritize backward compatibility.

Prefer:

- Additive changes
- Nullable fields (temporarily)
- Data migrations

Avoid destructive changes without a migration strategy.

---

# Documentation

Every table should have a clear purpose.

Document:

- Relationships
- Constraints
- Ownership
- Lifecycle

Database documentation should evolve alongside the schema.

---

# Database Checklist

Before merging a schema change:

- [ ] Migration created
- [ ] Migration reviewed
- [ ] Constraints defined
- [ ] Foreign keys added
- [ ] Indexes reviewed
- [ ] Relationships documented
- [ ] Tests updated
- [ ] Seed data updated if required
- [ ] Performance impact considered

---

# Anti-Patterns

Avoid:

- Integer primary keys mixed with UUIDs
- Missing foreign keys
- Missing indexes on foreign keys
- Business logic in models
- JSON used as a relational database
- Unbounded queries
- Duplicate data
- Manual schema changes
- Over-indexing
- Circular relationships without need

---

# Database Definition of Done

A database feature is complete only when:

- Schema follows naming conventions.
- UUIDs are used consistently.
- Relationships are explicit.
- Constraints are enforced.
- Migrations exist.
- Tests pass.
- Documentation is updated.

---

# Summary

The database is the foundation of every product built on FastForge.

Consistency, correctness, and maintainability take priority over clever optimizations.

Every schema decision should support long-term evolution, safe migrations, and predictable behavior.

A well-designed database reduces application complexity and enables rapid product development for years to come.