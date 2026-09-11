# GrowFlow — Part 5F: Application Architecture Finalization

## Final Specification — FROZEN

**Status:** FINAL / FROZEN  
**Part:** 5F — Application Architecture Finalization  
**Product:** GrowFlow  
**Depends On:**  
- Part 4 — AI Agent Architecture
- Part 5A — Application Foundation
- Part 5B — Student Application Architecture
- Part 5C — Mentor Application Architecture
- Part 5D — Admin Application Architecture
- Part 5E — Application Integration & Cross-Role Architecture

---

# 1. Purpose

Part 5F is the final consolidation and architectural boundary-definition step for GrowFlow's application architecture.

Parts 5A–5E established:

- shared application foundation
- Student application
- Mentor application
- Admin application
- cross-role integration
- events
- notifications
- activity
- project lifecycle
- project changes
- AI/agent integration
- RAG
- GitHub
- authorization
- streaming
- observability

Part 5F does not introduce another role or another feature set.

Its purpose is to establish the final architectural contract that implementation must follow.

The goal is:

> **5A–5E define what GrowFlow is.  
> 5F defines exactly how those pieces fit together and where each responsibility ends.**

---

# 2. Final Layered Architecture

GrowFlow uses a layered architecture:

```text
┌──────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                   │
│                                                          │
│ Student UI │ Mentor UI │ Admin UI │ Shared Components   │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                         API LAYER                        │
│                                                          │
│ FastAPI Routes │ Request Validation │ Auth │ RBAC        │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                     │
│                                                          │
│ Use Cases │ Orchestration │ Commands │ Queries           │
└──────────────────────────┬───────────────────────────────┘
                           │
             ┌─────────────┼──────────────┐
             ▼             ▼              ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ DOMAIN SERVICES │ │ AI ORCHESTR. │ │ INTEGRATIONS     │
│                 │ │              │ │                  │
│ Projects        │ │ LangGraph    │ │ GitHub           │
│ Tasks           │ │ Agents       │ │ Tavily           │
│ Milestones      │ │ Validation   │ │ OAuth            │
│ Risks           │ │ QA/Judge     │ │ Email            │
│ Progress        │ └──────────────┘ │ AI Providers     │
│ Health          │                  └──────────────────┘
│ Groups          │
│ Notifications   │
│ Documents       │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                     DATA / STATE LAYER                   │
│                                                          │
│ PostgreSQL / Supabase │ Vector Store │ File Storage      │
└──────────────────────────────────────────────────────────┘

             ┌──────────────────────────────────┐
             │     CROSS-CUTTING SYSTEMS        │
             │                                  │
             │ Security │ Events │ Audit        │
             │ Logging  │ Metrics │ Tracing     │
             └──────────────────────────────────┘
```

This architecture is frozen.

---

# 3. Modular Monolith Decision

GrowFlow will initially use a:

> **Modular Monolith**

rather than a distributed microservice architecture.

The initial backend is one deployable application with clearly separated logical modules.

Conceptually:

```text
One Backend
    │
    ├── Auth
    ├── Users
    ├── Groups
    ├── Projects
    ├── Planning
    ├── Documents
    ├── RAG
    ├── GitHub
    ├── AI
    ├── Notifications
    ├── Admin
    └── Observability
```

Each module maintains clear internal boundaries.

A module may later be extracted into an independent service if actual scale, reliability, ownership, or deployment requirements justify it.

Microservices are not introduced merely for architectural appearance.

---

# 4. Why Modular Monolith

GrowFlow is a serious system, but unnecessary distributed infrastructure would increase:

- deployment complexity
- debugging complexity
- networking complexity
- operational overhead
- development time
- failure modes

The initial architecture therefore prioritizes:

- clear module boundaries
- strong domain separation
- explicit interfaces
- testability
- observability
- maintainability

without prematurely distributing the application.

---

# 5. Final Domain Modules

The backend is logically divided into the following modules.

## 5.1 Identity & Access

Responsible for:

- authentication
- users
- roles
- OAuth
- authorization
- sessions/tokens
- account access state

---

## 5.2 Organization

Responsible for:

- groups
- mentor relationships
- student relationships
- group membership
- group-level scope

---

## 5.3 Project

Responsible for:

- Project Definitions
- Project Instances
- Project Profile
- Assessment
- Blueprint
- Project Changes
- project-level lifecycle coordination

---

## 5.4 Planning

Responsible for:

- Features
- Specifications
- MVP
- Duration
- Risks
- Tasks
- Milestones

---

## 5.5 Execution

Responsible for:

- progress
- phase
- health
- blocked tasks
- recommended action
- execution-state calculations

---

## 5.6 Communication

Responsible for:

- Mentor Notes
- Help Requests
- Notifications

---

## 5.7 Knowledge

Responsible for:

- Documents
- File Processing
- RAG
- Embeddings
- Vector Retrieval

---

## 5.8 Integrations

Responsible for:

- GitHub
- Tavily
- Google OAuth
- GitHub OAuth
- AI providers
- Email

External systems are accessed through controlled integration boundaries.

---

## 5.9 AI

Responsible for:

- AI Mentor
- Agent Orchestrator
- 12 Agents
- validation
- QA/Judge
- generation
- AI Tool Layer
- execution state

---

## 5.10 Platform

Responsible for:

- Admin
- Audit
- System Health
- AI Observatory
- Cost & Usage
- Platform Analytics

---

## 5.11 Observability

Responsible for:

- logs
- metrics
- traces
- execution records
- correlation IDs
- operational telemetry

---

# 6. Shared Domain Services

Student, Mentor, and Admin should not have separate implementations of the same underlying domain logic.

Avoid:

```text
Student Project Service
Mentor Project Service
Admin Project Service
```

Instead:

```text
             Project Domain Service
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    Student UI   Mentor UI    Admin UI
```

The same principle applies to:

- Groups
- Students
- Projects
- Documents
- Notifications
- AI executions
- Activity

Role-specific authorization and response shaping are applied around shared domain logic.

---

# 7. Command / Query Separation

GrowFlow distinguishes between:

## Queries

Read information.

Examples:

```text
Get Project
Get Student
List Group Projects
Get AI Execution
Get System Health
```

## Commands

Request a state change.

Examples:

```text
Complete Task
Create Help Request
Update Project Profile
Generate Blueprint
Suspend Account
Create Investigation Request
```

This separation improves:

- authorization
- validation
- auditability
- state-mutation control
- testability
- reasoning about side effects

The architecture does not require a separate CQRS infrastructure or separate databases.

---

# 8. Canonical Ownership Matrix

The following ownership is frozen:

| State | Owner |
|---|---|
| User identity | Identity Service |
| Role | Authorization/Identity |
| Group | Group Service |
| Project Definition | Project Service |
| Project Instance | Project Service |
| Assessment | Assessment Service |
| Blueprint | Blueprint/Project Service |
| Features | Planning Service |
| Specification | Planning Service |
| MVP | Planning Service |
| Duration | Planning Service |
| Risks | Risk Service |
| Tasks | Task Service |
| Milestones | Milestone Service |
| Progress | Execution/Progress Service |
| Phase | Project Lifecycle Service |
| Health | Health/Risk Service |
| Mentor Notes | Communication Service |
| Help Requests | Communication Service |
| Notifications | Notification Service |
| Documents | Document Service |
| RAG index | RAG Service |
| GitHub monitoring | GitHub Integration |
| Agent executions | AI Execution Service |
| AI traces | Observability |
| Audit events | Audit Service |

This is logical ownership.

It does not require every service to become a separate deployable process.

---

# 9. Database Ownership

PostgreSQL/Supabase is shared infrastructure, but the data model has logical module ownership.

Conceptually:

```text
auth
users
roles
groups
group_members
project_definitions
project_instances
project_profiles
assessments
blueprints
features
specifications
risks
tasks
milestones
notifications
help_requests
mentor_notes
documents
rag_documents
rag_chunks
github_connections
agent_executions
ai_usage
audit_events
activity_events
...
```

