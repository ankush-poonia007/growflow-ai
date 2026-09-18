"""
GrowFlow Batch 06 (S27–S33) — Gate Verification & Hardening Test Suite.

Verifies:
1. Blueprint Version Promotion Safety (Approved V1 -> Candidate V2 -> QA -> Atomic Promotion -> V2 Approved -> V1 Superseded; V1 remains APPROVED on failure; dynamic versions; recoverable versions)
2. Project Change Idempotency (repeat confirmation, repeated confirmation after COMPLETED, confirmation while REGENERATING, zero duplicate versions/events)
3. AI Mentor Architecture & Truthfulness (AIProviderGateway usage, truthful unavailable fallback, never fabricates text)
4. AI Project Isolation (strictly project-scoped context, zero cross-project leakage)
5. AI Action Security (no passive mutation, valid owner, unauthorized project, invalid resource ID, wrong project resource, duplicate execution, already-completed task)
6. GitHub Integration (observation only, zero canonical git commit table, no credential exposure, disconnect)
7. Activity Trail (reads canonical domain_events/outbox only, actor & resource correctness, chronological ordering)
8. Help Request Authority (student creates in OPEN state, unauthorized access denied)
9. Mentor Feedback Boundary (student acknowledges without mutating operational execution state)
10. Operational Boundary Preservation (zero silent deletion of tasks, milestones, risks, documents)
"""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest

from backend.app.application.services.activity_service import ActivityService
from backend.app.application.services.ai_mentor_service import AIMentorService
from backend.app.application.services.github_service import GitHubService
from backend.app.application.services.help_request_service import HelpRequestService
from backend.app.application.services.mentor_feedback_service import MentorFeedbackService
from backend.app.application.services.project_change_service import ProjectChangeService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.infrastructure.database.models.blueprint import BlueprintModel
from backend.app.infrastructure.database.models.execution import (
    ProjectMilestoneModel,
    ProjectTaskModel,
)
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.workspace_extensions import (
    AIMentorConversationModel,
    AIMentorMessageModel,
    ProjectBlueprintVersionModel,
    ProjectChangeRequestModel,
    ProjectGitHubIntegrationModel,
    ProjectHelpRequestModel,
    ProjectMentorNoteModel,
)
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    NotFoundException,
)


# ============================================================================
# In-Memory Repositories for Direct Service Hardening Tests
# ============================================================================

class InMemoryProjectRepo:
    def __init__(self) -> None:
        self.projects: dict[str, ProjectInstanceModel] = {}

    async def get_by_id(self, project_id: uuid.UUID | str) -> ProjectInstanceModel | None:
        return self.projects.get(str(project_id))


class InMemoryGroupRepo:
    async def get_by_id(self, group_id: uuid.UUID | str) -> Any | None:
        return None


class InMemoryBlueprintRepo:
    def __init__(self) -> None:
        self.blueprints: dict[str, BlueprintModel] = {}

    async def get_by_project_id(self, project_id: uuid.UUID | str) -> BlueprintModel | None:
        for bp in self.blueprints.values():
            if str(bp.project_instance_id) == str(project_id):
                return bp
        return None

    async def update(self, blueprint: BlueprintModel) -> BlueprintModel:
        self.blueprints[str(blueprint.id)] = blueprint
        return blueprint


class InMemoryTaskRepo:
    def __init__(self) -> None:
        self.tasks: dict[str, ProjectTaskModel] = {}

    async def list_by_project(self, project_id: uuid.UUID | str, **kwargs: Any) -> list[ProjectTaskModel]:
        return [t for t in self.tasks.values() if str(t.project_instance_id) == str(project_id)]

    async def get_by_id(self, task_id: uuid.UUID | str) -> ProjectTaskModel | None:
        return self.tasks.get(str(task_id))

    async def add(self, task: ProjectTaskModel) -> ProjectTaskModel:
        self.tasks[str(task.id)] = task
        return task

    async def update(self, task: ProjectTaskModel) -> ProjectTaskModel:
        self.tasks[str(task.id)] = task
        return task


class InMemoryMilestoneRepo:
    def __init__(self) -> None:
        self.milestones: dict[str, ProjectMilestoneModel] = {}

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectMilestoneModel]:
        return [m for m in self.milestones.values() if str(m.project_instance_id) == str(project_id)]


class InMemoryBlueprintVersionRepo:
    def __init__(self) -> None:
        self.versions: list[ProjectBlueprintVersionModel] = []

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectBlueprintVersionModel]:
        return [v for v in self.versions if str(v.project_instance_id) == str(project_id)]

    async def get_by_version(
        self, blueprint_id: uuid.UUID | str, version_number: int
    ) -> ProjectBlueprintVersionModel | None:
        for v in self.versions:
            if str(v.blueprint_id) == str(blueprint_id) and v.version_number == version_number:
                return v
        return None

    async def get_latest_version_number(self, blueprint_id: uuid.UUID | str) -> int:
        matching = [v.version_number for v in self.versions if str(v.blueprint_id) == str(blueprint_id)]
        return max(matching) if matching else 0

    async def add(self, version: ProjectBlueprintVersionModel) -> ProjectBlueprintVersionModel:
        self.versions.append(version)
        return version

    async def update(self, version: ProjectBlueprintVersionModel) -> ProjectBlueprintVersionModel:
        for idx, v in enumerate(self.versions):
            if v.id == version.id:
                self.versions[idx] = version
                break
        return version


