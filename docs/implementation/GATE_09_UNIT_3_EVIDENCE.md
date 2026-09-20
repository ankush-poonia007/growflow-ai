# Gate 09 Unit 3 Evidence

# GATE 09 — UNIT 3: 12 AI AGENTS & TOOL BINDINGS
# VERIFICATION & EVIDENCE REPORT

**Document ID:** `GF-GATE09-UNIT3-EVIDENCE`  
**Status:** VERIFIED & COMPLETE  
**Date:** 2026-09-20  
**Branch:** `gate-09/ai-blueprint`  
**Authoritative References:**  
- GrowFlow Part 6F — AI Agent Architecture & Orchestration (Final Frozen Specification)
- GrowFlow Part 6E — AI Provider Gateway & Model Architecture (Final Frozen Specification)
- GrowFlow Part 6G — RAG Knowledge & Document Intelligence Architecture (Final Frozen Specification)
- Gate 09 Specification & Gate 09 Specification Resolution (`docs/gate09_spec_resolution.md`)
- Gate 09 Unit 1 Analysis (`docs/gate09_unit1_analysis.md`) & Evidence (`docs/implementation/GATE_09_UNIT_1_EVIDENCE.md`)
- Gate 09 Unit 2 Analysis (`docs/gate09_unit2_analysis.md`) & Evidence (`docs/implementation/GATE_09_UNIT_2_EVIDENCE.md`)
- Gate 09 Unit 3 Analysis (`docs/gate09_unit3_analysis.md`)

---

## 1. Scope Implemented

Unit 3 implements the concrete execution components for all 12 AI agents of the GrowFlow AI Blueprint generation pipeline:
- **Base Agent Abstraction (`BaseAgent[TInput, TOutput]`):** Generic async base class coordinating typed input parsing, prompt construction, targeted QA regeneration feedback injection, gateway structured synthesis via `AIProviderGateway.execute_structured(...)`, execution timing, and `AgentExecutionProvenance` mapping.
- **Shared System Prompt:** Centralized architectural role prompt enforcing structured JSON compliance, prompt-injection defenses, project tenancy boundaries, and credential safety.
- **12 Agent Prompt Modules:** Deterministic system and user prompt builders with explicit versioning (`PROMPT_VERSION = "1.0.0"`), typed input consumption, and domain constraints.
- **12 Concrete AI Agent Implementations:**
  - 10 standard capability agents: `IdeaAgent`, `ScopeAgent`, `TechnologyAgent`, `FeaturesAgent`, `SpecificationAgent`, `TimelineAgent`, `RiskAgent`, `TaskAgent`, `MilestoneAgent`, `ReadmeAgent`.
  - 2 reasoning capability agents: `MVPAgent` and `QAJudgeAgent`.
- **Test Fixtures & Offline Mock Infrastructure:** Pydantic v2 compliant factories in `backend/tests/unit/ai/fixtures.py` satisfying all contract minimums, constraints, and regex patterns.
- **Unit 3 Test Suite:** 17 comprehensive unit tests across 13 test modules validating BaseAgent lifecycle, targeted QA feedback injection, schema validation error bubbling, and individual agent execution against the mock provider.

---

## 2. Files Created

### Production Files (28 files)
| File Path | Description |
|---|---|
| `backend/app/domain/ai/agents/__init__.py` | Exports all 12 agent classes and `BaseAgent`. |
| `backend/app/domain/ai/agents/base.py` | Generic `BaseAgent[TInput, TOutput]` execution coordinator. |
| `backend/app/domain/ai/agents/idea.py` | `IdeaAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/scope.py` | `ScopeAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/technology.py` | `TechnologyAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/features.py` | `FeaturesAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/mvp.py` | `MVPAgent` implementation (REASONING capability). |
| `backend/app/domain/ai/agents/specification.py` | `SpecificationAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/timeline.py` | `TimelineAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/risk.py` | `RiskAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/task.py` | `TaskAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/milestone.py` | `MilestoneAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/readme.py` | `ReadmeAgent` implementation (STANDARD capability). |
| `backend/app/domain/ai/agents/qa.py` | `QAJudgeAgent` implementation (REASONING capability). |
| `backend/app/domain/ai/prompts/__init__.py` | Exports all prompt builder functions and constants. |
| `backend/app/domain/ai/prompts/system.py` | `SHARED_SYSTEM_PROMPT` definition. |
| `backend/app/domain/ai/prompts/idea.py` | Idea agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/scope.py` | Scope agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/technology.py` | Technology agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/features.py` | Features agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/mvp.py` | MVP agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/specification.py` | Specification agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/timeline.py` | Timeline agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/risk.py` | Risk agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/task.py` | Task agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/milestone.py` | Milestone agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/readme.py` | README agent prompt builder (`PROMPT_VERSION = "1.0.0"`). |
| `backend/app/domain/ai/prompts/qa.py` | QA / Judge prompt builder (`PROMPT_VERSION = "1.0.0"`). |

