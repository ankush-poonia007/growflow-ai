# GrowFlow — Part 5E: Application Integration & Cross-Role Architecture

## Final Specification — FROZEN

**Status:** FINAL / FROZEN  
**Part:** 5E — Application Integration & Cross-Role Architecture  
**Product:** GrowFlow  
**Depends On:**  
- Part 4 — AI Agent Architecture
- Part 5A — Application Foundation
- Part 5B — Student Application Architecture
- Part 5C — Mentor Application Architecture
- Part 5D — Admin Application Architecture

---

# 1. Purpose

Part 5E defines how the complete GrowFlow application operates as one integrated system.

Parts 5A–5D define the individual application experiences:

- Student
- Mentor
- Admin

Part 5E defines the contracts between them.

It establishes the integration architecture for:

- cross-role data flow
- canonical project state
- events
- notifications
- activity
- project lifecycle
- project changes
- AI agents
- document generation
- RAG
- GitHub monitoring
- authorization
- streaming
- failure/recovery
- observability
- cross-role boundaries

The objective is to prevent the application from becoming a collection of independently implemented features that contradict each other.

---

# 2. Final Cross-Role Philosophy

GrowFlow has three application responsibilities:

```text
Student = BUILD
Mentor  = SUPERVISE
Admin   = GOVERN
```

The systems underneath them are shared.

```text
                    ┌─────────────────┐
                    │     STUDENT     │
                    │     BUILD       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ PROJECT SYSTEM  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   AI AGENTS               RAG                GITHUB
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  BACKEND/API    │
                    │   SERVICES      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
          NOTIFICATION    ACTIVITY      OBSERVABILITY
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
         ┌─────────┐                    ┌─────────┐
         │ MENTOR  │                    │  ADMIN  │
         │SUPERVISE│                    │ GOVERN  │
         └─────────┘                    └─────────┘
```

The applications consume shared canonical services rather than maintaining competing versions of project state.

---

# 3. Core Architectural Rule

The most important integration rule is:

> **The database and deterministic domain services own canonical application state.**

AI agents do not become the source of truth.

Generated Markdown documents do not become the source of truth.

Frontend state does not become the source of truth.

Activity records do not become the source of truth.

The canonical state lives in structured backend persistence.

---

# 4. Canonical State vs Representation

GrowFlow distinguishes between:

## Canonical State

Structured, authoritative data such as:

- user
- role
- group
- project definition
- project instance
- project profile
- assessment
- technology
- feature
- specification
- MVP
- duration
- risk
- task
- milestone
- progress
- phase
- health
- GitHub connection
- notification
- help request
- mentor note
- generation metadata

## Representations

Derived or generated representations include:

- Markdown documents
- README
- UI summaries
- dashboards
- charts
- AI explanations
- activity projections
- analytics
- notifications
- generated previews

Representations can be regenerated from canonical state.

---

# 5. Cross-Role Data Flow

The application uses deterministic domain services as the central coordination point.

Example:

```text
Student completes Task
        ↓
Task Service
        ↓
Validation
        ↓
Database Transaction
        ↓
Task state updated
        ↓
Milestone recalculated
        ↓
Project progress recalculated
        ↓
Phase recalculated
        ↓
Health recalculated
        ↓
Activity Event
        ↓
Notification Evaluation
        ↓
Analytics / Observability
```

The Mentor and Admin applications consume the resulting state/events according to their permissions.

The Student receives the updated project state.

---

# 6. Event-Driven Integration Model

GrowFlow uses a **lightweight internal domain-event architecture** for cross-feature and cross-role coordination.

This does not require a heavyweight distributed event platform by default.

The initial implementation should use the existing backend/database infrastructure and a reliable background-processing mechanism where asynchronous delivery is required.

Heavy infrastructure such as Kafka should not be introduced unless scale or reliability requirements later justify it.

---

# 7. Domain Event Principles

A domain event represents something that has already happened.

Examples:

```text
TaskCompleted
TaskBlocked
MilestoneCompleted
ProjectProgressChanged
ProjectPhaseChanged
ProjectHealthChanged
RiskCreated
RiskUpdated
RiskResolved
HelpRequestCreated
HelpRequestUpdated
HelpRequestResolved
MentorNoteCreated
BlueprintGenerationStarted
BlueprintGenerationCompleted
BlueprintGenerationFailed
BlueprintRegenerationStarted
BlueprintRegenerationCompleted
AgentExecutionStarted
AgentExecutionCompleted
AgentExecutionFailed
GitHubActivityDetected
DocumentGenerationCompleted
DocumentGenerationFailed
RAGIndexingCompleted
RAGIndexingFailed
SecurityEventDetected
AccountStatusChanged
```

Events should not be treated as arbitrary messages.

Each event has a defined meaning and schema.

---

# 8. Event Structure

A canonical event should contain appropriate fields such as:

```text
event_id
event_type
occurred_at
actor_id
actor_role
resource_type
resource_id
project_id
group_id
visibility
metadata
correlation_id
```

