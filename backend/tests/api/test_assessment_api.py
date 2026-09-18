"""
GrowFlow Batch S07–S11 — API & Domain Tests for Student Assessment Workflow.

Covers:
1. Unauthenticated requests return 401 Unauthorized.
2. Cross-student access returns 403 Forbidden.
3. Nonexistent project returns 404 Not Found.
4. Starting assessment initializes session & transitions phase IDEA -> ASSESSMENT.
5. Resuming assessment is idempotent and does not create duplicate rows.
6. Core questions retrieval (1..10) with structured choices.
7. Answer submission persists answer and advances question pointer.
8. Answer re-submission upserts in-place without duplicate rows.
9. Adaptive questions retrieval (11..15) with project-specific context.
10. Completing incomplete assessment returns 400 BusinessRuleException.
11. Completing full 15-question assessment returns Enriched Project Understanding.
12. Duplicate completion request is idempotent and returns existing result.
13. Result retrieval returns canonical project understanding and dimensional scores.
14. Result retrieval before completion returns 404 Not Found.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import (
    get_assessment_service,
    get_group_service,
    get_profile_service,
    get_project_definition_service,
    get_project_service,
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
    AssessmentAnswerModel,
    AssessmentModel,
    AssessmentResultModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.assessment_repository import (
    AssessmentRepository,
)
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator
    from backend.app.config.settings import Settings


_TEST_SECRET = "gate-05-test-secret-at-least-32-chars-long-123"
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
def mentor_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def project_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def owner_token(owner_student_id: uuid.UUID) -> str:
    return _make_jwt(
        owner_student_id,
        "student.owner@example.com",
        UserRole.STUDENT.value,
    )


@pytest.fixture
def other_token(other_student_id: uuid.UUID) -> str:
    return _make_jwt(
        other_student_id,
        "other.student@example.com",
        UserRole.STUDENT.value,
    )


@pytest.fixture
def mentor_token(mentor_id: uuid.UUID) -> str:
    return _make_jwt(
        mentor_id,
        "mentor@example.com",
        UserRole.MENTOR.value,
    )




@pytest.fixture
def mock_owner_project(owner_student_id: uuid.UUID, project_id: uuid.UUID) -> ProjectInstanceModel:
    return ProjectInstanceModel(
        id=str(project_id),
        student_id=str(owner_student_id),
        name="Autonomous Solar Rover",
        problem="High cost and manual effort in off-grid solar farm inspection.",
        proposed_solution="Lightweight autonomous rover equipped with thermal cameras and ROS2 navigation.",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=0,
        status=ProjectStatus.ACTIVE.value,
    )


@pytest.fixture
def mock_assessment_repo() -> AsyncMock:
    repo = AsyncMock(spec=AssessmentRepository)
    repo._answers = {}
    repo._assessment = None
    repo._result = None

    async def _get_by_project_id(pid):
        if repo._assessment and str(repo._assessment.project_instance_id) == str(pid):
            return repo._assessment
        return None

    async def _get_by_id(aid):
        if repo._assessment and str(repo._assessment.id) == str(aid):
            return repo._assessment
        return None

    async def _create_assessment(asm):
        repo._assessment = asm
        return asm

    async def _update_assessment(asm):
        repo._assessment = asm
        return asm

    async def _get_answers(aid):
        return sorted(list(repo._answers.values()), key=lambda a: a.question_index)

    async def _get_answer(aid, qid):
        return repo._answers.get(qid)

    async def _upsert_answer(assessment_id, question_id, question_index, question_text, question_type, selected_option=None, text_response=None):
        ans = AssessmentAnswerModel(
            id=str(uuid.uuid4()),
            assessment_id=str(assessment_id),
            question_id=question_id,
            question_index=question_index,
            question_text=question_text,
            question_type=question_type,
            selected_option=selected_option,
            text_response=text_response,
        )
        repo._answers[question_id] = ans
        return ans

    async def _create_result(res):
        repo._result = res
        return res

    async def _get_result_by_project_id(pid):
        if repo._result and str(repo._result.project_instance_id) == str(pid):
            return repo._result
        return None

    async def _get_result_by_assessment_id(aid):
        if repo._result and str(repo._result.assessment_id) == str(aid):
            return repo._result
        return None

    repo.get_by_project_id.side_effect = _get_by_project_id
    repo.get_by_id.side_effect = _get_by_id
    repo.create_assessment.side_effect = _create_assessment
    repo.update_assessment.side_effect = _update_assessment
    repo.get_answers.side_effect = _get_answers
    repo.get_answer.side_effect = _get_answer
    repo.upsert_answer.side_effect = _upsert_answer
    repo.create_result.side_effect = _create_result
    repo.get_result_by_project_id.side_effect = _get_result_by_project_id
    repo.get_result_by_assessment_id.side_effect = _get_result_by_assessment_id

    return repo


@pytest.fixture
def mock_project_repo(mock_owner_project: ProjectInstanceModel) -> AsyncMock:
    repo = AsyncMock(spec=ProjectRepository)

    async def _get_by_id(pid):
        if str(pid) == str(mock_owner_project.id):
            return mock_owner_project
        return None

    repo.get_by_id.side_effect = _get_by_id
    return repo



@pytest.fixture
def assessment_client(
    auth_settings: Settings,
    owner_student_id: uuid.UUID,
    other_student_id: uuid.UUID,
    mentor_id: uuid.UUID,
    mock_assessment_repo: AsyncMock,
    mock_project_repo: AsyncMock,
) -> Generator[TestClient, None]:
    app = create_app(settings=auth_settings)

    mock_user_repo = AsyncMock(spec=UserRepository)

    async def _get_user_by_id(uid):
        uid_str = str(uid)
        if uid_str == str(owner_student_id):
            return UserModel(
                id=uid_str,
                email="student.owner@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
                full_name="Owner Student",
            )
        elif uid_str == str(other_student_id):
            return UserModel(
                id=uid_str,
                email="other.student@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
                full_name="Other Student",
            )
        elif uid_str == str(mentor_id):
            return UserModel(
                id=uid_str,
                email="mentor@example.com",
                role=UserRole.MENTOR.value,
                status=AccountStatus.ACTIVE.value,
                full_name="Mentor User",
            )
        return None

    mock_user_repo.get_by_id.side_effect = _get_user_by_id

    from backend.app.application.services.assessment_service import AssessmentService
    service = AssessmentService(
        assessment_repo=mock_assessment_repo,
        project_repo=mock_project_repo,
    )

    async def _override_get_db_session() -> AsyncGenerator[AsyncMock, None]:
        yield AsyncMock()

    app.dependency_overrides[get_db_session] = _override_get_db_session
    app.dependency_overrides[get_assessment_service] = lambda: service

    with patch(
        "backend.app.api.dependencies.auth.UserRepository",
        return_value=mock_user_repo,
    ):
        with TestClient(app, base_url="http://testserver") as client:
            yield client

    app.dependency_overrides.clear()


# ============================================================================
# Tests
# ============================================================================


def test_unauthenticated_requests_return_401(
    assessment_client: TestClient, project_id: uuid.UUID
) -> None:
    res = assessment_client.get(f"/api/v1/projects/{project_id}/assessment/status")
    assert res.status_code == 401


def test_non_student_role_returns_403(
    assessment_client: TestClient, project_id: uuid.UUID, mentor_token: str
) -> None:
    res = assessment_client.get(
        f"/api/v1/projects/{project_id}/assessment/status",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert res.status_code == 403


def test_cross_student_access_returns_403(
    assessment_client: TestClient, project_id: uuid.UUID, other_token: str
) -> None:
    res = assessment_client.get(
        f"/api/v1/projects/{project_id}/assessment/status",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403


def test_nonexistent_project_returns_404(
    assessment_client: TestClient, owner_token: str
) -> None:
    random_id = uuid.uuid4()
    res = assessment_client.get(
        f"/api/v1/projects/{random_id}/assessment/status",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 404


def test_start_assessment_success_and_lifecycle_sync(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str, mock_owner_project: ProjectInstanceModel
) -> None:
    assert mock_owner_project.current_phase == "IDEA"

    res = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]

    assert data["session"]["status"] == "IN_PROGRESS"
    assert data["session"]["current_question_index"] == 1
    assert data["session"]["total_questions"] == 15
    assert data["current_question"]["order_index"] == 1
    assert data["current_question"]["id"] == "core-01-problem-definition"

    # Verifies phase transition IDEA -> ASSESSMENT occurred
    assert mock_owner_project.current_phase == "ASSESSMENT"


def test_resume_assessment_is_idempotent(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str
) -> None:
    # 1st start
    res1 = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res1.status_code == 200

    # 2nd start (resume)
    res2 = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res2.status_code == 200
    assert res2.json()["data"]["session"]["status"] == "IN_PROGRESS"


def test_get_question_by_index(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str
) -> None:
    # Must start session first
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    res = assessment_client.get(
        f"/api/v1/projects/{project_id}/assessment/questions/3",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    q = res.json()["data"]["question"]
    assert q["order_index"] == 3
    assert q["id"] == "core-03-system-architecture"
    assert len(q["options"]) == 4


def test_invalid_question_index_returns_400(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str
) -> None:
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    res = assessment_client.get(
        f"/api/v1/projects/{project_id}/assessment/questions/99",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 400


def test_submit_answer_and_upsert(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str
) -> None:
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Submit answer 1
    res1 = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/answers",
        json={
            "question_index": 1,
            "selected_option": "SPECIFIC_PERSONA",
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res1.status_code == 200
    body1 = res1.json()["data"]
    assert body1["answer"]["selected_option"] == "SPECIFIC_PERSONA"
    assert body1["answered_count"] == 1
    assert body1["next_question_index"] == 2

    # Re-submit answer 1 with updated selection
    res2 = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/answers",
        json={
            "question_index": 1,
            "selected_option": "TARGET_SEGMENT",
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res2.status_code == 200
    body2 = res2.json()["data"]
    assert body2["answer"]["selected_option"] == "TARGET_SEGMENT"
    # Still count == 1, row was updated not duplicated
    assert body2["answered_count"] == 1


def test_adaptive_questions_incorporate_project_context(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str
) -> None:
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Get question 11
    res = assessment_client.get(
        f"/api/v1/projects/{project_id}/assessment/questions/11",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    q = res.json()["data"]["question"]
    assert q["is_adaptive"] is True
    assert q["context_badge"] == "ADAPTIVE: ARCHITECTURAL BOUNDARIES"
    assert "Autonomous Solar Rover" in q["question_text"]


def test_complete_incomplete_assessment_returns_400(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str
) -> None:
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Only answer Q1
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/answers",
        json={"question_index": 1, "selected_option": "SPECIFIC_PERSONA"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Try to complete
    res = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/complete",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 400
    assert "ASSESSMENT_INCOMPLETE" in res.json()["error"]["code"]


def test_complete_full_assessment_and_get_result(
    assessment_client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
    mock_owner_project: ProjectInstanceModel,
) -> None:
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Answer all 15 questions
    for idx in range(1, 11):
        assessment_client.post(
            f"/api/v1/projects/{project_id}/assessment/answers",
            json={"question_index": idx, "selected_option": "SAMPLE_OPTION"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
    for idx in range(11, 16):
        assessment_client.post(
            f"/api/v1/projects/{project_id}/assessment/answers",
            json={"question_index": idx, "text_response": f"Detailed technical plan for question {idx}."},
            headers={"Authorization": f"Bearer {owner_token}"},
        )

    # Complete
    res = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/complete",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    result_data = res.json()["data"]

    assert result_data["readiness_tier"] == "HIGH"
    assert result_data["overall_score"] == 84
    assert result_data["skill_level"] == "Intermediate"
    assert "dimension_scores" in result_data
    assert "identified_gaps" in result_data
    assert "recommendations" in result_data
    assert mock_owner_project.progress_percentage == 25

    # Retrieve result endpoint
    res_get = assessment_client.get(
        f"/api/v1/projects/{project_id}/assessment/result",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res_get.status_code == 200
    assert res_get.json()["data"]["id"] == result_data["id"]

    # Duplicate complete call is idempotent
    res_dup = assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/complete",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res_dup.status_code == 200
    assert res_dup.json()["data"]["id"] == result_data["id"]


def test_get_result_before_completion_returns_404(
    assessment_client: TestClient, project_id: uuid.UUID, owner_token: str
) -> None:
    assessment_client.post(
        f"/api/v1/projects/{project_id}/assessment/start",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    res = assessment_client.get(
        f"/api/v1/projects/{project_id}/assessment/result",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 404

