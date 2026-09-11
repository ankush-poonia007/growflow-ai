# GrowFlow — Part 6D: Authentication & Security Architecture
## Final Frozen Specification

**Project:** GrowFlow  
**Part:** 6D — Authentication & Security Architecture  
**Status:** FROZEN  
**Authentication Provider:** Supabase Auth  
**Application Authorization:** GrowFlow  
**Database Security:** PostgreSQL + Supabase RLS  
**API Framework:** FastAPI

---

# 1. Purpose

Part 6D defines how GrowFlow handles:

- authentication
- registration
- login
- logout
- sessions/tokens
- password security
- Google OAuth
- GitHub OAuth
- role-based access control
- resource authorization
- project/group isolation
- admin security
- AI/RAG authorization
- secrets
- security middleware
- rate limiting
- account lifecycle
- audit requirements
- security failure handling
- security testing

The core principle is:

> **Authentication proves who the user is. Authorization determines what that user is allowed to do.**

---

# 2. Security Architecture

The canonical security flow is:

```text
Request
   ↓
HTTPS
   ↓
Authentication
   ↓
Current User
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
Service / Tool Execution
   ↓
Audit if Required
```

The same security boundary applies to:

- Student APIs
- Mentor APIs
- Admin APIs
- AI tools
- RAG retrieval
- GitHub integration
- background jobs
- administrative investigations

---

# 3. Authentication Strategy

GrowFlow uses **Supabase Auth** for authentication rather than implementing password authentication cryptography from scratch.

This avoids unnecessarily rebuilding:

- password hashing
- session handling
- token issuance
- token refresh
- OAuth protocol handling
- account recovery mechanisms

GrowFlow's application database maintains its own `users` record and application-specific role/profile information.

Conceptually:

```text
Supabase Auth
     │
     │ authenticated identity
     ▼
GrowFlow users
     │
     ├── role
     ├── status
     ├── profile
     └── application permissions
```

Supabase Auth is the authentication authority.

GrowFlow is the application authorization authority.

---

# 4. Identity Mapping

Authentication identity and application identity must be linked deterministically.

Recommended relationship:

```text
Supabase Auth User UUID
          │
          ▼
GrowFlow users.id
```

The same UUID should be used where practical.

This avoids maintaining an unnecessary second authentication identifier.

---

# 5. User Registration

Registration flow:

```text
User
 ↓
POST /auth/register
 ↓
Validate input
 ↓
Supabase Auth registration
 ↓
Identity created
 ↓
GrowFlow user/profile initialization
 ↓
Role validation
 ↓
Account activation policy
 ↓
Authenticated application context
```

Registration validates:

- email format
- password requirements
- allowed role
- duplicate identity
- account state

---

# 6. Role Registration Security

Users must not be able to freely assign themselves privileged roles.

A malicious request such as:

```json
{
  "role": "ADMIN"
}
```

must never create an administrator.

Public registration supports normal student/mentor onboarding according to the platform's controlled policy.

`ADMIN` is a privileged platform role and must never be self-selected during normal registration.

---

# 7. Authentication Roles

Canonical roles:

```text
ADMIN
MENTOR
STUDENT
```

Roles are application-level authorization attributes.

They are not merely frontend labels.

Every privileged backend operation checks the authenticated user's role.

---

# 8. Account Status

Canonical account statuses:

```text
ACTIVE
INACTIVE
SUSPENDED
```

### ACTIVE

Normal access according to role.

### INACTIVE

Login/access restricted according to account policy.

### SUSPENDED

Access denied until explicitly restored by authorized administration.

Account status changes are persisted and historically tracked.

---

# 9. Password Security

GrowFlow does not implement custom password hashing.

Supabase Auth handles password credential security.

Application rules still enforce:

- minimum password requirements
- password strength feedback
- secure reset flow
- no password logging
- no password persistence in GrowFlow business tables

Password strength UI:

```text
Weak
Basic
Strong
```

Strength indicators are user guidance, not the sole security mechanism.

---

# 10. Password Reset

Flow:

```text
Forgot Password
      ↓
Request reset
      ↓
Identity provider
      ↓
Verified reset mechanism
      ↓
New password
      ↓
Existing session/security policy evaluated
```

Recovery endpoints should avoid exposing whether arbitrary email addresses belong to active accounts.

