"""API key request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    """Payload for issuing a new API key."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255)


class ApiKeyResponse(BaseModel):
    """Public representation of an API key. Never includes the raw secret."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    name: str
    key_prefix: str
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Returned once, at creation — the only time the raw key is available.

    Callers must store api_key themselves; it cannot be retrieved again.
    """

    api_key: str
