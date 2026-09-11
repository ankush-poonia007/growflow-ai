# GrowFlow — Part 6C: API Architecture
## Final Frozen Specification

**Project:** GrowFlow  
**Part:** 6C — API Architecture  
**Status:** FROZEN  
**Framework:** FastAPI  
**API Style:** REST-oriented  
**API Version:** `/api/v1`  
**Streaming:** Server-Sent Events (SSE)  
**Architecture:** Modular Monolith + Layered Architecture

---

# 1. Purpose

Part 6C defines GrowFlow's complete API architecture and contract between the frontend and the application/domain layers.

The API is responsible for HTTP transport, request validation, authentication context, authorization dependencies, serialization, error translation, pagination, API versioning, and streaming.

Business logic remains in application/domain services.

The API must not become a second business-logic layer.

---

# 2. Core API Architecture

The canonical request path is:

```text
Frontend
   ↓
FastAPI API
   ↓
Dependencies / Authentication / Authorization
   ↓
Pydantic Validation
   ↓
Application Commands / Queries
   ↓
Domain Services
   ↓
Repositories / Data Access
   ↓
PostgreSQL / Supabase
```

AI and long-running operations use:

```text
Frontend
   ↓
FastAPI API
   ↓
Application Service
   ↓
AI Orchestrator
   ↓
Agents / Tools
   ↓
Pydantic Validation
   ↓
QA / Judge
   ↓
Domain Service
   ↓
Repository
   ↓
PostgreSQL
```

---

# 3. API Goals

The GrowFlow API must be:

- REST-oriented for normal application operations
- versioned
- strongly typed
- resource-oriented
- authorization-aware
- consistent in response structure
- predictable in error handling
- suitable for frontend consumption
- suitable for long-running AI operations
- observable through correlation IDs
- independent of frontend implementation
- independent of specific external providers
- safe to retry where appropriate

---

# 4. API Versioning

The initial API namespace is:

```text
/api/v1
```

Examples:

```text
/api/v1/auth/login
/api/v1/projects
/api/v1/projects/{project_id}
/api/v1/projects/{project_id}/tasks
/api/v1/projects/{project_id}/ai/executions
```

Breaking API changes should use a new major version such as `/api/v2`.

Existing API behavior must not silently change in a breaking manner.

---

# 5. API Module Structure

Logical API organization:

```text
app/
└── api/
    ├── routes/
    │   ├── auth.py
    │   ├── users.py
    │   ├── students.py
    │   ├── mentors.py
    │   ├── admins.py
    │   ├── groups.py
    │   ├── projects.py
    │   ├── assessments.py
    │   ├── blueprints.py
    │   ├── features.py
    │   ├── specifications.py
    │   ├── mvps.py
    │   ├── timelines.py
    │   ├── risks.py
    │   ├── tasks.py
    │   ├── milestones.py
    │   ├── communications.py
    │   ├── notifications.py
    │   ├── documents.py
    │   ├── rag.py
    │   ├── github.py
    │   ├── ai.py
    │   ├── events.py
    │   ├── observability.py
    │   └── health.py
    │
    ├── schemas/
    ├── dependencies/
    ├── responses/
    └── middleware/
```

This is a logical organization. Files should be created when they have meaningful responsibility rather than creating empty or artificial modules.

---

# 6. REST Resource Model

Core API resources:

```text
users
students
mentors
groups
group-memberships

project-definitions
project-definition-versions
project-instances

assessments
assessment-questions
assessment-answers

blueprints
blueprint-versions
project-profiles
project-technologies
features
feature-specifications
mvps
timelines
timeline-phases
research-sources

tasks
milestones
risks
risk-history

project-change-requests

mentor-notes
help-requests
help-request-messages
notifications

documents
document-versions
rag

github-connections
github-repositories
github-activity

ai-executions
agent-executions
ai-quality-results

domain-events
audit-events
admin-investigations
```

---

# 7. HTTP Method Rules

Standard semantics:

| Method | Purpose |
|---|---|
| GET | Retrieve |
| POST | Create or initiate an operation |
| PUT | Full replacement where appropriate |
| PATCH | Partial update |
| DELETE | Delete where domain rules permit |

Meaningful state transitions may use explicit command/action endpoints.

Examples:

```text
POST /projects/{id}/tasks/{task_id}/complete
POST /projects/{id}/tasks/{task_id}/block
POST /projects/{id}/help-requests/{id}/resolve
POST /projects/{id}/assessment/start
POST /projects/{id}/assessment/answers
POST /projects/{id}/blueprint/generate
POST /projects/{id}/change-requests
POST /projects/{id}/change-requests/{id}/confirm
```

