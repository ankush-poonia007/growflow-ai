# GrowFlow — Phase 6N
# Backend Architecture Finalization
## Consolidation of 6A–6M and Final Phase 6 Freeze

**Project:** GrowFlow  
**Phase:** 6 — Backend & Platform Architecture  
**Subphase:** 6N — Backend Architecture Finalization  
**Status:** FINAL / FROZEN  
**Purpose:** Consolidate the complete Phase 6 architecture into one authoritative backend and platform architecture baseline for implementation.

---

# 1. Purpose

6N is the final architectural consolidation document for Phase 6.

It does not introduce a new architecture. It consolidates the decisions established across:

- 6A — Backend Architecture
- 6B — Database Architecture
- 6C — API Architecture
- 6D — Authentication & Security
- 6E — AI Infrastructure
- 6F — Agent Execution Infrastructure
- 6G — RAG & Document Infrastructure
- 6H — Background Jobs & Events
- 6I — External Integrations
- 6J — Observability
- 6K — Storage & File Architecture
- 6L — Deployment & Runtime
- 6M — Infrastructure Security

The purpose is to establish one coherent implementation baseline.

> **Phase 6 defines how GrowFlow is built. It does not implement GrowFlow.**

---

# 2. Original Phase 6 Roadmap

The authoritative Phase 6 sequence is:

| Subphase | Area |
|---|---|
| 6A | Backend Architecture |
| 6B | Database Architecture |
| 6C | API Architecture |
| 6D | Authentication & Security |
| 6E | AI Infrastructure |
| 6F | Agent Execution Infrastructure |
| 6G | RAG & Document Infrastructure |
| 6H | Background Jobs & Events |
| 6I | External Integrations |
| 6J | Observability |
| 6K | Storage & File Architecture |
| 6L | Deployment & Runtime |
| 6M | Infrastructure Security |
| 6N | Backend Architecture Finalization |

This sequence is the governing Phase 6 structure.

---

# 3. Final Architecture at a Glance

GrowFlow uses a secure, layered, modular-monolith architecture:

```text
                           CLIENTS
                              |
                    HTTPS / TLS Boundary
                              |
                         FRONTEND
                              |
                    -------------------
                              |
                         FASTAPI API
                              |
                Authentication / Authorization
                              |
                     Application Layer
                              |
                       Domain Layer
                              |
          +-------------------+-------------------+
          |                   |                   |
       Data Access       AI / Agents       Integrations
          |                   |                   |
     PostgreSQL          LangGraph          GitHub
     + Supabase          LangChain          Tavily
          |              LlamaIndex         OAuth
         RLS              Gateway            Email
          |                   |                   |
          +-------------------+-------------------+
                              |
                         Infrastructure
                              |
             +----------------+----------------+
             |                |                |
          Workers          Storage       Observability
             |                |                |
          Jobs/RAG/AI     Documents      Logs/Metrics/
          Events          Files          Traces/LangSmith
             |
       Transactional
          Outbox
```

The architecture remains a **modular monolith**, not a collection of microservices.

---

# 4. Architectural Principles

The final Phase 6 architecture follows these principles:

1. PostgreSQL is the canonical relational source of truth.
2. Supabase provides managed platform capabilities without replacing domain ownership.
3. FastAPI is the backend application framework.
4. The backend is a modular monolith.
5. The system uses layered architecture.
6. API routes remain thin.
7. Application services own use-case orchestration.
8. Domain services own business rules and authoritative state transitions.
9. Repositories own persistence access.
10. Pydantic defines typed boundaries.
11. FastAPI dependency injection supplies controlled dependencies.
12. Authentication and authorization are centralized.
13. Resource and project scope are enforced independently of role checks.
14. RLS provides database-level defense in depth.
15. AI cannot directly mutate canonical state.
16. AI provider communication goes through one gateway.
17. Agent execution is orchestrated through LangGraph.
18. RAG is project-scoped and authorization-enforced.
19. Background work is persistent and recoverable.
20. Domain events use lightweight internal event infrastructure.
21. Transactional outbox provides reliable event publication.
22. External systems are accessed through adapters/interfaces.
23. SSE is the initial streaming mechanism.
24. Observability does not bypass privacy or authorization.
25. Infrastructure security follows defense in depth.
26. Secrets remain outside source code and frontend clients.
27. Generated documents are representations, not canonical state.
28. Vector indexes are derived knowledge representations.
29. Deterministic services own canonical project state.
30. Unnecessary distributed infrastructure is deliberately avoided.

