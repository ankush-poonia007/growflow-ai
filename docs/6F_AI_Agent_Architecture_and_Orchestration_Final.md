# GrowFlow — Part 6F
# AI Agent Architecture & Orchestration — Final Specification

**Status:** FROZEN  
**Part:** 6F  
**System:** GrowFlow  
**Scope:** 12-agent architecture, LangGraph orchestration, agent state, dependency graph, parallelism, context construction, agent contracts, tools, QA/Judge, regeneration, project-change workflows, assessment adaptation, execution persistence, failure recovery, authorization, observability, and implementation boundaries.

---

# 1. Purpose

Part 6F defines how GrowFlow's AI agents are structured, orchestrated, executed, validated, observed, and recovered.

Part 6E established the AI infrastructure boundary:

- LangGraph for orchestration;
- LangChain for AI building blocks;
- LlamaIndex for RAG;
- LangSmith for AI observability/evaluation;
- Tavily for current web research;
- AI Provider Gateway for provider communication;
- five-key provider pool;
- model policy;
- retries;
- quota handling;
- streaming;
- Pydantic contracts;
- deterministic persistence.

Part 6F defines what happens **above that infrastructure**.

The central rule is:

> **Agents perform specialized reasoning. LangGraph orchestrates them. Deterministic application/domain services remain authoritative for GrowFlow state.**

---

# 2. Final Agent Architecture

GrowFlow has exactly 12 logical AI agents:

1. Idea Agent
2. Scope Agent
3. Technology Agent
4. Features Agent
5. Specification Agent
6. MVP Agent
7. Timeline/Duration Agent
8. Risk Agent
9. Task Agent
10. Milestone Agent
11. README Agent
12. QA/Judge Agent

Each agent has one primary responsibility.

No agent becomes a general-purpose "do everything" agent.

---

# 3. Agent Responsibility Principle

Each agent follows:

```text
Input Contract
      ↓
Relevant Context
      ↓
Agent Reasoning
      ↓
Structured Output Contract
      ↓
Pydantic Validation
```

An agent does not:

- directly write business tables;
- directly modify project state;
- bypass authorization;
- choose arbitrary provider keys;
- bypass the AI Provider Gateway;
- orchestrate unrelated agents;
- perform unrestricted SQL;
- retrieve unrestricted project/global data.

---

# 4. Agent Responsibilities

## 4.1 Idea Agent

Responsible for understanding and refining the project's core idea.

Inputs may include:

- original project idea;
- problem statement;
- proposed solution;
- project type;
- student goals;
- assessment context;
- relevant research.

Outputs may include:

- refined idea;
- objective;
- target users;
- project purpose;
- problem interpretation;
- initial value proposition;
- assumptions.

The Idea Agent does not independently finalize scope or implementation tasks.

---

## 4.2 Scope Agent

Responsible for defining project boundaries.

Outputs may include:

- in-scope areas;
- out-of-scope areas;
- project boundaries;
- assumptions;
- constraints;
- expected outcome;
- scope risks.

Idea and Scope may be partially combined in the documentation-generation flow, but their responsibilities remain logically distinct.

---

## 4.3 Technology Agent

Responsible for technology-stack recommendations.

It considers:

- project requirements;
- complexity;
- student skill;
- learning goals;
- scope;
- features;
- architecture requirements;
- current technology availability where appropriate.

For each technology, output should explain:

- what it is;
- why it is selected;
- why it is appropriate;
- student's expected understanding;
- where it will be used.

---

## 4.4 Features Agent

Responsible for identifying project features.

Features are classified:

```text
MUST
SHOULD
GOOD_TO_HAVE
OUT_OF_SCOPE
```

Outputs include feature:

- title;
- description;
- priority;
- expected behavior;
- dependencies where known;
- scope relationship.

---

## 4.5 Specification Agent

Responsible for turning features into implementation-oriented specifications.

It considers:

- feature behavior;
- dependencies;
- technical requirements;
- acceptance criteria;
- constraints;
- project architecture.

It must remain consistent with the approved scope.

---

## 4.6 MVP Agent

Responsible for determining the practical MVP.

It considers:

- project objective;
- scope;
- features;
- technical feasibility;
- duration;
- student skill;
- current existing solutions;
- current APIs/platform capabilities where relevant.

For current web research it may use:

```text
MVP Agent
   ↓
Tavily Tool
   ↓
Current Web Research
```

Research evidence is not treated as absolute authority.

---

## 4.7 Timeline/Duration Agent

Responsible for project duration and timeline planning.

It considers:

- complexity;
- student skill;
- scope;
- technologies;
- features;
- dependencies;
- available duration;
- milestones;
- implementation effort.

Outputs include:

- project start/end;
- phases;
- dates;
- objectives;
- outcomes;
- dependencies;
- duration;
- milestone targets.

Timeline and Milestone remain separate logical responsibilities.

---

## 4.8 Risk Agent

Responsible for project risk analysis.

It considers risks including:

- implementation;
- technology;
- APIs;
- third-party services;
- authentication;
- database;
- AI;
- integrations;
- deployment;
- hosting;
- cost;
- time;
- scope creep;
- learning;
- security;
- performance;
- dependencies;
- GitHub;
- unexpected complexity.

Each risk may include:

- probability;
- impact;
- severity;
- reason;
- warning signs;
- prevention;
- mitigation;
- recommended action.

---

## 4.9 Task Agent

Responsible for transforming validated project planning into actionable tasks.

Tasks should contain:

- title;
- description;
- priority;
- ordering;
- dependencies where applicable;
- expected milestone relationship;
- due date where appropriate.

Task Agent does not directly create database tasks.

---

## 4.10 Milestone Agent

Responsible for grouping/planning meaningful project milestones.

It considers:

- tasks;
- timeline;
- project phases;
- dependencies;
- project outcomes.

It produces milestone structures that can be validated against the timeline and task plan.

Milestone Agent does not directly mark milestones complete.

---

## 4.11 README Agent

Responsible for producing the concise project README.

It receives curated validated project information rather than the entire raw project database.

Inputs may include:

- project profile;
- objective;
- scope;
- technology;
- features;
- MVP;
- timeline;
- important implementation information.

Output is a structured README representation suitable for deterministic Markdown rendering.

---

## 4.12 QA/Judge Agent

QA/Judge is responsible for evaluating generated outputs and determining whether they are suitable for persistence.

It checks:

- schema correctness;
- completeness;
- contradictions;
- project-context consistency;
- scope consistency;
- technology consistency;
- timeline consistency;
- task dependencies;
- milestone consistency;
- risk coverage;
- README consistency;
- unsupported claims;
- required-field omissions.

