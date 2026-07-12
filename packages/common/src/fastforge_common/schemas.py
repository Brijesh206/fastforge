"""Shared Pydantic schemas."""

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """Standard API error detail."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    details: dict[str, object] | None = None


class ErrorResponse(BaseModel):
    """Standard API error envelope."""

    model_config = ConfigDict(extra="forbid")

    error: ErrorDetail