The exact table schema, indexes, constraints, relationships, and migrations will be finalized in the database architecture phase.

5F establishes ownership boundaries rather than prematurely freezing every column.

---

# 10. AI Architecture Boundary

The AI system has a strict boundary.

The canonical flow is:

```text
Application
     ↓
AI Application Service
     ↓
Context Builder
     ↓
Authorization
     ↓
LangGraph Orchestrator
     ↓
Agents / Tools
     ↓
Structured Output
     ↓
Validation
     ↓
QA/Judge
     ↓
Domain Service
     ↓
Database
```

Agents do not:

- directly own persistence
- directly manipulate arbitrary database tables
- bypass authorization
- bypass validation
- become the source of truth

---

# 11. AI Tool Layer

AI tools are grouped by capability.

## Project Tools

- project state
- tasks
- milestones
- risks
- progress

## Document Tools

- document retrieval
- document metadata
- project documents

## RAG Tools

- project-scoped retrieval
- authorized knowledge search

## GitHub Tools

- repository monitoring
- activity retrieval

## Research Tools

- Tavily/web research

## Platform Tools

Admin AI only:

- users
- groups
- projects
- system health
- AI usage
- agent executions
- platform analytics

Every tool performs authorization.

---

# 12. RAG Boundary

RAG remains independent from the agents.

The architecture is:

```text
Document
 ↓
Processing
 ↓
Chunking
 ↓
Embedding
 ↓
Vector Store
 ↓
Retrieval Service
 ↓
Authorized AI Tool
 ↓
Agent
```

Agents do not directly query the vector database.

This creates one controlled retrieval and authorization boundary.

---

# 13. Integration Boundary

External services are wrapped behind internal integration interfaces/adapters.

Examples:

```text
GitHubIntegration
TavilyIntegration
AIProviderGateway
GoogleOAuthIntegration
EmailIntegration
```

The domain/application layers should not spread provider-specific implementation throughout the system.

Conceptually:

```text
Project Service
      ↓
GitHub Integration Interface
      ↓
GitHub Adapter
```

This improves:

- testability
- provider replacement
- failure isolation
- maintainability

---

# 14. AI Provider Gateway

AI access is centralized through an AI Provider Gateway.

```text
AI Application Service
        ↓
AI Provider Gateway
        ↓
OpenRouter / Provider
        ↓
Model
```

The gateway handles:

- provider configuration
- model routing
- key-pool selection
- retries
- rate-limit handling
- provider errors
- timeout handling
- usage recording

Actual API secrets must remain outside:

- UI
- logs
- traces where inappropriate
- normal telemetry
- Admin views

---

# 15. Five-Key Pool

The planned five-key pool remains an infrastructure resilience mechanism.

```text
AI Request
    ↓
Provider Gateway
    ↓
Key Pool Manager
    ↓
Healthy Key Selection
    ↓
Provider
```

Admin may see metadata such as:

- key alias
- provider
- status
- failures
- rate-limit events
- usage
- last success
- last failure

Actual secrets remain inaccessible.

The pool is not intended to bypass provider policies or provider limits.

---

# 16. Event Architecture

The final application uses lightweight internal domain events.

```text
Domain Service
      ↓
Database Transaction
      ↓
Domain Event
      ↓
Event Handlers
      ├── Activity
      ├── Notifications
      ├── Analytics
      └── Observability
```

Events coordinate application modules and cross-role behavior.

A heavyweight external event platform is not required initially.

---

# 17. Background Job Boundary

Long-running or asynchronous operations should use background workers.

Examples:

- AI generation
- agent execution
- document parsing
- embeddings
- RAG indexing
- email delivery
- GitHub synchronization
- analytics aggregation

Conceptually:

```text
API
 ↓
Job / Execution
 ↓
Worker
 ↓
Result
```

The exact queue/worker technology is finalized in the infrastructure architecture phase.

