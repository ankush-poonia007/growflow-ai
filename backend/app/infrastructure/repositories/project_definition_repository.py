"""
GrowFlow — Project Definition Repository Implementation.

Provides persistence operations for mentor project definitions and their
immutable version snapshots.

Architecture ref:
  6A § 7 — Repository Architecture
  6B § 7.1 — project_definitions
  6B § 7.2 — project_definition_versions
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy import func, select

from backend.app.domain.project.models import ProjectComplexity, ProjectDefinitionStatus
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
)
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class ProjectDefinitionRepository(BaseRepository[ProjectDefinitionModel]):
    """Repository managing mentor-owned project definitions and immutable versions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectDefinitionModel)

    async def list_by_mentor(
        self, mentor_id: uuid.UUID | str, status: str | None = None
    ) -> Sequence[tuple[ProjectDefinitionModel, ProjectDefinitionVersionModel | None]]:
        stmt = (
            select(ProjectDefinitionModel, ProjectDefinitionVersionModel)
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionModel.current_version_id == ProjectDefinitionVersionModel.id,
            )
            .where(ProjectDefinitionModel.owner_mentor_id == str(mentor_id))
            .order_by(
                ProjectDefinitionModel.updated_at.desc(),
                ProjectDefinitionModel.name.asc(),
            )
        )
        if status:
            stmt = stmt.where(ProjectDefinitionModel.status == status)
        result = await self._session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_active_catalog(
        self,
    ) -> Sequence[tuple[ProjectDefinitionModel, ProjectDefinitionVersionModel | None]]:
        """Retrieve all ACTIVE project definitions efficiently outer-joined with their current version snapshot."""
        stmt = (
            select(ProjectDefinitionModel, ProjectDefinitionVersionModel)
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionModel.current_version_id == ProjectDefinitionVersionModel.id,
            )
            .where(ProjectDefinitionModel.status == ProjectDefinitionStatus.ACTIVE.value)
            .order_by(
                ProjectDefinitionModel.created_at.desc(),
                ProjectDefinitionModel.name.asc(),
            )
        )
        result = await self._session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_active_catalog_item(
        self, definition_id: uuid.UUID | str
    ) -> tuple[ProjectDefinitionModel, ProjectDefinitionVersionModel | None] | None:
        """Retrieve an ACTIVE project definition outer-joined with its current version snapshot."""
        stmt = (
            select(ProjectDefinitionModel, ProjectDefinitionVersionModel)
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionModel.current_version_id == ProjectDefinitionVersionModel.id,
            )
            .where(
                ProjectDefinitionModel.id == str(definition_id),
                ProjectDefinitionModel.status == ProjectDefinitionStatus.ACTIVE.value,
            )
        )
        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            return None
        return (row[0], row[1])

    async def create_definition(
        self,
        owner_mentor_id: uuid.UUID | str,
        name: str,
        status: str = ProjectDefinitionStatus.DRAFT.value,
    ) -> ProjectDefinitionModel:
        definition = ProjectDefinitionModel(
            id=uuid.uuid4(),
            owner_mentor_id=str(owner_mentor_id),
            name=name.strip(),
            status=status,
        )
        return await self.add(definition)

    async def get_latest_version_number(self, definition_id: uuid.UUID | str) -> int:
        result = await self._session.execute(
            select(func.coalesce(func.max(ProjectDefinitionVersionModel.version_number), 0)).where(
                ProjectDefinitionVersionModel.project_definition_id == str(definition_id)
            )
        )
        return int(result.scalar_one())

    async def create_version(
        self,
        project_definition_id: uuid.UUID | str,
        *,
        name: str,
        problem: str,
        proposed_solution: str,
        created_by: uuid.UUID | str,
        complexity: str = ProjectComplexity.INTERMEDIATE.value,
        description: str = "",
        duration: str = "",
        constraints: str = "",
        assumptions: str = "",
        technology_snapshot: list[dict[str, Any]] | None = None,
    ) -> ProjectDefinitionVersionModel:
        latest = await self.get_latest_version_number(project_definition_id)
        new_version_num = latest + 1

        version = ProjectDefinitionVersionModel(
            id=uuid.uuid4(),
            project_definition_id=str(project_definition_id),
            version_number=new_version_num,
            name=name.strip(),
            problem=problem.strip(),
            proposed_solution=proposed_solution.strip(),
            complexity=complexity,
            description=description.strip(),
            duration=duration.strip(),
            constraints=constraints.strip(),
            assumptions=assumptions.strip(),
            technology_snapshot=technology_snapshot or [],
            created_by=str(created_by),
        )
        self._session.add(version)
        await self._session.flush()
        await self._session.refresh(version)

        # Update definition pointer to current version
        definition = await self.get_by_id(project_definition_id)
        if definition:
            definition.current_version_id = str(version.id)
            await self._session.flush()

        return version

    async def get_version(
        self, definition_id: uuid.UUID | str, version_number: int
    ) -> ProjectDefinitionVersionModel | None:
        result = await self._session.execute(
            select(ProjectDefinitionVersionModel).where(
                ProjectDefinitionVersionModel.project_definition_id == str(definition_id),
                ProjectDefinitionVersionModel.version_number == version_number,
            )
        )
        return result.scalar_one_or_none()

    async def get_version_by_id(
        self, version_id: uuid.UUID | str
    ) -> ProjectDefinitionVersionModel | None:
        result = await self._session.execute(
            select(ProjectDefinitionVersionModel).where(
                ProjectDefinitionVersionModel.id == str(version_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_versions(
        self, definition_id: uuid.UUID | str
    ) -> Sequence[ProjectDefinitionVersionModel]:
        result = await self._session.execute(
            select(ProjectDefinitionVersionModel)
            .where(ProjectDefinitionVersionModel.project_definition_id == str(definition_id))
            .order_by(ProjectDefinitionVersionModel.version_number.desc())
        )
        return result.scalars().all()
