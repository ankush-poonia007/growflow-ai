"""Gate 11: create workspace extensions tables (GitHub, blueprint versions, change requests, AI mentor, help requests, mentor notes).

Revision ID: 0007_gate11_extensions
Revises: 0006_gate10_execution_management
Create Date: 2026-09-13 UTC

Authorised by: Gate 11 — Integrations, Communication & Project Changes
Architecture ref:
  Batch 6 — Student Build Workspace Final Slice (S27–S33)
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic (<= 32 chars for alembic_version column limit).
revision: str = "0007_gate11_extensions"
down_revision: str | None = "0006_gate10_execution_management"
branch_labels: str | None = None
depends_on: str | None = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. project_github_integrations
    # ---------------------------------------------------------
    op.create_table(
        "project_github_integrations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("repository_name", sa.String(length=255), nullable=False),
        sa.Column("repository_url", sa.String(length=500), nullable=False),
        sa.Column("connection_status", sa.String(length=50), nullable=False, server_default="NOT_CONNECTED"),
        sa.Column("default_branch", sa.String(length=100), nullable=False, server_default="main"),
        sa.Column("commit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_error", sa.Text(), nullable=True),
        sa.Column("cached_commits_preview", JSON_TYPE, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_github_integrations_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_github_integrations")),
        sa.UniqueConstraint("project_instance_id", name="uq_project_github_integrations_project_instance_id"),
    )
    op.create_index(
        op.f("ix_project_github_integrations_project_instance_id"),
        "project_github_integrations",
        ["project_instance_id"],
        unique=True,
    )

    # ---------------------------------------------------------
    # 2. project_blueprint_versions
    # ---------------------------------------------------------
    op.create_table(
        "project_blueprint_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("blueprint_id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="APPROVED"),
        sa.Column("content", JSON_TYPE, nullable=False),
        sa.Column("qa_score", sa.Integer(), nullable=True),
        sa.Column("qa_feedback", JSON_TYPE, nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["blueprint_id"],
            ["blueprints.id"],
            name=op.f("fk_project_blueprint_versions_blueprint_id_blueprints"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_blueprint_versions_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_blueprint_versions")),
        sa.UniqueConstraint("blueprint_id", "version_number", name="uq_project_blueprint_version"),
    )
    op.create_index(
        op.f("ix_project_blueprint_versions_blueprint_id"),
        "project_blueprint_versions",
        ["blueprint_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_blueprint_versions_project_instance_id"),
        "project_blueprint_versions",
        ["project_instance_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 3. project_change_requests
    # ---------------------------------------------------------
    op.create_table(
        "project_change_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("change_title", sa.String(length=255), nullable=False),
        sa.Column("change_description", sa.Text(), nullable=False),
        sa.Column("change_type", sa.String(length=50), nullable=False, server_default="SCOPE"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ANALYZED"),
        sa.Column("idempotency_key", sa.String(length=100), nullable=True),
        sa.Column("impact_analysis", JSON_TYPE, nullable=False),
        sa.Column("source_blueprint_version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("resulting_blueprint_version_number", sa.Integer(), nullable=True),
        sa.Column("qa_score", sa.Integer(), nullable=True),
        sa.Column("qa_feedback", JSON_TYPE, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_change_requests_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_project_change_requests_student_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_change_requests")),
    )
    op.create_index(
        op.f("ix_project_change_requests_project_instance_id"),
        "project_change_requests",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_change_requests_student_id"),
        "project_change_requests",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_change_requests_idempotency_key"),
        "project_change_requests",
        ["idempotency_key"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 4. ai_mentor_conversations
    # ---------------------------------------------------------
    op.create_table(
        "ai_mentor_conversations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, server_default="Project Consultation"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_ai_mentor_conversations_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_ai_mentor_conversations_student_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_mentor_conversations")),
    )
    op.create_index(
        op.f("ix_ai_mentor_conversations_project_instance_id"),
        "ai_mentor_conversations",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_mentor_conversations_student_id"),
        "ai_mentor_conversations",
        ["student_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 5. ai_mentor_messages
    # ---------------------------------------------------------
    op.create_table(
        "ai_mentor_messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sources", JSON_TYPE, nullable=False, server_default="[]"),
        sa.Column("suggested_action", JSON_TYPE, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["ai_mentor_conversations.id"],
            name=op.f("fk_ai_mentor_messages_conversation_id_ai_mentor_conversations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_mentor_messages")),
    )
    op.create_index(
        op.f("ix_ai_mentor_messages_conversation_id"),
        "ai_mentor_messages",
        ["conversation_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 6. project_help_requests
    # ---------------------------------------------------------
    op.create_table(
        "project_help_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="TECHNICAL"),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="OPEN"),
        sa.Column("mentor_response", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_help_requests_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_project_help_requests_student_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_help_requests")),
    )
    op.create_index(
        op.f("ix_project_help_requests_project_instance_id"),
        "project_help_requests",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_help_requests_student_id"),
        "project_help_requests",
        ["student_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 7. project_mentor_notes
    # ---------------------------------------------------------
    op.create_table(
        "project_mentor_notes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("mentor_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("note_type", sa.String(length=50), nullable=False, server_default="INFORMATIONAL"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="UNREAD"),
        sa.Column("related_resource_type", sa.String(length=50), nullable=True),
        sa.Column("related_resource_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_mentor_notes_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["mentor_id"],
            ["users.id"],
            name=op.f("fk_project_mentor_notes_mentor_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_mentor_notes")),
    )
    op.create_index(
        op.f("ix_project_mentor_notes_project_instance_id"),
        "project_mentor_notes",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_mentor_notes_mentor_id"),
        "project_mentor_notes",
        ["mentor_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_project_mentor_notes_mentor_id"), table_name="project_mentor_notes")
    op.drop_index(op.f("ix_project_mentor_notes_project_instance_id"), table_name="project_mentor_notes")
    op.drop_table("project_mentor_notes")

    op.drop_index(op.f("ix_project_help_requests_student_id"), table_name="project_help_requests")
    op.drop_index(op.f("ix_project_help_requests_project_instance_id"), table_name="project_help_requests")
    op.drop_table("project_help_requests")

    op.drop_index(op.f("ix_ai_mentor_messages_conversation_id"), table_name="ai_mentor_messages")
    op.drop_table("ai_mentor_messages")

    op.drop_index(op.f("ix_ai_mentor_conversations_student_id"), table_name="ai_mentor_conversations")
    op.drop_index(op.f("ix_ai_mentor_conversations_project_instance_id"), table_name="ai_mentor_conversations")
    op.drop_table("ai_mentor_conversations")

    op.drop_index(op.f("ix_project_change_requests_idempotency_key"), table_name="project_change_requests")
    op.drop_index(op.f("ix_project_change_requests_student_id"), table_name="project_change_requests")
    op.drop_index(op.f("ix_project_change_requests_project_instance_id"), table_name="project_change_requests")
    op.drop_table("project_change_requests")

    op.drop_index(op.f("ix_project_blueprint_versions_project_instance_id"), table_name="project_blueprint_versions")
    op.drop_index(op.f("ix_project_blueprint_versions_blueprint_id"), table_name="project_blueprint_versions")
    op.drop_table("project_blueprint_versions")

    op.drop_index(op.f("ix_project_github_integrations_project_instance_id"), table_name="project_github_integrations")
    op.drop_table("project_github_integrations")
