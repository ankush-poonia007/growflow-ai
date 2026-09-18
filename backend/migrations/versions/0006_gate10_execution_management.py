"""Gate 10: create execution management tables (milestones, tasks, risks, documents).

Revision ID: 0006_gate10_execution_management
Revises: 0005_gate09_blueprint
Create Date: 2026-09-13 UTC

Authorised by: Gate 10 — Execution Management Foundation
Architecture ref:
  6B § 20 & § 44 — Phase Progression & History
  6B § 21 & § 43 — Health Model
  Batch 5 — Student Build Execution Management (S18–S26)
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0006_gate10_execution_management"
down_revision: str | None = "0005_gate09_blueprint"
branch_labels: str | None = None
depends_on: str | None = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. project_milestones
    # ---------------------------------------------------------
    op.create_table(
        "project_milestones",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("gate_code", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("target_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="UPCOMING"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deliverables", JSON_TYPE, nullable=False, server_default="[]"),
        sa.Column("section_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_milestones_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_milestones")),
    )
    op.create_index(
        op.f("ix_project_milestones_project_instance_id"),
        "project_milestones",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_milestones_status"),
        "project_milestones",
        ["status"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 2. project_tasks
    # ---------------------------------------------------------
    op.create_table(
        "project_tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("milestone_id", sa.String(length=36), nullable=True),
        sa.Column("task_code", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="TODO"),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("category", sa.String(length=100), nullable=False, server_default=""),
        sa.Column("phase", sa.String(length=50), nullable=False, server_default="PLANNING"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dependencies", JSON_TYPE, nullable=False, server_default="[]"),
        sa.Column("acceptance_criteria", JSON_TYPE, nullable=False, server_default="[]"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_tasks_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["milestone_id"],
            ["project_milestones.id"],
            name=op.f("fk_project_tasks_milestone_id_project_milestones"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_tasks")),
    )
    op.create_index(
        op.f("ix_project_tasks_project_instance_id"),
        "project_tasks",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_milestone_id"),
        "project_tasks",
        ["milestone_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_status"),
        "project_tasks",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_priority"),
        "project_tasks",
        ["priority"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_phase"),
        "project_tasks",
        ["phase"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 3. project_risks
    # ---------------------------------------------------------
    op.create_table(
        "project_risks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("risk_code", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("probability", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("impact", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="OPEN"),
        sa.Column("mitigation", sa.Text(), nullable=False, server_default=""),
        sa.Column("owner", sa.String(length=255), nullable=False, server_default="Student"),
        sa.Column("review_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_risks_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_risks")),
    )
    op.create_index(
        op.f("ix_project_risks_project_instance_id"),
        "project_risks",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_risks_status"),
        "project_risks",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_risks_severity"),
        "project_risks",
        ["severity"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 4. project_documents
    # ---------------------------------------------------------
    op.create_table(
        "project_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("document_key", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("doc_type", sa.String(length=50), nullable=False, server_default="SPECIFICATION"),
        sa.Column("format", sa.String(length=50), nullable=False, server_default="markdown"),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("version", sa.String(length=20), nullable=False, server_default="1.0.0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="BLUEPRINT_GENERATED"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_documents_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_documents")),
    )
    op.create_index(
        op.f("ix_project_documents_project_instance_id"),
        "project_documents",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_documents_document_key"),
        "project_documents",
        ["document_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_documents_doc_type"),
        "project_documents",
        ["doc_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_documents_status"),
        "project_documents",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("project_documents")
    op.drop_table("project_risks")
    op.drop_table("project_tasks")
    op.drop_table("project_milestones")
