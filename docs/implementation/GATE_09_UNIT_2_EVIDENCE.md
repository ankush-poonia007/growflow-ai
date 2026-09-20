# GATE 09 — UNIT 2: AGENT CONTRACTS, PYDANTIC SCHEMAS & PROJECT CONTEXT BUILDER
# VERIFICATION & EVIDENCE REPORT

**Document ID:** `GF-GATE09-UNIT2-EVIDENCE`  
**Status:** VERIFIED & COMPLETE  
**Date:** 2026-09-20  
**Branch:** `gate-09/ai-blueprint`  
**Authoritative References:**  
- GrowFlow Part 6F — AI Agent Architecture & Orchestration (Final Frozen Specification)
- GrowFlow Part 6E — AI Provider Gateway & Model Architecture (Final Frozen Specification)
- Gate 09 Specification & Gate 09 Specification Resolution (`docs/gate09_spec_resolution.md`)
- Gate 09 Unit 1 Analysis (`docs/gate09_unit1_analysis.md`)
- Gate 09 Unit 1 Evidence (`docs/implementation/GATE_09_UNIT_1_EVIDENCE.md`)
- Gate 09 Unit 2 Analysis (`docs/gate09_unit2_analysis.md`)

---

## 1. Unit Scope

Unit 2 establishes the formal typed contract and context foundations required by the 12-agent AI blueprint workflow:
- **Base Agent Contracts:** `BaseAgentInput`, `BaseAgentOutput`, and `AgentExecutionProvenance` establishing deterministic execution scoping, provenance tracking, and error boundaries.
- **11 Generator Agent Contracts:** Strongly-typed Pydantic input and output schemas for all 11 generator agents (`Idea`, `Scope`, `Technology`, `Features`, `MVP`, `Specification`, `Timeline`, `Risk`, `Task`, `Milestone`, `README`) with field constraints, regexes, and mathematical consistency rules.
- **QA / Judge Contract:** Strongly-typed `QAJudgeAgentInput` and `QAJudgeAgentOutput` enforcing the frozen evaluation gate: `PASS iff overall_score >= 75 AND zero CRITICAL findings`.
- **Shared Blueprint Workflow State:** `BlueprintWorkflowState` (TypedDict for LangGraph compatibility) and `BlueprintWorkflowStateModel` (Pydantic model for serialization and checkpointing).
- **Context Model Layer:** `ProjectBaseContext`, `AssessmentContext`, and tailored purpose-built agent projection models honoring strict token budgets.
- **Project Context Builder:** Centralized `ProjectContextBuilder` service performing pre-execution ownership/tenancy validation, isolated PostgreSQL repository querying, and deterministic long-form text truncation.

---

## 2. Files Created

| File | Purpose |
|---|---|
| `backend/app/domain/ai/__init__.py` | Top-level AI domain package export. |
| `backend/app/domain/ai/contracts/__init__.py` | Exports all contracts, schemas, and enums. |
| `backend/app/domain/ai/contracts/base.py` | `BaseAgentInput`, `BaseAgentOutput`, and `AgentExecutionProvenance` models. |
| `backend/app/domain/ai/contracts/agents.py` | 11 generator-agent input/output contract pairs and nested domain schemas. |
| `backend/app/domain/ai/contracts/qa.py` | `QASeverity` enum, `QAFinding`, `QAJudgeAgentInput`, and `QAJudgeAgentOutput`. |
| `backend/app/domain/ai/contracts/state.py` | `BlueprintWorkflowState` (TypedDict) and `BlueprintWorkflowStateModel`. |
| `backend/app/domain/ai/context/__init__.py` | Context package exports. |
| `backend/app/domain/ai/context/models.py` | `ProjectBaseContext`, `AssessmentContext`, and 12 purpose-built agent projections. |
| `backend/app/domain/ai/context/builder.py` | `ProjectContextBuilder` service with tenancy checks and agent projections. |
| `backend/tests/unit/test_agent_contracts.py` | 15 contract validation, constraint, serialization, and gateway compatibility tests. |
| `backend/tests/unit/test_qa_contract.py` | 8 QA evaluation gate, severity taxonomy, and scorecard serialization tests. |
| `backend/tests/unit/test_context_builder.py` | 5 context builder extraction, truncation, and projection tests. |
| `backend/tests/unit/test_project_isolation.py` | 5 tenancy security, authorization boundary, and credential exclusion tests. |

