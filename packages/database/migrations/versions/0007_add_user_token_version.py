"""Add users.token_version.

Embedded in every JWT as "ver"; bumping it revokes all outstanding tokens
(password reset does this). Existing tokens carry no "ver" claim and decode
as version 0, matching the column default, so they stay valid until the
first bump.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_add_user_token_version"
down_revision: str | None = "0006_create_api_keys_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("users", "token_version")
