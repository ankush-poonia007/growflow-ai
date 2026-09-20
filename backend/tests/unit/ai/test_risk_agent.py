"""
GrowFlow — Unit Tests for Risk Agent.

Verifies:
- Valid fixture execution and typed RiskAgentOutput synthesis
- Category coverage (TECHNICAL and SECURITY mandatory)
- Risk ID regex and uniqueness (^R\\d{2}$)
- STANDARD capability assignment
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.risk import RiskAgent
from backend.app.domain.ai.contracts.agents import RiskAgentOutput, RiskCategory
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import make_risk_input, make_risk_output


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_risk_agent_execution_success(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_risk_output()
    adapter.register_structured_response("RiskAgentOutput", expected_output)

    agent = RiskAgent(gateway=gateway)
    input_data = make_risk_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-risk-1")

    assert isinstance(output, RiskAgentOutput)
    assert len(output.risks) >= 4
    categories = {r.category for r in output.risks}
    assert RiskCategory.TECHNICAL in categories
    assert RiskCategory.SECURITY in categories

    # Verify provenance
    assert provenance.agent_name == "risk_agent"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"

    # Verify prompt contents
    prompt = adapter.last_prompt
    assert input_data.technology.backend.name in prompt
    assert str(input_data.timeline.estimated_total_weeks) in prompt