---

# 5. Final Layered Architecture

```text
Presentation
    ↓
API / Transport
    ↓
Application
    ↓
Domain
    ↓
Data Access
    ↓
Infrastructure
```

Supporting controlled components:

```text
AI
Integrations
Workers
Observability
Security
Events
```

These components do not create alternate ownership paths around the core layers.

---

# 6. Presentation Layer

The frontend is responsible for:

- UI rendering
- navigation
- local interaction state
- form state
- displaying server state
- SSE consumption
- user confirmation
- validation feedback
- responsive behavior

The frontend is not authoritative for:

- project progress
- task completion
- milestone completion
- phase
- health
- permissions
- AI state changes
- database state

All authoritative changes go through the backend.

---

# 7. API Layer

FastAPI provides the HTTP boundary.

Responsibilities:

- route definitions
- request parsing
- authentication dependencies
- authorization dependencies
- Pydantic validation
- response serialization
- HTTP status codes
- transport-specific behavior
- correlation IDs
- SSE transport

Routes should not contain complex business logic.

Canonical API namespace:

```text
/api/v1
```

Long-running operations use:

```text
POST
  ↓
Validate
  ↓
Create execution/job
  ↓
202 Accepted
  ↓
Worker
  ↓
Persist result
  ↓
SSE / polling
```

---

# 8. Application Layer

Application services implement use cases.

Representative use cases:

- RegisterUser
- AuthenticateUser
- CreateGroup
- JoinGroup
- CreateProject
- AssignProjectDefinition
- StartAssessment
- SubmitAssessmentAnswer
- GenerateBlueprint
- CompleteTask
- BlockTask
- CompleteMilestone
- CreateHelpRequest
- ResolveHelpRequest
- GenerateAIResponse
- RequestProjectChange
- AuthorizeAdminInvestigation

Application services coordinate domain services, repositories, integrations, and workers.

They do not become generic God services.

---

# 9. Domain Layer

The domain layer contains GrowFlow's authoritative business concepts and rules.

Final domain modules:

```text
Identity & Access
Organization
Project
Planning
Execution
Communication
Knowledge
Integrations
AI
Platform
Observability
```

Domain logic must remain independent of HTTP transport.

---

# 10. Data Access Layer

All persistent database access is controlled through repositories/data-access components.

Representative repositories:

- UserRepository
- GroupRepository
- GroupMembershipRepository
- ProjectDefinitionRepository
- ProjectInstanceRepository
- AssessmentRepository
- BlueprintRepository
- FeatureRepository
- SpecificationRepository
- MVPRepository
- TimelineRepository
- RiskRepository
- TaskRepository
- MilestoneRepository
- NotificationRepository
- DocumentRepository
- RAGRepository
- GitHubRepository
- AIExecutionRepository
- AuditRepository

Routes must not scatter raw database operations throughout the application.

---

# 11. Infrastructure Layer

Infrastructure implements external technical concerns:

```text
Database
AI Provider
GitHub
Tavily
OAuth
RAG / Vector Store
Storage
Email
Observability
Workers
```

External providers are accessed through adapters or gateways.

Provider-specific logic must not leak throughout the application.

---

# 12. Database Architecture

PostgreSQL/Supabase remains the canonical relational system.

Major logical areas:

```text
Identity
Organization
Projects
Assessment
Blueprint
Planning
Risks
Execution
Communication
Knowledge
GitHub
AI
Platform
Security
Observability
```

Important principles:

- UUID identifiers
- UTC timestamps
- foreign-key integrity
- database constraints
- indexes based on real query patterns
- JSONB only where naturally flexible
- migrations required
- RLS defense in depth
- controlled cascade behavior
- meaningful history preservation
- no blanket soft-delete requirement

---

# 13. Canonical State Ownership

| State | Authoritative Owner |
|---|---|
| User identity | Identity |
| Role | Identity / Authorization |
| Group | Organization |
| Project Definition | Project |
| Project Instance | Project |
| Assessment | Assessment |
| Blueprint | Project / Blueprint |
| Features | Planning |
| Specifications | Planning |
| MVP | Planning |
| Timeline | Planning |
| Risks | Risk |
| Tasks | Planning / Execution |
| Milestones | Planning / Execution |
| Progress | Execution |
| Phase | Project Lifecycle |
| Health | Health / Risk |
| Mentor Notes | Communication |
| Help Requests | Communication |
| Notifications | Notification |
| Documents | Knowledge / Document |
| RAG Index | Knowledge / RAG |
| GitHub Monitoring | GitHub Integration |
| Agent Execution | AI Execution |
| AI Trace | Observability |
| Audit | Audit |

No secondary component may silently become authoritative for these states.

---

# 14. Project State Model

The canonical project lifecycle is:

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

The deterministic execution chain is:

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

AI may recommend changes but does not arbitrarily overwrite this chain.

---

# 15. Project Definition and Instance Model

A mentor-created project has:

```text
Project Definition
      ↓
Definition Version
      ↓
Student Project Instance
```

Existing student instances are independent.

When a definition changes:

- existing instances remain unchanged
- new assignments receive the new version
- affected existing students receive a concise notification
- no automatic migration occurs
- existing students may voluntarily adopt the change through the project-change workflow

This prevents hidden project-state mutation.

---

# 16. Assessment Architecture

Assessment consists of:

```text
10 standardized core questions
+
5 dynamic project-specific questions
```

The dynamic questions are generated sequentially.

Each dynamic question may use:

- previous answer
- accumulated relevant context
- project context

Only one question is presented at a time.

Assessment results become structured project context for blueprint generation.

Assessment state is persisted and recoverable.

---

# 17. AI Infrastructure

The AI stack is:

| Technology | Responsibility |
|---|---|
| LangGraph | Agent orchestration/workflow |
| LangChain | Prompt/tool/structured LLM abstractions |
| LlamaIndex | Document/RAG pipeline |
| LangSmith | Tracing/evaluation |
| Pydantic | Structured contracts/validation |
| OpenAI-compatible client | Provider communication mechanism |
| OpenRouter | Initial AI provider/routing layer |
| Tavily | Current web research |
| AI Provider Gateway | Central provider boundary |

No agent or application route bypasses the gateway.

---

# 18. AI Provider Gateway

The gateway owns:

- provider communication
- model policy
- capability routing
- five-key pool
- key health
- rotation
- cooldown
- rate limits
- retries
- timeouts
- fallback
- streaming
- provider error normalization
- usage/cost tracking

Five keys do not constitute permission to bypass provider-level quota restrictions.

When usable capacity is exhausted:

```text
QUOTA_EXHAUSTED
or
PROVIDER_UNAVAILABLE
```

The platform returns a clear failure and preserves canonical project state.

---

# 19. Agent Architecture

GrowFlow has exactly 12 logical agents:

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

Each has one primary responsibility.

No dedicated Change/Impact Agent exists.

Impact analysis is an orchestration/application responsibility.

---

# 20. Blueprint Agent Graph

Canonical workflow:

```text
Project + Assessment
        ↓
     Idea Agent
        ↓
     Scope Agent
        ↓
 +------+------+------+
 |             |      |
Technology   Features  MVP
 |             |      |
 +------+------+------+
        ↓
 Specification
        ↓
 Timeline
        ↓
 Risk
        ↓
 Task
        ↓
 Milestone
        ↓
 README
        ↓
 QA / Judge
        ↓
   PASS / FAIL
      |       |
      |       +----→ Targeted Regeneration
      |
 Persist
```

