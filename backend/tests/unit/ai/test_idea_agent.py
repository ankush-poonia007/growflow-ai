"""
GrowFlow — Unit Tests for Idea Agent.

Verifies:
- Valid fixture execution and typed IdeaAgentOutput synthesis
- Prompt construction includes problem, solution, and recommendations
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.idea import IdeaAgent
from backend.app.domain.ai.contracts.agents import IdeaAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_idea_input, make_idea_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_idea_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_idea_output()
    adapter.register_structured_response("IdeaAgentOutput", expected_output)

    agent = IdeaAgent(gateway=gateway)
    input_data = make_idea_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-idea-1")

    assert isinstance(output, IdeaAgentOutput)
    assert output.refined_title == expected_output.refined_title
    assert len(output.target_users) >= 1
    assert len(output.value_propositions) >= 2

    # Verify provenance
    assert provenance.agent_name == "idea_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.correlation_id == "corr-idea-1"
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert "AgriFlow Telemetry" in prompt
    assert input_data.initial_problem in prompt
    assert input_data.initial_solution in prompt
