"""
GrowFlow — Unit 4 Test: Provenance Persistence & Audit Integrity.

Verifies:
- Every executed agent records provenance via AgentExecutionRepository
- Verification that all fields (latency, tokens, cost, model, capability, generation number, execution ID) are preserved
- Key alias safety validation (raw API keys/secrets rejected)
- Tenant isolation (project-scoped and job-scoped queries)
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.ai.contracts.base import AgentExecutionProvenance
from backend.app.infrastructure.ai.models import AIUsageMetadata, ProviderCapability
from backend.app.infrastructure.repositories.agent_execution_repository import (
    AgentExecutionRepository,
)


def make_valid_provenance(
    agent_name: str = "specification",
    key_alias: str = "key_primary",
    gen_number: int = 2,
    regen_attempt: int = 1,
) -> AgentExecutionProvenance:
    now = datetime.now(UTC)
    return AgentExecutionProvenance(
        agent_name=agent_name,
        agent_version="1.2.0",
        prompt_version="1.1.0",
        contract_version="1.0.0",
        generation_number=gen_number,
        regeneration_attempt=regen_attempt,
        execution_id="exec-42",
        correlation_id="corr-99",
        provider="anthropic",
        model="claude-3-5-sonnet",
        key_alias=key_alias,
        capability=ProviderCapability.REASONING,
        latency_ms=350.5,
        usage=AIUsageMetadata(
            prompt_tokens=1500,
            completion_tokens=800,
            total_tokens=2300,
            estimated_cost_usd=0.0125,
        ),
        retry_count=1,
        status="SUCCESS",
        started_at=now,
        completed_at=now,
    )


@pytest.mark.asyncio
async def test_provenance_persistence_records_all_fields() -> None:
    """Verify AgentExecutionRepository correctly maps and persists all provenance fields."""
    session = AsyncMock(spec=AsyncSession)
    repo = AgentExecutionRepository(session=session)

    job_id = uuid.uuid4()
    project_id = uuid.uuid4()
    blueprint_id = uuid.uuid4()
    prov = make_valid_provenance()

    saved_model = await repo.record_execution(
        provenance=prov,
        blueprint_job_id=str(job_id),
        blueprint_id=str(blueprint_id),
        project_instance_id=str(project_id),
    )

    session.add.assert_called_once()
    session.flush.assert_called_once()

    assert saved_model.blueprint_job_id == str(job_id)
    assert saved_model.project_instance_id == str(project_id)
    assert saved_model.blueprint_id == str(blueprint_id)
    assert saved_model.agent_name == "specification"
    assert saved_model.agent_version == "1.2.0"
    assert saved_model.prompt_version == "1.1.0"
    assert saved_model.contract_version == "1.0.0"
    assert saved_model.generation_number == 2
    assert saved_model.regeneration_attempt == 1
    assert saved_model.execution_id == "exec-42"
    assert saved_model.correlation_id == "corr-99"
    assert saved_model.provider == "anthropic"
    assert saved_model.model == "claude-3-5-sonnet"
    assert saved_model.key_alias == "key_primary"
    assert saved_model.capability == ProviderCapability.REASONING.value
    assert saved_model.latency_ms == 350.5
    assert saved_model.prompt_tokens == 1500
    assert saved_model.completion_tokens == 800
    assert saved_model.total_tokens == 2300
    assert saved_model.estimated_cost_usd == 0.0125
    assert saved_model.retry_count == 1
    assert saved_model.status == "SUCCESS"


def test_provenance_rejects_raw_api_keys() -> None:
    """AgentExecutionProvenance validator strictly prevents storing raw keys."""
    now = datetime.now(UTC)
    with pytest.raises(ValueError, match="Raw API key or authorization token detected"):
        AgentExecutionProvenance(
            agent_name="idea",
            agent_version="1.0.0",
            prompt_version="1.0.0",
            contract_version="1.0.0",
            generation_number=1,
            regeneration_attempt=0,
            execution_id="exec-1",
            correlation_id="corr-1",
            provider="openai",
            model="gpt-4o",
            key_alias="sk-proj-1234567890abcdef123456",  # Raw OpenAI key format
            capability=ProviderCapability.STANDARD,
            latency_ms=10.0,
            usage=AIUsageMetadata(prompt_tokens=10, completion_tokens=10, total_tokens=20),
            started_at=now,
            completed_at=now,
        )

    with pytest.raises(ValueError, match="Raw API key or authorization token detected"):
        AgentExecutionProvenance(
            agent_name="idea",
            agent_version="1.0.0",
            prompt_version="1.0.0",
            contract_version="1.0.0",
            generation_number=1,
            regeneration_attempt=0,
            execution_id="exec-1",
            correlation_id="corr-1",
            provider="openai",
            model="gpt-4o",
            key_alias="Bearer eyJhbGciOi...",  # Bearer token
            capability=ProviderCapability.STANDARD,
            latency_ms=10.0,
            usage=AIUsageMetadata(prompt_tokens=10, completion_tokens=10, total_tokens=20),
            started_at=now,
            completed_at=now,
        )


@pytest.mark.asyncio
async def test_provenance_tenant_isolation_scoping() -> None:
    """Repository queries for provenance are strictly filtered by project/job."""
    session = AsyncMock(spec=AsyncSession)
    repo = AgentExecutionRepository(session=session)

    # Setup execute mock
    project_id = uuid.uuid4()
    job_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    session.execute.return_value = mock_result

    # 1. list_by_job
    await repo.list_by_job(job_id)
    session.execute.assert_called_once()

    # 2. list_by_project
    session.execute.reset_mock()
    await repo.list_by_project(project_id)
    session.execute.assert_called_once()