This avoids abusing generic PATCH requests for important business transitions.

---

# 8. Command and Query Separation

GrowFlow uses logical Command/Query separation without introducing separate CQRS infrastructure.

## Queries

Read-only:

```text
GET /projects
GET /projects/{id}
GET /projects/{id}/tasks
GET /projects/{id}/risks
GET /notifications
GET /groups/{id}/students
```

## Commands

State-changing:

```text
POST /projects
POST /projects/{id}/tasks/{task_id}/complete
POST /projects/{id}/assessment/start
POST /projects/{id}/blueprint/generate
POST /help-requests
```

Queries must not mutate authoritative state.

Commands must pass through application/domain rules.

---

# 9. Authentication APIs

Core endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
POST /api/v1/auth/password/change
POST /api/v1/auth/password/forgot
POST /api/v1/auth/password/reset
```

OAuth:

```text
GET /api/v1/auth/oauth/google
GET /api/v1/auth/oauth/google/callback

GET /api/v1/auth/oauth/github
GET /api/v1/auth/oauth/github/callback
```

Exact authentication/session mechanics are finalized in the dedicated security/authentication phase.

The API consumes the authenticated identity/context rather than implementing authentication logic inside every route.

---

# 10. User and Profile APIs

Examples:

```text
GET   /users/me
PATCH /users/me

GET   /students/me
PATCH /students/me

GET   /mentors/me
PATCH /mentors/me

GET   /users/me/preferences
PATCH /users/me/preferences
```

Administrative account management:

```text
GET  /admin/users
GET  /admin/users/{user_id}
POST /admin/users/{user_id}/activate
POST /admin/users/{user_id}/deactivate
POST /admin/users/{user_id}/suspend
GET  /admin/users/{user_id}/history
```

No impersonation endpoint exists.

---

# 11. Group APIs

Mentor group management:

```text
POST /groups
GET  /groups
GET  /groups/{group_id}
PATCH /groups/{group_id}
```

Student joining:

```text
POST /groups/join
```

Group information:

```text
GET /groups/{group_id}/students
GET /groups/{group_id}/activity
```

Group management remains intentionally minimal.

---

# 12. Project Definition APIs

Mentor-owned reusable project definitions:

```text
POST /project-definitions
GET  /project-definitions
GET  /project-definitions/{definition_id}
PATCH /project-definitions/{definition_id}
POST /project-definitions/{definition_id}/archive
```

Versions:

```text
GET /project-definitions/{definition_id}/versions
GET /project-definitions/{definition_id}/versions/{version_id}
```

Assignment:

```text
POST /project-definitions/{definition_id}/assign
```

Assignment creates an independent Project Instance.

---

# 13. Project Instance APIs

Core:

```text
POST /projects
GET  /projects
GET  /projects/{project_id}
PATCH /projects/{project_id}
```

Student-created projects can provide:

```text
name
complexity
problem
proposed_solution
technologies
duration
deadline
github
```

Mentor-defined projects are created through assignment:

```text
POST /project-definitions/{definition_id}/assign
```

Both paths produce an independent Project Instance and enter the assessment workflow.

---

# 14. Project Overview API

A dashboard should not require the frontend to make many unrelated requests.

GrowFlow therefore provides an aggregated project query:

```text
GET /projects/{project_id}/overview
```

The response may include:

- project identity
- progress
- phase
- health
- deadline
- days remaining
- current milestone
- task summary
- risk summary
- blocked tasks
- technologies
- GitHub summary
- recent activity
- next recommended action

Aggregation is performed by an application/query service.

The route itself does not contain the aggregation business logic.

---

# 15. Assessment APIs

Start:

```text
POST /projects/{project_id}/assessment/start
```

Current question:

```text
GET /projects/{project_id}/assessment/current
```

Submit answer:

```text
POST /projects/{project_id}/assessment/answers
```

Assessment status:

```text
GET /projects/{project_id}/assessment
```

Result:

```text
GET /projects/{project_id}/assessment/result
```

The server determines the next question.

The frontend does not determine whether a question is CORE or DYNAMIC.

---

# 16. Adaptive Assessment API Flow

```text
POST /assessment/start
        ↓
Server creates assessment
        ↓
GET current question
        ↓
Student submits answer
        ↓
Server validates answer
        ↓