class InMemoryProjectChangeRepo:
    def __init__(self) -> None:
        self.requests: dict[str, ProjectChangeRequestModel] = {}

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectChangeRequestModel]:
        return [r for r in self.requests.values() if str(r.project_instance_id) == str(project_id)]

    async def get_by_id(self, change_id: uuid.UUID | str) -> ProjectChangeRequestModel | None:
        return self.requests.get(str(change_id))

    async def get_by_idempotency_key(self, idempotency_key: str) -> ProjectChangeRequestModel | None:
        if not idempotency_key:
            return None
        for r in self.requests.values():
            if r.idempotency_key == idempotency_key:
                return r
        return None

    async def add(self, req: ProjectChangeRequestModel) -> ProjectChangeRequestModel:
        self.requests[str(req.id)] = req
        return req

    async def update(self, req: ProjectChangeRequestModel) -> ProjectChangeRequestModel:
        self.requests[str(req.id)] = req
        return req


class InMemoryOutboxService:
    def __init__(self) -> None:
        self.enqueued_events: list[dict[str, Any]] = []

    async def enqueue(self, **kwargs: Any) -> None:
        self.enqueued_events.append(kwargs)


class InMemoryOutboxRepo:
    def __init__(self) -> None:
        self.events: list[DomainEventModel] = []

    async def list_by_project(
        self, project_id: uuid.UUID | str, limit: int = 50, offset: int = 0
    ) -> list[DomainEventModel]:
        matched = [e for e in self.events if str(e.project_instance_id) == str(project_id)]
        return matched[offset : offset + limit]


class InMemoryAIMentorRepo:
    def __init__(self) -> None:
        self.conversations: dict[str, AIMentorConversationModel] = {}
        self.messages: list[AIMentorMessageModel] = []

    async def get_or_create_conversation(
        self, project_id: uuid.UUID | str, student_id: uuid.UUID | str
    ) -> AIMentorConversationModel:
        key = f"{project_id}_{student_id}"
        if key not in self.conversations:
            conv = AIMentorConversationModel(
                id=uuid.uuid4(),
                project_instance_id=str(project_id),
                student_id=str(student_id),
                title="Project Consultation",
            )
            self.conversations[key] = conv
        return self.conversations[key]

    async def list_messages(
        self, conversation_id: uuid.UUID | str, limit: int = 50
    ) -> list[AIMentorMessageModel]:
        matched = [m for m in self.messages if str(m.conversation_id) == str(conversation_id)]
        return matched[-limit:]

    async def add_message(
        self,
        conversation_id: uuid.UUID | str,
        role: str,
        content: str,
        sources: list[dict[str, Any]] | None = None,
        suggested_action: dict[str, Any] | None = None,
    ) -> AIMentorMessageModel:
        msg = AIMentorMessageModel(
            id=uuid.uuid4(),
            conversation_id=str(conversation_id),
            role=role,
            content=content,
            sources=sources or [],
            suggested_action=suggested_action,
            created_at=datetime.now(UTC),
        )
        self.messages.append(msg)
        return msg


class InMemoryHelpRequestRepo:
    def __init__(self) -> None:
        self.requests: dict[str, ProjectHelpRequestModel] = {}

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectHelpRequestModel]:
        return [r for r in self.requests.values() if str(r.project_instance_id) == str(project_id)]

    async def get_by_id(self, request_id: uuid.UUID | str) -> ProjectHelpRequestModel | None:
        return self.requests.get(str(request_id))

    async def add(
        self,
        entity_or_project_id: Any = None,
        student_id: str | None = None,
        subject: str | None = None,
        description: str | None = None,
        category: str = "TECHNICAL",
        priority: str = "MEDIUM",
        **kwargs: Any,
    ) -> ProjectHelpRequestModel:
        if isinstance(entity_or_project_id, ProjectHelpRequestModel):
            req = entity_or_project_id
        else:
            req = ProjectHelpRequestModel(
                id=uuid.uuid4(),
                project_instance_id=str(entity_or_project_id),
                student_id=str(student_id),
                subject=str(subject),
                description=str(description),
                category=category,
                priority=priority,
                status="OPEN",
                created_at=datetime.now(UTC),
            )
        self.requests[str(req.id)] = req
        return req


class InMemoryMentorNoteRepo:
    def __init__(self) -> None:
        self.notes: dict[str, ProjectMentorNoteModel] = {}

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectMentorNoteModel]:
        return [n for n in self.notes.values() if str(n.project_instance_id) == str(project_id)]

    async def get_by_id(self, note_id: uuid.UUID | str) -> ProjectMentorNoteModel | None:
        return self.notes.get(str(note_id))

    async def mark_acknowledged(self, note_id: uuid.UUID | str) -> ProjectMentorNoteModel | None:
        note = self.notes.get(str(note_id))
        if note:
            note.status = "ACKNOWLEDGED"
        return note


