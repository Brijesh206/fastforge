"""API key management routes.

Thin: create/list/revoke delegate to ApiKeyService. Authenticated the same
way as any other endpoint — get_current_user also accepts an API key, so a
key can be used to manage other keys, matching GitHub/Stripe's own APIs.
"""

from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from fastforge_api_keys import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse, ApiKeyService
from fastforge_auth import User

from app.api_keys.dependencies import get_api_key_service
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreatedResponse, status_code=HTTPStatus.CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKeyCreatedResponse:
    """Issue a new API key. The raw key is returned only in this response."""
    api_key, raw_key = await service.create_key(current_user.id, payload.name)
    return ApiKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        last_used_at=api_key.last_used_at,
        revoked_at=api_key.revoked_at,
        created_at=api_key.created_at,
        api_key=raw_key,
    )


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> list[ApiKeyResponse]:
    """List the authenticated user's API keys. Never includes raw values."""
    keys = await service.list_keys(current_user.id)
    return [ApiKeyResponse.model_validate(key) for key in keys]


@router.delete("/{key_id}", status_code=HTTPStatus.NO_CONTENT)
async def revoke_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> None:
    """Revoke a key. 404s if it doesn't exist or isn't the caller's."""
    await service.revoke_key(current_user.id, key_id)