Not every event requires every field.

Sensitive data must not be embedded into events unnecessarily.

Prefer IDs and operational metadata over private content.

---

# 9. Event Lifecycle

The standard flow is:

```text
Domain Action
    ↓
Validation
    ↓
Database Transaction
    ↓
State Change
    ↓
Domain Event
    ↓
Event Handlers
    ├── Activity
    ├── Notifications
    ├── Analytics
    ├── Observability
    └── Other permitted workflows
```

The state change must succeed before an event claiming that the state changed is emitted.

---

# 10. Event Reliability

Events that affect important downstream behavior must be delivered reliably.

The implementation should support:

- unique event IDs
- idempotent handlers
- retry handling
- failure logging
- correlation IDs
- dead-letter/error handling where appropriate
- duplicate-event protection

Handlers must be safe to retry.

---

# 11. Event Ownership

The domain service that owns the state change is responsible for producing the event.

Examples:

| Event | Primary Owner |
|---|---|
| TaskCompleted | Task Service |
| MilestoneCompleted | Milestone/Project Service |
| ProjectHealthChanged | Project Health Service |
| RiskCreated | Risk Service |
| HelpRequestCreated | Help Request Service |
| BlueprintGenerated | Blueprint/Generation Service |
| AgentExecutionFailed | Agent Execution Service |
| GitHubActivityDetected | GitHub Integration Service |
| AccountStatusChanged | Account/Admin Service |

No frontend should create authoritative domain events.

---

# 12. Canonical Project Lifecycle

All applications use the same canonical project lifecycle:

```text
IDEA
  ↓
ASSESSMENT
  ↓
BLUEPRINT
  ↓
PLANNING
  ↓
IMPLEMENTATION
  ↓
TESTING
  ↓
DEPLOYMENT
  ↓
COMPLETED
```

The exact current phase is determined from canonical project state.

AI may recommend changes or identify issues, but deterministic project services own lifecycle transitions.

---

# 13. Project Lifecycle Rules

A project does not advance simply because an AI agent says it should.

A phase transition must satisfy the applicable deterministic conditions.

Examples:

- Assessment completion is based on assessment state.
- Blueprint phase completion depends on valid blueprint outputs.
- Planning depends on valid tasks/milestones/planning state.
- Implementation depends on execution state.
- Testing depends on testing completion state.
- Deployment depends on deployment state.
- Completed requires the project's defined completion conditions.

The exact transition predicates are implementation details to be finalized in the backend/domain phase, but the ownership principle is frozen here.

---

# 14. Task → Milestone → Progress → Phase → Health

This chain is canonical:

```text
Task
 ↓
Milestone
 ↓
Progress
 ↓
Phase
 ↓
Health
```

Changes propagate through deterministic services.

For example:

```text
Task becomes COMPLETED
        ↓
Milestone completion recalculated
        ↓
Project progress recalculated
        ↓
Phase eligibility recalculated
        ↓
Project health recalculated
```

AI does not arbitrarily overwrite this chain.

---

# 15. Project Health

Project health is a deterministic application state derived from available project signals.

Possible signals include:

- task delays
- blocked tasks
- milestone status
- deadline proximity
- inactivity
- risks
- GitHub activity
- implementation progress
- technology mismatch
- deployment state
- testing state

AI may explain health and recommend action, but the canonical health calculation remains controlled by deterministic application logic.

---

# 16. At-Risk Integration

The Mentor At-Risk system and Admin monitoring consume canonical project-health/risk signals.

Example:

```text
Project signal changes
       ↓
Health / Risk Service
       ↓
At-risk state recalculated
       ↓
Activity Event
       ↓
Notification rules
       ↓
Mentor dashboard
       ↓
Admin platform monitoring
```

Mentor receives project/group-relevant information.

Admin receives platform-level operational visibility.

Student receives relevant project-level information.

---

# 17. Notification Architecture

GrowFlow uses one centralized notification service.

All roles consume notifications through role-appropriate filtering.

The notification service is responsible for:

- creating notifications
- determining recipients
- checking preferences
- assigning priority
- tracking read/unread state
- deduplication where necessary
- delivery state
- optional email delivery

---

# 18. Notification Channels

The initial channels are:

### In-App

Mandatory.

### Email

Optional/configurable.

The system should not require email for normal application operation.

Additional channels may be added later if justified.

---

# 19. Notification Flow

```text
Domain Event
    ↓
Notification Rules
    ↓
Recipient Authorization
    ↓
Notification Created
    ↓
In-App Delivery
    ↓
Optional Email Delivery
```

Notifications must never bypass authorization.

---

# 20. Student Notifications

Examples:

- mentor note
- help-request status change
- blueprint generation result
- blueprint regeneration result
- important project risk
- blocked task
- milestone event
- project health warning
- important deadline warning
- GitHub monitoring event
- relevant AI recommendation
- project-definition update notification

---

# 21. Mentor Notifications

Examples:

- student help request
- project becoming at risk
- important student project change
- blocked task requiring attention
- inactivity warning
- important project event
- project-definition update affecting assigned students
- major blueprint/project event

---

# 22. Admin Notifications

Examples:

- system failures
- elevated API errors
- AI provider incidents
- agent failure spikes
- RAG failures
- storage problems
- OAuth failures
- GitHub integration degradation
- security alerts
- major platform anomalies

Admin notifications should remain operationally focused.

---

# 23. Notification Preferences

Users may control permitted notification preferences.

Preferences should distinguish:

- notification type
- channel
- priority
- enabled/disabled

Critical security/system notifications may have mandatory delivery behavior for Admin where appropriate.

---

# 24. Activity Architecture

GrowFlow uses **one canonical activity/event system**.

Student, Mentor, and Admin do not maintain independent activity databases.

Instead:

```text
Canonical Event
      ↓
Activity Projection
      ↓
Role / Resource Filtering
      ↓
UI Activity Timeline
```

---

# 25. Activity Record

A canonical activity record can contain:

```text
activity_id
event_id
actor_id
actor_role
event_type
resource_type
resource_id
project_id
group_id
timestamp
visibility
summary
metadata
```

Private content should not be stored in activity summaries unless explicitly required.

---

# 26. Student Activity

Student sees relevant activity for:

- their project
- their tasks
- milestones
- blueprint
- documents
- risks
- GitHub monitoring
- mentor interactions
- help requests
- important AI/project events

---

# 27. Mentor Activity

Mentor sees activity for authorized:

- groups
- students
- project definitions
- project instances

Mentor does not automatically see unrelated platform activity.

---

# 28. Admin Activity

Admin can see platform-level activity appropriate to their role.

Admin activity views distinguish:

- normal platform activity
- administrative activity
- investigation activity

This separation is required for accountability.

---

# 29. Project Change Workflow

Project changes require a dedicated controlled workflow.

Examples of meaningful changes:

- problem
- proposed solution
- objective
- scope
- technology
- features
- duration
- constraints
- assumptions
- project context

---

# 30. Project Change Flow

The canonical process is:

```text
Change Requested
       ↓
Impact Analysis
       ↓
Affected Components Identified
       ↓
User Review / Confirmation
       ↓
Regeneration of Affected Outputs
       ↓
Validation
       ↓
QA / Judge
       ↓
Accept
       ↓
Persist Canonical State
       ↓
Regenerate Required Documents
       ↓
Emit Events
       ↓
Notifications / Activity
```

---

# 31. Impact Analysis

Impact analysis determines what may become invalid.

Potentially affected components:

- Project Profile
- Technology Stack
- Features
- Specifications
- MVP
- Duration
- Risks
- Tasks
- Milestones
- README
- Blueprint
- project phase/planning state where applicable

Not every change affects every component.

The system should regenerate only affected outputs when safe.

---

# 32. Broad Changes

If the change affects the foundational project understanding, the system may require broader blueprint regeneration.

Examples:

- completely different problem
- major solution change
- major scope change
- major technology change
- major feature restructuring

The system must avoid leaving contradictory active documents.

---

# 33. Project Definition Changes

Mentor project-definition changes follow the previously frozen rule.

Existing student instances are not automatically migrated.

```text
Project Definition Updated
       ↓
Existing Student Instances
       └── Unchanged
       ↓
New Assignments
       └── Receive Updated Definition
       ↓
Affected Existing Students
       └── Receive Notification
```

An existing student may independently review/adopt the change through the approved project-change workflow.

---

# 34. AI Agent Integration

The frontend does not directly orchestrate individual agents.

The canonical flow is:

```text
Frontend
   ↓
FastAPI API
   ↓
Application / Generation Service
   ↓
LangGraph Orchestrator
   ↓
Agent Execution
   ↓
Structured Output
   ↓
Validation
   ↓
QA / Judge
   ↓
Deterministic Persistence
   ↓
Document Rendering
   ↓
Event
   ↓
Frontend Update
```

---

# 35. Agent Responsibilities

The frozen 12-agent system is:

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

Idea + Scope may be coordinated closely for documentation generation, but they remain conceptually distinct responsibilities unless an implementation decision explicitly merges execution.

---

# 36. Agent Orchestration

The LangGraph orchestrator owns:

- dependency ordering
- parallelism
- execution state
- context preparation
- retries
- recovery
- routing
- QA gating
- targeted regeneration
- failure handling

Agents should not independently decide the overall workflow.

---

# 37. Agent Context Strategy

Agents receive only the context relevant to their role.

Context may include:

- project profile
- assessment
- previous agent outputs
- relevant structured state
- relevant documents
- relevant RAG results
- relevant web research
- user constraints
- previous validation results

The system should avoid passing the entire project state to every agent unnecessarily.

This reduces:

- token usage
- latency
- irrelevant context
- accidental cross-scope reasoning

---

# 38. Structured Agent Outputs

Agents should preferentially return validated structured outputs.

Example:

```text
Agent
 ↓
Pydantic Schema
 ↓
Validation
 ↓
Orchestrator
```

The backend then persists canonical structured state.

Markdown is rendered from that state where appropriate.

---

# 39. README Agent Exception

The README Agent remains a dedicated agent because the product decision explicitly retains it.

Its context should be assembled from the final authoritative project state and approved outputs rather than blindly passing every intermediate agent transcript.

This keeps README generation manageable and consistent.

---

# 40. QA / Judge Integration

QA/Judge is a first-class gate.

It evaluates:

- completeness
- consistency
- schema validity
- cross-document consistency
- project suitability
- requirements satisfaction
- generated-output quality

When a defined failure trigger occurs, it can initiate targeted regeneration through the orchestrator.

It does not directly bypass deterministic persistence rules.

---

# 41. Agent Failure Recovery

Agent executions must have explicit states.

Example:

```text
QUEUED
RUNNING
VALIDATING
QA
COMPLETED
FAILED
RETRYING
CANCELLED
```

Failures should preserve enough execution metadata to support recovery.

---

# 42. Generation Recovery

When generation fails or resumes:

1. Inspect current generation status.
2. Inspect valid existing outputs.
3. Determine whether relevant project state changed.
4. Reuse valid outputs where safe.
5. Regenerate affected outputs.
6. Run validation.
7. Run QA/Judge.
8. Persist accepted state.
9. Update generation metadata.
10. Emit appropriate events.

No generation process should casually create contradictory active versions.

---

# 43. Generation Metadata

Generation records should track information such as:

```text
generation_id
project_id
generation_type
status
started_at
completed_at
trigger
context_version
input_version
output_version
affected_components
agent_execution_ids
qa_status
failure_reason
retry_count
```

This allows the system to explain what happened during generation.

---

# 44. AI Action Boundary

The architectural rule is:

> **AI may recommend, analyze, explain, generate, and request an action; deterministic services perform authoritative state changes.**

For example:

```text
AI: "This task appears complete."
        ↓
AI recommendation / proposed action
        ↓
Confirmation if required
        ↓
Task Service
        ↓
Validation
        ↓
Database transaction
        ↓
TaskCompleted
```

The AI never directly writes arbitrary project state.

---

# 45. AI Streaming Architecture

GrowFlow uses streaming for long-running AI responses and executions.

The initial mechanism is:

> **Server-Sent Events (SSE)**

WebSockets are not required unless later UX requirements justify them.

---

# 46. AI Streaming Flow

```text
Frontend
   ↓
Generation Request
   ↓
FastAPI
   ↓
execution_id
   ↓
SSE Connection
   ↓
Orchestrator
   ↓
Agent Events
   ↓
Validation / QA Events
   ↓
Completion / Failure
```

The frontend can display:

- current stage
- current agent
- progress information
- generated content
- validation state
- QA state
- errors
- completion

---

# 47. Streaming UX Rule

The previously frozen AI streaming behavior remains:

1. When a response starts, the viewport focuses the current generated response.
2. The user can scroll away while generation continues.
3. If the user manually leaves the response, the system does not force-scroll them back.
4. Streaming continues independently of viewport position.
5. Completion state remains visible without hijacking the user's scroll position.

---

# 48. Long-Running Execution

Long-running generation must not depend on an open browser connection remaining alive.

The backend should persist execution state.

Therefore:

```text
Browser disconnects
       ↓
Execution continues
       ↓
State persisted
       ↓
User reconnects
       ↓
Current execution status retrieved
```

SSE is a delivery mechanism, not the source of execution state.

---

# 49. Cancellation

Where supported, users may request cancellation of long-running generation.

Cancellation must:

- identify the execution
- validate ownership/authorization
- request orchestrator cancellation
- persist cancellation state
- stop eligible work
- cleanly finalize execution
- emit an execution event

Cancellation must not corrupt canonical project state.

---

# 50. RAG Integration

RAG is project-scoped.

The canonical pipeline is:

```text
Upload
  ↓
Parse
  ↓
Chunk
  ↓
Embed
  ↓
Vector Store
  ↓
Project-Scoped Retrieval
  ↓
Authorized AI Tool
  ↓
Agent / AI Mentor
```

---

# 51. RAG Authorization

Every retrieval must enforce:

- authenticated user
- role
- project scope
- resource ownership/relationship
- document access permissions

The AI model itself does not determine authorization.

The retrieval/tool layer enforces it.

---

# 52. RAG and Cross-Role Access

### Student

Can retrieve documents belonging to their authorized project scope.

### Mentor

Can retrieve documents within authorized student/group/project scope.

### Admin

Normal Admin access is metadata-first.

Protected content requires the controlled investigation process where applicable.

---

# 53. GitHub Integration

GitHub is monitoring-only in the current architecture.

The integration may retrieve authorized:

- repository information
- commits
- branches where supported
- pull requests
- issues where supported
- activity signals
- relevant project activity

GrowFlow does not use the integration for repository management.

---

