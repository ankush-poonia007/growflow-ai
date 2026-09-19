"""
GrowFlow — Assessment Repository Implementation.

Provides persistence operations for:
- assessments (session entity)
- assessment_answers (answer entities)
- assessment_results (enriched project understanding entity)

Architecture ref:
  6A § 7 — Repository Architecture
  6N § 10 — Data Access Layer (AssessmentRepository)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import select

from backend.app.infrastructure.database.models.assessment import (
    AssessmentAnswerModel,
    AssessmentModel,
    AssessmentQuestionModel,
    AssessmentQuestionTemplateModel,
    AssessmentResultModel,
)
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class AssessmentRepository(BaseRepository[AssessmentModel]):
    """Repository managing assessment sessions, student answers, and enriched results."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=AssessmentModel)

    async def get_by_project_id(self, project_id: uuid.UUID | str) -> AssessmentModel | None:
        stmt = select(AssessmentModel).where(AssessmentModel.project_instance_id == str(project_id))
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, assessment_id: uuid.UUID | str) -> AssessmentModel | None:
        stmt = select(AssessmentModel).where(AssessmentModel.id == str(assessment_id))
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def create_assessment(self, assessment: AssessmentModel) -> AssessmentModel:
        self._session.add(assessment)
        await self._session.flush()
        await self._session.refresh(assessment)
        return assessment

    async def update_assessment(self, assessment: AssessmentModel) -> AssessmentModel:
        await self._session.flush()
        await self._session.refresh(assessment)
        return assessment

    async def get_answers(self, assessment_id: uuid.UUID | str) -> Sequence[AssessmentAnswerModel]:
        stmt = (
            select(AssessmentAnswerModel)
            .where(AssessmentAnswerModel.assessment_id == str(assessment_id))
            .order_by(AssessmentAnswerModel.question_index.asc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_answer(
        self, assessment_id: uuid.UUID | str, question_id: str
    ) -> AssessmentAnswerModel | None:
        stmt = select(AssessmentAnswerModel).where(
            AssessmentAnswerModel.assessment_id == str(assessment_id),
            AssessmentAnswerModel.question_id == question_id,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

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
        existing = await self.get_answer(assessment_id, question_id)
        if existing:
            existing.question_index = question_index
            existing.question_text = question_text
            existing.question_type = question_type
            existing.selected_option = selected_option
            existing.text_response = text_response
            await self._session.flush()
            await self._session.refresh(existing)
            return existing

        answer = AssessmentAnswerModel(
            id=str(uuid.uuid4()),
            assessment_id=str(assessment_id),
            question_id=question_id,
            question_index=question_index,
            question_text=question_text,
            question_type=question_type,
            selected_option=selected_option,
            text_response=text_response,
        )
        self._session.add(answer)
        await self._session.flush()
        await self._session.refresh(answer)
        return answer

    async def create_result(self, result: AssessmentResultModel) -> AssessmentResultModel:
        self._session.add(result)
        await self._session.flush()
        await self._session.refresh(result)
        return result

    async def get_result_by_assessment_id(
        self, assessment_id: uuid.UUID | str
    ) -> AssessmentResultModel | None:
        stmt = select(AssessmentResultModel).where(
            AssessmentResultModel.assessment_id == str(assessment_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_result_by_project_id(
        self, project_id: uuid.UUID | str
    ) -> AssessmentResultModel | None:
        stmt = select(AssessmentResultModel).where(
            AssessmentResultModel.project_instance_id == str(project_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    # -------------------------------------------------------------------------
    # Question Templates (Versioned Core Questions)
    # -------------------------------------------------------------------------

    async def get_templates(
        self, version: int = 1, active_only: bool = True
    ) -> Sequence[AssessmentQuestionTemplateModel]:
        stmt = select(AssessmentQuestionTemplateModel).where(
            AssessmentQuestionTemplateModel.version == version
        )
        if active_only:
            stmt = stmt.where(AssessmentQuestionTemplateModel.active.is_(True))
        stmt = stmt.order_by(AssessmentQuestionTemplateModel.sequence_number.asc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_template_by_sequence(
        self, sequence_number: int, version: int = 1
    ) -> AssessmentQuestionTemplateModel | None:
        stmt = select(AssessmentQuestionTemplateModel).where(
            AssessmentQuestionTemplateModel.version == version,
            AssessmentQuestionTemplateModel.sequence_number == sequence_number,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def create_template(
        self, template: AssessmentQuestionTemplateModel
    ) -> AssessmentQuestionTemplateModel:
        self._session.add(template)
        await self._session.flush()
        await self._session.refresh(template)
        return template

    # -------------------------------------------------------------------------
    # Persisted Generated Questions
    # -------------------------------------------------------------------------

    async def get_persisted_question(
        self, assessment_id: uuid.UUID | str, sequence_number: int
    ) -> AssessmentQuestionModel | None:
        stmt = select(AssessmentQuestionModel).where(
            AssessmentQuestionModel.assessment_id == str(assessment_id),
            AssessmentQuestionModel.sequence_number == sequence_number,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_persisted_questions(
        self, assessment_id: uuid.UUID | str
    ) -> Sequence[AssessmentQuestionModel]:
        stmt = (
            select(AssessmentQuestionModel)
            .where(AssessmentQuestionModel.assessment_id == str(assessment_id))
            .order_by(AssessmentQuestionModel.sequence_number.asc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_persisted_question(
        self, question: AssessmentQuestionModel
    ) -> AssessmentQuestionModel:
        self._session.add(question)
        await self._session.flush()
        await self._session.refresh(question)
        return question

    async def get_answer_by_index(
        self, assessment_id: uuid.UUID | str, question_index: int
    ) -> AssessmentAnswerModel | None:
        stmt = select(AssessmentAnswerModel).where(
            AssessmentAnswerModel.assessment_id == str(assessment_id),
            AssessmentAnswerModel.question_index == question_index,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()