---

# 18. Frontend State Ownership

Frontend state is divided into three categories.

## 18.1 Server State

Examples:

- projects
- tasks
- milestones
- health
- notifications
- documents
- AI execution status

Backend is authoritative.

## 18.2 UI State

Examples:

- sidebar collapsed
- current tab
- modal state
- selected filters
- current scroll position

Frontend owns this.

## 18.3 Streaming State

Examples:

- AI tokens
- generation progress
- temporary execution messages

Streaming state is presentation state.

Persistent execution state remains backend-owned.

---

# 19. API Boundary

Frontend communicates through backend APIs and streams.

```text
Frontend
   ↓
REST / SSE
   ↓
FastAPI
```

There is no:

```text
Frontend → Database
Frontend → AI Provider
Frontend → GitHub
Frontend → Vector Database
```

direct access.

---

# 20. API Contract Principles

APIs should be:

- typed
- validated
- authorization-aware
- consistent
- versionable where required
- explicit about errors
- free from secrets
- appropriately scoped

Sensitive database fields must not automatically become API response fields.

---

# 21. API Error Contract

Conceptually:

```text
{
    code,
    message,
    details,
    request_id
}
```

Potential error categories include:

```text
AUTHENTICATION_REQUIRED
FORBIDDEN
NOT_FOUND
VALIDATION_ERROR
CONFLICT
RATE_LIMITED
DEPENDENCY_FAILURE
AI_GENERATION_FAILED
INTERNAL_ERROR
```

The exact implementation schema is finalized in the backend/API architecture phase.

---

# 22. API Versioning

The initial application API should use:

```text
/api/v1
```

Premature multi-version complexity should be avoided.

Internal modules can evolve without becoming separate services.

---

# 23. Observability Architecture

Important operations must be traceable across the system.

```text
Request ID
   ↓
Operation ID
   ↓
Generation ID
   ↓
Execution ID
   ↓
Agent Execution IDs
   ↓
Events
   ↓
Notifications
```

Observability covers:

- logs
- metrics
- traces
- AI executions
- provider calls
- RAG operations
- document processing
- external integrations
- security events

LangSmith is used for appropriate AI execution tracing.

---

# 24. Security Architecture

Security is cross-cutting.

```text
Authentication
      ↓
Role Authorization
      ↓
Resource Authorization
      ↓
Privacy
      ↓
Tool Authorization
      ↓
Operation
      ↓
Audit
```

Security checks are server-side.

Frontend checks improve UX but are never the final security boundary.

---

# 25. Project Isolation

Project ID is a fundamental isolation boundary.

For project-scoped resources:

```text
User
 ↓
Authorized Relationship
 ↓
Project
 ↓
Resource
```

This applies to:

- documents
- RAG
- tasks
- milestones
- risks
- GitHub
- AI context
- generated outputs
- activity

---

# 26. Cross-Role Access Model

## Student

```text
Own account
→ own project instances
→ own project resources
```

## Mentor

```text
Own groups
→ students in groups
→ their authorized project instances
```

## Admin

```text
Platform
→ basic authorized information
→ operational data
→ protected content only through investigation
```

This is the unified authorization model.

---

# 27. Document Architecture

Generated documents are derived representations.

```text
Structured Project State
        ↓
Document Renderer
        ↓
Markdown
        ↓
Viewer / Preview / Raw / Download
```

If underlying project state changes:

```text
State Change
 ↓
Impact Analysis
 ↓
Affected Documents
 ↓
Regeneration
```

Downloaded Markdown is not the authoritative project state.

---

# 28. Project Versioning

Project generation/version metadata must answer:

- What state generated this blueprint?
- Which documents belong to which project version?
- What changed?
- Why was regeneration triggered?
- Which QA result approved the output?

This is controlled project/generation versioning, not necessarily Git-style version control.

---

# 29. Project Change Integration

Meaningful project changes continue to use:

```text
Change Requested
       ↓
Impact Analysis
       ↓
Affected Components
       ↓
User Review / Confirmation
       ↓
Regeneration
       ↓
Validation
       ↓
QA / Judge
       ↓
Accept
       ↓
Persist Canonical State
       ↓
Document Rendering
       ↓
Events
       ↓
Notifications / Activity
```

This prevents stale or contradictory project documentation.

---

# 30. Deterministic State Boundary

The following remain deterministic:

- authorization
- ownership
- role checking
- task transitions
- milestone transitions
- progress calculation
- phase transitions
- account status enforcement
- notification permissions
- project isolation
- document access
- RAG authorization
- GitHub authorization
- investigation authorization
- audit creation

AI may assist but cannot replace these controls.

---

# 31. AI Action Boundary

The final rule is:

> **AI may recommend, analyze, explain, generate, and request an action; deterministic services perform authoritative state changes.**

Example:

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
Database Transaction
        ↓
TaskCompleted
```

AI does not directly set arbitrary project state.

---

# 32. Async vs Synchronous Boundary

Recommended initial classification:

| Operation | Mode |
|---|---|
| AI blueprint generation | Async |
| Agent execution | Async |
| Document parsing | Async |
| Embeddings | Async |
| RAG indexing | Async |
| Email | Async |
| GitHub synchronization | Usually Async |
| Analytics aggregation | Async |
| Simple CRUD | Usually Synchronous |
| Task completion | Usually Synchronous |
| Help-request creation | Synchronous |
| Basic reads | Synchronous |

This is a logical boundary, not a requirement to create separate deployable services.

---

# 33. Long-Running Execution Independence

AI execution state must survive browser disconnection.

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

SSE is only a delivery mechanism.

The backend execution record is authoritative.

---

# 34. AI Streaming

The initial streaming mechanism is:

> **Server-Sent Events (SSE)**

WebSockets are not required initially.

They may be introduced later only if actual product requirements justify them.

The stream can communicate:

- current stage
- current agent
- progress
- generated content
- validation
- QA
- errors
- completion

---

# 35. Failure Isolation

A failure in one subsystem must not falsely represent failure of the whole platform.

Examples:

- AI provider failure must not corrupt project state.
- Email failure must not invalidate an in-app notification.
- RAG indexing failure must not delete canonical documents.
- GitHub outage must not make a project disappear.
- Analytics failure must not block task completion.

Core transactional state should remain independent from non-critical downstream operations.

---

# 36. Retry Architecture

Retries are allowed only when safe.

Good candidates:

- AI provider requests
- email delivery
- RAG indexing
- background processing
- telemetry submission

State-changing operations require:

- idempotency
- transactions
- duplicate protection
- or equivalent safeguards

before retry.

---

# 37. Idempotency

Important operations should be safe against repeated delivery/execution.

Examples:

- task completion
- help-request transitions
- notification creation
- agent execution callbacks
- document-generation completion
- event handlers

Repeated events must not create duplicated state.

---

# 38. Database Transaction Boundary

Core domain state changes should use appropriate database transactions.

Example:

```text
Task completion
    ├── task state
    ├── milestone state
    ├── project progress
    └── relevant project state
```

Non-critical downstream actions such as:

- email
- analytics
- external telemetry

should not unnecessarily extend the core database transaction.

---

# 39. Cross-Role Activity Model

There remains one canonical activity/event foundation.

```text
Canonical Event
      ↓
Activity Projection
      ↓
Role / Resource Filtering
      ↓
Role-Specific Timeline
```

### Student

Relevant project activity.

### Mentor

Authorized group/student/project activity.

### Admin

Platform, administrative, and authorized investigation activity.

---

# 40. Cross-Role Notification Model

There remains one centralized notification system.

```text
Domain Event
    ↓
Notification Rules
    ↓
Recipient Authorization
    ↓
Notification
    ↓
In-App
    ↓
Optional Email
```

Student, Mentor, and Admin receive different notification classes according to role and resource scope.

---

# 41. Cross-Role Project Model

There is one canonical project domain.

```text
Project Definition
        ↓