# 54. GitHub Data Flow

```text
GitHub
   ↓
Authorized Integration
   ↓
Project-scoped Data
   ↓
Monitoring / Analysis
   ↓
Project Signals
   ↓
Activity / Health / Notifications
```

GitHub data must not bypass project authorization.

---

# 55. Human Mentor Communication

Human Mentor communication remains separate from AI Mentor interaction.

Supported mechanisms:

- Mentor Notes
- Help Requests

Help Requests use:

```text
OPEN
 ↓
IN_PROGRESS
 ↓
RESOLVED
```

Mentor Notes do not directly mutate project state.

---

# 56. Blocked Task Escalation

A blocked task can produce:

```text
Task becomes BLOCKED
       ↓
Student receives project-level indication
       ↓
AI Mentor can help troubleshoot
       ↓
Student may request Mentor help
       ↓
Help Request
       ↓
Mentor notification
       ↓
Mentor responds
       ↓
Help Request resolved
```

The Mentor response does not automatically alter task state.

---

# 57. Authorization Architecture

All cross-role interactions follow:

```text
Authentication
      ↓
Role Authorization
      ↓
Resource Authorization
      ↓
Project / Group Scope
      ↓
Action Permission
      ↓
Privacy Policy
      ↓
Tool / Service Execution
      ↓
Audit if Required
```

Frontend restrictions are supplementary.

Backend authorization is authoritative.

---

# 58. Student Scope

A Student normally operates within:

```text
Own Account
   ↓
Own Group Relationship
   ↓
Own Project Instances
   ↓
Own Project Resources
```

A student cannot access another student's project merely by knowing an ID or URL.

---

# 59. Mentor Scope

A Mentor normally operates within:

```text
Mentor Account
   ↓
Owned / Authorized Groups
   ↓
Students in Those Groups
   ↓
Their Authorized Project Instances
```

A Mentor cannot access unrelated students simply by manipulating request parameters.

---

# 60. Admin Scope

Admin has platform-level authority for approved operational information.

Default access includes:

- platform statistics
- basic user information
- group relationships
- project relationships
- project monitoring information
- AI operational metrics
- system health
- audit metadata

Protected private content remains subject to privacy controls.

---

# 61. Admin Investigation Boundary

The controlled investigation process is:

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

The system should never interpret ADMIN role as automatic authorization to inspect every private resource.

---

# 62. AI Tool Authorization

AI tools must enforce authorization independently.

Architecture:

```text
AI / Agent
   ↓
Authorized Tool
   ↓
Identity + Role
   ↓
Resource Scope
   ↓
Privacy Check
   ↓
Data Retrieval
```

Never:

```text
AI → unrestricted SQL
```

Never:

```text
AI → unrestricted vector search
```

Never:

```text
AI → arbitrary project files
```

---

# 63. Global Search Integration

Global search operates through authorized indexed entities.

Search can include:

- students
- mentors
- groups
- project definitions
- project instances
- permitted operational records

Private content is not globally searchable by default.

---

# 64. Observability Integration

All important subsystems produce observability metadata.

The Admin layer can consume:

- API metrics
- database metrics
- AI usage
- agent execution data
- LangSmith traces
- RAG metrics
- document-generation metrics
- GitHub integration metrics
- OAuth metrics
- queue/worker metrics
- security events

---

# 65. Correlation IDs

Cross-system operations should use correlation identifiers.

Example:

```text
User Request
   ↓
request_id
   ↓
generation_id
   ↓
execution_id
   ↓
agent_execution_ids
   ↓
events
   ↓
notifications
   ↓
activity
```

This allows a single user-visible operation to be traced across the backend.

---

# 66. Example End-to-End Blueprint Generation

```text
Student clicks "Generate Blueprint"
        ↓
Frontend
        ↓
FastAPI
        ↓
Authorization
        ↓
Project State Validation
        ↓
Generation Record Created
        ↓
LangGraph Orchestrator
        ↓
Idea / Scope
        ↓
Technology
        ↓
Features / Specification
        ↓
MVP
        ↓
Duration
        ↓
Risk
        ↓
Task / Milestone
        ↓
README
        ↓
QA / Judge
        ↓
Validation
        ↓
Deterministic Persistence
        ↓
Document Rendering
        ↓
BlueprintCompleted Event
        ↓
Activity
        ↓
Notification
        ↓
Analytics / AI Observability
        ↓
Frontend Updated
```

The exact parallel/serial execution order is determined by the frozen agent dependency graph from Part 4.

---

# 67. Example End-to-End At-Risk Flow

```text
Task delay detected
        ↓
Project signals updated
        ↓
Health / Risk Service
        ↓
Project becomes AT_RISK
        ↓
ProjectHealthChanged
        ↓
Activity
        ↓
Notification Rules
        ├── Student notification
        └── Mentor notification
        ↓
Mentor At-Risk Dashboard
        ↓
Admin platform telemetry
```

The AI may explain why the project is at risk and recommend an action.

---

# 68. Example End-to-End Help Request

