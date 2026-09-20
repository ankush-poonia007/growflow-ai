"""
GrowFlow — Unit Tests for AI Project Isolation & Tenancy Security.

Verifies:
- Student A cannot build AI context for Student B's project (AuthorizationException).
- Non-existent project ID raises NotFoundException.
- Admin users are permitted cross-project access according to platform rules.
- Project A context contains zero data from Project B.
- Assessment A answers never leak into Project B context.
- Mentor private notes and system credentials are strictly excluded.
- Context builder deterministically enforces current_user token identity.
"""

from unittest.mock import AsyncMock
import uuid

import pytest

from backend.app.domain.ai.context.builder import ProjectContextBuilder
from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)


class MockProjectInstance:
    """Mock project instance entity."""

    def __init__(self, project_id: str, student_id: str, name: str):
        self.id = project_id
        self.student_id = student_id
        self.name = name
        self.problem = f"Problem for {name}"
        self.proposed_solution = f"Solution for {name}"
        self.complexity = "INTERMEDIATE"
        self.current_phase = "BLUEPRINT"
        self.health = "HEALTHY"


class MockAssessment:
    """Mock assessment session entity."""

    def __init__(self, assessment_id: str, project_id: str):
        self.id = assessment_id
        self.project_instance_id = project_id
        self.status = "COMPLETED"


class MockAssessmentAnswer:
    """Mock assessment answer entity."""

    def __init__(self, qid: str, qtext: str, secret_text: str):
        self.question_id = qid
        self.question_index = 1
        self.question_text = qtext
        self.selected_option = None
        self.text_response = secret_text


@pytest.fixture
def student_a():
    """Create authenticated student A."""
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="student_a@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        full_name="Alice Student",
    )


@pytest.fixture
def student_b():
    """Create authenticated student B."""
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="student_b@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        full_name="Bob Student",
    )


@pytest.fixture
def admin_user():
    """Create authenticated platform admin."""
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="admin@growflow.internal",
        role=UserRole.ADMIN,
        status=AccountStatus.ACTIVE,
        full_name="Administrator",
    )


@pytest.mark.asyncio
async def test_student_cannot_access_other_student_project(student_a, student_b):
    """Verify Student B cannot access Student A's project (raises AuthorizationException)."""
    project_repo = AsyncMock()
    assessment_repo = AsyncMock()

    proj_a_id = str(uuid.uuid4())
    proj_a = MockProjectInstance(proj_a_id, str(student_a.user_id), name="Project A")
    project_repo.get_by_id = AsyncMock(return_value=proj_a)

    builder = ProjectContextBuilder(project_repo, assessment_repo)

    # Student B attempts to build context for Student A's project
    with pytest.raises(
        AuthorizationException, match=r"Access to this project is denied\."
    ) as exc_info:
        await builder.build_base_contexts(proj_a_id, current_user=student_b)

    assert exc_info.value.code == "AUTH_FORBIDDEN_RESOURCE"


@pytest.mark.asyncio
async def test_non_existent_project_raises_not_found(student_a):
    """Verify non-existent project raises NotFoundException."""
    project_repo = AsyncMock()
    assessment_repo = AsyncMock()
    project_repo.get_by_id = AsyncMock(return_value=None)

    builder = ProjectContextBuilder(project_repo, assessment_repo)

    with pytest.raises(NotFoundException, match=r"Project not found\.") as exc_info:
        await builder.build_base_contexts(str(uuid.uuid4()), current_user=student_a)

    assert exc_info.value.code == "PROJECT_NOT_FOUND"


@pytest.mark.asyncio
async def test_admin_can_access_any_project(student_a, admin_user):
    """Verify Admin user can assemble context for any project instance."""
    project_repo = AsyncMock()
    assessment_repo = AsyncMock()

    proj_a_id = str(uuid.uuid4())
    proj_a = MockProjectInstance(proj_a_id, str(student_a.user_id), name="Project A")
    project_repo.get_by_id = AsyncMock(return_value=proj_a)
    project_repo.get_profile = AsyncMock(return_value=None)
    project_repo.list_technologies = AsyncMock(return_value=[])
    assessment_repo.get_by_project_id = AsyncMock(return_value=None)

    builder = ProjectContextBuilder(project_repo, assessment_repo)

    base_ctx, _assess_ctx = await builder.build_base_contexts(proj_a_id, current_user=admin_user)
    assert base_ctx.name == "Project A"
    assert base_ctx.student_id == student_a.user_id


