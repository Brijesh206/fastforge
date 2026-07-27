"""User model."""

from datetime import datetime

from fastforge_database.models.base import BaseModel
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class User(BaseModel):
    """Core user identity shared across every product.

    ``password_hash`` is nullable because a user may authenticate only
    through an OAuth provider and never set a local password.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Embedded in every JWT as "ver"; bumping it revokes all outstanding
    # access + refresh tokens (password reset does this).
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    @property
    def has_password(self) -> bool:
        """True when a local password is set; false for OAuth-only accounts.

        The settings UI reads this to decide between "set a password" and
        "change password" — an OAuth-only user has no current password to
        prove.
        """
        return self.password_hash is not None
