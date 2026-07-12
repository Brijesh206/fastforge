"""Health check schemas."""

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Health check response."""

    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    checks: dict[str, str] = Field(default_factory=dict)