Use generic recovery responses where necessary to prevent account enumeration.

---

# 11. Logout

Logout invalidates/removes the appropriate authentication session/token according to the selected Supabase Auth session model.

The frontend clears local authenticated state.

Protected API requests after logout must fail authentication.

---

# 12. Session Strategy

Use the Supabase Auth session mechanism rather than implementing an independent custom session store.

The backend validates the authenticated session/token and builds:

```text
CurrentUser
AuthorizationContext
```

for each protected request.

GrowFlow should not create a second competing authentication/session architecture without a concrete requirement.

---

# 13. Token Validation

Every protected request validates:

- token/session validity
- signature/provider validity
- expiration
- user identity
- account status
- application authorization context

A valid token alone does not grant access to every resource.

---

# 14. Authentication Dependency

FastAPI dependency:

```text
get_current_user()
```

conceptually performs:

```text
Request
 ↓
Extract auth credentials
 ↓
Validate credentials
 ↓
Resolve Supabase identity
 ↓
Load GrowFlow user
 ↓
Check account status
 ↓
Return CurrentUser
```

---

# 15. Authorization Context

After authentication, the backend creates an authorization context containing information such as:

```text
user_id
role
account_status
group memberships
relevant permissions
```

This context is available through FastAPI dependency injection.

---

# 16. Role-Based Access Control

GrowFlow uses RBAC.

## Student

Can:

- manage own profile
- create own projects
- join authorized groups
- execute own project
- complete own tasks
- use authorized AI Mentor
- submit help requests
- view authorized documents
- connect/monitor authorized GitHub repositories

## Mentor

Can:

- manage own groups
- manage project definitions
- view authorized students
- view authorized project instances
- monitor progress/health/risks
- create mentor notes
- manage help requests
- use authorized Mentor AI

## Admin

Can:

- administer platform accounts
- observe platform entities
- inspect system health
- inspect AI observability
- review platform analytics
- perform controlled investigations

Admin cannot automatically mutate student project execution state.

---

# 17. Resource-Based Authorization

RBAC alone is insufficient.

A mentor may be a valid `MENTOR` but still must not access:

- another mentor's group
- another mentor's student
- another student's private project

Therefore GrowFlow requires:

```text
Role Authorization
+
Resource Authorization
```

---

# 18. Student Authorization

A student may access:

- their own user/profile
- their own projects
- their own assessment
- their own blueprint
- their own tasks
- their own milestones
- their own risks
- their own documents
- their own AI context
- their own GitHub monitoring
- authorized group information
- authorized mentor communication

A student must not access another student's project by changing a project ID.

The backend verifies ownership and scope.

---

# 19. Mentor Authorization

Mentor access is determined through authorized relationships.

Conceptually:

```text
Mentor
 ↓
Group Ownership / Membership
 ↓
Student
 ↓
Project Instance
```

A mentor can access a student's project when the mentor has an authorized relationship through the relevant group/project relationship.

No frontend-only filtering is trusted.

---

# 20. Multi-Group Authorization

Students may belong to multiple groups.

The authorization model must therefore support:

```text
Student
 ├── Group A
 ├── Group B
 └── Group C
```

Each access decision evaluates the relevant membership and resource relationship.

---

# 21. Project Isolation

Project isolation is mandatory.

Every project-scoped request should resolve:

```text
Authenticated User
        ↓
Project Instance
        ↓
Authorized Relationship
```

Project IDs are identifiers, not access credentials.

Knowing a UUID never grants access.

---

# 22. Group Isolation

Group resources require group-level authorization.

For example:

```text
GET /groups/{group_id}/students
```

requires:

```text
user authenticated
AND
user authorized for group
```

A student cannot enumerate arbitrary groups by guessing IDs.

---

# 23. Admin Authorization

Admin access requires:

```text
authenticated
AND
role == ADMIN
AND
account ACTIVE
```

Admin APIs still apply action-specific authorization.

Being an administrator does not create an unrestricted data bypass.

---

# 24. Controlled Admin Investigation

For protected/deeper information:

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

The investigation record stores:

- administrator
- target
- reason
- status
- authorization
- timestamps

This preserves legitimate administrative capability while protecting privacy.

---

# 25. No Impersonation

GrowFlow explicitly does not implement:

```text
Login as Student
Impersonate User
Act as Mentor
```

