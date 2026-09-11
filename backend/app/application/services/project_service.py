"""
GrowFlow — Project Service Implementation.

Manages independent student project instances, deterministic lifecycle phase
state machine transitions, health updates, and workspace overview aggregation.

Architecture ref:
  6A § 9  — Class-Based Architecture
  6B § 7.3 — project_instances
  6B § 10 — project_profiles
  6B § 20 & § 44 — project_phase_history & canonical phase model
  6B § 21 & § 43 — project_health_history & health model
  6C § 13 — Project Instance APIs
  6C § 14 — Project Overview API
  6H § 6  — ProjectCreated, ProjectPhaseChanged, ProjectHealthChanged events
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
    can_transition_phase,
)
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    NotFoundException,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    import uuid

    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import (
        ProjectInstanceModel,
    )
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.technology_repository import (
        TechnologyRepository,
    )


class ProjectService:
    """Application service for student project instances and lifecycle orchestration."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        technology_repo: TechnologyRepository,
        outbox_service: OutboxService,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._technology_repo = technology_repo
        self._outbox_service = outbox_service

    async def create_project(
        self,
        student_id: uuid.UUID,
        name: str,
        *,
        problem: str = "",
        proposed_solution: str = "",
        complexity: str = ProjectComplexity.INTERMEDIATE.value,
        technologies: Sequence[uuid.UUID | str] | None = None,
        deadline: datetime | None = None,
        group_id: uuid.UUID | None = None,
        correlation_id: str = "",
    ) -> ProjectInstanceModel:
        # Create project instance initialized in IDEA phase and HEALTHY health
        project = await self._project_repo.create_project_instance(
            student_id=student_id,
            name=name,
            problem=problem,
            proposed_solution=proposed_solution,
            complexity=complexity,
            group_id=group_id,
            deadline=deadline,
            current_phase=ProjectPhase.IDEA.value,
            health=ProjectHealth.HEALTHY.value,
            status=ProjectStatus.ACTIVE.value,
        )

        # Initialize structured project profile
        await self._project_repo.create_or_update_profile(
            project_instance_id=project.id,
            objective=f"Project objective for {project.name}",
            scope=problem,
            expected_outcome=proposed_solution,
        )

        # Link any initial technologies
        if technologies:
            for tech_id in technologies:
                tech = await self._technology_repo.get_by_id(tech_id)
                if tech:
                    await self._project_repo.add_technology(
                        project_instance_id=project.id,
                        technology_id=tech.id,
                        category=tech.category,
                    )

        # Emit ProjectCreated domain event
        await self._outbox_service.emit(
            event_type=DomainEventType.PROJECT_CREATED.value,
            actor_role="STUDENT",
            resource_type="project_instance",
            resource_id=str(project.id),
            actor_id=student_id,
            project_instance_id=project.id,
            group_id=group_id,
            metadata={
                "project_name": project.name,
                "complexity": project.complexity,
                "current_phase": project.current_phase,
            },
            correlation_id=correlation_id,
        )

        return project

    async def get_project(
        self,
        project_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> ProjectInstanceModel:
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise NotFoundException("Project not found.", code="PROJECT_NOT_FOUND")

        # Authorization verification
        if current_user.is_admin:
            return project

        if current_user.is_student and str(project.student_id) == str(current_user.user_id):
            return project

        if current_user.is_mentor and project.group_id:
            group = await self._group_repo.get_by_id(project.group_id)
            if group and str(group.mentor_id) == str(current_user.user_id):
                return project

        raise AuthorizationException(
            "Access to this project is denied.", code="AUTH_FORBIDDEN_RESOURCE"
        )

    async def list_projects_for_user(
        self,
        current_user: CurrentUser,
    ) -> Sequence[ProjectInstanceModel]:
        if current_user.is_student:
            return await self._project_repo.list_by_student(current_user.user_id)

        if current_user.is_mentor:
            # Mentors see projects belonging to groups they supervise
            mentor_groups = await self._group_repo.list_by_mentor(current_user.user_id)
            projects: list[ProjectInstanceModel] = []
            for grp in mentor_groups:
                group_projects = await self._project_repo.list_by_group(grp.id)
                projects.extend(group_projects)
            return projects

        return []

    async def update_project(
        self,
        project_id: uuid.UUID,
        current_user: CurrentUser,
        *,
        name: str | None = None,
        problem: str | None = None,
        proposed_solution: str | None = None,
        complexity: str | None = None,
        deadline: datetime | None = None,
    ) -> ProjectInstanceModel:
        project = await self.get_project(project_id, current_user)

        # Mutating core project properties is reserved for owner student or admin
        if not current_user.is_admin and str(project.student_id) != str(current_user.user_id):
            raise AuthorizationException(
                "Only the project owner may modify project details.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )

        if name is not None:
            project.name = name.strip()
        if problem is not None:
            project.problem = problem.strip()
        if proposed_solution is not None:
            project.proposed_solution = proposed_solution.strip()
        if complexity is not None:
            project.complexity = complexity
        if deadline is not None:
            project.deadline = deadline

        return project

    async def transition_phase(
        self,
        project_id: uuid.UUID,
        current_user: CurrentUser,
        target_phase: str,
        *,
        reason: str = "",
        correlation_id: str = "",
    ) -> ProjectInstanceModel:
        project = await self.get_project(project_id, current_user)

        # Only student owner or admin can transition project phase
        if not current_user.is_admin and str(project.student_id) != str(current_user.user_id):
            raise AuthorizationException(
                "Only the project owner may transition the project phase.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )

        try:
            current_phase_enum = ProjectPhase(project.current_phase)
            target_phase_enum = ProjectPhase(target_phase)
        except ValueError as exc:
            raise BusinessRuleException(
                f"Unknown phase value: {target_phase}.", code="PROJECT_INVALID_PHASE"
            ) from exc

        # Strict sequential state machine check
        if not can_transition_phase(current_phase_enum, target_phase_enum):
            raise BusinessRuleException(
                f"Invalid phase transition from '{project.current_phase}' to '{target_phase}'. "
                "Phase progression must follow the canonical sequence.",
                code="PROJECT_INVALID_PHASE_TRANSITION",
            )

        prev_phase = project.current_phase
        project.current_phase = target_phase_enum.value

        # Record authoritative transition in project_phase_history
        await self._project_repo.record_phase_transition(
            project_instance_id=project.id,
            previous_phase=prev_phase,
            new_phase=target_phase_enum.value,
            changed_by=current_user.user_id,
            reason=reason or f"Transitioned phase to {target_phase_enum.value}",
        )

        # Emit ProjectPhaseChanged domain event
        await self._outbox_service.emit(
            event_type=DomainEventType.PROJECT_PHASE_CHANGED.value,
            actor_role=current_user.role.value,
            resource_type="project_instance",
            resource_id=str(project.id),
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            group_id=project.group_id,
            metadata={
                "previous_phase": prev_phase,
                "new_phase": target_phase_enum.value,
                "reason": reason,
            },
            correlation_id=correlation_id,
        )

        return project

    async def update_health(
        self,
        project_id: uuid.UUID,
        current_user: CurrentUser,
        new_health: str,
        *,
        reason: str = "",
        correlation_id: str = "",
    ) -> ProjectInstanceModel:
        project = await self.get_project(project_id, current_user)

        try:
            target_health_enum = ProjectHealth(new_health)
        except ValueError as exc:
            raise BusinessRuleException(
                f"Unknown health indicator value: {new_health}.",
                code="PROJECT_INVALID_HEALTH",
            ) from exc

        prev_health = project.health
        project.health = target_health_enum.value

        # Record health history
        await self._project_repo.record_health_transition(
            project_instance_id=project.id,
            previous_health=prev_health,
            new_health=target_health_enum.value,
            changed_by=current_user.user_id,
            reason=reason or f"Health transitioned to {target_health_enum.value}",
        )

        # Emit ProjectHealthChanged domain event
        await self._outbox_service.emit(
            event_type=DomainEventType.PROJECT_HEALTH_CHANGED.value,
            actor_role=current_user.role.value,
            resource_type="project_instance",
            resource_id=str(project.id),
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            group_id=project.group_id,
            metadata={
                "previous_health": prev_health,
                "new_health": target_health_enum.value,
                "reason": reason,
            },
            correlation_id=correlation_id,
        )

        return project

    async def get_project_overview(
        self,
        project_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> dict[str, Any]:
        project = await self.get_project(project_id, current_user)
        profile = await self._project_repo.get_profile(project.id)
        technologies = await self._project_repo.list_technologies(project.id)
        phase_history = await self._project_repo.list_phase_history(project.id)
        health_history = await self._project_repo.list_health_history(project.id)

        # Calculate days remaining if deadline exists
        days_remaining: int | None = None
        if project.deadline:
            delta = project.deadline - datetime.now(UTC)
            days_remaining = max(0, delta.days)

        return {
            "id": str(project.id),
            "student_id": str(project.student_id),
            "group_id": str(project.group_id) if project.group_id else None,
            "project_definition_id": str(project.project_definition_id)
            if project.project_definition_id
            else None,
            "name": project.name,
            "problem": project.problem,
            "proposed_solution": project.proposed_solution,
            "complexity": project.complexity,
            "current_phase": project.current_phase,
            "health": project.health,
            "progress_percentage": project.progress_percentage,
            "status": project.status,
            "deadline": project.deadline.isoformat() if project.deadline else None,
            "days_remaining": days_remaining,
            "profile": {
                "objective": profile.objective if profile else "",
                "target_users": profile.target_users if profile else "",
                "project_type": profile.project_type if profile else "",
                "student_skill_context": profile.student_skill_context if profile else "",
                "goals": profile.goals if profile else "",
                "scope": profile.scope if profile else "",
                "expected_outcome": profile.expected_outcome if profile else "",
                "constraints": profile.constraints if profile else "",
                "assumptions": profile.assumptions if profile else "",
                "version": profile.version if profile else 1,
            }
            if profile
            else None,
            "technologies": [
                {
                    "id": str(t.id),
                    "technology_id": str(t.technology_id),
                    "category": t.category,
                    "purpose": t.purpose,
                    "why_selected": t.why_selected,
                }
                for t in technologies
            ],
            "recent_activity": {
                "latest_phase_transition": {
                    "previous_phase": phase_history[0].previous_phase,
                    "new_phase": phase_history[0].new_phase,
                    "changed_at": phase_history[0].changed_at.isoformat(),
                    "reason": phase_history[0].reason,
                }
                if phase_history
                else None,
                "latest_health_transition": {
                    "previous_health": health_history[0].previous_health,
                    "new_health": health_history[0].new_health,
                    "changed_at": health_history[0].changed_at.isoformat(),
                    "reason": health_history[0].reason,
                }
                if health_history
                else None,
            },
        }