```text
Student
  ↓
Creates Help Request
  ↓
Help Request Service
  ↓
Database
  ↓
HelpRequestCreated
  ├── Activity
  └── Notification
          ↓
       Mentor
          ↓
     In Progress
          ↓
      Response
          ↓
       Resolved
          ↓
   Student Notification
```

---

# 69. Example End-to-End Project Definition Update

```text
Mentor updates Project Definition
        ↓
Definition Service
        ↓
Validation
        ↓
Persist Definition Version
        ↓
Existing Instances remain unchanged
        ↓
New assignments use new definition
        ↓
Affected existing students identified
        ↓
Student notifications
        ↓
Activity
```

No automatic student blueprint migration occurs.

---

# 70. Example End-to-End Admin Investigation

```text
Admin identifies incident
        ↓
Investigation Request
        ↓
Authorization
        ↓
Minimum Scope Determined
        ↓
Protected Data Inspection
        ↓
Investigation Results
        ↓
Audit Record
```

The inspection must be limited to the approved scope.

---

# 71. Cross-Role Consistency Rules

The following rules are mandatory:

1. There is one canonical project state.
2. Student, Mentor, and Admin do not maintain competing project states.
3. AI does not directly own core state.
4. Events describe completed state changes.
5. Notifications derive from authorized events/rules.
6. Activity derives from canonical events.
7. RAG retrieval is project/resource scoped.
8. GitHub access is project scoped.
9. Admin private-content access is controlled.
10. Frontend authorization is never sufficient.
11. Backend authorization is authoritative.
12. Long-running AI execution state is persisted.
13. Generated documents are representations of canonical state.
14. Existing student instances are not silently migrated when mentor definitions change.
15. Administrative visibility does not imply administrative control over student execution.

---

# 72. Error Handling Across the Application

Every integration boundary should distinguish:

- validation failure
- authorization failure
- not found
- conflict
- dependency failure
- timeout
- provider failure
- rate limit
- processing failure
- generation failure
- partial failure

Errors should be:

- logged appropriately
- correlated
- surfaced to the relevant user
- visible to Admin where operationally relevant
- retryable only where safe

---

# 73. Partial Failure Principle

A failure in one subsystem should not falsely imply that the whole platform failed.

Examples:

- AI provider failure should not corrupt project state.
- Email failure should not invalidate an in-app notification.
- RAG indexing failure should not delete canonical documents.
- GitHub outage should not make the project disappear.
- Analytics failure should not block task completion.

Core transactional state should remain independent from non-critical downstream systems.

---

# 74. Retry Principle

Retries are permitted only for operations that are safe to retry.

Examples:

- AI provider request
- email delivery
- RAG indexing
- background processing
- telemetry submission

State-changing domain operations must use idempotency or transaction safeguards before retry.

---

# 75. Idempotency

Important operations should use idempotency protections.

Examples:

- task completion
- help-request transitions
- notification creation
- agent execution callbacks
- document generation completion
- event handlers

Repeated delivery must not create duplicated state.

---

# 76. Database Transaction Boundary

When a core domain action changes canonical state, related critical state updates should occur within an appropriate transaction.

Example:

```text
Task completion
    ├── task state
    ├── milestone state
    ├── project progress
    └── relevant project state
```

Downstream operations such as email, analytics, or external telemetry should not unnecessarily extend the core transaction.

---

# 77. Background Processing

Asynchronous workers should handle appropriate long-running/non-critical work such as:

- AI execution
- document processing
- embedding
- RAG indexing
- email delivery
- analytics aggregation
- external integration polling
- notification fan-out where appropriate

The exact worker technology will be finalized in the infrastructure/backend architecture phase.

---

# 78. Frontend Integration Rule

Frontend applications consume backend APIs and streams.

They do not:

- calculate authoritative project state independently
- bypass authorization
- write directly to the database
- orchestrate AI agents
- determine privacy permissions
- create authoritative events

Client-side calculations may be used for presentation, but server state remains authoritative.

---

# 79. API Boundary

The application layer should logically separate:

### Identity/Auth APIs

Authentication and authorization.

### Project APIs

Project state and execution.

### Generation APIs

AI generation and orchestration.

### Document APIs

Document retrieval/rendering/download.

### RAG APIs

Authorized indexing/retrieval operations.

### GitHub APIs

Monitoring integration.

### Communication APIs

Notes/help requests/notifications.

### Admin APIs

Platform administration and observability.

---

# 80. API Response Principles

API responses should be:

- typed
- validated
- authorization-aware
- consistent
- versionable where required
- explicit about errors
- free from secrets
- appropriately scoped

Sensitive fields should never be returned merely because they exist in the underlying database model.

---

# 81. Data Versioning

Generated project outputs should have version/context metadata.

This allows the system to determine:

- what generated output corresponds to which project state
- whether an existing document is still valid
- whether regeneration is necessary
- which version passed QA
- what changed between generations

---

# 82. Document Synchronization

The relationship is:

```text
Canonical Structured State
        ↓
Document Renderer
        ↓
Markdown Document
        ↓
Preview / Raw Markdown / Download
```

The UI must not treat a downloaded Markdown file as the authoritative project state.

---

# 83. Download Behavior

The frozen Student document behavior remains:

- View
- Preview
- Raw Markdown
- Download

Download applies to the currently open document.

The same generated document representation can be surfaced to authorized Mentor/Admin views subject to their access scope.

---

# 84. Security Boundary Around Files

File access must validate:

- user identity
- role
- project ownership/relationship
- document permissions
- investigation status where required

Knowing a document ID must never be sufficient for access.

---

# 85. Cross-Role AI Mentor Boundary

### Student AI Mentor

Project-focused assistance.

### Mentor AI

Authorized group/student/project supervision and analysis.

### Admin AI

Platform-wide operational/basic-information intelligence plus authorized investigation support.

These are different AI experiences with different tools and scopes.

They must not share unrestricted tool permissions.

---

# 86. Admin AI Integration

Admin AI can access authorized basic platform information:

- users
- mentors
- students
- groups
- projects
- project instances
- operational metrics
- AI usage
- agent executions
- system health
- RAG operations
- audit metadata

It can then:

```text
Observe
 ↓
Analyze
 ↓
Explain
 ↓
Recommend
```

Protected private content requires the appropriate investigation workflow.

---

# 87. AI Observability Integration

Every meaningful AI execution should contribute operational metadata to the observability layer.

At minimum:

```text
execution_id
request_id
user_id
project_id
agent
model
provider
start_time
duration
status
tokens
retries
validation_status
qa_status
error
```

Where applicable, detailed tracing is integrated with LangSmith.

---

# 88. Cost Integration

AI usage events feed Cost & Usage.

```text
AI Execution
    ↓
Usage Record
    ├── tokens
    ├── model
    ├── provider
    ├── agent
    ├── project
    └── user
        ↓
Cost / Usage Aggregation
        ↓
Admin
```

Actual API secrets never enter this telemetry stream.

---

# 89. External Integration Failure Boundary

External systems include:

- AI providers
- OpenRouter
- GitHub
- Google OAuth
- external APIs
- Tavily/web research
- email providers

External failure must be isolated from core project state.

The system should record the failure, retry when appropriate, and surface an understandable state to the user.

---

# 90. Web Research Integration

MVP and relevant project research can use Tavily for current web information.

Research output should be treated as **evidence**, not as authoritative project state.

The flow is:

```text
Project Context
      ↓
Research Request
      ↓
Tavily
      ↓
Evidence / Sources
      ↓
MVP / Agent Reasoning
      ↓
Validated Structured Output
```

The final project plan remains under GrowFlow's canonical state model.

---

# 91. Context Isolation

Cross-project data leakage must be prevented.

For every AI/RAG/tool operation, the system should explicitly carry relevant scope such as:

```text
tenant/platform scope
user scope
role
group scope
project scope
resource scope
```

The tool layer validates that scope before retrieving data.

---

# 92. No Implicit Cross-Project Context

An AI agent working on Project A must not accidentally receive:

- Project B documents
- Project B RAG chunks
- Project B GitHub data
- Project B private communication
- Project B agent context

unless an explicitly authorized platform-level operation requires it.

Admin AI is the controlled exception for authorized platform-wide information.

---

# 93. Shared Service Model

Student, Mentor, and Admin should reuse shared backend domain services where their underlying operation is the same.

Example:

```text
Student Project View ──┐
Mentor Project View ───┼──> Project Query Service
Admin Project View ────┘
```

Authorization and response shaping occur according to role.

This avoids three separate implementations of the same domain logic.

---

# 94. Query vs Command Separation

Where appropriate, distinguish:

### Queries

Read-only retrieval.

### Commands

Intent to change state.

Example:

```text
GET Project
```

vs.

```text
POST Complete Task
```

This makes authorization and audit behavior easier to reason about.

---

# 95. State-Mutation Confirmation

High-impact AI-assisted actions require explicit confirmation where previously defined.

The flow is:

```text
AI Recommendation
       ↓
User Review
       ↓
Confirmation
       ↓
Deterministic Command
       ↓
Validation
       ↓
State Change
```

AI suggestions must not silently become user actions.

---

# 96. End-to-End Security Model

The complete security boundary is:

```text
Authentication
      ↓
Role
      ↓
Resource Scope
      ↓
Action
      ↓
Privacy
      ↓
Tool
      ↓
Data
      ↓
Audit
```

Every layer must fail closed.

---

# 97. Integration Testing Strategy

Cross-role integration testing must verify:

## Student → Mentor

- student project updates appear to authorized Mentor
- help requests reach Mentor
- relevant notifications work
- at-risk signals appear correctly

## Mentor → Student

- mentor notes reach the correct student
- project-definition updates notify affected students
- mentor actions do not silently mutate student execution state

## Platform → Admin