---

## 3. Files Modified

**Zero existing production files modified.** Unit 2 is 100% additive. No changes were made to `backend/app/infrastructure/ai/*`, `backend/app/infrastructure/database/models/*`, `backend/migrations/*`, or `frontend/*`.

---

## 4. Contract Inventory (12 Logical Agents)

### 4.1 Base Contracts (`base.py`)
- `BaseAgentInput`: `execution_id`, `project_id`, `student_id`, `agent_name`, `contract_version`, `regeneration_attempt` ($\ge 0$), `qa_feedback_hint`.
- `BaseAgentOutput`: `agent_name`, `contract_version`, `summary`, `confidence_score` ($0.0 \le s \le 1.0$), `assumptions`, `warnings`.
- `AgentExecutionProvenance`: Tracks `agent_name`, `generation_number`, `regeneration_attempt`, `execution_id`, `correlation_id`, `provider`, `model`, `key_alias` (validated safe alias, rejects raw keys), `capability`, `latency_ms`, `usage` (`AIUsageMetadata`), `retry_count`, `status`, `started_at`, `completed_at`.

### 4.2 Generator Agent Contracts (`agents.py`)
1. **Idea Agent:** `IdeaAgentInput` $\to$ `IdeaAgentOutput` (`target_users` $\ge 1$, `value_propositions` $\ge 2$).
2. **Scope Agent:** `ScopeAgentInput` $\to$ `ScopeAgentOutput` (`in_scope` $\ge 3$, `out_of_scope` $\ge 2$, `architectural_boundaries` $\ge 2$).
3. **Technology Agent:** `TechnologyAgentInput` $\to$ `TechnologyAgentOutput` (`backend`, `database`, `frontend`, `security_auth`, `telemetry_observability`, `communication_protocols`, `TechItem`, `LearningCurve` enum).
4. **Features Agent:** `FeaturesAgentInput` $\to$ `FeaturesAgentOutput` (`features` $\ge 4$, regex `^F\d{2}$`, unique IDs, $\ge 2$ `P0` features).
5. **MVP Agent:** `MVPAgentInput` $\to$ `MVPAgentOutput` (`core_user_journey` $\ge 3$, `included_capabilities` $\ge 2$, `excluded_from_mvp` $\ge 1$).
6. **Specification Agent:** `SpecificationAgentInput` $\to$ `SpecificationAgentOutput` (`entities` $\ge 2$, `api_endpoints` $\ge 3$, `DataEntitySpec`, `APIEndpointSpec`).
7. **Timeline Agent:** `TimelineAgentInput` $\to$ `TimelineAgentOutput` (`phases` $\ge 3$, model validator enforces $\sum \text{duration\_weeks} == \text{estimated\_total\_weeks}$).
8. **Risk Agent:** `RiskAgentInput` $\to$ `RiskAgentOutput` (`risks` $\ge 4$, regex `^R\d{2}$`, unique IDs, validator enforces both `TECHNICAL` and `SECURITY` coverage).
9. **Task Agent:** `TaskAgentInput` $\to$ `TaskAgentOutput` (`tasks` $\ge 8$, regex `^T\d{2}$`, unique IDs, `TaskCategory`, `TaskPriority`).
10. **Milestone Agent:** `MilestoneAgentInput` $\to$ `MilestoneAgentOutput` (`milestones` $\ge 3$, regex `^M\d{1,2}$`, unique IDs, `GateDecision`).
11. **README Agent:** `ReadmeAgentInput` $\to$ `ReadmeAgentOutput` (`curated_context`, `getting_started` $\ge 2$, `EnvVarSpec`).