Where dependencies permit, independent agents execute concurrently.

LangGraph controls the workflow.

LangGraph state is execution state, not canonical application state.

---

# 21. AI Output Authority Boundary

The authoritative pipeline is:

```text
LLM
 ↓
Structured Output
 ↓
Pydantic Validation
 ↓
QA / Judge
 ↓
Deterministic Domain Service
 ↓
Database
```

AI output is not authoritative merely because the model produced it.

This boundary applies to:

- blueprint generation
- project change regeneration
- AI recommendations
- AI-assisted state changes

---

# 22. AI Mentor

AI Mentor is an application capability, not an additional blueprint agent.

It uses:

- authorized structured data
- project RAG
- GitHub monitoring
- current research where appropriate
- reasoning
- controlled tools

Source routing:

```text
Structured state → PostgreSQL tools
Documents → RAG
GitHub → GitHub integration
Current research → Tavily
Complex reasoning → LLM
```

AI Mentor cannot bypass authorization or directly mutate core state.

---

# 23. RAG Architecture

Canonical relationship:

```text
PostgreSQL
   ↓
Document Metadata
   ↓
Object/File Storage
   ↓
Parse
   ↓
Normalize
   ↓
Chunk
   ↓
Embed
   ↓
Vector Index
   ↓
Project-Scoped Retrieval
   ↓
Context Builder
   ↓
AI
```

The vector store is derived data.

PostgreSQL remains authoritative for document metadata and project relationships.

RAG retrieval is always authorization-aware.

---

# 24. Document Architecture

Generated and uploaded documents are representations of canonical project state or project knowledge.

Documents are versioned where required.

Typical lifecycle:

```text
Upload / Generate
   ↓
Validate
   ↓
Store
   ↓
Parse
   ↓
Normalize
   ↓
Version
   ↓
Index if applicable
   ↓
Ready
```

Generated Markdown is not the source of truth.

The source of truth is structured PostgreSQL state.

---

# 25. External Integrations

External integrations use adapters/interfaces.

Required integrations include:

- GitHub
- Tavily
- Google OAuth
- GitHub OAuth
- Email
- Supabase/Storage
- OpenRouter
- LangSmith

Integration failures must be isolated.

Example:

```text
GitHub unavailable
      ↓
GitHub monitoring degraded
      ↓
Core project remains usable
```

GrowFlow's GitHub capability remains monitoring-only.

---

# 26. Background Jobs

Long-running work is executed asynchronously.

Examples:

- blueprint generation
- agent execution
- AI requests
- document parsing
- embedding
- RAG indexing
- GitHub synchronization
- email delivery

Jobs persist independently of the browser.

Browser disconnection does not automatically cancel work.

---

# 27. Event Architecture

GrowFlow uses lightweight internal domain events.

Core pattern:

```text
Database Transaction
       ↓
Transactional Outbox
       ↓
Event Publication
       ↓
Worker / Handler
       ↓
Side Effect
```

Events are delivered at least once.

Handlers must be idempotent.

Representative events include:

- TaskCompleted
- TaskBlocked
- MilestoneCompleted
- ProjectProgressChanged
- ProjectPhaseChanged
- ProjectHealthChanged
- RiskCreated
- RiskResolved
- HelpRequestCreated
- HelpRequestResolved
- MentorNoteCreated
- BlueprintGenerated
- AgentExecutionCompleted
- GitHubActivityDetected
- DocumentIndexed
- SecurityEventDetected
- AccountStatusChanged

Kafka/RabbitMQ are intentionally not required initially.

---

# 28. Reliability Model

Reliability controls include:

- idempotency
- retries
- bounded exponential backoff
- jitter
- dead-letter handling
- job state persistence
- crash recovery
- startup reconciliation
- graceful shutdown
- concurrency controls
- backpressure
- optimistic concurrency
- stale execution protection
- failure isolation

No infinite retry loop is permitted.

---

# 29. Authorization Architecture

The final authorization chain is:

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

Role alone never establishes complete access.

---

# 30. Admin Security Boundary

