"""Login and token schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Payload for email/password login."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email casing so lookups stay consistent with registration."""
        return value.strip().lower()


class AccountDeleteRequest(BaseModel):
    """Payload confirming a user's password before deleting their own account."""

    model_config = ConfigDict(extra="forbid")

    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """Payload for exchanging a refresh token for a new token pair."""

    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(..., min_length=1)


class TokenClaims(BaseModel):
    """Verified claims decoded from an access or refresh token."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    # Must match users.token_version; a mismatch means the token was revoked.
    token_version: int = 0


class TokenPair(BaseModel):
    """Access and refresh token issued after successful authentication."""

    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
