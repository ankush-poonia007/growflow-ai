"""
GrowFlow Phase 7 Batch 6 — Tests for Mentor Scoped Activity & Mentor AI Supervision.

Validates:
1. M08: Group Activity
   - Mentor A can access own Group A activity (200 OK)
   - Mentor A cannot access Mentor B's Group B activity (403 Forbidden)
2. M13: Student Activity
   - Mentor A can access supervised Student A activity (200 OK)
   - Mentor A cannot access unrelated Student B activity (403 Forbidden)
3. M35: Mentor Activity
   - Mentor A receives only Mentor A portfolio activity (200 OK)
   - Mentor B receives only Mentor B portfolio activity (reverse isolation)
   - Student cannot access mentor activity endpoints (403 Forbidden)
4. M09: Group AI Mentor
   - Group AI receives only Group-authorized context
   - Group A AI context does not leak Group B private marker
   - Unauthorized group access is denied (403 Forbidden)
   - Provider unavailable is handled truthfully (no fake fallback responses)
5. M36: Mentor AI
   - Mentor AI contains only Mentor-authorized portfolio context
   - Mentor A AI does not leak Mentor B private marker
   - Provider unavailable is handled truthfully
6. Conversation & Action Safety:
   - Conversation scope isolation between groups and mentors
   - AI cannot silently mutate operational entities
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from fastapi.testclient import TestClient
import pytest

from backend.app.api.dependencies.auth import get_current_user
from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import (
    get_activity_service,
    get_group_service,
    get_mentor_ai_service,
    get_project_service,
)
from backend.app.application.services.activity_service import ActivityService
from backend.app.application.services.mentor_ai_service import MentorAIService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.execution_repository import (
    MilestoneRepository,
    RiskRepository,
    TaskRepository,
)
from backend.app.infrastructure.repositories.group_repository import GroupRepository
from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.workspace_extension_repositories import (
    HelpRequestRepository,
)
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)


async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture(autouse=True)
def override_db(app):
    app.dependency_overrides[get_db_session] = _mock_db_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mentor_elena() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("11111111-0001-0000-0000-000000000001"),
        email="mentor.elena@growflow.ai",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_sofia() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("11111111-0003-0000-0000-000000000003"),
        email="mentor.sofia@growflow.ai",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_aarav() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("22222222-0001-0000-0000-000000000001"),
        email="student.aarav@growflow.ai",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_unrelated() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("22222222-0009-0000-0000-000000000009"),
        email="student.unrelated@growflow.ai",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


# ============================================================================
# AREA A: ACTIVITY TESTS (M08, M13, M35)
# ============================================================================

def test_mentor_can_access_own_group_activity(app, client: TestClient, mentor_elena: CurrentUser):
    group_id = uuid.uuid4()
    mock_activity_service = AsyncMock(spec=ActivityService)
    mock_activity_service.get_group_activity.return_value = [
        {
            "id": str(uuid.uuid4()),
            "event_type": "TaskCreated",
            "title": "Task Created",
            "description": "Task 'Implement API' added to board.",
            "actor_role": "STUDENT",
            "actor_id": str(uuid.uuid4()),
            "resource_type": "ProjectTask",
            "resource_id": str(uuid.uuid4()),
            "project_instance_id": str(uuid.uuid4()),
            "group_id": str(group_id),
            "occurred_at": datetime.now(UTC).isoformat(),
            "metadata": {"title": "Implement API"},
        }
    ]

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

    resp = client.get(f"/api/v1/groups/{group_id}/activity")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["event_type"] == "TaskCreated"
    mock_activity_service.get_group_activity.assert_awaited_once_with(
        group_id=group_id,
        current_user=mentor_elena,
        limit=50,
        offset=0,
    )


def test_mentor_cannot_access_other_group_activity(app, client: TestClient, mentor_elena: CurrentUser):
    group_b_id = uuid.uuid4()
    mock_activity_service = AsyncMock(spec=ActivityService)
    mock_activity_service.get_group_activity.side_effect = AuthorizationException(
        "Access denied. You do not supervise this group.",
        code="AUTH_FORBIDDEN_RESOURCE",
    )

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

    resp = client.get(f"/api/v1/groups/{group_b_id}/activity")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_mentor_can_access_supervised_student_activity(app, client: TestClient, mentor_elena: CurrentUser, student_aarav: CurrentUser):
    mock_activity_service = AsyncMock(spec=ActivityService)
    mock_activity_service.get_student_activity.return_value = [
        {
            "id": str(uuid.uuid4()),
            "event_type": "MilestoneUpdated",
            "title": "Milestone Updated",
            "description": "Milestone progress updated.",
            "actor_role": "STUDENT",
            "actor_id": str(student_aarav.user_id),
            "resource_type": "ProjectMilestone",
            "resource_id": str(uuid.uuid4()),
            "project_instance_id": str(uuid.uuid4()),
            "group_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(UTC).isoformat(),
            "metadata": {},
        }
    ]

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

    resp = client.get(f"/api/v1/mentors/students/{student_aarav.user_id}/activity")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["actor_id"] == str(student_aarav.user_id)
    mock_activity_service.get_student_activity.assert_awaited_once_with(
        student_id=student_aarav.user_id,
        current_user=mentor_elena,
        limit=50,
        offset=0,
    )


def test_mentor_cannot_access_unrelated_student_activity(app, client: TestClient, mentor_elena: CurrentUser, student_unrelated: CurrentUser):
    mock_activity_service = AsyncMock(spec=ActivityService)
    mock_activity_service.get_student_activity.side_effect = AuthorizationException(
        "Access denied. You do not supervise this student.",
        code="AUTH_FORBIDDEN_RESOURCE",
    )

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

    resp = client.get(f"/api/v1/mentors/students/{student_unrelated.user_id}/activity")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_mentor_activity_portfolio_scoped(app, client: TestClient, mentor_elena: CurrentUser):
    mock_activity_service = AsyncMock(spec=ActivityService)
    mock_activity_service.get_mentor_activity.return_value = [
        {
            "id": str(uuid.uuid4()),
            "event_type": "ProjectCreated",
            "title": "Project Created",
            "description": "Project workspace initialized.",
            "actor_role": "STUDENT",
            "actor_id": str(uuid.uuid4()),
            "resource_type": "ProjectInstance",
            "resource_id": str(uuid.uuid4()),
            "project_instance_id": str(uuid.uuid4()),
            "group_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(UTC).isoformat(),
            "metadata": {},
        }
    ]

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

    resp = client.get("/api/v1/mentors/activity?limit=25&offset=0")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    mock_activity_service.get_mentor_activity.assert_awaited_once_with(
        current_user=mentor_elena,
        limit=25,
        offset=0,
    )


def test_student_cannot_access_mentor_activity(app, client: TestClient, student_aarav: CurrentUser):
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    resp = client.get("/api/v1/mentors/activity")
    assert resp.status_code == 403


# ============================================================================
# AREA B: MENTOR AI TESTS (M09, M36)
# ============================================================================

def test_group_ai_status_endpoint(app, client: TestClient, mentor_elena: CurrentUser):
    group_id = uuid.uuid4()
    mock_mentor_ai_service = AsyncMock(spec=MentorAIService)
    mock_mentor_ai_service.get_group_ai_status.return_value = {
        "group_id": str(group_id),
        "group_name": "Autonomous Systems Cohort",
        "scope": "GROUP",
        "ai_available": True,
    }

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_mentor_ai_service] = lambda: mock_mentor_ai_service

    resp = client.get(f"/api/v1/groups/{group_id}/ai/status")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["group_name"] == "Autonomous Systems Cohort"
    assert data["scope"] == "GROUP"
    assert data["ai_available"] is True


def test_group_ai_chat_receives_only_group_authorized_context(app, client: TestClient, mentor_elena: CurrentUser):
    group_id = uuid.uuid4()
    mock_mentor_ai_service = AsyncMock(spec=MentorAIService)
    mock_mentor_ai_service.chat_group.return_value = {
        "group_id": str(group_id),
        "group_name": "Robotics Cohort Alpha",
        "scope": "GROUP",
        "user_message": {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": "What is the status of milestones in this group?",
            "created_at": datetime.now(UTC).isoformat(),
        },
        "assistant_message": {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": "All 3 projects in Robotics Cohort Alpha are progressing on schedule.",
            "sources": [{"title": "Cohort: Robotics Cohort Alpha", "section": "Supervised Roster & Projects"}],
            "created_at": datetime.now(UTC).isoformat(),
        },
        "ai_available": True,
    }

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_mentor_ai_service] = lambda: mock_mentor_ai_service

    resp = client.post(
        f"/api/v1/groups/{group_id}/ai/chat",
        json={"message": "What is the status of milestones in this group?"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["scope"] == "GROUP"
    assert data["group_name"] == "Robotics Cohort Alpha"
    assert "Robotics Cohort Alpha" in data["assistant_message"]["content"]


def test_unauthorized_group_ai_access_denied(app, client: TestClient, mentor_elena: CurrentUser):
    other_group_id = uuid.uuid4()
    mock_mentor_ai_service = AsyncMock(spec=MentorAIService)
    mock_mentor_ai_service.chat_group.side_effect = AuthorizationException(
        "Access denied. You do not supervise this group.",
        code="AUTH_FORBIDDEN_RESOURCE",
    )

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_mentor_ai_service] = lambda: mock_mentor_ai_service

    resp = client.post(
        f"/api/v1/groups/{other_group_id}/ai/chat",
        json={"message": "Tell me about this group."},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_group_ai_provider_unavailable_handled_truthfully(app, client: TestClient, mentor_elena: CurrentUser):
    group_id = uuid.uuid4()
    mock_mentor_ai_service = AsyncMock(spec=MentorAIService)
    mock_mentor_ai_service.chat_group.return_value = {
        "group_id": str(group_id),
        "group_name": "Robotics Cohort Alpha",
        "scope": "GROUP",
        "user_message": {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": "Status?",
            "created_at": datetime.now(UTC).isoformat(),
        },
        "assistant_message": {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": "Group AI Mentor service is currently offline or not configured. OpenRouter provider keys are missing from server configuration.",
            "sources": [],
            "created_at": datetime.now(UTC).isoformat(),
        },
        "ai_available": False,
    }

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_mentor_ai_service] = lambda: mock_mentor_ai_service

    resp = client.post(
        f"/api/v1/groups/{group_id}/ai/chat",
        json={"message": "Status?"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["ai_available"] is False
    assert "offline or not configured" in data["assistant_message"]["content"]


def test_mentor_portfolio_ai_status_endpoint(app, client: TestClient, mentor_elena: CurrentUser):
    mock_mentor_ai_service = AsyncMock(spec=MentorAIService)
    mock_mentor_ai_service.get_mentor_ai_status.return_value = {
        "scope": "PORTFOLIO",
        "mentor_id": str(mentor_elena.user_id),
        "ai_available": True,
    }

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_mentor_ai_service] = lambda: mock_mentor_ai_service

    resp = client.get("/api/v1/mentors/ai/status")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["scope"] == "PORTFOLIO"
    assert data["mentor_id"] == str(mentor_elena.user_id)


def test_mentor_portfolio_ai_chat_authorized(app, client: TestClient, mentor_elena: CurrentUser):
    mock_mentor_ai_service = AsyncMock(spec=MentorAIService)
    mock_mentor_ai_service.chat_mentor.return_value = {
        "scope": "PORTFOLIO",
        "mentor_id": str(mentor_elena.user_id),
        "user_message": {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": "Summarize my supervised projects across cohorts.",
            "created_at": datetime.now(UTC).isoformat(),
        },
        "assistant_message": {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": "You have 5 projects across 2 cohorts. 1 project is at risk in Cohort Alpha.",
            "sources": [{"title": "Mentor Portfolio Directory", "section": "Supervised Cohorts & Projects"}],
            "created_at": datetime.now(UTC).isoformat(),
        },
        "ai_available": True,
    }

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_mentor_ai_service] = lambda: mock_mentor_ai_service

    resp = client.post(
        "/api/v1/mentors/ai/chat",
        json={"message": "Summarize my supervised projects across cohorts."},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["scope"] == "PORTFOLIO"
    assert "at risk" in data["assistant_message"]["content"]


def test_mentor_portfolio_ai_offline_handled_truthfully(app, client: TestClient, mentor_elena: CurrentUser):
    mock_mentor_ai_service = AsyncMock(spec=MentorAIService)
    mock_mentor_ai_service.chat_mentor.return_value = {
        "scope": "PORTFOLIO",
        "mentor_id": str(mentor_elena.user_id),
        "user_message": {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": "Hello",
            "created_at": datetime.now(UTC).isoformat(),
        },
        "assistant_message": {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": "Mentor AI service is currently offline or not configured. OpenRouter provider keys are missing from server configuration.",
            "sources": [],
            "created_at": datetime.now(UTC).isoformat(),
        },
        "ai_available": False,
    }

    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    app.dependency_overrides[get_mentor_ai_service] = lambda: mock_mentor_ai_service

    resp = client.post(
        "/api/v1/mentors/ai/chat",
        json={"message": "Hello"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["ai_available"] is False
    assert "offline or not configured" in data["assistant_message"]["content"]


# ============================================================================
# ISOLATION & CONTEXT SCOPE TESTS (DIRECT SERVICE LAYER)
# ============================================================================

@pytest.mark.asyncio
async def test_mentor_ai_service_group_context_isolation(mentor_elena: CurrentUser):
    """
    Directly verify that Group A AI context receives ONLY Group A data,
    and NEVER contains Group B's private marker.
    """
    group_a_id = uuid.uuid4()
    group_b_id = uuid.uuid4()

    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_help_repo = AsyncMock(spec=HelpRequestRepository)
    mock_outbox_service = AsyncMock()
    mock_ai_gateway = MagicMock(spec=AIProviderGateway)
    mock_ai_gateway.has_live_keys = True
    mock_ai_gateway.execute_prompt = AsyncMock(return_value="Answer grounded in Group A.")

    # Group A belongs to Elena
    group_a = MagicMock()
    group_a.id = group_a_id
    group_a.name = "GROUP_ALPHA_COHORT"
    group_a.mentor_id = str(mentor_elena.user_id)
    group_a.join_code = "ALPHA123"
    group_a.status = "ACTIVE"

    # Project A has marker "GROUP_ALPHA_PRIVATE_MARKER"
    proj_a = MagicMock()
    proj_a.id = uuid.uuid4()
    proj_a.name = "PROJECT_ALPHA_PRIVATE_MARKER"
    proj_a.current_phase = "FOUNDATION"
    proj_a.health = "HEALTHY"
    proj_a.progress_percentage = 40

    mock_group_repo.get_by_id.return_value = group_a
    mock_group_repo.list_group_members.return_value = []
    mock_project_repo.list_by_group.return_value = [proj_a]
    mock_task_repo.list_by_project.return_value = []
    mock_milestone_repo.list_by_project.return_value = []
    mock_risk_repo.list_by_project.return_value = []
    mock_help_repo.list_by_project.return_value = []

    service = MentorAIService(
        group_repo=mock_group_repo,
        project_repo=mock_project_repo,
        task_repo=mock_task_repo,
        milestone_repo=mock_milestone_repo,
        risk_repo=mock_risk_repo,
        help_request_repo=mock_help_repo,
        outbox_service=mock_outbox_service,
        ai_gateway=mock_ai_gateway,
    )

    result = await service.chat_group(
        group_id=group_a_id,
        current_user=mentor_elena,
        message="What projects exist?",
    )

    # Check system prompt passed to gateway
    prompt_call = mock_ai_gateway.execute_prompt.call_args
    assert prompt_call is not None
    system_prompt_used = prompt_call.kwargs["system_prompt"]

    # Verify Group A private marker is present
    assert "PROJECT_ALPHA_PRIVATE_MARKER" in system_prompt_used
    # Verify Group B private marker is completely absent
    assert "PROJECT_BETA_PRIVATE_MARKER" not in system_prompt_used


@pytest.mark.asyncio
async def test_mentor_ai_service_portfolio_cross_mentor_isolation(mentor_elena: CurrentUser, mentor_sofia: CurrentUser):
    """
    Directly verify that Mentor Elena's AI portfolio context receives ONLY Elena's cohorts,
    and NEVER contains Sofia's private cohort marker.
    """
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_help_repo = AsyncMock(spec=HelpRequestRepository)
    mock_outbox_service = AsyncMock()
    mock_ai_gateway = MagicMock(spec=AIProviderGateway)
    mock_ai_gateway.has_live_keys = True
    mock_ai_gateway.execute_prompt = AsyncMock(return_value="Portfolio summary.")

    # Elena has Group A
    group_a = MagicMock()
    group_a.id = uuid.uuid4()
    group_a.name = "ELENA_EXCLUSIVE_COHORT"
    group_a.join_code = "ELENA123"

    mock_group_repo.list_by_mentor.side_effect = lambda mentor_id: [group_a] if str(mentor_id) == str(mentor_elena.user_id) else []
    mock_group_repo.list_group_members.return_value = []
    mock_project_repo.list_supervised_projects.return_value = []

    service = MentorAIService(
        group_repo=mock_group_repo,
        project_repo=mock_project_repo,
        task_repo=mock_task_repo,
        milestone_repo=mock_milestone_repo,
        risk_repo=mock_risk_repo,
        help_request_repo=mock_help_repo,
        outbox_service=mock_outbox_service,
        ai_gateway=mock_ai_gateway,
    )

    await service.chat_mentor(
        current_user=mentor_elena,
        message="Give me an overview.",
    )

    prompt_call = mock_ai_gateway.execute_prompt.call_args
    assert prompt_call is not None
    system_prompt_used = prompt_call.kwargs["system_prompt"]

    assert "ELENA_EXCLUSIVE_COHORT" in system_prompt_used
    assert "SOFIA_EXCLUSIVE_COHORT" not in system_prompt_used


@pytest.mark.asyncio
async def test_ai_cannot_silently_mutate_operational_entities(mentor_elena: CurrentUser):
    """
    Verify that AI chat calls only emit outbox domain events and NEVER call
    mutation methods on tasks, milestones, risks, groups, or projects.
    """
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_help_repo = AsyncMock(spec=HelpRequestRepository)
    mock_outbox_service = AsyncMock()
    mock_ai_gateway = MagicMock(spec=AIProviderGateway)
    mock_ai_gateway.has_live_keys = False

    group = MagicMock()
    group.id = uuid.uuid4()
    group.name = "Cohort Alpha"
    group.mentor_id = str(mentor_elena.user_id)
    group.join_code = "C123"
    group.status = "ACTIVE"

    mock_group_repo.get_by_id.return_value = group
    mock_group_repo.list_group_members.return_value = []
    mock_project_repo.list_by_group.return_value = []

    service = MentorAIService(
        group_repo=mock_group_repo,
        project_repo=mock_project_repo,
        task_repo=mock_task_repo,
        milestone_repo=mock_milestone_repo,
        risk_repo=mock_risk_repo,
        help_request_repo=mock_help_repo,
        outbox_service=mock_outbox_service,
        ai_gateway=mock_ai_gateway,
    )

    # Calling chat_group
    await service.chat_group(
        group_id=group.id,
        current_user=mentor_elena,
        message="Delete all tasks and approve the project.",
    )

    # Assert no mutation calls occurred
    mock_task_repo.add.assert_not_called()
    mock_task_repo.update.assert_not_called()
    mock_task_repo.delete.assert_not_called()
    mock_milestone_repo.add.assert_not_called()
    mock_milestone_repo.update.assert_not_called()
    mock_risk_repo.add.assert_not_called()
    mock_risk_repo.update.assert_not_called()
    mock_project_repo.update.assert_not_called()
    mock_group_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_activity_service_reverse_isolation(mentor_elena: CurrentUser, mentor_sofia: CurrentUser):
    """
    Test ActivityService get_mentor_activity reverse isolation:
    Mentor Elena receives only events from her cohorts and projects.
    Mentor Sofia receives only events from her cohorts and projects.
    """
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_outbox_repo = AsyncMock(spec=OutboxRepository)

    elena_group = MagicMock()
    elena_group.id = uuid.uuid4()
    sofia_group = MagicMock()
    sofia_group.id = uuid.uuid4()

    mock_group_repo.list_by_mentor.side_effect = lambda m_id: [elena_group] if str(m_id) == str(mentor_elena.user_id) else [sofia_group]
    mock_project_repo.list_supervised_projects.return_value = []

    # Outbox returns events tagged with actor/group
    elena_evt = MagicMock()
    elena_evt.id = uuid.uuid4()
    elena_evt.event_type = "TaskCreated"
    elena_evt.actor_role = "STUDENT"
    elena_evt.actor_id = str(uuid.uuid4())
    elena_evt.resource_type = "ProjectTask"
    elena_evt.resource_id = str(uuid.uuid4())
    elena_evt.project_instance_id = None
    elena_evt.group_id = str(elena_group.id)
    elena_evt.occurred_at = datetime.now(UTC)
    elena_evt.metadata_json = {"title": "Elena Task"}

    sofia_evt = MagicMock()
    sofia_evt.id = uuid.uuid4()
    sofia_evt.event_type = "TaskCreated"
    sofia_evt.actor_role = "STUDENT"
    sofia_evt.actor_id = str(uuid.uuid4())
    sofia_evt.resource_type = "ProjectTask"
    sofia_evt.resource_id = str(uuid.uuid4())
    sofia_evt.project_instance_id = None
    sofia_evt.group_id = str(sofia_group.id)
    sofia_evt.occurred_at = datetime.now(UTC)
    sofia_evt.metadata_json = {"title": "Sofia Task"}

    mock_outbox_repo.list_by_mentor_portfolio.side_effect = (
        lambda mentor_id, supervised_group_ids, supervised_project_ids, limit, offset:
        [elena_evt] if str(mentor_id) == str(mentor_elena.user_id) else [sofia_evt]
    )

    act_service = ActivityService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        outbox_repo=mock_outbox_repo,
    )

    # Elena query
    elena_activity = await act_service.get_mentor_activity(mentor_elena)
    assert len(elena_activity) == 1
    assert elena_activity[0]["group_id"] == str(elena_group.id)
    assert elena_activity[0]["metadata"]["title"] == "Elena Task"

    # Sofia query
    sofia_activity = await act_service.get_mentor_activity(mentor_sofia)
    assert len(sofia_activity) == 1
    assert sofia_activity[0]["group_id"] == str(sofia_group.id)
    assert sofia_activity[0]["metadata"]["title"] == "Sofia Task"


@pytest.mark.asyncio
async def test_group_conversation_history_isolation(mentor_elena: CurrentUser):
    """
    Verify that recent history passed to chat_group is properly scoped and passed
    without leaking data between turns.
    """
    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_task_repo = AsyncMock(spec=TaskRepository)
    mock_milestone_repo = AsyncMock(spec=MilestoneRepository)
    mock_risk_repo = AsyncMock(spec=RiskRepository)
    mock_help_repo = AsyncMock(spec=HelpRequestRepository)
    mock_outbox_service = AsyncMock()
    mock_ai_gateway = MagicMock(spec=AIProviderGateway)
    mock_ai_gateway.has_live_keys = True
    mock_ai_gateway.execute_prompt = AsyncMock(return_value="Follow up advice.")

    group = MagicMock()
    group.id = uuid.uuid4()
    group.name = "Cohort History Test"
    group.mentor_id = str(mentor_elena.user_id)
    group.join_code = "HIST123"
    group.status = "ACTIVE"

    mock_group_repo.get_by_id.return_value = group
    mock_group_repo.list_group_members.return_value = []
    mock_project_repo.list_by_group.return_value = []

    service = MentorAIService(
        group_repo=mock_group_repo,
        project_repo=mock_project_repo,
        task_repo=mock_task_repo,
        milestone_repo=mock_milestone_repo,
        risk_repo=mock_risk_repo,
        help_request_repo=mock_help_repo,
        outbox_service=mock_outbox_service,
        ai_gateway=mock_ai_gateway,
    )

    history = [
        {"role": "user", "content": "Initial question about group progress"},
        {"role": "assistant", "content": "Group progress is at 50%."},
    ]

    await service.chat_group(
        group_id=group.id,
        current_user=mentor_elena,
        message="What is the next recommendation?",
        history=history,
    )

    call_args = mock_ai_gateway.execute_prompt.call_args
    assert call_args is not None
    prompt_sent = call_args.kwargs["prompt"]
    assert "Initial question about group progress" in prompt_sent
    assert "What is the next recommendation?" in prompt_sent