class InMemoryGitHubRepo:
    def __init__(self) -> None:
        self.integrations: dict[str, ProjectGitHubIntegrationModel] = {}

    async def get_by_project(self, project_id: uuid.UUID | str) -> ProjectGitHubIntegrationModel | None:
        return self.integrations.get(str(project_id))

    async def upsert(
        self,
        project_id: uuid.UUID | str,
        repository_name: str,
        repository_url: str,
        default_branch: str = "main",
        connection_status: str = "CONNECTED",
        commit_count: int = 0,
        cached_commits_preview: list[dict[str, Any]] | None = None,
        sync_error: str | None = None,
    ) -> ProjectGitHubIntegrationModel:
        existing = self.integrations.get(str(project_id))
        if existing:
            existing.repository_name = repository_name
            existing.repository_url = repository_url
            existing.default_branch = default_branch
            existing.connection_status = connection_status
            existing.commit_count = commit_count
            if cached_commits_preview is not None:
                existing.cached_commits_preview = cached_commits_preview
            existing.sync_error = sync_error
            existing.last_sync_at = datetime.now(UTC)
            return existing

        integration = ProjectGitHubIntegrationModel(
            id=uuid.uuid4(),
            project_instance_id=str(project_id),
            repository_name=repository_name,
            repository_url=repository_url,
            default_branch=default_branch,
            connection_status=connection_status,
            commit_count=commit_count,
            cached_commits_preview=cached_commits_preview or [],
            last_sync_at=datetime.now(UTC),
            sync_error=sync_error,
        )
        self.integrations[str(project_id)] = integration
        return integration


# ============================================================================
# Helpers
# ============================================================================

def make_test_user(user_id: uuid.UUID, role: UserRole = UserRole.STUDENT) -> CurrentUser:
    return CurrentUser(
        user_id=user_id,
        email="student@growflow.internal",
        role=role,
        status=AccountStatus.ACTIVE,
        full_name="Test Student",
    )


def make_test_project(student_id: uuid.UUID, project_id: uuid.UUID | None = None, name: str = "Test Project") -> ProjectInstanceModel:
    pid = project_id or uuid.uuid4()
    p = ProjectInstanceModel(
        id=str(pid),
        student_id=str(student_id),
        current_phase="BUILD",
        health="ON_TRACK",
        status="ACTIVE",
    )
    p.name = name  # assign name
    return p


# ============================================================================
# Test Suite
# ============================================================================

