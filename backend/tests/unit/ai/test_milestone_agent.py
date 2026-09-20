"""
GrowFlow — Unit Tests for Milestone Agent.

Verifies:
- Valid fixture execution and typed MilestoneAgentOutput synthesis
- Serial dependency: Milestone consumes Task output
- Task ID traceability and gate decision verification
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.milestone import MilestoneAgent
from backend.app.domain.ai.contracts.agents import MilestoneAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import (
    make_milestone_input,
    make_milestone_output,
)


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_milestone_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_milestone_output()
    adapter.register_structured_response("MilestoneAgentOutput", expected_output)

    agent = MilestoneAgent(gateway=gateway)
    input_data = make_milestone_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-mile-1")

    assert isinstance(output, MilestoneAgentOutput)
    assert len(output.milestones) >= 3
    assert all(m.gate_decision is not None for m in output.milestones)

    # Verify provenance
    assert provenance.agent_name == "milestone_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents: contains tasks
    prompt = adapter.last_prompt
    assert "AVAILABLE ENGINEERING TASKS" in prompt
    assert input_data.tasks.tasks[0].task_id in prompt
    assert str(input_data.timeline.estimated_total_weeks) in prompt