QA/Judge can recommend targeted regeneration.

It does not directly modify project state.

---

# 5. Agent Input/Output Contract

Every agent has a typed contract.

Conceptually:

```text
AgentRequest
├── execution_id
├── project_id
├── user_context
├── agent_type
├── contract_version
├── relevant_context
└── task_input

AgentResponse
├── agent_type
├── contract_version
├── status
├── structured_output
├── warnings
└── metadata
```

The exact Pydantic models are implementation details.

The contract principle is architectural.

---

# 6. One Agent, One Primary Role

Agents should not become overlapping autonomous personalities.

For example:

```text
Technology Agent
    = Technology

Risk Agent
    = Risk

Task Agent
    = Tasks
```

If another agent needs technology information, it consumes the validated Technology Agent output.

It does not independently recreate the entire technology analysis unless the orchestration workflow explicitly requires it.

---

# 7. LangGraph Responsibility

LangGraph is the orchestration engine.

It controls:

- graph state;
- nodes;
- transitions;
- dependencies;
- conditional execution;
- parallel execution;
- synchronization;
- QA routing;
- regeneration;
- workflow completion/failure.

LangGraph does not own:

- PostgreSQL business state;
- authorization;
- provider API keys;
- provider retry policy;
- core project mutation.

---

# 8. Canonical Blueprint Graph

The conceptual blueprint graph is:

```text
                Project + Assessment
                       │
                       ▼
                  Idea Agent
                       │
                       ▼
                  Scope Agent
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
     Technology     Features        MVP
       Agent         Agent         Agent
          │            │             │
          └────────────┼─────────────┘
                       ▼
              Specification Agent
                       │
                       ▼
             Timeline/Duration Agent
                       │
                       ▼
                  Risk Agent
                       │
                       ▼
                   Task Agent
                       │
                       ▼
                Milestone Agent
                       │
                       ▼
                 README Agent
                       │
                       ▼
                  QA/Judge
                       │
              ┌────────┴────────┐
              ▼                 ▼
            PASS              FAIL
              │                 │
              ▼                 ▼
       Deterministic       Targeted
        Persistence       Regeneration
                                │
                                └──→ QA
```

This is the logical graph. Exact parallelization can be optimized while preserving dependencies.

---

# 9. Dependency Principle

An agent may execute as soon as all of its required inputs are available and validated.

It does not have to wait for unrelated agents.

Example:

```text
Scope
  ↓
Technology
  ↓
Specification
```

But:

```text
Scope
  ↓
Features
```

can execute independently of Technology if its required context is available.

This allows controlled parallelism.

---

# 10. Parallel Agent Execution

Independent agents may run concurrently.

For example:

```text
                 Scope
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
  Technology    Features      MVP
       │           │           │
       └───────────┼───────────┘
                   ▼
             Specification
```

The orchestrator synchronizes them before dependent agents execute.

Parallelism must never sacrifice dependency correctness.

---

# 11. Dependency Graph as Data

The graph should be represented in code/configuration rather than scattered across agent implementations.

Conceptually:

```text
AgentNode
├── agent_type
├── required_inputs
├── dependencies
├── output_contract
├── execution_policy
└── retry/regeneration policy
```

This allows the graph to remain understandable and testable.

---

# 12. LangGraph State

The workflow maintains a typed execution state.

Conceptually:

```text
BlueprintGraphState
├── execution_id
├── project_id
├── user_id
├── correlation_id
├── workflow_status
├── project_context
├── assessment_context
├── agent_outputs
├── validation_results
├── qa_results
├── regeneration_state
├── errors
└── metadata
```

The state is workflow state, not the canonical project database.

---

# 13. State vs Database

Critical distinction:

```text
LangGraph State
    = temporary/workflow execution state

PostgreSQL
    = authoritative GrowFlow state
```

LangGraph state may contain intermediate AI outputs.

It must not become the permanent source of truth for project state.

---

# 14. State Persistence

Long-running execution metadata is persisted through the AI Execution system.

This means a worker/browser failure does not necessarily destroy the execution.

However, authoritative project entities remain persisted through their domain services.

---

# 15. Agent Context Architecture

Each agent receives a purpose-built context.

```text
Project State
+
Assessment
+
Previous Validated Outputs
+
Relevant RAG
+
Relevant GitHub
+
Relevant Research
+
User Input
        ↓
Context Builder
        ↓
Agent
```

The context builder determines relevance.

---

# 16. Context Is Not "Everything"

Never send:

```text
entire database
+
all documents
+
all students
+
all groups
+
all GitHub data
```

to an agent.

This creates:

- token waste;
- privacy risk;
- irrelevant information;
- context confusion;
- higher hallucination risk;
- unnecessary cost.

---

# 17. Agent Context Contracts

Each agent declares what it needs.

Example:

```text
Technology Agent:
- project profile
- problem
- solution
- complexity
- student skill
- goals
- scope
- assessment
- relevant research
```

Example:

```text
Risk Agent:
- project profile
- technology
- features
- specification
- MVP
- timeline
- dependencies
- relevant research
```

The context builder should construct these packages explicitly.

---

# 18. Context Freshness

Context should be based on the latest valid project state relevant to the execution.

When project state changes:

```text
Old Context
    ↓
Invalidated/obsolete
    ↓
New Context
```

The system should not reuse stale context blindly.

Execution metadata should identify the relevant project/blueprint versions where necessary.

---

# 19. Context Versioning

Important AI executions should record contextual references such as:

```text
project_version/state timestamp
assessment version
blueprint version
document versions
research timestamp
RAG context metadata
```

This makes outputs traceable.

---

# 20. RAG Context

When an agent needs project knowledge:

```text
Agent
 ↓
Context Requirement
 ↓
LlamaIndex Retrieval
 ↓
Project Authorization
 ↓
Relevant Chunks
 ↓
Context Builder
```

The agent does not perform unrestricted vector searches.

---

# 21. GitHub Context

GitHub monitoring information is retrieved only when relevant.

Example:

```text
AI Mentor
 ↓
"Why is my project behind?"
 ↓
Tasks + milestones
 +
GitHub activity
 ↓
LLM analysis
```

GitHub remains monitoring-only.

No agent receives GitHub write authority.

---

# 22. Web Research Context

Current web research is used only where justified.

Example:

```text
MVP Agent
 ↓
Tavily
 ↓
Current evidence
 ↓
Research sources
 ↓
MVP reasoning
```

Not every agent gets web access.

This reduces:

- cost;
- noise;
- latency;
- attack surface.

---

# 23. Tool Availability by Agent

Tool access should be capability-based.

Example:

| Agent | DB Context | RAG | Tavily | GitHub |
|---|---:|---:|---:|---:|
| Idea | Yes | Optional | Optional | No |
| Scope | Yes | Optional | Optional | No |
| Technology | Yes | Yes | Optional | No |
| Features | Yes | Yes | Optional | No |
| Specification | Yes | Yes | Optional | No |
| MVP | Yes | Yes | **Yes** | No |
| Timeline | Yes | Optional | No | No |
| Risk | Yes | Yes | Optional | Optional |
| Task | Yes | Yes | No | No |
| Milestone | Yes | No/Optional | No | No |
| README | Validated context | No direct global retrieval | No | No |
| QA/Judge | Validated outputs | Optional | Optional | Optional |

"Optional" means only when the workflow determines it is relevant and authorized.

---

# 24. Tool Authorization

Tools enforce authorization independently.

```text
Agent
 ↓
Tool Request
 ↓
Authorization Context
 ↓
Resource Scope
 ↓
Tool
```

The agent cannot override permissions.

---

# 25. No Direct Database Access

Agents do not receive database credentials.

Incorrect:

```text
Agent → SQL → PostgreSQL
```

Correct:

```text
Agent
 ↓
Typed Tool
 ↓
Application/Domain Query
 ↓
Repository
 ↓
PostgreSQL
```

This preserves authorization and data ownership.

---

# 26. Agent Output Pipeline

The canonical output path is:

```text
LLM
 ↓
Structured Output
 ↓
Pydantic Validation
 ↓
Agent Result
 ↓
QA/Judge
 ↓
Deterministic Domain Service
 ↓
Persistence
```

An LLM response by itself is never equivalent to database state.

---

# 27. Pydantic Failure

If the model returns malformed structured output:

```text
LLM
 ↓
Malformed Output
 ↓
Pydantic
 ↓
FAIL
```

The orchestrator can perform bounded regeneration.

If regeneration remains invalid:

```text
Execution = FAILED
```

No invalid data reaches the domain layer.

---

# 28. QA/Judge Gate

QA/Judge is a mandatory gate for generated blueprint artifacts.

```text
Agent Outputs
      ↓
Pydantic
      ↓
QA/Judge
      ↓
PASS / FAIL
```

Only a passing result proceeds to authoritative persistence.

---

# 29. QA/Judge Does Not Replace Deterministic Validation

Both are required.

### Deterministic validation

Checks:

- types;
- enums;
- required fields;
- database constraints;
- business rules;
- date validity;
- dependency structure.

### QA/Judge

Checks:

- semantic consistency;
- completeness;
- contradictions;
- quality;
- contextual coherence.

---

# 30. QA Trigger Categories

QA may flag:

```text
SCHEMA
MISSING_INFORMATION
CONTRADICTION
SCOPE_VIOLATION
TECHNOLOGY_INCONSISTENCY
TIMELINE_INCONSISTENCY
TASK_DEPENDENCY_ERROR
MILESTONE_INCONSISTENCY
RISK_GAP
README_MISMATCH
UNSUPPORTED_CLAIM
QUALITY_THRESHOLD
```

---

# 31. QA Severity

Findings may be classified:

```text
INFO
WARNING
ERROR
CRITICAL
```

Only configured severity thresholds should force regeneration.

Not every warning needs regeneration.

---

# 32. Targeted Regeneration

When QA identifies a localized issue:

```text
QA
 ↓
Affected Agent/Artifact
 ↓
Regenerate
 ↓
Validate
 ↓
QA
```

Example:

```text
Timeline inconsistency
       ↓
Timeline Agent
       ↓
New Timeline
       ↓
QA
```

---

# 33. Regeneration Dependency Awareness

If a changed output affects downstream artifacts, the orchestrator determines the impacted dependency chain.

Example:

```text
Technology changes
       ↓
Specification affected
       ↓
Tasks affected
       ↓
Milestones affected
       ↓
README potentially affected
```

Only impacted outputs are regenerated.

---

# 34. No Change/Impact Agent

There is no dedicated Change/Impact Agent.

Impact analysis is handled through:

- orchestration logic;
- dependency graph;
- context/version analysis;
- relevant agents;
- deterministic application logic.

This avoids creating an agent whose responsibility overlaps orchestration.

---

# 35. Regeneration Boundaries

Regeneration must be bounded.

```text
Initial
 ↓
QA
 ↓
Targeted regeneration
 ↓
QA
 ↓
Targeted regeneration
 ↓
Maximum attempts
 ↓
FAILED / REVIEW REQUIRED
```

No infinite loop.

---

# 36. Broad Regeneration

If QA determines that outputs are broadly inconsistent:

```text
QA
 ↓
Broad inconsistency
 ↓
Determine affected dependency subgraph
 ↓
Regenerate affected agents
 ↓
QA
```

The system does not automatically regenerate unrelated content.

---

# 37. Existing Valid Version Preservation

If a new generation fails:

```text
Blueprint v1 = valid
       ↓
Generate v2
       ↓
Failure
       ↓
Blueprint v1 remains valid
```

The system never replaces the last valid state with incomplete AI output.

---

# 38. Agent Execution Attempts

Each execution should distinguish:

```text
workflow attempt
agent attempt
regeneration attempt
provider retry
```

These are not the same thing.

Example:

```text
Agent attempt = 2
Provider retry = 3
QA regeneration = 1
```

This distinction is important for observability and cost analysis.

---

# 39. Provider Retry vs Agent Regeneration

Provider retry:

> Same logical AI request failed because of infrastructure/provider behavior.

Agent regeneration:

> The generated result was invalid or failed QA and a new generation is required.

They must not be counted as the same operation.

---

# 40. Blueprint Execution Lifecycle

```text
REQUESTED
   ↓
QUEUED
   ↓
RUNNING
   ↓
AGENTS_RUNNING
   ↓
VALIDATING
   ↓
QA
   ↓
 ┌───────────────┐
 │               │
PASS            FAIL
 │               │
 ▼               ▼
PERSIST       REGENERATE
 │               │
 ▼               └──→ VALIDATING
COMPLETED
```

Failure can occur at any stage:

```text
FAILED
```

Cancellation:

```text
CANCELLING
   ↓
CANCELLED
```

---

# 41. LangGraph Node Design

Each agent can be represented as a graph node.

Conceptually:

```text
class AgentNode:
    validate_input()
    build_context()
    execute()
    validate_output()
    return_result()
```

However, the implementation should avoid artificial inheritance hierarchies where they do not add value.

The architecture requires clear responsibilities, not class proliferation.

---

# 42. Agent Base Abstraction

A lightweight common interface is useful.

Conceptually:

```text
Agent
├── agent_type
├── input_contract
├── output_contract
├── execute()
└── required_context()
```

