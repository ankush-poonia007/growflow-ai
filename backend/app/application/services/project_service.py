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
import uuid

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
from backend.app.api.schemas.mentor_supervision import (
    MentorProjectInstanceDetailSchema,
    MentorProjectInstanceSummarySchema,
)
from backend.app.application.services.authorization_helpers import (
    is_mentor_supervising_project,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Sequence
    import uuid

    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import (
        ProjectInstanceModel,
    )
    from backend.app.infrastructure.repositories.assessment_repository import AssessmentRepository
    from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.technology_repository import (
        TechnologyRepository,
    )

logger = get_logger("growflow.application.project_service")


class ProjectService:
    """Application service for student project instances and lifecycle orchestration."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        technology_repo: TechnologyRepository,
        outbox_service: OutboxService,
        assessment_repo: AssessmentRepository | None = None,
        blueprint_repo: BlueprintRepository | None = None,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._technology_repo = technology_repo
        self._outbox_service = outbox_service
        self._assessment_repo = assessment_repo
        self._blueprint_repo = blueprint_repo

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

        if current_user.is_mentor and await is_mentor_supervising_project(
            self._group_repo, project, current_user.user_id
        ):
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

    async def list_group_projects(
        self,
        group_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> Sequence[ProjectInstanceModel]:
        """List all projects associated with a specific group with permission verification."""
        group = await self._group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundException(f"Group {group_id} not found.", code="GROUP_NOT_FOUND")

        if current_user.is_mentor and str(group.mentor_id) != str(current_user.user_id):
            raise AuthorizationException(
                "You do not supervise this group.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )
        if current_user.is_student:
            membership = await self._group_repo.get_active_membership_for_student(
                current_user.user_id, group_id
            )
            if not membership:
                raise AuthorizationException(
                    "You are not an active member of this group.",
                    code="AUTH_FORBIDDEN_RESOURCE",
                )

        all_projects = await self._project_repo.list_by_group(group_id)
        if current_user.is_student:
            return [p for p in all_projects if str(p.student_id) == str(current_user.user_id)]
        return all_projects


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
            clean_name = name.strip()
            if not clean_name:
                raise BusinessRuleException(
                    "Project name cannot be empty.",
                    code="PROJECT_INVALID_NAME",
                )
            project.name = clean_name
        if problem is not None:
            project.problem = problem.strip()
        if proposed_solution is not None:
            project.proposed_solution = proposed_solution.strip()
        if complexity is not None:
            try:
                target_complexity_enum = ProjectComplexity(complexity)
            except ValueError as exc:
                raise BusinessRuleException(
                    f"Unknown complexity value: {complexity}.",
                    code="PROJECT_INVALID_COMPLEXITY",
                ) from exc
            project.complexity = target_complexity_enum.value
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

        # Assessment summary synthesis
        assessment_summary: dict[str, Any] | None = None
        if self._assessment_repo:
            try:
                assessment = await self._assessment_repo.get_by_project_id(project.id)
                if assessment:
                    result = await self._assessment_repo.get_result_by_project_id(project.id)
                    assessment_summary = {
                        "status": assessment.status,
                        "overall_score": result.overall_score if result else None,
                        "readiness_tier": result.readiness_tier if result else None,
                        "dimension_scores": result.dimension_scores if result else None,
                        "technical_gaps_count": len(result.technical_gaps) if (result and result.technical_gaps) else 0,
                        "recommendations_count": len(result.recommendations) if (result and result.recommendations) else 0,
                        "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
                    }
                else:
                    assessment_summary = {
                        "status": "NOT_STARTED",
                        "overall_score": None,
                        "readiness_tier": None,
                        "dimension_scores": None,
                        "technical_gaps_count": 0,
                        "recommendations_count": 0,
                        "completed_at": None,
                    }
            except Exception as exc:
                logger.warning("Failed to retrieve assessment summary for project overview", error=str(exc))

        # Blueprint summary synthesis
        blueprint_summary: dict[str, Any] | None = None
        if self._blueprint_repo:
            try:
                blueprint = await self._blueprint_repo.get_by_project_id(project.id)
                if blueprint:
                    blueprint_summary = {
                        "id": str(blueprint.id),
                        "status": blueprint.status,
                        "qa_status": blueprint.qa_status,
                        "qa_score": blueprint.qa_score,
                        "approved_at": blueprint.approved_at.isoformat() if blueprint.approved_at else None,
                        "total_sections": len(blueprint.content) if blueprint.content else 0,
                    }
                else:
                    blueprint_summary = {
                        "id": None,
                        "status": "NOT_STARTED",
                        "qa_status": "PENDING",
                        "qa_score": None,
                        "approved_at": None,
                        "total_sections": 0,
                    }
            except Exception as exc:
                logger.warning("Failed to retrieve blueprint summary for project overview", error=str(exc))

        return {
            "id": str(project.id),
            "student_id": str(project.student_id),
            "group_id": str(project.group_id) if project.group_id else None,
            "project_definition_id": str(project.project_definition_id)
            if project.project_definition_id
            else None,
            "source_definition_version_id": str(project.source_definition_version_id)
            if project.source_definition_version_id
            else None,
            "is_mentor_project": bool(project.project_definition_id),
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
            "assessment_summary": assessment_summary,
            "blueprint_summary": blueprint_summary,
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

    async def list_supervised_projects(
        self,
        mentor_id: uuid.UUID | str,
        *,
        group_id: uuid.UUID | str | None = None,
        phase: str | None = None,
        health: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MentorProjectInstanceSummarySchema]:
        """List all project instances across groups supervised by the mentor."""
        mentor_groups = await self._group_repo.list_by_mentor(mentor_id)
        if not mentor_groups:
            return []

        group_ids = [g.id for g in mentor_groups]
        records = await self._project_repo.list_supervised_projects(
            group_ids=group_ids,
            group_id=group_id,
            phase=phase,
            health=health,
            status=status,
            search=search,
        )

        return [
            MentorProjectInstanceSummarySchema(
                id=str(proj.id),
                name=proj.name,
                student_id=str(student.id),
                student_name=student.full_name or student.email,
                student_email=student.email,
                group_id=str(grp.id) if grp else None,
                group_name=grp.name if grp else None,
                current_phase=proj.current_phase,
                health=proj.health,
                progress_percentage=proj.progress_percentage,
                status=proj.status,
                deadline=proj.deadline,
                source_definition_id=str(defn.id) if defn else None,
                source_definition_name=defn.name if defn else None,
                source_definition_version_number=ver.version_number if ver else None,
                created_at=proj.created_at,
                updated_at=proj.updated_at,
            )
            for proj, student, grp, defn, ver in records
        ]

    async def get_supervised_project_detail(
        self,
        project_id: uuid.UUID | str,
        mentor_id: uuid.UUID | str,
    ) -> MentorProjectInstanceDetailSchema:
        """Fetch project instance detail with student, group, and pinned definition snapshot context."""
        record = await self._project_repo.get_supervised_project_detail(project_id)
        if not record:
            raise NotFoundException(f"Project {project_id} not found.", code="PROJECT_NOT_FOUND")

        proj, student, grp, defn, ver, profile = record

        is_supervised = await self.is_project_supervised_by_mentor(proj, mentor_id)
        if not is_supervised:
            raise AuthorizationException(
                "You do not supervise this project instance.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )

        return MentorProjectInstanceDetailSchema(
            id=str(proj.id),
            name=proj.name,
            problem=proj.problem,
            proposed_solution=proj.proposed_solution,
            complexity=proj.complexity,
            current_phase=proj.current_phase,
            health=proj.health,
            progress_percentage=proj.progress_percentage,
            status=proj.status,
            deadline=proj.deadline,
            started_at=proj.started_at,
            completed_at=proj.completed_at,
            student_id=str(student.id),
            student_name=student.full_name or student.email,
            student_email=student.email,
            group_id=str(grp.id) if grp else None,
            group_name=grp.name if grp else None,
            source_definition_id=str(defn.id) if defn else None,
            source_definition_name=defn.name if defn else None,
            source_definition_version_number=ver.version_number if ver else None,
            objective=profile.objective if profile else None,
            scope=profile.scope if profile else None,
            expected_outcome=profile.expected_outcome if profile else None,
            created_at=proj.created_at,
            updated_at=proj.updated_at,
        )

    async def list_at_risk_projects(
        self,
        mentor_id: uuid.UUID | str,
        *,
        group_id: uuid.UUID | str | None = None,
        health: str | None = None,
    ) -> list[MentorProjectInstanceSummarySchema]:
        """List all at-risk (WARNING and CRITICAL) project instances across mentor cohorts."""
        mentor_groups = await self._group_repo.list_by_mentor(mentor_id)
        if not mentor_groups:
            return []

        group_ids = [g.id for g in mentor_groups]
        records = await self._project_repo.list_at_risk_projects(
            group_ids=group_ids,
            group_id=group_id,
            health=health,
        )

        return [
            MentorProjectInstanceSummarySchema(
                id=str(proj.id),
                name=proj.name,
                student_id=str(student.id),
                student_name=student.full_name or student.email,
                student_email=student.email,
                group_id=str(grp.id) if grp else None,
                group_name=grp.name if grp else None,
                current_phase=proj.current_phase,
                health=proj.health,
                progress_percentage=proj.progress_percentage,
                status=proj.status,
                deadline=proj.deadline,
                source_definition_id=str(defn.id) if defn else None,
                source_definition_name=defn.name if defn else None,
                source_definition_version_number=ver.version_number if ver else None,
                created_at=proj.created_at,
                updated_at=proj.updated_at,
            )
            for proj, student, grp, defn, ver in records
        ]

    async def get_at_risk_project_detail(
        self,
        project_id: uuid.UUID | str,
        mentor_id: uuid.UUID | str,
    ) -> MentorProjectInstanceDetailSchema:
        """Fetch read-only detail of an at-risk project instance."""
        detail = await self.get_supervised_project_detail(project_id, mentor_id)
        if detail.health not in (ProjectHealth.WARNING.value, ProjectHealth.CRITICAL.value):
            raise NotFoundException(
                "Project is not currently at risk.",
                code="PROJECT_NOT_AT_RISK",
            )
        return detail

    async def is_project_supervised_by_mentor(
        self,
        project: ProjectInstanceModel | uuid.UUID | str,
        mentor_id: uuid.UUID | str,
    ) -> bool:
        """Check whether a project instance falls under the mentor's supervision scope.

        Supervision holds if either:
        1. The project has a group_id directly matching one of the mentor's supervised groups.
        2. The student owning the project is an active member in any active group supervised by the mentor.
        """
        proj_model = project
        if not hasattr(proj_model, "student_id"):
            proj_model = await self._project_repo.get_by_id(project)
            if not proj_model:
                return False

        return await is_mentor_supervising_project(self._group_repo, proj_model, mentor_id)

    async def assert_mentor_supervises_project(
        self,
        project_id: uuid.UUID | str,
        mentor_id: uuid.UUID | str,
    ) -> ProjectInstanceModel:
        """Assert that the mentor supervises the project instance.

        Returns the project instance model if supervised, raises NotFoundException (404) if project
        doesn't exist, or AuthorizationException (403) if the project is not supervised by the mentor.
        """
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project {project_id} not found.", code="PROJECT_NOT_FOUND")

        is_supervised = await self.is_project_supervised_by_mentor(project, mentor_id)
        if not is_supervised:
            raise AuthorizationException(
                "You do not supervise this project instance.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )
        return project

