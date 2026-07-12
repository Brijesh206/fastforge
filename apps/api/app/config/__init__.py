# TODO: Application-specific configuration.
# Must use Pydantic Settings — never os.getenv() in business logic.
# See docs/05-backend.md
"""API configuration."""

from functools import lru_cache

from fastforge_common.config import BaseAppSettings
from pydantic import Field


class ApiSettings(BaseAppSettings):
    """Settings for the FastAPI application."""

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, ge=1, le=65535, alias="API_PORT")
    api_reload: bool = Field(default=True, alias="API_RELOAD")


@lru_cache
def get_settings() -> ApiSettings:
    """Return cached API settings."""
    return ApiSettings()
