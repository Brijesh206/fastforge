# Auth Package

Authentication foundation for FastForge.

Application-managed authentication. Not tightly coupled to Supabase Auth
or any other identity provider — see `docs/08-authentication.md`.

## Responsibilities

- Shared `User` model (UUIDv7 primary key)
- Registration, login, and account-lifecycle schemas
- Password hashing interface + Argon2id adapter
- Token service interface + JWT adapter (access/refresh token pair)
- Single-use `AuthToken` model + repository for email verification and
  password reset (hashed at rest, expiring, single-use)
- `UserRepository` (get by id, get by email, create)
- `AuthService` (register, authenticate, verify email, reset password)
- Auth-specific exceptions built on the shared `fastforge_common` error hierarchy

### Account-lifecycle tokens

The token-issuing methods (`issue_email_verification_token`,
`issue_password_reset_token`) return the **raw** token for the caller to place
in an email link; only its SHA-256 hash is stored, so a database leak never
exposes a usable link. `verify_email` and `reset_password` consume a token,
enforcing single use and expiry. The package **does not** send email — the
application wires these tokens to the mail package (see
`apps/api/app/auth/emails.py`), keeping the two feature packages independent.

`issue_password_reset_token` returns `None` for an unknown or inactive
account rather than raising, so the endpoint can respond identically whether
or not the address exists (no account enumeration).

Not yet implemented (future passes): OAuth, session persistence/revocation,
roles/permissions, organizations, API keys.

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
