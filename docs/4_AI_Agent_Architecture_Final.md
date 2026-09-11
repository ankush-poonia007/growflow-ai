# GrowFlow — Part 4: AI Agent Architecture
## Final V1 Specification

**Status:** FROZEN  
**Part:** 4 — AI Agent Architecture  
**Purpose:** Define GrowFlow's complete V1 AI-agent system, responsibilities, boundaries, dependencies, context strategy, orchestration, validation, retry/recovery, and final decisions.

---

# 1. Executive Summary

GrowFlow will use a **specialized multi-agent architecture** rather than a single general-purpose AI agent.

The final V1 architecture contains **12 agents**:

1. Idea Agent
2. Scope Agent
3. Project Profile Agent
4. Technology Agent
5. Features Agent
6. Specification Agent
7. MVP Agent
8. Timeline / Duration Agent
9. Risk Agent
10. Task Agent
11. Milestone Agent
12. README Agent
13. QA / Judge Agent

> **Important correction:** The final count is **13 agents**, because the Project Profile Agent is retained as a dedicated agent in addition to the original 12-agent candidate list. The user's decision to "let Project Profile be an agent" therefore adds one specialized responsibility.

The architecture follows these principles:

- One meaningful reasoning responsibility per agent.
- Deterministic services remain deterministic.
- Agents produce validated structured outputs.
- PostgreSQL/Supabase remains the canonical project-state source of truth.
- Markdown files are generated representations, not the canonical state.
- Agents receive the context required for their responsibility rather than unrelated project data.
- RAG and external web research are tools/services, not generic agents.
- Tavily is primarily exposed to the MVP Agent for current web research.
- No dedicated Change Impact Agent is created.
- QA/Judge can either judge-only or trigger targeted regeneration depending on the severity/type of the issue.
- Failed generation is recoverable and version-aware.
- Active documents must remain consistent with the same canonical project state/version.

---

# 2. Architecture Goals

The AI architecture must provide:

- high-quality project understanding
- realistic project planning
- student-appropriate technical decisions
- controlled scope
- useful feature/specification definitions
- real-world MVP reasoning
- realistic timelines
- risk awareness
- executable tasks
- meaningful milestones
- coherent project documentation
- independent quality validation
- targeted regeneration
- observability
- project isolation
- predictable downstream outputs

The architecture must avoid:

- one giant AI prompt
- generic "documentation" agents
- unnecessary agents for deterministic operations
- unrestricted database access
- cross-project context leakage
- blindly regenerating every document after every change
- AI-controlled progress/state calculations
- uncontrolled context growth

---

# 3. Core Principle — One Agent, One Primary Role

Every agent has one primary reasoning responsibility.

An agent may produce several fields or closely related outputs, but it must not become a generic "do everything" component.

Examples:

- Idea Agent → What is this project really about?
- Scope Agent → What should and should not be built?
- Project Profile Agent → What is the normalized/enriched project definition?
- Technology Agent → What technology is appropriate?
- Features Agent → What capabilities should the project contain?
- Specification Agent → How should those capabilities behave?
- MVP Agent → What is the smallest valuable real-world product?
- Timeline Agent → When should the work happen?
- Risk Agent → What can go wrong and how should it be handled?
- Task Agent → What executable work must be performed?
- Milestone Agent → What meaningful checkpoints define progress?
- README Agent → How should the complete project be communicated?
- QA/Judge Agent → Is the resulting blueprint coherent and realistic?

---

# 4. Agent vs Service Boundary

This boundary is fundamental.

## 4.1 AI agents own reasoning

Agents handle:

- interpretation
- contextual analysis
- planning
- recommendation
- generation
- technical judgment
- risk reasoning
- project evaluation
- synthesis

## 4.2 Deterministic application services own system state

Normal services handle:

- authentication
- OAuth
- authorization
- CRUD
- database transactions
- project membership
- task status
- milestone status
- progress calculation
- project health calculation
- deadline calculations
- notifications
- audit logs
- file storage
- document versioning
- RAG ingestion
- embeddings
- vector storage
- GitHub API operations
- usage accounting
- execution persistence
- permission checks

AI can recommend or explain these things, but it does not become the authoritative owner of them.

---

# 5. Final Agent Inventory