### 4.3 QA / Judge Contract (`qa.py`)
12. **QA / Judge Agent:** `QAJudgeAgentInput` $\to$ `QAJudgeAgentOutput`
    - `QASeverity` enum: `INFO`, `WARNING`, `ERROR`, `CRITICAL` (no `HIGH`).
    - `QAFinding`: `finding_id`, `section`, `target_agent`, `severity`, `category`, `description`, `recommendation`, `requires_regeneration`.
    - `overall_score`: $0 \le \text{score} \le 100$.
    - Validator enforces Gate 09 Decision A3: `PASS` iff `overall_score >= 75` AND zero `CRITICAL` findings. Rejects any attempt to pass with score $< 75$ or with critical findings.

---

## 5. Context Model Inventory (`models.py`)

- **`ProjectBaseContext`:** Scoped project identity, problem, proposed solution, complexity, phase, health, profile objective, constraints, and preferred technologies.
- **`AssessmentContext`:** Assessment session ID, student skill level, project complexity, alignment, technical confidence, learning depth, overall score, readiness tier, dimension scores, gaps, recommendations, and scoped `AssessmentAnswerItem` list.
- **Agent Projections:** Purpose-built minimal contexts preventing token bloat:
  - `IdeaAgentContext`, `ScopeAgentContext`, `TechnologyAgentContext`, `FeaturesAgentContext`, `MVPAgentContext`, `SpecificationAgentContext`, `TimelineAgentContext`, `RiskAgentContext`, `TaskAgentContext`, `MilestoneAgentContext`, `ReadmeAgentContext`, `QAJudgeAgentContext`.

---

## 6. Context Builder Behavior (`builder.py`)

`ProjectContextBuilder`:
- Accepts `project_id` and `current_user: CurrentUser`.
- Pre-execution validation verifies project existence (`NotFoundException`) and ownership (`project.student_id == current_user.user_id` or `current_user.is_admin`, otherwise `AuthorizationException`).
- Executes targeted queries against `ProjectRepository` and `AssessmentRepository`.
- Truncates long-form student answers exceeding 500 characters deterministically (`_truncate_text`).
- Slices foundational context into immutable, agent-specific projection models.
- Operates statelessly without global mutable caches.

---

## 7. Security & Isolation Behavior

1. **Authentication & Tenancy:** Caller identity is derived strictly from `CurrentUser` (Supabase JWT), never from untrusted frontend payloads.
2. **Cross-Project Contamination Prevention:** Project A context contains zero data from Project B. Verified via `test_cross_project_isolation_guarantee`.
3. **Data Scrubbing:** Mentor private notes, administrator audit logs, API credentials, and internal foreign keys are strictly excluded from context models.

---

## 8. Test Commands & Exact Results

