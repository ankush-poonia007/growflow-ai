"""
GrowFlow — Technology Repository Implementation.

Provides persistence operations for technologies and student_technologies.

Architecture ref:
  6A § 7 — Repository Architecture
  6B § 5.5 — technologies
  6B § 5.6 — student_technologies
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import delete, select

from backend.app.infrastructure.database.models.profile import (
    StudentTechnologyModel,
    TechnologyModel,
)
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class TechnologyRepository(BaseRepository[TechnologyModel]):
    """Repository managing the canonical technology catalog and student associations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=TechnologyModel)

    async def get_by_name(self, name: str) -> TechnologyModel | None:
        result = await self._session.execute(
            select(TechnologyModel).where(TechnologyModel.name.ilike(name.strip()))
        )
        return result.scalar_one_or_none()

    async def list_technologies(self, category: str | None = None) -> Sequence[TechnologyModel]:
        stmt = select(TechnologyModel)
        if category:
            stmt = stmt.where(TechnologyModel.category == category)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_technology(self, name: str, category: str) -> TechnologyModel:
        tech = TechnologyModel(
            id=uuid.uuid4(),
            name=name.strip(),
            category=category.strip(),
        )
        return await self.add(tech)

    async def get_student_technologies(
        self, student_id: uuid.UUID | str
    ) -> Sequence[StudentTechnologyModel]:
        result = await self._session.execute(
            select(StudentTechnologyModel).where(
                StudentTechnologyModel.student_id == str(student_id)
            )
        )
        return result.scalars().all()

    async def add_student_technology(
        self,
        student_id: uuid.UUID | str,
        technology_id: uuid.UUID | str,
        *,
        proficiency: str = "INTERMEDIATE",
        relationship_type: str = "KNOWN",
    ) -> StudentTechnologyModel:
        # Check if relation already exists
        result = await self._session.execute(
            select(StudentTechnologyModel).where(
                StudentTechnologyModel.student_id == str(student_id),
                StudentTechnologyModel.technology_id == str(technology_id),
                StudentTechnologyModel.relationship_type == relationship_type,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            existing.proficiency = proficiency
            await self._session.flush()
            await self._session.refresh(existing)
            return existing

        item = StudentTechnologyModel(
            id=uuid.uuid4(),
            student_id=str(student_id),
            technology_id=str(technology_id),
            proficiency=proficiency,
            relationship_type=relationship_type,
        )
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def remove_student_technology(
        self,
        student_id: uuid.UUID | str,
        technology_id: uuid.UUID | str,
        relationship_type: str | None = None,
    ) -> None:
        stmt = delete(StudentTechnologyModel).where(
            StudentTechnologyModel.student_id == str(student_id),
            StudentTechnologyModel.technology_id == str(technology_id),
        )
        if relationship_type:
            stmt = stmt.where(StudentTechnologyModel.relationship_type == relationship_type)
        await self._session.execute(stmt)
        await self._session.flush()