Determine next question
        ↓
If dynamic, generate from accumulated context
        ↓
Persist question
        ↓
Return next question
```

The backend retains:

- previous answers
- question order
- question type
- generated-from relationship
- accumulated context
- generation metadata

---

# 17. Blueprint APIs

Generation:

```text
POST /projects/{project_id}/blueprint/generate
```

Current blueprint:

```text
GET /projects/{project_id}/blueprint
```

Generation status:

```text
GET /projects/{project_id}/blueprint/status
```

Versions:

```text
GET /projects/{project_id}/blueprint/versions
GET /projects/{project_id}/blueprint/versions/{version_id}
```

Blueprint regeneration is a controlled workflow and does not silently overwrite authoritative state.

---

# 18. Long-Running Blueprint Generation

Blueprint generation is asynchronous.

Initial request:

```text
POST /projects/{project_id}/blueprint/generate
```

Conceptual response:

```json
{
  "success": true,
  "message": "Blueprint generation started.",
  "data": {
    "execution_id": "uuid",
    "status": "QUEUED"
  },
  "metadata": {}
}
```

The frontend then observes execution progress through the execution/SSE APIs.

---

# 19. AI Execution APIs

Top-level execution:

```text
GET /ai/executions/{execution_id}
GET /ai/executions/{execution_id}/agents
GET /ai/executions/{execution_id}/quality
GET /ai/executions/{execution_id}/events
GET /ai/executions/{execution_id}/stream
POST /ai/executions/{execution_id}/cancel
```

Execution state is persistent and independent of the browser.

---

# 20. SSE Streaming

GrowFlow initially uses Server-Sent Events.

Example:

```text
GET /api/v1/ai/executions/{execution_id}/stream
```

Possible event types:

```text
execution.started
agent.started
agent.progress
agent.completed
qa.started
qa.completed
execution.completed
execution.failed
```

Conceptual event:

```text
event: agent.progress
data: {
  "execution_id": "...",
  "agent": "technology",
  "message": "Evaluating technology choices..."
}
```

SSE is a transport mechanism only.

Execution state remains persisted in PostgreSQL.

---

# 21. AI Mentor API

Project AI Mentor:

```text
POST /projects/{project_id}/ai/chat
```

Request:

```json
{
  "message": "Why is my implementation phase at risk?"
}
```

The server determines the appropriate sources:

```text
Structured DB
RAG
GitHub
LLM reasoning
Combined sources
```

The AI tool layer enforces project/group/user authorization.

The client cannot use the AI endpoint to request arbitrary database records.

---

# 22. AI Action Confirmation

AI-generated state changes follow:

```text
AI Response
   ↓
Proposed Action
   ↓
User Confirmation
   ↓
Command API
   ↓
Application Service
   ↓
Domain Validation
   ↓
Persistence
```

Example:

```text
POST /projects/{project_id}/ai/actions/{action_id}/confirm
```

AI cannot directly mutate authoritative project state.

---

# 23. Task APIs

Collection:

```text
GET  /projects/{project_id}/tasks
POST /projects/{project_id}/tasks
```

Individual:

```text
GET   /projects/{project_id}/tasks/{task_id}
PATCH /projects/{project_id}/tasks/{task_id}
```

State transitions:

```text
POST /projects/{project_id}/tasks/{task_id}/start
POST /projects/{project_id}/tasks/{task_id}/complete
POST /projects/{project_id}/tasks/{task_id}/block
POST /projects/{project_id}/tasks/{task_id}/cancel
```

Task completion passes through deterministic execution rules.

---

# 24. Milestone APIs

```text
GET /projects/{project_id}/milestones
GET /projects/{project_id}/milestones/{milestone_id}

POST /projects/{project_id}/milestones/{milestone_id}/start
POST /projects/{project_id}/milestones/{milestone_id}/complete
POST /projects/{project_id}/milestones/{milestone_id}/block
```

Milestone state is validated against authoritative task/execution state where appropriate.

---

# 25. Risk APIs

```text
GET   /projects/{project_id}/risks
GET   /projects/{project_id}/risks/{risk_id}
POST  /projects/{project_id}/risks
PATCH /projects/{project_id}/risks/{risk_id}
```

State transitions:

```text
POST /projects/{project_id}/risks/{risk_id}/mitigate
POST /projects/{project_id}/risks/{risk_id}/resolve
POST /projects/{project_id}/risks/{risk_id}/accept
```

AI-generated risks must pass validation and the Risk domain service before becoming authoritative records.

---

# 26. Communication APIs

Mentor Notes:

```text
POST /projects/{project_id}/mentor-notes
GET  /projects/{project_id}/mentor-notes
```

Help Requests:

```text
POST /projects/{project_id}/help-requests
GET  /projects/{project_id}/help-requests
GET  /help-requests/{request_id}