### Test Files (15 files)
| File Path | Description |
|---|---|
| `backend/tests/unit/ai/__init__.py` | Package marker for AI agent tests. |
| `backend/tests/unit/ai/fixtures.py` | Compliant Pydantic v2 input and output test factories for all 12 agents. |
| `backend/tests/unit/ai/test_agent_base.py` | Lifecycle, QA regeneration feedback, and validation error bubbling tests for `BaseAgent`. |
| `backend/tests/unit/ai/test_idea_agent.py` | `IdeaAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_scope_agent.py` | `ScopeAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_technology_agent.py` | `TechnologyAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_features_agent.py` | `FeaturesAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_mvp_agent.py` | `MVPAgent` execution test against mock gateway (REASONING capability). |
| `backend/tests/unit/ai/test_specification_agent.py` | `SpecificationAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_timeline_agent.py` | `TimelineAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_risk_agent.py` | `RiskAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_task_agent.py` | `TaskAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_milestone_agent.py` | `MilestoneAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_readme_agent.py` | `ReadmeAgent` execution test against mock gateway. |
| `backend/tests/unit/ai/test_qa_judge_agent.py` | `QAJudgeAgent` execution test, pass/fail rules, and regeneration targets. |

---

## 3. Files Modified

| File Path | Description |
|---|---|
| `backend/app/domain/ai/__init__.py` | Updated exports to include `agents` and `prompts` packages. |

**Zero existing production files outside the Unit 3 boundary were modified.**  
No modifications to:
- `backend/app/infrastructure/ai/*`
- `backend/app/domain/ai/contracts/*`
- `backend/app/domain/ai/context/*`
- `backend/app/application/services/blueprint_service.py`
- `backend/app/infrastructure/database/*`
- `backend/app/api/*`
- Frontend application code

---

## 4. Agent Inventory

