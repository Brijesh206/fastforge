"""User request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from fastforge_auth.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH


class UserCreate(BaseModel):
    """Payload for registering a new user."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email casing so lookups and uniqueness stay consistent."""
        return value.strip().lower()


class UserUpdate(BaseModel):
    """Payload for editing your own profile.

    ``full_name`` is required-but-nullable rather than optional: with a single
    editable field, making the client send it explicitly removes the "was it
    omitted or cleared?" ambiguity that partial updates otherwise need
    model_fields_set to resolve.
    """

    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(..., max_length=255)

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        """Treat a blank or whitespace-only name as cleared."""
        if value is None:
            return None
        return value.strip() or None


class PasswordChange(BaseModel):
    """Payload for setting or changing your own password.

    ``current_password`` is required only when one is already set — an
    OAuth-only account sets its first password without it, since there is
    nothing to prove.
    """

    model_config = ConfigDict(extra="forbid")

    current_password: str | None = None
    new_password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)


class UserResponse(BaseModel):
    """Public representation of a user. Never expose the SQLAlchemy model directly."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    has_password: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    # Not a user column — admin status comes from the ADMIN_EMAILS setting, so
    # only the routes that have access to it fill this in (see /auth/me).
    is_admin: bool = False