POST /help-requests/{request_id}/messages
POST /help-requests/{request_id}/start
POST /help-requests/{request_id}/resolve
```

---

# 27. Notification APIs

```text
GET  /notifications
GET  /notifications/unread-count
POST /notifications/{notification_id}/read
POST /notifications/read-all
```

System notifications are generated centrally from domain events.

Clients do not directly create system notifications.

---

# 28. Document APIs

List:

```text
GET /projects/{project_id}/documents
```

Document:

```text
GET /projects/{project_id}/documents/{document_id}
```

Versions:

```text
GET /projects/{project_id}/documents/{document_id}/versions
GET /projects/{project_id}/documents/{document_id}/versions/{version_id}
```

Download:

```text
GET /projects/{project_id}/documents/{document_id}/download
```

Raw Markdown:

```text
GET /projects/{project_id}/documents/{document_id}/raw
```

Only the authorized document/version requested by the application contract is returned.

---

# 29. Document Viewer Contract

The frontend supports:

```text
View
Preview
Raw Markdown
Download
```

The API provides document metadata and content/reference information required for these modes.

Documents are not exposed as an unrestricted filesystem browser.

---

# 30. RAG APIs

RAG is primarily an internal service boundary.

Minimal project-scoped indexing endpoints may include:

```text
POST /projects/{project_id}/documents/{document_id}/index
GET  /projects/{project_id}/documents/{document_id}/index-status
```

There is no unrestricted user-facing vector-search endpoint.

AI retrieval occurs through authorized internal tools.

---

# 31. GitHub APIs

Connections:

```text
POST /github/connections
GET  /github/connections
DELETE /github/connections/{connection_id}
```

Repositories:

```text
POST /projects/{project_id}/github/repositories
GET  /projects/{project_id}/github/repositories
GET  /projects/{project_id}/github/repositories/{repository_id}
```

Activity:

```text
GET /projects/{project_id}/github/activity
```

GrowFlow provides GitHub monitoring only.

No repository-management/write APIs are exposed.

---

# 32. Student APIs

Student-specific projections:

```text
GET /students/me/dashboard
GET /students/me/projects
GET /students/me/activity
GET /students/me/mentor
GET /students/me/help-requests
```

These endpoints use shared domain/application services.

They do not duplicate project business logic.

---

# 33. Mentor APIs

Overview:

```text
GET /mentors/me/overview
```

Groups:

```text
GET /mentors/me/groups
```

Students:

```text
GET /mentors/me/students
GET /mentors/me/students/{student_id}
```

At-risk:

```text
GET /mentors/me/at-risk
```

Projects:

```text
GET /mentors/me/project-definitions
GET /mentors/me/project-instances
```

Mentor AI:

```text
POST /mentor/ai/chat
```

Underlying project/task/risk logic remains shared.

---

# 34. Admin APIs

Overview:

```text
GET /admin/overview
```

Platform resources:

```text
GET /admin/mentors
GET /admin/students
GET /admin/groups
GET /admin/projects
```

Project monitoring:

```text
GET /admin/projects/{project_id}
```

AI Observatory:

```text
GET /admin/ai/usage
GET /admin/ai/executions
GET /admin/ai/traces
GET /admin/ai/quality
```

System:

```text
GET /admin/system-health
GET /admin/documents-rag
GET /admin/cost-usage
GET /admin/security-audit
GET /admin/platform-analytics
```

---

# 35. Controlled Admin Investigation APIs

Protected/deeper inspection uses:

```text
POST /admin/investigations
GET  /admin/investigations
GET  /admin/investigations/{investigation_id}
POST /admin/investigations/{investigation_id}/authorize
POST /admin/investigations/{investigation_id}/complete
```

Inspection endpoints must verify an authorized investigation before exposing protected information.

There is no hidden administrative bypass.

---

# 36. Canonical Success Response

Normal responses use:

```json
{
  "success": true,
  "message": "Project retrieved successfully.",
  "data": {},
  "metadata": {}
}
```

---

# 37. Collection Response

Example:

```json
{
  "success": true,
  "message": "Projects retrieved successfully.",
  "data": [],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 42,
      "total_pages": 3
    }
  }
}
```

---

# 38. Canonical Error Response

```json
{
  "success": false,
  "message": "You do not have access to this project.",
  "data": null,
  "error": {
    "code": "PROJECT_ACCESS_DENIED",
    "details": []
  }
}
```

Machine-readable error codes are mandatory.

Internal stack traces and infrastructure details must not be exposed to clients.

---

# 39. HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 202 | Asynchronous operation accepted |
| 204 | Successful operation with no body |
| 400 | Invalid request |
| 401 | Unauthenticated |
| 403 | Unauthorized |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation failure |
| 429 | Rate limited |
| 500 | Internal error |
| 502 | External provider failure |
| 503 | Service unavailable |

The API must not return `200` for every failure.

---

# 40. Pagination

Collection endpoints support pagination where appropriate.

Standard parameters:

```text
?page=1&page_size=20
```

Response:

```json
{
  "page": 1,
  "page_size": 20,
  "total": 42,
  "total_pages": 3
}
```

The API validates page sizes and prevents pathological requests.

---

# 41. Filtering, Search, and Sorting

Resource-specific filters may include:

```text
?status=ACTIVE
?phase=IMPLEMENTATION
?health=AT_RISK
```

Sorting:

```text
?sort=created_at
?sort=-updated_at
```

Search:

```text
?search=python
```

Only approved fields may be used for sorting/filtering.

Clients cannot inject arbitrary SQL expressions through query parameters.

---

# 42. Pydantic Validation

Pydantic is used for:

- request bodies
- query parameters
- path parameters where useful
- response contracts
- AI structured outputs
- agent contracts
- tool contracts
- internal boundaries where useful

Conceptual flow:

```text
HTTP Request
     ↓
