# Auth Package

Authentication foundation for FastForge.

Application-managed authentication. Not tightly coupled to Supabase Auth
or any other identity provider — see `docs/08-authentication.md`.

## Responsibilities (first pass)

- Shared `User` model (UUIDv7 primary key)
- Registration and login schemas
- Password hashing interface + Argon2id adapter
- Token service interface + JWT adapter (access/refresh token pair)
- `UserRepository` (get by id, get by email, create)
- `AuthService` (register, authenticate)
- Auth-specific exceptions built on the shared `fastforge_common` error hierarchy

Not yet implemented (future passes): OAuth, sessions, email verification,
password reset, roles/permissions, organizations, API keys.

## Usage

```python
from fastforge_auth import (
    AuthService,
    AuthSettings,
    Argon2PasswordHasher,
    JwtTokenService,
    UserRepository,
)

password_hasher = Argon2PasswordHasher()
token_service = JwtTokenService(AuthSettings())
user_repository = UserRepository(session)  # session: AsyncSession

auth_service = AuthService(user_repository, password_hasher, token_service)

user = await auth_service.register_user(UserCreate(email="a@b.com", password="..."))
tokens = await auth_service.authenticate_user(LoginRequest(email="a@b.com", password="..."))
```

## Architecture

- Routes must not contain business logic — that belongs to `AuthService`.
- `UserRepository` owns all SQLAlchemy access; it never checks permissions
  or runs business workflows.
- `AuthService` never imports Argon2 or PyJWT directly — it depends only on
  the `PasswordHasher` and `TokenService` interfaces, so the underlying
  hashing algorithm or token strategy can change without touching business
  logic.
- Transactions are controlled by the caller (e.g. a FastAPI dependency using
  `DatabaseManager.transaction()`), consistent with the rest of the platform.

## Configuration

`AuthSettings` reads from the environment:

```
JWT_SECRET_KEY=<at least 16 characters>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
```

## Migrations

The `users` table is defined in the shared database migrations directory:

```
packages/database/migrations/versions/0002_create_users_table.py
```

Migrations for all feature packages live in `packages/database/migrations`
(see `packages/database/README.md`). `packages/database/migrations/env.py`
imports `fastforge_auth.models.user.User` so the model is registered on the
shared metadata for future autogenerate runs.

```bash
cd packages/database
uv run alembic upgrade head
```

See `docs/08-authentication.md` for full standards.
