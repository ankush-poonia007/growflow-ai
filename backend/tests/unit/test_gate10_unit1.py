"""
GrowFlow — Gate 10 Unit 1: Blueprint Approval & Safe Execution Materialization Tests.

Covers:
1. Blueprint Approval Lifecycle Transition (Part A & D):
   - Approving an eligible blueprint transitions project from BLUEPRINT to PLANNING
   - ProjectService.transition_phase is invoked canonically
   - BLUEPRINT_APPROVED domain event is emitted
   - Downstream failure in phase transition propagates and halts the approval flow
2. Execution Materialization Safety (Part B):
   - Non-approved blueprint (READY_FOR_APPROVAL, GENERATED, VALIDATING) skips materialization
   - Approved blueprint (APPROVED) triggers materialization of milestones, tasks, risks, documents
   - Missing blueprint or empty content skips materialization
   - Existing records guard idempotency
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
import uuid

import pytest

from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.application.services.execution_service import ExecutionService
from backend.app.application.services.outbox_service import OutboxService
from backend.app.application.services.project_service import ProjectService
from backend.app.domain.blueprint.models import (
    BlueprintQAStatus,
    BlueprintStatus,
)
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.domain.project.models import ProjectHealth, ProjectPhase
from backend.app.infrastructure.database.models.blueprint import BlueprintModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.repositories.assessment_repository import AssessmentRepository
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
from backend.app.infrastructure.repositories.execution_repository import (
    DocumentRepository,
    MilestoneRepository,
    RiskRepository,
    TaskRepository,
)
from backend.app.infrastructure.repositories.group_repository import GroupRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import BusinessRuleException

# ============================================================================
# FIXTURES & HELPERS
# ============================================================================


def _create_student_user(user_id: uuid.UUID | None = None) -> CurrentUser:
    uid = user_id or uuid.uuid4()
    return CurrentUser(
        user_id=uid,
        email="student@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        full_name="Alex Student",
    )


def _create_project_model(
    project_id: uuid.UUID,
    student_id: uuid.UUID,
    phase: ProjectPhase = ProjectPhase.BLUEPRINT,
) -> ProjectInstanceModel:
    return ProjectInstanceModel(
        id=project_id,
        student_id=str(student_id),
        name="AI Healthcare Triage",
        problem="Slow emergency room triage",
        proposed_solution="AI-driven priority queue",
        current_phase=phase.value,
        health=ProjectHealth.HEALTHY.value,
    )


def _create_blueprint_model(
    project_id: uuid.UUID,
    student_id: uuid.UUID,
    status: BlueprintStatus = BlueprintStatus.READY_FOR_APPROVAL,
    qa_status: BlueprintQAStatus = BlueprintQAStatus.PASS,
    content: dict | None = None,
) -> BlueprintModel:
    bp = BlueprintModel()
    bp.id = str(uuid.uuid4())
    bp.project_instance_id = str(project_id)
    bp.student_id = str(student_id)
    bp.status = status.value
    bp.qa_status = qa_status.value
    bp.qa_score = 92
    bp.generation_number = 1
    bp.content = content if content is not None else {
        "milestones": {
            "milestones_schedule": [
                {"gate": "M1", "name": "Scaffolding & DB", "deliverable": "Core tables setup"},
                {"gate": "M2", "name": "Core Service Logic", "deliverable": "APIs functional"},
            ]
        },
        "tasks": {
            "tasks_breakdown": [
                {
                    "title": "Configure Postgres",
                    "description": "Initialize schema",
                    "category": "BACKEND",
                    "priority": "HIGH",
                    "estimated_hours": 4,
                    "target_milestone_gate": "M1",
                },
                {
                    "title": "Build Auth Endpoints",
                    "description": "JWT authentication",
                    "category": "BACKEND",
                    "priority": "CRITICAL",
                    "estimated_hours": 6,
                    "target_milestone_gate": "M2",
                },
            ]
        },
        "risks": {
            "technical_risks": [
                {
                    "title": "Database latency under load",
                    "impact": "HIGH",
                    "likelihood": "LOW",
                    "mitigation": "Add Redis caching",
                }
            ]
        },
    }
    bp.created_at = datetime.now(UTC)
    bp.updated_at = datetime.now(UTC)
    return bp


# ============================================================================
# PART A & D: BLUEPRINT APPROVAL -> PROJECT PLANNING & ATOMICITY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_approve_blueprint_transitions_project_to_planning():
    """Authoritative blueprint approval must transition project from BLUEPRINT to PLANNING."""
    student_user = _create_student_user()
    project_id = uuid.uuid4()
    project = _create_project_model(project_id, student_user.user_id, ProjectPhase.BLUEPRINT)
    blueprint = _create_blueprint_model(project_id, student_user.user_id)

    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_assessment_repo = AsyncMock(spec=AssessmentRepository)
    mock_project_service = AsyncMock(spec=ProjectService)
    mock_outbox_service = AsyncMock(spec=OutboxService)

    # Repository returns project and blueprint
    mock_project_repo.get_by_id.return_value = project
    mock_blueprint_repo.get_by_project_id.return_value = blueprint

    async def _mock_approve(bp):
        bp.status = BlueprintStatus.APPROVED.value
        bp.approved_at = datetime.now(UTC)
        return bp

    mock_blueprint_repo.approve_blueprint.side_effect = _mock_approve

    service = BlueprintService(
        blueprint_repo=mock_blueprint_repo,
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
        project_service=mock_project_service,
        outbox_service=mock_outbox_service,
    )

    result = await service.approve_blueprint(project_id, student_user)

    # 1. Assert blueprint status and approval timestamp
    assert result.status == BlueprintStatus.APPROVED
    assert result.approved_at is not None

    # 2. Assert ProjectService.transition_phase was called with canonical PLANNING
    mock_project_service.transition_phase.assert_awaited_once_with(
        project.id,
        student_user,
        ProjectPhase.PLANNING.value,
        reason="Blueprint approved by student. Entering execution planning phase.",
    )

    # 3. Assert outbox event BLUEPRINT_APPROVED was emitted
    mock_outbox_service.emit.assert_awaited_once()
    assert mock_outbox_service.emit.call_args.kwargs["event_type"] == DomainEventType.BLUEPRINT_APPROVED.value
    assert mock_outbox_service.emit.call_args.kwargs["project_instance_id"] == project.id


@pytest.mark.asyncio
async def test_approve_blueprint_failure_in_transition_halts_approval():
    """If project phase transition fails, approval must raise and not emit outbox events."""
    student_user = _create_student_user()
    project_id = uuid.uuid4()
    project = _create_project_model(project_id, student_user.user_id, ProjectPhase.BLUEPRINT)
    blueprint = _create_blueprint_model(project_id, student_user.user_id)

    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_assessment_repo = AsyncMock(spec=AssessmentRepository)
    mock_project_service = AsyncMock(spec=ProjectService)
    mock_outbox_service = AsyncMock(spec=OutboxService)

    mock_project_repo.get_by_id.return_value = project
    mock_blueprint_repo.get_by_project_id.return_value = blueprint

    async def _mock_approve(bp):
        bp.status = BlueprintStatus.APPROVED.value
        bp.approved_at = datetime.now(UTC)
        return bp

    mock_blueprint_repo.approve_blueprint.side_effect = _mock_approve

    # Simulate phase transition rejection (e.g. invalid state machine transition)
    mock_project_service.transition_phase.side_effect = BusinessRuleException(
        "Invalid phase transition from 'BLUEPRINT' to 'PLANNING'.",
        code="PROJECT_INVALID_PHASE_TRANSITION",
    )

    service = BlueprintService(
        blueprint_repo=mock_blueprint_repo,
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
        project_service=mock_project_service,
        outbox_service=mock_outbox_service,
    )

    with pytest.raises(BusinessRuleException) as exc_info:
        await service.approve_blueprint(project_id, student_user)

    assert exc_info.value.code == "PROJECT_INVALID_PHASE_TRANSITION"
    # Verify outbox event was NEVER emitted due to failure
    mock_outbox_service.emit.assert_not_awaited()


# ============================================================================
# PART B: APPROVED-ONLY EXECUTION MATERIALIZATION TESTS
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "unapproved_status",
    [
        BlueprintStatus.READY_FOR_APPROVAL,
        BlueprintStatus.GENERATED,
        BlueprintStatus.GENERATING,
        BlueprintStatus.VALIDATING,
        BlueprintStatus.QA_REJECTED,
        BlueprintStatus.NOT_STARTED,
        BlueprintStatus.FAILED,
    ],
)
async def test_ensure_initialized_skips_when_blueprint_not_approved(unapproved_status: BlueprintStatus):
    """ensure_initialized must not materialize records if blueprint is not in APPROVED state."""
    student_user = _create_student_user()
    project_id = uuid.uuid4()
    project = _create_project_model(project_id, student_user.user_id, ProjectPhase.BLUEPRINT)
    blueprint = _create_blueprint_model(project_id, student_user.user_id, status=unapproved_status)

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_doc_repo = AsyncMock(spec=DocumentRepository)
    mock_outbox_service = AsyncMock(spec=OutboxService)

    mock_project_repo.get_by_id.return_value = project
    mock_milestone_repo.count_by_project.return_value = 0
    mock_task_repo.count_by_project.return_value = 0
    mock_blueprint_repo.get_latest_by_project.return_value = blueprint

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        blueprint_repo=mock_blueprint_repo,
        milestone_repo=mock_milestone_repo,
        task_repo=mock_task_repo,
        risk_repo=mock_risk_repo,
        document_repo=mock_doc_repo,
        outbox_service=mock_outbox_service,
    )

    await service.ensure_initialized(project_id, student_user)

    # Verify no execution entities were created
    mock_milestone_repo.bulk_create.assert_not_awaited()
    mock_task_repo.bulk_create.assert_not_awaited()
    mock_risk_repo.bulk_create.assert_not_awaited()
    mock_doc_repo.bulk_create.assert_not_awaited()


@pytest.mark.asyncio
async def test_ensure_initialized_materializes_when_blueprint_approved():
    """ensure_initialized must materialize milestones, tasks, risks, and documents when APPROVED."""
    student_user = _create_student_user()
    project_id = uuid.uuid4()
    project = _create_project_model(project_id, student_user.user_id, ProjectPhase.PLANNING)
    blueprint = _create_blueprint_model(project_id, student_user.user_id, status=BlueprintStatus.APPROVED)

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_doc_repo = AsyncMock(spec=DocumentRepository)
    mock_outbox_service = AsyncMock(spec=OutboxService)

    mock_project_repo.get_by_id.return_value = project
    mock_milestone_repo.count_by_project.return_value = 0
    mock_task_repo.count_by_project.return_value = 0
    mock_doc_repo.count_by_project.return_value = 0
    mock_blueprint_repo.get_latest_by_project.return_value = blueprint

    mock_milestone_repo.bulk_create.side_effect = lambda items: items
    mock_task_repo.bulk_create.side_effect = lambda items: items
    mock_risk_repo.bulk_create.side_effect = lambda items: items

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        blueprint_repo=mock_blueprint_repo,
        milestone_repo=mock_milestone_repo,
        task_repo=mock_task_repo,
        risk_repo=mock_risk_repo,
        document_repo=mock_doc_repo,
        outbox_service=mock_outbox_service,
    )

    await service.ensure_initialized(project_id, student_user)

    # Verify materialization occurred
    mock_milestone_repo.bulk_create.assert_awaited_once()
    created_milestones = mock_milestone_repo.bulk_create.call_args[0][0]
    assert len(created_milestones) == 2
    assert created_milestones[0].gate_code == "M1"
    assert created_milestones[1].gate_code == "M2"

    mock_task_repo.bulk_create.assert_awaited_once()
    created_tasks = mock_task_repo.bulk_create.call_args[0][0]
    assert len(created_tasks) == 2
    # Verify deterministic milestone linkage
    assert created_tasks[0].milestone_id == created_milestones[0].id
    assert created_tasks[1].milestone_id == created_milestones[1].id

    mock_risk_repo.bulk_create.assert_awaited_once()
    created_risks = mock_risk_repo.bulk_create.call_args[0][0]
    assert len(created_risks) == 1
    assert created_risks[0].title == "Database latency under load"
    assert created_risks[0].mitigation == "Add Redis caching"

    # Verify initial documents were seeded
    mock_doc_repo.bulk_create.assert_awaited_once()


@pytest.mark.asyncio
async def test_ensure_initialized_skips_when_no_blueprint_or_no_content():
    """ensure_initialized must safely do nothing when no blueprint exists or content is empty."""
    student_user = _create_student_user()
    project_id = uuid.uuid4()
    project = _create_project_model(project_id, student_user.user_id, ProjectPhase.PLANNING)

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_doc_repo = AsyncMock(spec=DocumentRepository)
    mock_outbox_service = AsyncMock(spec=OutboxService)

    mock_project_repo.get_by_id.return_value = project
    mock_milestone_repo.count_by_project.return_value = 0
    mock_task_repo.count_by_project.return_value = 0

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        blueprint_repo=mock_blueprint_repo,
        milestone_repo=mock_milestone_repo,
        task_repo=mock_task_repo,
        risk_repo=mock_risk_repo,
        document_repo=mock_doc_repo,
        outbox_service=mock_outbox_service,
    )

    # 1. No blueprint at all
    mock_blueprint_repo.get_latest_by_project.return_value = None
    await service.ensure_initialized(project_id, student_user)
    mock_milestone_repo.bulk_create.assert_not_awaited()

    # 2. Blueprint exists but has empty content
    empty_bp = _create_blueprint_model(project_id, student_user.user_id, status=BlueprintStatus.APPROVED, content={})
    mock_blueprint_repo.get_latest_by_project.return_value = empty_bp
    await service.ensure_initialized(project_id, student_user)
    mock_milestone_repo.bulk_create.assert_not_awaited()


@pytest.mark.asyncio
async def test_ensure_initialized_idempotency_when_records_already_exist():
    """ensure_initialized must exit early without querying blueprint if records exist."""
    student_user = _create_student_user()
    project_id = uuid.uuid4()
    project = _create_project_model(project_id, student_user.user_id, ProjectPhase.PLANNING)

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_doc_repo = AsyncMock(spec=DocumentRepository)
    mock_outbox_service = AsyncMock(spec=OutboxService)

    mock_project_repo.get_by_id.return_value = project
    mock_milestone_repo.count_by_project.return_value = 3
    mock_task_repo.count_by_project.return_value = 5

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        blueprint_repo=mock_blueprint_repo,
        milestone_repo=mock_milestone_repo,
        task_repo=mock_task_repo,
        risk_repo=mock_risk_repo,
        document_repo=mock_doc_repo,
        outbox_service=mock_outbox_service,
    )

    await service.ensure_initialized(project_id, student_user)

    # Should not even fetch the blueprint
    mock_blueprint_repo.get_latest_by_project.assert_not_awaited()
    mock_milestone_repo.bulk_create.assert_not_awaited()
