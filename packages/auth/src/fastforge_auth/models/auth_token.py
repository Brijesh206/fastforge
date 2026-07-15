"""Single-use auth token model (email verification, password reset)."""

from datetime import datetime
from uuid import UUID

from fastforge_database.models.base import BaseModel
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from fastforge_auth.constants import TOKEN_HASH_LENGTH


class AuthToken(BaseModel):
    """A hashed, expiring, single-use token tied to a user and a purpose.

    Only the hash is stored. The raw token lives solely in the email link
    sent to the user. ``used_at`` enforces single use; a redeemed or expired
    row can never be replayed.
    """

    __tablename__ = "auth_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(
        String(TOKEN_HASH_LENGTH), unique=True, nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
