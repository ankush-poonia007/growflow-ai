"""
GrowFlow — Unit Tests for README Agent.

Verifies:
- Valid fixture execution and typed ReadmeAgentOutput synthesis
- Curated context consumption across all upstream decisions
- Getting started steps (>= 2) and safe environment variable specs
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.readme import ReadmeAgent
from backend.app.domain.ai.contracts.agents import ReadmeAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_readme_input, make_readme_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_readme_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_readme_output()
    adapter.register_structured_response("ReadmeAgentOutput", expected_output)

    agent = ReadmeAgent(gateway=gateway)
    input_data = make_readme_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-readme-1")

    assert isinstance(output, ReadmeAgentOutput)
    assert len(output.getting_started) >= 2
    assert "Backend" in output.tech_stack_summary
    assert len(output.environment_variables) >= 1

    # Verify provenance
    assert provenance.agent_name == "readme_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents: contains curated context
    prompt = adapter.last_prompt
    assert input_data.curated_context.idea.refined_title in prompt
    assert input_data.curated_context.technology.backend.name in prompt
    assert input_data.curated_context.mvp.mvp_name in prompt