- platform events appear appropriately
- AI telemetry is recorded
- system failures surface
- audit records exist

## AI → Project

- generated outputs validate
- QA gates work
- failed generation does not corrupt state
- retries are safe

## RAG → AI

- project isolation works
- unauthorized documents cannot be retrieved

## GitHub → Project

- monitoring works
- external failures are isolated

---

# 98. Integration Acceptance Criteria

Part 5E is considered correctly implemented when:

### State

- one canonical project state exists
- deterministic services own state transitions

### Events

- important state changes generate defined events
- event handlers are idempotent

### Notifications

- centralized notification service exists
- Student/Mentor/Admin receive role-appropriate notifications

### Activity

- one canonical activity/event source exists
- each role receives a scoped projection

### AI

- frontend never directly orchestrates agents
- LangGraph orchestrates executions
- outputs are validated
- QA gates generation
- state persistence is deterministic

### Security

- backend authorization is enforced
- AI tools enforce authorization
- project isolation is maintained
- Admin private inspection is controlled

### Streaming

- AI executions can stream through SSE
- execution state survives browser disconnects

### RAG

- retrieval is project scoped
- protected content requires authorization

### GitHub

- monitoring only
- project scoped

### Observability

- AI executions are traceable
- failures and costs are measurable
- cross-system correlation is possible

---

# 99. Final Cross-Role Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                        GROWFLOW UI                            │
│                                                               │
│   STUDENT              MENTOR                 ADMIN           │
│   BUILD                SUPERVISE              GOVERN          │
└───────────────┬──────────────┬──────────────────┬─────────────┘
                │              │                  │
                └──────────────┼──────────────────┘
                               ▼
                     ┌───────────────────┐
                     │    FASTAPI API    │
                     └─────────┬─────────┘
                               │
                    Authentication / RBAC
                               │
                         Resource Auth
                               │
                         Privacy Layer
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
             ▼                                   ▼
    ┌──────────────────┐                ┌──────────────────┐
    │ DOMAIN SERVICES  │                │ AI ORCHESTRATOR  │
    │                  │                │   LANGGRAPH      │
    │ Projects         │                └────────┬─────────┘
    │ Tasks            │                         │
    │ Milestones       │                  ┌──────┴──────┐
    │ Risks            │                  │   12 AGENTS │
    │ Progress         │                  └──────┬──────┘
    │ Health           │                         │
    │ Groups           │                   Validation
    │ Communication    │                         │
    └────────┬─────────┘                       QA
             │                                  │
             └──────────────┬───────────────────┘
                            ▼
                   ┌──────────────────┐
                   │   CANONICAL DB   │
                   │ PostgreSQL /     │
                   │ Supabase         │
                   └────────┬─────────┘
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
             EVENTS    NOTIFICATIONS  ACTIVITY
                │           │           │
                └───────────┼───────────┘
                            │
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
       RAG                GitHub            Observability
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                       ADMIN AI /
                    AI OBSERVATORY
```

---

# 100. Final Architectural Principles

The following principles are frozen:

1. **One canonical source of truth.**
2. **Deterministic services own core state.**
3. **AI assists; it does not become the authority.**
4. **Events coordinate cross-role behavior.**
5. **Notifications are centralized.**
6. **Activity has one canonical event foundation.**
7. **Student, Mentor, and Admin consume scoped views of shared state.**
8. **Authorization is enforced server-side.**
9. **AI tools enforce authorization independently.**
10. **RAG is project/resource scoped.**
11. **GitHub is monitoring-only.**
12. **Admin has broad operational visibility but not unrestricted private-content access.**
13. **Controlled investigations are explicitly authorized and audited.**
14. **Long-running AI execution state is persisted independently of the browser.**
15. **SSE is the initial streaming mechanism.**
16. **Generated Markdown is a representation, not canonical state.**
17. **Project changes use impact analysis and controlled regeneration.**
18. **Existing student instances are not silently migrated after definition changes.**
19. **Failures in external/non-critical systems must not corrupt core state.**
20. **Cross-role boundaries remain explicit.**

---

# 101. Part 5E Freeze Statement

**Part 5E — Application Integration & Cross-Role Architecture is FINAL and FROZEN.**

GrowFlow now has a unified application architecture covering:

- shared application foundation
- Student application
- Mentor application
- Admin application
- cross-role data flow
- canonical project state
- domain events
- notifications
- activity
- project lifecycle
- project change workflow
- AI agent integration
- QA and regeneration
- RAG
- GitHub monitoring
- authorization
- privacy
- streaming
- failure/recovery
- observability
- cost/usage integration
- cross-role security boundaries

The resulting application model is:

> **Student builds the project.**  
> **Mentor supervises the project.**  
> **Admin governs the platform.**  
> **Deterministic backend services own state.**  
> **AI agents provide intelligence.**  
> **Events connect the system.**  
> **Authorization controls every boundary.**

This document is the authoritative Part 5E specification for subsequent GrowFlow architecture and implementation planning.

**Status: FROZEN.**
