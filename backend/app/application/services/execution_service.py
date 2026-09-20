"""
GrowFlow — Execution Management Application Service.

Coordinates operational tasks, milestones, risks, roadmap projection,
and project document lifecycle for student projects.

Architecture ref:
  6A § 9   — Class-Based Architecture
  6B § 20  — Project milestones & tasks
  6B § 44  — Project execution models
  Gate 10  — Execution Management
"""

from __future__ import annotations

from datetime import UTC, datetime
import re
from typing import TYPE_CHECKING
import uuid

from backend.app.api.schemas.execution import (
    DocumentCreatePayload,
    DocumentResponse,
    DocumentUpdatePayload,
    MilestoneCreatePayload,
    MilestoneResponse,
    MilestoneUpdatePayload,
    RiskCreatePayload,
    RiskResponse,
    RiskUpdatePayload,
    RoadmapGroupedTasks,
    RoadmapMilestoneItem,
    RoadmapResponse,
    RoadmapSummary,
    TaskCreatePayload,
    TaskResponse,
    TaskUpdatePayload,
)
from backend.app.application.services.authorization_helpers import (
    verify_project_read_access,
)
from backend.app.domain.blueprint.models import BlueprintStatus
from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectMilestoneModel,
    ProjectRiskModel,
    ProjectTaskModel,
)
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import ProjectInstanceModel
    from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
    from backend.app.infrastructure.repositories.execution_repository import (
        DocumentRepository,
        MilestoneRepository,
        RiskRepository,
        TaskRepository,
    )
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository

logger = get_logger("growflow.application.execution_service")


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", cleaned)[:50] or "document"


