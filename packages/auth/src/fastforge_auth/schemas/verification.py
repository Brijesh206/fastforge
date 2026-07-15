"""Email verification and password reset schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from fastforge_auth.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH


class VerifyEmailRequest(BaseModel):
    """Payload confirming an email address with a verification token."""

    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., min_length=1)


class PasswordResetRequest(BaseModel):
    """Payload requesting a password reset link for an email address."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize casing to match how the address was registered."""
        return value.strip().lower()


class PasswordResetConfirm(BaseModel):
    """Payload setting a new password with a reset token."""

    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)


class MessageResponse(BaseModel):
    """Generic acknowledgement for endpoints with no resource to return."""

    model_config = ConfigDict(extra="forbid")

    detail: str
