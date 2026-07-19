"""Database configuration."""

import ssl
from typing import Literal, cast

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

DatabaseSslMode = Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
DATABASE_SSL_MODES: set[str] = {
    "disable",
    "allow",
    "prefer",
    "require",
    "verify-ca",
    "verify-full",
}


class DatabaseSettings(BaseSettings):
    """Database connection settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = Field(
        ...,
        alias="DATABASE_URL",
        description="Async PostgreSQL connection URL (postgresql+asyncpg://...)",
    )
    pool_size: int = Field(default=5, ge=1, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=10, ge=0, alias="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, ge=1, alias="DATABASE_POOL_TIMEOUT")
    # pre_ping issues a `SELECT 1` on every connection checkout to detect dead
    # connections. That is one extra network round-trip per request — cheap next
    # to a local DB (~1ms), painful against a remote one (a US Supabase from
    # India is ~330ms of pure tax per request). Keep it on for prod resilience;
    # turn it off in dev when the DB is far away and an occasional reconnect is
    # tolerable. See DATABASE_POOL_RECYCLE for the pre_ping-free safety net.
    pool_pre_ping: bool = Field(default=True, alias="DATABASE_POOL_PRE_PING")
    pool_recycle: int = Field(default=1800, ge=-1, alias="DATABASE_POOL_RECYCLE")
    echo: bool = Field(default=False, alias="DATABASE_ECHO")
    ssl_mode: DatabaseSslMode | None = Field(default=None, alias="DATABASE_SSL_MODE")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Ensure the database URL uses a PostgreSQL scheme."""
        if not value.startswith(("postgresql://", "postgresql+asyncpg://")):
            msg = "DATABASE_URL must use postgresql:// or postgresql+asyncpg://"
            raise ValueError(msg)
        return value

    @property
    def async_url(self) -> str:
        """Return the database URL as an asyncpg SQLAlchemy URL."""
        return self._async_url().render_as_string(hide_password=False)

    @property
    def connect_args(self) -> dict[str, object]:
        """Return driver-specific connection arguments.

        SSL semantics follow libpq's ``sslmode`` values, mapped to an asyncpg
        SSL context:

        - ``disable`` — no SSL.
        - ``allow`` / ``prefer`` — let asyncpg negotiate (no explicit arg).
        - ``require`` — encrypt, but do not verify the server certificate.
          Managed providers such as Supabase present certificates that are not
          verifiable against the local trust store, so verification is
          intentionally disabled here (matching ``sslmode=require``).
        - ``verify-ca`` / ``verify-full`` — verify the certificate chain (and
          the hostname for ``verify-full``) against the system trust store.
        """
        ssl_mode = self._resolved_ssl_mode()
        if ssl_mode is None or ssl_mode in {"allow", "prefer"}:
            return {}
        if ssl_mode == "disable":
            return {"ssl": False}

        context = ssl.create_default_context()
        if ssl_mode in {"verify-ca", "verify-full"}:
            context.check_hostname = ssl_mode == "verify-full"
            return {"ssl": context}

        # "require": encrypt without certificate verification.
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return {"ssl": context}

    @property
    def is_supabase_url(self) -> bool:
        """Return True when DATABASE_URL points at Supabase Postgres."""
        host = self._database_url().host
        return host is not None and (
            host.endswith(".supabase.co") or "pooler.supabase.com" in host
        )

    def _database_url(self) -> URL:
        """Parse the configured database URL."""
        return make_url(self.database_url)

    def _async_url(self) -> URL:
        """Normalize a PostgreSQL URL for SQLAlchemy's asyncpg driver."""
        url = self._database_url()
        query = dict(url.query)
        query.pop("sslmode", None)
        query.pop("sslrootcert", None)

        if url.drivername == "postgresql":
            url = url.set(drivername="postgresql+asyncpg")

        return url.set(query=query)

    def _resolved_ssl_mode(self) -> DatabaseSslMode | None:
        """Resolve SSL mode from settings, URL query, and known provider hosts."""
        if self.ssl_mode is not None:
            return self.ssl_mode

        query_ssl_mode = self._database_url().query.get("sslmode")
        if isinstance(query_ssl_mode, str) and query_ssl_mode in DATABASE_SSL_MODES:
            return cast(DatabaseSslMode, query_ssl_mode)

        if self.is_supabase_url:
            return "require"

        return None
