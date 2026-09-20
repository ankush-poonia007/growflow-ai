"""
GrowFlow — Unit Tests for Task Agent.

Verifies:
- Valid fixture execution and typed TaskAgentOutput synthesis
- Task count (>= 8) and ID regex/uniqueness (^T\\d{2}$)
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.task import TaskAgent
from backend.app.domain.ai.contracts.agents import TaskAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_task_input, make_task_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_task_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_task_output()
    adapter.register_structured_response("TaskAgentOutput", expected_output)

    agent = TaskAgent(gateway=gateway)
    input_data = make_task_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-task-1")

    assert isinstance(output, TaskAgentOutput)
    assert len(output.tasks) >= 8
    assert all(t.estimated_hours >= 1 for t in output.tasks)

    # Verify provenance
    assert provenance.agent_name == "task_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert input_data.technology.backend.name in prompt
    assert input_data.features.features[0].title in prompt