Admin has broad platform visibility but remains subject to privacy boundaries.

Default behavior:

> Metadata-first.

Deeper protected/private inspection requires:

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

No impersonation.

Admin AI uses the same authorization and infrastructure boundaries.

---

# 31. Storage Architecture

Storage is separated conceptually into:

```text
PostgreSQL
  → metadata, relationships, state

Object Storage
  → large documents/files/content

Vector Index
  → derived retrieval representation
```

Private project files require authorized access.

Signed URLs, where used, are short-lived and do not replace authorization.

---

# 32. Deployment Architecture

Initial deployment topology:

```text
Frontend
     +
FastAPI
     +
Worker
     +
Supabase / PostgreSQL
     +
Object Storage
     +
External Providers
     +
Observability
     +
CI/CD
```

Environment separation:

```text
Development
Staging
Production
```

Each environment has separate appropriate configuration and credentials.

---

# 33. Runtime Architecture

FastAPI handles synchronous request/response work.

Workers handle expensive asynchronous work.

SSE handles execution streaming.

Health/readiness endpoints expose runtime state appropriate to deployment requirements.

Graceful shutdown ensures active work is not silently corrupted.

Long-running execution survives browser disconnect.

---

# 34. Infrastructure Security

Infrastructure security is defense-in-depth across:

```text
TLS
 ↓
Network Boundaries
 ↓
Runtime Hardening
 ↓
Application Authorization
 ↓
Database/RLS
 ↓
Storage Authorization
 ↓
Integration Security
 ↓
Audit/Observability
```

Mandatory controls include:

- secrets outside source code
- backend-only privileged credentials
- secure CORS
- security headers
- rate limiting
- SSRF protection
- file upload restrictions
- path traversal protection
- container hardening
- dependency scanning
- environment isolation
- worker authorization revalidation
- secret redaction
- secure backups
- resource limits

---

# 35. Secrets Architecture

Configuration flow:

```text
Environment / Secret Store
          ↓
Typed Settings
          ↓
Dependency Injection
          ↓
Application Component
```

Application code does not repeatedly read `.env`.

Secrets must never appear in:

- frontend code
- API responses
- logs
- AI prompts
- generated documents
- source control

---

# 36. Security Invariants

The following are final Phase 6 invariants:

1. Canonical project state exists in PostgreSQL.
2. AI cannot directly mutate canonical state.
3. Every protected resource requires authorization.
4. Project isolation is enforced at application level and reinforced at database/RAG level.
5. Privileged credentials remain backend-only.
6. AI provider keys are centralized in the provider gateway.
7. Agents cannot access raw SQL or unrestricted databases.
8. External systems are accessed through controlled adapters.
9. Background jobs revalidate authorization.
10. Stale executions cannot overwrite newer state.
11. Uploaded files are untrusted.
12. Retrieved documents are untrusted data.
13. Arbitrary server-side URL fetching is prohibited.
14. Private storage requires authorization.
15. Security-sensitive actions are auditable.
16. Observability cannot bypass privacy.
17. Admin access does not imply unrestricted private-content access.
18. Long-running work survives browser disconnect.
19. Failures preserve the last valid canonical state.
20. Security controls are tested.

---

# 37. Error Architecture

Canonical success:

```json
{
  "success": true,
  "message": "...",
  "data": {},
  "metadata": {}
}
```

Canonical error:

```json
{
  "success": false,
  "message": "...",
  "data": null,
  "error": {
    "code": "...",
    "details": []
  }
}
```

Core exception categories include:

- ValidationException
- AuthenticationException
- AuthorizationException
- NotFoundException
- ConflictException
- BusinessRuleException
- IntegrationException
- AIException
- RAGException
- StorageException
- InfrastructureException

Special protocols such as SSE, file responses, and health endpoints use appropriate transport semantics.

---

# 38. Observability Architecture

Observability covers:

- requests
- API latency/errors
- database behavior
- workers
- jobs
- events/outbox
- AI executions
- agent executions
- LangGraph workflows
- LangSmith traces
- provider/key-pool behavior
- RAG
- document processing
- GitHub
- Tavily
- email
- storage
- security
- audit