| # | Agent | Primary Responsibility | V1 |
|---|---|---|---|
| 1 | Idea Agent | Understand/refine project idea | ✅ |
| 2 | Scope Agent | Define realistic project boundaries | ✅ |
| 3 | Project Profile Agent | Consolidate/enrich project definition | ✅ |
| 4 | Technology Agent | Select appropriate technology stack | ✅ |
| 5 | Features Agent | Define project features | ✅ |
| 6 | Specification Agent | Define feature behavior/specifications | ✅ |
| 7 | MVP Agent | Define valuable MVP using project context + current evidence | ✅ |
| 8 | Timeline / Duration Agent | Build realistic temporal plan | ✅ |
| 9 | Risk Agent | Identify and mitigate project risks | ✅ |
| 10 | Task Agent | Generate executable project tasks | ✅ |
| 11 | Milestone Agent | Define meaningful milestones | ✅ |
| 12 | README Agent | Generate coherent project README | ✅ |
| 13 | QA / Judge Agent | Validate the complete blueprint | ✅ |

---

# 6. Idea Agent

## Purpose

Transform the student's initial idea and assessment information into a coherent project concept.

## Inputs

- initial project information
- project name
- problem statement
- proposed solution
- project type
- project complexity
- student skill level
- goals
- constraints
- assessment answers
- preferred/interested technologies
- mentor-project context when applicable

## Responsibilities

- understand the actual problem
- clarify the proposed solution
- identify target users
- refine objective
- identify intended outcome
- identify meaningful innovation/differentiation
- identify initial scope direction
- identify obvious unrealistic assumptions
- preserve the student's actual project intent

## Output

- refined project idea
- problem definition
- objective
- target users
- proposed solution
- innovation
- intended outcome
- initial scope direction
- initial exclusions
- assumptions
- project context

## Boundary

The Idea Agent does not own:

- final technology selection
- final timeline
- final task plan
- detailed specifications
- final risk plan

---

# 7. Scope Agent

## Purpose

Turn the refined idea into a realistic project boundary.

## Inputs

- Idea Agent output
- Project Profile information
- student skill
- complexity
- available duration
- goals
- constraints
- intended solution
- assessment-derived context

## Responsibilities

- define in-scope functionality
- define out-of-scope functionality
- define MVP boundary
- identify constraints
- identify dependencies
- identify deliverables
- define acceptance expectations
- detect excessive scope
- detect student-skill/scope mismatch
- prevent unnecessary scope creep

## Output

- in-scope
- out-of-scope
- MVP boundary
- constraints
- dependencies
- deliverables
- acceptance expectations
- scope warnings

---

# 8. Idea + Scope Relationship for Documentation

The user requested that Idea and Scope be **partially merged only for the documentation side**.

The solution is:

> **Do not merge the agents. Merge their outputs into the Project Profile documentation context.**

Conceptually:

```text
Idea Agent
    │
    ├─────────────┐
    │             │
    ▼             ▼
Idea Output    Scope Agent
                  │
                  ▼
              Scope Output
                  │
                  └──────┐
                         ▼
               Project Profile Agent
                         │
                         ▼
                 Project Profile
```

This preserves the one-agent-one-role principle while ensuring the Project Profile represents both:

- what the project is
- what the project realistically is allowed to become

---

# 9. Project Profile Agent

## Purpose

Create the enriched, normalized project definition used as a major downstream context source.

The agent is retained because the user explicitly chose to keep Project Profile as an agent.

## Inputs

- original project information
- assessment results
- Idea Agent output
- Scope Agent output
- student skill
- project complexity
- project type
- goals
- constraints
- intended outcome
- mentor project context where applicable

## Responsibilities

- consolidate project understanding
- resolve compatible information from upstream outputs
- enrich missing project context
- normalize project terminology
- produce a coherent project definition
- preserve the student's intent
- ensure scope is represented consistently

## Output

- project name
- problem
- proposed solution
- objective
- target users
- project type
- complexity
- student skill
- goals
- scope
- intended outcome
- constraints
- assumptions
- project context

## Boundary

The Project Profile Agent must not independently redesign the project.

It consolidates and enriches the established project understanding.

---

# 10. Technology Agent

## Purpose

Select a coherent, student-appropriate technology stack.

## Inputs

- Project Profile
- Scope
- Features
- MVP
- student skill
- learning goals
- duration
- constraints
- technical requirements

## Responsibilities

- select programming languages
- frameworks
- libraries
- database
- APIs
- AI/ML technologies where necessary
- authentication
- deployment
- development tools
- explain why each major technology is needed
- identify what the student should understand
- minimize technology sprawl

## Core rule

> **Minimum appropriate stack > technology sprawl.**

The Technology Agent should not add technology simply to make the project appear more advanced.

---

# 11. Features Agent

## Purpose

Define **what the project contains**.

## Inputs

- Project Profile
- Scope
- proposed solution
- assessment context
- complexity
- technology context
- MVP context where available

## Responsibilities

Categorize features:

- Must Have
- Should Have
- Good to Have
- Out of Scope

For each feature:

- name
- purpose
- priority
- dependencies
- relationships
- feasibility considerations

## Boundary

Features answer:

> **WHAT does the system have?**

---

# 12. Specification Agent

## Purpose

Define **how project features behave**.

## Inputs

- Project Profile
- Scope
- Features
- Technology Stack
- MVP
- constraints

## Responsibilities

For relevant features:

- functional requirements
- purpose
- behavior
- inputs
- outputs
- validation
- dependencies
- constraints
- technical considerations
- acceptance criteria

## Boundary

Specifications answer:

> **HOW does the feature behave?**

---

# 13. MVP Agent

## Purpose

Determine the smallest valuable and realistic version of the project.

## Inputs

- Project Profile
- Scope
- Features
- Specifications
- Technology
- student skill
- duration
- constraints
- goals

## External Research

The MVP Agent is the primary V1 consumer of **Tavily**.

It can research:

- existing solutions
- similar products
- current APIs
- current platform capabilities
- current implementation patterns
- open-source approaches
- real-world expectations
- technical constraints

## Flow

```text
Project Context
      ↓
MVP Agent
      ↓
Tavily
      ↓
Current Web Evidence
      ↓
Evidence Analysis
      ↓
MVP Reasoning
      ↓
MVP Recommendation
```

## Important rule

Tavily supplies evidence.

The MVP Agent makes the reasoning-based recommendation.

The web does not become the source of truth for the project.

## Output

- MVP definition
- core functionality
- major components
- MVP boundary
- exclusions
- rationale
- real-world considerations
- research/source provenance

---

# 14. Timeline / Duration Agent

## Purpose

Create a realistic temporal execution plan.

## Inputs

- Project Profile
- Scope
- Features
- Specifications
- MVP
- Technology
- student skill
- available duration
- dependencies
- risks when available

## Outputs

- phases
- phase objectives
- start dates
- end dates
- estimated duration
- dependencies
- expected outcomes
- major milestones
- final completion date

## Conceptual phases

```text
Documentation
→ Planning
→ Implementation
→ Testing
→ Deployment
→ Completed
```

Exact state transitions remain deterministic application logic.

---

# 15. Risk Agent

## Purpose

Identify realistic risks and provide mitigation strategies.

## Inputs

- Project Profile
- Scope
- Features
- Specifications
- Technology
- MVP
- Timeline
- student skill
- dependencies
- external services

## Risk Categories

- scope
- time
- technology
- learning difficulty
- APIs
- AI/LLM
- database
- authentication
- integration
- security
- performance
- deployment
- hosting
- cost
- GitHub
- third-party dependencies
- unexpected complexity

## Each Risk Contains

- risk
- probability
- impact
- reason
- early warning
- prevention
- mitigation
- recommended student action

---

# 16. Task Agent

## Purpose

Convert the project definition into executable work.

## Inputs

- Project Profile
- Scope
- Features
- Specifications
- MVP
- Technology
- Timeline
- Risks
- dependencies

## Each Task Contains

- task name
- objective
- description
- rationale
- expected output
- dependencies
- estimated duration
- start date
- end date
- related milestone
- completion criteria

## Boundary

The Task Agent creates task definitions.

The backend determines actual task status.

---

# 17. Milestone Agent

## Purpose

Define meaningful project completion checkpoints.

## Inputs

- Project Profile
- Scope
- Features
- Specifications
- MVP
- Timeline
- Tasks
- dependencies
- Risks

## Each Milestone Contains

- name
- purpose
- related tasks
- expected outcome
- completion criteria
- target date
- dependencies

## Boundary

The Milestone Agent defines milestones.

The deterministic state engine determines actual completion.

---

# 18. Timeline vs Milestone Decision

Timeline and Milestone remain **separate agents**.

Reason:

- Timeline determines **when work should happen**.
- Milestone determines **what meaningful checkpoint signifies progress**.

They interact, but their reasoning responsibilities are distinct.

---

# 19. Task + Milestone Planning Decision

Task and Milestone remain separate specialized agents.

They form the planning chain:

```text
Timeline
   ↓
Task Agent
   ↓
Milestone Agent
```

The Task Agent establishes executable work.

The Milestone Agent groups/organizes that work into meaningful completion checkpoints.

This is preferable to creating a generic "Planning Agent" because it preserves clear ownership and output schemas.

---

# 20. README Agent

## Purpose

Generate the final concise master README.

## Why an Agent

The README is not merely a database dump. It must synthesize multiple project artifacts into a coherent human-facing narrative.

Therefore, retaining an agent is justified.

