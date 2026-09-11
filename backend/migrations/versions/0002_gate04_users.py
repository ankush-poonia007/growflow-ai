"""Gate 04: create users table with RLS policy primitives.

Revision ID: 0002_gate04_users
Revises: 0001_gate03_baseline
Create Date: 2026-09-11 UTC

Authorised by: Gate 04 — Authentication & Security Foundation
Architecture ref:
  6B § 5.1 — Canonical users identity table
  6D § 4   — Supabase Auth User UUID linkage
  6D § 33-34 — RLS defense in depth
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_gate04_users"
down_revision: str | None = "0001_gate03_baseline"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create users table and enable RLS with self-access primitives."""
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), server_default="", nullable=False),
        sa.Column("role", sa.String(length=50), server_default="STUDENT", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column("avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )

    # 2. Create indexes
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_status"), "users", ["status"], unique=False)

    # 3. PostgreSQL-specific RLS primitives (safe defense-in-depth)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_self_select'
                    ) THEN
                        CREATE POLICY users_self_select ON users
                            FOR SELECT
                            USING (id = auth.uid()::text);
                    END IF;
                END IF;
            END
            $$;
        """)


def downgrade() -> None:
    """Drop users table and associated policies."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP POLICY IF EXISTS users_self_select ON users")
        op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")

    op.drop_index(op.f("ix_users_status"), table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
