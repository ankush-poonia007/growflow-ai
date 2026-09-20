"""
GrowFlow — Unit Tests for QA / Judge Agent.

Verifies:
- Valid fixture execution producing PASS verdict (score >= 75, 0 CRITICAL findings)
- Failure execution producing FAIL verdict with targeted regeneration_target
- Model validator enforcement of Gate 09 Decision A3 pass rule
- REASONING capability assignment (frozen architectural invariant)
- Comprehensive evaluation prompt construction
- Provenance mapping
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.qa import QAJudgeAgent
from backend.app.domain.ai.contracts.qa import (
    QAFinding,
    QAJudgeAgentOutput,
    QASeverity,
)
from backend.app.domain.blueprint.models import BlueprintQAStatus
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import ProviderCapability
from backend.tests.unit.ai.fixtures import (
    make_qa_judge_input,
    make_qa_judge_output_fail,
    make_qa_judge_output_pass,
)


@pytest.fixture
def mock_gateway() -> tuple[AIProviderGateway, MockAIProviderAdapter]:
    adapter = MockAIProviderAdapter()
    gateway = AIProviderGateway(adapter=adapter)
    return gateway, adapter


@pytest.mark.asyncio
async def test_qa_judge_agent_execution_pass(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_qa_judge_output_pass()
    adapter.register_structured_response("QAJudgeAgentOutput", expected_output)

    agent = QAJudgeAgent(gateway=gateway)
    input_data = make_qa_judge_input()

    output, provenance = await agent.execute(input_data=input_data, correlation_id="corr-qa-pass")

    assert isinstance(output, QAJudgeAgentOutput)
    assert output.status == BlueprintQAStatus.PASS
    assert output.overall_score >= 75
    assert not any(f.severity == QASeverity.CRITICAL for f in output.findings)

    # Verify frozen architectural invariant: QA uses REASONING
    assert provenance.agent_name == "qa_judge_agent"
    assert provenance.capability == ProviderCapability.REASONING
    assert provenance.status == "SUCCESS"

    # Verify prompt contents: contains project context, EPU, and upstream sections
    prompt = adapter.last_prompt
    assert input_data.project_context.name in prompt
    assert input_data.assessment_context.skill_level in prompt
    assert "AgriFlow Autonomous Telemetry System" in prompt


@pytest.mark.asyncio
async def test_qa_judge_agent_execution_fail_with_regeneration_target(
    mock_gateway: tuple[AIProviderGateway, MockAIProviderAdapter],
):
    gateway, adapter = mock_gateway
    expected_output = make_qa_judge_output_fail()
    adapter.register_structured_response("QAJudgeAgentOutput", expected_output)

    agent = QAJudgeAgent(gateway=gateway)
    input_data = make_qa_judge_input()

    output, _provenance = await agent.execute(input_data=input_data, correlation_id="corr-qa-fail")

    assert isinstance(output, QAJudgeAgentOutput)
    assert output.status == BlueprintQAStatus.FAIL
    assert output.overall_score < 75 or any(
        f.severity == QASeverity.CRITICAL for f in output.findings
    )
    assert output.regeneration_target == "features_agent"


def test_qa_judge_output_contract_enforces_gate_09_pass_rule():
    """Verify Gate 09 Decision A3 invariant: PASS requires score >= 75 AND zero CRITICAL."""
    # 1. Critical finding prevents PASS
    with pytest.raises(ValueError, match="QA status cannot be PASS when CRITICAL findings exist"):
        QAJudgeAgentOutput(
            agent_name="qa_judge_agent",
            summary="Invalid pass with critical finding",
            status=BlueprintQAStatus.PASS,
            overall_score=85,
            findings=[
                QAFinding(
                    finding_id="QA-F01",
                    section="scope",
                    target_agent="scope_agent",
                    severity=QASeverity.CRITICAL,
                    category="CONTRADICTION",
                    description="Fatal contradiction.",
                    recommendation="Fix it.",
                )
            ],
        )

    # 2. Score < 75 prevents PASS
    with pytest.raises(ValueError, match=r"overall_score .* is below 75"):
        QAJudgeAgentOutput(
            agent_name="qa_judge_agent",
            summary="Invalid pass with low score",
            status=BlueprintQAStatus.PASS,
            overall_score=74,
            findings=[],
        )
