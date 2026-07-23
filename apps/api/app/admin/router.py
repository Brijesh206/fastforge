"""Admin routes.

Owner-only: the whole router is gated by ``require_admin`` (ADMIN_EMAILS
allowlist). Thin — each endpoint delegates to ``AdminService``.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastforge_auth import User
from fastforge_billing import Subscription
from fastforge_database.utils.pagination import PaginationParams

from app.admin.dependencies import get_admin_service, require_admin
from app.admin.schemas import (
    AdminStats,
    AdminSubscriptionInfo,
    AdminUserDetail,
    AdminUserItem,
    AdminUserList,
)
from app.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats", response_model=AdminStats)
async def get_stats(service: AdminService = Depends(get_admin_service)) -> AdminStats:
    """Headline counts: total users, total & active subscriptions."""
    return AdminStats(**await service.stats())


@router.get("/users", response_model=AdminUserList)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, description="Filter by email substring"),
    service: AdminService = Depends(get_admin_service),
) -> AdminUserList:
    """Paginated user list, newest first, optional email search."""
    result = await service.list_users(
        PaginationParams(page=page, page_size=page_size), query=q
    )
    return AdminUserList(
        items=[AdminUserItem.model_validate(user) for user in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/users/{user_id}", response_model=AdminUserDetail)
async def get_user(
    user_id: UUID, service: AdminService = Depends(get_admin_service)
) -> AdminUserDetail:
    """A single user with their subscription, if any."""
    user, subscription = await service.get_user_detail(user_id)
    return _to_detail(user, subscription)


@router.post("/users/{user_id}/activate", response_model=AdminUserItem)
async def activate_user(
    user_id: UUID, service: AdminService = Depends(get_admin_service)
) -> AdminUserItem:
    """Re-enable a deactivated user."""
    user = await service.set_user_active(user_id, active=True)
    return AdminUserItem.model_validate(user)


@router.post("/users/{user_id}/deactivate", response_model=AdminUserItem)
async def deactivate_user(
    user_id: UUID, service: AdminService = Depends(get_admin_service)
) -> AdminUserItem:
    """Suspend a user. Refused for admin accounts (no self-lockout)."""
    user = await service.set_user_active(user_id, active=False)
    return AdminUserItem.model_validate(user)


def _to_detail(user: User, subscription: Subscription | None) -> AdminUserDetail:
    return AdminUserDetail(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        subscription=(
            AdminSubscriptionInfo.from_model(subscription) if subscription else None
        ),
    )
