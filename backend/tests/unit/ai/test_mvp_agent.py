"""
GrowFlow — Unit Tests for MVP Agent.

Verifies:
- Valid fixture execution and typed MVPAgentOutput synthesis
- REASONING capability assignment (frozen architectural invariant)
- Core user journey and validation criteria constraints
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.mvp import MVPAgent
from backend.app.domain.ai.contracts.agents import MVPAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_mvp_input, make_mvp_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_mvp_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_mvp_output()
    adapter.register_structured_response("MVPAgentOutput", expected_output)

    agent = MVPAgent(gateway=gateway)
    input_data = make_mvp_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-mvp-1")

    assert isinstance(output, MVPAgentOutput)
    assert len(output.core_user_journey) >= 3
    assert len(output.included_capabilities) >= 2
    assert len(output.validation_criteria) >= 2

    # Verify frozen architectural invariant: MVP uses REASONING
    assert provenance.agent_name == "mvp_agent"
    assert provenance.capability == ProviderCapability.REASONING
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert input_data.idea.refined_title in prompt
    assert "Stage-1 MVP" in prompt