Pydantic Request Schema
     ↓
Application Command
     ↓
Domain Logic
```

Invalid input does not reach business logic.

---

# 43. API Dependency Injection

FastAPI dependency injection provides controlled access to:

```text
CurrentUser
AuthorizationContext
DatabaseSession
Settings
Repositories
ApplicationServices
IntegrationClients
```

Conceptual chain:

```text
require_authenticated_user
        ↓
require_role
        ↓
require_resource_access
        ↓
require_action_permission
```

The exact security dependency implementation belongs to the security/authentication phase.

---

# 44. Resource Authorization

Authentication alone is insufficient.

Project access follows:

```text
Authenticated?
    ↓
Correct role?
    ↓
Relationship to resource?
    ↓
Correct project/group scope?
    ↓
Action permitted?
    ↓
Privacy rules satisfied?
    ↓
Execute
```

The same model applies to:

- API endpoints
- AI tools
- RAG retrieval
- GitHub integration
- Admin investigation

---

# 45. AI API Security

AI endpoints must never blindly accept arbitrary:

```text
table_name
SQL
project_id
document_id
vector namespace
GitHub repository ID
```

and execute them.

Instead:

```text
AI Request
 ↓
Authorized AI Orchestrator
 ↓
Typed Tool
 ↓
Authorization
 ↓
Application/Domain Service
 ↓
Repository
```

The model is never granted unrestricted database access.

---

# 46. Idempotency

Retryable state-changing requests should support idempotency.

Example header:

```http
Idempotency-Key: <client-generated-key>
```

Important operations include:

- project creation
- blueprint generation initiation
- document generation
- GitHub synchronization
- event processing
- notification creation
- external integration commands
- project-change commands

The implementation may use execution IDs, unique constraints, stored idempotency records, or equivalent mechanisms.

---

# 47. Correlation IDs

Every API request receives or propagates a correlation ID.

Example:

```http
X-Correlation-ID: <uuid>
```

If absent, the backend generates one.

It flows through:

```text
HTTP request
 ↓
Application service
 ↓
AI execution
 ↓
Agent execution
 ↓
Background jobs
 ↓
Domain events
 ↓
Logs
 ↓
Audit records where applicable
```

---

# 48. Request vs Correlation ID

Conceptually:

```text
Request ID
= individual HTTP request

Correlation ID
= complete business/execution flow
```

For simple operations they may be identical.

Long-running executions retain the correlation ID after the original HTTP request has completed.

---

# 49. Long-Running Operation Pattern

Long-running operations follow:

```text
POST command
      ↓
Validate
      ↓
Create execution/job
      ↓
Return 202
      ↓
Background worker
      ↓
Persist state
      ↓
SSE progress
      ↓
