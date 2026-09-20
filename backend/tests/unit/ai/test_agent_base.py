"""
GrowFlow — Unit Tests for BaseAgent Abstraction.

Verifies:
- Standard execution lifecycle (prompt construction, gateway call, timing)
- Provenance construction and metadata mapping
- Targeted QA regeneration feedback injection
- Correlation ID propagation
- Schema validation error bubbling
- Capability and version propagation
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import IdeaAgentInput, IdeaAgentOutput
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import (
    AISchemaValidationException,
    ProviderCapability,
)
from backend.tests.unit.ai.fixtures import make_idea_input, make_idea_output


class ConcreteTestAgent(BaseAgent[IdeaAgentInput, IdeaAgentOutput]):
    """Concrete test agent inheriting from BaseAgent for lifecycle verification."""

    @property
    def agent_name(self) -> str:
        return "test_concrete_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[IdeaAgentOutput]:
        return IdeaAgentOutput

    @property
    def agent_version(self) -> str:
        return "1.2.0"

    @property
    def prompt_version(self) -> str:
        return "1.1.0"

    def build_system_prompt(self, input_data: IdeaAgentInput) -> str:
        return f"System prompt for {input_data.project_name}"

    def build_user_prompt(self, input_data: IdeaAgentInput) -> str:
        return f"User prompt for {input_data.project_name}: {input_data.initial_problem}"


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_base_agent_execution_lifecycle(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_idea_output()
    adapter.register_structured_response("IdeaAgentOutput", expected_output)

    agent = ConcreteTestAgent(gateway=gateway)
    input_data = make_idea_input()

    output, provenance = await agent.execute(
        input_data=input_data,
        correlation_id="corr-test-123",
        generation_number=2,
    )

    # 1. Verify returned typed output
    assert isinstance(output, IdeaAgentOutput)
    assert output.refined_title == expected_output.refined_title
    assert output.confidence_score == expected_output.confidence_score

    # 2. Verify provenance
    assert provenance.agent_name == "test_concrete_agent"
    assert provenance.agent_version == "1.2.0"
    assert provenance.prompt_version == "1.1.0"
    assert provenance.contract_version == input_data.contract_version
    assert provenance.generation_number == 2
    assert provenance.regeneration_attempt == 0
    assert provenance.execution_id == input_data.execution_id
    assert provenance.correlation_id == "corr-test-123"
    assert provenance.capability == ProviderCapability.STANDARD
    assert provenance.status == "SUCCESS"
    assert provenance.key_alias.startswith("key_")
    assert provenance.latency_ms > 0
    assert provenance.started_at <= provenance.completed_at

    # 3. Verify adapter invocation
    assert adapter.call_count == 1
    assert (
        adapter.last_prompt
        == "User prompt for AgriFlow Telemetry: Farmers cannot track field moisture quickly across large farms."
    )


@pytest.mark.asyncio
async def test_base_agent_targeted_regeneration_injection(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    adapter.register_structured_response("IdeaAgentOutput", make_idea_output())

    agent = ConcreteTestAgent(gateway=gateway)
    base_input = make_idea_input()

    # Create regeneration input with QA feedback
    regen_input = base_input.model_copy(
        update={
            "regeneration_attempt": 1,
            "qa_feedback_hint": "Clarify the target audience and value propositions for smallholder farms.",
        }
    )

    _output, provenance = await agent.execute(input_data=regen_input)

    assert provenance.regeneration_attempt == 1
    assert "TARGETED REGENERATION GUIDANCE (Attempt 1)" in adapter.last_prompt
    assert "Clarify the target audience and value propositions" in adapter.last_prompt


@pytest.mark.asyncio
async def test_base_agent_bubbles_schema_validation_error(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    adapter.simulate_malformed_json(times=1)

    agent = ConcreteTestAgent(gateway=gateway)
    input_data = make_idea_input()

    with pytest.raises(AISchemaValidationException):
        await agent.execute(input_data=input_data)
