"""Create chats and users tables (idempotent on PostgreSQL).

Uses IF NOT EXISTS so existing databases that already have these tables
(from older bot builds using metadata.create_all) can run ``alembic upgrade head``
without a manual ``alembic stamp``.

Revision ID: 0001_create_tables
Revises:
Create Date: 2026-04-12

"""
from alembic import op

revision = "0001_create_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            chat_id BIGINT NOT NULL PRIMARY KEY,
            status BOOLEAN,
            schedule_status BOOLEAN
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT NOT NULL PRIMARY KEY,
            schedule_status BOOLEAN
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TABLE IF EXISTS chats")
