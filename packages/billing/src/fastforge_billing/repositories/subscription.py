"""Subscription repository."""

from uuid import UUID

from fastforge_database.repositories.base import BaseRepository

from fastforge_billing.models.subscription import Subscription


class SubscriptionRepository(BaseRepository[Subscription]):
    """Persistence for subscriptions. Owns database access only."""

    model = Subscription

    async def get_by_user_id(self, user_id: UUID) -> Subscription | None:
        """Fetch the subscription row for a user, if one exists."""
        query = self._base_query().where(Subscription.user_id == user_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_customer_id(self, stripe_customer_id: str) -> Subscription | None:
        """Fetch the subscription row for a Stripe customer, if one exists."""
        query = self._base_query().where(
            Subscription.stripe_customer_id == stripe_customer_id
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
