"""
GrowFlow — Unit Tests for Technology Agent.

Verifies:
- Valid fixture execution and typed TechnologyAgentOutput synthesis
- Prompt construction includes student skill tier and preferred technologies
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.technology import TechnologyAgent
from backend.app.domain.ai.contracts.agents import TechnologyAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import (
    make_technology_input,
    make_technology_output,
)


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_technology_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_technology_output()
    adapter.register_structured_response("TechnologyAgentOutput", expected_output)

    agent = TechnologyAgent(gateway=gateway)
    input_data = make_technology_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-tech-1")

    assert isinstance(output, TechnologyAgentOutput)
    assert output.backend.name == "FastAPI"
    assert output.database.name == "PostgreSQL"
    assert len(output.communication_protocols) >= 1

    # Verify provenance
    assert provenance.agent_name == "technology_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert "FastAPI" in prompt
    assert "PostgreSQL" in prompt
    assert input_data.student_skill_level in prompt
