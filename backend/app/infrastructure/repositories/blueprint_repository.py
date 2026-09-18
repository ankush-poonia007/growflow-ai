"""
GrowFlow — Blueprint Repository Implementation.

Provides persistence operations for:
- blueprints (canonical blueprint entity)
- blueprint_jobs (asynchronous/persistent generation job records)

Architecture ref:
  6A § 7 — Repository Architecture
  6N § 10 — Data Access Layer (BlueprintRepository)
  Gate 09 — AI Blueprint & Agent System
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy import func, select

from backend.app.domain.blueprint.models import BlueprintJobStatus, BlueprintQAStatus, BlueprintStatus
from backend.app.infrastructure.database.models.blueprint import (
    BlueprintJobModel,
    BlueprintModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BlueprintRepository(BaseRepository[BlueprintModel]):
    """Repository managing blueprints and generation job history."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=BlueprintModel)

    async def get_by_project_id(
        self, project_id: uuid.UUID | str
    ) -> BlueprintModel | None:
        stmt = select(BlueprintModel).where(
            BlueprintModel.project_instance_id == str(project_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_latest_by_project(
        self, project_id: uuid.UUID | str
    ) -> BlueprintModel | None:
        return await self.get_by_project_id(project_id)

    async def create_or_get_blueprint(
        self,
        project_instance_id: uuid.UUID | str,
        student_id: uuid.UUID | str,
    ) -> BlueprintModel:
        existing = await self.get_by_project_id(project_instance_id)
        if existing:
            return existing

        blueprint = BlueprintModel(
            id=str(uuid.uuid4()),
            project_instance_id=str(project_instance_id),
            student_id=str(student_id),
            status=BlueprintStatus.NOT_STARTED.value,
            progress_percent=0,
            qa_status=BlueprintQAStatus.PENDING.value,
            content={},
        )
        self._session.add(blueprint)
        await self._session.flush()
        return blueprint

    async def update_status(
        self,
        blueprint: BlueprintModel,
        status: BlueprintStatus,
        *,
        current_step: str | None = None,
        progress_percent: int | None = None,
        error_message: str | None = None,
        failed_output_key: str | None = None,
    ) -> BlueprintModel:
        blueprint.status = status.value
        if current_step is not None:
            blueprint.current_step = current_step
        if progress_percent is not None:
            blueprint.progress_percent = progress_percent
        if error_message is not None:
            blueprint.error_message = error_message
        if failed_output_key is not None:
            blueprint.failed_output_key = failed_output_key
        blueprint.updated_at = datetime.now(UTC)
        await self._session.flush()
        return blueprint

    async def save_content_section(
        self,
        blueprint: BlueprintModel,
        section_key: str,
        section_data: Any,
        progress_percent: int,
    ) -> BlueprintModel:
        current_content = dict(blueprint.content or {})
        current_content[section_key] = section_data
        blueprint.content = current_content
        blueprint.current_step = section_key
        blueprint.progress_percent = progress_percent
        blueprint.updated_at = datetime.now(UTC)
        await self._session.flush()
        return blueprint

    async def record_qa_result(
        self,
        blueprint: BlueprintModel,
        qa_status: BlueprintQAStatus,
        qa_score: int,
        qa_feedback: dict[str, Any],
    ) -> BlueprintModel:
        blueprint.qa_status = qa_status.value
        blueprint.qa_score = qa_score
        blueprint.qa_feedback = qa_feedback
        if qa_status == BlueprintQAStatus.PASS:
            blueprint.status = BlueprintStatus.READY_FOR_APPROVAL.value
            blueprint.error_message = None
            blueprint.failed_output_key = None
        else:
            blueprint.status = BlueprintStatus.QA_REJECTED.value
        blueprint.updated_at = datetime.now(UTC)
        await self._session.flush()
        return blueprint

    async def approve_blueprint(
        self,
        blueprint: BlueprintModel,
    ) -> BlueprintModel:
        blueprint.status = BlueprintStatus.APPROVED.value
        blueprint.approved_at = datetime.now(UTC)
        blueprint.updated_at = datetime.now(UTC)
        await self._session.flush()
        return blueprint

    async def create_job(
        self,
        blueprint_id: str,
        project_instance_id: str,
        job_type: str,
        target_output: str | None = None,
    ) -> BlueprintJobModel:
        job = BlueprintJobModel(
            id=str(uuid.uuid4()),
            blueprint_id=blueprint_id,
            project_instance_id=project_instance_id,
            job_type=job_type,
            target_output=target_output,
            status=BlueprintJobStatus.RUNNING.value,
            progress_percent=0,
            started_at=datetime.now(UTC),
        )
        self._session.add(job)
        await self._session.flush()
        return job

    async def update_job_progress(
        self,
        job: BlueprintJobModel,
        *,
        current_step: str | None = None,
        progress_percent: int | None = None,
    ) -> BlueprintJobModel:
        """Synchronize persistent job execution progress."""
        if current_step is not None:
            job.current_step = current_step
        if progress_percent is not None:
            job.progress_percent = progress_percent
        job.updated_at = datetime.now(UTC)
        await self._session.flush()
        return job

    async def complete_job(
        self,
        job: BlueprintJobModel,
        status: BlueprintJobStatus,
        error: str | None = None,
    ) -> BlueprintJobModel:
        job.status = status.value
        job.error = error
        if status == BlueprintJobStatus.COMPLETED:
            job.progress_percent = 100
        job.completed_at = datetime.now(UTC)
        job.updated_at = datetime.now(UTC)
        await self._session.flush()
        return job

    async def recover_orphaned_jobs(
        self,
        error_message: str = "Execution interrupted by server restart",
    ) -> int:
        """
        Identify blueprint jobs stranded in RUNNING state according to existing database state,
        transition recoverable orphaned jobs to FAILED, persist the truthful interruption error,
        and transition any associated GENERATING blueprints to FAILED.
        """
        now = datetime.now(UTC)
        stmt = select(BlueprintJobModel).where(
            BlueprintJobModel.status == BlueprintJobStatus.RUNNING.value
        )
        res = await self._session.execute(stmt)
        running_jobs = list(res.scalars().all())

        if not running_jobs:
            return 0

        bp_ids = {job.blueprint_id for job in running_jobs if job.blueprint_id}

        for job in running_jobs:
            job.status = BlueprintJobStatus.FAILED.value
            job.error = error_message
            job.completed_at = now
            job.updated_at = now

        if bp_ids:
            bp_stmt = select(BlueprintModel).where(
                BlueprintModel.id.in_(bp_ids),
                BlueprintModel.status == BlueprintStatus.GENERATING.value,
            )
            bp_res = await self._session.execute(bp_stmt)
            generating_bps = list(bp_res.scalars().all())
            for bp in generating_bps:
                bp.status = BlueprintStatus.FAILED.value
                bp.error_message = error_message
                bp.updated_at = now

        await self._session.flush()
        return len(running_jobs)

    async def list_platform_jobs(
        self,
        *,
        status: str | None = None,
        job_type: str | None = None,
        project_id: uuid.UUID | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[tuple[BlueprintJobModel, str]]:
        """List platform generation jobs with linked project names, filtering, and pagination."""
        stmt = (
            select(BlueprintJobModel, ProjectInstanceModel.name)
            .outerjoin(ProjectInstanceModel, BlueprintJobModel.project_instance_id == ProjectInstanceModel.id)
        )
        if project_id:
            stmt = stmt.where(BlueprintJobModel.project_instance_id == str(project_id))
        if status and status.upper() != "ALL":
            stmt = stmt.where(BlueprintJobModel.status == status.upper())
        if job_type and job_type.upper() != "ALL":
            stmt = stmt.where(BlueprintJobModel.job_type == job_type.upper())
        stmt = stmt.order_by(BlueprintJobModel.created_at.desc()).offset(offset).limit(limit)
        res = await self._session.execute(stmt)
        return [(job, proj_name or "Unknown Project") for job, proj_name in res.all()]

    async def count_platform_jobs(
        self,
        *,
        status: str | None = None,
        job_type: str | None = None,
        project_id: uuid.UUID | str | None = None,
    ) -> int:
        """Count platform generation jobs matching filters."""
        stmt = select(func.count(BlueprintJobModel.id))
        if project_id:
            stmt = stmt.where(BlueprintJobModel.project_instance_id == str(project_id))
        if status and status.upper() != "ALL":
            stmt = stmt.where(BlueprintJobModel.status == status.upper())
        if job_type and job_type.upper() != "ALL":
            stmt = stmt.where(BlueprintJobModel.job_type == job_type.upper())
        res = await self._session.execute(stmt)
        return res.scalar_one() or 0

    async def get_job_counts_by_status(self) -> dict[str, int]:
        """Return count summary grouped by job status."""
        stmt = select(BlueprintJobModel.status, func.count(BlueprintJobModel.id)).group_by(BlueprintJobModel.status)
        res = await self._session.execute(stmt)
        return {status: count for status, count in res.all()}