Individual agents implement their specialized behavior.

Common infrastructure such as execution metadata and provider access should be injected rather than duplicated.

---

# 43. Agent Independence

Agents should be independently testable.

For example:

```text
TechnologyAgent
```

can be tested using:

```text
Mock Context
+
Mock AI Provider
```

without running the entire blueprint workflow.

This is important for development speed and reliability.

---

# 44. Agent Prompt Separation

Prompts should not be scattered inside unrelated business services.

Logical organization:

```text
Agent
 ├── Contract
 ├── Context Requirements
 ├── Prompt Definition
 ├── Tool Requirements
 └── Execution Logic
```

Prompt/version metadata should be traceable to executions.

---

# 45. Agent Model Selection

Agents request logical model capabilities.

Example:

```text
MVP Agent → REASONING
README Agent → STANDARD
QA/Judge → REASONING
```

Actual provider model names are determined by the Part 6E model policy.

Agents do not know API keys or provider credentials.

---

# 46. Agent Tool Selection

Agents should have an explicit tool allowlist.

Example:

```text
MVP Agent:
    Tavily
    Project Query
    RAG

Task Agent:
    Project Query
    Feature Query
    Specification Query
    Timeline Query
```

This reduces accidental overreach.

---

# 47. AI Mentor Is Not One of the 12 Blueprint Agents

The 12 agents are primarily specialized project-generation/planning agents.

The AI Mentor is an application-level AI capability that may use the same:

- AI Provider Gateway;
- LangChain;
- RAG;
- tools;
- context builder;
- observability.

It does not need to become a thirteenth autonomous planning agent.

---

# 48. AI Mentor Workflow

```text
Student
 ↓
AI Mentor API
 ↓
Authorization
 ↓
Context Builder
 ↓
Relevant Tools/RAG
 ↓
LangChain
 ↓
AI Provider Gateway
 ↓
Model
 ↓
Response
```

For complex reasoning it can use appropriate orchestration components, but it does not gain unrestricted authority.

---

# 49. Assessment Dynamic Question Workflow

The five dynamic questions are sequentially adaptive.

```text
Core Questions
      ↓
Assessment Context
      ↓
Dynamic Q1
      ↓
Answer 1
      ↓
Dynamic Q2
      ↓
Answer 2
      ↓
Dynamic Q3
      ↓
...
      ↓
Dynamic Q5
```

Each dynamic question can depend on:

- previous answer;
- accumulated relevant context;
- project context;
- prior assessment information.

Only one dynamic question is generated at a time.

---

# 50. Assessment State

The assessment workflow maintains:

```text
assessment_id
current_question
answers
accumulated_context
question_sequence
generation_metadata
```

Questions are persisted before being presented.

This ensures the assessment remains recoverable.

---

# 51. Assessment Generation Failure

If dynamic question generation fails:

```text
Generate Question
 ↓
Provider/AI Failure
 ↓
Persist failure
 ↓
Retry/fallback according to AI policy
 ↓
If unavailable:
    assessment remains recoverable
```

The system does not invent a question to hide an AI failure.

---

# 52. AI Execution Persistence

Every long-running agent workflow has:

```text
execution_id
correlation_id
user_id
project_id
execution_type
status
started_at
completed_at
duration
token usage
provider
model
error
```

Each agent has its own execution record.

---

# 53. Execution Events

Execution events may include:

```text
execution.started
agent.started
agent.progress
agent.completed
agent.failed
validation.started
validation.failed
qa.started
qa.completed
regeneration.triggered
execution.completed
execution.failed
execution.cancelled
```

These support:

- SSE;
- activity;
- notifications;
- Admin observability;
- debugging.

---

# 54. LangSmith Trace Relationship

A logical relationship should exist:

```text
GrowFlow Execution ID
       ↕
LangGraph Run
       ↕
LangChain Calls
       ↕
Agent Runs
       ↕
Tool Calls
       ↕
Provider Calls
```

This makes an entire AI workflow traceable.

---

# 55. Correlation IDs

Every workflow carries:

```text
correlation_id
execution_id
agent_execution_id
```

Example:

```text
HTTP Request C123
      ↓
AI Execution E456
      ↓
Technology Agent A789
```

This makes cross-system debugging practical.

---

# 56. AI Event Streaming

LangGraph execution events should be normalized into GrowFlow execution events.

```text
LangGraph
   ↓
Execution Event Adapter
   ↓
GrowFlow Event System
   ↓
SSE
```

The frontend should not depend directly on LangGraph internals.

---

# 57. AI Worker Architecture

```text
FastAPI
  ↓
Application Service
  ↓
Create Execution
  ↓
Worker Queue
  ↓
AI Worker
  ↓
LangGraph
  ↓
Agents
  ↓
AI Provider Gateway
```

The worker is responsible for running long-running workflows independently of the request lifecycle.

---

# 58. Browser Disconnect

A browser disconnect must not destroy the workflow.

```text
Browser
   X
AI Worker
   ↓
Execution continues
   ↓
Persisted state
```

On reconnect:

```text
GET /ai/executions/{execution_id}
```

or SSE reconnection can retrieve the existing execution state.

---

# 59. Cancellation

Cancellation follows:

```text
User
 ↓
Cancel Request
 ↓
Authorization
 ↓
Execution Manager
 ↓
CANCELLING
 ↓
LangGraph/Worker cancellation
 ↓
CANCELLED
```

No new agents should be started after cancellation is accepted.

---

# 60. Failure Handling

Failure categories include:

```text
VALIDATION_FAILURE
PROVIDER_FAILURE
RATE_LIMIT
QUOTA_EXHAUSTED
PROVIDER_UNAVAILABLE
TOOL_FAILURE
RAG_FAILURE
RESEARCH_FAILURE
QA_FAILURE
AUTHORIZATION_FAILURE
TIMEOUT
CANCELLED
INTERNAL_FAILURE
```

Each failure is persisted with a machine-readable code.

---

# 61. AI Quota Exhaustion in Agent Workflows

If AI quota becomes exhausted during a workflow:

```text
Agent A → COMPLETED
Agent B → COMPLETED
Agent C → QUOTA_EXHAUSTED
```

The workflow must not fabricate Agent C output.

Depending on workflow requirements, it should:

- stop the workflow;
- mark execution as quota exhausted;
- preserve previous valid outputs;
- allow retry later.

Partial intermediate outputs must not be treated as a complete blueprint.

---

# 62. Provider Failure During Workflow

If an agent encounters provider failure:

```text
Agent
 ↓
Gateway retry
 ↓
Fallback if valid
 ↓
Still failing
 ↓
Agent FAILED
 ↓
Workflow recovery policy
```

