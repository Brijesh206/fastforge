# Database Package

Database foundation for FastForge.

## Responsibilities

- SQLAlchemy 2 async configuration
- Base models with UUIDv7 primary keys
- Stable Alembic naming conventions
- Soft delete and audit mixins
- Session management
- Repository base classes
- Pagination and sorting helpers
- Local PostgreSQL and Supabase PostgreSQL URLs
- Alembic migrations

## Usage

```python
from fastforge_database.config import DatabaseSettings
from fastforge_database.session import DatabaseManager
from fastforge_database.models.base import BaseModel, SoftDeleteMixin, TimestampMixin
from fastforge_database.repositories.base import BaseRepository
from fastforge_database.utils.pagination import PaginationParams, PaginatedResult
```

## Migrations

```bash
cd packages/database
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"
```

## Configuration

Set `DATABASE_URL` in your environment:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fastforge_platform
```

Supabase connection strings are supported directly:

```
DATABASE_URL=postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require
```

The package normalizes `postgresql://` URLs to `postgresql+asyncpg://` and enables
SSL automatically for Supabase hosts. You can also force SSL explicitly:

```
DATABASE_SSL_MODE=require
```

See `docs/07-database.md` for full standards.