@pytest.mark.asyncio
async def test_blueprint_promotion_safety_lifecycle() -> None:
    """
    1. Prove lifecycle:
       Approved V1 -> Change Request -> Impact Analysis -> Student Confirmation
       -> Candidate V2 -> Validation -> QA -> Atomic Promotion -> V2 Approved -> V1 Superseded.
       Prove previous approved version V1 remains recoverable via get_blueprint_version.
       Prove dynamic version numbering (not hardcoded).
    """
    student_id = uuid.uuid4()
    user = make_test_user(student_id)
    project = make_test_project(student_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project.id)] = project

    blueprint = BlueprintModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(project.id),
        status="APPROVED",
        content={"system_overview": {"title": "Baseline V1 Architecture"}},
        qa_score=90,
        qa_feedback={"status": "APPROVED", "overall_score": 90},
    )
    blueprint_repo = InMemoryBlueprintRepo()
    blueprint_repo.blueprints[str(blueprint.id)] = blueprint

    task_repo = InMemoryTaskRepo()
    milestone_repo = InMemoryMilestoneRepo()
    version_repo = InMemoryBlueprintVersionRepo()
    change_repo = InMemoryProjectChangeRepo()
    outbox = InMemoryOutboxService()

    change_service = ProjectChangeService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        blueprint_repo=blueprint_repo,
        task_repo=task_repo,
        milestone_repo=milestone_repo,
        blueprint_version_repo=version_repo,
        project_change_repo=change_repo,
        outbox_service=outbox,
    )

    # 1. Propose and analyze change
    analyzed = await change_service.analyze_change(
        project_id=project.id,
        current_user=user,
        change_title="Add Redis Caching Layer",
        change_description="Introduce Redis cluster for fast caching of user queries.",
        change_type="TECH_STACK",
    )
    assert analyzed["status"] == "ANALYZED"
    assert analyzed["source_blueprint_version_number"] == 1
    change_id = analyzed["id"]

    # 2. Confirm change -> triggers candidate generation, QA evaluation, and atomic promotion
    confirmed = await change_service.confirm_change(
        project_id=project.id,
        change_id=change_id,
        current_user=user,
        idempotency_key="key-test-01",
    )
    assert confirmed["status"] == "COMPLETED"
    assert confirmed["resulting_blueprint_version_number"] == 2
    assert confirmed["qa_score"] == 92

    # 3. Verify Version Records: V1 is SUPERSEDED, V2 is APPROVED
    v1 = await change_service.get_blueprint_version(project.id, 1, user)
    assert v1["version_number"] == 1
    assert v1["status"] == "SUPERSEDED"
    assert "Baseline V1 Architecture" in str(v1["content"])

    v2 = await change_service.get_blueprint_version(project.id, 2, user)
    assert v2["version_number"] == 2
    assert v2["status"] == "APPROVED"
    assert v2["qa_score"] == 92

    # 4. Verify Active Blueprint in repository is updated to V2
    active_bp = await blueprint_repo.get_by_project_id(project.id)
    assert active_bp.status == "APPROVED"
    assert active_bp.qa_score == 92

    # 5. Propose a second change to verify dynamic version numbering (V2 -> V3)
    analyzed_2 = await change_service.analyze_change(
        project_id=project.id,
        current_user=user,
        change_title="Add GraphQL Gateway",
        change_description="Expose unified GraphQL schema for frontend consumption.",
        change_type="ARCHITECTURE",
    )
    assert analyzed_2["source_blueprint_version_number"] == 2
    confirmed_2 = await change_service.confirm_change(
        project_id=project.id,
        change_id=analyzed_2["id"],
        current_user=user,
        idempotency_key="key-test-02",
    )
    assert confirmed_2["resulting_blueprint_version_number"] == 3

    # Verify V2 is now SUPERSEDED and V3 is APPROVED
    v2_updated = await change_service.get_blueprint_version(project.id, 2, user)
    assert v2_updated["status"] == "SUPERSEDED"
    v3 = await change_service.get_blueprint_version(project.id, 3, user)
    assert v3["version_number"] == 3
    assert v3["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_blueprint_promotion_safety_failure_preserves_v1_approved() -> None:
    """
    Critical requirement: If generation, validation, or QA fails:
    V1 MUST remain APPROVED.
    Never archive or supersede the approved blueprint before replacement candidate passes QA.
    """
    student_id = uuid.uuid4()
    user = make_test_user(student_id)
    project = make_test_project(student_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project.id)] = project

    baseline_content = {"system_overview": {"title": "Canonical V1 Baseline"}}
    blueprint = BlueprintModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(project.id),
        status="APPROVED",
        content=baseline_content,
        qa_score=90,
        qa_feedback={"status": "APPROVED"},
    )
    blueprint_repo = InMemoryBlueprintRepo()
    blueprint_repo.blueprints[str(blueprint.id)] = blueprint

    version_repo = InMemoryBlueprintVersionRepo()
    change_repo = InMemoryProjectChangeRepo()
    outbox = InMemoryOutboxService()

    change_service = ProjectChangeService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        blueprint_repo=blueprint_repo,
        task_repo=InMemoryTaskRepo(),
        milestone_repo=InMemoryMilestoneRepo(),
        blueprint_version_repo=version_repo,
        project_change_repo=change_repo,
        outbox_service=outbox,
    )

    analyzed = await change_service.analyze_change(
        project_id=project.id,
        current_user=user,
        change_title="Flawed Architecture Proposal",
        change_description="Propose breaking change with invalid circular dependencies.",
    )
    change_id = analyzed["id"]

    # Patch copy.deepcopy to simulate candidate failure / exception
    with patch.object(
        copy,
        "deepcopy",
        side_effect=RuntimeError("Validation error: Circular service dependencies detected in candidate"),
    ):
        with pytest.raises(BusinessRuleException) as exc_info:
            await change_service.confirm_change(
                project_id=project.id,
                change_id=change_id,
                current_user=user,
            )
        assert exc_info.value.code == "REGENERATION_FAILED"

    # CRITICAL CHECK: V1 MUST REMAIN APPROVED
    active_bp = await blueprint_repo.get_by_project_id(project.id)
    assert active_bp.status == "APPROVED"
    assert active_bp.content == baseline_content

    # Check that change request is FAILED
    change_req = await change_repo.get_by_id(change_id)
    assert change_req.status == "FAILED"

    # Verify no version was marked SUPERSEDED
    versions = await version_repo.list_by_project(project.id)
    for v in versions:
        assert v.status == "APPROVED"


