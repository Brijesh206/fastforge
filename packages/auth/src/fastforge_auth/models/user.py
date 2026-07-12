"""User model."""

from datetime import datetime

from fastforge_database.models.base import BaseModel
from sqlalchemy import Boolean, DateTime, String
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
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
