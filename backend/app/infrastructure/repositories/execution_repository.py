"""
GrowFlow — Execution Management Repositories.

Provides repository implementations for:
- MilestoneRepository
- TaskRepository
- RiskRepository
- DocumentRepository

Architecture ref:
  6B § 20 & § 44 — Execution Entities
  Gate 10 — Execution Management
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy import delete, func, or_, select

from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectMilestoneModel,
    ProjectRiskModel,
    ProjectTaskModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class MilestoneRepository(BaseRepository[ProjectMilestoneModel]):
    """Repository managing operational project milestones."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectMilestoneModel)

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectMilestoneModel]:
        stmt = (
            select(ProjectMilestoneModel)
            .where(ProjectMilestoneModel.project_instance_id == str(project_id))
            .order_by(ProjectMilestoneModel.section_order.asc(), ProjectMilestoneModel.created_at.asc())
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, milestone_id: uuid.UUID | str) -> ProjectMilestoneModel | None:
        stmt = select(ProjectMilestoneModel).where(ProjectMilestoneModel.id == str(milestone_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def count_by_project(self, project_id: uuid.UUID | str) -> int:
        stmt = (
            select(func.count(ProjectMilestoneModel.id))
            .where(ProjectMilestoneModel.project_instance_id == str(project_id))
        )
        res = await self._session.execute(stmt)
        return res.scalar() or 0

    async def bulk_create(self, milestones: list[ProjectMilestoneModel]) -> None:
        self._session.add_all(milestones)
        await self._session.flush()


class TaskRepository(BaseRepository[ProjectTaskModel]):
    """Repository managing operational project tasks."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectTaskModel)

    async def list_by_project(
        self,
        project_id: uuid.UUID | str,
        *,
        status: str | None = None,
        priority: str | None = None,
        milestone_id: str | None = None,
        phase: str | None = None,
        search: str | None = None,
    ) -> list[ProjectTaskModel]:
        stmt = select(ProjectTaskModel).where(
            ProjectTaskModel.project_instance_id == str(project_id)
        )

        if status:
            stmt = stmt.where(ProjectTaskModel.status == status)
        if priority:
            stmt = stmt.where(ProjectTaskModel.priority == priority)
        if milestone_id:
            stmt = stmt.where(ProjectTaskModel.milestone_id == milestone_id)
        if phase:
            stmt = stmt.where(ProjectTaskModel.phase == phase)
        if search:
            q = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(ProjectTaskModel.title).like(q),
                    func.lower(ProjectTaskModel.description).like(q),
                    func.lower(ProjectTaskModel.task_code).like(q),
                    func.lower(ProjectTaskModel.category).like(q),
                )
            )

        stmt = stmt.order_by(ProjectTaskModel.created_at.asc())
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, task_id: uuid.UUID | str) -> ProjectTaskModel | None:
        stmt = select(ProjectTaskModel).where(ProjectTaskModel.id == str(task_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def count_by_project(self, project_id: uuid.UUID | str) -> int:
        stmt = (
            select(func.count(ProjectTaskModel.id))
            .where(ProjectTaskModel.project_instance_id == str(project_id))
        )
        res = await self._session.execute(stmt)
        return res.scalar() or 0

    async def count_completed_by_project(self, project_id: uuid.UUID | str) -> int:
        stmt = (
            select(func.count(ProjectTaskModel.id))
            .where(
                ProjectTaskModel.project_instance_id == str(project_id),
                ProjectTaskModel.status == "COMPLETED",
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar() or 0

    async def bulk_create(self, tasks: list[ProjectTaskModel]) -> None:
        self._session.add_all(tasks)
        await self._session.flush()

    async def delete_by_id(self, task_id: uuid.UUID | str) -> bool:
        task = await self.get_by_id(task_id)
        if not task:
            return False
        await self._session.delete(task)
        await self._session.flush()
        return True


class RiskRepository(BaseRepository[ProjectRiskModel]):
    """Repository managing operational project risks."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectRiskModel)

    async def list_by_project(
        self,
        project_id: uuid.UUID | str,
        *,
        status: str | None = None,
        severity: str | None = None,
        search: str | None = None,
    ) -> list[ProjectRiskModel]:
        stmt = select(ProjectRiskModel).where(
            ProjectRiskModel.project_instance_id == str(project_id)
        )

        if status:
            stmt = stmt.where(ProjectRiskModel.status == status)
        if severity:
            stmt = stmt.where(ProjectRiskModel.severity == severity)
        if search:
            q = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(ProjectRiskModel.title).like(q),
                    func.lower(ProjectRiskModel.description).like(q),
                    func.lower(ProjectRiskModel.risk_code).like(q),
                    func.lower(ProjectRiskModel.mitigation).like(q),
                )
            )

        stmt = stmt.order_by(ProjectRiskModel.created_at.asc())
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, risk_id: uuid.UUID | str) -> ProjectRiskModel | None:
        stmt = select(ProjectRiskModel).where(ProjectRiskModel.id == str(risk_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def count_by_project(self, project_id: uuid.UUID | str) -> int:
        stmt = (
            select(func.count(ProjectRiskModel.id))
            .where(ProjectRiskModel.project_instance_id == str(project_id))
        )
        res = await self._session.execute(stmt)
        return res.scalar() or 0

    async def bulk_create(self, risks: list[ProjectRiskModel]) -> None:
        self._session.add_all(risks)
        await self._session.flush()

    async def delete_by_id(self, risk_id: uuid.UUID | str) -> bool:
        risk = await self.get_by_id(risk_id)
        if not risk:
            return False
        await self._session.delete(risk)
        await self._session.flush()
        return True


class DocumentRepository(BaseRepository[ProjectDocumentModel]):
    """Repository managing operational project documents."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectDocumentModel)

    async def list_by_project(
        self,
        project_id: uuid.UUID | str,
        *,
        doc_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[ProjectDocumentModel]:
        stmt = select(ProjectDocumentModel).where(
            ProjectDocumentModel.project_instance_id == str(project_id)
        )

        if doc_type:
            stmt = stmt.where(ProjectDocumentModel.doc_type == doc_type)
        if status:
            stmt = stmt.where(ProjectDocumentModel.status == status)
        if search:
            q = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(ProjectDocumentModel.title).like(q),
                    func.lower(ProjectDocumentModel.document_key).like(q),
                    func.lower(ProjectDocumentModel.content).like(q),
                )
            )

        stmt = stmt.order_by(ProjectDocumentModel.created_at.asc())
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, document_id: uuid.UUID | str) -> ProjectDocumentModel | None:
        stmt = select(ProjectDocumentModel).where(ProjectDocumentModel.id == str(document_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_key(
        self, project_id: uuid.UUID | str, document_key: str
    ) -> ProjectDocumentModel | None:
        stmt = select(ProjectDocumentModel).where(
            ProjectDocumentModel.project_instance_id == str(project_id),
            ProjectDocumentModel.document_key == document_key,
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def count_by_project(self, project_id: uuid.UUID | str) -> int:
        stmt = (
            select(func.count(ProjectDocumentModel.id))
            .where(ProjectDocumentModel.project_instance_id == str(project_id))
        )
        res = await self._session.execute(stmt)
        return res.scalar() or 0

    async def bulk_create(self, documents: list[ProjectDocumentModel]) -> None:
        self._session.add_all(documents)
        await self._session.flush()

    async def list_platform_documents(
        self,
        *,
        search: str | None = None,
        doc_type: str | None = None,
        status: str | None = None,
        project_id: uuid.UUID | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[tuple[ProjectDocumentModel, str]]:
        """List platform-wide documents with project information, filtering, and pagination."""
        stmt = (
            select(ProjectDocumentModel, ProjectInstanceModel.name)
            .outerjoin(ProjectInstanceModel, ProjectDocumentModel.project_instance_id == ProjectInstanceModel.id)
        )
        if project_id:
            stmt = stmt.where(ProjectDocumentModel.project_instance_id == str(project_id))
        if doc_type and doc_type.upper() != "ALL":
            stmt = stmt.where(ProjectDocumentModel.doc_type == doc_type.upper())
        if status and status.upper() != "ALL":
            stmt = stmt.where(ProjectDocumentModel.status == status.upper())
        if search and search.strip():
            q = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(ProjectDocumentModel.title).like(q),
                    func.lower(ProjectDocumentModel.document_key).like(q),
                    func.lower(ProjectInstanceModel.name).like(q),
                )
            )
        stmt = stmt.order_by(ProjectDocumentModel.created_at.desc()).offset(offset).limit(limit)
        res = await self._session.execute(stmt)
        return [(doc, proj_name or "Unknown Project") for doc, proj_name in res.all()]

    async def count_platform_documents(
        self,
        *,
        search: str | None = None,
        doc_type: str | None = None,
        status: str | None = None,
        project_id: uuid.UUID | str | None = None,
    ) -> int:
        """Count platform-wide documents matching filters."""
        stmt = select(func.count(ProjectDocumentModel.id)).outerjoin(
            ProjectInstanceModel, ProjectDocumentModel.project_instance_id == ProjectInstanceModel.id
        )
        if project_id:
            stmt = stmt.where(ProjectDocumentModel.project_instance_id == str(project_id))
        if doc_type and doc_type.upper() != "ALL":
            stmt = stmt.where(ProjectDocumentModel.doc_type == doc_type.upper())
        if status and status.upper() != "ALL":
            stmt = stmt.where(ProjectDocumentModel.status == status.upper())
        if search and search.strip():
            q = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(ProjectDocumentModel.title).like(q),
                    func.lower(ProjectDocumentModel.document_key).like(q),
                    func.lower(ProjectInstanceModel.name).like(q),
                )
            )
        res = await self._session.execute(stmt)
        return res.scalar_one() or 0

