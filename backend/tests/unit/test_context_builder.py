"""
GrowFlow — Unit Tests for Project Context Builder.

Verifies:
- ProjectBaseContext and AssessmentContext assembled accurately from repositories.
- Project profile and technology preferences correctly mapped.
- Assessment EPU and student answers correctly captured.
- Graceful handling of missing/incomplete assessment data.
- Distinct agent projections contain only specified fields.
- Absence of ORM models or credentials in output contracts.
- Deterministic text truncation for long-form answers (> 500 chars).
"""

from unittest.mock import AsyncMock
import uuid

import pytest

from backend.app.domain.ai.context.builder import (
    MAX_TEXT_RESPONSE_LENGTH,
    ProjectContextBuilder,
    _truncate_text,
)
from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole


class MockProjectInstance:
    """Mock project instance entity."""

    def __init__(self, project_id: str, student_id: str, name: str = "AgriDrone"):
        self.id = project_id
        self.student_id = student_id
        self.name = name
        self.problem = "Pest infestation causes crop loss"
        self.proposed_solution = "Autonomous camera drones"
        self.complexity = "INTERMEDIATE"
        self.current_phase = "BLUEPRINT"
        self.health = "HEALTHY"


class MockProjectProfile:
    """Mock project profile entity."""

    def __init__(self):
        self.objective = "Deliver an MVP in 12 weeks"
        self.target_users = "Farmers and agronomists"
        self.constraints = "Must operate offline on edge"
        self.assumptions = "GPS availability in fields"


class MockProjectTech:
    """Mock project technology entity."""

    def __init__(self, purpose: str, category: str):
        self.purpose = purpose
        self.category = category
        self.technology_id = str(uuid.uuid4())


class MockAssessment:
    """Mock assessment session."""

    def __init__(self, assessment_id: str, project_id: str):
        self.id = assessment_id
        self.project_instance_id = project_id
        self.status = "COMPLETED"


class MockAssessmentAnswer:
    """Mock assessment answer entity."""

    def __init__(self, qid: str, idx: int, qtext: str, option: str | None, text: str | None):
        self.question_id = qid
        self.question_index = idx
        self.question_text = qtext
        self.selected_option = option
        self.text_response = text


class MockAssessmentResult:
    """Mock assessment result (EPU) entity."""

    def __init__(self):
        self.skill_level = "INTERMEDIATE"
        self.project_complexity = "INTERMEDIATE"
        self.alignment = "HIGH"
        self.technical_confidence = "HIGH"
        self.learning_depth = "DEEP"
        self.overall_score = 88
        self.readiness_tier = "HIGH"
        self.dimension_scores = {"backend": 85, "architecture": 90}
        self.identified_gaps = ["Lack of drone edge runtime experience"]
        self.recommendations = ["Focus on lightweight Python frameworks"]


@pytest.fixture
def mock_current_user():
    """Create test student user."""
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="student@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        full_name="Alex Farmer",
    )


@pytest.fixture
def mock_project_repo(mock_current_user):
    """Create mock ProjectRepository."""
    repo = AsyncMock()
    project_id = str(uuid.uuid4())
    project = MockProjectInstance(project_id, str(mock_current_user.user_id))
    profile = MockProjectProfile()
    technologies = [
        MockProjectTech(purpose="FastAPI Web Framework", category="Backend"),
        MockProjectTech(purpose="PostgreSQL Relational DB", category="Database"),
    ]

    repo.get_by_id = AsyncMock(return_value=project)
    repo.get_profile = AsyncMock(return_value=profile)
    repo.list_technologies = AsyncMock(return_value=technologies)
    return repo


@pytest.fixture
def mock_assessment_repo(mock_project_repo):
    """Create mock AssessmentRepository."""
    repo = AsyncMock()
    assessment_id = str(uuid.uuid4())
    assessment = MockAssessment(assessment_id, mock_project_repo.get_by_id.return_value.id)
    answers = [
        MockAssessmentAnswer("Q01", 1, "What is your primary language?", "Python", None),
        MockAssessmentAnswer("Q02", 2, "Describe your project vision in detail", None, "A" * 600),
    ]
    result = MockAssessmentResult()

    repo.get_by_project_id = AsyncMock(return_value=assessment)
    repo.get_answers = AsyncMock(return_value=answers)
    repo.get_result_by_assessment_id = AsyncMock(return_value=result)
    return repo


