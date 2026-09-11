"""
GrowFlow — Project Definition Service Implementation.

Manages reusable mentor project templates, immutable version snapshots,
and assignment workflows to independent student project instances.

Architecture ref:
  6A § 9 — Class-Based Architecture
  6B § 7.1 — project_definitions
  6B § 7.2 — project_definition_versions
  6C § 12 — Project Definition APIs
  6H § 6 — ProjectDefinitionCreated, ProjectDefinitionAssigned events
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectDefinitionStatus,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    NotFoundException,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime
    import uuid

    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import (
        ProjectDefinitionModel,
        ProjectDefinitionVersionModel,
        ProjectInstanceModel,
    )
    from backend.app.infrastructure.repositories.project_definition_repository import (
        ProjectDefinitionRepository,
    )
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository


class ProjectDefinitionService:
    """Application service managing reusable project definitions and version immutability."""

    def __init__(
        self,
        definition_repo: ProjectDefinitionRepository,
        project_repo: ProjectRepository,
        outbox_service: OutboxService,
    ) -> None:
        self._definition_repo = definition_repo
        self._project_repo = project_repo
        self._outbox_service = outbox_service

    async def create_definition(
        self,
        mentor_id: uuid.UUID,
        name: str,
        problem: str,
        proposed_solution: str,
        *,
        complexity: str = ProjectComplexity.INTERMEDIATE.value,
        description: str = "",
        duration: str = "",
        constraints: str = "",
        assumptions: str = "",
        technology_snapshot: list[dict[str, Any]] | None = None,
        correlation_id: str = "",
    ) -> tuple[ProjectDefinitionModel, ProjectDefinitionVersionModel]:
        # 1. Create definition container
        definition = await self._definition_repo.create_definition(
            owner_mentor_id=mentor_id,
            name=name,
            status=ProjectDefinitionStatus.ACTIVE.value,
        )

        # 2. Create version 1 immutable snapshot
        version = await self._definition_repo.create_version(
            project_definition_id=definition.id,
            name=name,
            problem=problem,
            proposed_solution=proposed_solution,
            created_by=mentor_id,
            complexity=complexity,
            description=description,
            duration=duration,
            constraints=constraints,
            assumptions=assumptions,
            technology_snapshot=technology_snapshot,
        )

        # 3. Emit Domain Event
        await self._outbox_service.emit(
            event_type=DomainEventType.PROJECT_DEFINITION_CREATED.value,
            actor_role="MENTOR",
            resource_type="project_definition",
            resource_id=str(definition.id),
            actor_id=mentor_id,
            metadata={
                "definition_name": definition.name,
                "version_number": version.version_number,
                "complexity": version.complexity,
            },
            correlation_id=correlation_id,
        )

        return definition, version

    async def list_definitions(
        self,
        mentor_id: uuid.UUID,
        status: str | None = None,
    ) -> Sequence[ProjectDefinitionModel]:
        return await self._definition_repo.list_by_mentor(mentor_id, status=status)

    async def get_definition(
        self,
        definition_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> tuple[ProjectDefinitionModel, ProjectDefinitionVersionModel | None]:
        definition = await self._definition_repo.get_by_id(definition_id)
        if definition is None:
            raise NotFoundException(
                "Project definition not found.", code="PROJECT_DEFINITION_NOT_FOUND"
            )

        if not current_user.is_admin and str(definition.owner_mentor_id) != str(
            current_user.user_id
        ):
            raise AuthorizationException(
                "Access to this project definition is denied.", code="AUTH_FORBIDDEN_RESOURCE"
            )

        current_ver = None
        if definition.current_version_id:
            current_ver = await self._definition_repo.get_version_by_id(
                definition.current_version_id
            )

        return definition, current_ver

    async def update_definition(
        self,
        definition_id: uuid.UUID,
        current_user: CurrentUser,
        *,
        name: str | None = None,
        problem: str | None = None,
        proposed_solution: str | None = None,
        complexity: str | None = None,
        description: str | None = None,
        duration: str | None = None,
        constraints: str | None = None,
        assumptions: str | None = None,
        technology_snapshot: list[dict[str, Any]] | None = None,
    ) -> tuple[ProjectDefinitionModel, ProjectDefinitionVersionModel]:
        definition, current_ver = await self.get_definition(definition_id, current_user)
        if definition.status == ProjectDefinitionStatus.ARCHIVED.value:
            raise BusinessRuleException(
                "Cannot update an archived project definition.",
                code="PROJECT_DEFINITION_ARCHIVED",
            )

        if name is not None:
            definition.name = name.strip()

        # Build fields for new version, defaulting to current version values if not provided
        v_name = name.strip() if name is not None else definition.name
        v_problem = (
            problem.strip() if problem is not None else (current_ver.problem if current_ver else "")
        )
        v_solution = (
            proposed_solution.strip()
            if proposed_solution is not None
            else (current_ver.proposed_solution if current_ver else "")
        )
        v_complexity = (
            complexity
            if complexity is not None
            else (current_ver.complexity if current_ver else ProjectComplexity.INTERMEDIATE.value)
        )
        v_desc = (
            description.strip()
            if description is not None
            else (current_ver.description if current_ver else "")
        )
        v_duration = (
            duration.strip()
            if duration is not None
            else (current_ver.duration if current_ver else "")
        )
        v_constraints = (
            constraints.strip()
            if constraints is not None
            else (current_ver.constraints if current_ver else "")
        )
        v_assumptions = (
            assumptions.strip()
            if assumptions is not None
            else (current_ver.assumptions if current_ver else "")
        )
        v_tech = (
            technology_snapshot
            if technology_snapshot is not None
            else (current_ver.technology_snapshot if current_ver else [])
        )

        # Create new version snapshot (preserving existing version immutability)
        new_version = await self._definition_repo.create_version(
            project_definition_id=definition.id,
            name=v_name,
            problem=v_problem,
            proposed_solution=v_solution,
            created_by=current_user.user_id,
            complexity=v_complexity,
            description=v_desc,
            duration=v_duration,
            constraints=v_constraints,
            assumptions=v_assumptions,
            technology_snapshot=v_tech,
        )

        return definition, new_version

    async def archive_definition(
        self,
        definition_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> ProjectDefinitionModel:
        definition, _ = await self.get_definition(definition_id, current_user)
        definition.status = ProjectDefinitionStatus.ARCHIVED.value
        return definition

    async def list_versions(
        self,
        definition_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> Sequence[ProjectDefinitionVersionModel]:
        await self.get_definition(definition_id, current_user)
        return await self._definition_repo.list_versions(definition_id)

    async def get_version(
        self,
        definition_id: uuid.UUID,
        version_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> ProjectDefinitionVersionModel:
        await self.get_definition(definition_id, current_user)
        version = await self._definition_repo.get_version_by_id(version_id)
        if version is None or str(version.project_definition_id) != str(definition_id):
            raise NotFoundException("Definition version not found.", code="VERSION_NOT_FOUND")
        return version

    async def assign_definition(
        self,
        definition_id: uuid.UUID,
        mentor_user: CurrentUser,
        student_id: uuid.UUID,
        *,
        group_id: uuid.UUID | None = None,
        deadline: datetime | None = None,
        correlation_id: str = "",
    ) -> ProjectInstanceModel:
        definition, current_ver = await self.get_definition(definition_id, mentor_user)
        if definition.status == ProjectDefinitionStatus.ARCHIVED.value:
            raise BusinessRuleException(
                "Cannot assign an archived project definition.",
                code="PROJECT_DEFINITION_ARCHIVED",
            )

        if current_ver is None:
            raise BusinessRuleException(
                "Project definition has no active version snapshot.",
                code="PROJECT_DEFINITION_NO_VERSION",
            )

        # Create independent student project instance
        project_instance = await self._project_repo.create_project_instance(
            student_id=student_id,
            name=current_ver.name,
            problem=current_ver.problem,
            proposed_solution=current_ver.proposed_solution,
            complexity=current_ver.complexity,
            group_id=group_id,
            project_definition_id=definition.id,
            source_definition_version_id=current_ver.id,
            deadline=deadline,
            current_phase=ProjectPhase.IDEA.value,
            health=ProjectHealth.HEALTHY.value,
            status=ProjectStatus.ACTIVE.value,
        )

        # Create structured project profile populated from the snapshot
        await self._project_repo.create_or_update_profile(
            project_instance_id=project_instance.id,
            objective=current_ver.description,
            constraints=current_ver.constraints,
            assumptions=current_ver.assumptions,
            scope=current_ver.problem,
            expected_outcome=current_ver.proposed_solution,
        )

        # Emit events
        await self._outbox_service.emit(
            event_type=DomainEventType.PROJECT_DEFINITION_ASSIGNED.value,
            actor_role="MENTOR",
            resource_type="project_definition",
            resource_id=str(definition.id),
            actor_id=mentor_user.user_id,
            project_instance_id=project_instance.id,
            group_id=group_id,
            metadata={
                "student_id": str(student_id),
                "definition_id": str(definition.id),
                "version_number": current_ver.version_number,
            },
            correlation_id=correlation_id,
        )

        await self._outbox_service.emit(
            event_type=DomainEventType.PROJECT_CREATED.value,
            actor_role="MENTOR",
            resource_type="project_instance",
            resource_id=str(project_instance.id),
            actor_id=mentor_user.user_id,
            project_instance_id=project_instance.id,
            group_id=group_id,
            metadata={
                "project_name": project_instance.name,
                "assigned_from_definition": True,
            },
            correlation_id=correlation_id,
        )

        return project_instance
