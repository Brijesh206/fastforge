"""Admin service: orchestrates the auth and billing repositories for the panel.

Lives in the app (not a package) because it deliberately crosses feature
boundaries — packages stay independent; the app is where they're wired.
"""

from uuid import UUID

from fastforge_auth import User, UserRepository
from fastforge_billing import Subscription, SubscriptionRepository
from fastforge_common.exceptions import AuthorizationError, NotFoundError
from fastforge_database.utils.pagination import PaginatedResult, PaginationParams

from app.config import get_settings


class AdminService:
    """Read + light management operations over users and their subscriptions."""

    def __init__(
        self, users: UserRepository, subscriptions: SubscriptionRepository
    ) -> None:
        self._users = users
        self._subscriptions = subscriptions

    async def list_users(
        self, pagination: PaginationParams, *, query: str | None = None
    ) -> PaginatedResult[User]:
        """Paginated user list, optionally filtered by an email substring."""
        return await self._users.search_paginated(pagination, email_query=query)

    async def get_user_detail(
        self, user_id: UUID
    ) -> tuple[User, Subscription | None]:
        """A user plus their subscription row (if any). 404 if no such user."""
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        subscription = await self._subscriptions.get_by_user_id(user_id)
        return user, subscription

    async def set_user_active(self, user_id: UUID, *, active: bool) -> User:
        """Activate or deactivate a user. Refuses to deactivate an admin so an
        operator can't lock the panel out from itself."""
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        if not active and get_settings().is_admin(user.email):
            raise AuthorizationError("Cannot deactivate an admin account.")
        user.is_active = active
        return await self._users.update(user)

    async def stats(self) -> dict[str, int]:
        """Headline counts for the panel."""
        return {
            "total_users": await self._users.count(),
            "total_subscriptions": await self._subscriptions.count(),
            "active_subscriptions": await self._subscriptions.count_active(),
        }