@pytest.mark.asyncio
async def test_build_base_contexts_happy_path(
    mock_project_repo, mock_assessment_repo, mock_current_user
):
    """Verify context builder correctly maps project and assessment data into typed contracts."""
    builder = ProjectContextBuilder(
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
    )
    project_id = mock_project_repo.get_by_id.return_value.id
    base_ctx, assess_ctx = await builder.build_base_contexts(project_id, mock_current_user)

    # 1. ProjectBaseContext verification
    assert base_ctx.name == "AgriDrone"
    assert base_ctx.profile_objective == "Deliver an MVP in 12 weeks"
    assert len(base_ctx.preferred_technologies) == 2
    assert "FastAPI Web Framework" in base_ctx.preferred_technologies

    # 2. AssessmentContext verification
    assert assess_ctx.skill_level == "INTERMEDIATE"
    assert assess_ctx.overall_score == 88
    assert assess_ctx.readiness_tier == "HIGH"
    assert len(assess_ctx.answers) == 2
    assert assess_ctx.answers[0].selected_option == "Python"


@pytest.mark.asyncio
async def test_text_truncation_limits_long_responses(
    mock_project_repo, mock_assessment_repo, mock_current_user
):
    """Verify long-form text responses exceeding 500 characters are deterministically truncated."""
    builder = ProjectContextBuilder(
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
    )
    project_id = mock_project_repo.get_by_id.return_value.id
    _, assess_ctx = await builder.build_base_contexts(project_id, mock_current_user)

    truncated_answer = assess_ctx.answers[1]
    assert truncated_answer.text_response is not None
    assert len(truncated_answer.text_response) <= MAX_TEXT_RESPONSE_LENGTH + len(" ...[truncated]")
    assert truncated_answer.text_response.endswith("...[truncated]")


@pytest.mark.asyncio
async def test_build_base_contexts_handles_missing_assessment_gracefully(
    mock_project_repo, mock_assessment_repo, mock_current_user
):
    """Verify builder produces default assessment context when no assessment was recorded."""
    mock_assessment_repo.get_by_project_id = AsyncMock(return_value=None)
    builder = ProjectContextBuilder(
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
    )
    project_id = mock_project_repo.get_by_id.return_value.id
    base_ctx, assess_ctx = await builder.build_base_contexts(project_id, mock_current_user)

    assert base_ctx.name == "AgriDrone"
    assert assess_ctx.skill_level == "INTERMEDIATE"
    assert assess_ctx.answers == []


@pytest.mark.asyncio
async def test_purpose_built_agent_projections(
    mock_project_repo, mock_assessment_repo, mock_current_user
):
    """Verify purpose-built projections deliver only the intended fields per agent."""
    builder = ProjectContextBuilder(
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
    )
    project_id = mock_project_repo.get_by_id.return_value.id
    base_ctx, assess_ctx = await builder.build_base_contexts(project_id, mock_current_user)

    # 1. Idea projection contains problem and readiness tier
    idea_ctx = builder.build_idea_context(base_ctx, assess_ctx)
    assert idea_ctx.project_name == "AgriDrone"
    assert idea_ctx.readiness_tier == "HIGH"

    # 2. Technology projection contains preferred technologies but not user profiles
    tech_ctx = builder.build_technology_context(base_ctx, assess_ctx)
    assert "FastAPI Web Framework" in tech_ctx.preferred_technologies
    assert not hasattr(tech_ctx, "profile_objective")

    # 3. Scope projection contains constraints and identified gaps
    scope_ctx = builder.build_scope_context(base_ctx, assess_ctx)
    assert "offline" in scope_ctx.profile_constraints
    assert len(scope_ctx.identified_gaps) == 1

    # 4. Projections are distinct
    assert type(idea_ctx) is not type(tech_ctx)
    assert type(tech_ctx) is not type(scope_ctx)


def test_truncate_text_helper():
    """Verify standalone _truncate_text utility."""
    assert _truncate_text(None) is None
    assert _truncate_text("Short text") == "Short text"
    long_str = "x" * 600
    truncated = _truncate_text(long_str, max_len=500)
    assert truncated is not None
    assert len(truncated) == 500 + len(" ...[truncated]")
    assert truncated.endswith("...[truncated]")
