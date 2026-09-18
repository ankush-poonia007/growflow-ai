"""Gate 09: create blueprints and blueprint_jobs tables.

Revision ID: 0005_gate09_blueprint
Revises: 0004_gate08_assessment
Create Date: 2026-09-13 UTC

Authorised by: Gate 09 — AI Blueprint & Agent System
Architecture ref:
  6B § 7 — Project Instances
  6N § 18 — AI Provider Gateway
  6N § 20 — Blueprint Agent Graph
  6N § 21 — AI Output Authority Boundary
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0005_gate09_blueprint"
down_revision: str | None = "0004_gate08_assessment"
branch_labels: str | None = None
depends_on: str | None = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. blueprints
    # ---------------------------------------------------------
    op.create_table(
        "blueprints",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="NOT_STARTED"),
        sa.Column("current_step", sa.String(length=100), nullable=True),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("failed_output_key", sa.String(length=100), nullable=True),
        sa.Column("qa_status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("qa_score", sa.Integer(), nullable=True),
        sa.Column("qa_feedback", JSON_TYPE, nullable=True),
        sa.Column("content", JSON_TYPE, nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_blueprints_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_blueprints_student_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_blueprints")),
        sa.UniqueConstraint("project_instance_id", name="uq_blueprints_project_instance"),
    )
    op.create_index(
        op.f("ix_blueprints_project_instance_id"),
        "blueprints",
        ["project_instance_id"],
        unique=True,
    )
    op.create_index(op.f("ix_blueprints_student_id"), "blueprints", ["student_id"], unique=False)
    op.create_index(op.f("ix_blueprints_status"), "blueprints", ["status"], unique=False)

    # ---------------------------------------------------------
    # 2. blueprint_jobs
    # ---------------------------------------------------------
    op.create_table(
        "blueprint_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("blueprint_id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column(
            "job_type",
            sa.String(length=50),
            nullable=False,
            server_default="FULL_GENERATION",
        ),
        sa.Column("target_output", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("current_step", sa.String(length=100), nullable=True),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["blueprint_id"],
            ["blueprints.id"],
            name=op.f("fk_blueprint_jobs_blueprint_id_blueprints"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_blueprint_jobs_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_blueprint_jobs")),
    )
    op.create_index(
        op.f("ix_blueprint_jobs_blueprint_id"),
        "blueprint_jobs",
        ["blueprint_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_blueprint_jobs_project_instance_id"),
        "blueprint_jobs",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_blueprint_jobs_status"),
        "blueprint_jobs",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_blueprint_jobs_status"), table_name="blueprint_jobs")
    op.drop_index(op.f("ix_blueprint_jobs_project_instance_id"), table_name="blueprint_jobs")
    op.drop_index(op.f("ix_blueprint_jobs_blueprint_id"), table_name="blueprint_jobs")
    op.drop_table("blueprint_jobs")

    op.drop_index(op.f("ix_blueprints_status"), table_name="blueprints")
    op.drop_index(op.f("ix_blueprints_student_id"), table_name="blueprints")
    op.drop_index(op.f("ix_blueprints_project_instance_id"), table_name="blueprints")
    op.drop_table("blueprints")
