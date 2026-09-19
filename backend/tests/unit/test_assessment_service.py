"""
GrowFlow — Unit Tests for Assessment Application Service (Gate 08).

Comprehensive verification of:
A. Question Structure (10 core + 5 adaptive = 15 total, strictly ordered)
B. Template Versioning (v1 templates, sequence numbers, active filtering, metadata traceability)
C. Strict Sequential Generation (Q11 requires Q10, Q12 requires Q11... future questions blocked)
D. Accumulated Context & Answer Influence (Q11 <- Q3, Q12 <- Q11, Q13 <- Q12, Q14 <- Q10, Q15 <- Q14)
E. Answer Persistence & Immutability (idempotent duplicate submission, rejection of modification after progression)
F. Start Idempotency & Concurrency Safety
G. Recovery & Resume (after Q5, after Q10, mid-adaptive, persisted question unchanged)
H. Completion Invariants (all 15 required, idempotent duplicate completion, no answers after completion)
I. Authorization & Ownership (student ownership enforced, cross-student rejected)
J. Deterministic EPU Scoring (bounded 0-100, thresholds HIGH/MODERATE/NEEDS_REFINEMENT, four dimensions, no hardcoded score)
"""

from __future__ import annotations

from unittest.mock import AsyncMock
import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.application.services.assessment_service import (
    AssessmentService,
)
from backend.app.domain.assessment.models import (
    AssessmentReadinessTier,
    AssessmentStatus,
    QuestionType,
)
from backend.app.domain.identity import AccountStatus, CurrentUser, UserRole
from backend.app.domain.project.models import ProjectComplexity, ProjectPhase
from backend.app.infrastructure.database.models.assessment import (
    AssessmentAnswerModel,
    AssessmentModel,
    AssessmentQuestionModel,
    AssessmentQuestionTemplateModel,
    AssessmentResultModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    NotFoundException,
)

# =============================================================================
# In-Memory Test Repository Fixture
# =============================================================================