The orchestrator determines whether the failure is recoverable.

---

# 63. Tool Failure During Workflow

Example:

```text
MVP Agent
 ↓
Tavily failure
```

The agent should not fabricate research evidence.

Possible behavior:

```text
Retry
 ↓
Fallback if configured
 ↓
If unavailable:
    research-dependent output fails or is marked incomplete
```

The workflow must preserve epistemic honesty.

---

# 64. RAG Failure

If RAG is unavailable:

```text
RAG retrieval
 ↓
Failure
```

The system should not pretend the missing documents were retrieved.

The agent may continue only if the task remains valid without those documents.

Otherwise the execution fails or enters a controlled degraded path.

---

# 65. Partial Workflow Recovery

Where safe, completed valid agent outputs may be reused.

Example:

```text
Idea ✓
Scope ✓
Technology ✓
Features ✓
Specification ✗
```

If Specification failed because of a transient provider issue, valid upstream outputs remain available.

A retry can resume from the failed node if the context/version remains valid.

---

# 66. Recovery After Project Changes

If the project changed while an AI workflow was running:

```text
Execution started
      ↓
Project changed
      ↓
Context no longer valid
      ↓
Impact check
      ↓
Cancel/invalidate stale execution
      ↓
New execution with current context
```

Stale AI output must not silently overwrite newer project state.

---

# 67. Optimistic Execution Safety

Every authoritative persistence step should verify that the relevant project/blueprint version remains compatible.

If not:

```text
Version mismatch
    ↓
Reject stale persistence
    ↓
Require regeneration/reconciliation
```

This prevents race-condition corruption.

---

# 68. AI and Project Versioning

AI execution should reference relevant versions:

```text
project state/version
blueprint version
document version
assessment version
```

This enables the system to determine whether an output is still valid.

---

# 69. Deterministic Persistence

After QA:

```text
Validated AI Output
      ↓
Application Service
      ↓
Domain Validation
      ↓
Transaction
      ↓
PostgreSQL
```

The domain service decides how the structured output maps to canonical entities.

---

# 70. Example: Technology Agent

```text
Technology Agent
      ↓
TechnologyPlan
      ↓
Pydantic
      ↓
QA
      ↓
Project Technology Service
      ↓
project_technologies
```

The agent never performs the final database mutation.

---

# 71. Example: Task Agent

```text
Task Agent
      ↓
TaskPlan
      ↓
Pydantic
      ↓
QA
      ↓
Task Service
      ↓
Business validation
      ↓
Transaction
      ↓
tasks
```

---

# 72. Example: Risk Agent

```text
Risk Agent
      ↓
RiskPlan
      ↓
Pydantic
      ↓
QA
      ↓
Risk Service
      ↓
risks
```

Risk state remains deterministic and auditable.

---

# 73. Example: README Agent

```text
Validated Project State
      ↓
README Agent
      ↓
READMEOutput
      ↓
Pydantic
      ↓
QA
      ↓
Markdown Renderer
      ↓
Document Version
```

Markdown remains a representation, not the canonical project state.

---

# 74. Agent-to-Agent Communication

Agents should communicate primarily through **validated structured outputs**, not arbitrary conversational messages.

Correct:

```text
TechnologyAgent
      ↓
TechnologyPlan
      ↓
SpecificationAgent
```

This improves:

- determinism;
- validation;
- observability;
- debugging;
- versioning.

---

# 75. No Agent Conversation Theater

Agents do not need artificial back-and-forth conversations.

Avoid:

```text
Agent A: "What do you think?"
Agent B: "I agree."
Agent C: "Maybe."
```

The architecture is workflow-oriented, not simulated multi-agent conversation.

Agents execute purposeful computational roles.

---

# 76. QA Feedback Routing

QA findings should identify affected outputs.

Example:

```text
Finding:
Timeline conflicts with available duration

Affected:
Timeline

Action:
Regenerate Timeline
```

Another:

```text
Finding:
Task dependency references missing feature

Affected:
Task + potentially Specification

Action:
Regenerate affected dependency chain
```

---

# 77. QA as Graph Routing

Conceptually:

```text
QA
 │
 ├── PASS → Persistence
 │
 ├── Local FAIL → Affected Agent
 │
 └── Broad FAIL → Impacted Subgraph
```

This makes regeneration controlled.

---

# 78. Agent Quality Thresholds

Different agent outputs may have different quality requirements.

For example:

- README can tolerate minor wording differences;
- timeline requires date/dependency consistency;
- tasks require structural consistency;
- QA itself requires high-confidence evaluation.

Quality thresholds are configured by workflow/agent policy.

---

# 79. Agent Determinism

LLM outputs are inherently variable.

GrowFlow should therefore achieve operational determinism through:

- fixed contracts;
- controlled context;
- versioned prompts;
- model policy;
- bounded temperature/configuration where appropriate;
- validation;
- QA;
- deterministic persistence.

The architecture does not assume the LLM is deterministic.

---

# 80. Temperature / Generation Configuration

Generation parameters should be controlled centrally where appropriate.

Agents should not arbitrarily modify provider generation parameters.

Possible configuration:

```text
temperature
max_output_tokens
structured_output_mode
tool_choice_policy
```

Exact values are implementation/model-stack decisions.

---

# 81. Token Budgeting

Each agent should have a reasonable token budget based on its task.

This prevents one agent from consuming excessive context/output capacity.

Token limits are centrally configurable.

---

# 82. Context Budgeting

The Context Builder should prioritize:

1. required project state;
2. direct user input;
3. dependent validated outputs;
4. relevant documents;
5. relevant research;
6. optional supporting context.

If context exceeds the configured budget, irrelevant/low-priority context is removed rather than blindly truncating critical project information.

---

# 83. Context Compression

If large context must be reduced, use deterministic or controlled summarization strategies.

Do not automatically send an entire document corpus to the model.

Existing validated structured state should generally be preferred over repeatedly summarizing the same information.

---

# 84. Agent Memory

GrowFlow should not implement unrestricted autonomous agent memory.

Relevant state comes from:

- PostgreSQL;
- assessment;
- blueprint versions;
- documents/RAG;
- GitHub;
- execution context.

This provides explicit, inspectable memory.

---

# 85. AI Execution Idempotency

A generation request should have an execution identity.

Duplicate requests should not create multiple competing authoritative blueprint versions without explicit user intent.

Idempotency should be applied to appropriate commands.

---

# 86. Concurrency Between AI Workflows

The system must prevent conflicting workflows from silently overwriting each other.

Example:

```text
Blueprint Generation E1
       +
Project Change E2
```

If both target the same project state:

```text
Version compatibility check
        ↓
One execution becomes stale/incompatible
        ↓
Stale output cannot persist
```

---

# 87. AI Workflow Locking

Do not introduce heavy distributed locks unnecessarily.

Use:

- execution state;
- version checks;
- domain transaction boundaries;
- command conflict rules.

A project may have workflow-level restrictions where necessary, but the solution should remain lightweight.

---

# 88. AI Mentor Concurrency

AI Mentor conversations may run concurrently, but state-changing actions still pass through deterministic command services.

Two recommendations do not themselves mutate state.

---

# 89. Agent Security

Every agent execution inherits:

```text
user_id
role
group scope
project scope
privacy policy
execution permissions
```

The agent cannot elevate these permissions.

---

# 90. Agent Data Isolation

A student agent can only receive authorized student/project information.

A mentor agent can only receive authorized group/student/project information.

An admin agent can access authorized platform information according to the Admin privacy model.

Private/deeper content remains subject to controlled investigation where required.

---

# 91. Admin AI

Admin AI can use the same agent/tool infrastructure for authorized operational and basic cross-platform information.

It can query:

- students;
- mentors;
- groups;
- projects;
- instances;
- AI usage;
- execution status;
- system health.

Deeper protected/private content requires the controlled investigation workflow:

```text
Request
 ↓
Authorization
 ↓
Minimum Required Data
 ↓
Inspection
 ↓
Audit Log
```

No unrestricted admin AI access.

---

# 92. Agent Observability

Every agent execution should be traceable by:

```text
execution_id
agent_execution_id
correlation_id
agent_type
sequence
attempt
model
provider
latency
tokens
status
errors
```

This supports Admin AI Observatory.

---

# 93. Agent Metrics

Track:

- executions;
- success rate;
- failure rate;
- average latency;
- token usage;
- retries;
- QA failures;
- regeneration rate;
- average regeneration attempts;
- provider/model usage.

---

# 94. Cost Attribution

AI cost should be attributable where possible to:

```text
user
project
execution
agent
model
provider
```

This allows analysis such as:

```text
Which agents consume the most tokens?
Which projects generate the most AI cost?
Which model is most expensive?
```

---

# 95. LangSmith Evaluation

LangSmith can support evaluation of:

- agent outputs;
- workflow behavior;
- tool selection;
- retrieval quality;
- consistency;
- regression tests.

However, LangSmith evaluation does not replace GrowFlow's authoritative QA/domain validation.

---

# 96. Agent Regression Testing

Agent behavior should be tested against controlled fixtures.

Example:

```text
Input Project A
 ↓
Technology Agent
 ↓
Expected structural properties
 ↓
Pydantic
 ↓
QA
```

Tests should emphasize properties and contracts rather than requiring exact wording from an LLM.

---

# 97. Evaluation Data

Evaluation datasets may include:

- representative project ideas;
- weak project ideas;
- ambiguous requirements;
- unrealistic technology choices;
- conflicting timelines;
- excessive scope;
- incomplete requirements.

This helps test the system against realistic project scenarios.

---

# 98. Failure Injection

The AI orchestration test suite should intentionally simulate:

```text
Provider timeout
Rate limit
Quota exhaustion
Malformed output
Tool failure
RAG failure
Tavily failure
QA failure
Worker crash
Cancellation
Stale project version
```

The system should recover or fail predictably.

---

# 99. Agent Execution Security Tests

Test:

- unauthorized project context;
- cross-student retrieval;
- cross-group retrieval;
- malicious tool arguments;
- prompt injection;
- malicious uploaded files;
- malicious GitHub content;
- malicious web content;
- secret leakage;
- stale execution persistence.

---

# 100. No Autonomous Authority

Agents do not have authority to:

- change project ownership;
- change user roles;
- change permissions;
- access unrelated projects;
- delete authoritative state;
- manage GitHub repositories;
- bypass mentor/admin permissions;
- bypass AI quota controls.

AI is a reasoning layer, not a security principal.

---

# 101. AI Quota Exhaustion — Final Agent Rule

When the provider capacity is exhausted:

```text
AI Provider Gateway
       ↓
QUOTA_EXHAUSTED
       ↓
Agent execution cannot continue
       ↓
Workflow enters controlled unavailable/failed state
```

No agent may attempt to obtain unauthorized credentials.

No agent may repeatedly retry after a confirmed quota exhaustion.

The user receives the platform's explicit quota-exhausted state.

---

# 102. Core Platform Continues

While an AI workflow is unavailable:

```text
AI
 ├── unavailable
 │
Core GrowFlow
 ├── project viewing
 ├── task management
 ├── milestone management
 ├── deterministic progress
 ├── mentor communication
 ├── notifications
 ├── document viewing
 └── GitHub monitoring
```

continue where independently available.

---

# 103. Agent Retry Hierarchy

There are three distinct levels:

```text
Level 1
Provider Retry
    ↓
same logical model request

Level 2
Agent Regeneration
    ↓
new model generation because output failed validation/QA

Level 3
Workflow Recovery
    ↓
resume/restart affected graph nodes
```

These must remain separate in code and observability.

---

# 104. Agent Failure Policy

Each agent should define whether failure is:

```text
BLOCKING
NON_BLOCKING
OPTIONAL
```

For blueprint generation, most core planning agents are blocking because downstream outputs depend on them.

Optional enrichment may be allowed to fail without destroying the entire blueprint if the workflow explicitly permits it.

The exact per-agent policy belongs in the workflow configuration.

---

# 105. Dependency-Aware Failure

Example:

```text
Technology Agent FAILED
       ↓
Specification cannot safely run
       ↓
Tasks cannot safely run
```

The orchestrator should not blindly execute dependent agents with missing required inputs.

---

# 106. Optional Context Failure

If an optional source fails:

```text
GitHub unavailable
```

an AI Mentor request may still proceed if GitHub data is not essential.

The context builder marks unavailable context explicitly.

It must never imply that unavailable data was successfully retrieved.

---

# 107. Uncertainty Handling

Agents should be allowed to express uncertainty where appropriate.

For example:

```text
confidence
assumptions
warnings
evidence
```

This is preferable to forcing the model to invent certainty.

---

# 108. Evidence vs Recommendation

AI outputs should distinguish:

```text
Evidence
```

from:

```text
Recommendation
```

Especially for:

- MVP research;
- technology recommendations;
- risk analysis;
- AI Mentor responses.

This improves transparency.

---

# 109. Agent Output Metadata

Where useful, outputs may include:

```text
source_references
assumptions
warnings
confidence
generation_metadata
```

These are metadata, not substitutes for domain validation.

---