| Agent Name | Agent Class | Capability | Input Contract | Output Contract | Versions | Key Invariants & Dependencies |
|---|---|---|---|---|---|---|
| **Idea** | `IdeaAgent` | `STANDARD` | `IdeaAgentInput` | `IdeaAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Slices project & assessment context into refined vision, target users, value props. |
| **Scope** | `ScopeAgent` | `STANDARD` | `ScopeAgentInput` | `ScopeAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Idea; establishes strict in-scope/out-of-scope boundaries. |
| **Technology** | `TechnologyAgent` | `STANDARD` | `TechnologyAgentInput` | `TechnologyAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Idea & Scope; produces backend, database, frontend, auth, protocol stack. |
| **Features** | `FeaturesAgent` | `STANDARD` | `FeaturesAgentInput` | `FeaturesAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Idea & Scope; outputs $\ge 4$ features (`^F\d{2}$`), $\ge 2$ P0 priorities. |
| **MVP** | `MVPAgent` | `REASONING` | `MVPAgentInput` | `MVPAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Evaluates architectural tradeoffs for walking skeleton; core user journey $\ge 3$. |
| **Specification** | `SpecificationAgent` | `STANDARD` | `SpecificationAgentInput` | `SpecificationAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Tech + Features + MVP; defines entities $\ge 2$, API endpoints $\ge 3$. |
| **Timeline** | `TimelineAgent` | `STANDARD` | `TimelineAgentInput` | `TimelineAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Spec; enforces $\sum \text{duration\_weeks} == \text{estimated\_total\_weeks}$. Strictly before Risk. |
| **Risk** | `RiskAgent` | `STANDARD` | `RiskAgentInput` | `RiskAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Timeline & Spec; outputs $\ge 4$ risks (`^R\d{2}$`) with TECHNICAL & SECURITY coverage. Strictly after Timeline. |
| **Task** | `TaskAgent` | `STANDARD` | `TaskAgentInput` | `TaskAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Spec, Tech, Features, Timeline, Risk; outputs $\ge 8$ actionable engineering tasks (`^T\d{2}$`). Strictly before Milestone. |
| **Milestone** | `MilestoneAgent` | `STANDARD` | `MilestoneAgentInput` | `MilestoneAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes Timeline & Tasks; groups valid task IDs into milestone stages $\ge 3$. Strictly serial after Task. |
| **Readme** | `ReadmeAgent` | `STANDARD` | `ReadmeAgentInput` | `ReadmeAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Consumes curated structured context; getting started steps $\ge 2$. Zero secret generation. |
| **QA / Judge** | `QAJudgeAgent` | `REASONING` | `QAJudgeAgentInput` | `QAJudgeAgentOutput` | Agent: `1.0.0`<br>Prompt: `1.0.0` | Evaluates full blueprint; enforces Gate 09 A3 rule: `PASS` iff `overall_score >= 75` and 0 `CRITICAL` findings. |

---

## 5. Gateway Integration

All LLM calls execute through `AIProviderGateway.execute_structured(...)`.

1. **Encapsulation:** Agents have no knowledge of OpenRouter, API keys, HTTP clients, rate limits, timeouts, or cooldowns.
2. **Execution Flow:**
   ```
   Typed Agent Input
          ↓
   BaseAgent.build_prompts(input_data)
          ↓
   AIProviderGateway.execute_structured(
       system_prompt=system_prompt,
       user_prompt=user_prompt,
       output_schema=self.output_schema,
       capability=self.capability,
       correlation_id=input_data.execution_id,
   )
          ↓
   AIExecutionResult (typed Pydantic model + execution metadata)
          ↓
   BaseAgent._build_provenance(execution_result, input_data, started_at, completed_at)
          ↓
   tuple[TOutput, AgentExecutionProvenance]
   ```
3. **Capability Propagation:**
   - `MVPAgent` explicitly requests `ProviderCapability.REASONING`.
   - `QAJudgeAgent` explicitly requests `ProviderCapability.REASONING`.
   - All other 10 agents request `ProviderCapability.STANDARD`.

---

## 6. Prompt Architecture

1. **System Prompt Layer (`backend/app/domain/ai/prompts/system.py`):**
   - Establishes the GrowFlow architectural intelligence role.
   - Demands strict adherence to JSON schema without conversational filler.
   - Inoculates against prompt injection by declaring student input as unprivileged data.
   - Forbids cross-project data leakage and credential generation.
2. **Domain Prompt Modules (`backend/app/domain/ai/prompts/*.py`):**
   - Each module defines `PROMPT_VERSION = "1.0.0"`.
   - `build_system_prompt(...)` combines `SHARED_SYSTEM_PROMPT` with agent-specific domain directives.
   - `build_user_prompt(input_data)` formats typed Pydantic input deterministically into markdown sections.
3. **Targeted QA Feedback Injection (`BaseAgent`):**
   - When `input_data.qa_feedback_hint` is populated, `BaseAgent` appends a delimited feedback section:
     ```markdown
     ## TARGETED REVISION DIRECTIVE (Regeneration Attempt {attempt})
     The previous output for this stage received specific QA feedback requiring correction:
     {qa_feedback_hint}

     Please resolve this issue while maintaining consistency with all upstream inputs and constraints.
     ```
   - Normal prompt structure is fully preserved.

---

## 7. Structured Output Validation

- The gateway parses model responses with Pydantic v2 `model_validate_json(raw_text)`.
- If the model output violates schema types, regexes, or custom validators (e.g., Timeline duration sum or QA Pass gate), the gateway raises `AIStructuredOutputException`.
- `BaseAgent` lets `AIStructuredOutputException` bubble cleanly to callers, verified by `test_base_agent_bubbles_schema_validation_error`.
- In Unit 4, the LangGraph orchestrator will catch this exception and trigger retry/regeneration policies.

---

## 8. Provenance

For every successful execution, `BaseAgent` constructs an immutable `AgentExecutionProvenance` record using verified metadata returned by the Unit 1 gateway:
- `agent_name`: Name of the executing agent (e.g., `"IdeaAgent"`).
- `agent_version`: `"1.0.0"`.
- `prompt_version`: `"1.0.0"`.
- `contract_version`: Propagated from input (`"1.0.0"`).
- `generation_number`: Propagated from orchestration input (or `1` default).
- `regeneration_attempt`: Propagated from orchestration input (`0` initial).
- `execution_id`: Unique execution UUID from input.
- `correlation_id`: Correlation UUID propagated through the gateway.
- `provider`: Resolved provider name from gateway execution (e.g., `"openrouter"` or `"mock"`).
- `model`: Resolved model identifier (e.g., `"anthropic/claude-3.5-sonnet"` or `"mock-model"`).
- `key_alias`: Sanitized key alias from `APIKeyPoolManager` (e.g., `"key_1"`), strictly rejecting raw API keys.
- `capability`: Explicit capability used (`STANDARD` or `REASONING`).
- `latency_ms`: Measured wall-clock execution duration.
- `usage`: `AIUsageMetadata` containing prompt, completion, total tokens, and cost.
- `retry_count`: Transient retry count from gateway execution.
- `status`: `"COMPLETED"`.
- `started_at` / `completed_at`: UTC timestamps.

Zero execution records are persisted to PostgreSQL in Unit 3; persistence is owned by Unit 4.

---

## 9. Security / Isolation

1. **Zero Database Direct Access:** Agents never import SQLAlchemy `Session`, database models, or repositories.
2. **Context Integrity:** Agents accept only pre-sliced, authorized typed context from Unit 2.
3. **Credential Exclusion:**
   - Agents never read environment files (`.env`), file system secrets, or database credentials.
   - Prompts explicitly instruct agents to output placeholders (e.g., `"your-secret-key-here"`) in README configuration sections.
   - Provenance validator explicitly rejects any string that resembles a raw API key.
4. **Prompt Injection Defense:** Student answers are explicitly enclosed in structured data blocks and treated as unprivileged data.

---

## 10. RAG / Tavily Boundary

- **RAG Architecture:** Strictly **DEFERRED**. No vector databases, embeddings, index builders, or retrieval tools are present or imported.
- **Tavily Live Integration:** Strictly **DEFERRED**. No live web requests or search tools are called. `MVPAgentInput.research_evidence` accepts typed fixtures or an empty list (`[]`) without fabricating external network calls.

---

## 11. Test Results

Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/ai/ -v
```

Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- D:\PROJECTS\Infosys SpringBoot\growflow_ai\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\PROJECTS\Infosys SpringBoot\growflow_ai
configfile: pyproject.toml
plugins: anyio-4.15.1, langsmith-0.12.4, asyncio-1.4.0, cov-7.1.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 17 items

backend/tests/unit/ai/test_agent_base.py::test_base_agent_execution_lifecycle PASSED [  5%]
backend/tests/unit/ai/test_agent_base.py::test_base_agent_targeted_regeneration_injection PASSED [ 11%]
backend/tests/unit/ai/test_agent_base.py::test_base_agent_bubbles_schema_validation_error PASSED [ 17%]
backend/tests/unit/ai/test_features_agent.py::test_features_agent_execution_success PASSED [ 23%]
backend/tests/unit/ai/test_idea_agent.py::test_idea_agent_execution_success PASSED [ 29%]
backend/tests/unit/ai/test_milestone_agent.py::test_milestone_agent_execution_success PASSED [ 35%]
backend/tests/unit/ai/test_mvp_agent.py::test_mvp_agent_execution_success PASSED [ 41%]
backend/tests/unit/ai/test_qa_judge_agent.py::test_qa_judge_agent_execution_pass PASSED [ 47%]
backend/tests/unit/ai/test_qa_judge_agent.py::test_qa_judge_agent_execution_fail_with_regeneration_target PASSED [ 52%]
backend/tests/unit/ai/test_qa_judge_agent.py::test_qa_judge_output_contract_enforces_gate_09_pass_rule PASSED [ 58%]
backend/tests/unit/ai/test_readme_agent.py::test_readme_agent_execution_success PASSED [ 64%]
backend/tests/unit/ai/test_risk_agent.py::test_risk_agent_execution_success PASSED [ 70%]
backend/tests/unit/ai/test_scope_agent.py::test_scope_agent_execution_success PASSED [ 76%]
backend/tests/unit/ai/test_specification_agent.py::test_specification_agent_execution_success PASSED [ 82%]
backend/tests/unit/ai/test_task_agent.py::test_task_agent_execution_success PASSED [ 88%]
backend/tests/unit/ai/test_technology_agent.py::test_technology_agent_execution_success PASSED [ 94%]
backend/tests/unit/ai/test_timeline_agent.py::test_timeline_agent_execution_success PASSED [100%]

============================= 17 passed in 3.24s ==============================
```

---

## 12. Regression Results

### 12.1 Gate 09 Complete Suite (Unit 1 + Unit 2 + Unit 3)
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_ai_gateway.py backend/tests/unit/test_agent_contracts.py backend/tests/unit/test_qa_contract.py backend/tests/unit/test_context_builder.py backend/tests/unit/test_project_isolation.py backend/tests/unit/ai/ -v
```
Result: **71 passed in 8.55s (100% pass rate, zero regressions)**.

### 12.2 Full Backend Unit Test Suite
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/ -q
```
Result: **220 passed in 17.74s (100% pass rate, zero regressions across entire project)**.

---

## 13. Lint / Formatting / Type Checking

### 13.1 Ruff Check
Command:
```powershell
.\.venv\Scripts\python.exe -m ruff check backend/app/domain/ai/ backend/tests/unit/ai/
```
Output:
```text
All checks passed!
```

### 13.2 Ruff Format Check
Command:
```powershell
.\.venv\Scripts\python.exe -m ruff format --check backend/app/domain/ai/ backend/tests/unit/ai/
```
Output:
```text
52 files already formatted
```

### 13.3 Mypy Static Type Checking
Command:
```powershell
.\.venv\Scripts\python.exe -m mypy backend/app/domain/ai/ --explicit-package-bases
```
Output:
```text
Found 0 errors in backend/app/domain/ai/
```
*(Note: 5 pre-existing repository warnings in `settings.py`, `logger.py`, and `outbox_repository.py` remain documented from earlier gates).*

---

## 14. Known Limitations

1. **No Autonomous Workflow Orchestration:** Unit 3 agents are stateless functional execution components. Sequencing, parallel dispatch, and checkpointing will be implemented in Unit 4 via LangGraph.
2. **No Persistent Execution Records:** Provenance is assembled in memory and returned as a typed object; persistence into the `agent_executions` table will be implemented in Unit 4.
3. **No SSE Streaming:** Real-time event streaming of agent progression will be implemented in Unit 5.
4. **Deferred RAG & Tavily Integration:** RAG knowledge retrieval and Tavily live web research remain deferred to future iterations per project roadmap.

---

## 15. Unit 4 Handoff

The Unit 3 agents are immediately ready for integration as LangGraph nodes in Unit 4:
- Every agent can be invoked via `output, provenance = await agent.execute(input_data)`.
- Input and output types match `BlueprintWorkflowState` fields exactly.
- Parallel execution of `TechnologyAgent`, `FeaturesAgent`, and `MVPAgent` is directly achievable using `asyncio.gather` or LangGraph parallel fan-out branches.
- Serial dependencies (`Specification` $\to$ `Timeline` $\to$ `Risk` $\to$ `Task` $\to$ `Milestone` $\to$ `README` $\to$ `QAJudge`) map 1:1 to StateGraph transitions.
- QA evaluation provides clean `requires_regeneration` and `target_agent` pointers that Unit 4 will route back to upstream nodes (up to 2 automatic regeneration loops).

---

## 16. Final Verdict

# VERDICT: PASS

Unit 3 implementation strictly satisfies all frozen architectural specifications (Part 6E, Part 6F, Gate 09 Resolutions), achieves 100% test pass rate across 71 Gate 09 tests and 220 full backend tests, passes all linting and type checks, and preserves all isolation and security boundaries.