@pytest.mark.asyncio
async def test_cross_project_isolation_guarantee(student_a, student_b):
    """Verify Project A context contains ZERO data from Project B and vice versa."""
    project_repo = AsyncMock()
    assessment_repo = AsyncMock()

    proj_a_id = str(uuid.uuid4())
    proj_b_id = str(uuid.uuid4())

    proj_a = MockProjectInstance(proj_a_id, str(student_a.user_id), name="Alpha Secret Agronomy")
    proj_b = MockProjectInstance(
        proj_b_id, str(student_b.user_id), name="Beta Confidential Fintech"
    )

    assess_a = MockAssessment(str(uuid.uuid4()), proj_a_id)
    assess_b = MockAssessment(str(uuid.uuid4()), proj_b_id)

    answers_a = [MockAssessmentAnswer("Q01", "Vision", "Alpha Secret Soil Technology")]
    answers_b = [MockAssessmentAnswer("Q01", "Vision", "Beta Confidential Banking API")]

    def mock_get_by_id(pid):
        if str(pid) == proj_a_id:
            return proj_a
        if str(pid) == proj_b_id:
            return proj_b
        return None

    def mock_get_by_project_id(pid):
        if str(pid) == proj_a_id:
            return assess_a
        if str(pid) == proj_b_id:
            return assess_b
        return None

    def mock_get_answers(aid):
        if str(aid) == assess_a.id:
            return answers_a
        if str(aid) == assess_b.id:
            return answers_b
        return []

    project_repo.get_by_id = AsyncMock(side_effect=mock_get_by_id)
    project_repo.get_profile = AsyncMock(return_value=None)
    project_repo.list_technologies = AsyncMock(return_value=[])

    assessment_repo.get_by_project_id = AsyncMock(side_effect=mock_get_by_project_id)
    assessment_repo.get_answers = AsyncMock(side_effect=mock_get_answers)
    assessment_repo.get_result_by_assessment_id = AsyncMock(return_value=None)

    builder = ProjectContextBuilder(project_repo, assessment_repo)

    # 1. Build context for Student A
    base_a, assess_ctx_a = await builder.build_base_contexts(proj_a_id, current_user=student_a)
    assert "Alpha" in base_a.name
    assert "Beta" not in base_a.name
    assert "Beta" not in assess_ctx_a.answers[0].text_response

    # 2. Build context for Student B
    base_b, assess_ctx_b = await builder.build_base_contexts(proj_b_id, current_user=student_b)
    assert "Beta" in base_b.name
    assert "Alpha" not in base_b.name
    assert "Alpha" not in assess_ctx_b.answers[0].text_response


@pytest.mark.asyncio
async def test_absence_of_credentials_and_mentor_notes(student_a):
    """Verify built context dictionary has zero credential or mentor notes attributes."""
    project_repo = AsyncMock()
    assessment_repo = AsyncMock()

    proj_a_id = str(uuid.uuid4())
    proj_a = MockProjectInstance(proj_a_id, str(student_a.user_id), name="Safe Project")
    project_repo.get_by_id = AsyncMock(return_value=proj_a)
    project_repo.get_profile = AsyncMock(return_value=None)
    project_repo.list_technologies = AsyncMock(return_value=[])
    assessment_repo.get_by_project_id = AsyncMock(return_value=None)

    builder = ProjectContextBuilder(project_repo, assessment_repo)
    base_ctx, assess_ctx = await builder.build_base_contexts(proj_a_id, current_user=student_a)

    dumped_base = base_ctx.model_dump()
    dumped_assess = assess_ctx.model_dump()

    # Assert no sensitive keys exist
    forbidden_keys = {"mentor_notes", "api_key", "secret", "password", "token", "service_role"}
    assert not forbidden_keys.intersection(dumped_base.keys())
    assert not forbidden_keys.intersection(dumped_assess.keys())