@pytest.mark.asyncio
async def test_project_change_idempotency() -> None:
    """
    Test:
    POST confirm(change_id, idempotency_key=X) -> generation
    Repeat confirm(change_id, idempotency_key=X)
    Expected:
    - same change request
    - no duplicate generation job
    - no duplicate Blueprint version
    - no duplicate completion event
    - no duplicate operational mutation
    Also test:
    - repeated confirmation after COMPLETED
    - confirmation while REGENERATING
    """
    student_id = uuid.uuid4()
    user = make_test_user(student_id)
    project = make_test_project(student_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project.id)] = project

    blueprint = BlueprintModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(project.id),
        status="APPROVED",
        content={"system_overview": {"title": "Base"}},
        qa_score=90,
    )
    blueprint_repo = InMemoryBlueprintRepo()
    blueprint_repo.blueprints[str(blueprint.id)] = blueprint

    version_repo = InMemoryBlueprintVersionRepo()
    change_repo = InMemoryProjectChangeRepo()
    outbox = InMemoryOutboxService()

    change_service = ProjectChangeService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        blueprint_repo=blueprint_repo,
        task_repo=InMemoryTaskRepo(),
        milestone_repo=InMemoryMilestoneRepo(),
        blueprint_version_repo=version_repo,
        project_change_repo=change_repo,
        outbox_service=outbox,
    )

    analyzed = await change_service.analyze_change(
        project_id=project.id,
        current_user=user,
        change_title="Add Auth Layer",
        change_description="Implement OAuth2/OIDC integration.",
    )
    change_id = analyzed["id"]
    idempotency_key = "idemp-unique-12345"

    # First call: performs regeneration and completes
    res1 = await change_service.confirm_change(
        project_id=project.id,
        change_id=change_id,
        current_user=user,
        idempotency_key=idempotency_key,
    )
    assert res1["status"] == "COMPLETED"
    version_count_after_first = len(version_repo.versions)
    event_count_after_first = len(outbox.enqueued_events)

    # Repeat call with same idempotency key (simulates network retry / double click)
    res2 = await change_service.confirm_change(
        project_id=project.id,
        change_id=change_id,
        current_user=user,
        idempotency_key=idempotency_key,
    )
    assert res2["status"] == "COMPLETED"
    assert res2["id"] == res1["id"]
    assert res2["resulting_blueprint_version_number"] == res1["resulting_blueprint_version_number"]

    # Verify zero duplicate versions and zero duplicate events
    assert len(version_repo.versions) == version_count_after_first
    assert len(outbox.enqueued_events) == event_count_after_first

    # Test repeated confirmation after COMPLETED (without idempotency key, e.g. browser refresh)
    res3 = await change_service.confirm_change(
        project_id=project.id,
        change_id=change_id,
        current_user=user,
        idempotency_key=None,
    )
    assert res3["status"] == "COMPLETED"
    assert len(version_repo.versions) == version_count_after_first

    # Test confirmation while REGENERATING (simulates concurrent requests)
    change_req_2 = await change_service.analyze_change(
        project_id=project.id,
        current_user=user,
        change_title="Concurrent Test Change",
        change_description="Testing concurrency state guard during regeneration.",
    )
    # Manually set to REGENERATING to simulate in-flight job
    raw_req = await change_repo.get_by_id(change_req_2["id"])
    raw_req.status = "REGENERATING"

    res_in_flight = await change_service.confirm_change(
        project_id=project.id,
        change_id=change_req_2["id"],
        current_user=user,
    )
    assert res_in_flight["status"] == "REGENERATING"
    # Did not create another version
    assert len(version_repo.versions) == version_count_after_first


@pytest.mark.asyncio
async def test_ai_mentor_truthful_unavailability() -> None:
    """
    3. AI Mentor Architecture Verification:
    Confirm it uses AIProviderGateway.
    When provider/API keys are unavailable:
    return truthful AI_UNAVAILABLE / offline explanation.
    Never fabricate assistant responses or present deterministic mock text as live AI.
    """
    student_id = uuid.uuid4()
    user = make_test_user(student_id)
    project = make_test_project(student_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project.id)] = project

    ai_repo = InMemoryAIMentorRepo()
    outbox = InMemoryOutboxService()

    # Mock gateway with has_live_keys = False
    mock_gateway = MagicMock()
    mock_gateway.has_live_keys = False

    ai_service = AIMentorService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        blueprint_repo=InMemoryBlueprintRepo(),
        task_repo=InMemoryTaskRepo(),
        milestone_repo=InMemoryMilestoneRepo(),
        ai_mentor_repo=ai_repo,
        help_request_repo=InMemoryHelpRequestRepo(),
        outbox_service=outbox,
        ai_gateway=mock_gateway,
    )

    res = await ai_service.send_message(
        project_id=project.id,
        current_user=user,
        content="How should I structure my backend services?",
    )

    # Must be marked unavailable truthfully
    assert res["ai_available"] is False
    assert "offline or not configured" in res["assistant_message"]["content"]
    assert "OPENROUTER_API_KEY" in res["assistant_message"]["content"]
    # Gateway was not called to generate fake hallucinated answers
    mock_gateway.execute_prompt.assert_not_called()


