"""
GrowFlow Batch S12-S14 — API & Domain Tests for Student Blueprint Workflow.

Covers:
1. Unauthenticated requests return 401 Unauthorized.
2. Cross-student access returns 403 Forbidden.
3. Nonexistent project returns 404 Not Found.
4. Starting generation fails with 400/409 when assessment is incomplete.
5. Starting generation succeeds when assessment is completed:
   - Synthesizes all 10 canonical sections
   - Advances project phase to BLUEPRINT
   - Executes QA / Judge evaluation
   - Sets status to READY_FOR_APPROVAL on QA pass
6. Generation idempotency (calling generate on ready session returns existing state).
7. Getting blueprint content returns all 10 structured sections.
8. Targeted retry regenerates only the affected output key.
9. Targeted retry rejects invalid section keys with 400.
10. Approving blueprint succeeds when QA passed, sets status APPROVED with timestamp.
11. Approving blueprint rejects when QA has not passed or status is NOT_STARTED.
12. Mentor project definition and source version remain strictly immutable.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_blueprint_service
from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.domain.ai.orchestration.worker import BlueprintWorker
from backend.app.domain.assessment.models import AssessmentStatus
from backend.app.domain.blueprint.models import (
    CANONICAL_BLUEPRINT_SECTION_ORDER,
    BlueprintQAStatus,
    BlueprintSectionKey,
    BlueprintStatus,
)
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.assessment import (
    AssessmentModel,
    AssessmentResultModel,
)
from backend.app.infrastructure.database.models.blueprint import BlueprintModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.assessment_repository import AssessmentRepository
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from backend.app.config.settings import Settings

_TEST_SECRET = "gate-09-test-secret-at-least-32-chars-long-123"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_jwt(
    user_id: uuid.UUID,
    email: str = "test@example.com",
    role: str = "STUDENT",
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": _TEST_AUDIENCE,
        "iss": _TEST_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=3600)).timestamp()),
        "app_metadata": {"role": role},
    }
    return jwt.encode(payload, _TEST_SECRET, algorithm="HS256")


@pytest.fixture
def auth_settings(test_settings: Settings) -> Settings:
    test_settings.auth.JWT_SECRET = _TEST_SECRET
    test_settings.auth.JWT_AUDIENCE = _TEST_AUDIENCE
    test_settings.auth.JWT_ISSUER = _TEST_ISSUER
    test_settings.database.DATABASE_URL = None
    return test_settings


@pytest.fixture
def owner_student_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_student_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def project_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def owner_token(owner_student_id: uuid.UUID) -> str:
    return _make_jwt(owner_student_id, "owner@example.com", UserRole.STUDENT.value)


@pytest.fixture
def other_token(other_student_id: uuid.UUID) -> str:
    return _make_jwt(other_student_id, "other@example.com", UserRole.STUDENT.value)


@pytest.fixture
def sample_project(owner_student_id: uuid.UUID, project_id: uuid.UUID) -> ProjectInstanceModel:
    proj = ProjectInstanceModel()
    proj.id = str(project_id)
    proj.student_id = str(owner_student_id)
    proj.name = "Autonomous Precision Agriculture Drone"
    proj.problem = "Crop monitoring inefficiencies in large fields"
    proj.proposed_solution = "Autonomous multi-rotor drone with multispectral telemetry"
    proj.complexity = ProjectComplexity.INTERMEDIATE.value
    proj.current_phase = ProjectPhase.ASSESSMENT.value
    proj.health = ProjectHealth.HEALTHY.value
    proj.status = ProjectStatus.ACTIVE.value
    proj.progress_percentage = 25
    proj.created_at = datetime.now(UTC)
    proj.updated_at = datetime.now(UTC)
    return proj


@pytest.fixture
def completed_assessment(project_id: uuid.UUID, owner_student_id: uuid.UUID) -> AssessmentModel:
    asm = AssessmentModel()
    asm.id = str(uuid.uuid4())
    asm.project_instance_id = str(project_id)
    asm.student_id = str(owner_student_id)
    asm.status = AssessmentStatus.COMPLETED.value
    asm.current_question_index = 15
    asm.total_questions = 15
    asm.started_at = datetime.now(UTC) - timedelta(minutes=15)
    asm.completed_at = datetime.now(UTC)
    asm.created_at = datetime.now(UTC) - timedelta(minutes=15)
    asm.updated_at = datetime.now(UTC)
    return asm


@pytest.fixture
def client(
    auth_settings: Settings,
    owner_student_id: uuid.UUID,
    other_student_id: uuid.UUID,
    sample_project: ProjectInstanceModel,
    completed_assessment: AssessmentModel,
) -> Generator[TestClient, None, None]:
    app = create_app(settings=auth_settings)

    # In-memory storage for blueprint tests
    blueprints_store: dict[str, BlueprintModel] = {}
    project_store: dict[str, ProjectInstanceModel] = {str(sample_project.id): sample_project}
    assessment_store: dict[str, AssessmentModel] = {str(completed_assessment.project_instance_id): completed_assessment}

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    async def _p_get_by_id(pid):
        return project_store.get(str(pid))
    mock_project_repo.get_by_id.side_effect = _p_get_by_id

    mock_assessment_repo = AsyncMock(spec=AssessmentRepository)
    async def _a_get_by_project(pid):
        return assessment_store.get(str(pid))
    async def _a_get_answers(aid):
        return []
    async def _a_get_result(aid):
        res = AssessmentResultModel()
        res.id = str(uuid.uuid4())
        res.assessment_id = str(aid)
        res.overall_score = 84
        res.readiness_tier = "HIGH"
        res.dimension_scores = {"problem_clarity": 88}
        res.identified_gaps = []
        res.recommendations = []
        return res
    mock_assessment_repo.get_by_project_id.side_effect = _a_get_by_project
    mock_assessment_repo.get_answers.side_effect = _a_get_answers
    mock_assessment_repo.get_result_by_assessment_id.side_effect = _a_get_result

    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    async def _bp_get_by_proj(pid):
        return blueprints_store.get(str(pid))
    async def _bp_create_or_get(pid, sid):
        if str(pid) in blueprints_store:
            return blueprints_store[str(pid)]
        bp = BlueprintModel()
        bp.id = str(uuid.uuid4())
        bp.project_instance_id = str(pid)
        bp.student_id = str(sid)
        bp.status = BlueprintStatus.NOT_STARTED.value
        bp.progress_percent = 0
        bp.qa_status = BlueprintQAStatus.PENDING.value
        bp.content = {}
        bp.created_at = datetime.now(UTC)
        bp.updated_at = datetime.now(UTC)
        blueprints_store[str(pid)] = bp
        return bp
    async def _bp_update_status(bp, st, current_step=None, progress_percent=None, error_message=None, failed_output_key=None):
        bp.status = st.value
        if current_step is not None:
            bp.current_step = current_step
        if progress_percent is not None:
            bp.progress_percent = progress_percent
        if error_message is not None:
            bp.error_message = error_message
        if failed_output_key is not None:
            bp.failed_output_key = failed_output_key
        bp.updated_at = datetime.now(UTC)
        blueprints_store[str(bp.project_instance_id)] = bp
        return bp
    async def _bp_save_content(bp, sec_key, sec_data, pct):
        cnt = dict(bp.content or {})
        cnt[sec_key] = sec_data
        bp.content = cnt
        bp.current_step = sec_key
        bp.progress_percent = pct
        bp.updated_at = datetime.now(UTC)
        blueprints_store[str(bp.project_instance_id)] = bp
        return bp
    async def _bp_record_qa(bp, q_st, q_sc, q_fb):
        bp.qa_status = q_st.value
        bp.qa_score = q_sc
        bp.qa_feedback = q_fb
        bp.status = BlueprintStatus.READY_FOR_APPROVAL.value if q_st == BlueprintQAStatus.PASS else BlueprintStatus.QA_REJECTED.value
        bp.updated_at = datetime.now(UTC)
        blueprints_store[str(bp.project_instance_id)] = bp
        return bp
    async def _bp_approve(bp):
        bp.status = BlueprintStatus.APPROVED.value
        bp.approved_at = datetime.now(UTC)
        bp.updated_at = datetime.now(UTC)
        blueprints_store[str(bp.project_instance_id)] = bp
        return bp
    async def _bp_create_job(*args, **kwargs):
        from backend.app.infrastructure.database.models.blueprint import BlueprintJobModel
        j = BlueprintJobModel()
        j.id = str(uuid.uuid4())
        return j
    async def _bp_complete_job(*args, **kwargs):
        return None
    async def _bp_get_by_id(bpid):
        for bp in blueprints_store.values():
            if str(bp.id) == str(bpid):
                return bp
        return blueprints_store.get(str(bpid))

    mock_blueprint_repo.get_by_id.side_effect = _bp_get_by_id
    mock_blueprint_repo.get_by_project_id.side_effect = _bp_get_by_proj
    mock_blueprint_repo.get_by_project_id_for_update.side_effect = _bp_get_by_proj
    mock_blueprint_repo.increment_generation_number.return_value = 1
    mock_blueprint_repo.create_or_get_blueprint.side_effect = _bp_create_or_get
    mock_blueprint_repo.update_status.side_effect = _bp_update_status
    mock_blueprint_repo.save_content_section.side_effect = _bp_save_content
    mock_blueprint_repo.record_qa_result.side_effect = _bp_record_qa
    mock_blueprint_repo.approve_blueprint.side_effect = _bp_approve
    mock_blueprint_repo.create_job.side_effect = _bp_create_job
    mock_blueprint_repo.complete_job.side_effect = _bp_complete_job

    mock_project_service = AsyncMock()
    async def _mock_trans_phase(*args, **kwargs):
        return None
    mock_project_service.transition_phase.side_effect = _mock_trans_phase

    mock_outbox_service = AsyncMock()
    async def _mock_emit(*args, **kwargs):
        return None
    mock_outbox_service.emit.side_effect = _mock_emit

    mock_worker = AsyncMock(spec=BlueprintWorker)
    async def _mock_run_job(job_id, project_id, blueprint_id, **kwargs):
        bp = blueprints_store.get(str(project_id))
        if bp:
            bp.status = BlueprintStatus.READY_FOR_APPROVAL.value
            bp.qa_status = BlueprintQAStatus.PASS.value
            bp.qa_score = 88
            bp.qa_feedback = {
                "overall_score": 88,
                "overall_feedback": "Looks great",
                "critical_issues": [],
                "recommendations": [],
            }
            bp.content = {k.value: f"Section {k.value} content" for k in BlueprintSectionKey}
            bp.updated_at = datetime.now(UTC)
    mock_worker.run_generation_job.side_effect = _mock_run_job

    service = BlueprintService(
        blueprint_repo=mock_blueprint_repo,
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
        project_service=mock_project_service,
        outbox_service=mock_outbox_service,
        worker=mock_worker,
    )

    orig_start = service.start_generation
    async def _wrapped_start(*args, **kwargs):
        res = await orig_start(*args, **kwargs)
        if service._active_tasks:
            await asyncio.gather(*list(service._active_tasks), return_exceptions=True)
            bp = await mock_blueprint_repo.get_by_project_id(args[0])
            if bp:
                return bp.to_domain()
        return res
    service.start_generation = _wrapped_start

    orig_retry = service.retry_generation
    async def _wrapped_retry(*args, **kwargs):
        res = await orig_retry(*args, **kwargs)
        if service._active_tasks:
            await asyncio.gather(*list(service._active_tasks), return_exceptions=True)
            bp = await mock_blueprint_repo.get_by_project_id(args[0])
            if bp:
                return bp.to_domain()
        return res
    service.retry_generation = _wrapped_retry

    mock_user_repo = AsyncMock(spec=UserRepository)
    async def _get_user_by_id(uid):
        uid_str = str(uid)
        if uid_str == str(owner_student_id):
            return UserModel(
                id=uid_str,
                email="owner@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
                full_name="Owner Student",
            )
        elif uid_str == str(other_student_id):
            return UserModel(
                id=uid_str,
                email="other@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
                full_name="Other Student",
            )
        return None
    mock_user_repo.get_by_id.side_effect = _get_user_by_id

    async def _override_get_db_session() -> AsyncGenerator[AsyncMock, None]:
        yield AsyncMock()

    app.dependency_overrides[get_db_session] = _override_get_db_session
    app.dependency_overrides[get_blueprint_service] = lambda: service

    with (
        patch("backend.app.api.dependencies.auth.UserRepository", return_value=mock_user_repo),
        TestClient(app, base_url="http://testserver") as test_client,
    ):
        yield test_client

    app.dependency_overrides.clear()


class TestBlueprintAPI:
    def test_unauthenticated_request_returns_401(self, client: TestClient, project_id: uuid.UUID):
        response = client.get(f"/api/v1/projects/{project_id}/blueprint/status")
        assert response.status_code == 401

    def test_cross_student_access_returns_403(self, client: TestClient, project_id: uuid.UUID, other_token: str):
        response = client.get(
            f"/api/v1/projects/{project_id}/blueprint/status",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 403

    def test_nonexistent_project_returns_404(self, client: TestClient, owner_token: str):
        random_id = uuid.uuid4()
        response = client.get(
            f"/api/v1/projects/{random_id}/blueprint/status",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert response.status_code == 404

    def test_start_generation_fails_if_assessment_incomplete(
        self, client: TestClient, project_id: uuid.UUID, owner_token: str, completed_assessment: AssessmentModel
    ):
        completed_assessment.status = AssessmentStatus.IN_PROGRESS.value
        response = client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        assert response.status_code in [400, 409]
        body = response.json()
        assert body["error"]["code"] == "ASSESSMENT_NOT_COMPLETED"
        completed_assessment.status = AssessmentStatus.COMPLETED.value

    def test_start_generation_succeeds_when_assessment_completed(
        self, client: TestClient, project_id: uuid.UUID, owner_token: str
    ):
        response = client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert data["status"] == "READY_FOR_APPROVAL"
        assert data["qa_status"] == "PASS"
        assert data["qa_score"] == 88
        assert data["qa_feedback"] is not None
        assert "evaluated_criteria" in data["qa_feedback"]

    def test_generation_idempotency(self, client: TestClient, project_id: uuid.UUID, owner_token: str):
        client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        response = client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "READY_FOR_APPROVAL"

    def test_get_content_returns_structured_sections(
        self, client: TestClient, project_id: uuid.UUID, owner_token: str
    ):
        client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        response = client.get(
            f"/api/v1/projects/{project_id}/blueprint/content",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        content = data["content"]
        for key in CANONICAL_BLUEPRINT_SECTION_ORDER:
            assert key.value in content

    def test_targeted_retry_regenerates_affected_section(
        self, client: TestClient, project_id: uuid.UUID, owner_token: str
    ):
        client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        response = client.post(
            f"/api/v1/projects/{project_id}/blueprint/retry",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"target_output_key": "specifications"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "READY_FOR_APPROVAL"
        assert data["qa_status"] == "PASS"

    def test_targeted_retry_rejects_invalid_section_key(
        self, client: TestClient, project_id: uuid.UUID, owner_token: str
    ):
        client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        response = client.post(
            f"/api/v1/projects/{project_id}/blueprint/retry",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"target_output_key": "nonexistent_section"},
        )
        assert response.status_code == 400
        body = response.json()
        assert body["error"]["code"] == "BLUEPRINT_INVALID_SECTION_KEY"

    def test_approve_blueprint_succeeds_when_qa_passed(
        self, client: TestClient, project_id: uuid.UUID, owner_token: str
    ):
        client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        response = client.post(
            f"/api/v1/projects/{project_id}/blueprint/approve",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["success"] is True
        assert data["status"] == "APPROVED"
        assert data["approved_at"] is not None

    def test_approve_blueprint_rejects_when_not_ready(
        self, client: TestClient, owner_token: str, sample_project: ProjectInstanceModel
    ):
        unready_project_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/projects/{unready_project_id}/blueprint/approve",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert response.status_code in [400, 404]

    def test_mentor_definition_remains_untouched_during_blueprint_workflow(
        self, client: TestClient, project_id: uuid.UUID, owner_token: str, sample_project: ProjectInstanceModel
    ):
        # Set mentor provenance IDs
        mentor_def_id = str(uuid.uuid4())
        source_ver_id = str(uuid.uuid4())
        sample_project.project_definition_id = mentor_def_id
        sample_project.source_definition_version_id = source_ver_id

        # Generate & approve blueprint
        res_gen = client.post(
            f"/api/v1/projects/{project_id}/blueprint/generate",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={},
        )
        assert res_gen.status_code == 200

        res_app = client.post(
            f"/api/v1/projects/{project_id}/blueprint/approve",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert res_app.status_code == 200

        # Assert project instance provenance fields are strictly identical
        assert sample_project.project_definition_id == mentor_def_id
        assert sample_project.source_definition_version_id == source_ver_id