for administrators.

Admin observation and controlled investigation are preferred over account impersonation.

---

# 26. AI Authorization

AI operates under the user's authorization context.

The AI does not automatically receive:

- admin privileges
- database credentials
- global project access

Example:

```text
Student asks AI:
"Show me my project risks."
```

AI tools may retrieve only that student's authorized project risks.

---

# 27. Mentor AI Authorization

Mentor AI may retrieve information from:

- authorized groups
- authorized students
- authorized project instances
- authorized documents
- authorized RAG context
- authorized GitHub monitoring

It cannot retrieve unrelated users/projects.

---

# 28. Admin AI Authorization

Admin AI can perform authorized cross-platform operational queries.

Examples:

```text
"How many active students are there?"
"Which groups currently have the most at-risk projects?"
"How many AI executions failed today?"
```

For protected/private content, the controlled investigation boundary still applies.

Admin AI does not receive unrestricted SQL access.

---

# 29. RAG Authorization

RAG retrieval must enforce:

```text
User Authorization
+
Project Scope
+
Document Authorization
```

A vector similarity result is never sufficient proof of access.

The retrieval layer must apply authorization filtering before content reaches the model.

---

# 30. AI Tool Authorization

Every AI tool must define:

- tool identity
- allowed roles
- resource scope
- permitted actions
- required authorization checks
- whether it is read-only or state-changing

Conceptually:

```text
AI Tool Call
 ↓
Tool Contract
 ↓
Authorization
 ↓
Resource Scope
 ↓
Service
```

---

# 31. No Direct Database Access

AI agents never receive:

- database credentials
- raw SQL execution
- unrestricted repository access

Instead:

```text
Agent
 ↓
Typed Tool
 ↓
Authorization
 ↓
Application Service
 ↓
Repository
```

This is a hard security boundary.

---

# 32. AI State Mutation

AI cannot directly mutate:

- task completion
- milestone completion
- progress
- phase
- health
- risk state
- project state
- account state

Any proposed mutation follows:

```text
AI
 ↓
Structured Proposal
 ↓
Validation
 ↓
User Confirmation where required
 ↓
Domain Service
 ↓
Persistence
```

---

# 33. RLS Defense in Depth

PostgreSQL/Supabase Row Level Security is used as a second authorization boundary where practical.

Conceptually:

```text
Application Authorization
          +
Database RLS
```

If application code contains an authorization bug, RLS provides another protection layer.

RLS does not replace application-level authorization.

---

# 34. RLS Scope

RLS policies should be based on authenticated identity and authorized relationships.

Examples:

```text
Student → own project
Mentor → authorized group/project
Admin → authorized platform data
```

Sensitive/admin investigation data receives stricter policy treatment.

Exact SQL policies are implemented during database/security implementation.

---

# 35. Secrets Management

Secrets must never be hard-coded.

Sensitive configuration includes:

- Supabase service credentials
- OAuth secrets
- OpenRouter/API credentials
- five AI provider keys
- Tavily credentials
- GitHub credentials/tokens
- email provider credentials
- storage credentials
- LangSmith credentials

Secrets originate from:

```text
Environment / Secret Manager
          ↓
Typed Settings
          ↓
Dependency Injection
          ↓
Authorized Component
```

---

# 36. Settings Boundary

Application code does not repeatedly read `.env`.

Instead:

```text
.env / environment
       ↓
settings.py
       ↓
Typed Settings
       ↓
Dependency Injection
```

This preserves the centralized configuration architecture established in 6A.

---

# 37. Secret Exposure Rules

Never expose secrets through:

- API responses
- logs
- exceptions
- AI prompts
- database metadata
- domain events
- audit records
- Git commits
- frontend bundles

Secrets must also be excluded from debugging payloads.

---

# 38. OAuth Security

Supported providers:

- Google
- GitHub

OAuth flow validates:

- provider response
- state/CSRF protection
- redirect URI
- identity mapping
- account association
- authorization policy

OAuth identity does not bypass GrowFlow's role/resource authorization.

---

# 39. OAuth Account Linking

OAuth accounts must map deterministically to the application user identity.

The system must avoid creating duplicate application users merely because the same user logs in using a different supported provider.

Account-linking behavior must be explicit and secure.

---

# 40. GitHub Security Boundary