Student Project Instance
        ↓
Project State
        ↓
Student UI
Mentor UI
Admin UI
```

Different roles receive different authorized views of the same underlying state.

---

# 42. Mentor Definition Update Boundary

The previously frozen rule remains:

```text
Project Definition Updated
        ↓
Existing Instances
        └── Unchanged
        ↓
New Assignments
        └── Updated Definition
        ↓
Affected Existing Students
        └── Notification
```

No automatic migration of existing student:

- profile
- blueprint
- tasks
- milestones
- risks
- timeline
- progress
- phase
- health

occurs.

Students may voluntarily review/adopt the change through the approved project-change workflow.

---

# 43. Admin Boundary

Admin remains:

> **Govern + Observe + Analyze + Investigate + Controlled Intervene**

Admin is not:

- a second Mentor
- a super-student
- a GitHub administrator
- a project editor
- a task manager
- a roadmap editor
- an unrestricted database browser
- an unrestricted private-chat viewer
- an impersonation mechanism

---

# 44. Admin AI Boundary

Admin AI can access authorized platform information and operational intelligence.

It can:

- retrieve basic platform information
- retrieve authorized student/mentor/group/project information
- analyze platform metrics
- analyze AI usage
- analyze agent executions
- analyze system health
- analyze RAG operations
- explain anomalies
- recommend operational actions

Protected private content remains behind the controlled investigation workflow.

---

# 45. Controlled Investigation

The privacy workflow remains:

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

Admin role alone does not mean unrestricted access to all private content.

---

# 46. Shared Service Pattern

The final application follows this pattern:

```text
                   Shared Domain Service
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Student        Mentor         Admin
             UI            UI             UI
```

This applies wherever the underlying domain operation is shared.

Role-specific behavior should be implemented through:

- authorization
- query scope
- response shaping
- allowed commands
- privacy policy

rather than duplicated domain logic.

---

# 47. What Should NOT Become a Separate Service

The following remain logical modules inside the modular monolith initially:

- Task Service
- Milestone Service
- Risk Service
- Notification Service
- Project Service
- Document Service
- RAG Service
- Admin Service

"Service" means a logical application/domain boundary.

It does not automatically mean a separate server.

---

# 48. Scope Boundary — Explicit Non-Goals

The initial architecture does not require:

- microservices
- Kafka
- Kubernetes
- service mesh
- WebSockets
- event sourcing
- CQRS infrastructure as a separate system
- blockchain
- complex ML risk scoring
- custom vector database platform
- custom model hosting
- autonomous AI administrative actions
- user impersonation
- unrestricted Admin data access

These may be reconsidered only if actual requirements justify them.

---

# 49. Final Responsibility Model

```text
                    USER
                     │
                     ▼
                 FRONTEND
                     │
                     ▼
                  FASTAPI
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     APPLICATION            AUTHORIZATION
       SERVICES
          │
    ┌─────┴──────────────┐
    ▼                    ▼
DOMAIN SERVICES       AI SERVICES
    │                    │
    │               LANGGRAPH
    │                    │
    │                 AGENTS
    │                    │
    │                VALIDATION
    │                    │
    │                  QA/JUDGE
    │                    │
    └─────────┬──────────┘
              ▼
       CANONICAL STATE
              │
        ┌─────┼──────┐
        ▼     ▼      ▼
      EVENTS ACTIVITY NOTIFICATIONS
        │
   ┌────┴───────────┐
   ▼                ▼
INTEGRATIONS    OBSERVABILITY
```

---

# 50. Final 5A–5F Architecture

The complete application architecture is now:

```text
5A
Shared Application Foundation
        ↓
5B
Student Application
        ↓
5C
Mentor Application
        ↓
5D
Admin Application
        ↓
5E
Cross-Role Integration
        ↓
