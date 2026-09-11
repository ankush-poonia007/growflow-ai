# GrowFlow — Part 6A Backend Architecture

**Status:** FROZEN  
**Part:** 6A — Backend Architecture  
**Project:** GrowFlow

## 1. Purpose

Part 6A translates the frozen Part 5 application architecture into a concrete backend engineering architecture. It defines the backend structure, layers, module boundaries, services, repositories, configuration, validation, dependency injection, responses, errors, security boundaries, AI boundaries, asynchronous work, testing, and coding standards.

This document is the engineering contract for Parts 6B–6N.

## 2. Frozen Decisions

- FastAPI
- Modular Monolith
- Layered architecture
- Repository/Data Access pattern
- Pydantic-first contracts
- FastAPI Dependency Injection
- Centralized typed configuration
- `settings.py` as the application configuration interface
- No direct `.env` access in application/business code
- Single Responsibility
- Class-based architecture by default
- Canonical API responses
- Centralized exception handling
- Strong typing
- Thin API routes
- Explicit dependency direction
- No God classes/services
- External systems behind adapters/interfaces
- AI cannot directly mutate authoritative core state
- SSE for initial streaming
- No unnecessary distributed infrastructure

## 3. Core Architecture

GrowFlow is a modular monolith with explicit internal boundaries:

```text
Frontend
  ↓
FastAPI API
  ↓
Application Layer
  ↓
Domain Layer
  ↓
Repository / Integration Interfaces
  ↓
Infrastructure
  ↓
PostgreSQL/Supabase + External Providers
```

The application remains one deployable backend initially. Internal modules are organized by business capability rather than by deployable service.

## 4. Layer Responsibilities

### API / Presentation
Owns HTTP, routing, request parsing, Pydantic validation, authentication/authorization dependencies, serialization, HTTP status codes, and transport-specific behavior.

Routes must not contain business logic, database queries, AI calls, GitHub calls, or complex orchestration.

### Application
Owns use cases and orchestration such as CreateProject, StartAssessment, SubmitAssessmentAnswer, GenerateBlueprint, CompleteTask, CreateHelpRequest, and GenerateAIResponse.

### Domain
Owns GrowFlow business concepts and deterministic rules: users, groups, projects, assessments, blueprints, features, specifications, MVPs, duration, risks, tasks, milestones, progress, phases, health, communication, documents, and AI execution state.

### Infrastructure
Implements persistence, external provider adapters, AI gateways, RAG, storage, email, observability, and other technical concerns.

## 5. Target Backend Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── environments.py
│   │   └── validators.py
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies/
│   │   ├── schemas/
│   │   └── responses/
│   ├── application/
│   │   ├── services/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── use_cases/
│   ├── domain/
│   │   ├── identity/
│   │   ├── organization/
│   │   ├── project/
│   │   ├── planning/
│   │   ├── execution/
│   │   ├── communication/
│   │   ├── knowledge/
│   │   ├── integrations/
│   │   ├── ai/
│   │   └── platform/
│   ├── infrastructure/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── ai/
│   │   ├── github/
│   │   ├── tavily/
│   │   ├── rag/
│   │   ├── storage/
│   │   ├── email/
│   │   └── observability/
│   ├── workers/
│   └── shared/
│       ├── exceptions/
│       ├── logging/
│       ├── security/
│       ├── events/
│       ├── utilities/
│       └── constants/
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

This is the target logical structure. Empty folders are not created merely for appearance; modules are introduced as functionality is implemented.

## 6. Domain Modules

The backend remains aligned with Part 5F:

- Identity & Access
- Organization
- Project
- Planning
- Execution
- Communication
- Knowledge
- Integrations
- AI
- Platform
- Observability

These are internal business modules, not microservices.

## 7. Repository Architecture

Persistence is isolated behind repositories such as:

- UserRepository
- GroupRepository
- ProjectRepository
- AssessmentRepository
- BlueprintRepository
- TaskRepository
- MilestoneRepository
- RiskRepository
- DocumentRepository
- NotificationRepository

Application/domain code depends on repository contracts. Infrastructure implements them.

Repositories own persistence access but do not own unrelated business rules, notifications, AI calls, or HTTP formatting.

## 8. Command / Query Separation

Logical CQ separation is used without separate CQRS infrastructure.

Commands change state:

- CreateProject
- UpdateProject
- CompleteTask
- CreateRisk
- GenerateBlueprint
- ResolveHelpRequest

Queries read state:

- GetProject
- GetStudentDashboard
- GetMentorOverview
- GetAtRiskStudents
- GetProjectRisks
- GetProjectActivity

## 9. Class-Based Architecture

Architectural components use classes by default:

- ProjectService
- ProjectRepository
- AssessmentService
- BlueprintService
- RiskService
- TaskService
- NotificationService
- AIExecutionService
- GitHubAdapter
- TavilyAdapter
- OpenRouterGateway

Classes must not be created artificially for trivial constants or transformations.

## 10. Single Responsibility

Single Responsibility is a hard engineering rule.

Examples:

```text
project_service.py
project_repository.py
project_schema.py
project_router.py
project_authorization.py
```

Avoid generic dumping-ground files such as `misc.py`, `stuff.py`, or giant `utils.py` modules.

No file or class should accumulate unrelated responsibilities.

## 11. No God Classes or Services

Prohibited:

```text
MegaProjectService
  ├── CRUD
  ├── Assessment
  ├── Blueprint
  ├── GitHub
  ├── RAG
  ├── Notifications
  └── AI
```

Use focused components such as ProjectService, AssessmentService, BlueprintService, RiskService, TaskService, DocumentService, NotificationService, and AIExecutionService.

## 12. Pydantic Architecture

Pydantic is used for important boundaries:

- API request models
- API response models
- query/path validation
- configuration
- AI structured outputs
- agent input/output contracts
- tool contracts
- event payloads
- internal boundary objects where useful

AI output follows:

```text
LLM
 ↓
Structured Output
 ↓
Pydantic Validation
 ↓
QA/Judge
 ↓
Deterministic Domain Service
 ↓
Persistence
```

Raw, unvalidated LLM output is never authoritative project state.

## 13. Strong Typing

Use explicit typing for parameters, return values, collections, enums, configuration, and architectural contracts where useful.

Avoid unnecessary `Any`, untyped dictionaries, and implicit contracts.

## 14. Configuration Architecture

`.env` is a configuration source, not an application API.

Application code must not repeatedly read `.env` or use environment-variable APIs throughout the codebase.

```text
.env / deployment environment
        ↓
Settings Loader
        ↓
Typed Settings
        ↓
Dependency Injection
        ↓
Application Components
```

## 15. `settings.py`

`settings.py` is the central typed configuration interface.

Logical configuration groups:

```text
Settings
├── ApplicationSettings
├── DatabaseSettings
├── SecuritySettings
├── OAuthSettings
├── AISettings
├── GitHubSettings
├── TavilySettings
├── StorageSettings
├── EmailSettings
├── ObservabilitySettings
└── WorkerSettings
```

Exact fields are finalized as later infrastructure phases establish their requirements.

## 16. Configuration Lifecycle

Configuration is loaded and validated at startup:

```text
Application Startup
 ↓
Load Configuration
 ↓
Validate Configuration
 ↓
Construct Settings
 ↓
Start Application
```

Invalid required configuration should fail fast rather than causing delayed runtime failures.

## 17. Secret Management

Secrets include database credentials, JWT/session secrets, OAuth secrets, AI keys, GitHub secrets, Tavily credentials, email credentials, and storage credentials.

Rules:

- never hard-code secrets
- never commit `.env`
- maintain `.env.example`
- never log secrets
- never return secrets through APIs
- never expose secrets to frontend code
- never expose actual provider keys in Admin UI
- use deployment secret/environment facilities in production

The five AI keys are handled by the AI Provider Gateway/key pool.

## 18. Dependency Injection

FastAPI Dependency Injection supplies controlled dependencies such as:

- current authenticated user
- authorization context
- settings
- database sessions/connections
- repositories
- application services
- integration clients

Dependencies remain explicit and testable.

## 19. Authorization Boundary