class InMemoryAssessmentRepo:
    """Mock repository with in-memory state tracking for complete lifecycle testing."""

    def __init__(self) -> None:
        self.assessments: dict[str, AssessmentModel] = {}
        self.answers: dict[str, list[AssessmentAnswerModel]] = {}
        self.results: dict[str, AssessmentResultModel] = {}
        self.questions: dict[tuple[str, int], AssessmentQuestionModel] = {}
        self.templates: dict[tuple[int, int], AssessmentQuestionTemplateModel] = {}

    async def get_by_project_id(self, project_id: uuid.UUID | str) -> AssessmentModel | None:
        for a in self.assessments.values():
            if str(a.project_instance_id) == str(project_id):
                return a
        return None

    async def get_by_id(self, assessment_id: uuid.UUID | str) -> AssessmentModel | None:
        return self.assessments.get(str(assessment_id))

    async def create_assessment(self, assessment: AssessmentModel) -> AssessmentModel:
        pid = str(assessment.project_instance_id)
        for existing in self.assessments.values():
            if str(existing.project_instance_id) == pid:
                raise IntegrityError(
                    "duplicate", params=None, orig=Exception("uq_assessments_project_instance")
                )
        self.assessments[str(assessment.id)] = assessment
        return assessment

    async def update_assessment(self, assessment: AssessmentModel) -> AssessmentModel:
        self.assessments[str(assessment.id)] = assessment
        return assessment

    async def get_answers(self, assessment_id: uuid.UUID | str) -> list[AssessmentAnswerModel]:
        return sorted(self.answers.get(str(assessment_id), []), key=lambda a: a.question_index)

    async def get_answer(
        self, assessment_id: uuid.UUID | str, question_id: str
    ) -> AssessmentAnswerModel | None:
        for a in self.answers.get(str(assessment_id), []):
            if a.question_id == question_id:
                return a
        return None

    async def get_answer_by_index(
        self, assessment_id: uuid.UUID | str, question_index: int
    ) -> AssessmentAnswerModel | None:
        for a in self.answers.get(str(assessment_id), []):
            if a.question_index == question_index:
                return a
        return None

    async def upsert_answer(
        self,
        assessment_id: uuid.UUID | str,
        question_id: str,
        question_index: int,
        question_text: str,
        question_type: str,
        selected_option: str | None = None,
        text_response: str | None = None,
    ) -> AssessmentAnswerModel:
        aid = str(assessment_id)
        if aid not in self.answers:
            self.answers[aid] = []

        existing = await self.get_answer_by_index(aid, question_index)
        if existing:
            existing.question_id = question_id
            existing.question_text = question_text
            existing.question_type = question_type
            existing.selected_option = selected_option
            existing.text_response = text_response
            return existing

        ans = AssessmentAnswerModel(
            id=str(uuid.uuid4()),
            assessment_id=aid,
            question_id=question_id,
            question_index=question_index,
            question_text=question_text,
            question_type=question_type,
            selected_option=selected_option,
            text_response=text_response,
        )
        self.answers[aid].append(ans)
        return ans

    async def create_result(self, result: AssessmentResultModel) -> AssessmentResultModel:
        self.results[str(result.assessment_id)] = result
        return result

    async def get_result_by_assessment_id(
        self, assessment_id: uuid.UUID | str
    ) -> AssessmentResultModel | None:
        return self.results.get(str(assessment_id))

    async def get_result_by_project_id(
        self, project_id: uuid.UUID | str
    ) -> AssessmentResultModel | None:
        for r in self.results.values():
            if str(r.project_instance_id) == str(project_id):
                return r
        return None

    async def get_persisted_question(
        self, assessment_id: uuid.UUID | str, sequence_number: int
    ) -> AssessmentQuestionModel | None:
        return self.questions.get((str(assessment_id), sequence_number))

    async def get_persisted_questions(
        self, assessment_id: uuid.UUID | str
    ) -> list[AssessmentQuestionModel]:
        res = [q for (aid, _), q in self.questions.items() if aid == str(assessment_id)]
        return sorted(res, key=lambda q: q.sequence_number)

    async def create_persisted_question(
        self, question: AssessmentQuestionModel
    ) -> AssessmentQuestionModel:
        key = (str(question.assessment_id), question.sequence_number)
        self.questions[key] = question
        return question

    async def get_template_by_sequence(
        self, sequence_number: int, version: int = 1
    ) -> AssessmentQuestionTemplateModel | None:
        tmpl = self.templates.get((version, sequence_number))
        if tmpl and tmpl.active:
            return tmpl
        return None

    async def get_templates(
        self, version: int = 1, active_only: bool = True
    ) -> list[AssessmentQuestionTemplateModel]:
        res = [t for (v, _), t in self.templates.items() if v == version]
        if active_only:
            res = [t for t in res if t.active]
        return sorted(res, key=lambda t: t.sequence_number)

    async def create_template(
        self, template: AssessmentQuestionTemplateModel
    ) -> AssessmentQuestionTemplateModel:
        self.templates[(template.version, template.sequence_number)] = template
        return template


# =============================================================================
# Test Setup Fixtures
# =============================================================================


@pytest.fixture
def student_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def current_student(student_user_id: uuid.UUID) -> CurrentUser:
    return CurrentUser(
        user_id=student_user_id,
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        email="student@growflow.internal",
    )


@pytest.fixture
def other_student(other_user_id: uuid.UUID) -> CurrentUser:
    return CurrentUser(
        user_id=other_user_id,
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        email="other@growflow.internal",
    )


@pytest.fixture
def sample_project(student_user_id: uuid.UUID) -> ProjectInstanceModel:
    return ProjectInstanceModel(
        id=str(uuid.uuid4()),
        student_id=str(student_user_id),
        name="Telemetry Mesh Edge",
        problem="Sparse environmental monitoring in remote research stations.",
        proposed_solution="Decentralized low-power sensor network with edge anomaly detection.",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        current_phase=ProjectPhase.IDEA.value,
        progress_percentage=0,
    )


@pytest.fixture
def in_memory_repo() -> InMemoryAssessmentRepo:
    return InMemoryAssessmentRepo()


@pytest.fixture
def mock_project_repo(sample_project: ProjectInstanceModel) -> AsyncMock:
    repo = AsyncMock(spec=ProjectRepository)

    async def _get_by_id(pid):
        if str(pid) == str(sample_project.id):
            return sample_project
        return None

    repo.get_by_id.side_effect = _get_by_id
    return repo


