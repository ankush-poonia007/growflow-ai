"""
GrowFlow — Project Repository Implementation.

Provides persistence operations for:
- project_instances
- project_profiles
- project_technologies
- project_phase_history
- project_health_history

Architecture ref:
  6A § 7 — Repository Architecture
  6B § 7.3 — project_instances
  6B § 10.1 — project_profiles
  6B § 11.1 — project_technologies
  6B § 20 & § 44 — project_phase_history
  6B § 21 & § 43 — project_health_history
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import select

from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.infrastructure.database.models.organization import GroupModel
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
    ProjectHealthHistoryModel,
    ProjectInstanceModel,
    ProjectPhaseHistoryModel,
    ProjectProfileModel,
    ProjectTechnologyModel,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession


class ProjectRepository(BaseRepository[ProjectInstanceModel]):
    """Repository managing student project instances and associated structured domain state."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectInstanceModel)

    async def list_by_student(
        self, student_id: uuid.UUID | str, status: str | None = None
    ) -> Sequence[ProjectInstanceModel]:
        stmt = select(ProjectInstanceModel).where(
            ProjectInstanceModel.student_id == str(student_id)
        )
        if status:
            stmt = stmt.where(ProjectInstanceModel.status == status)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_group(
        self, group_id: uuid.UUID | str, status: str | None = None
    ) -> Sequence[ProjectInstanceModel]:
        stmt = select(ProjectInstanceModel).where(ProjectInstanceModel.group_id == str(group_id))
        if status:
            stmt = stmt.where(ProjectInstanceModel.status == status)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_active_by_student_and_definition(
        self,
        student_id: uuid.UUID | str,
        project_definition_id: uuid.UUID | str,
    ) -> ProjectInstanceModel | None:
        """Retrieve an active project instance linked to the given student and project definition."""
        stmt = select(ProjectInstanceModel).where(
            ProjectInstanceModel.student_id == str(student_id),
            ProjectInstanceModel.project_definition_id == str(project_definition_id),
            ProjectInstanceModel.status == ProjectStatus.ACTIVE.value,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def lock_student_for_update(self, student_id: uuid.UUID | str) -> None:
        """Acquire a row-level lock on the student user record to serialize concurrent selections."""
        stmt = select(UserModel.id).where(UserModel.id == str(student_id)).with_for_update()
        await self._session.execute(stmt)

    async def create_project_instance(
        self,
        student_id: uuid.UUID | str,
        name: str,
        *,
        problem: str = "",
        proposed_solution: str = "",
        complexity: str = ProjectComplexity.INTERMEDIATE.value,
        group_id: uuid.UUID | str | None = None,
        project_definition_id: uuid.UUID | str | None = None,
        source_definition_version_id: uuid.UUID | str | None = None,
        deadline: datetime | None = None,
        current_phase: str = ProjectPhase.IDEA.value,
        health: str = ProjectHealth.HEALTHY.value,
        status: str = ProjectStatus.ACTIVE.value,
    ) -> ProjectInstanceModel:
        project = ProjectInstanceModel(
            id=str(uuid.uuid4()),
            student_id=str(student_id),
            group_id=str(group_id) if group_id else None,
            project_definition_id=str(project_definition_id) if project_definition_id else None,
            source_definition_version_id=str(source_definition_version_id)
            if source_definition_version_id
            else None,
            name=name.strip(),
            problem=problem.strip(),
            proposed_solution=proposed_solution.strip(),
            complexity=complexity,
            current_phase=current_phase,
            health=health,
            progress_percentage=0,
            status=status,
            deadline=deadline,
        )
        return await self.add(project)

    async def get_profile(self, project_instance_id: uuid.UUID | str) -> ProjectProfileModel | None:
        result = await self._session.execute(
            select(ProjectProfileModel).where(
                ProjectProfileModel.project_instance_id == str(project_instance_id)
            )
        )
        return result.scalar_one_or_none()

    async def create_or_update_profile(
        self,
        project_instance_id: uuid.UUID | str,
        *,
        objective: str | None = None,
        target_users: str | None = None,
        project_type: str | None = None,
        student_skill_context: str | None = None,
        goals: str | None = None,
        scope: str | None = None,
        expected_outcome: str | None = None,
        constraints: str | None = None,
        assumptions: str | None = None,
        context: str | None = None,
    ) -> ProjectProfileModel:
        profile = await self.get_profile(project_instance_id)
        if profile is None:
            profile = ProjectProfileModel(
                id=str(uuid.uuid4()),
                project_instance_id=str(project_instance_id),
                objective=objective or "",
                target_users=target_users or "",
                project_type=project_type or "",
                student_skill_context=student_skill_context or "",
                goals=goals or "",
                scope=scope or "",
                expected_outcome=expected_outcome or "",
                constraints=constraints or "",
                assumptions=assumptions or "",
                context=context or "",
                version=1,
            )
            self._session.add(profile)
        else:
            if objective is not None:
                profile.objective = objective
            if target_users is not None:
                profile.target_users = target_users
            if project_type is not None:
                profile.project_type = project_type
            if student_skill_context is not None:
                profile.student_skill_context = student_skill_context
            if goals is not None:
                profile.goals = goals
            if scope is not None:
                profile.scope = scope
            if expected_outcome is not None:
                profile.expected_outcome = expected_outcome
            if constraints is not None:
                profile.constraints = constraints
            if assumptions is not None:
                profile.assumptions = assumptions
            if context is not None:
                profile.context = context
            profile.version += 1

        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def list_technologies(
        self, project_instance_id: uuid.UUID | str
    ) -> Sequence[ProjectTechnologyModel]:
        result = await self._session.execute(
            select(ProjectTechnologyModel).where(
                ProjectTechnologyModel.project_instance_id == str(project_instance_id)
            )
        )
        return result.scalars().all()

    async def add_technology(
        self,
        project_instance_id: uuid.UUID | str,
        technology_id: uuid.UUID | str,
        *,
        category: str = "",
        purpose: str = "",
        why_selected: str = "",
        appropriateness: str = "",
        student_understanding: str = "",
        usage_context: str = "",
    ) -> ProjectTechnologyModel:
        # Check if already added
        result = await self._session.execute(
            select(ProjectTechnologyModel).where(
                ProjectTechnologyModel.project_instance_id == str(project_instance_id),
                ProjectTechnologyModel.technology_id == str(technology_id),
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            existing.category = category
            existing.purpose = purpose
            existing.why_selected = why_selected
            existing.appropriateness = appropriateness
            existing.student_understanding = student_understanding
            existing.usage_context = usage_context
            await self._session.flush()
            await self._session.refresh(existing)
            return existing

        item = ProjectTechnologyModel(
            id=uuid.uuid4(),
            project_instance_id=str(project_instance_id),
            technology_id=str(technology_id),
            category=category,
            purpose=purpose,
            why_selected=why_selected,
            appropriateness=appropriateness,
            student_understanding=student_understanding,
            usage_context=usage_context,
        )
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def record_phase_transition(
        self,
        project_instance_id: uuid.UUID | str,
        *,
        previous_phase: str,
        new_phase: str,
        changed_by: uuid.UUID | str,
        reason: str = "",
    ) -> ProjectPhaseHistoryModel:
        history = ProjectPhaseHistoryModel(
            id=uuid.uuid4(),
            project_instance_id=str(project_instance_id),
            previous_phase=previous_phase,
            new_phase=new_phase,
            changed_by=str(changed_by),
            reason=reason.strip(),
        )
        self._session.add(history)
        await self._session.flush()
        await self._session.refresh(history)
        return history

    async def list_phase_history(
        self, project_instance_id: uuid.UUID | str
    ) -> Sequence[ProjectPhaseHistoryModel]:
        result = await self._session.execute(
            select(ProjectPhaseHistoryModel)
            .where(ProjectPhaseHistoryModel.project_instance_id == str(project_instance_id))
            .order_by(ProjectPhaseHistoryModel.changed_at.desc())
        )
        return result.scalars().all()

    async def record_health_transition(
        self,
        project_instance_id: uuid.UUID | str,
        *,
        previous_health: str,
        new_health: str,
        changed_by: uuid.UUID | str,
        reason: str = "",
    ) -> ProjectHealthHistoryModel:
        history = ProjectHealthHistoryModel(
            id=uuid.uuid4(),
            project_instance_id=str(project_instance_id),
            previous_health=previous_health,
            new_health=new_health,
            changed_by=str(changed_by),
            reason=reason.strip(),
        )
        self._session.add(history)
        await self._session.flush()
        await self._session.refresh(history)
        return history

    async def list_health_history(
        self, project_instance_id: uuid.UUID | str
    ) -> Sequence[ProjectHealthHistoryModel]:
        result = await self._session.execute(
            select(ProjectHealthHistoryModel)
            .where(ProjectHealthHistoryModel.project_instance_id == str(project_instance_id))
            .order_by(ProjectHealthHistoryModel.changed_at.desc())
        )
        return result.scalars().all()

    async def list_supervised_projects(
        self,
        group_ids: Sequence[uuid.UUID | str],
        *,
        group_id: uuid.UUID | str | None = None,
        phase: str | None = None,
        health: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> Sequence[
        tuple[
            ProjectInstanceModel,
            UserModel,
            GroupModel | None,
            ProjectDefinitionModel | None,
            ProjectDefinitionVersionModel | None,
        ]
    ]:
        """List projects belonging to supervised groups with eager-joined student, group, and definition snapshot metadata."""
        if not group_ids:
            return []

        stmt = (
            select(
                ProjectInstanceModel,
                UserModel,
                GroupModel,
                ProjectDefinitionModel,
                ProjectDefinitionVersionModel,
            )
            .join(UserModel, UserModel.id == ProjectInstanceModel.student_id)
            .outerjoin(GroupModel, GroupModel.id == ProjectInstanceModel.group_id)
            .outerjoin(
                ProjectDefinitionModel,
                ProjectDefinitionModel.id == ProjectInstanceModel.project_definition_id,
            )
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionVersionModel.id == ProjectInstanceModel.source_definition_version_id,
            )
            .where(ProjectInstanceModel.group_id.in_([str(g) for g in group_ids]))
        )
        if group_id:
            stmt = stmt.where(ProjectInstanceModel.group_id == str(group_id))
        if phase:
            stmt = stmt.where(ProjectInstanceModel.current_phase == phase)
        if health:
            stmt = stmt.where(ProjectInstanceModel.health == health)
        if status:
            stmt = stmt.where(ProjectInstanceModel.status == status)
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                ProjectInstanceModel.name.ilike(term)
                | UserModel.full_name.ilike(term)
                | UserModel.email.ilike(term)
            )
        stmt = stmt.order_by(ProjectInstanceModel.updated_at.desc())
        result = await self._session.execute(stmt)
        return result.all()  # type: ignore[return-value]

    async def get_supervised_project_detail(
        self,
        project_id: uuid.UUID | str,
    ) -> tuple[
        ProjectInstanceModel,
        UserModel,
        GroupModel | None,
        ProjectDefinitionModel | None,
        ProjectDefinitionVersionModel | None,
        ProjectProfileModel | None,
    ] | None:
        """Fetch project instance detail with student, group, definition, version snapshot, and profile."""
        stmt = (
            select(
                ProjectInstanceModel,
                UserModel,
                GroupModel,
                ProjectDefinitionModel,
                ProjectDefinitionVersionModel,
                ProjectProfileModel,
            )
            .join(UserModel, UserModel.id == ProjectInstanceModel.student_id)
            .outerjoin(GroupModel, GroupModel.id == ProjectInstanceModel.group_id)
            .outerjoin(
                ProjectDefinitionModel,
                ProjectDefinitionModel.id == ProjectInstanceModel.project_definition_id,
            )
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionVersionModel.id == ProjectInstanceModel.source_definition_version_id,
            )
            .outerjoin(
                ProjectProfileModel,
                ProjectProfileModel.project_instance_id == ProjectInstanceModel.id,
            )
            .where(ProjectInstanceModel.id == str(project_id))
        )
        result = await self._session.execute(stmt)
        return result.first()  # type: ignore[return-value]

    async def list_at_risk_projects(
        self,
        group_ids: Sequence[uuid.UUID | str],
        *,
        group_id: uuid.UUID | str | None = None,
        health: str | None = None,
    ) -> Sequence[
        tuple[
            ProjectInstanceModel,
            UserModel,
            GroupModel | None,
            ProjectDefinitionModel | None,
            ProjectDefinitionVersionModel | None,
        ]
    ]:
        """List at-risk (WARNING and CRITICAL only) projects across supervised groups."""
        if not group_ids:
            return []

        target_health = [ProjectHealth.WARNING.value, ProjectHealth.CRITICAL.value]
        if health:
            if health in target_health:
                target_health = [health]
            else:
                return []

        stmt = (
            select(
                ProjectInstanceModel,
                UserModel,
                GroupModel,
                ProjectDefinitionModel,
                ProjectDefinitionVersionModel,
            )
            .join(UserModel, UserModel.id == ProjectInstanceModel.student_id)
            .outerjoin(GroupModel, GroupModel.id == ProjectInstanceModel.group_id)
            .outerjoin(
                ProjectDefinitionModel,
                ProjectDefinitionModel.id == ProjectInstanceModel.project_definition_id,
            )
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionVersionModel.id == ProjectInstanceModel.source_definition_version_id,
            )
            .where(
                ProjectInstanceModel.group_id.in_([str(g) for g in group_ids]),
                ProjectInstanceModel.health.in_(target_health),
            )
        )
        if group_id:
            stmt = stmt.where(ProjectInstanceModel.group_id == str(group_id))

        stmt = stmt.order_by(
            (ProjectInstanceModel.health == ProjectHealth.CRITICAL.value).desc(),
            ProjectInstanceModel.updated_at.desc(),
        )
        result = await self._session.execute(stmt)
        return result.all()  # type: ignore[return-value]