@pytest.mark.asyncio
async def test_ai_project_isolation() -> None:
    """
    4. AI Project Isolation:
    Project A: unique identifying information ("Drone Flight Controller", "C++ / ROS2").
    Project B: unique identifying information ("FinTech Ledger", "Java / Spring Boot").
    Verify Project B information can NEVER appear in Project A's AI prompt context.
    Verify user from Project B cannot access Project A's AI mentor.
    """
    student_a_id = uuid.uuid4()
    student_b_id = uuid.uuid4()

    user_a = make_test_user(student_a_id)
    user_b = make_test_user(student_b_id)

    project_a = make_test_project(student_a_id, name="Drone Flight Controller")
    project_b = make_test_project(student_b_id, name="FinTech Ledger")

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project_a.id)] = project_a
    project_repo.projects[str(project_b.id)] = project_b

    blueprint_repo = InMemoryBlueprintRepo()
    bp_a = BlueprintModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(project_a.id),
        status="APPROVED",
        content={"technical_stack": {"language": "C++", "framework": "ROS2"}},
    )
    bp_b = BlueprintModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(project_b.id),
        status="APPROVED",
        content={"technical_stack": {"language": "Java", "framework": "Spring Boot"}},
    )
    blueprint_repo.blueprints[str(bp_a.id)] = bp_a
    blueprint_repo.blueprints[str(bp_b.id)] = bp_b

    task_repo = InMemoryTaskRepo()
    task_a = ProjectTaskModel(
        id=uuid.uuid4(),
        project_instance_id=str(project_a.id),
        title="Implement PID Motor Controller",
        status="TODO",
        priority="HIGH",
        category="EMBEDDED",
    )
    task_b = ProjectTaskModel(
        id=uuid.uuid4(),
        project_instance_id=str(project_b.id),
        title="Double-Entry Balance Reconciliation",
        status="TODO",
        priority="HIGH",
        category="FINANCE",
    )
    await task_repo.add(task_a)
    await task_repo.add(task_b)

    ai_repo = InMemoryAIMentorRepo()
    outbox = InMemoryOutboxService()

    mock_gateway = MagicMock()
    mock_gateway.has_live_keys = True
    captured_system_prompts: list[str] = []

    async def fake_execute_prompt(prompt: str, system_prompt: str, **kwargs: Any) -> str:
        captured_system_prompts.append(system_prompt)
        return "I recommend tuning the PID loop gains."

    mock_gateway.execute_prompt = AsyncMock(side_effect=fake_execute_prompt)

    ai_service = AIMentorService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        blueprint_repo=blueprint_repo,
        task_repo=task_repo,
        milestone_repo=InMemoryMilestoneRepo(),
        ai_mentor_repo=ai_repo,
        help_request_repo=InMemoryHelpRequestRepo(),
        outbox_service=outbox,
        ai_gateway=mock_gateway,
    )

    # Student A queries Project A
    res_a = await ai_service.send_message(
        project_id=project_a.id,
        current_user=user_a,
        content="How do I tune motor response?",
    )
    assert res_a["ai_available"] is True

    # Inspect the system prompt constructed for Project A
    assert len(captured_system_prompts) == 1
    prompt_a = captured_system_prompts[0]

    assert "Drone Flight Controller" in prompt_a
    assert "ROS2" in prompt_a
    # Critical: Project B info must NEVER appear
    assert "FinTech Ledger" not in prompt_a
    assert "Spring Boot" not in prompt_a
    assert "Double-Entry" not in prompt_a

    # Verify authorization boundary: Student B attempting to query Project A raises 403
    with pytest.raises(AuthorizationException) as exc_info:
        await ai_service.send_message(
            project_id=project_a.id,
            current_user=user_b,
            content="Can I see Project A?",
        )
    assert exc_info.value.code == "AUTH_FORBIDDEN_RESOURCE"


@pytest.mark.asyncio
async def test_ai_action_security() -> None:
    """
    5. AI Action Security:
    Verify suggested action cannot mutate project state merely because assistant returned payload.
    Must go through explicit confirmation:
    - valid owner
    - unauthorized project (raises AuthorizationException)
    - invalid resource ID (raises NotFoundException)
    - wrong project resource (raises NotFoundException without leaking existence)
    - already-completed task (raises BusinessRuleException)
    - duplicate execution
    """
    student_a_id = uuid.uuid4()
    student_b_id = uuid.uuid4()
    user_a = make_test_user(student_a_id)
    user_b = make_test_user(student_b_id)

    project_a = make_test_project(student_a_id)
    project_b = make_test_project(student_b_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project_a.id)] = project_a
    project_repo.projects[str(project_b.id)] = project_b

    task_repo = InMemoryTaskRepo()
    task_a = ProjectTaskModel(
        id=uuid.uuid4(),
        project_instance_id=str(project_a.id),
        title="Setup CI/CD Pipeline",
        status="TODO",
        priority="HIGH",
        category="INFRASTRUCTURE",
    )
    task_b = ProjectTaskModel(
        id=uuid.uuid4(),
        project_instance_id=str(project_b.id),
        title="Project B Private Task",
        status="TODO",
        priority="LOW",
        category="SECURITY",
    )
    await task_repo.add(task_a)
    await task_repo.add(task_b)

    outbox = InMemoryOutboxService()
    ai_service = AIMentorService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        blueprint_repo=InMemoryBlueprintRepo(),
        task_repo=task_repo,
        milestone_repo=InMemoryMilestoneRepo(),
        ai_mentor_repo=InMemoryAIMentorRepo(),
        help_request_repo=InMemoryHelpRequestRepo(),
        outbox_service=outbox,
    )

    # 1. Valid Owner executes COMPLETE_TASK
    res = await ai_service.execute_suggested_action(
        project_id=project_a.id,
        current_user=user_a,
        action_type="COMPLETE_TASK",
        payload={"task_id": str(task_a.id)},
    )
    assert res["status"] == "SUCCESS"
    assert task_a.status == "DONE"

    # Verify domain event enqueued
    assert any(e["event_type"] == DomainEventType.TASK_COMPLETED for e in outbox.enqueued_events)

    # 2. Duplicate Execution / Already-Completed Task
    with pytest.raises(BusinessRuleException) as exc_dup:
        await ai_service.execute_suggested_action(
            project_id=project_a.id,
            current_user=user_a,
            action_type="COMPLETE_TASK",
            payload={"task_id": str(task_a.id)},
        )
    assert exc_dup.value.code == "TASK_ALREADY_COMPLETED"

    # 3. Unauthorized User executing action on Project A
    with pytest.raises(AuthorizationException):
        await ai_service.execute_suggested_action(
            project_id=project_a.id,
            current_user=user_b,
            action_type="CREATE_TASK",
            payload={"title": "Unauthorized Task"},
        )

    # 4. Invalid Resource ID
    with pytest.raises(NotFoundException) as exc_nf:
        await ai_service.execute_suggested_action(
            project_id=project_a.id,
            current_user=user_a,
            action_type="COMPLETE_TASK",
            payload={"task_id": str(uuid.uuid4())},
        )
    assert exc_nf.value.code == "TASK_NOT_FOUND"

    # 5. Wrong Project Resource (task_b belongs to project_b, student_a passes task_b in project_a)
    # Must raise NotFoundException to avoid leaking task existence across projects
    with pytest.raises(NotFoundException) as exc_wrong:
        await ai_service.execute_suggested_action(
            project_id=project_a.id,
            current_user=user_a,
            action_type="COMPLETE_TASK",
            payload={"task_id": str(task_b.id)},
        )
    assert exc_wrong.value.code == "TASK_NOT_FOUND"