## Large Context Problem

The README Agent may require information from nearly every upstream artifact.

Sending every raw document in full is inefficient and may cause context bloat.

### Solution — Context Compilation

Before invoking the README Agent, the orchestrator creates a **README Context Package**.

It contains:

- current Project Profile
- approved Scope
- Technology Stack summary
- Features
- Specifications summary
- MVP
- Timeline summary
- Risks summary
- Tasks summary
- Milestones
- project structure
- canonical metadata
- links/references to detailed documents

Large documents are summarized or represented in structured form where full text is unnecessary.

## Output

- project overview
- objective
- technology stack
- features
- specification overview
- MVP
- scope
- duration
- phases
- risks
- tasks
- milestones
- project structure
- references to detailed documents

## Rule

> README is the master entry point, not a duplicate of every document.

---

# 21. QA / Judge Agent

## Purpose

Act as an independent quality gate for the complete blueprint.

## Inputs

- Project Profile
- Scope
- Technology
- Features
- Specifications
- MVP
- Timeline
- Risks
- Tasks
- Milestones
- README
- student constraints
- project version metadata

## Checks

- contradictions
- unrealistic scope
- student-skill mismatch
- technology sprawl
- missing requirements
- missing deliverables
- timeline problems
- dependency errors
- risk gaps
- MVP problems
- task gaps
- milestone gaps
- document inconsistencies

## Output

- score: 0–100
- strengths
- issues
- critical issues
- recommendations
- affected outputs
- regeneration priority

---

# 22. QA Trigger Behavior

The QA/Judge Agent supports two outcomes.

## Mode A — Judge Only

Used when:

- output is acceptable
- issues are informational
- no regeneration is required

The result is recorded.

## Mode B — Judge + Targeted Regeneration

Used when:

- critical contradiction exists
- hard constraint is violated
- scope is unrealistic
- required information is missing
- an upstream artifact is invalid
- downstream artifacts conflict with an upstream artifact

The Judge identifies the affected outputs.

The orchestrator then triggers targeted regeneration.

The Judge itself does not directly mutate canonical state.

---

# 23. Final Dependency Graph

The recommended V1 graph is:

```text
                 ORIGINAL PROJECT INPUT
                          │
                          ▼
                    IDEA AGENT
                          │
                          ▼
                    SCOPE AGENT
                          │
                          ▼
               PROJECT PROFILE AGENT
                          │
             ┌────────────┼─────────────┐
             │            │             │
             ▼            ▼             ▼
       TECHNOLOGY      FEATURES       MVP
          AGENT          AGENT       AGENT
                                        │
                                      Tavily
             │            │             │
             └────────────┼─────────────┘
                          ▼
                 SPECIFICATION AGENT
                          │
                          ▼
                 TIMELINE AGENT
                          │
                          ▼
                    RISK AGENT
                          │
                          ▼
                     TASK AGENT
                          │
                          ▼
                  MILESTONE AGENT
                          │
                          ▼
                    README AGENT
                          │
                          ▼
                   QA / JUDGE AGENT
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
               PASS                FAIL
                │                   │
                ▼                   ▼
         APPROVED BLUEPRINT    TARGETED REGENERATION
                                      │
                                      ▼
                                  RE-VALIDATE
                                      │
                                      ▼
                                  QA / JUDGE
```

---

# 24. Parallel Execution

Parallel execution is allowed where dependencies do not require one output to exist first.

## Stage 1

Sequential:

```text
Idea
→ Scope
→ Project Profile
```

Reason: each stage enriches the understanding needed by the next.

## Stage 2

After Project Profile:

```text
Technology Agent
Features Agent
MVP Agent
```

can execute in parallel.

MVP Agent may perform Tavily research independently.

## Stage 3

```text
Features + Technology + MVP
→ Specification
```

Specification waits for the relevant upstream outputs.

## Stage 4

```text
Specification
→ Timeline
```

Timeline should use the detailed project definition.

## Stage 5

```text
Timeline
→ Risk
```

The V1 recommendation is to let Risk use the final timeline because schedule pressure is itself an important risk input.

## Stage 6

```text
Risk + Timeline + all detailed project definition
→ Task
```

## Stage 7

```text
Tasks + Timeline
→ Milestone
```

## Stage 8

```text
All major approved outputs
→ README
```

## Stage 9

```text
Complete Blueprint
→ QA/Judge
```

---

# 25. Why Some Agents Are Sequential

Sequential execution is used when an agent's reasoning depends materially on another agent's result.

Examples:

### Scope depends on Idea

The system should know what the refined project is before deciding its realistic boundaries.