5F
Final Architecture Consolidation
```

Underlying all of it:

```text
                 GROWFLOW
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   STUDENT         MENTOR        ADMIN
     BUILD        SUPERVISE      GOVERN
       │             │             │
       └─────────────┼─────────────┘
                     ▼
              FASTAPI BACKEND
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   DOMAIN SERVICES          AI SYSTEM
          │                     │
          ▼                  LANGGRAPH
      POSTGRESQL                │
          │                  12 AGENTS
          │                     │
          │                  QA/JUDGE
          │                     │
          └──────────┬──────────┘
                     ▼
              EVENTS / ACTIVITY
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     NOTIFICATIONS  RAG       GITHUB
                     │
                     ▼
              OBSERVABILITY
                     │
                     ▼
                 ADMIN AI
```

---

# 51. Final Architectural Principles

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
21. **The backend begins as a modular monolith.**
22. **Shared domain services prevent duplicated business logic.**
23. **Commands and queries have clear separation of intent.**
24. **External providers are isolated behind integration adapters.**
25. **No architectural infrastructure is introduced without a real requirement.**

---

# 52. Final 5F Decision Summary

All ten proposed architecture decisions are approved and frozen.

| # | Decision | Final |
|---|---|---|
| **1** | Layered architecture: Presentation → API → Application → Domain/AI/Integrations → Data | **YES** |
| **2** | Modular Monolith rather than microservices initially | **YES** |
| **3** | Shared domain services across Student/Mentor/Admin | **YES** |
| **4** | Command/Query separation | **YES** |
| **5** | Canonical ownership matrix | **YES** |
| **6** | AI → Tools → Agents → Validation → QA → Domain Service → DB | **YES** |
| **7** | External integrations behind adapters/interfaces | **YES** |
| **8** | Central authorization/security boundary | **YES** |
| **9** | Async workers for AI/RAG/document/integration workloads | **YES** |
| **10** | Explicitly avoid unnecessary infrastructure/microservices | **YES** |

---

# 53. Architecture-to-Implementation Boundary

After Part 5F, the following are considered architecturally defined:

### Application

- shared shell
- Student application
- Mentor application
- Admin application
- navigation
- role boundaries
- project workspace
- cross-role views

### Backend

- layered architecture
- modular monolith
- logical domain modules
- application services
- commands/queries
- domain services
- repositories/data-access boundary

### AI

- LangGraph orchestration
- 12-agent architecture
- AI tool layer
- structured outputs
- validation
- QA/Judge
- generation/recovery
- AI action boundary
- provider gateway

### Data

- canonical state principle
- logical data ownership
- project isolation
- document representation model
- generation/version metadata

### Integration

- GitHub monitoring
- Tavily research
- OAuth
- AI providers
- email
- RAG

### Cross-Cutting

- authentication
- authorization
- privacy
- events
- notifications
- activity
- audit
- logging
- metrics
- tracing
- correlation IDs

### Infrastructure Boundary

- synchronous vs asynchronous work
- background processing
- SSE
- failure isolation
- retries
- idempotency

The exact implementation technologies, schemas, endpoint contracts, queue choice, deployment topology, and infrastructure configuration are finalized in the corresponding later architecture/implementation phases.

---

# 54. Part 5F Freeze Statement

**Part 5F — Application Architecture Finalization is FINAL and FROZEN.**

Part 5 is now complete.

GrowFlow's application architecture is defined from the user interface all the way through:

- role-specific applications
- shared application shell
- API layer
- application services
- domain services
- AI orchestration
- agents
- tools
- validation
- QA
- integrations
- events
- notifications
- activity
- canonical database state
- RAG
- GitHub
- observability
- security
- privacy
- background execution
- failure recovery

The architectural philosophy is:

> **Student builds.**  
> **Mentor supervises.**  
> **Admin governs.**  
> **Backend owns state.**  
> **AI provides intelligence.**  
> **Events connect the system.**  
> **Authorization protects every boundary.**  
> **Infrastructure remains as simple as the real requirements allow.**

No additional application architecture should be introduced unless a concrete requirement exposes a genuine architectural gap.

**Status: FROZEN.**

**Part 5 — Application Architecture: COMPLETE.**