Completion/failure
```

The browser is not required to remain connected.

---

# 50. API Timeout Policy

Normal APIs should remain short-lived.

The following must not depend on a long-running HTTP request:

- multi-agent blueprint generation
- AI generation
- document generation
- RAG indexing
- large GitHub synchronization
- other long-running integrations

These operations use background execution.

---

# 51. Middleware

API middleware may include:

- correlation/request ID
- structured request logging
- request timing
- CORS
- security headers
- centralized exception propagation

Middleware must not contain domain business logic.

---

# 52. Rate Limiting

Rate limiting is applied at the appropriate boundaries.

Potential dimensions:

- IP
- authenticated user
- endpoint
- AI execution
- provider gateway

Provider-specific limits belong primarily to the AI Provider Gateway.

The API protects itself against abusive request patterns without duplicating provider-specific behavior.

---

# 53. External Integration Boundary

Provider-specific logic stays behind adapters/interfaces.

GitHub:

```text
API
 ↓
Application Service
 ↓
GitHubAdapter
 ↓
GitHub API
```

AI:

```text
AI Service
 ↓
AI Provider Gateway
 ↓
OpenRouter / Provider
```

Research:

```text
MVP Service
 ↓
TavilyAdapter
 ↓
Tavily
```

The API does not contain provider-specific implementation details.

---

# 54. API and Transactions

Routes do not manually coordinate complex transactions.

Application/domain services own meaningful transaction boundaries.

Example:

```text
POST /tasks/{id}/complete
        ↓
CompleteTaskCommand
        ↓
Task Service
        ↓
Validate task
        ↓
Update task
        ↓
Recalculate progress
        ↓
Evaluate milestone
        ↓
Evaluate phase
        ↓
Evaluate health
        ↓
Create domain events
        ↓
Commit transaction
```

This maintains the deterministic execution chain established in 6B.

---

# 55. API and Domain Events

A successful command may produce:

```text
TaskCompleted
ProjectProgressChanged
MilestoneCompleted
ProjectPhaseChanged
ProjectHealthChanged
NotificationCreated
```

The API returns the immediate command result.

Event handlers process downstream activity/notification/integration work where appropriate.

---

# 56. API and Documents

Document generation follows:

```text
Structured Project State
        ↓
AI / Agent Generation
        ↓
Validation
        ↓
Domain Persistence
        ↓
Document Renderer
        ↓
Document Version
        ↓
Storage
```

The API exposes the resulting document/version.

It does not treat arbitrary Markdown as the canonical project state.

---

# 57. API and Project Change Workflow

Canonical API flow:

```text
POST /projects/{id}/change-requests
        ↓
Impact Analysis
        ↓
AWAITING_CONFIRMATION
        ↓
POST /change-requests/{id}/confirm
        ↓
Regeneration
        ↓
QA
        ↓
COMPLETED
```

Existing project state is not silently migrated.

---

# 58. API Contract Ownership

| Concern | Owner |
|---|---|
| HTTP routing | API |
| Request validation | API / Pydantic |
| Authentication context | Security / Dependencies |
| Authorization | Central Security |
| Use-case orchestration | Application |
| Business rules | Domain |
| Database access | Repository/Data Access |
| AI orchestration | AI/Application |
| External providers | Adapters |
| Persistence | Repository |
| Events | Platform/Event Service |
| Response serialization | API |
| Error translation | API/Exception Layer |

---

# 59. Thin Route Rule

A route should conceptually:

```text
receive request
    ↓
validate
    ↓
resolve dependencies
    ↓
call application service
    ↓
return response
```

A route must not become a giant workflow containing:

```text
database queries
business rules
AI calls
GitHub calls
progress calculations
notification creation
document generation
```

Those responsibilities belong to the appropriate layers.

---

# 60. API DTO vs Domain Model

API schemas and domain models remain separate.

Example:

```text
CreateProjectRequest
        ↓
CreateProjectCommand
        ↓
Project Domain
```

Database ORM/entity representations are not automatically public API contracts.

This prevents internal database changes from silently becoming API breaking changes.

---

# 61. Response DTO Rules

Response schemas intentionally expose only permitted information.

Responses must not accidentally expose:

- secrets
- authentication tokens
- provider credentials
- internal database details
- private AI traces
- authorization internals
- internal stack traces
- protected administrative metadata
- private investigation information without authorization

---

# 62. Error Translation

Internal exceptions are translated into safe API errors.

Example:

```text
AuthorizationException
        ↓