### Specification depends on Features

The system cannot specify behavior for features that have not been defined.

### Task depends on Timeline/Risk

Executable tasks should account for schedule and risk constraints.

### Milestone depends on Tasks

Milestones should represent meaningful groups of actual work.

### README depends on the Blueprint

The README must represent the approved project rather than incomplete intermediate outputs.

### QA depends on everything

The Judge cannot evaluate the complete blueprint until its required artifacts exist.

---

# 26. Agent Context Strategy

The user's requirement was that agents receive the content necessary to generate effective responses.

The final rule is:

> **Every agent receives a purpose-built context package containing all information materially relevant to its responsibility.**

Not too little.

Not everything blindly.

---

# 27. Common Context

Most agents may receive:

- project ID
- project version
- project type
- complexity
- student skill level
- goals
- constraints
- relevant assessment results
- authorized mentor/group context where applicable
- execution metadata
- upstream outputs required by that agent

---

# 28. Context Package Levels

## Level 1 — Identity

- project ID
- student/project relationship
- project version
- project type
- complexity
- student skill

## Level 2 — Project Understanding

- project profile
- problem
- solution
- objective
- users
- goals
- constraints
- scope

## Level 3 — Domain Outputs

Only relevant outputs are included.

Examples:

Technology Agent:

- project profile
- scope
- student skill
- features/MVP when available
- technical requirements

Specification Agent:

- project profile
- scope
- features
- technology
- MVP

Risk Agent:

- project profile
- scope
- technology
- MVP
- timeline
- dependencies
- external services

Task Agent:

- project profile
- scope
- features
- specifications
- MVP
- technology
- timeline
- risks

## Level 4 — Evidence

Only when relevant:

- RAG results
- Tavily research
- GitHub data
- uploaded reference material

## Level 5 — Execution State

- execution ID
- generation version
- previous attempt
- retry count
- dependency status
- validation errors
- prior output version

---

# 29. Context Compilation Layer

To prevent unnecessary context growth, the orchestrator should construct agent-specific context packages.

Conceptually:

```text
Canonical Project State
        +
Relevant Upstream Outputs
        +
Relevant Evidence
        +
Execution Metadata
        ↓
Context Compiler
        ↓
Agent-Specific Context Package
        ↓
Agent
```

This becomes especially important for:

- README Agent
- QA/Judge Agent
- large projects
- projects with many uploaded documents
- projects with large RAG collections

---

# 30. Context Priority

When information conflicts, agents should use the following priority:

1. current canonical project state
2. latest approved upstream structured output
3. validated project documents
4. authorized project-specific RAG evidence
5. external web evidence
6. model general knowledge

External web research must not silently override canonical project requirements.

---

# 31. RAG Architecture

RAG is infrastructure, not an agent.

Pipeline:

```text
Project File Upload
      ↓
Parsing
      ↓
Chunking
      ↓
Embedding
      ↓
Project-Scoped Vector Storage
      ↓
Authorized Retrieval
      ↓
Agent Context
```

RAG can support agents with:

- uploaded project files
- references
- generated documents
- technical/project knowledge

## Isolation

Project A must never retrieve Project B's content.

Authorization must be enforced before retrieval.

---

# 32. Tavily Architecture

Tavily is a controlled external research capability.

V1 primary owner:

> **MVP Agent**

Tavily results are treated as external evidence.

They should be stored/associated with the relevant execution where provenance is useful.

The final MVP remains a reasoning result based on:

- project requirements
- student constraints
- canonical project state
- current external evidence

---

# 33. GitHub Architecture

GitHub remains a deterministic integration/service.

Agents can receive relevant GitHub information for reasoning about:

- repository context
- activity
- implementation progress
- project status

The GitHub service owns API communication and authorization.

---

# 34. Structured Agent Outputs

Agents should produce validated structured outputs whenever their results feed another component.

Preferred flow:

```text
Agent
  ↓
Structured Pydantic Output
  ↓
Schema Validation
  ↓
Persistence
  ↓
Document Renderer
  ↓
Markdown File
```

This improves:

- reliability
- testing
- retryability
- versioning
- downstream consistency
- UI integration

---

# 35. Document Ownership

| Document | Primary Owner |
|---|---|
| Project Profile | Project Profile Agent |
| Technology Stack | Technology Agent |
| Features | Features Agent |
| Specifications | Specification Agent |
| MVP Definition | MVP Agent |
| Project Duration | Timeline Agent |
| Risk Documentation | Risk Agent |
| Tasks | Task Agent |
| Milestones | Milestone Agent |
| README | README Agent |

There is **no generic Documentation Agent**.

---

