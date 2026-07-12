# Common Package

Shared foundation utilities for FastForge.

## Responsibilities

- Base application settings
- Environment enums
- Shared constants
- Application exception hierarchy
- Standard error schemas

## Usage

```python
from fastforge_common.config import BaseAppSettings
from fastforge_common.enums import AppEnvironment
from fastforge_common.exceptions import AppError, NotFoundError
from fastforge_common.schemas import ErrorResponse
```

## Rules

- Keep this package framework-agnostic.
- Do not import FastAPI, SQLAlchemy, Celery, Redis, Stripe, or provider SDKs.
- Put shared primitives here only when multiple packages or apps need them.
- Feature-specific errors, schemas, and constants should stay in their owning package.