Telemetry must include safe correlation identifiers.

Sensitive content must not be captured indiscriminately.

---

# 39. AI Quality Architecture

AI quality is evaluated through:

- structured-output validation
- QA/Judge results
- completeness
- contradiction detection
- scope validation
- technology consistency
- timeline consistency
- dependency consistency
- risk coverage
- README consistency
- unsupported-claim detection
- regeneration tracking
- feedback
- regression evaluation

QA failure results in targeted regeneration where possible.

---

# 40. Project Change Architecture

Project changes use the canonical workflow:

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
      ↓
Deterministic Persistence
```

There is no dedicated Change/Impact Agent.

Impact analysis is handled by orchestration/application logic.

Existing valid project state remains protected until the change is successfully validated.

---

# 41. Failure Model

The platform must degrade safely.

Examples:

### AI unavailable

```text
AI generation fails
      ↓
Execution marked failed/unavailable
      ↓
Existing project state preserved
```

### RAG unavailable

```text
RAG retrieval fails
      ↓
AI capability degraded
      ↓
Canonical project state preserved
```

### Email unavailable

```text
Email fails
      ↓
In-app notification remains available
```

### GitHub unavailable

```text
GitHub monitoring fails
      ↓
GitHub data becomes temporarily stale
      ↓
Core project execution continues
```

---

# 42. Performance and Scalability Strategy

GrowFlow scales first through:

- efficient database queries
- proper indexes
- connection management
- worker concurrency
- asynchronous processing
- backpressure
- bounded AI workloads
- storage separation
- horizontal application/worker scaling when needed

The architecture does not prematurely introduce microservices.

---

# 43. Testing Architecture

Phase 6 establishes testing expectations across:

```text
Unit
Domain
Repository
Database Integration
API
Contract
Security
AI / Agent
RAG
Events / Workers
Frontend
E2E
Performance
Failure / Recovery
Deployment / Smoke
Regression / Evaluation
```

Critical invariants must be directly tested.

Particularly important:

- project isolation
- role boundaries
- RLS
- AI authorization
- RAG isolation
- stale execution protection
- provider quota behavior
- job idempotency
- outbox reliability
- SSE behavior
- file security
- OAuth security

---

# 44. Final Repository / Package Direction

The backend follows the structure established in 6A:

```text
backend/
├── app/
│   ├── main.py
│   ├── config/
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── workers/
│   └── shared/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── e2e/
├── migrations/
├── scripts/
├── .env
├── .env.example
├── pyproject.toml
└── README.md
```

This is a logical architectural structure. Empty modules or folders must not be created solely to satisfy a diagram.

---

# 45. Dependency Direction

The intended dependency direction is:

```text
API
 ↓
Application
 ↓
Domain
 ↓
Data Access Interfaces
 ↓
Infrastructure Implementations
```

Supporting dependencies:

```text
Application / Domain
        ↓
Controlled Interfaces
        ↓