# 36. Project Blueprint Document Set

The generated Blueprint contains:

1. Project Profile
2. Technology Stack
3. Features & Specifications
4. MVP Definition
5. Project Duration
6. Risk Documentation
7. README
8. Tasks & Milestones

The actual underlying structured outputs may be stored separately even when the UI presents combined Markdown documents.

---

# 37. Canonical Source of Truth

PostgreSQL/Supabase remains authoritative for structured project state.

Canonical entities include:

- Project
- Phase
- Milestone
- Task
- Risk
- Health
- Progress
- Deadline
- document metadata
- agent execution metadata

Markdown documents are representations of the canonical state.

They are not the source of truth.

---

# 38. Deterministic Project State

The state chain remains:

```text
Task completion
      ↓
Milestone completion
      ↓
Progress
      ↓
Phase
      ↓
Health
```

The AI may:

- explain state
- recommend action
- identify problems
- suggest changes

The AI may not arbitrarily rewrite these deterministic calculations.

---

# 39. Document Versioning

Every generated document should track:

- document ID
- project ID
- document type
- version
- generation status
- generation context/version
- created timestamp
- updated timestamp
- active/current version
- originating agent
- execution ID
- failure details where applicable

---

# 40. Generation States

Recommended states:

- PENDING
- RUNNING
- COMPLETED
- FAILED
- RETRYING
- SKIPPED
- INVALIDATED

These states apply to agent executions and/or document-generation records as appropriate.

---

# 41. Partial Generation Recovery

Example:

```text
Idea              ✓
Scope             ✓
Project Profile   ✓
Technology        ✓
Features          ✓
Specification     ✗
MVP               ✓
Timeline          —
Risk              —
Task              —
Milestone         —
README            —
```

When Retry is requested:

1. inspect the previous execution
2. identify successful outputs
3. identify failed outputs
4. identify not-started outputs
5. inspect failure reasons
6. compare project versions
7. check dependency validity
8. preserve valid outputs
9. retry failed work
10. regenerate affected downstream outputs
11. continue remaining workflow
12. run QA again

---

# 42. Project Change Handling

No dedicated Change Impact Agent is created.

The solution is:

> **Orchestrator + dependency graph + agent-specific reasoning + versioning**

Example:

Student changes:

> "Add real-time collaboration."

The system identifies affected outputs through dependency relationships.

Potentially affected:

- Scope
- Technology
- Features
- Specifications
- MVP
- Timeline
- Risks
- Tasks
- Milestones
- README

Only affected outputs should be regenerated where safely possible.

If the change is fundamental, a broader regeneration is performed.

---

# 43. Why No Change Impact Agent

This directly follows the user's decision.

A dedicated Impact Agent would introduce a broad meta-responsibility that overlaps orchestration and every downstream agent.

Instead:

- orchestrator determines dependency relationships
- versioning identifies stale outputs
- each specialized agent regenerates its own responsibility
- QA verifies the resulting system

This preserves the one-agent-one-role principle.

---

# 44. Retry Strategy

Retries are targeted rather than blind.

Before retrying, the system determines:

- transient vs permanent failure
- schema validation failure
- dependency failure
- provider failure
- external research failure
- project state change
- stale output
- invalid downstream dependency

---

# 45. Failure Categories

## Transient Failure

Examples:

- timeout
- provider failure
- rate limit
- network problem

Action:

Retry according to provider/retry policy.

## Structured Output Failure

Examples:

- missing required field
- invalid enum
- malformed JSON
- schema violation

Action:

Retry with validation feedback.

## Dependency Failure

Example:

Specification cannot run because Features is invalid.

Action:

Repair upstream dependency first.

## State/Version Failure

Example:

Project changed while generation was running.

Action:

Invalidate affected outputs and regenerate against the current project version.

---

# 46. Consistency Invariant

The most important Blueprint invariant is:

> **All active generated documents must represent the same canonical project state/version.**

The system must never leave:

- new Features + old Specifications
- new Technology + old Tasks
- new Scope + old MVP
- new Timeline + old README

as simultaneously active contradictory artifacts.

---

# 47. QA Feedback Loop

Final workflow:

```text
Generation
   ↓
Validation
   ↓
QA/Judge
   ↓
Decision
```

### PASS

```text
Approved Blueprint
```

### MINOR ISSUES

```text
Record recommendations
```

### CORRECTABLE ISSUES

```text
Identify affected outputs
        ↓
Targeted regeneration
        ↓
Validation
        ↓
QA again
```

### FUNDAMENTAL FAILURE

```text
Find earliest invalid dependency
        ↓
Regenerate dependency chain
        ↓
Validation
        ↓
QA again
```

