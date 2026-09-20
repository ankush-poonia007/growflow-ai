"""
GrowFlow — Agent Execution Repository.

Persistence layer for per-agent execution provenance records.

Architecture ref:
  6B § 27.2 — agent_executions
  6E § 31   — Execution Provenance Tracking
  6F § 45   — Agent Model & Capability Assignment
  Gate 09 — Unit 4 Orchestration & Durable Execution
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import select

from backend.app.infrastructure.database.models.agent_execution import AgentExecutionModel
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.domain.ai.contracts.base import AgentExecutionProvenance


class AgentExecutionRepository(BaseRepository[AgentExecutionModel]):
    """Repository managing persistence and queries for AgentExecutionModel."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=AgentExecutionModel)

    async def record_execution(
        self,
        provenance: AgentExecutionProvenance,
        *,
        blueprint_job_id: str,
        blueprint_id: str,
        project_instance_id: str,
        error_message: str | None = None,
    ) -> AgentExecutionModel:
        """Persist a typed AgentExecutionProvenance instance into the agent_executions table."""
        record = AgentExecutionModel(
            id=str(uuid.uuid4()),
            blueprint_job_id=str(blueprint_job_id),
            blueprint_id=str(blueprint_id),
            project_instance_id=str(project_instance_id),
            execution_id=str(provenance.execution_id),
            correlation_id=str(provenance.correlation_id),
            agent_name=provenance.agent_name,
            agent_version=provenance.agent_version,
            prompt_version=provenance.prompt_version,
            contract_version=provenance.contract_version,
            generation_number=provenance.generation_number,
            regeneration_attempt=provenance.regeneration_attempt,
            provider=provenance.provider,
            model=provenance.model,
            key_alias=provenance.key_alias,
            capability=provenance.capability.value
            if hasattr(provenance.capability, "value")
            else str(provenance.capability),
            latency_ms=provenance.latency_ms,
            prompt_tokens=provenance.usage.prompt_tokens,
            completion_tokens=provenance.usage.completion_tokens,
            total_tokens=provenance.usage.total_tokens,
            estimated_cost_usd=provenance.usage.estimated_cost_usd or 0.0,
            retry_count=provenance.retry_count,
            status=provenance.status,
            error_message=error_message,
            started_at=provenance.started_at,
            completed_at=provenance.completed_at,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def list_by_job(self, job_id: str | uuid.UUID) -> list[AgentExecutionModel]:
        """List all agent executions associated with a specific blueprint generation job."""
        stmt = (
            select(AgentExecutionModel)
            .where(AgentExecutionModel.blueprint_job_id == str(job_id))
            .order_by(AgentExecutionModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_project(
        self, project_instance_id: str | uuid.UUID
    ) -> list[AgentExecutionModel]:
        """List all agent executions for a project instance, ordered chronologically."""
        stmt = (
            select(AgentExecutionModel)
            .where(AgentExecutionModel.project_instance_id == str(project_instance_id))
            .order_by(AgentExecutionModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_execution_id(self, execution_id: str) -> AgentExecutionModel | None:
        """Find an execution record by its unique execution_id string."""
        stmt = select(AgentExecutionModel).where(AgentExecutionModel.execution_id == execution_id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    # Functional alias
    persist_provenance = record_execution
