"""Set schedule_status = true for all existing users.

Revision ID: 0002_enable_user_schedule
Revises: 0001_create_tables
Create Date: 2026-04-12

"""
from alembic import op

revision = "0002_enable_user_schedule"
down_revision = "0001_create_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE users
        SET schedule_status = true
        WHERE schedule_status IS DISTINCT FROM true
        """
    )


def downgrade() -> None:
    # Cannot restore previous per-user flags; no-op downgrade.
    pass
