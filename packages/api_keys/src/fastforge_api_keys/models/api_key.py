"""API key model."""

from datetime import datetime
from uuid import UUID

from fastforge_database.models.base import BaseModel
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class ApiKey(BaseModel):
    """A programmatic credential a user can issue for their account.

    Only the hash of the raw key is stored (key_hash) — the raw value is
    returned to the caller once, at creation, and never persisted or
    recoverable. key_prefix holds the first characters in plaintext so a
    key-management UI can show "ffk_xK9f2Lq…" without the full secret.
    """

    __tablename__ = "api_keys"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    @property
    def is_revoked(self) -> bool:
        """Return True if the key has been revoked."""
        return self.revoked_at is not None
