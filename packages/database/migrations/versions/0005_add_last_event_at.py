"""Add subscriptions.last_event_at.

Tracks the Stripe event's own `created` timestamp so handle_event can reject
an out-of-order (redelivered/retried) older event instead of overwriting
fresher state (fastforge_billing.services.billing_service.BillingService).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_add_last_event_at"
down_revision: str | None = "0004_create_subscriptions_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "last_event_at")
