"""
GrowFlow — Project SQLAlchemy ORM Models.

Defines ORM mappings for:
- project_definitions
- project_definition_versions
- project_instances
- project_profiles
- project_technologies
- project_phase_history
- project_health_history

Architecture ref:
  6B § 7.1 — project_definitions
  6B § 7.2 — project_definition_versions
  6B § 7.3 — project_instances
  6B § 10.1 — project_profiles
  6B § 11.1 — project_technologies
  6B § 20 & § 44 — project_phase_history
  6B § 21 & § 43 — project_health_history
"""

from __future__ import annotations

from datetime import (  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper
    datetime,
)
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectDefinition,
    ProjectDefinitionStatus,
    ProjectDefinitionVersion,
    ProjectHealth,
    ProjectHealthHistory,
    ProjectInstance,
    ProjectPhase,
    ProjectPhaseHistory,
    ProjectProfile,
    ProjectStatus,
    ProjectTechnology,
)
from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

JSON_TYPE = JSON().with_variant(postgresql.JSONB(), "postgresql")


class ProjectDefinitionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_definitions table."""

    __tablename__ = "project_definitions"

    owner_mentor_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=ProjectDefinitionStatus.DRAFT.value,
        index=True,
        nullable=False,
    )
    current_version_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        default=None,
    )

    def to_domain(self) -> ProjectDefinition:
        return ProjectDefinition(
            id=UUID(str(self.id)),
            owner_mentor_id=UUID(self.owner_mentor_id),
            name=self.name,
            status=ProjectDefinitionStatus(self.status),
            current_version_id=UUID(self.current_version_id) if self.current_version_id else None,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ProjectDefinitionVersionModel(Base, UUIDPrimaryKeyMixin):
    """SQLAlchemy model for project_definition_versions table."""

    __tablename__ = "project_definition_versions"
    __table_args__ = (
        UniqueConstraint(
            "project_definition_id",
            "version_number",
            name="uq_proj_def_version",
        ),
    )

    project_definition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_definitions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    problem: Mapped[str] = mapped_column(Text, default="", nullable=False)
    proposed_solution: Mapped[str] = mapped_column(Text, default="", nullable=False)
    complexity: Mapped[str] = mapped_column(
        String(50),
        default=ProjectComplexity.INTERMEDIATE.value,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    duration: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    constraints: Mapped[str] = mapped_column(Text, default="", nullable=False)
    assumptions: Mapped[str] = mapped_column(Text, default="", nullable=False)
    technology_snapshot: Mapped[list[Any]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    created_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def to_domain(self) -> ProjectDefinitionVersion:
        return ProjectDefinitionVersion(
            id=UUID(str(self.id)),
            project_definition_id=UUID(self.project_definition_id),
            version_number=self.version_number,
            name=self.name,
            problem=self.problem,
            proposed_solution=self.proposed_solution,
            complexity=ProjectComplexity(self.complexity),
            description=self.description,
            duration=self.duration,
            constraints=self.constraints,
            assumptions=self.assumptions,
            technology_snapshot=self.technology_snapshot or [],
            created_by=UUID(self.created_by),
            created_at=self.created_at,
        )


class ProjectInstanceModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_instances table."""

    __tablename__ = "project_instances"
    __table_args__ = (
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_project_progress_range",
        ),
    )

    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    group_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("groups.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )
    project_definition_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("project_definitions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )
    source_definition_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("project_definition_versions.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    problem: Mapped[str] = mapped_column(Text, default="", nullable=False)
    proposed_solution: Mapped[str] = mapped_column(Text, default="", nullable=False)
    complexity: Mapped[str] = mapped_column(
        String(50),
        default=ProjectComplexity.INTERMEDIATE.value,
        nullable=False,
    )
    current_phase: Mapped[str] = mapped_column(
        String(50),
        default=ProjectPhase.IDEA.value,
        index=True,
        nullable=False,
    )
    health: Mapped[str] = mapped_column(
        String(50),
        default=ProjectHealth.HEALTHY.value,
        index=True,
        nullable=False,
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    @property
    def progress_percent(self) -> int:
        return self.progress_percentage

    @progress_percent.setter
    def progress_percent(self, val: int) -> None:
        self.progress_percentage = val

    status: Mapped[str] = mapped_column(
        String(50),
        default=ProjectStatus.ACTIVE.value,
        index=True,
        nullable=False,
    )
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def to_domain(self) -> ProjectInstance:
        return ProjectInstance(
            id=UUID(str(self.id)),
            student_id=UUID(self.student_id),
            group_id=UUID(self.group_id) if self.group_id else None,
            project_definition_id=UUID(self.project_definition_id)
            if self.project_definition_id
            else None,
            source_definition_version_id=UUID(self.source_definition_version_id)
            if self.source_definition_version_id
            else None,
            name=self.name,
            problem=self.problem,
            proposed_solution=self.proposed_solution,
            complexity=ProjectComplexity(self.complexity),
            current_phase=ProjectPhase(self.current_phase),
            health=ProjectHealth(self.health),
            progress_percentage=self.progress_percentage,
            status=ProjectStatus(self.status),
            deadline=self.deadline,
            started_at=self.started_at,
            completed_at=self.completed_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ProjectProfileModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_profiles table."""

    __tablename__ = "project_profiles"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    objective: Mapped[str] = mapped_column(Text, default="", nullable=False)
    target_users: Mapped[str] = mapped_column(Text, default="", nullable=False)
    project_type: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    student_skill_context: Mapped[str] = mapped_column(Text, default="", nullable=False)
    goals: Mapped[str] = mapped_column(Text, default="", nullable=False)
    scope: Mapped[str] = mapped_column(Text, default="", nullable=False)
    expected_outcome: Mapped[str] = mapped_column(Text, default="", nullable=False)
    constraints: Mapped[str] = mapped_column(Text, default="", nullable=False)
    assumptions: Mapped[str] = mapped_column(Text, default="", nullable=False)
    context: Mapped[str] = mapped_column(Text, default="", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    def to_domain(self) -> ProjectProfile:
        return ProjectProfile(
            id=UUID(str(self.id)),
            project_instance_id=UUID(self.project_instance_id),
            objective=self.objective,
            target_users=self.target_users,
            project_type=self.project_type,
            student_skill_context=self.student_skill_context,
            goals=self.goals,
            scope=self.scope,
            expected_outcome=self.expected_outcome,
            constraints=self.constraints,
            assumptions=self.assumptions,
            context=self.context,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ProjectTechnologyModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_technologies table."""

    __tablename__ = "project_technologies"
    __table_args__ = (
        UniqueConstraint(
            "project_instance_id",
            "technology_id",
            name="uq_project_technology",
        ),
    )

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    technology_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("technologies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    purpose: Mapped[str] = mapped_column(Text, default="", nullable=False)
    why_selected: Mapped[str] = mapped_column(Text, default="", nullable=False)
    appropriateness: Mapped[str] = mapped_column(Text, default="", nullable=False)
    student_understanding: Mapped[str] = mapped_column(Text, default="", nullable=False)
    usage_context: Mapped[str] = mapped_column(Text, default="", nullable=False)

    def to_domain(self) -> ProjectTechnology:
        return ProjectTechnology(
            id=UUID(str(self.id)),
            project_instance_id=UUID(self.project_instance_id),
            technology_id=UUID(self.technology_id),
            category=self.category,
            purpose=self.purpose,
            why_selected=self.why_selected,
            appropriateness=self.appropriateness,
            student_understanding=self.student_understanding,
            usage_context=self.usage_context,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ProjectPhaseHistoryModel(Base, UUIDPrimaryKeyMixin):
    """SQLAlchemy model for project_phase_history table."""

    __tablename__ = "project_phase_history"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    previous_phase: Mapped[str] = mapped_column(String(50), nullable=False)
    new_phase: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def to_domain(self) -> ProjectPhaseHistory:
        return ProjectPhaseHistory(
            id=UUID(str(self.id)),
            project_instance_id=UUID(self.project_instance_id),
            previous_phase=ProjectPhase(self.previous_phase),
            new_phase=ProjectPhase(self.new_phase),
            changed_by=UUID(self.changed_by),
            reason=self.reason,
            changed_at=self.changed_at,
        )


class ProjectHealthHistoryModel(Base, UUIDPrimaryKeyMixin):
    """SQLAlchemy model for project_health_history table."""

    __tablename__ = "project_health_history"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    previous_health: Mapped[str] = mapped_column(String(50), nullable=False)
    new_health: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def to_domain(self) -> ProjectHealthHistory:
        return ProjectHealthHistory(
            id=UUID(str(self.id)),
            project_instance_id=UUID(self.project_instance_id),
            previous_health=ProjectHealth(self.previous_health),
            new_health=ProjectHealth(self.new_health),
            changed_by=UUID(self.changed_by),
            reason=self.reason,
            changed_at=self.changed_at,
        )