HTTP 403
        ↓
ACTION_NOT_ALLOWED
```

The client receives a useful error without receiving internal infrastructure details.

---

# 63. Health Endpoints

Operational endpoints:

```text
GET /health
GET /health/live
GET /health/ready
```

They may check:

- API process
- database connectivity
- critical infrastructure readiness

Detailed observability belongs to the Admin/System Health architecture.

---

# 64. OpenAPI Documentation

FastAPI/OpenAPI provides API documentation.

Typical endpoints:

```text
/openapi.json
/docs
```

Production exposure may be restricted according to environment/security policy.

Public API endpoints should have:

- summary
- description where needed
- request schema
- response schema
- expected status codes
- authorization requirements
- error contract

---

# 65. API Testing

Testing is organized into:

### Unit

Application/domain behavior.

### API

Endpoint contracts, status codes, validation, and authorization.

### Integration

API → application → repository → database.

### E2E

Complete user workflows.

Critical E2E flow:

```text
Student Registration
→ Create Project
→ Assessment
→ Blueprint
→ Tasks
→ Complete Task
→ Progress Update
→ Health Evaluation
```

Mentor flow:

```text
Mentor Creates Definition
→ Assigns Student
→ Student Gets Independent Instance
→ Mentor Observes Instance
```

AI flow:

```text
AI Generation
→ Agents
→ Validation
→ QA
→ Persistence
→ SSE
```

---

# 66. API Security Tests

Must cover:

- unauthenticated access
- wrong-role access
- cross-group access
- cross-student access
- cross-project access
- unauthorized AI retrieval
- unauthorized RAG retrieval
- unauthorized GitHub access
- unauthorized admin investigation
- expired authentication
- suspended users
- malformed identifiers
- injection attempts
- replayed commands
- duplicate idempotency keys

---

# 67. Naming Conventions

Use consistent plural resource names:

```text
/projects
/tasks
/milestones
/risks
/groups
/notifications
/documents
```

Use nested resources where ownership/scope is meaningful:

```text
/projects/{project_id}/tasks
/projects/{project_id}/risks
/projects/{project_id}/documents
```

Avoid action names such as:

```text
/getProjects
/createProject
/fetchTask
```

unless an endpoint is explicitly a command/action.

---

# 68. Resource-Oriented Design

Prefer resource semantics over frontend-screen semantics.

Avoid:

```text
POST /student-dashboard/load-everything
```

Prefer:

```text
GET /students/me/dashboard
```

The underlying query service can aggregate required data.

---

# 69. Role Boundary

GrowFlow supports:

```text
STUDENT
MENTOR
ADMIN
```

Role-specific endpoints are allowed for role-specific projections:

```text
GET /students/me/dashboard
GET /mentors/me/overview
GET /admin/overview
```

Underlying business services remain shared.

---

# 70. Privacy Boundary

### Student

May access their own authorized projects and permitted mentor/group information.

### Mentor

May access authorized students, groups, projects, and related information.

### Admin

May access platform information within administrative permissions.

### Protected/private content

Requires the appropriate controlled investigation process.

The frontend is never trusted to enforce privacy by itself.

---

# 71. Final API Architecture

```text
                       Frontend
                          │
                    HTTPS / JSON
                          │
                          ▼
                  ┌───────────────┐
                  │ FastAPI API   │
                  │   /api/v1     │
                  └───────┬───────┘
                          │
              ┌───────────┴───────────┐
              │                       │
       Dependencies              Pydantic
       Auth / DI / Scope          Validation
              │                       │
              └───────────┬───────────┘
                          ▼
                Application Services
                Commands / Queries
                          │
             ┌────────────┼─────────────┐
             │            │             │
          Domain         AI        Integrations
             │            │             │
             │       Orchestrator       │
             │            │             │
             │      Agents / Tools      │
             │            │             │
             │       Validation / QA    │
             │            │             │
             └────────────┼──────────────┘
                          ▼
                    Repositories
                          │
                          ▼
                 PostgreSQL / Supabase
```

Long-running flow:

```text
POST Command
    ↓
202 Accepted
    ↓
Execution Persisted
    ↓
Background Worker
    ↓
AI / Agents / RAG / Integration
    ↓
Events + Persistence
    ↓
SSE Stream
    ↓