---

# 48. Human Intervention

The system must not regenerate indefinitely.

Human intervention may be required when:

- repeated failure occurs
- critical contradictions remain
- project requirements remain ambiguous
- external information is unavailable
- model outputs remain invalid
- regeneration causes major scope changes
- retry policy is exhausted

The UI should show:

- failure reason
- affected agent
- affected documents
- retry attempts
- dependency impact
- recommended action

---

# 49. Agent Execution Record

Each execution should record:

- execution ID
- project ID
- agent
- execution version
- input context/version
- start time
- end time
- status
- model
- provider
- token usage
- latency
- retry count
- error
- output version

This data supports the Admin AI Observatory.

---

# 50. Agent Observability

LangSmith can provide detailed AI traces.

GrowFlow's own database should also maintain durable execution records.

Admin can observe:

- executions
- success/failure
- duration
- retries
- tokens
- model/provider
- errors
- validation failures
- QA scores
- regeneration frequency

The approved Admin privacy model remains in force:

> Default metadata-only visibility; controlled authorized investigation for legitimate incidents, with investigation access audit logged.

---

# 51. Authorization Boundary

Agents never receive unrestricted access to the database.

Preferred pattern:

```text
Agent
  ↓
Authorized Tool / Service
  ↓
Authorization Check
  ↓
Scoped Data
  ↓
Agent
```

This protects:

- student isolation
- group isolation
- project isolation
- role boundaries
- RAG isolation

---

# 52. Student AI Boundary

Student AI can reason over:

- current project state
- project documents
- project-specific RAG
- GitHub information
- technical knowledge
- approved tools
- relevant agent outputs

Normal conversation does not mutate project state.

State-changing actions require explicit confirmation.

---

# 53. Mentor AI Boundary

Mentor AI can reason over authorized:

- groups
- students
- projects
- project state
- risks
- progress
- relevant documents

It cannot bypass:

- group membership
- student access
- project authorization
- RAG isolation

---

# 54. Admin AI Boundary

Admin AI/observability can access the metadata and operational information permitted by the finalized Admin privacy model.

Default:

- usage
- status
- performance
- execution metadata
- errors
- system health
- audit events

Controlled investigation may expose additional information only when justified, scoped, authorized, and audited.

---

# 55. Final End-to-End Blueprint Workflow

```text
Student Project Input
        │
        ▼
15-Question Assessment
        │
        ▼
Idea Agent
        │
        ▼
Scope Agent
        │
        ▼
Project Profile Agent
        │
        ├──────────────┬──────────────┐
        ▼              ▼              ▼
 Technology        Features          MVP
 Agent             Agent             Agent
                                      │
                                    Tavily
        │              │              │
        └──────────────┼──────────────┘
                       ▼
              Specification Agent
                       │
                       ▼
                Timeline Agent
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
                 QA / Judge Agent
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
           PASS                 FAIL
             │                   │
             ▼                   ▼
       Approved Blueprint   Targeted Regeneration
                                 │
                                 ▼
                            QA / Judge
```

---

# 56. Final Architectural Rules

1. GrowFlow uses specialized agents.
2. V1 contains 13 agents including the explicitly retained Project Profile Agent.
3. Idea and Scope remain separate agents.
4. Idea + Scope are combined only when constructing Project Profile documentation/context.
5. Technology, Features, and MVP can execute in parallel after Project Profile.
6. MVP Agent is the primary V1 consumer of Tavily.
7. Features and Specifications remain separate.
8. Timeline and Milestone remain separate.
9. Task and Milestone remain separate.
10. README remains an agent.
11. README receives a compiled context package rather than blindly receiving every raw document.
12. Project Profile remains an agent.
13. No dedicated Change Impact Agent exists.
14. Orchestration handles dependency/impact propagation.
15. QA/Judge supports both judge-only and targeted-regeneration outcomes.
16. Agents do not own deterministic project state.
17. PostgreSQL/Supabase remains the structured source of truth.
18. Markdown files are representations of canonical state.
19. Agents should return validated structured outputs.
20. RAG is infrastructure, not an agent.
21. Tavily is a controlled research tool.
22. GitHub is a deterministic integration/service.
23. Agent access is project-scoped and authorization-aware.
24. Retry is targeted and version-aware.
25. Active documents must remain state-consistent.
26. Infinite regeneration is prohibited; human intervention is a valid terminal state.
27. Agent executions are observable and persisted.
28. Privacy and authorization boundaries apply to all agent/tool calls.

---

# 57. Final Decision Log — Questions and Solutions

This section records every architectural question raised during finalization and the solution adopted.