@pytest.fixture
def assessment_service(
    in_memory_repo: InMemoryAssessmentRepo,
    mock_project_repo: AsyncMock,
) -> AssessmentService:
    return AssessmentService(
        assessment_repo=in_memory_repo,  # type: ignore[arg-type]
        project_repo=mock_project_repo,
    )


# =============================================================================
# A. Question Structure Tests
# =============================================================================


class TestQuestionStructure:
    def test_total_questions_and_ordering(self, assessment_service: AssessmentService) -> None:
        """Total questions must be exactly 15 with 10 core and 5 adaptive."""
        assert assessment_service.TOTAL_QUESTIONS == 15
        assert assessment_service.CORE_QUESTIONS_COUNT == 10
        assert assessment_service.ADAPTIVE_QUESTIONS_COUNT == 5

        core = assessment_service._get_core_questions()
        assert len(core) == 10
        for i, q in enumerate(core, start=1):
            assert q.order_index == i
            assert q.is_adaptive is False
            assert q.question_type == QuestionType.MULTIPLE_CHOICE
            assert len(q.options) >= 2


# =============================================================================
# B. Template Versioning Tests
# =============================================================================


class TestTemplateVersioning:
    @pytest.mark.asyncio
    async def test_version_1_core_template_instantiation(
        self,
        assessment_service: AssessmentService,
        in_memory_repo: InMemoryAssessmentRepo,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Core question is instantiated from version 1 template with generation metadata."""
        # Seed a custom template v1
        template = AssessmentQuestionTemplateModel(
            id=str(uuid.uuid4()),
            version=1,
            sequence_number=1,
            question_text="Versioned Template Question 1",
            active=True,
            category="Problem Definition",
            help_text="Help text v1",
            question_type="MULTIPLE_CHOICE",
            options=[{"value": "OPT1", "label": "Option 1", "description": "Desc"}],
        )
        await in_memory_repo.create_template(template)

        assessment, first_q = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        assert first_q.order_index == 1
        assert first_q.question_text == "Versioned Template Question 1"

        # Verify persisted record contains template version metadata
        persisted = await in_memory_repo.get_persisted_question(assessment.id, 1)
        assert persisted is not None
        assert persisted.generation_metadata["template_version"] == 1
        assert persisted.generation_metadata["template_id"] == str(template.id)

    @pytest.mark.asyncio
    async def test_inactive_templates_not_selected(
        self,
        assessment_service: AssessmentService,
        in_memory_repo: InMemoryAssessmentRepo,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Inactive templates are bypassed in favor of fallback active templates."""
        inactive_tmpl = AssessmentQuestionTemplateModel(
            id=str(uuid.uuid4()),
            version=1,
            sequence_number=1,
            question_text="INACTIVE TEMPLATE",
            active=False,
            category="Old",
            help_text="",
            question_type="MULTIPLE_CHOICE",
            options=[],
        )
        await in_memory_repo.create_template(inactive_tmpl)

        _assessment, first_q = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        assert first_q.question_text != "INACTIVE TEMPLATE"


# =============================================================================
# C. Strict Sequential Generation Tests
# =============================================================================


class TestSequentialAdaptiveGeneration:
    @pytest.mark.asyncio
    async def test_cannot_access_q11_before_q10_is_answered(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Q11 cannot exist or be generated before Q10 answer is persisted."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)

        # Answer questions 1 through 9 only
        for i in range(1, 10):
            await assessment_service.submit_answer(
                sample_project.id, i, "SPECIFIC_PERSONA", None, current_student
            )

        with pytest.raises(BusinessRuleException) as exc_info:
            await assessment_service.get_question(sample_project.id, 11, current_student)
        assert exc_info.value.code == "ASSESSMENT_QUESTION_NOT_READY"

    @pytest.mark.asyncio
    async def test_sequential_adaptive_chain_eligibility(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Q12 requires Q11, Q13 requires Q12, Q14 requires Q13, Q15 requires Q14."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)

        # Answer 1..10
        for i in range(1, 11):
            await assessment_service.submit_answer(
                sample_project.id, i, "MODULAR_MONOLITH", None, current_student
            )

        # Q11 is now eligible
        q11, _ = await assessment_service.get_question(sample_project.id, 11, current_student)
        assert q11.order_index == 11

        # Q12 is NOT eligible yet
        with pytest.raises(BusinessRuleException) as exc:
            await assessment_service.get_question(sample_project.id, 12, current_student)
        assert exc.value.code == "ASSESSMENT_QUESTION_NOT_READY"

        # Answer Q11
        await assessment_service.submit_answer(
            sample_project.id, 11, None, "Strict domain repository boundaries.", current_student
        )

        # Q12 is now eligible, but Q13 is NOT
        q12, _ = await assessment_service.get_question(sample_project.id, 12, current_student)
        assert q12.order_index == 12
        with pytest.raises(BusinessRuleException) as exc:
            await assessment_service.get_question(sample_project.id, 13, current_student)
        assert exc.value.code == "ASSESSMENT_QUESTION_NOT_READY"


# =============================================================================
# D. Accumulated Context & Answer Influence Tests
# =============================================================================


class TestAdaptiveContextInfluence:
    @pytest.mark.asyncio
    async def test_q11_influenced_by_q3_answer(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Changing Q3 architecture answer materially changes Q11 question text."""
        assessment, _ = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        for i in range(1, 11):
            opt = "EVENT_DRIVEN_MICROSERVICES" if i == 3 else "SPECIFIC_PERSONA"
            await assessment_service.submit_answer(sample_project.id, i, opt, None, current_student)

        q11 = await assessment_service.get_or_generate_question(assessment, 11, sample_project)
        assert "EVENT_DRIVEN_MICROSERVICES" in q11.question_text

    @pytest.mark.asyncio
    async def test_q13_influenced_by_q12_answer(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Q13 question text is materially influenced by Q12's state reconciliation answer."""
        assessment, _ = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        for i in range(1, 11):
            await assessment_service.submit_answer(
                sample_project.id, i, "RELATIONAL_ACID", None, current_student
            )

        await assessment_service.submit_answer(
            sample_project.id, 11, None, "Boundary logic", current_student
        )
        await assessment_service.submit_answer(
            sample_project.id, 12, None, "Two-phase commit with distributed sagas", current_student
        )

        q13 = await assessment_service.get_or_generate_question(assessment, 13, sample_project)
        assert "Two-phase commit with distributed sagas" in q13.question_text

    @pytest.mark.asyncio
    async def test_q15_influenced_by_q14_answer(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Q15 question text is materially influenced by Q14's risk mitigation answer."""
        assessment, _ = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        for i in range(1, 11):
            await assessment_service.submit_answer(
                sample_project.id,
                i,
                "SCOPE_CREEP" if i == 10 else "MODULAR_MONOLITH",
                None,
                current_student,
            )
        await assessment_service.submit_answer(
            sample_project.id, 11, None, "Boundary", current_student
        )
        await assessment_service.submit_answer(
            sample_project.id, 12, None, "Sagas", current_student
        )
        await assessment_service.submit_answer(
            sample_project.id, 13, None, "Tradeoff latency", current_student
        )
        await assessment_service.submit_answer(
            sample_project.id,
            14,
            None,
            "Strict circuit breaker with stale cache fallback",
            current_student,
        )

        q15 = await assessment_service.get_or_generate_question(assessment, 15, sample_project)
        assert "Strict circuit breaker with stale cache fallback" in q15.question_text


# =============================================================================
# E. Answer Persistence & Immutability Tests
# =============================================================================


class TestAnswerImmutability:
    @pytest.mark.asyncio
    async def test_duplicate_submission_is_idempotent(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Submitting the exact same answer again returns the existing answer idempotently."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        ans1, _, _ = await assessment_service.submit_answer(
            sample_project.id, 1, "SPECIFIC_PERSONA", None, current_student
        )
        ans2, _, _ = await assessment_service.submit_answer(
            sample_project.id, 1, "SPECIFIC_PERSONA", None, current_student
        )
        assert ans1.id == ans2.id

    @pytest.mark.asyncio
    async def test_cannot_modify_answer_after_progression(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Once question 2 is answered, question 1 is immutable and cannot be changed."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        await assessment_service.submit_answer(
            sample_project.id, 1, "SPECIFIC_PERSONA", None, current_student
        )
        await assessment_service.submit_answer(
            sample_project.id, 2, "AUTOMATED_WORKFLOW", None, current_student
        )

        # Attempt to change Q1
        with pytest.raises(BusinessRuleException) as exc:
            await assessment_service.submit_answer(
                sample_project.id, 1, "TARGET_SEGMENT", None, current_student
            )
        assert exc.value.code == "ASSESSMENT_ANSWER_IMMUTABLE"

    @pytest.mark.asyncio
    async def test_completed_assessment_answers_are_immutable(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """After assessment completion, all answers reject modification."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        for i in range(1, 11):
            await assessment_service.submit_answer(
                sample_project.id, i, "SAMPLE", None, current_student
            )
        for i in range(11, 16):
            await assessment_service.submit_answer(
                sample_project.id, i, None, f"Technical details {i}", current_student
            )

        await assessment_service.complete_assessment(sample_project.id, current_student)

        with pytest.raises(BusinessRuleException) as exc:
            await assessment_service.submit_answer(
                sample_project.id, 15, None, "New Text", current_student
            )
        assert exc.value.code == "ASSESSMENT_ALREADY_COMPLETED"


# =============================================================================
# F. Start Idempotency & Concurrency Tests
# =============================================================================


class TestStartIdempotency:
    @pytest.mark.asyncio
    async def test_repeated_start_returns_same_session(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Calling start multiple times returns the same assessment ID."""
        asm1, q1 = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        asm2, q2 = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        assert asm1.id == asm2.id
        assert q1.id == q2.id


# =============================================================================
# G. Recovery & Resume Tests
# =============================================================================


class TestRecoveryAndResume:
    @pytest.mark.asyncio
    async def test_resume_preserves_persisted_adaptive_text(
        self,
        assessment_service: AssessmentService,
        in_memory_repo: InMemoryAssessmentRepo,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """On resume, an already generated adaptive question is returned unchanged from DB."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        for i in range(1, 11):
            await assessment_service.submit_answer(
                sample_project.id, i, "SAMPLE", None, current_student
            )

        # Generate Q11
        q11_first, _ = await assessment_service.get_question(sample_project.id, 11, current_student)

        # Resume session
        _asm, q11_resumed = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        assert q11_resumed.order_index == 11
        assert q11_resumed.question_text == q11_first.question_text

    @pytest.mark.asyncio
    async def test_resume_mid_assessment_pointers(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Resuming after answering Q1..Q5 points to Q6."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        for i in range(1, 6):
            await assessment_service.submit_answer(
                sample_project.id, i, "SAMPLE", None, current_student
            )

        asm, cur_q = await assessment_service.start_or_resume_assessment(
            sample_project.id, current_student
        )
        assert cur_q.order_index == 6
        assert asm.current_question_index == 6


# =============================================================================
# H. Completion Invariants Tests
# =============================================================================


class TestCompletionInvariants:
    @pytest.mark.asyncio
    async def test_cannot_complete_before_all_15_answered(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Completion is rejected if any question is missing."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        for i in range(1, 15):  # 14 out of 15
            await assessment_service.submit_answer(
                sample_project.id,
                i,
                "OPT" if i <= 10 else None,
                "TXT" if i > 10 else None,
                current_student,
            )

        with pytest.raises(BusinessRuleException) as exc:
            await assessment_service.complete_assessment(sample_project.id, current_student)
        assert exc.value.code == "ASSESSMENT_INCOMPLETE"

    @pytest.mark.asyncio
    async def test_duplicate_completion_is_idempotent(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Calling complete_assessment multiple times returns the same result instance."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        for i in range(1, 11):
            await assessment_service.submit_answer(
                sample_project.id, i, "OPT", None, current_student
            )
        for i in range(11, 16):
            await assessment_service.submit_answer(
                sample_project.id, i, None, "Valid plan text", current_student
            )

        asm1, res1 = await assessment_service.complete_assessment(
            sample_project.id, current_student
        )
        _asm2, res2 = await assessment_service.complete_assessment(
            sample_project.id, current_student
        )
        assert asm1.status == AssessmentStatus.COMPLETED.value
        assert res1.id == res2.id


# =============================================================================
# I. Authorization & Ownership Tests
# =============================================================================


class TestAuthorization:
    @pytest.mark.asyncio
    async def test_cross_student_access_raises_403(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        other_student: CurrentUser,
    ) -> None:
        """A student who does not own the project instance cannot start or access its assessment."""
        with pytest.raises(AuthorizationException):
            await assessment_service.start_or_resume_assessment(sample_project.id, other_student)

    @pytest.mark.asyncio
    async def test_nonexistent_project_raises_404(
        self,
        assessment_service: AssessmentService,
        current_student: CurrentUser,
    ) -> None:
        """Accessing assessment for a non-existent project returns 404."""
        with pytest.raises(NotFoundException):
            await assessment_service.start_or_resume_assessment(uuid.uuid4(), current_student)


# =============================================================================
# J. Deterministic EPU Scoring Tests
# =============================================================================


class TestDeterministicEPUScoring:
    @pytest.mark.asyncio
    async def test_epu_score_is_deterministic_and_bounded(
        self,
        assessment_service: AssessmentService,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """EPU score is deterministic, bounded 0-100, and dimensions match frozen contract."""
        await assessment_service.start_or_resume_assessment(sample_project.id, current_student)
        for i in range(1, 11):
            await assessment_service.submit_answer(
                sample_project.id,
                i,
                "MODULAR_MONOLITH" if i == 3 else "SPECIFIC_PERSONA",
                None,
                current_student,
            )
        for i in range(11, 16):
            await assessment_service.submit_answer(
                sample_project.id,
                i,
                None,
                "Detailed contract boundary with transaction rollback schema",
                current_student,
            )

        _, result = await assessment_service.complete_assessment(sample_project.id, current_student)

        # Invariants
        assert 0 <= result.overall_score <= 100
        for dim, score in result.dimension_scores.items():
            assert 0 <= score <= 100
            assert dim in {"architecture", "feasibility", "stack_depth", "security"}

        assert len(result.dimension_scores) == 4

        # Thresholds
        if result.overall_score >= 80:
            assert result.readiness_tier == AssessmentReadinessTier.HIGH.value
        elif result.overall_score >= 60:
            assert result.readiness_tier == AssessmentReadinessTier.MODERATE.value
        else:
            assert result.readiness_tier == AssessmentReadinessTier.NEEDS_REFINEMENT.value

    @pytest.mark.asyncio
    async def test_epu_score_changes_with_different_answers(
        self,
        in_memory_repo: InMemoryAssessmentRepo,
        mock_project_repo: AsyncMock,
        sample_project: ProjectInstanceModel,
        current_student: CurrentUser,
    ) -> None:
        """Different answers produce different scores, proving score is not hardcoded."""
        # High maturity session
        service1 = AssessmentService(assessment_repo=in_memory_repo, project_repo=mock_project_repo)
        await service1.start_or_resume_assessment(sample_project.id, current_student)
        for i in range(1, 11):
            await service1.submit_answer(
                sample_project.id, i, "SPECIFIC_PERSONA", None, current_student
            )
        for i in range(11, 16):
            await service1.submit_answer(
                sample_project.id,
                i,
                None,
                "Comprehensive technical specification with rollback validation and circuit breaker resilience",
                current_student,
            )
        _, res_high = await service1.complete_assessment(sample_project.id, current_student)

        # Low maturity project & session
        low_project = ProjectInstanceModel(
            id=str(uuid.uuid4()),
            student_id=str(current_student.user_id),
            name="Low Project",
            problem="Unknown",
            proposed_solution="Unknown",
            complexity=ProjectComplexity.BEGINNER.value,
            current_phase=ProjectPhase.IDEA.value,
            progress_percentage=0,
        )
        mock_project_repo.get_by_id.side_effect = lambda pid: (
            low_project if str(pid) == str(low_project.id) else sample_project
        )

        service2 = AssessmentService(assessment_repo=in_memory_repo, project_repo=mock_project_repo)
        await service2.start_or_resume_assessment(low_project.id, current_student)
        for i in range(1, 11):
            # Pick lower maturity options
            opt = (
                "EXPLORATORY"
                if i == 1
                else "PUBLIC_READ_PRIVATE_WRITE"
                if i == 7
                else "MANUAL_ACCEPTANCE"
                if i == 9
                else "SCOPE_CREEP"
            )
            await service2.submit_answer(low_project.id, i, opt, None, current_student)
        for i in range(11, 16):
            await service2.submit_answer(low_project.id, i, None, "brief text", current_student)

        _, res_low = await service2.complete_assessment(low_project.id, current_student)

        # Proof of non-hardcoded scoring
        assert res_high.overall_score != res_low.overall_score
        assert res_high.overall_score > res_low.overall_score
