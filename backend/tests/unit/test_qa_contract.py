"""
GrowFlow — Unit Tests for QA / Judge Agent Contract & Evaluation Gate.

Verifies:
- PASS condition: score >= 75 AND zero CRITICAL findings.
- FAIL condition when score >= 75 but has CRITICAL finding.
- FAIL condition when score < 75 regardless of findings.
- Severity levels (INFO, WARNING, ERROR, CRITICAL) are distinct.
- Representation of regeneration targets and human review escalation.
- Score bounds enforcement (0 to 100).
- Full JSON serialization and deserialization roundtrip.
"""

from pydantic import ValidationError
import pytest

from backend.app.domain.ai.contracts.qa import (
    QAFinding,
    QAJudgeAgentOutput,
    QASeverity,
)
from backend.app.domain.blueprint.models import BlueprintQAStatus


def test_qa_severity_distinct_levels():
    """Verify that the four QA severity levels are distinct and DO NOT include HIGH."""
    assert QASeverity.INFO == "INFO"
    assert QASeverity.WARNING == "WARNING"
    assert QASeverity.ERROR == "ERROR"
    assert QASeverity.CRITICAL == "CRITICAL"

    # Rejects 'HIGH' as an invalid severity for QA
    with pytest.raises(ValueError):
        QASeverity("HIGH")


def test_qa_pass_with_score_75_and_no_critical():
    """Verify score >= 75 with zero CRITICAL findings represents a valid PASS."""
    qa_out = QAJudgeAgentOutput(
        agent_name="QAJudgeAgent",
        summary="All sections coherent and complete.",
        status=BlueprintQAStatus.PASS,
        overall_score=75,
        evaluated_criteria={"completeness": 80, "consistency": 75},
        findings=[
            QAFinding(
                finding_id="QA-01",
                section="features",
                target_agent="FeaturesAgent",
                severity=QASeverity.INFO,
                category="STYLE",
                description="Minor phrasing recommendation",
                recommendation="Enhance feature user stories",
            ),
            QAFinding(
                finding_id="QA-02",
                section="risks",
                target_agent="RiskAgent",
                severity=QASeverity.WARNING,
                category="OPERATIONAL",
                description="Consider cloud cost overrun",
                recommendation="Add budget limits",
            ),
        ],
        recommendations=["Proceed to approval"],
    )
    assert qa_out.status == BlueprintQAStatus.PASS
    assert qa_out.overall_score == 75


def test_qa_pass_rejected_if_critical_finding_present():
    """Verify score >= 75 with one or more CRITICAL findings CANNOT be marked PASS."""
    with pytest.raises(ValidationError, match="cannot be PASS when CRITICAL findings exist"):
        QAJudgeAgentOutput(
            agent_name="QAJudgeAgent",
            summary="Attempted pass with critical flaw.",
            status=BlueprintQAStatus.PASS,
            overall_score=85,
            findings=[
                QAFinding(
                    finding_id="QA-C1",
                    section="tech_stack",
                    target_agent="TechnologyAgent",
                    severity=QASeverity.CRITICAL,
                    category="TECH_INCONSISTENCY",
                    description="Fatal technology incompatibility detected",
                    recommendation="Change database driver",
                    requires_regeneration=True,
                )
            ],
        )


def test_qa_pass_rejected_if_score_below_75():
    """Verify score < 75 CANNOT be marked PASS even if there are zero findings."""
    with pytest.raises(ValidationError, match="below 75"):
        QAJudgeAgentOutput(
            agent_name="QAJudgeAgent",
            summary="Attempted pass with low score.",
            status=BlueprintQAStatus.PASS,
            overall_score=74,
            findings=[],
        )


def test_qa_fail_with_regeneration_target():
    """Verify FAIL scorecard correctly captures failing agent and targeted regeneration."""
    qa_fail = QAJudgeAgentOutput(
        agent_name="QAJudgeAgent",
        summary="Timeline does not match task estimates.",
        status=BlueprintQAStatus.FAIL,
        overall_score=68,
        findings=[
            QAFinding(
                finding_id="QA-E1",
                section="duration",
                target_agent="TimelineAgent",
                severity=QASeverity.ERROR,
                category="TIMELINE_INCONSISTENCY",
                description="Task hours exceed allocated sprint weeks",
                recommendation="Expand timeline duration to 14 weeks",
                requires_regeneration=True,
            )
        ],
        recommendations=["Regenerate timeline to reflect 14 weeks"],
        regeneration_target="TimelineAgent",
        requires_human_review=False,
    )
    assert qa_fail.status == BlueprintQAStatus.FAIL
    assert qa_fail.overall_score == 68
    assert qa_fail.regeneration_target == "TimelineAgent"
    assert not qa_fail.requires_human_review


def test_qa_fail_escalates_to_human_review():
    """Verify FAIL scorecard can flag requires_human_review when regeneration limit reached."""
    qa_review = QAJudgeAgentOutput(
        agent_name="QAJudgeAgent",
        summary="Repeated failure after max regeneration attempts.",
        status=BlueprintQAStatus.FAIL,
        overall_score=60,
        findings=[
            QAFinding(
                finding_id="QA-C2",
                section="scope",
                target_agent="ScopeAgent",
                severity=QASeverity.CRITICAL,
                category="SCOPE_VIOLATION",
                description="Unresolvable domain contradiction",
                recommendation="Requires human mentor intervention",
                requires_regeneration=False,
            )
        ],
        recommendations=["Mentor review needed"],
        regeneration_target=None,
        requires_human_review=True,
    )
    assert qa_review.status == BlueprintQAStatus.FAIL
    assert qa_review.requires_human_review is True


def test_qa_score_bounds_enforced():
    """Verify overall_score enforces 0 <= score <= 100."""
    with pytest.raises(ValidationError):
        QAJudgeAgentOutput(
            agent_name="QAJudgeAgent",
            summary="Negative score",
            status=BlueprintQAStatus.FAIL,
            overall_score=-1,
        )

    with pytest.raises(ValidationError):
        QAJudgeAgentOutput(
            agent_name="QAJudgeAgent",
            summary="Score over 100",
            status=BlueprintQAStatus.FAIL,
            overall_score=101,
        )


def test_qa_json_serialization_roundtrip():
    """Verify QAJudgeAgentOutput serializes to and deserializes from JSON perfectly."""
    qa_out = QAJudgeAgentOutput(
        agent_name="QAJudgeAgent",
        summary="Passed evaluation.",
        status=BlueprintQAStatus.PASS,
        overall_score=92,
        evaluated_criteria={"feasibility": 95, "coherence": 90},
        findings=[],
        recommendations=["Ready for development"],
    )
    json_data = qa_out.model_dump_json()
    assert '"overall_score":92' in json_data or '"overall_score": 92' in json_data
    restored = QAJudgeAgentOutput.model_validate_json(json_data)
    assert restored.overall_score == 92
    assert restored.status == BlueprintQAStatus.PASS