Frontend
```

---

# 72. Final Frozen Decisions

## API

- FastAPI
- REST-oriented architecture
- `/api/v1`
- Pydantic-first contracts
- thin routes
- application-service driven
- logical Command/Query separation
- conventional HTTP semantics

## Authentication

- centralized authentication dependencies
- registration/login
- OAuth
- refresh/logout/password workflows
- exact auth mechanics finalized in 6D

## Authorization

- centralized
- role-aware
- resource-aware
- project/group scoped
- action-aware
- privacy-aware
- AI/RAG/tool authorization enforced

## Responses

- canonical success envelope
- canonical error envelope
- machine-readable error codes
- correct HTTP status codes

## Long-Running Work

- `202 Accepted`
- persistent execution records
- background workers
- SSE
- browser disconnect does not cancel work

## AI

- dedicated execution APIs
- AI Mentor API
- typed tools
- explicit action confirmation
- no direct DB mutation
- no arbitrary database queries

## Projects

- Project Definitions
- Project Definition Versions
- Project Instances
- assessment
- blueprint
- tasks
- milestones
- risks
- documents
- GitHub monitoring
- activity

## Admin

- administrative API namespace
- observability APIs
- controlled investigation workflow
- no impersonation
- no unrestricted private-data API

## Reliability

- correlation IDs
- idempotency
- centralized exception handling
- appropriate retries
- long-running execution persistence

## Security

- HTTPS
- authentication dependencies
- resource authorization
- RLS defense in depth
- Pydantic/input validation
- safe error responses
- no secrets in responses/logs
- no API bypass around domain authorization

---

# 73. Explicit Non-Goals

GrowFlow 6C does not introduce:

- GraphQL
- WebSockets initially
- separate API gateway service
- microservices
- CQRS infrastructure
- event-sourcing API
- generic CRUD generation
- ORM models as automatic public contracts
- unrestricted SQL endpoints
- unrestricted AI query endpoints
- frontend-driven business logic
- duplicated Student/Mentor/Admin business services
- unnecessary API aggregation infrastructure
- Kafka
- unnecessary proxy/gateway layers

---

# 74. Architecture Compliance Rules

Every new endpoint must answer:

1. What resource or command does it represent?
2. Which role can call it?
3. What resource scope applies?
4. Which application service owns the operation?
5. Which domain rule validates it?
6. Which repository owns persistence?
7. Is the operation synchronous or asynchronous?
8. Does it require idempotency?
9. Does it generate domain events?
10. Does it expose only authorized data?
11. Does it need an audit record?
12. Does it need SSE/execution tracking?

If these questions cannot be answered clearly, the endpoint is not ready for implementation.

---

# 75. Implementation Boundary

Part 6C defines the logical API architecture and endpoint contract.

The following remain implementation details for later phases:

- exact authentication/session mechanism
- exact JWT/cookie configuration
- exact OAuth implementation
- exact FastAPI dependency implementation
- exact middleware implementation
- exact Pydantic class definitions
- exact repository implementation
- exact database queries
- exact rate-limiter implementation
- exact idempotency persistence
- exact SSE manager implementation
- exact worker implementation
- exact OpenAPI metadata
- exact deployment/reverse-proxy configuration

These implementation details must remain consistent with the frozen API architecture.

---

# 76. Relationship to Previous Parts

6C depends on and preserves:

```text
5A  Application Foundation
 ↓
5B  Student Architecture
 ↓
5C  Mentor Architecture
 ↓
5D  Admin Architecture
 ↓
5E  Cross-Role Integration
 ↓
5F  Application Architecture Finalization
 ↓
6A  Backend Architecture
 ↓
6B  Database Architecture
 ↓
6C  API Architecture
```

The resulting backend boundary is:

```text
Frontend
    ↓
6C API
    ↓
6A Application / Domain Architecture
    ↓
6B Database
```

AI remains governed by the same architecture:

```text
API
 ↓
Application
 ↓
AI Orchestrator
 ↓
Agents + Tools
 ↓
Validation
 ↓
QA/Judge
 ↓
Domain Service
 ↓
Repository
 ↓
Database
```

---

# 77. Freeze Statement

**Part 6C — API Architecture is COMPLETE and FROZEN.**

The API architecture established here is the contract for subsequent backend implementation.

Future implementation phases may define exact schemas, dependencies, authentication mechanics, SQL queries, middleware, workers, and deployment configuration, but they must preserve the API boundaries, authorization model, response/error conventions, asynchronous execution model, SSE strategy, and separation of responsibilities defined in this document unless a deliberate architecture change is explicitly approved.

**Next:** Part 6D — Authentication & Security Architecture.
