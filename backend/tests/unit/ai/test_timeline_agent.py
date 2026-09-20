"""
GrowFlow — Unit Tests for Timeline Agent.

Verifies:
- Valid fixture execution and typed TimelineAgentOutput synthesis
- Phase duration summation matches estimated_total_weeks
- Frozen dependency: Timeline does NOT consume Risk
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.timeline import TimelineAgent
from backend.app.domain.ai.contracts.agents import TimelineAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_timeline_input, make_timeline_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_timeline_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_timeline_output()
    adapter.register_structured_response("TimelineAgentOutput", expected_output)

    agent = TimelineAgent(gateway=gateway)
    input_data = make_timeline_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-time-1")

    assert isinstance(output, TimelineAgentOutput)
    assert len(output.phases) >= 3
    assert sum(p.duration_weeks for p in output.phases) == output.estimated_total_weeks

    # Verify provenance
    assert provenance.agent_name == "timeline_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents: contains spec, does NOT contain risk
    prompt = adapter.last_prompt
    assert input_data.idea.refined_title in prompt
    assert "TECHNICAL SPECIFICATION SUMMARY" in prompt
    assert "RiskAgentOutput" not in prompt
    assert "R01" not in prompt
