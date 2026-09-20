"""
GrowFlow — Project Context Builder Service.

Coordinates:
- Deterministic project authorization and student tenancy checks BEFORE context assembly.
- Single-fetch extraction of project instance, profile, and selected technologies.
- Scoped extraction of completed assessment results (EPU) and student answers.
- Bounded, deterministic truncation of long-form text responses.
- Creation of immutable typed ProjectBaseContext and AssessmentContext.
- Creation of purpose-built, minimal agent projections to honor token budgets.

Architecture ref:
  6F § 15 — Agent Context Architecture
  6F § 16 — Context Is Not 'Everything'
  6F § 17 — Agent Context Contracts
  6F § 82 — Context Budgeting
  6F § 89 — Agent Security
  6F § 90 — Agent Data Isolation
  Gate 09 — Unit 2 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from backend.app.domain.ai.context.models import (
    AssessmentAnswerItem,
    AssessmentContext,
    FeaturesAgentContext,
    IdeaAgentContext,
    MilestoneAgentContext,
    MVPAgentContext,
    ProjectBaseContext,
    QAJudgeAgentContext,
    ReadmeAgentContext,
    RiskAgentContext,
    ScopeAgentContext,
    SpecificationAgentContext,
    TaskAgentContext,
    TechnologyAgentContext,
    TimelineAgentContext,
)
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.repositories.assessment_repository import AssessmentRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository

logger = get_logger("growflow.domain.ai.context.builder")

MAX_TEXT_RESPONSE_LENGTH = 500


def _truncate_text(text: str | None, max_len: int = MAX_TEXT_RESPONSE_LENGTH) -> str | None:
    """Deterministically truncate long-form responses to prevent prompt explosion."""
    if not text:
        return text
    stripped = text.strip()
    if len(stripped) <= max_len:
        return stripped
    return stripped[:max_len] + " ...[truncated]"


class ProjectContextBuilder:
    """
    Centralized service responsible for authorized extraction and tailored
    projection of project and assessment context for AI agent reasoning.
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        assessment_repo: AssessmentRepository,
    ) -> None:
        self._project_repo = project_repo
        self._assessment_repo = assessment_repo

    async def build_base_contexts(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> tuple[ProjectBaseContext, AssessmentContext]:
        """
        Authorize the caller, query PostgreSQL repositories, and assemble
        immutable ProjectBaseContext and AssessmentContext.
        """
        # 1. Deterministic Tenancy & Ownership Authorization
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found.", code="PROJECT_NOT_FOUND")

        if not current_user.is_admin and str(project.student_id) != str(current_user.user_id):
            logger.warning(
                "Unauthorized project context access attempt",
                caller_user_id=str(current_user.user_id),
                project_id=str(project_id),
                owner_student_id=str(project.student_id),
            )
            raise AuthorizationException(
                "Access to this project is denied.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )

        if not current_user.is_student and not current_user.is_admin:
            raise AuthorizationException(
                "Only students and administrators may build project AI context.",
                code="AUTH_FORBIDDEN_ROLE",
            )

        # 2. Extract Project Profile and Selected Technologies
        profile = await self._project_repo.get_profile(project.id)
        tech_records = await self._project_repo.list_technologies(project.id)

        preferred_technologies: list[str] = []
        for t in tech_records:
            pref = (
                getattr(t, "purpose", "")
                or getattr(t, "category", "")
                or str(getattr(t, "technology_id", ""))
            )
            if pref:
                preferred_technologies.append(pref)

        project_base = ProjectBaseContext(
            project_id=uuid.UUID(str(project.id)),
            student_id=uuid.UUID(str(project.student_id)),
            name=project.name,
            problem=project.problem or "Unspecified problem domain",
            proposed_solution=project.proposed_solution or "Unspecified technical solution",
            complexity=project.complexity or "INTERMEDIATE",
            current_phase=project.current_phase or "IDEA",
            health=project.health or "HEALTHY",
            profile_objective=profile.objective if profile else "",
            profile_target_users=profile.target_users if profile else "",
            profile_constraints=profile.constraints if profile else "",
            profile_assumptions=profile.assumptions if profile else "",
            preferred_technologies=preferred_technologies,
        )

        # 3. Extract Assessment Results & Answers
        assessment = await self._assessment_repo.get_by_project_id(project.id)
        answers: list[AssessmentAnswerItem] = []
        result_data: dict[str, Any] = {}

        if assessment:
            session_answers = await self._assessment_repo.get_answers(assessment.id)
            for a in session_answers:
                answers.append(
                    AssessmentAnswerItem(
                        question_id=a.question_id,
                        question_index=a.question_index,
                        question_text=a.question_text,
                        selected_option=a.selected_option,
                        text_response=_truncate_text(a.text_response),
                    )
                )

            res_model = await self._assessment_repo.get_result_by_assessment_id(assessment.id)
            if res_model:
                result_data = {
                    "skill_level": res_model.skill_level,
                    "project_complexity": res_model.project_complexity,
                    "alignment": res_model.alignment,
                    "technical_confidence": res_model.technical_confidence,
                    "learning_depth": res_model.learning_depth,
                    "overall_score": res_model.overall_score,
                    "readiness_tier": str(res_model.readiness_tier),
                    "dimension_scores": res_model.dimension_scores or {},
                    "identified_gaps": res_model.identified_gaps or [],
                    "recommendations": res_model.recommendations or [],
                }

        assessment_context = AssessmentContext(
            assessment_id=uuid.UUID(str(assessment.id)) if assessment else uuid.uuid4(),
            project_id=uuid.UUID(str(project.id)),
            skill_level=result_data.get("skill_level", "INTERMEDIATE"),
            project_complexity=result_data.get(
                "project_complexity", project.complexity or "INTERMEDIATE"
            ),
            alignment=result_data.get("alignment", "MODERATE"),
            technical_confidence=result_data.get("technical_confidence", "MODERATE"),
            learning_depth=result_data.get("learning_depth", "STANDARD"),
            overall_score=result_data.get("overall_score", 75),
            readiness_tier=result_data.get("readiness_tier", "MODERATE"),
            dimension_scores=result_data.get("dimension_scores", {}),
            identified_gaps=result_data.get("identified_gaps", []),
            recommendations=result_data.get("recommendations", []),
            answers=answers,
        )

        return project_base, assessment_context

    # ==========================================================================
    # Purpose-Built Agent Projections
    # ==========================================================================

    @staticmethod
    def build_idea_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> IdeaAgentContext:
        """Project context required for Idea Agent."""
        return IdeaAgentContext(
            project_name=base.name,
            problem=base.problem,
            proposed_solution=base.proposed_solution,
            complexity=base.complexity,
            skill_level=assessment.skill_level,
            readiness_tier=assessment.readiness_tier,
            assessment_recommendations=assessment.recommendations,
        )

    @staticmethod
    def build_scope_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> ScopeAgentContext:
        """Project context required for Scope Agent."""
        return ScopeAgentContext(
            profile_constraints=base.profile_constraints,
            profile_assumptions=base.profile_assumptions,
            identified_gaps=assessment.identified_gaps,
        )

    @staticmethod
    def build_technology_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> TechnologyAgentContext:
        """Project context required for Technology Agent."""
        return TechnologyAgentContext(
            skill_level=assessment.skill_level,
            complexity=base.complexity,
            preferred_technologies=base.preferred_technologies,
        )

    @staticmethod
    def build_features_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> FeaturesAgentContext:
        """Project context required for Features Agent."""
        return FeaturesAgentContext(
            target_users=base.profile_target_users,
            profile_objective=base.profile_objective,
        )

    @staticmethod
    def build_mvp_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> MVPAgentContext:
        """Project context required for MVP Agent."""
        return MVPAgentContext(
            complexity=base.complexity,
            skill_level=assessment.skill_level,
        )

    @staticmethod
    def build_specification_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> SpecificationAgentContext:
        """Project context required for Specification Agent."""
        return SpecificationAgentContext(
            project_name=base.name,
            complexity=base.complexity,
        )

    @staticmethod
    def build_timeline_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> TimelineAgentContext:
        """Project context required for Timeline Agent."""
        return TimelineAgentContext(
            complexity=base.complexity,
            deadline_weeks=12,
        )

    @staticmethod
    def build_risk_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> RiskAgentContext:
        """Project context required for Risk Agent."""
        return RiskAgentContext(
            identified_gaps=assessment.identified_gaps,
            complexity=base.complexity,
        )

    @staticmethod
    def build_task_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> TaskAgentContext:
        """Project context required for Task Agent."""
        return TaskAgentContext(
            complexity=base.complexity,
        )

    @staticmethod
    def build_milestone_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> MilestoneAgentContext:
        """Project context required for Milestone Agent."""
        return MilestoneAgentContext(
            project_name=base.name,
        )

    @staticmethod
    def build_readme_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> ReadmeAgentContext:
        """Project context required for README Agent."""
        return ReadmeAgentContext(
            project_name=base.name,
        )

    @staticmethod
    def build_qa_context(
        base: ProjectBaseContext, assessment: AssessmentContext
    ) -> QAJudgeAgentContext:
        """Project context required for QA / Judge Agent."""
        return QAJudgeAgentContext(
            project_base=base,
            assessment=assessment,
        )
