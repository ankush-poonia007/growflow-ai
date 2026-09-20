"""
GrowFlow — Unit Tests for Specification Agent.

Verifies:
- Valid fixture execution and typed SpecificationAgentOutput synthesis
- Entities, endpoints, and acceptance criteria constraints
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.specification import SpecificationAgent
from backend.app.domain.ai.contracts.agents import SpecificationAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import (
    make_specification_input,
    make_specification_output,
)


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_specification_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_specification_output()
    adapter.register_structured_response("SpecificationAgentOutput", expected_output)

    agent = SpecificationAgent(gateway=gateway)
    input_data = make_specification_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-spec-1")

    assert isinstance(output, SpecificationAgentOutput)
    assert len(output.entities) >= 2
    assert len(output.api_endpoints) >= 3
    assert len(output.system_acceptance_criteria) >= 2

    # Verify provenance
    assert provenance.agent_name == "specification_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert input_data.idea.refined_title in prompt
    assert input_data.technology.backend.name in prompt