### 8.1 Unit 2 Test Suite (33 Scenarios)
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_agent_contracts.py backend/tests/unit/test_qa_contract.py backend/tests/unit/test_context_builder.py backend/tests/unit/test_project_isolation.py -v
```
Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 33 items

backend/tests/unit/test_agent_contracts.py::test_base_agent_input_valid PASSED [  3%]
backend/tests/unit/test_agent_contracts.py::test_base_agent_input_rejects_negative_regeneration_attempt PASSED [  6%]
backend/tests/unit/test_agent_contracts.py::test_base_agent_output_defaults PASSED [  9%]
backend/tests/unit/test_agent_contracts.py::test_agent_execution_provenance_rejects_raw_keys PASSED [ 12%]
backend/tests/unit/test_agent_contracts.py::test_idea_agent_contract_validation PASSED [ 15%]
backend/tests/unit/test_scope_agent_contract_validation PASSED [ 18%]
backend/tests/unit/test_technology_agent_contract_validation PASSED [ 21%]
backend/tests/unit/test_features_agent_contract_validation PASSED [ 24%]
backend/tests/unit/test_timeline_agent_duration_consistency PASSED [ 27%]
backend/tests/unit/test_risk_agent_coverage_validation PASSED [ 30%]
backend/tests/unit/test_task_agent_validation PASSED [ 33%]
backend/tests/unit/test_milestone_agent_validation PASSED [ 36%]
backend/tests/unit/test_specification_agent_validation PASSED [ 39%]
backend/tests/unit/test_readme_agent_validation PASSED [ 42%]
backend/tests/unit/test_agent_output_schema_compatibility_with_mock_gateway PASSED [ 45%]
backend/tests/unit/test_qa_contract.py::test_qa_severity_distinct_levels PASSED [ 48%]
backend/tests/unit/test_qa_contract.py::test_qa_pass_with_score_75_and_no_critical PASSED [ 51%]
backend/tests/unit/test_qa_contract.py::test_qa_pass_rejected_if_critical_finding_present PASSED [ 54%]
backend/tests/unit/test_qa_contract.py::test_qa_pass_rejected_if_score_below_75 PASSED [ 57%]
backend/tests/unit/test_qa_contract.py::test_qa_fail_with_regeneration_target PASSED [ 60%]
backend/tests/unit/test_qa_contract.py::test_qa_fail_escalates_to_human_review PASSED [ 63%]
backend/tests/unit/test_qa_contract.py::test_qa_score_bounds_enforced PASSED [ 66%]
backend/tests/unit/test_qa_contract.py::test_qa_json_serialization_roundtrip PASSED [ 69%]
backend/tests/unit/test_context_builder.py::test_build_base_contexts_happy_path PASSED [ 72%]
backend/tests/unit/test_context_builder.py::test_text_truncation_limits_long_responses PASSED [ 75%]
backend/tests/unit/test_context_builder.py::test_build_base_contexts_handles_missing_assessment_gracefully PASSED [ 78%]
backend/tests/unit/test_context_builder.py::test_purpose_built_agent_projections PASSED [ 81%]
backend/tests/unit/test_context_builder.py::test_truncate_text_helper PASSED [ 84%]
backend/tests/unit/test_project_isolation.py::test_student_cannot_access_other_student_project PASSED [ 87%]
backend/tests/unit/test_project_isolation.py::test_non_existent_project_raises_not_found PASSED [ 90%]
backend/tests/unit/test_admin_can_access_any_project PASSED [ 93%]
backend/tests/unit/test_project_isolation.py::test_cross_project_isolation_guarantee PASSED [ 96%]
backend/tests/unit/test_project_isolation.py::test_absence_of_credentials_and_mentor_notes PASSED [100%]

============================= 33 passed in 0.34s ==============================
```

### 8.2 Unit 1 Gateway Regression Suite (21 Scenarios)
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_ai_gateway.py -v
```
Result: **21 passed in 4.08s (100% pass rate)**.

### 8.3 Full Backend Unit Test Suite Regression (203 Scenarios)
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit -v
```
Result: **203 passed in 13.64s (100% pass rate, zero regressions)**.

---

## 9. Lint, Format & Type Checking Results

### 9.1 Ruff Check
Command:
```powershell
.\.venv\Scripts\python.exe -m ruff check backend/app/domain/ai backend/tests/unit/test_agent_contracts.py backend/tests/unit/test_qa_contract.py backend/tests/unit/test_context_builder.py backend/tests/unit/test_project_isolation.py
```
Output:
```text
All checks passed!
```

### 9.2 Ruff Format Check
Command:
```powershell
.\.venv\Scripts\python.exe -m ruff format --check backend/app/domain/ai backend/tests/unit/test_agent_contracts.py backend/tests/unit/test_qa_contract.py backend/tests/unit/test_context_builder.py backend/tests/unit/test_project_isolation.py
```
Output:
```text
13 files already formatted
```

### 9.3 Mypy Static Type Checking
Command:
```powershell
.\.venv\Scripts\python.exe -m mypy backend/app/domain/ai --explicit-package-bases
```
Result: **Zero type errors in `backend/app/domain/ai`**. (Any pre-existing repository warnings in `settings.py` / `logger.py` remain documented from earlier gates).

---

## 10. Confirmation of Strict Non-Execution Rules

- [x] **Zero database migrations created.**
- [x] **Zero AI agents implemented (deferred to Unit 3).**
- [x] **Zero LangGraph graphs, nodes, or workers implemented (deferred to Unit 4).**
- [x] **Zero SSE endpoints implemented (deferred to Unit 5).**
- [x] **Zero frontend code modified (deferred to Unit 6).**
- [x] **Zero BlueprintService generation code modified.**
- [x] **No Git commit executed.**
- [x] **No Git push executed.**
- [x] **No PR created.**