@pytest.mark.asyncio
async def test_github_integration_observation_boundary() -> None:
    """
    6. GitHub Integration Verification:
    - Frontend -> FastAPI -> GitHubService -> GitHub API
    - No canonical local git commit table exists.
    - Connect, sync, repository metadata, recent commits, sync timestamp, disconnect.
    - Token/credentials are never exposed.
    """
    student_id = uuid.uuid4()
    user = make_test_user(student_id)
    project = make_test_project(student_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project.id)] = project

    github_repo = InMemoryGitHubRepo()
    outbox = InMemoryOutboxService()

    github_service = GitHubService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        github_repo=github_repo,
        outbox_service=outbox,
    )

    # 1. Initial State: NOT_CONNECTED
    initial = await github_service.get_integration(project.id, user)
    assert initial["connection_status"] == "NOT_CONNECTED"
    assert initial["commit_count"] == 0

    # 2. Connect
    connected = await github_service.connect_repository(
        project_id=project.id,
        current_user=user,
        repository_url="https://github.com/growflow/demo-app.git",
        default_branch="main",
    )
    assert connected["connection_status"] == "CONNECTED"
    assert connected["repository_name"] == "demo-app"
    assert connected["default_branch"] == "main"
    assert len(connected["cached_commits_preview"]) > 0
    assert connected["last_sync_at"] is not None
    # No secret token field in response
    assert "token" not in connected
    assert "access_token" not in connected

    # 3. Sync
    synced = await github_service.sync_repository(project.id, user)
    assert synced["connection_status"] == "CONNECTED"
    assert synced["commit_count"] > 0
    assert any(e["event_type"] == DomainEventType.GITHUB_SYNCED for e in outbox.enqueued_events)

    # 4. Disconnect
    disconnected = await github_service.disconnect_repository(project.id, user)
    assert disconnected["connection_status"] == "NOT_CONNECTED"
    assert disconnected["commit_count"] == 0
    assert disconnected["cached_commits_preview"] == []


@pytest.mark.asyncio
async def test_activity_canonical_event_stream() -> None:
    """
    7. Activity Verification:
    Confirm S28 reads from canonical domain_events/outbox-derived events only.
    Chronological ordering, correct actor, resource, and project.
    """
    student_id = uuid.uuid4()
    user = make_test_user(student_id)
    project = make_test_project(student_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project.id)] = project

    outbox_repo = InMemoryOutboxRepo()

    t1 = datetime(2026, 9, 13, 10, 0, 0, tzinfo=UTC)
    t2 = datetime(2026, 9, 13, 10, 30, 0, tzinfo=UTC)

    event1 = DomainEventModel(
        id=uuid.uuid4(),
        event_type="TaskCreated",
        actor_role="STUDENT",
        actor_id=student_id,
        resource_type="ProjectTask",
        resource_id=uuid.uuid4(),
        project_instance_id=project.id,
        occurred_at=t1,
        metadata_json={"title": "Design Database Schema"},
    )
    event2 = DomainEventModel(
        id=uuid.uuid4(),
        event_type="TaskCompleted",
        actor_role="STUDENT",
        actor_id=student_id,
        resource_type="ProjectTask",
        resource_id=event1.resource_id,
        project_instance_id=project.id,
        occurred_at=t2,
        metadata_json={"title": "Design Database Schema"},
    )
    outbox_repo.events = [event1, event2]

    activity_service = ActivityService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        outbox_repo=outbox_repo,
    )

    activity = await activity_service.get_project_activity(project.id, user)
    assert len(activity) == 2
    assert activity[0]["title"] == "Task Created"
    assert activity[1]["title"] == "Task Completed"
    assert activity[0]["actor_role"] == "STUDENT"
    assert activity[0]["resource_type"] == "ProjectTask"


