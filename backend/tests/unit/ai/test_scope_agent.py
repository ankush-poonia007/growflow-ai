"""
GrowFlow — Unit Tests for Scope Agent.

Verifies:
- Valid fixture execution and typed ScopeAgentOutput synthesis
- Prompt construction includes Idea output and assessment gaps
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.scope import ScopeAgent
from backend.app.domain.ai.contracts.agents import ScopeAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_scope_input, make_scope_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_scope_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_scope_output()
    adapter.register_structured_response("ScopeAgentOutput", expected_output)

    agent = ScopeAgent(gateway=gateway)
    input_data = make_scope_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-scope-1")

    assert isinstance(output, ScopeAgentOutput)
    assert len(output.in_scope) >= 3
    assert len(output.out_of_scope) >= 2
    assert len(output.architectural_boundaries) >= 2

    # Verify provenance
    assert provenance.agent_name == "scope_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert input_data.idea.refined_title in prompt
    assert "Limited distributed systems experience" in prompt