Infrastructure
```

The architecture must prevent:

```text
Route → random database operation
Route → provider SDK
Agent → database
Agent → API key
Frontend → provider
Domain → HTTP framework
```

---

# 46. Implementation Boundary

Phase 6 ends at architectural definition.

The following are now architecturally defined:

- backend structure
- modules
- layers
- database model
- APIs
- authentication
- authorization
- AI infrastructure
- agents
- RAG
- workers
- events
- integrations
- observability
- storage
- deployment
- infrastructure security

Implementation decisions that remain naturally adjustable include exact:

- package versions
- model identifiers
- deployment provider-specific settings
- worker library/runtime configuration
- exact SQL migration syntax
- exact frontend library implementation
- exact environment variable names where not contractually exposed
- operational thresholds
- test fixture values

These are implementation details, not reasons to reopen the architecture.

---

# 47. Explicit Non-Goals

Phase 6 does not require:

- microservices
- Kubernetes
- service mesh
- Kafka
- RabbitMQ
- event sourcing
- separate CQRS infrastructure
- GraphQL
- WebSockets initially
- custom model hosting
- custom vector database platform
- autonomous AI administration
- unrestricted SQL tools
- unrestricted global RAG retrieval
- user impersonation
- complex ML risk scoring
- custom distributed security platform
- unnecessary API gateway infrastructure
- unnecessary infrastructure duplication

---

# 48. Architecture Consistency Rules

Any future implementation must obey these rules.

### Rule 1 — Database Authority

PostgreSQL is authoritative for canonical structured state.

### Rule 2 — Domain Authority

Domain/application services own business transitions.

### Rule 3 — AI Boundary

AI proposes/produces structured outputs; deterministic services validate and persist.

### Rule 4 — Security Boundary

Authorization occurs before protected resource/tool/service execution.

### Rule 5 — Project Isolation

Every project-scoped operation verifies project ownership or authorized relationship.

### Rule 6 — Integration Boundary

External providers are accessed through adapters/gateways.

### Rule 7 — Async Boundary

Expensive long-running work executes through persistent workers.

### Rule 8 — Event Boundary

Events communicate meaningful state changes without becoming a second source of truth.

### Rule 9 — Document Boundary

Generated Markdown and RAG indexes are derived representations.

### Rule 10 — Observability Boundary

Telemetry does not grant data access.

---

# 49. Final Architecture Diagram

```text
                             GROWFLOW
                                |
          +---------------------+---------------------+
          |                                           |
       FRONTEND                                  ADMIN / MENTOR
          |                                           |
          +---------------- HTTPS --------------------+
                                |
                           FASTAPI API
                                |
                  Authentication / Authorization
                                |
                       Application Services
                                |
                         Domain Modules
                                |
             +------------------+------------------+
             |                  |                  |
          Repositories       AI Layer          Integrations
             |                  |                  |
        PostgreSQL          LangGraph           GitHub
        + Supabase          LangChain           Tavily
             |              LlamaIndex          OAuth
            RLS             Gateway             Email
             |                  |
             |            OpenRouter
             |
       Canonical State
             |
     +-------+--------+
     |                |
 Transactional     Storage
    Outbox           |
     |          Documents/Files
     |
   Events
     |
   Workers
     |
 +---+---------+----------------+
 |             |                |
 AI/RAG     GitHub/Email    Other Jobs
 |
 +-----------------------------+
 |
 Persisted Results
 |
 +-----------------------------+
 |                             |
 SSE                      Notifications
 |
 Observability
 |
 Logs + Metrics + Traces + LangSmith + Audit
```

---

# 50. Final Technology Responsibility Map

| Technology / Component | Final Responsibility |
|---|---|
| FastAPI | HTTP/API application boundary |
| Pydantic | Typed validation/contracts |
| PostgreSQL | Canonical relational state |
| Supabase | Managed DB/Auth/Storage platform capabilities |
| Repository layer | Persistence abstraction |
| LangGraph | Agent workflow/orchestration |
| LangChain | LLM/tool abstractions |
| LlamaIndex | RAG/document intelligence |
| LangSmith | AI/agent tracing and evaluation |
| OpenRouter | Initial AI provider/routing |
| AI Provider Gateway | Central provider/key/model boundary |
| Tavily | Current web research |
| GitHub API | Monitoring |
| OAuth Providers | External authentication |
| Object Storage | Large file/document storage |
| Transactional Outbox | Reliable event publication |
| Workers | Long-running asynchronous processing |
| SSE | AI/execution streaming |
| PostgreSQL RLS | Database defense-in-depth |
| Audit Service | Security-sensitive audit records |
| Observability | Runtime/AI/system visibility |

---

# 51. Final Responsibility Model

```text
Frontend
  → Interaction

API
  → Transport

Application
  → Use Cases

Domain
  → Business Rules + Canonical State Transitions

Repositories
  → Persistence

AI
  → Reasoning / Structured Proposals

Agents
  → Specialized AI Responsibilities

QA/Judge
  → AI Output Quality Gate