class ExecutionService:
    """Application service for operational project execution management."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        blueprint_repo: BlueprintRepository,
        milestone_repo: MilestoneRepository,
        task_repo: TaskRepository,
        risk_repo: RiskRepository,
        document_repo: DocumentRepository,
        outbox_service: OutboxService,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._blueprint_repo = blueprint_repo
        self._milestone_repo = milestone_repo
        self._task_repo = task_repo
        self._risk_repo = risk_repo
        self._document_repo = document_repo
        self._outbox_service = outbox_service

    # =========================================================================
    # Authorization & Project Verification
    # =========================================================================

    async def _verify_project_access(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> ProjectInstanceModel:
        """Ensure project exists and caller has read access."""
        return await verify_project_read_access(
            self._project_repo, self._group_repo, project_id, current_user
        )

    def _verify_can_modify(
        self, project: ProjectInstanceModel, current_user: CurrentUser
    ) -> None:
        """Ensure caller is owner student or admin to perform mutations."""
        if current_user.is_admin:
            return
        if current_user.is_student and str(project.student_id) == str(current_user.user_id):
            return
        raise AuthorizationException(
            "Only the project owner may modify execution items.",
            code="AUTH_FORBIDDEN_RESOURCE",
        )

    # =========================================================================
    # Idempotent Blueprint -> Execution Initialization
    # =========================================================================

    async def ensure_initialized(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> None:
        """
        Idempotently populate milestones, tasks, risks, and initial documents
        from the approved blueprint if no operational records exist yet.
        """
        project = await self._verify_project_access(project_id, current_user)

        milestones_count = await self._milestone_repo.count_by_project(project.id)
        tasks_count = await self._task_repo.count_by_project(project.id)

        if milestones_count > 0 or tasks_count > 0:
            return

        latest_bp = await self._blueprint_repo.get_latest_by_project(project.id)
        if not latest_bp or not latest_bp.content:
            return

        # Gate 10: Execution structures must materialize ONLY from an APPROVED blueprint
        if latest_bp.status != BlueprintStatus.APPROVED.value:
            return

        content = latest_bp.content or {}

        # 1. Initialize Milestones
        milestones_data = content.get("milestones") or {}
        raw_schedule = (
            milestones_data.get("milestones_schedule")
            if isinstance(milestones_data, dict)
            else []
        ) or []

        created_milestones: list[ProjectMilestoneModel] = []
        gate_to_milestone_id: dict[str, str] = {}

        if raw_schedule:
            for idx, item in enumerate(raw_schedule):
                gate = str(item.get("gate") or f"M{idx + 1}")
                m_id = str(uuid.uuid4())
                gate_to_milestone_id[gate] = m_id
                deliverable = item.get("deliverable") or ""
                deliverables_list = [deliverable] if deliverable else []

                m = ProjectMilestoneModel(
                    id=m_id,
                    project_instance_id=str(project.id),
                    title=str(item.get("name") or f"Milestone {idx + 1}"),
                    description=deliverable,
                    gate_code=gate,
                    target_date=None,
                    status="IN_PROGRESS" if idx == 0 else "UPCOMING",
                    progress_percent=0,
                    deliverables=deliverables_list,
                    section_order=idx + 1,
                )
                created_milestones.append(m)
        else:
            defaults = [
                ("M1", "Foundation & Architecture Setup", "Core models and scaffolding"),
                ("M2", "Core Domain & Service Logic", "Primary workflows implemented"),
                ("M3", "Testing, Hardening & Polishing", "Automated tests and QA passing"),
                ("M4", "Final Delivery & Documentation", "Complete showcase and release"),
            ]
            for idx, (gate, title, desc) in enumerate(defaults):
                m_id = str(uuid.uuid4())
                gate_to_milestone_id[gate] = m_id
                m = ProjectMilestoneModel(
                    id=m_id,
                    project_instance_id=str(project.id),
                    title=title,
                    description=desc,
                    gate_code=gate,
                    status="IN_PROGRESS" if idx == 0 else "UPCOMING",
                    progress_percent=0,
                    deliverables=[desc],
                    section_order=idx + 1,
                )
                created_milestones.append(m)

        await self._milestone_repo.bulk_create(created_milestones)

        # 2. Initialize Tasks
        tasks_data = content.get("tasks") or {}
        raw_tasks = (
            tasks_data.get("tasks_breakdown")
            if isinstance(tasks_data, dict)
            else []
        ) or []

        created_tasks: list[ProjectTaskModel] = []
        milestone_keys = list(gate_to_milestone_id.values())

        if raw_tasks:
            for idx, item in enumerate(raw_tasks):
                task_id = str(uuid.uuid4())
                # Link task to milestone deterministically
                assigned_milestone = milestone_keys[idx % len(milestone_keys)] if milestone_keys else None
                priority_raw = str(item.get("priority") or "MEDIUM").upper()
                priority = priority_raw if priority_raw in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else "MEDIUM"
                phase_raw = str(item.get("phase") or "IMPLEMENTATION").upper()
                phase = phase_raw if phase_raw in ("PLANNING", "IMPLEMENTATION", "TESTING", "DEPLOYMENT") else (
                    "PLANNING" if idx < 2 else "IMPLEMENTATION"
                )

                t = ProjectTaskModel(
                    id=task_id,
                    project_instance_id=str(project.id),
                    milestone_id=assigned_milestone,
                    task_code=str(item.get("id") or f"T{idx + 1:02d}"),
                    title=str(item.get("name") or item.get("title") or f"Task {idx + 1}"),
                    description=str(item.get("description") or ""),
                    status="TODO",
                    priority=priority,
                    category=str(item.get("category") or "ENGINEERING"),
                    phase=phase,
                    due_date=None,
                    dependencies=item.get("dependencies") if isinstance(item.get("dependencies"), list) else [],
                    acceptance_criteria=item.get("acceptance_criteria") if isinstance(item.get("acceptance_criteria"), list) else [],
                )
                created_tasks.append(t)
        else:
            default_tasks = [
                ("T01", "Configure project environment and repository", "PLANNING", "CRITICAL"),
                ("T02", "Implement core domain entities and database schema", "IMPLEMENTATION", "HIGH"),
                ("T03", "Build API endpoints and request validation", "IMPLEMENTATION", "HIGH"),
                ("T04", "Develop responsive frontend UI views", "IMPLEMENTATION", "MEDIUM"),
                ("T05", "Execute integration and end-to-end tests", "TESTING", "HIGH"),
                ("T06", "Prepare deployment documentation and user guide", "DEPLOYMENT", "LOW"),
            ]
            for idx, (code, title, phase, prio) in enumerate(default_tasks):
                t_id = str(uuid.uuid4())
                assigned_milestone = milestone_keys[idx % len(milestone_keys)] if milestone_keys else None
                t = ProjectTaskModel(
                    id=t_id,
                    project_instance_id=str(project.id),
                    milestone_id=assigned_milestone,
                    task_code=code,
                    title=title,
                    description=f"Initial task for {title}",
                    status="TODO",
                    priority=prio,
                    category="DEVELOPMENT",
                    phase=phase,
                )
                created_tasks.append(t)

        await self._task_repo.bulk_create(created_tasks)

        # 3. Initialize Risks
        risks_data = content.get("risks") or {}
        raw_risks = (
            risks_data.get("technical_risks")
            if isinstance(risks_data, dict)
            else []
        ) or []

        created_risks: list[ProjectRiskModel] = []
        if raw_risks:
            for idx, item in enumerate(raw_risks):
                r_id = str(uuid.uuid4())
                sev_raw = str(item.get("severity") or "MEDIUM").upper()
                sev = sev_raw if sev_raw in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else "MEDIUM"
                prob_raw = str(item.get("probability") or "MEDIUM").upper()
                prob = prob_raw if prob_raw in ("LOW", "MEDIUM", "HIGH") else "MEDIUM"
                impact_raw = str(item.get("impact") or "MEDIUM").upper()
                impact = impact_raw if impact_raw in ("LOW", "MEDIUM", "HIGH") else "MEDIUM"

                r = ProjectRiskModel(
                    id=r_id,
                    project_instance_id=str(project.id),
                    risk_code=str(item.get("id") or f"R{idx + 1:02d}"),
                    title=str(item.get("title") or item.get("name") or f"Risk {idx + 1}"),
                    description=str(item.get("description") or ""),
                    severity=sev,
                    probability=prob,
                    impact=impact,
                    status="OPEN",
                    mitigation=str(item.get("mitigation") or "Standard monitoring and architectural review"),
                    owner="Student",
                )
                created_risks.append(r)
        else:
            default_risks = [
                ("R01", "Third-party dependency latency or downtime", "MEDIUM", "HIGH", "Implement retry policy and fallback responses."),
                ("R02", "Complex asynchronous state synchronization", "HIGH", "HIGH", "Enforce strict unidirectional state models and optimistic UI rollback."),
                ("R03", "Schema migration rollbacks during deployment", "MEDIUM", "MEDIUM", "Maintain backward compatible schema migrations with automated test validation."),
            ]
            for idx, (code, title, sev, impact, mit) in enumerate(default_risks):
                r_id = str(uuid.uuid4())
                r = ProjectRiskModel(
                    id=r_id,
                    project_instance_id=str(project.id),
                    risk_code=code,
                    title=title,
                    description=title,
                    severity=sev,
                    probability="MEDIUM",
                    impact=impact,
                    status="OPEN",
                    mitigation=mit,
                    owner="Student",
                )
                created_risks.append(r)

        await self._risk_repo.bulk_create(created_risks)

        # 4. Initialize Default Documents
        docs_count = await self._document_repo.count_by_project(project.id)
        if docs_count == 0:
            created_docs: list[ProjectDocumentModel] = []

            # Master Architecture Document
            bp_profile = content.get("project_profile") or {}
            bp_tech = content.get("tech_stack") or {}
            master_md = f"""# Master Architecture Blueprint