GitHub credentials/tokens are handled as sensitive integration credentials.

GrowFlow requests only permissions necessary for monitoring functionality.

GitHub integration remains:

```text
Read / Monitor
```

rather than repository management.

No unnecessary write permissions should be requested.

---

# 41. AI Provider Key Pool Security

The five-key pool is managed centrally by the AI Provider Gateway.

Application components receive:

```text
AI Provider Gateway
```

rather than individual raw keys.

The gateway manages:

- key selection
- rotation
- rate-limit state
- cooldown
- provider failures
- retries
- timeouts

Raw keys never appear in AI execution responses.

---

# 42. Rate Limiting

Security rate limits apply to:

- authentication
- password reset
- OAuth initiation/callback
- expensive AI requests
- document generation
- RAG indexing
- sensitive administrative endpoints
- suspicious repeated requests

Exact numerical thresholds are configuration rather than architectural constants.

---

# 43. Brute-Force Protection

Authentication is protected against repeated credential attacks through the authentication provider's controls plus application-level rate limiting where necessary.

Repeated failures should not reveal whether an account exists.

---

# 44. Account Enumeration Protection

Authentication/recovery endpoints should avoid responses such as:

```text
"This email does not exist."
```

where that would reveal account existence.

Use generic responses where necessary.

---

# 45. Input Security

All API inputs pass through typed validation.

Security validation covers:

- malformed UUIDs
- oversized payloads
- invalid enum values
- unexpected fields where strictness is required
- dangerous filenames
- unsafe URLs where relevant
- invalid query parameters

Input validation does not replace authorization.

---

# 46. Injection Protection

Database access uses parameterized queries/ORM/repository mechanisms.

Never construct SQL by concatenating user input.

Likewise:

- shell commands must not be built from uncontrolled input
- HTML output must be safely handled
- Markdown rendering must be handled according to its output context
- external URLs must be validated according to feature requirements

---

# 47. File Upload Security

Project files/documents are untrusted input.

Validation should include:

- allowed file types
- file size
- filename normalization
- content validation
- storage isolation
- malware/security scanning where appropriate
- authorization before access

Uploaded content must not automatically become executable.

---

# 48. Path Traversal Protection

User-provided filenames/path values must never directly control server filesystem paths.

Use generated storage identifiers and controlled object-storage keys.

Path traversal such as:

```text
../../secret.env
```

must never reach an uncontrolled filesystem operation.

---

# 49. SSRF Protection

Features that fetch external URLs must validate outbound requests where relevant.

User-controlled URLs must not become unrestricted internal network requests.

Tavily and other provider adapters own provider-specific retrieval behavior.

---

# 50. CORS

CORS uses explicit configured allowed origins.

Development may allow configured local origins.

Production uses the authorized frontend origin(s).

Avoid unrestricted:

```text
Access-Control-Allow-Origin: *
```

for authenticated application APIs unless a specific public endpoint requires it.

---

# 51. Security Headers

The production API/web stack should use appropriate security headers for:

- clickjacking protection
- MIME-sniffing protection
- unsafe resource-loading protection where applicable
- transport security
- other browser-level attack mitigation

Exact deployment headers are finalized during security/deployment implementation.

---

# 52. HTTPS

Production traffic must use HTTPS.

Sensitive credentials/tokens must never be transmitted over plain HTTP.

HTTP should redirect to HTTPS at the appropriate deployment boundary.

---

# 53. CSRF

The CSRF strategy depends on the final authentication session transport.

If browser cookies are used for authentication, CSRF protection is required for state-changing requests.

If bearer tokens are used without ambient browser authentication cookies, the CSRF threat model differs.

The final authentication transport determines the exact implementation.

---

# 54. XSS Protection

The backend must:

- avoid unsafe HTML generation
- validate content where necessary
- encode user-generated content at the rendering boundary
- avoid returning executable content unexpectedly

The following are treated as untrusted content:

- project descriptions
- mentor notes
- help messages
- document content
- AI content

---

# 55. AI Prompt-Injection Security

GrowFlow assumes retrieved documents and external content can contain malicious instructions.

Retrieved text is **data**, not trusted instructions.

AI tools separate:

```text
System/Developer Policy
+
Authorized Application Context
+
Retrieved Content
+
User Content
```

Retrieved content cannot override authorization or system policy.