The authorization chain is:

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
```

This applies to normal APIs and AI tools.

## 20. Resource Isolation

Project-sensitive operations enforce appropriate user, role, group, project, project-instance, and ownership scope.

Project A data must never leak into Project B through APIs, repositories, AI tools, RAG, documents, GitHub data, or background jobs.

## 21. Response Architecture

Normal JSON APIs use a canonical contract:

```json
{
  "success": true,
  "message": "Project created successfully.",
  "data": {},
  "metadata": {}
}
```

Errors use:

```json
{
  "success": false,
  "message": "Project could not be created.",
  "data": null,
  "error": {
    "code": "PROJECT_CREATION_FAILED",
    "details": []
  }
}
```

Special transports retain appropriate protocols:

- JSON → standard API response
- SSE → event-stream contract
- File → file response
- Health → health contract

## 22. Exception Architecture

Typed exceptions:

```text
GrowFlowException
├── ValidationException
├── AuthenticationException
├── AuthorizationException
├── NotFoundException
├── ConflictException
├── BusinessRuleException
├── IntegrationException
├── AIException
├── RAGException
├── StorageException
└── InfrastructureException
```

Application/domain components raise meaningful exceptions. Global handlers translate them into safe API responses.

## 23. Error Codes

Machine-readable codes include:

```text
AUTH_INVALID_CREDENTIALS
AUTH_UNAUTHORIZED
PROJECT_NOT_FOUND
PROJECT_ACCESS_DENIED
PROJECT_INVALID_STATE
TASK_NOT_FOUND
TASK_ALREADY_COMPLETED
BLUEPRINT_GENERATION_FAILED
AI_PROVIDER_UNAVAILABLE
RAG_RETRIEVAL_FAILED
GITHUB_INTEGRATION_FAILED
DOCUMENT_NOT_FOUND
```

Unexpected exceptions are logged centrally and returned as safe generic errors without leaking internal details.

## 24. Middleware

Middleware remains intentionally small and may include:

- correlation/request ID
- request logging
- request timing
- CORS
- security headers
- exception propagation

Business logic does not belong in middleware.

## 25. Correlation IDs

Important operations should be traceable:

```text
HTTP Request
 ↓
Application Service
 ↓
Database Operations
 ↓
AI Execution
 ↓
Agent Execution
 ↓
RAG Operations
 ↓
Events
 ↓
Logs
```

Correlation IDs and execution IDs are propagated where appropriate.

## 26. Transactions

Transactions are organized around meaningful business operations.

Example:

```text
Complete Task
 ↓
Validate
 ↓
Update Task
 ↓
Recalculate Milestone
 ↓
Recalculate Progress
 ↓
Evaluate Phase
 ↓
Evaluate Health
 ↓
Create Event
 ↓
Commit
```

Exact PostgreSQL transaction and RLS behavior is finalized in Part 6B.

## 27. Deterministic State Boundary

Authoritative state follows:

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

AI may analyze, recommend, explain, generate, and identify risks, but it cannot arbitrarily overwrite authoritative state.

## 28. AI Boundary

AI execution follows:

```text
Application Use Case
 ↓
AI Orchestrator
 ↓
Agent
 ↓
Authorized Tools
 ↓
DB / RAG / GitHub / Web
 ↓
LLM Provider Gateway
 ↓
Structured Pydantic Output
 ↓
Validation
 ↓
QA/Judge
 ↓
Deterministic Domain Service
 ↓
Database
```

Agents do not receive unrestricted database access.

## 29. AI Provider Gateway

Model access is centralized:

```text
AI Service
 ↓
AI Provider Gateway
 ↓
Key Pool
 ├── K1
 ├── K2
 ├── K3
 ├── K4
 └── K5
 ↓
OpenRouter / Provider
 ↓
Model
```

The gateway owns provider communication, key selection/health, rotation, retry behavior, rate-limit handling, timeout behavior, provider errors, and model selection policy.

Other application components do not select keys directly.

## 30. External Integrations

External providers are accessed through interfaces/adapters:

```text
Application
 ↓
Interface
 ↓
Adapter / Gateway
 ↓
External Provider
```

Examples:

- GitHubAdapter
- TavilyAdapter
- EmailAdapter
- StorageAdapter
- OpenRouterGateway

Provider-specific implementation must not spread through business logic.

## 31. RAG Boundary

```text
Upload
 ↓
Document Service
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
AI
```

Retrieval always enforces authorization and project scope.

## 32. Synchronous vs Asynchronous Work

Synchronous operations:

- authentication
- simple reads
- simple CRUD
- permission checks
- small state changes

Background operations:

- blueprint generation
- agent workflows
- long AI generation
- document parsing
- embedding
- RAG indexing
- GitHub synchronization
- email delivery
- long-running integrations

## 33. Browser Independence

Long-running work continues after browser disconnection.

```text
Generate Blueprint
 ↓
