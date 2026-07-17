# TODO: Application-specific configuration.
# Must use Pydantic Settings — never os.getenv() in business logic.
# See docs/05-backend.md
"""API configuration."""

from functools import lru_cache
from typing import Annotated

from fastforge_common.config import BaseAppSettings
from pydantic import Field, field_validator
from pydantic_settings import NoDecode


class ApiSettings(BaseAppSettings):
    """Settings for the FastAPI application."""

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, ge=1, le=65535, alias="API_PORT")
    api_reload: bool = Field(default=True, alias="API_RELOAD")
    # Where the web app serves its verify-email / reset-password pages. Email
    # links point here, not at the API.
    frontend_base_url: str = Field(
        default="http://localhost:3000", alias="FRONTEND_BASE_URL"
    )
    # Emails allowed into the admin panel. Comma-separated in the env, e.g.
    # ADMIN_EMAILS=you@example.com,ops@example.com. Empty = no admins (locked).
    admin_emails: Annotated[list[str], NoDecode] = Field(
        default_factory=list, alias="ADMIN_EMAILS"
    )

    @field_validator("admin_emails", mode="before")
    @classmethod
    def _split_admin_emails(cls, value: object) -> object:
        """Accept a comma-separated env string and normalize to lowercased emails."""
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(",") if item.strip()]
        return value

    def is_admin(self, email: str) -> bool:
        """Return True if the email is on the admin allowlist."""
        return email.strip().lower() in self.admin_emails


@lru_cache
def get_settings() -> ApiSettings:
    """Return cached API settings."""
    return ApiSettings()