---

# 56. Tool Permission Boundary

AI tools follow least privilege.

For example:

```text
read_project_status
```

does not imply:

```text
modify_project_status
```

A read-only tool cannot be used as a hidden mutation mechanism.

---

# 57. Background Job Security

Background workers preserve the initiating authorization context.

They retain enough information to determine:

- who initiated the operation
- which project it belongs to
- what operation was authorized
- correlation ID
- execution ID

A worker must not assume that the existence of a job means every referenced resource remains accessible.

---

# 58. Authorization Revalidation

For sensitive asynchronous operations, authorization should be revalidated when the worker performs the operation.

This prevents:

```text
User authorized at T1
        ↓
Permission revoked
        ↓
Worker blindly executes at T2
```

Long-running operations must follow the authorization semantics appropriate to their execution type.

---

# 59. Security Audit Events

Security-relevant actions should generate audit events.

Examples:

- relevant login/security failures
- role changes
- account suspension
- account activation
- admin investigation
- privileged data inspection
- permission-sensitive changes
- security configuration changes
- sensitive integration changes

Audit records are append-oriented.

---

# 60. Audit Integrity

Audit records are not ordinary editable CRUD resources.

Normal users must not be able to modify or delete audit records.

Audit access is strictly controlled.

---

# 61. Security Logging

Structured security logs may contain:

- timestamp
- severity
- module
- event
- correlation ID
- request ID
- execution ID
- user ID where appropriate
- project ID where appropriate
- duration
- error code

Never log:

- passwords
- access tokens
- API keys
- OAuth secrets
- raw authentication headers
- unnecessary sensitive private content

---

# 62. Error Handling Security

Client errors must not expose:

- SQL queries
- stack traces
- filesystem paths
- provider credentials
- internal service topology
- secret configuration
- debugging internals

Clients receive safe machine-readable errors.

Authorized internal logs contain diagnostic information.

---

# 63. Dependency Security

Backend dependencies must be:

- controlled appropriately
- periodically updated
- vulnerability-reviewed
- minimized where practical

Do not add libraries unnecessarily when existing platform capabilities are sufficient.

---

# 64. Security Configuration

Security-sensitive settings are centralized in typed configuration.

Examples:

```text
allowed_origins
token/session configuration
rate limits
upload limits
OAuth configuration
AI provider configuration
storage configuration
security headers
environment
```

Configuration validation should fail fast when required security settings are missing or invalid.

---

# 65. Environment Separation

GrowFlow distinguishes:

```text
development
testing
staging
production
```

Production secrets/configuration must not be casually reused in development.

Development configuration must never accidentally point to production data.

---

# 66. Database Security

Database access follows:

```text
Application
 ↓
Repositories
 ↓
PostgreSQL
```

Application users do not receive database credentials.

The frontend never receives privileged PostgreSQL credentials.

Supabase client capabilities, if used from the frontend, remain limited to intended client-safe operations and RLS-protected access.

Privileged service credentials remain backend-only.

---

# 67. Service-Role Boundary

Supabase service-role credentials, if required by backend infrastructure, are strictly backend-only.

They must never be:

- shipped to frontend JavaScript
- returned through APIs
- stored in user-accessible metadata
- exposed to AI agents
- logged

Operations using elevated service privileges must still enforce application authorization.

---

# 68. Data Minimization

Only necessary data should be returned.

Student responses should not return:

- internal admin metadata
- provider credentials
- other users' private information
- AI internal traces
- audit records

unless explicitly authorized and required.

---

# 69. Privacy by Default

Default visibility follows:

```text
Own Data
    ↓
Authorized Relationship
    ↓
Minimum Necessary Information
```

Private information is not globally exposed simply because the requester has a privileged role.

---

# 70. Notification Security

Notifications must respect authorization.

A notification must not reveal protected content to an unauthorized recipient.

Sensitive project details should not be unnecessarily embedded in notification metadata.

---

# 71. Document Security

Document access verifies:

```text
authenticated user
+
project authorization
+
document authorization
```

A direct document URL cannot bypass authorization.

Document IDs are not access tokens.

---

# 72. GitHub Data Security

GitHub activity is scoped to the authorized project.

A user cannot access another project's repository metadata by supplying its repository ID.

External GitHub credentials are separated from project-readable activity data.