Execution Created
 ↓
Worker Starts
 ↓
Browser Disconnects
 ↓
Worker Continues
 ↓
Execution State Persisted
 ↓
Student Reconnects
 ↓
Current State Retrieved
```

## 34. SSE

SSE is the initial streaming mechanism for AI and long-running execution progress.

```text
Frontend
  | SSE
  v
FastAPI
  ↓
Execution State / Event Stream
```

WebSockets are not introduced unless a demonstrated requirement emerges.

## 35. Logging

Structured logs should include, where appropriate:

- timestamp
- level
- module
- event
- correlation ID
- execution ID
- user ID
- project ID
- duration
- error code

Never log passwords, API keys, OAuth tokens, or unnecessary private content.

## 36. Testing

```text
tests/
├── unit/
├── integration/
├── api/
└── e2e/
```

### Unit
Domain rules, services, validators, calculations, authorization.

### Integration
Repositories, database behavior, external adapters, AI gateway, RAG.

### API
Authentication, authorization, validation, response contracts, HTTP behavior.

### E2E
Complete workflows from registration through project execution.

## 37. API Versioning

Initial namespace:

```text
/api/v1/
```

Examples:

```text
/api/v1/auth
/api/v1/projects
/api/v1/assessments
/api/v1/blueprints
/api/v1/tasks
/api/v1/risks
/api/v1/ai
```

The detailed endpoint catalogue is Part 6C.

## 38. Shared Role Architecture

Student, Mentor, and Admin applications use shared backend domain services where the underlying business operation is shared.

Authorization determines permitted operations and visibility.

Do not duplicate business logic merely because the caller has a different role.

## 39. Admin Boundary

Admin capabilities follow the frozen Part 5 privacy model:

```text
Default:
Metadata-first / operational visibility

Deeper inspection:
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

Admin has no unrestricted private-data access and no impersonation capability.

## 40. Events

Lightweight internal events remain part of the modular monolith.

Examples:

- TaskCompleted
- MilestoneCompleted
- ProjectProgressChanged
- ProjectPhaseChanged
- ProjectHealthChanged
- RiskCreated/Updated/Resolved
- HelpRequestCreated/Resolved
- MentorNoteCreated
- BlueprintGenerationStarted/Completed
- AgentExecutionCompleted
- GitHubActivityDetected
- DocumentProcessed
- RAGIndexUpdated
- SecurityEventDetected
- AccountStatusChanged

Detailed worker/event infrastructure is Part 6H.

## 41. Failure Handling

External and background operations use:

- timeouts
- controlled retries
- idempotency where appropriate
- failure isolation
- persisted execution state
- meaningful error states
- structured logs
- correlation IDs

Retries must not blindly duplicate state changes.

## 42. File and Document Boundary

Documents are managed by the Document Service.

The backend distinguishes:

- canonical structured state
- generated Markdown representations
- uploaded files
- processed document content
- RAG index data

Generated documents are representations of canonical state, not the source of truth.

## 43. Coding Standards

1. Single Responsibility.
2. High cohesion.
3. Low coupling.
4. Strong typing.
5. Pydantic at important boundaries.
6. Explicit dependencies.
7. Thin routers.
8. Focused services.
9. Focused repositories.
10. Typed exceptions.
11. Canonical response handling.
12. Structured logging.
13. No hard-coded secrets.
14. No direct `.env` access from business/application code.
15. No hidden side effects.
16. Explicit transaction boundaries.
17. Idempotency where retries are possible.
18. Testable components.
19. Provider abstraction.
20. Authorization before resource/tool execution.
21. Project isolation at every relevant boundary.
22. AI output is never authoritative without validation/QA.
23. Avoid unnecessary abstractions.
24. Avoid premature infrastructure.
25. Keep implementation aligned with frozen architecture.

## 44. Prohibited Patterns

### Architecture
- Microservices without a demonstrated requirement
- Kafka by default
- Kubernetes by default
- Service mesh
- Event sourcing
- Distributed CQRS infrastructure
- Premature WebSockets
- Custom model hosting
- Unnecessary databases

### Code
- Business logic in routers
- Database access in routers
- Direct provider calls from domain logic
- Direct `.env` access throughout application code
- Hard-coded secrets
- Giant utility/dumping-ground modules
- God classes
- God services
- Unexplained `Any`
- Duplicated role-specific business logic