RAG
  → Project Knowledge Retrieval

Integrations
  → External Systems

Workers
  → Asynchronous Execution

Events
  → Internal Change Propagation

Observability
  → Visibility / Diagnosis

Security
  → Protection / Authorization Boundaries

PostgreSQL
  → Canonical Structured State
```

---

# 52. Phase 6 Completeness Check

| Architectural Area | Covered |
|---|---:|
| Backend structure | ✅ |
| Layering | ✅ |
| Database | ✅ |
| API | ✅ |
| Authentication | ✅ |
| Authorization | ✅ |
| AI provider infrastructure | ✅ |
| AI key pool | ✅ |
| Agent orchestration | ✅ |
| RAG | ✅ |
| Documents | ✅ |
| Workers | ✅ |
| Events | ✅ |
| Reliability | ✅ |
| External integrations | ✅ |
| Observability | ✅ |
| Storage | ✅ |
| Deployment/runtime | ✅ |
| Infrastructure security | ✅ |
| Testing/verification | ✅ |
| Admin boundary | ✅ |
| Cross-role architecture | ✅ |
| Project lifecycle | ✅ |
| State ownership | ✅ |
| Failure/recovery | ✅ |

---

# 53. Final Phase 6 Decision Set

The complete backend architecture is based on these final decisions:

1. **FastAPI + modular monolith**
2. **Layered backend architecture**
3. **PostgreSQL/Supabase canonical relational state**
4. **Repository/data-access pattern**
5. **Pydantic-first contracts**
6. **FastAPI dependency injection**
7. **Supabase Auth for authentication**
8. **RBAC + resource/project/group authorization**
9. **RLS as defense in depth**
10. **Central AI Provider Gateway**
11. **Exactly five provider keys**
12. **LangGraph for agent orchestration**
13. **LangChain for LLM/tool abstractions**
14. **LlamaIndex for RAG/document intelligence**
15. **LangSmith for AI observability/evaluation**
16. **Tavily for current research**
17. **Exactly twelve blueprint agents**
18. **QA/Judge as quality gate and regeneration controller**
19. **Project-scoped RAG**
20. **Typed AI tools**
21. **AI cannot directly mutate canonical state**
22. **Transactional outbox**
23. **Persistent background workers**
24. **SSE for initial streaming**
25. **Controlled external adapters**
26. **Centralized notifications/events**
27. **Structured observability**
28. **Secure storage/file architecture**
29. **Defense-in-depth infrastructure security**
30. **No unnecessary distributed infrastructure**

---

# 54. Final Architecture Freeze

With 6N, Phase 6 establishes the complete architectural baseline:

```text
6A Backend
      +
6B Database
      +
6C API
      +
6D Authentication & Security
      +
6E AI Infrastructure
      +
6F Agent Execution
      +
6G RAG & Documents
      +
6H Jobs & Events
      +
6I External Integrations
      +
6J Observability
      +
6K Storage & Files
      +
6L Deployment & Runtime
      +
6M Infrastructure Security
      ↓
6N FINAL CONSOLIDATION
      ↓
╔══════════════════════════════════════════════╗
║        GROWFLOW PHASE 6 — FROZEN           ║
║     BACKEND & PLATFORM ARCHITECTURE        ║
╚══════════════════════════════════════════════╝
```

---

# 55. Freeze Statement

**Phase 6 — Backend & Platform Architecture is now architecturally finalized.**

The architecture is intentionally:

- secure
- modular
- testable
- observable
- recoverable
- project-isolated
- AI-enabled
- integration-ready
- deployment-ready
- implementation-oriented without being implementation itself

The architecture does **not** require reopening previously frozen product decisions.

Future implementation work must conform to this architecture unless a deliberate architectural change is formally introduced and documented.

> **The purpose of Phase 6 is complete: GrowFlow now has one coherent backend and platform architecture from API boundary to database, AI execution, RAG, integrations, workers, storage, observability, deployment, and infrastructure security.**

**PHASE 6 — FINAL / FROZEN**