# 110. Agent Versioning

Each execution should identify:

```text
agent_type
agent_version
prompt_version
contract_version
model
provider
```

This enables reproducibility and debugging when the system evolves.

---

# 111. Prompt Versioning

When meaningful prompt changes occur:

```text
Prompt v1
Prompt v2
```

new executions identify the version used.

Existing generated artifacts remain associated with their original execution/version.

---

# 112. Model Change Safety

Changing a configured model should not silently invalidate historical outputs.

Historical executions retain:

```text
provider
model
prompt version
contract version
agent version
```

Future executions use the new configuration.

---

# 113. Agent Workflow and Documents

The canonical relationship is:

```text
Agent Structured Output
       ↓
Validation
       ↓
Domain Persistence
       ↓
Markdown Renderer
       ↓
Document Version
```

Documents do not become a hidden second source of truth.

---

# 114. Blueprint Completion Criteria

A blueprint workflow is complete only when:

- required agents completed;
- outputs passed Pydantic validation;
- QA/Judge passed;
- deterministic persistence succeeded;
- required document versions were generated;
- execution state is COMPLETED.

A model response alone does not mean blueprint completion.

---

# 115. Blueprint Failure Criteria

Blueprint generation fails when:

- required AI capacity is unavailable;
- required provider calls cannot complete;
- required structured output cannot be validated;
- QA cannot pass after bounded regeneration;
- required dependencies cannot be resolved;
- project version becomes stale;
- worker/execution failure cannot recover.

The previous valid blueprint remains intact.

---

# 116. Blueprint Recovery

If failure occurs before authoritative persistence:

```text
Existing valid blueprint
        ↓
UNCHANGED
```

A later retry may create a new execution.

---

# 117. Project Change Recovery

For a project-change workflow:

```text
Change Request
 ↓
Impact Analysis
 ↓
Confirmation
 ↓
Regeneration
 ↓
QA
```

If regeneration fails:

```text
Previous valid blueprint
        ↓
Remains active
```

No partial change is silently committed.

---

# 118. AI Mentor Tool Boundary

AI Mentor may access:

```text
Project
Assessment
Blueprint
Tasks
Milestones
Risks
Documents/RAG
GitHub Activity
```

only when authorized and relevant.

It may also use Tavily when current external information is necessary.

It cannot directly execute project mutations.

---

# 119. Agent Communication with Domain Services

Agents return structured proposals.

Domain services interpret them.

Example:

```text
TaskAgent
   ↓
TaskPlan
   ↓
TaskService
   ↓
Validate
   ↓
Persist
```

This keeps domain rules independent of LLM behavior.

---

# 120. Domain Authority

The final authority remains:

```text
Domain Rules
+
Database Constraints
```

not:

```text
LLM output
```

This is one of the most important architectural boundaries in GrowFlow.

---

# 121. Agent Orchestration Does Not Become a Microservice

LangGraph runs inside the modular-monolith architecture.

```text
GrowFlow Backend
├── API
├── Application
├── Domain
├── Infrastructure
├── AI
│   ├── LangGraph
│   ├── LangChain
│   ├── Agents
│   └── Provider Gateway
└── Workers
```

No separate agent microservice is required.

---

# 122. Agent Package Organization

Logical structure:

```text
app/
└── domain/
    └── ai/
        ├── agents/
        │   ├── idea/
        │   ├── scope/
        │   ├── technology/
        │   ├── features/
        │   ├── specification/
        │   ├── mvp/
        │   ├── timeline/
        │   ├── risk/
        │   ├── task/
        │   ├── milestone/
        │   ├── readme/
        │   └── qa/
        │
        ├── orchestration/
        ├── contracts/
        ├── context/
        └── policies/
```

Exact package placement may be refined during implementation, but each file must retain a focused responsibility.

---

# 123. Agent Implementation Boundary

Agents should depend on abstractions such as:

```text
AIProviderGateway
ContextBuilder
Tool interfaces
Contract models
Execution context
```

They should not depend directly on:

```text
OpenRouter SDK
PostgreSQL driver
Supabase service key
raw vector DB
GitHub SDK
Tavily HTTP implementation
```

External details belong behind infrastructure adapters.

---

# 124. Agent Dependency Direction

Correct:

```text
Agent
 ↓
Abstraction
 ↓
Infrastructure implementation
```

Incorrect:

```text
Agent
 ↓
Vendor SDK
 ↓
Provider
```

This preserves testability and replaceability.

---

# 125. Final AI Agent Architecture

```text
                         AI USE CASE
                              │
                              ▼
                    AI Execution Manager
                              │
                              ▼
                         LangGraph
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   Context Builder        Agent Nodes          Tool Layer
        │                     │                     │
        │          ┌──────────┼──────────┐          │
        │          ▼          ▼          ▼          │
        │       Agents      Agents      QA           │
        │          │          │          │           │
        └──────────┼──────────┼──────────┼───────────┘
                   │
                   ▼
               LangChain
                   │
                   ▼
          AI Provider Gateway
                   │
        ┌──────────┼───────────┐
        ▼          ▼           ▼
    Model Policy Key Pool   Retry/Quota
        │          │           │
        └──────────┼───────────┘
                   ▼
           OpenRouter Adapter
                   │
                   ▼
                Provider
```

Supporting:

```text
Documents → LlamaIndex → RAG → Context Builder
MVP Agent → Tavily → Research
Workflow → LangSmith → Tracing/Evaluation
Outputs → Pydantic → QA → Domain Services → PostgreSQL
```

---

# 126. Final Agent Responsibility Matrix

| Agent | Primary Responsibility | Main Outputs |
|---|---|---|
| Idea | Refine project idea | Idea analysis/profile |
| Scope | Define boundaries | Scope |
| Technology | Recommend stack | Technology plan |
| Features | Identify features | Feature plan |
| Specification | Detail features | Specifications |
| MVP | Define MVP | MVP definition/research |
| Timeline | Plan duration | Timeline/phases |
| Risk | Identify/manage risks | Risk plan |
| Task | Break work down | Tasks |
| Milestone | Group meaningful outcomes | Milestones |
| README | Produce project README | README |
| QA/Judge | Validate/evaluate | QA result |

---

# 127. Final Technology Responsibility Matrix

| Technology | Responsibility |
|---|---|
| LangGraph | Agent workflow orchestration |
| LangChain | AI building blocks |
| LlamaIndex | RAG/document knowledge |
| LangSmith | AI traces/evaluation |
| OpenAI-compatible SDK | Provider communication through gateway |
| OpenRouter | Initial external provider/routing |
| Tavily | Current web research |
| Pydantic | Structured AI contracts |
| PostgreSQL | Canonical application state |
| SSE | AI execution streaming |
| Workers | Long-running execution |