### AI
- Unrestricted database access
- Unrestricted project access
- AI directly changing authoritative state
- Persisting raw unvalidated LLM output
- Bypassing required QA
- Bypassing authorization through tools

## 45. Final Request Lifecycle

```text
HTTP Request
 ↓
FastAPI Router
 ↓
Pydantic Request Validation
 ↓
Authentication
 ↓
Authorization
 ↓
Application Use Case
 ↓
Domain Logic
 ↓
Repository / Integration Interface
 ↓
Infrastructure
 ↓
Database / External System
 ↓
Domain Result
 ↓
Pydantic Response Model
 ↓
Canonical API Response
 ↓
HTTP Response
```

## 46. Final AI Lifecycle

```text
Request
 ↓
Authentication
 ↓
Authorization
 ↓
Application Use Case
 ↓
AI Orchestrator
 ↓
Agent
 ↓
Authorized Tools
 ↓
DB / RAG / GitHub / Web
 ↓
Provider Gateway
 ↓
Structured Output
 ↓
Pydantic Validation
 ↓
QA/Judge
 ↓
Deterministic Domain Service
 ↓
Transaction
 ↓
Database
```

## 47. Deferred Decisions

### 6B — Database
Schema, tables, relationships, keys, constraints, indexes, PostgreSQL/Supabase behavior, RLS, migrations, transaction implementation, event/audit/versioning tables.

### 6C — API
Complete endpoint catalogue, schemas, pagination, filtering, sorting, status codes, error catalogue, SSE contracts.

### 6D — Authentication & Security
Password hashing, sessions/tokens, OAuth, JWT/session lifecycle, refresh/revocation, CORS/CSRF, headers, authorization implementation.

### 6E — AI Infrastructure
OpenRouter implementation, model configuration, five-key pool, rate limits, provider fallback, token/cost tracking.

### 6F — Agent Infrastructure
LangGraph execution, agent state, orchestration, parallelism, checkpoints, retries, recovery, QA/Judge execution.

### 6G — RAG & Documents
Parsing, chunking, embeddings, vector storage, retrieval, metadata, isolation, document processing.

### 6H — Jobs & Events
Worker/queue strategy, job state, retries, dead-letter behavior, event dispatch and handlers.

### 6I — Integrations
GitHub, Tavily, OAuth providers, email, storage, provider adapters.

### 6J — Observability
Metrics, traces, LangSmith, dashboards, logging, AI observability.

### 6K — Storage
File storage, document storage, generated artifacts, upload/download lifecycle.

### 6L — Deployment
Runtime, environments, deployment topology, CI/CD, production configuration, scaling.

### 6M — Infrastructure Security
Network security, secret management, production hardening and infrastructure access policies.

### 6N — Finalization
Cross-phase consistency, dependency map, architecture review, implementation boundary, final freeze.

## 48. Final 6A Architecture Map

```text
                    GROWFLOW BACKEND
                           |
                           v
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           |
                           v
                  ┌──────────────────┐
                  │ Application Layer│
                  │ Commands / Query │
                  │ Use Cases/Service│
                  └────────┬─────────┘
                           |
                           v
                    ┌─────────────┐
                    │Domain Layer │
                    └──────┬──────┘
                           |
             ┌─────────────┴─────────────┐
             v                           v
       Repositories                 Adapters/Gateways
             |                           |
             v                           v
     PostgreSQL/Supabase          AI/GitHub/Tavily/
                                  Email/Storage/etc.

Cross-cutting:
Configuration / Security / Logging /
Exceptions / Events / Observability
```

## 49. Freeze Statement

**Part 6A — Backend Architecture is COMPLETE and FROZEN.**

GrowFlow will use a FastAPI modular monolith with domain-oriented layered architecture, thin routes, application use cases, deterministic domain services, repository-based persistence, Pydantic contracts, centralized typed configuration through `settings.py`, dependency injection, canonical responses, centralized typed errors, structured logging, correlation IDs, controlled asynchronous execution, adapter-based integrations, strict authorization and project isolation, project-scoped RAG, and a controlled AI boundary.

Unnecessary distributed infrastructure is explicitly excluded.

This document is the backend engineering foundation for Parts 6B–6N.