---

# 73. AI Execution Security

AI execution records may contain sensitive information.

Visibility:

### Student

Own authorized executions.

### Mentor

Relevant authorized student/project executions.

### Admin

Operational metadata by default; deeper/private information only according to admin privacy/investigation rules.

Detailed LangSmith traces are not automatically exposed to ordinary users.

---

# 74. RAG Content Security

RAG indexing preserves:

```text
project_instance_id
document_id
document_version_id
authorization scope
```

Retrieval filters by authorization before content reaches the model.

This protects against cross-project semantic retrieval leakage.

---

# 75. External Research Security

External research content is untrusted.

Tavily results may contain:

- malicious instructions
- misleading content
- prompt injection
- malicious links

The research agent treats results as evidence, not executable instructions.

---

# 76. Project Change Workflow Security

Project-change operations require:

```text
authorized requester
 ↓
impact analysis
 ↓
explicit confirmation
 ↓
regeneration
 ↓
QA
 ↓
deterministic persistence
```

Authorization is checked when the request is created and when the state-changing command executes.

---

# 77. Definition Update Security

Mentor project-definition updates are authorized against the definition owner.

Updating a definition does not automatically authorize modification of existing student instances.

Existing instances remain isolated.

---

# 78. Task Completion Security

Only authorized users can complete tasks.

### Student

Own project execution.

### Mentor

Observation/mentoring according to frozen architecture.

### Admin

Observation only.

This preserves the previously established ownership model.

---

# 79. Progress and Health Security

No unrestricted endpoint should allow arbitrary updates such as:

```json
{
  "progress": 99,
  "health": "HEALTHY"
}
```

unless the operation is part of the deterministic domain workflow.

This prevents accidental or malicious corruption of project state.

---

# 80. Security Testing Strategy

Security testing occurs at multiple layers.

### Unit

Authorization rules.

### API

Authentication, roles, scopes, forbidden resources.

### Integration

Database/RLS plus application authorization.

### E2E

Real user workflows.

### Adversarial

Attempt to bypass:

- role checks
- project isolation
- group isolation
- RAG scope
- AI tool scope
- admin investigation
- document authorization
- GitHub authorization

---

# 81. Critical Security Test Matrix

| Scenario | Expected |
|---|---|
| Unauthenticated → protected API | 401 |
| Student → admin API | 403 |
| Student → another student's project | 403/404 according to resource policy |
| Mentor → unrelated group | 403/404 according to resource policy |
| Mentor → unrelated project | 403/404 according to resource policy |
| Admin → normal project execution mutation | Denied |
| AI → unauthorized project | Denied |
| AI → unrestricted SQL | Impossible |
| RAG → cross-project retrieval | Denied |
| Direct document URL → unauthorized user | Denied |
| Suspended user → protected API | Denied |
| Invalid/expired token | 401 |
| Duplicate sensitive command | Idempotent/controlled |
| Admin private inspection without investigation | Denied |
| Investigation without authorization | Denied |

---

# 82. Security Incident Correlation

Serious security events should be traceable through:

```text
Request ID
Correlation ID
User
Action
Resource
Timestamp
Audit Event
AI Execution if relevant
```

This supports investigation without requiring unrestricted access to application internals.

---

# 83. Authentication vs Authorization Ownership

| Concern | Owner |
|---|---|
| Identity authentication | Supabase Auth |
| Application identity | GrowFlow users |
| Role | GrowFlow authorization |
| Account status | GrowFlow |
| Resource access | GrowFlow |
| Project isolation | GrowFlow + RLS |
| AI tool authorization | GrowFlow AI security boundary |
| RAG authorization | GrowFlow Knowledge/Security |
| Admin investigation | GrowFlow Security/Admin |
| Secrets | Environment/secret management |
| Audit | Security/Audit service |

---

# 84. Final Security Architecture

```text
                     Client
                       │
                     HTTPS
                       │
                       ▼
                 FastAPI API
                       │
                       ▼
                Authentication
                Supabase Auth
                       │
                       ▼
                 Current User
                       │
                       ▼
              Role Authorization
                       │
                       ▼
            Resource Authorization
                       │
             ┌─────────┴─────────┐
             │                   │
        Project Scope        Group Scope
             │                   │
             └─────────┬─────────┘
                       ▼
                 Action Permission
                       │
                       ▼
                 Privacy Policy
                       │
             ┌─────────┴─────────┐
             │                   │
          Services            AI Tools
             │                   │
             │              RAG / GitHub
             │                   │
             └─────────┬─────────┘
                       ▼
                  Repository
                       │
                       ▼
              PostgreSQL + RLS
                       │
                       ▼
                  Audit/Logs
```