## A. Agent Count

### Question

Do all 12 proposed agents deserve to exist?

### Decision

**Yes.**

The specialized responsibilities are retained.

### Additional clarification

Because Project Profile was explicitly retained as an agent, the finalized architecture contains **13 agents**, not 12.

---

## B. Idea + Scope Boundary

### Question

Should Idea and Scope remain separate or partially merge?

### Decision

**Remain separate.**

### Solution

Their outputs are combined only for Project Profile/documentation context.

This gives:

```text
Idea reasoning
+
Scope reasoning
↓
Project Profile
```

This avoids creating an overly broad Idea/Scope agent.

---

## C. Timeline vs Milestone

### Question

Should Timeline and Milestone be separate?

### Decision

**Yes.**

### Solution

Timeline owns temporal planning.

Milestone owns meaningful project checkpoints.

They share information but have different responsibilities.

---

## D. Task + Milestone

### Question

Should Task and Milestone become one planning agent?

### Decision

**No. Keep them separate.**

### Solution

Task Agent creates executable work.

Milestone Agent creates meaningful completion checkpoints from the task plan.

This preserves one-agent-one-role boundaries.

---

## E. README Agent

### Question

Should README be an agent or a deterministic renderer?

### Decision

**Keep README as an agent.**

### Problem identified

README requires information from almost the entire Blueprint, creating a potentially large context.

### Solution

Introduce a deterministic **Context Compilation Layer**.

Instead of:

```text
Every raw document
→ README Agent
```

use:

```text
Canonical State
+
Relevant structured outputs
+
Summaries
+
References
→ Context Compiler
→ README Context Package
→ README Agent
```

This gives the README Agent enough information without unnecessary context bloat.

---

## F. Project Profile

### Question

Should Project Profile be an agent or deterministic transformation?

### Decision

**Keep Project Profile as an agent.**

### Solution

The Project Profile Agent consolidates:

- original project information
- assessment
- Idea output
- Scope output
- student context
- constraints

It produces the normalized/enriched project representation used downstream.

It does not independently redesign the project.

---

## G. Change Impact Agent

### Question

Should a dedicated Project Change / Impact Agent exist?

### Decision

**No.**

### Solution

Use:

- canonical project versioning
- dependency graph
- orchestrator
- invalidation logic
- agent-specific regeneration
- QA

This avoids creating a broad meta-agent that overlaps every other agent.

---

## H. QA/Judge Behavior

### Question

Should QA only judge or also trigger regeneration?

### Decision

**Both, based on triggers.**

### Solution

QA can:

- judge only when the result is acceptable
- identify targeted regeneration when a correctable issue exists
- identify the earliest invalid dependency for fundamental failures

The orchestrator performs the actual workflow transition.

QA does not directly mutate canonical state.

---

## I. Agent Dependencies

### Question

Which agents can run in parallel and which must wait?

### Decision

Use a dependency-aware execution graph.

### Solution

Sequential:

```text
Idea
→ Scope
→ Project Profile
```

Parallel after Project Profile:

```text
Technology
Features
MVP
```

Then:

```text
Specification
→ Timeline
→ Risk
→ Task
→ Milestone
→ README
→ QA
```

This balances performance with correctness.

---

## J. Agent Memory / Context

### Question

What context should each agent receive?

### Decision

Each agent receives a purpose-built context package containing all information materially required for its task.

### Solution

Use:

```text
Canonical State
+
Relevant Upstream Outputs
+
Relevant Evidence
+
Execution Metadata
↓
Context Compiler
↓
Agent Context
```

Agents do not receive irrelevant data merely because it exists.

---

# 58. Final Status

| Part | Status |
|---|---|
| Part 1 — Mentor Side | 🟢 FROZEN |
| Part 2 — Student Side | 🟢 AGREED / FINAL CANDIDATE |
| Part 3 — Admin Side | 🟢 FROZEN |
| Part 4 — AI Agent Architecture | 🟢 **FROZEN** |

---

# 59. Part 4 Completion Statement

The GrowFlow V1 AI architecture is now defined as a **specialized, dependency-aware, version-aware multi-agent system**.

The architecture does not rely on an oversized general-purpose documentation agent. Instead, project intelligence is distributed across specialized agents with clear ownership.

The system combines:

- specialized AI reasoning
- deterministic orchestration
- structured outputs
- canonical project state
- project-scoped RAG
- controlled Tavily research
- targeted regeneration
- QA-based quality gates
- execution observability
- strict authorization boundaries

This architecture is now ready to serve as the foundation for the next design phase: **detailed agent contracts and workflow implementation planning**.
