"""Gate 09: add generation_number, cancellation, and agent_executions provenance table.

Revision ID: 0011_gate09_agent_executions
Revises: 0010_gate08_question_templates
Create Date: 2026-09-20 UTC

Authorised by: Gate 09 — AI Blueprint & Agent System
Architecture ref:
  6B § 27.2 — agent_executions
  6E § 31   — Execution Provenance Tracking
  6F § 37   — Version Preservation & generation_number
  6F § 40   — Execution Lifecycle & Cancellation
  6H § 39   — Cancellation Safety
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic (<= 32 chars for alembic_version column limit).
revision: str = "0011_gate09_agent_executions"
down_revision: str | None = "0010_gate08_question_templates"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Update blueprints table
    # ---------------------------------------------------------
    op.add_column(
        "blueprints",
        sa.Column("generation_number", sa.Integer(), nullable=False, server_default="1"),
    )

    # ---------------------------------------------------------
    # 2. Update blueprint_jobs table
    # ---------------------------------------------------------
    op.add_column(
        "blueprint_jobs",
        sa.Column("generation_number", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "blueprint_jobs",
        sa.Column(
            "cancellation_requested",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "blueprint_jobs",
        sa.Column("locked_by", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "blueprint_jobs",
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ---------------------------------------------------------
    # 3. Create agent_executions table
    # ---------------------------------------------------------
    op.create_table(
        "agent_executions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("blueprint_job_id", sa.String(length=36), nullable=False),
        sa.Column("blueprint_id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("execution_id", sa.String(length=36), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("agent_version", sa.String(length=20), nullable=False),
        sa.Column("prompt_version", sa.String(length=20), nullable=False),
        sa.Column("contract_version", sa.String(length=20), nullable=False),
        sa.Column("generation_number", sa.Integer(), nullable=False),
        sa.Column(
            "regeneration_attempt",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("key_alias", sa.String(length=50), nullable=False),
        sa.Column("capability", sa.String(length=50), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column(
            "prompt_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "completion_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "estimated_cost_usd",
            sa.Numeric(precision=10, scale=6),
            nullable=False,
            server_default="0.0",
        ),
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["blueprint_job_id"],
            ["blueprint_jobs.id"],
            name=op.f("fk_agent_executions_blueprint_job_id_blueprint_jobs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["blueprint_id"],
            ["blueprints.id"],
            name=op.f("fk_agent_executions_blueprint_id_blueprints"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_agent_executions_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_executions")),
    )

    op.create_index(
        op.f("ix_agent_executions_blueprint_job_id"),
        "agent_executions",
        ["blueprint_job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_executions_blueprint_id"),
        "agent_executions",
        ["blueprint_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_executions_project_instance_id"),
        "agent_executions",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_executions_execution_id"),
        "agent_executions",
        ["execution_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 4. PostgreSQL Row Level Security (RLS)
    # ---------------------------------------------------------
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY")
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    DROP POLICY IF EXISTS agent_executions_select ON agent_executions;
                    CREATE POLICY agent_executions_select ON agent_executions
                        FOR SELECT
                        USING (
                            EXISTS (
                                SELECT 1 FROM project_instances pi
                                WHERE pi.id = agent_executions.project_instance_id
                                AND (
                                    pi.student_id = auth.uid()::text
                                    OR EXISTS (
                                        SELECT 1 FROM users u
                                        WHERE u.id = auth.uid()::text
                                        AND u.role = 'ADMIN'
                                    )
                                )
                            )
                        );
                END IF;
            END $$;
        """)


def downgrade() -> None:
    op.drop_index(
        op.f("ix_agent_executions_execution_id"),
        table_name="agent_executions",
    )
    op.drop_index(
        op.f("ix_agent_executions_project_instance_id"),
        table_name="agent_executions",
    )
    op.drop_index(
        op.f("ix_agent_executions_blueprint_id"),
        table_name="agent_executions",
    )
    op.drop_index(
        op.f("ix_agent_executions_blueprint_job_id"),
        table_name="agent_executions",
    )
    op.drop_table("agent_executions")

    op.drop_column("blueprint_jobs", "locked_at")
    op.drop_column("blueprint_jobs", "locked_by")
    op.drop_column("blueprint_jobs", "cancellation_requested")
    op.drop_column("blueprint_jobs", "generation_number")

    op.drop_column("blueprints", "generation_number")