---

# 85. Final Frozen Decisions

## Authentication

- Supabase Auth
- application identity mapped to Supabase identity
- secure password authentication through Supabase
- Google OAuth
- GitHub OAuth
- secure session/token handling
- password recovery
- logout
- no custom password cryptography

## Authorization

- RBAC
- resource-based authorization
- group/project scope
- action-level permissions
- centralized security dependencies
- backend enforcement
- RLS defense in depth

## Roles

```text
ADMIN
MENTOR
STUDENT
```

## Account Status

```text
ACTIVE
INACTIVE
SUSPENDED
```

## Admin

- no impersonation
- metadata-first
- controlled investigation for deeper/private information
- audit required for controlled investigation

## AI

- authorization inherited from user context
- typed tools
- no raw SQL
- no direct DB access
- no unrestricted project retrieval
- no arbitrary state mutation

## RAG

- project-scoped
- authorization-filtered
- vector similarity does not grant access

## Secrets

- centralized typed configuration
- environment/secret management
- backend-only privileged credentials
- never logged/exposed

## Security

- HTTPS
- CORS restrictions
- security headers
- rate limiting
- brute-force protection
- account-enumeration protection
- input validation
- injection protection
- upload security
- path traversal protection
- SSRF considerations
- XSS protection
- prompt-injection defenses

## Observability

- request IDs
- correlation IDs
- structured logs
- security audit events
- execution correlation

---

# 86. Explicit Non-Goals

6D does not introduce:

- custom password hashing implementation
- custom authentication server
- independent session database
- administrator impersonation
- unrestricted service-role frontend access
- unrestricted SQL
- unrestricted AI database access
- global RAG retrieval
- GitHub write-management
- automatic privilege escalation
- blanket admin bypass
- storing secrets in PostgreSQL business tables
- security logic exclusively in the frontend
- unnecessary identity microservices

---

# 87. Implementation Boundary

6D defines the security architecture.

Exact implementation details to be finalized during implementation include:

- Supabase Auth configuration
- JWT/session transport details
- cookie vs bearer-token configuration
- exact OAuth callback implementation
- exact RLS policy SQL
- exact FastAPI security dependencies
- exact rate-limit thresholds
- exact password-strength configuration
- exact security headers
- exact upload scanning mechanism
- exact secret-management platform
- exact audit retention policy
- exact production CORS configuration
- exact CSRF implementation based on the selected session transport

These implementation choices must preserve the frozen security boundaries.

---

# 88. Relationship to Previous Parts

```text
5A–5F
Application Architecture
        ↓
6A
Backend Architecture
        ↓
6B
Database Architecture
        ↓
6C
API Architecture
        ↓
6D
Authentication & Security
```

The complete backend request boundary is:

```text
Frontend
   ↓
HTTPS
   ↓
Authentication
   ↓
Authorization
   ↓
FastAPI
   ↓
Pydantic
   ↓
Application
   ↓
Domain
   ↓
Repository
   ↓
PostgreSQL + RLS
```

For AI:

```text
User
 ↓
Authentication
 ↓
Authorization
 ↓
AI API
 ↓
AI Orchestrator
 ↓
Authorized Tools
 ↓
RAG / DB / GitHub
 ↓
Validation
 ↓
QA
 ↓
Domain Service
 ↓
Database
```

---

# 89. Freeze Statement

**Part 6D — Authentication & Security Architecture is COMPLETE and FROZEN.**

The security architecture established here is the mandatory security boundary for subsequent GrowFlow implementation phases.

Future implementation may refine configuration and implementation mechanics, but must preserve:

- centralized authentication
- centralized authorization
- RBAC
- resource/project/group isolation
- RLS defense in depth
- controlled admin investigation
- no impersonation
- AI authorization boundaries
- RAG authorization
- secret isolation
- secure API behavior
- auditability
- least privilege

**Next:** Part 6E — AI Provider Gateway & Model Architecture.
