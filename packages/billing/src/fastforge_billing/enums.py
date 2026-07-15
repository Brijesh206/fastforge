"""Billing enums."""

from enum import StrEnum


class SubscriptionStatus(StrEnum):
    """Platform subscription statuses, mapped 1:1 from Stripe's own values.

    ACTIVE and TRIALING grant access; every other state does not.
    """

    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    UNPAID = "unpaid"


ACTIVE_STATUSES = frozenset({SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING})
