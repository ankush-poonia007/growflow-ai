"""Gate 13: create notifications table with user indexes, deduplication event_id, and RLS.

Revision ID: 0009_gate13_notifications
Revises: 0008_gate12_rls_hardening
Create Date: 2026-09-17 UTC

Authorised by: Batch 3 — Notifications, Search & Shared Platform UX
Architecture ref:
  Phase 8 Batch 3 Specification § 2, 11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic (<= 32 chars for alembic_version column limit).
revision: str = "0009_gate13_notifications"
down_revision: str | None = "0008_gate12_rls_hardening"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. notifications table
    # ---------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("actor_role", sa.String(length=50), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="SYSTEM"),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("link", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("event_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            name=op.f("fk_notifications_actor_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_notifications_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )

    # Indexes
    op.create_index(
        "ix_notifications_user_unread",
        "notifications",
        ["user_id", "is_read", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_user_created",
        "notifications",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_event_id",
        "notifications",
        ["event_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_notifications_event_user",
        "notifications",
        ["event_id", "user_id"],
    )

    # ---------------------------------------------------------
    # 2. PostgreSQL Row Level Security (RLS)
    # ---------------------------------------------------------
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE notifications ENABLE ROW LEVEL SECURITY")
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    DROP POLICY IF EXISTS notifications_self_select ON notifications;
                    DROP POLICY IF EXISTS notifications_self_update ON notifications;

                    CREATE POLICY notifications_self_select ON notifications
                        FOR SELECT
                        USING (user_id = (SELECT auth.uid()::text));

                    CREATE POLICY notifications_self_update ON notifications
                        FOR UPDATE
                        USING (user_id = (SELECT auth.uid()::text));
                END IF;
            END
            $$;
        """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    DROP POLICY IF EXISTS notifications_self_select ON notifications;
                    DROP POLICY IF EXISTS notifications_self_update ON notifications;
                END IF;
            END
            $$;
        """)

    op.drop_constraint("uq_notifications_event_user", table_name="notifications", type_="unique")
    op.drop_index("ix_notifications_event_id", table_name="notifications")
    op.drop_index("ix_notifications_user_created", table_name="notifications")
    op.drop_index("ix_notifications_user_unread", table_name="notifications")
    op.drop_table("notifications")
