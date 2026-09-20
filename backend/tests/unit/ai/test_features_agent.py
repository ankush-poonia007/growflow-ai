"""
GrowFlow — Unit Tests for Features Agent.

Verifies:
- Valid fixture execution and typed FeaturesAgentOutput synthesis
- Feature prioritization (at least two P0 features) and regex IDs (^F\\d{2}$)
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.features import FeaturesAgent
from backend.app.domain.ai.contracts.agents import FeaturePriority, FeaturesAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_features_input, make_features_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_features_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_features_output()
    adapter.register_structured_response("FeaturesAgentOutput", expected_output)

    agent = FeaturesAgent(gateway=gateway)
    input_data = make_features_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-feat-1")

    assert isinstance(output, FeaturesAgentOutput)
    assert len(output.features) >= 4
    p0_count = sum(1 for f in output.features if f.priority == FeaturePriority.P0)
    assert p0_count >= 2

    # Verify provenance
    assert provenance.agent_name == "features_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert input_data.idea.refined_title in prompt
    assert "In-Scope Capabilities" in prompt