## 1. Project Profile
**Project Name:** {project.name}
**Problem Statement:** {project.problem or 'Not specified'}
**Target Solution:** {project.proposed_solution or 'Not specified'}

## 2. Technology Stack & Architecture
- **Primary Stack:** {bp_tech.get('primary_language', 'Python / TypeScript')}
- **Frameworks:** {bp_tech.get('frameworks', 'FastAPI, React, PostgreSQL')}
- **Architecture Style:** Clean Architecture with Domain-Driven Core

## 3. Operational Strategy
This system was compiled automatically from Approved Blueprint {latest_bp.id} and transitioned to active execution.
"""
            created_docs.append(
                ProjectDocumentModel(
                    id=str(uuid.uuid4()),
                    project_instance_id=str(project.id),
                    document_key="master_blueprint",
                    title="Master Architecture Blueprint",
                    doc_type="BLUEPRINT",
                    format="markdown",
                    content=master_md.strip(),
                    version="1.0",
                    status="ACTIVE",
                    source="BLUEPRINT_INIT",
                )
            )

            # Technical Specifications
            spec_data = content.get("specifications") or {}
            spec_md = f"""# Technical Specifications & Data Models

## 1. Core Models & System Entities
The system operates on relational database models with ACID compliance:
- **Project Instances:** Lifecycle phase management and audit history
- **Execution Tasks:** Granular units of work tied to milestones
- **Milestones:** Verification gates enforcing quality standards
- **Risk Registry:** Proactive mitigation of technical and operational blockers