---

# 128. Final Execution Responsibility Matrix

| Responsibility | Owner |
|---|---|
| Workflow graph | LangGraph |
| Agent reasoning | Agent |
| Context assembly | Context Builder |
| Provider communication | AI Provider Gateway |
| Model selection | Model Policy |
| Key rotation | Key Pool |
| Retry | Retry Policy |
| Quota handling | AI Provider Gateway |
| RAG retrieval | LlamaIndex/RAG Service |
| Web research | Tavily Adapter |
| Schema validation | Pydantic |
| Semantic QA | QA/Judge |
| Business validation | Domain Service |
| State persistence | Domain/Data Services |
| AI tracing | LangSmith |
| Execution persistence | AI Execution Service |
| User streaming | SSE |

---

# 129. Final Non-Negotiable Rules

1. Exactly 12 logical agents.
2. One primary responsibility per agent.
3. LangGraph owns orchestration.
4. LangChain provides AI building blocks.
5. LlamaIndex provides RAG/document workflows.
6. LangSmith provides AI tracing/evaluation.
7. Tavily provides current web research where required.
8. Agents never access raw provider keys.
9. Agents never directly call providers.
10. Agents never bypass the AI Provider Gateway.
11. Agents never receive unrestricted SQL access.
12. Agents never directly mutate authoritative project state.
13. Agent outputs use typed contracts.
14. Pydantic validation precedes domain persistence.
15. QA/Judge gates blueprint persistence.
16. Regeneration is targeted where possible.
17. Regeneration is bounded.
18. Provider retries and agent regeneration are separate concepts.
19. Workflow recovery and provider retries are separate concepts.
20. Existing valid project state survives failed AI generation.
21. Stale executions cannot overwrite newer project state.
22. RAG remains project-scoped and authorization-aware.
23. Retrieved content is untrusted data.
24. Tool calls are independently authorization-checked.
25. AI quota exhaustion stops further LLM calls when no valid capacity/fallback exists.
26. Quota exhaustion never triggers unauthorized key/provider usage.
27. Core non-AI platform functionality continues during AI outages where independent.
28. Browser disconnect does not destroy long-running execution.
29. SSE is the initial streaming mechanism.
30. Agent execution is observable through application telemetry and LangSmith.
31. AI cost/token usage is tracked where available.
32. Exact model names remain centralized in model policy.
33. Prompts/contracts are version-traceable.
34. Context is purpose-built rather than "entire project".
35. AI workflow state is not the canonical project state.
36. No unnecessary agent microservices or distributed orchestration infrastructure.

---

# 130. Architecture-to-Implementation Boundary

Part 6F freezes the architecture.

The following are intentionally left for implementation/technology decisions:

- exact Python class implementations;
- exact LangGraph node implementation;
- exact graph persistence/checkpoint mechanism;
- exact LangChain package/version;
- exact LlamaIndex package/version;
- exact LangSmith package/version;
- exact Tavily package/version;
- exact model names;
- exact model parameters;
- exact worker/queue technology;
- exact retry numbers;
- exact QA thresholds;
- exact token budgets;
- exact concurrency limits;
- exact prompt wording;
- exact Pydantic class definitions;
- exact vector store;
- exact embedding model.

These must not be prematurely hard-coded into the architecture.

---

# 131. Complete GrowFlow AI Architecture

The final architecture from user request to authoritative state is:

```text
USER
 │
 ▼
FASTAPI
 │
 ▼
AUTHORIZATION
 │
 ▼
APPLICATION SERVICE
 │
 ▼
AI EXECUTION
 │
 ▼
WORKER
 │
 ▼
LANGGRAPH
 │
 ├───────────────┐
 │               │
 ▼               ▼
CONTEXT       AGENT GRAPH
BUILDER           │
 │                ├── Idea
 │                ├── Scope
 │                ├── Technology
 │                ├── Features
 │                ├── Specification
 │                ├── MVP
 │                ├── Timeline
 │                ├── Risk
 │                ├── Task
 │                ├── Milestone
 │                ├── README
 │                └── QA/Judge
 │
 ├── PostgreSQL
 ├── LlamaIndex/RAG
 ├── GitHub
 └── Tavily
          │
          ▼
       LANGCHAIN
          │
          ▼
 AI PROVIDER GATEWAY
          │
 ┌────────┼─────────────┐
 │        │             │
 ▼        ▼             ▼
MODEL   FIVE KEYS    RETRY/QUOTA
POLICY   POOL        /FALLBACK
 │        │             │
 └────────┼─────────────┘
          ▼
 OPENROUTER ADAPTER
          │
          ▼
       AI MODEL
          │
          ▼
 STRUCTURED OUTPUT
          │
          ▼
       PYDANTIC
          │
          ▼
      QA/JUDGE
          │
     ┌────┴────┐
     ▼         ▼
   PASS       FAIL
     │         │
     │         ▼
     │     TARGETED
     │   REGENERATION
     │         │
     │         └──→ QA
     │
     ▼
DOMAIN SERVICE
     │
     ▼
POSTGRESQL
     │
     ├── Events
     ├── Notifications
     ├── Documents
     └── Activity
```

Observability:

```text
LangGraph
   ↓
LangChain
   ↓
Agents
   ↓
Tools
   ↓
Gateway
   ↓
Provider
   ↓
LangSmith
```

---

# 132. Part 6F Freeze Statement

**Part 6F — AI Agent Architecture & Orchestration is architecturally FROZEN.**

GrowFlow now has a complete definition of:

- the 12-agent system;
- each agent's responsibility;
- agent boundaries;
- LangGraph orchestration;
- workflow state;
- dependency management;
- controlled parallelism;
- context construction;
- RAG integration;
- Tavily integration;
- tool authorization;
- LangChain integration;
- structured contracts;
- Pydantic validation;
- QA/Judge;
- targeted regeneration;
- bounded regeneration;
- execution persistence;
- provider failure;
- quota exhaustion;
- partial recovery;
- stale execution protection;
- project-change workflows;
- assessment adaptation;
- AI Mentor integration;
- Admin AI integration;
- LangSmith observability;
- deterministic persistence;
- security;
- testing;
- implementation boundaries.

> **Agents reason. LangGraph orchestrates. LangChain supplies AI building blocks. LlamaIndex retrieves knowledge. Tavily supplies current research. LangSmith observes and evaluates. The AI Provider Gateway controls external model access. Pydantic validates structure. QA/Judge validates quality. Domain services own authoritative state. PostgreSQL remains the canonical source of truth.**

**6F is ready to proceed to the next architecture decision phase.**