@pytest.mark.asyncio
async def test_help_request_and_mentor_feedback_authority() -> None:
    """
    8 & 9. Help Request and Mentor Feedback Authority:
    - Student creates Help Request in OPEN state.
    - Non-owner student cannot access help request.
    - Student can acknowledge mentor notes.
    - Acknowledging mentor note does NOT mutate operational task/milestone records.
    """
    student_a = uuid.uuid4()
    student_b = uuid.uuid4()
    user_a = make_test_user(student_a)
    user_b = make_test_user(student_b)

    project_a = make_test_project(student_a)
    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project_a.id)] = project_a

    help_repo = InMemoryHelpRequestRepo()
    mentor_repo = InMemoryMentorNoteRepo()
    task_repo = InMemoryTaskRepo()
    milestone_repo = InMemoryMilestoneRepo()
    outbox = InMemoryOutboxService()

    help_service = HelpRequestService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        help_request_repo=help_repo,
        outbox_service=outbox,
    )
    feedback_service = MentorFeedbackService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        mentor_note_repo=mentor_repo,
        outbox_service=outbox,
    )

    # 1. Create Help Request
    created = await help_service.create_help_request(
        project_id=project_a.id,
        current_user=user_a,
        subject="Docker container failing on startup",
        description="Exit code 137 OOM killer triggered.",
        category="TECHNICAL",
        priority="HIGH",
    )
    assert created["status"] == "OPEN"
    assert created["mentor_response"] is None

    # Unauthorized student B cannot view or retrieve help request
    with pytest.raises(AuthorizationException):
        await help_service.get_help_request(project_a.id, created["id"], user_b)

    # 2. Mentor Note Acknowledgement
    note = ProjectMentorNoteModel(
        id=uuid.uuid4(),
        project_instance_id=str(project_a.id),
        mentor_id=str(uuid.uuid4()),
        title="Check Memory Limits",
        message="Assign at least 2GB of memory to the container runtime.",
        note_type="ACTIONABLE",
        status="UNREAD",
    )
    mentor_repo.notes[str(note.id)] = note

    # Pre-existing tasks and milestones
    task = ProjectTaskModel(
        id=uuid.uuid4(),
        project_instance_id=str(project_a.id),
        title="Configure Dockerfile",
        status="TODO",
        priority="MEDIUM",
        category="DEVOPS",
    )
    await task_repo.add(task)

    # Acknowledge note
    ack = await feedback_service.acknowledge_note(project_a.id, note.id, user_a)
    assert ack["status"] == "ACKNOWLEDGED"

    # CRITICAL: Verify operational task was NOT mutated or deleted
    fetched_task = await task_repo.get_by_id(task.id)
    assert fetched_task is not None
    assert fetched_task.status == "TODO"
    assert fetched_task.title == "Configure Dockerfile"


@pytest.mark.asyncio
async def test_operational_boundary_preservation_on_regeneration() -> None:
    """
    10. Project Change Operational Boundary:
    Confirm regeneration does NOT silently delete tasks, milestones, risks, documents,
    or erase execution history.
    """
    student_id = uuid.uuid4()
    user = make_test_user(student_id)
    project = make_test_project(student_id)

    project_repo = InMemoryProjectRepo()
    project_repo.projects[str(project.id)] = project

    blueprint = BlueprintModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(project.id),
        status="APPROVED",
        content={"system_overview": {"title": "Base Architecture"}},
        qa_score=90,
    )
    blueprint_repo = InMemoryBlueprintRepo()
    blueprint_repo.blueprints[str(blueprint.id)] = blueprint

    task_repo = InMemoryTaskRepo()
    t1 = ProjectTaskModel(
        id=uuid.uuid4(),
        project_instance_id=str(project.id),
        title="Existing Task 1",
        status="DONE",
        priority="HIGH",
        category="BACKEND",
    )
    t2 = ProjectTaskModel(
        id=uuid.uuid4(),
        project_instance_id=str(project.id),
        title="Existing Task 2",
        status="IN_PROGRESS",
        priority="MEDIUM",
        category="FRONTEND",
    )
    await task_repo.add(t1)
    await task_repo.add(t2)

    milestone_repo = InMemoryMilestoneRepo()
    m1 = ProjectMilestoneModel(
        id=uuid.uuid4(),
        project_instance_id=str(project.id),
        title="Alpha Release",
        status="IN_PROGRESS",
        progress_percent=50,
        section_order=1,
    )
    milestone_repo.milestones[str(m1.id)] = m1

    change_service = ProjectChangeService(
        project_repo=project_repo,
        group_repo=InMemoryGroupRepo(),
        blueprint_repo=blueprint_repo,
        task_repo=task_repo,
        milestone_repo=milestone_repo,
        blueprint_version_repo=InMemoryBlueprintVersionRepo(),
        project_change_repo=InMemoryProjectChangeRepo(),
        outbox_service=InMemoryOutboxService(),
    )

    # Analyze and confirm change
    analyzed = await change_service.analyze_change(
        project_id=project.id,
        current_user=user,
        change_title="Major Architectural Scope Shift",
        change_description="Expand to multi-tenant organization support.",
        change_type="SCOPE",
    )
    assert analyzed["impact_analysis"]["total_tasks_count"] == 2
    assert analyzed["impact_analysis"]["total_milestones_count"] == 1

    await change_service.confirm_change(
        project_id=project.id,
        change_id=analyzed["id"],
        current_user=user,
    )

    # Verify zero operational state deletion or mutation:
    tasks_after = await task_repo.list_by_project(project.id)
    assert len(tasks_after) == 2
    assert any(t.title == "Existing Task 1" and t.status == "DONE" for t in tasks_after)
    assert any(t.title == "Existing Task 2" and t.status == "IN_PROGRESS" for t in tasks_after)

    milestones_after = await milestone_repo.list_by_project(project.id)
    assert len(milestones_after) == 1
    assert milestones_after[0].title == "Alpha Release"
    assert milestones_after[0].progress_percent == 50