## 2. API Contract Guidelines
- RESTful HTTP endpoints with JSON serialization
- Standardized error codes and envelope responses
- Transactional Outbox pattern for asynchronous domain event propagation
"""
            created_docs.append(
                ProjectDocumentModel(
                    id=str(uuid.uuid4()),
                    project_instance_id=str(project.id),
                    document_key="technical_specifications",
                    title="Technical Specifications & Data Models",
                    doc_type="SPECIFICATION",
                    format="markdown",
                    content=spec_md.strip(),
                    version="1.0",
                    status="ACTIVE",
                    source="BLUEPRINT_INIT",
                )
            )

            # README & Setup Guide
            readme_data = content.get("readme") or {}
            readme_raw = readme_data.get("markdown") if isinstance(readme_data, dict) else ""
            readme_md = readme_raw or f"""# {project.name}

## Overview
{project.problem or 'Interactive project repository managed by GrowFlow.'}

## Getting Started
1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run development server:
   ```bash
   npm run dev
   ```
"""
            created_docs.append(
                ProjectDocumentModel(
                    id=str(uuid.uuid4()),
                    project_instance_id=str(project.id),
                    document_key="project_readme",
                    title="README & Setup Guide",
                    doc_type="README",
                    format="markdown",
                    content=readme_md.strip(),
                    version="1.0",
                    status="ACTIVE",
                    source="BLUEPRINT_INIT",
                )
            )

            await self._document_repo.bulk_create(created_docs)

        logger.info(
            "Initialized execution state for project %s (milestones=%d, tasks=%d, risks=%d)",
            project.id,
            len(created_milestones),
            len(created_tasks),
            len(created_risks),
        )

    # =========================================================================
    # Task Methods (S18 & S19)
    # =========================================================================

    async def list_tasks(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        *,
        status: str | None = None,
        priority: str | None = None,
        milestone_id: str | None = None,
        phase: str | None = None,
        search: str | None = None,
    ) -> list[TaskResponse]:
        await self.ensure_initialized(project_id, current_user)
        models = await self._task_repo.list_by_project(
            project_id,
            status=status,
            priority=priority,
            milestone_id=milestone_id,
            phase=phase,
            search=search,
        )
        return [TaskResponse.model_validate(m) for m in models]

    async def get_task(
        self,
        project_id: uuid.UUID | str,
        task_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> TaskResponse:
        await self._verify_project_access(project_id, current_user)
        task = await self._task_repo.get_by_id(task_id)
        if not task or task.project_instance_id != str(project_id):
            raise NotFoundException("Task not found.", code="TASK_NOT_FOUND")
        return TaskResponse.model_validate(task)

    async def create_task(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: TaskCreatePayload,
    ) -> TaskResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        count = await self._task_repo.count_by_project(project.id)
        task_code = f"T{count + 1:02d}"

        task = ProjectTaskModel(
            id=str(uuid.uuid4()),
            project_instance_id=str(project.id),
            milestone_id=payload.milestone_id,
            task_code=task_code,
            title=payload.title.strip(),
            description=payload.description.strip(),
            status="TODO",
            priority=payload.priority,
            category=payload.category.strip() or "GENERAL",
            phase=payload.phase,
            due_date=payload.due_date,
            dependencies=payload.dependencies,
            acceptance_criteria=payload.acceptance_criteria,
        )
        await self._task_repo.create(task)

        # Recalculate milestone progress if assigned
        if payload.milestone_id:
            await self._recalculate_milestone_progress(payload.milestone_id)

        # Recalculate project progress
        await self._recalculate_project_progress(project)

        # Emit event
        await self._outbox_service.emit(
            event_type=DomainEventType.TASK_CREATED.value,
            actor_role="STUDENT",
            resource_type="project_task",
            resource_id=task.id,
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            metadata={"task_code": task.task_code, "title": task.title},
        )

        return TaskResponse.model_validate(task)

    async def update_task(
        self,
        project_id: uuid.UUID | str,
        task_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: TaskUpdatePayload,
    ) -> TaskResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        task = await self._task_repo.get_by_id(task_id)
        if not task or task.project_instance_id != str(project.id):
            raise NotFoundException("Task not found.", code="TASK_NOT_FOUND")

        old_milestone_id = task.milestone_id
        old_status = task.status

        if payload.title is not None:
            task.title = payload.title.strip()
        if payload.description is not None:
            task.description = payload.description.strip()
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.category is not None:
            task.category = payload.category.strip()
        if payload.phase is not None:
            task.phase = payload.phase
        if payload.milestone_id is not None:
            task.milestone_id = payload.milestone_id if payload.milestone_id != "" else None
        if payload.due_date is not None:
            task.due_date = payload.due_date
        if payload.dependencies is not None:
            task.dependencies = payload.dependencies
        if payload.acceptance_criteria is not None:
            task.acceptance_criteria = payload.acceptance_criteria

        status_changed = False
        if payload.status is not None and payload.status != task.status:
            task.status = payload.status
            status_changed = True
            if payload.status == "COMPLETED":
                task.completed_at = datetime.now(UTC)
            elif old_status == "COMPLETED":
                task.completed_at = None

        await self._task_repo.save(task)

        # Recalculate milestone progress
        if task.milestone_id:
            await self._recalculate_milestone_progress(task.milestone_id)
        if old_milestone_id and old_milestone_id != task.milestone_id:
            await self._recalculate_milestone_progress(old_milestone_id)

        # Recalculate project progress
        await self._recalculate_project_progress(project)

        # Emit events
        event_type = (
            DomainEventType.TASK_COMPLETED.value
            if task.status == "COMPLETED" and status_changed
            else DomainEventType.TASK_UPDATED.value
        )
        await self._outbox_service.emit(
            event_type=event_type,
            actor_role="STUDENT",
            resource_type="project_task",
            resource_id=task.id,
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            metadata={"status": task.status, "task_code": task.task_code},
        )

        return TaskResponse.model_validate(task)

    async def delete_task(
        self,
        project_id: uuid.UUID | str,
        task_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> bool:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        task = await self._task_repo.get_by_id(task_id)
        if not task or task.project_instance_id != str(project.id):
            raise NotFoundException("Task not found.", code="TASK_NOT_FOUND")

        milestone_id = task.milestone_id
        await self._task_repo.delete_by_id(task_id)

        if milestone_id:
            await self._recalculate_milestone_progress(milestone_id)
        await self._recalculate_project_progress(project)
        return True

    # =========================================================================
    # Milestone Methods (S20 & S21)
    # =========================================================================

    async def list_milestones(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> list[MilestoneResponse]:
        await self.ensure_initialized(project_id, current_user)
        milestones = await self._milestone_repo.list_by_project(project_id)
        all_tasks = await self._task_repo.list_by_project(project_id)

        # Group tasks by milestone
        tasks_by_milestone: dict[str, list[ProjectTaskModel]] = {}
        for t in all_tasks:
            if t.milestone_id:
                tasks_by_milestone.setdefault(t.milestone_id, []).append(t)

        responses: list[MilestoneResponse] = []
        for m in milestones:
            m_tasks = tasks_by_milestone.get(m.id, [])
            completed_tasks = [t for t in m_tasks if t.status == "COMPLETED"]
            task_resp = [TaskResponse.model_validate(t) for t in m_tasks]

            resp = MilestoneResponse(
                id=m.id,
                project_instance_id=m.project_instance_id,
                title=m.title,
                description=m.description or "",
                gate_code=m.gate_code or "",
                target_date=m.target_date,
                status=m.status,
                progress_percent=m.progress_percent,
                deliverables=m.deliverables or [],
                section_order=m.section_order,
                task_count=len(m_tasks),
                completed_task_count=len(completed_tasks),
                tasks=task_resp,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            responses.append(resp)
        return responses

    async def get_milestone(
        self,
        project_id: uuid.UUID | str,
        milestone_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> MilestoneResponse:
        await self._verify_project_access(project_id, current_user)
        m = await self._milestone_repo.get_by_id(milestone_id)
        if not m or m.project_instance_id != str(project_id):
            raise NotFoundException("Milestone not found.", code="MILESTONE_NOT_FOUND")

        m_tasks = await self._task_repo.list_by_project(project_id, milestone_id=str(milestone_id))
        completed_tasks = [t for t in m_tasks if t.status == "COMPLETED"]

        return MilestoneResponse(
            id=m.id,
            project_instance_id=m.project_instance_id,
            title=m.title,
            description=m.description or "",
            gate_code=m.gate_code or "",
            target_date=m.target_date,
            status=m.status,
            progress_percent=m.progress_percent,
            deliverables=m.deliverables or [],
            section_order=m.section_order,
            task_count=len(m_tasks),
            completed_task_count=len(completed_tasks),
            tasks=[TaskResponse.model_validate(t) for t in m_tasks],
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def create_milestone(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: MilestoneCreatePayload,
    ) -> MilestoneResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        count = await self._milestone_repo.count_by_project(project.id)
        gate_code = payload.gate_code.strip() or f"M{count + 1}"

        m = ProjectMilestoneModel(
            id=str(uuid.uuid4()),
            project_instance_id=str(project.id),
            title=payload.title.strip(),
            description=payload.description.strip(),
            gate_code=gate_code,
            target_date=payload.target_date,
            status="UPCOMING",
            progress_percent=0,
            deliverables=payload.deliverables,
            section_order=count + 1,
        )
        await self._milestone_repo.create(m)

        return MilestoneResponse(
            id=m.id,
            project_instance_id=m.project_instance_id,
            title=m.title,
            description=m.description or "",
            gate_code=m.gate_code or "",
            target_date=m.target_date,
            status=m.status,
            progress_percent=m.progress_percent,
            deliverables=m.deliverables or [],
            section_order=m.section_order,
            task_count=0,
            completed_task_count=0,
            tasks=[],
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def update_milestone(
        self,
        project_id: uuid.UUID | str,
        milestone_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: MilestoneUpdatePayload,
    ) -> MilestoneResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        m = await self._milestone_repo.get_by_id(milestone_id)
        if not m or m.project_instance_id != str(project.id):
            raise NotFoundException("Milestone not found.", code="MILESTONE_NOT_FOUND")

        if payload.title is not None:
            m.title = payload.title.strip()
        if payload.description is not None:
            m.description = payload.description.strip()
        if payload.gate_code is not None:
            m.gate_code = payload.gate_code.strip()
        if payload.target_date is not None:
            m.target_date = payload.target_date
        if payload.status is not None:
            m.status = payload.status
        if payload.deliverables is not None:
            m.deliverables = payload.deliverables

        await self._milestone_repo.save(m)

        # Emit event
        await self._outbox_service.emit(
            event_type=DomainEventType.MILESTONE_UPDATED.value,
            actor_role="STUDENT",
            resource_type="project_milestone",
            resource_id=m.id,
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            metadata={"status": m.status, "gate_code": m.gate_code},
        )

        m_tasks = await self._task_repo.list_by_project(project.id, milestone_id=str(m.id))
        completed_tasks = [t for t in m_tasks if t.status == "COMPLETED"]

        return MilestoneResponse(
            id=m.id,
            project_instance_id=m.project_instance_id,
            title=m.title,
            description=m.description or "",
            gate_code=m.gate_code or "",
            target_date=m.target_date,
            status=m.status,
            progress_percent=m.progress_percent,
            deliverables=m.deliverables or [],
            section_order=m.section_order,
            task_count=len(m_tasks),
            completed_task_count=len(completed_tasks),
            tasks=[TaskResponse.model_validate(t) for t in m_tasks],
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    # =========================================================================
    # Risk Methods (S22 & S23)
    # =========================================================================

    async def list_risks(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        *,
        status: str | None = None,
        severity: str | None = None,
        search: str | None = None,
    ) -> list[RiskResponse]:
        await self.ensure_initialized(project_id, current_user)
        models = await self._risk_repo.list_by_project(
            project_id, status=status, severity=severity, search=search
        )
        return [RiskResponse.model_validate(m) for m in models]

    async def get_risk(
        self,
        project_id: uuid.UUID | str,
        risk_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> RiskResponse:
        await self._verify_project_access(project_id, current_user)
        r = await self._risk_repo.get_by_id(risk_id)
        if not r or r.project_instance_id != str(project_id):
            raise NotFoundException("Risk not found.", code="RISK_NOT_FOUND")
        return RiskResponse.model_validate(r)

    async def create_risk(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: RiskCreatePayload,
    ) -> RiskResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        count = await self._risk_repo.count_by_project(project.id)
        risk_code = f"R{count + 1:02d}"

        r = ProjectRiskModel(
            id=str(uuid.uuid4()),
            project_instance_id=str(project.id),
            risk_code=risk_code,
            title=payload.title.strip(),
            description=payload.description.strip(),
            severity=payload.severity,
            probability=payload.probability,
            impact=payload.impact,
            status="OPEN",
            mitigation=payload.mitigation.strip(),
            owner=payload.owner.strip() or "Student",
            review_date=payload.review_date,
        )
        await self._risk_repo.create(r)

        # Emit event
        await self._outbox_service.emit(
            event_type=DomainEventType.RISK_CREATED.value,
            actor_role="STUDENT",
            resource_type="project_risk",
            resource_id=r.id,
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            metadata={"risk_code": r.risk_code, "severity": r.severity},
        )

        return RiskResponse.model_validate(r)

    async def update_risk(
        self,
        project_id: uuid.UUID | str,
        risk_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: RiskUpdatePayload,
    ) -> RiskResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        r = await self._risk_repo.get_by_id(risk_id)
        if not r or r.project_instance_id != str(project.id):
            raise NotFoundException("Risk not found.", code="RISK_NOT_FOUND")

        if payload.title is not None:
            r.title = payload.title.strip()
        if payload.description is not None:
            r.description = payload.description.strip()
        if payload.severity is not None:
            r.severity = payload.severity
        if payload.probability is not None:
            r.probability = payload.probability
        if payload.impact is not None:
            r.impact = payload.impact
        if payload.status is not None:
            r.status = payload.status
        if payload.mitigation is not None:
            r.mitigation = payload.mitigation.strip()
        if payload.owner is not None:
            r.owner = payload.owner.strip()
        if payload.review_date is not None:
            r.review_date = payload.review_date

        await self._risk_repo.save(r)

        # Emit event
        await self._outbox_service.emit(
            event_type=DomainEventType.RISK_UPDATED.value,
            actor_role="STUDENT",
            resource_type="project_risk",
            resource_id=r.id,
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            metadata={"status": r.status, "risk_code": r.risk_code},
        )

        return RiskResponse.model_validate(r)

    async def delete_risk(
        self,
        project_id: uuid.UUID | str,
        risk_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> bool:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        r = await self._risk_repo.get_by_id(risk_id)
        if not r or r.project_instance_id != str(project.id):
            raise NotFoundException("Risk not found.", code="RISK_NOT_FOUND")

        return await self._risk_repo.delete_by_id(risk_id)

    # =========================================================================
    # Roadmap Projection (S24)
    # =========================================================================

    async def get_roadmap(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> RoadmapResponse:
        """
        Deterministic backend synthesis:
        Aggregates milestones, tasks, dates, and state into an actionable roadmap.
        """
        await self.ensure_initialized(project_id, current_user)
        project = await self._verify_project_access(project_id, current_user)

        milestones = await self._milestone_repo.list_by_project(project.id)
        tasks = await self._task_repo.list_by_project(project.id)

        now = datetime.now(UTC)

        # Classify tasks
        overdue: list[TaskResponse] = []
        blocked: list[TaskResponse] = []
        in_progress: list[TaskResponse] = []
        upcoming: list[TaskResponse] = []
        completed: list[TaskResponse] = []

        # Map tasks to milestones
        milestone_tasks: dict[str, list[TaskResponse]] = {}

        for t in tasks:
            t_resp = TaskResponse.model_validate(t)
            if t.milestone_id:
                milestone_tasks.setdefault(t.milestone_id, []).append(t_resp)

            if t.status == "COMPLETED":
                completed.append(t_resp)
            elif t.due_date and t.due_date < now:
                overdue.append(t_resp)
            elif t.status == "BLOCKED":
                blocked.append(t_resp)
            elif t.status == "IN_PROGRESS":
                in_progress.append(t_resp)
            else:
                upcoming.append(t_resp)

        # Build milestone items
        milestone_items: list[RoadmapMilestoneItem] = []
        completed_milestones_cnt = 0

        for m in milestones:
            m_ts = milestone_tasks.get(m.id, [])
            if m.status == "COMPLETED" or (m_ts and all(x.status == "COMPLETED" for x in m_ts)):
                completed_milestones_cnt += 1

            milestone_items.append(
                RoadmapMilestoneItem(
                    id=m.id,
                    gate_code=m.gate_code or "",
                    title=m.title,
                    description=m.description or "",
                    status=m.status,
                    progress_percent=m.progress_percent,
                    target_date=m.target_date,
                    deliverables=m.deliverables or [],
                    tasks=m_ts,
                )
            )

        summary = RoadmapSummary(
            total_milestones=len(milestones),
            completed_milestones=completed_milestones_cnt,
            total_tasks=len(tasks),
            completed_tasks=len(completed),
            overdue_tasks_count=len(overdue),
            blocked_tasks_count=len(blocked),
            current_phase=project.current_phase,
            overall_progress=getattr(project, "progress_percentage", 0),
        )

        return RoadmapResponse(
            project_id=str(project.id),
            project_name=project.name,
            current_phase=project.current_phase,
            summary=summary,
            milestones=milestone_items,
            grouped_tasks=RoadmapGroupedTasks(
                overdue=overdue,
                blocked=blocked,
                in_progress=in_progress,
                upcoming=upcoming,
                completed=completed,
            ),
        )

    # =========================================================================
    # Document Methods (S25 & S26)
    # =========================================================================

    async def list_documents(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        *,
        doc_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[DocumentResponse]:
        await self.ensure_initialized(project_id, current_user)
        models = await self._document_repo.list_by_project(
            project_id, doc_type=doc_type, status=status, search=search
        )
        return [DocumentResponse.model_validate(m) for m in models]

    async def get_document(
        self,
        project_id: uuid.UUID | str,
        document_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> DocumentResponse:
        await self._verify_project_access(project_id, current_user)
        doc = await self._document_repo.get_by_id(document_id)
        if not doc or doc.project_instance_id != str(project_id):
            raise NotFoundException("Document not found.", code="DOCUMENT_NOT_FOUND")
        return DocumentResponse.model_validate(doc)

    async def create_document(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: DocumentCreatePayload,
    ) -> DocumentResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        base_key = _slugify(payload.title)
        document_key = f"{base_key}_{uuid.uuid4().hex[:6]}"

        doc = ProjectDocumentModel(
            id=str(uuid.uuid4()),
            project_instance_id=str(project.id),
            document_key=document_key,
            title=payload.title.strip(),
            doc_type=payload.doc_type,
            format=payload.format,
            content=payload.content,
            version="1.0",
            status="ACTIVE",
            source="STUDENT_CREATED",
        )
        await self._document_repo.create(doc)

        # Emit event
        await self._outbox_service.emit(
            event_type=DomainEventType.DOCUMENT_CREATED.value,
            actor_role="STUDENT",
            resource_type="project_document",
            resource_id=doc.id,
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            metadata={"title": doc.title, "document_key": doc.document_key},
        )

        return DocumentResponse.model_validate(doc)

    async def update_document(
        self,
        project_id: uuid.UUID | str,
        document_id: uuid.UUID | str,
        current_user: CurrentUser,
        payload: DocumentUpdatePayload,
    ) -> DocumentResponse:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        doc = await self._document_repo.get_by_id(document_id)
        if not doc or doc.project_instance_id != str(project.id):
            raise NotFoundException("Document not found.", code="DOCUMENT_NOT_FOUND")

        content_changed = False
        if payload.title is not None:
            doc.title = payload.title.strip()
        if payload.content is not None and payload.content != doc.content:
            doc.content = payload.content
            content_changed = True
        if payload.status is not None:
            doc.status = payload.status

        # Increment version if content changed (e.g. 1.0 -> 1.1)
        if content_changed:
            try:
                major, minor = doc.version.split(".")
                doc.version = f"{major}.{int(minor) + 1}"
            except Exception:
                doc.version = "1.1"

        await self._document_repo.save(doc)

        # Emit event
        await self._outbox_service.emit(
            event_type=DomainEventType.DOCUMENT_UPDATED.value,
            actor_role="STUDENT",
            resource_type="project_document",
            resource_id=doc.id,
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            metadata={"title": doc.title, "version": doc.version},
        )

        return DocumentResponse.model_validate(doc)

    async def get_raw_document(
        self,
        project_id: uuid.UUID | str,
        document_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> tuple[str, str]:
        """Returns (filename, markdown_content)."""
        await self._verify_project_access(project_id, current_user)
        doc = await self._document_repo.get_by_id(document_id)
        if not doc or doc.project_instance_id != str(project_id):
            raise NotFoundException("Document not found.", code="DOCUMENT_NOT_FOUND")

        filename = f"{doc.document_key}.md"
        return filename, doc.content or ""

    # =========================================================================
    # Helpers
    # =========================================================================

    async def _recalculate_milestone_progress(self, milestone_id: str) -> None:
        """Update milestone progress percent based on attached tasks."""
        m = await self._milestone_repo.get_by_id(milestone_id)
        if not m:
            return
        m_tasks = await self._task_repo.list_by_project(m.project_instance_id, milestone_id=milestone_id)
        if not m_tasks:
            return
        completed = [t for t in m_tasks if t.status == "COMPLETED"]
        progress = int((len(completed) / len(m_tasks)) * 100)
        m.progress_percent = progress
        if progress == 100:
            m.status = "COMPLETED"
        elif progress > 0 and m.status == "UPCOMING":
            m.status = "IN_PROGRESS"
        await self._milestone_repo.save(m)

    async def _recalculate_project_progress(self, project: ProjectInstanceModel) -> None:
        """Update overall project progress advancing towards 100%."""
        total = await self._task_repo.count_by_project(project.id)
        if total == 0:
            return
        completed = await self._task_repo.count_completed_by_project(project.id)
        # Stage 3/Execution baseline is 35%. Remaining 65% scaled with task completion
        project.progress_percentage = min(100, 35 + int(0.65 * ((completed / total) * 100)))
        await self._project_repo.save(project)
