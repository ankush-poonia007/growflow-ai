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

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy import func, select, update

from backend.app.domain.blueprint.models import (
    BlueprintJobStatus,
    BlueprintQAStatus,
    BlueprintStatus,
)
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

    async def get_by_project_id(self, project_id: uuid.UUID | str) -> BlueprintModel | None:
        stmt = select(BlueprintModel).where(BlueprintModel.project_instance_id == str(project_id))
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_project_id_for_update(
        self, project_id: uuid.UUID | str
    ) -> BlueprintModel | None:
        """Retrieve blueprint with row-level lock (FOR UPDATE) for concurrent protection."""
        stmt = (
            select(BlueprintModel)
            .where(BlueprintModel.project_instance_id == str(project_id))
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_latest_by_project(self, project_id: uuid.UUID | str) -> BlueprintModel | None:
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

    async def increment_generation_number(self, blueprint_id: uuid.UUID | str) -> int:
        """Atomically increment the generation_number for a blueprint using database-level lock/returning."""
        stmt = (
            update(BlueprintModel)
            .where(BlueprintModel.id == str(blueprint_id))
            .values(
                generation_number=BlueprintModel.generation_number + 1,
                updated_at=datetime.now(UTC),
            )
            .returning(BlueprintModel.generation_number)
        )
        res = await self._session.execute(stmt)
        val = res.scalar_one_or_none()
        await self._session.flush()
        return val if val is not None else 1

    async def create_job(
        self,
        blueprint_id: str,
        project_instance_id: str,
        job_type: str,
        target_output: str | None = None,
        generation_number: int = 1,
    ) -> BlueprintJobModel:
        job = BlueprintJobModel(
            id=str(uuid.uuid4()),
            blueprint_id=blueprint_id,
            project_instance_id=project_instance_id,
            job_type=job_type,
            target_output=target_output,
            generation_number=generation_number,
            cancellation_requested=False,
            status=BlueprintJobStatus.RUNNING.value,
            progress_percent=0,
            started_at=datetime.now(UTC),
        )
        self._session.add(job)
        await self._session.flush()
        return job

    async def get_job_by_id(self, job_id: uuid.UUID | str) -> BlueprintJobModel | None:
        """Retrieve a persistent blueprint job by its ID."""
        stmt = select(BlueprintJobModel).where(BlueprintJobModel.id == str(job_id))
        res = await self._session.execute(stmt)
        return res.scalars().first()

    async def request_cancellation(self, job_id: uuid.UUID | str) -> BlueprintJobModel | None:
        """Mark a job as CANCELLING with cancellation_requested=True idempotently."""
        job = await self.get_job_by_id(job_id)
        if not job:
            return None
        terminal_statuses = [
            BlueprintJobStatus.COMPLETED.value,
            BlueprintJobStatus.FAILED.value,
            "CANCELLED",
        ]
        if job.status in terminal_statuses:
            return job  # Idempotent no-op

        job.cancellation_requested = True
        job.status = "CANCELLING"
        job.updated_at = datetime.now(UTC)
        await self._session.flush()
        return job

    async def is_cancellation_requested(self, job_id: uuid.UUID | str) -> bool:
        """Lightweight database check whether cancellation was requested for a job."""
        stmt = select(BlueprintJobModel.cancellation_requested, BlueprintJobModel.status).where(
            BlueprintJobModel.id == str(job_id)
        )
        res = await self._session.execute(stmt)
        row = res.first()
        if not row:
            return False
        cancel_req, status_val = row
        return bool(cancel_req or status_val in ["CANCELLING", "CANCELLED"])

    async def claim_job_lease(
        self,
        job_id: uuid.UUID | str,
        worker_id: str,
        lease_timeout_seconds: int = 300,
    ) -> bool:
        """Attempt to atomically acquire a worker lock lease on a job to prevent duplicate execution."""
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=lease_timeout_seconds)
        stmt = (
            update(BlueprintJobModel)
            .where(
                BlueprintJobModel.id == str(job_id),
                BlueprintJobModel.status.in_(
                    [
                        BlueprintJobStatus.PENDING.value,
                        BlueprintJobStatus.RUNNING.value,
                    ]
                ),
                (
                    (BlueprintJobModel.locked_by.is_(None))
                    | (BlueprintJobModel.locked_at < cutoff)
                    | (BlueprintJobModel.locked_by == worker_id)
                ),
            )
            .values(
                locked_by=worker_id,
                locked_at=now,
                status=BlueprintJobStatus.RUNNING.value,
                updated_at=now,
            )
        )
        res = await self._session.execute(stmt)
        await self._session.flush()
        return (getattr(res, "rowcount", 0) or 0) > 0

    async def get_active_job(self, blueprint_id: uuid.UUID | str) -> BlueprintJobModel | None:
        """Find the most recent active or cancelling generation job for a blueprint."""
        stmt = (
            select(BlueprintJobModel)
            .where(
                BlueprintJobModel.blueprint_id == str(blueprint_id),
                BlueprintJobModel.status.in_(
                    [
                        BlueprintJobStatus.PENDING.value,
                        BlueprintJobStatus.RUNNING.value,
                        "CANCELLING",
                    ]
                ),
            )
            .order_by(BlueprintJobModel.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return res.scalars().first()

    async def commit_canonical_blueprint(
        self,
        *,
        blueprint_id: uuid.UUID | str,
        job_id: uuid.UUID | str,
        content: dict[str, Any],
        qa_score: int,
        qa_feedback: dict[str, Any],
        qa_status: str = BlueprintQAStatus.PASS.value,
        target_status: str = BlueprintStatus.READY_FOR_APPROVAL.value,
        expected_generation_number: int | None = None,
    ) -> bool:
        """
        Atomically commit validated generated content to canonical blueprints.content
        ONLY if the job remains active, has not been cancelled, and matches expected generation.
        """
        job = await self.get_job_by_id(job_id)
        if not job or job.cancellation_requested or job.status != BlueprintJobStatus.RUNNING.value:
            return False

        blueprint = await self.get_by_id(blueprint_id)
        if not blueprint or blueprint.status != BlueprintStatus.GENERATING.value:
            return False

        if (
            expected_generation_number is not None
            and blueprint.generation_number != expected_generation_number
        ):
            return False

        blueprint.content = content
        blueprint.status = target_status
        blueprint.qa_status = qa_status
        blueprint.qa_score = qa_score
        blueprint.qa_feedback = qa_feedback
        blueprint.current_step = "qa_judge"
        blueprint.progress_percent = 100
        blueprint.updated_at = datetime.now(UTC)

        job.status = BlueprintJobStatus.COMPLETED.value
        job.progress_percent = 100
        job.completed_at = datetime.now(UTC)
        job.updated_at = datetime.now(UTC)

        await self._session.flush()
        return True

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
        Identify blueprint jobs stranded in RUNNING or CANCELLING state,
        transition recoverable orphaned jobs to FAILED/CANCELLED, persist truthful errors,
        and transition associated GENERATING blueprints to FAILED without altering previous canonical content.
        """
        now = datetime.now(UTC)
        stmt = select(BlueprintJobModel).where(
            BlueprintJobModel.status.in_(
                [
                    BlueprintJobStatus.RUNNING.value,
                    BlueprintJobStatus.PENDING.value,
                    "CANCELLING",
                ]
            )
        )
        res = await self._session.execute(stmt)
        orphaned_jobs = list(res.scalars().all())

        if not orphaned_jobs:
            return 0

        bp_ids: set[str] = set()

        for job in orphaned_jobs:
            if job.status == "CANCELLING" or job.cancellation_requested:
                job.status = "CANCELLED"
                job.error = "Cancellation confirmed during server restart recovery"
            else:
                job.status = BlueprintJobStatus.FAILED.value
                job.error = error_message

            job.completed_at = now
            job.updated_at = now
            if job.blueprint_id:
                bp_ids.add(job.blueprint_id)

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
        return len(orphaned_jobs)

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
        stmt = select(BlueprintJobModel, ProjectInstanceModel.name).outerjoin(
            ProjectInstanceModel, BlueprintJobModel.project_instance_id == ProjectInstanceModel.id
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
        stmt = select(BlueprintJobModel.status, func.count(BlueprintJobModel.id)).group_by(
            BlueprintJobModel.status
        )
        res = await self._session.execute(stmt)
        return {str(status): int(count) for status, count in res.all()}
