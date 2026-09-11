# GrowFlow — Phase 6M
# Infrastructure Security Architecture
## Final Documentation

**Project:** GrowFlow  
**Phase:** 6 — Backend & Platform Architecture  
**Subphase:** 6M — Infrastructure Security  
**Status:** FINAL  
**Purpose:** Define the infrastructure-level security architecture for GrowFlow before final backend architecture consolidation in 6N.

---

# 1. Purpose

This document defines how GrowFlow protects its infrastructure, runtime environment, credentials, network boundaries, external integrations, storage, workers, database, observability systems, and deployment surfaces.

It complements, rather than replaces:

- 6D — Authentication & Security Architecture
- 6E — AI Infrastructure
- 6F — Agent Execution Infrastructure
- 6G — RAG & Document Infrastructure
- 6H — Background Jobs & Events
- 6I — External Integrations
- 6J — Observability
- 6K — Storage & File Architecture
- 6L — Deployment & Runtime

The distinction is intentional:

> **6D defines application/user security. 6M defines infrastructure and runtime security.**

GrowFlow follows defense in depth. No single control is treated as sufficient.

---

# 2. Security Objectives

Infrastructure security must preserve:

1. Confidentiality
2. Integrity
3. Availability
4. Authorization boundaries
5. Tenant/project isolation
6. Credential confidentiality
7. Auditability
8. Recoverability
9. Operational resilience
10. Safe degradation

Security controls must also preserve the project's architectural principles:

- modular monolith
- PostgreSQL/Supabase as canonical state
- controlled external integrations
- centralized AI Provider Gateway
- project-scoped RAG
- asynchronous workers for long-running work
- transactional outbox
- SSE for execution streaming
- centralized authorization
- deterministic domain ownership

---

# 3. Infrastructure Security Boundary

The security boundary is:

```text
                        INTERNET
                           |
                     HTTPS / TLS
                           |
                    Frontend / Client
                           |
                    ----------------
                           |
                     FastAPI API
                           |
             Authentication + Authorization
                           |
                 Application Services
                           |
        -----------------------------------------
        |            |            |             |
     Database      Storage      Workers      AI Gateway
        |            |            |             |
     Supabase     Object Store   Jobs       AI Providers
        |                                       |
        |                                    OpenRouter
        |                                    / Models
        |
   PostgreSQL / RLS

External integrations:
GitHub | Tavily | OAuth Providers | Email

Observability:
Logs | Metrics | Traces | LangSmith | Audit
```

Every boundary must have an explicit trust assumption and security control.

---

# 4. Core Security Principles

## 4.1 Least Privilege

Every component receives only the permissions it requires.

Examples:

- frontend never receives service-role credentials
- workers do not receive unnecessary administrative privileges
- AI agents do not receive database credentials
- RAG retrieval cannot access another project
- observability systems do not automatically become data-access systems
- admin investigation access is explicitly controlled

## 4.2 Never Trust Client Authorization

Frontend controls are UX controls only.

The backend independently validates:

- identity
- role
- resource ownership
- group membership
- project scope
- action permission
- privacy policy

## 4.3 Secrets Are Infrastructure Data

API keys, OAuth secrets, database credentials, signing secrets, service-role credentials, and encryption material must never be treated as normal configuration values exposed to application code indiscriminately.

## 4.4 Secure Defaults

Default behavior should be restrictive.

Examples:

- private resources remain private
- unknown origins are rejected
- unknown users are denied
- unknown project scope is denied
- failed authorization is deny-by-default
- failed secret loading prevents unsafe startup
- invalid infrastructure configuration fails fast

## 4.5 Defense in Depth

Controls should exist at multiple layers:

```text
Network
  ↓
Transport Security
  ↓
Runtime / Container Security
  ↓
Application Authorization
  ↓
Database Authorization / RLS
  ↓
Storage Access Control
  ↓
Integration Security
  ↓
Audit / Observability
```

---

# 5. Threat Model

Primary infrastructure threats include:

| Threat | Primary Control |
|---|---|
| Credential leakage | Secret management + redaction |
| Unauthorized API access | Authentication + authorization |
| Brute-force abuse | Rate limiting + throttling |
| DDoS/resource exhaustion | Edge/runtime limits + capacity controls |
| SSRF | URL validation + egress restrictions |
| Malicious file upload | MIME validation + size limits + safe parsing |
| Path traversal | Safe path handling |
| Container compromise | Minimal images + non-root runtime |
| Dependency compromise | Lockfiles + vulnerability scanning |
| Database exposure | Private credentials + RLS + network controls |
| Storage exposure | Signed/authorized access |
| Cross-project RAG leakage | Mandatory project filters + authorization |
| AI credential theft | Central gateway |
| Prompt injection | Treat retrieved content as untrusted |
| Log leakage | Redaction + structured logging |
| OAuth abuse | State/PKCE/redirect validation |
| Worker privilege abuse | Dedicated permissions |
| Replay/duplicate jobs | Idempotency |
| Stale background execution | Version/state validation |
| Configuration drift | Environment-specific configuration |
| Backup exposure | Access control + encryption |
| Supply-chain attack | Dependency and image scanning |

---

# 6. Secrets Management

## 6.1 Secrets That Require Protection

Examples include:

- Supabase service-role key
- database credentials
- OpenRouter/API provider keys
- five-key AI provider pool
- Tavily key
- GitHub application secrets
- OAuth client secrets
- email provider credentials
- storage credentials
- LangSmith credentials
- signing/encryption secrets
- webhook secrets
- deployment credentials

## 6.2 Storage Rules

Secrets must:

- exist outside source code
- exist outside committed configuration
- be injected through environment/secret management
- be available only to required components
- never be sent to frontend clients
- never be included in API responses
- never appear in logs
- never be embedded in generated documents
- never be exposed through AI tools

## 6.3 `.env` Policy

Development may use `.env`.

Production must use deployment secret management.

Application code accesses configuration through the centralized typed `Settings` interface established in 6A.

Application/business code must not repeatedly read `.env`.

## 6.4 Secret Rotation

The architecture must support rotation without requiring source-code changes.

Rotation should include:

1. create replacement secret
2. deploy/update configuration
3. validate new credential
4. revoke old credential
5. verify service health

For provider keys, the AI Provider Gateway handles key state and rotation behavior.

---

# 7. Five-Key AI Provider Security

GrowFlow uses exactly five configured AI provider keys.

Security rules:

- keys exist only on backend infrastructure
- agents never see raw keys
- routes never select keys directly
- frontend never sees keys
- logs never expose keys
- LangChain/LangGraph cannot bypass the gateway
- provider failures do not reveal credentials
- key identifiers may be logged as safe metadata, never key values

The gateway owns:

- key selection
- health state
- cooldown
- rate-limit handling
- retries
- provider failure handling
- quota exhaustion
- usage attribution

The five keys are not a mechanism for bypassing provider/account-level restrictions.

If all usable keys are exhausted:

```text
AI request
   ↓
Provider Gateway
   ↓
No usable capacity
   ↓
QUOTA_EXHAUSTED / PROVIDER_UNAVAILABLE
   ↓
Clear user-facing failure
```

No unauthorized credential or hidden provider is used.

---

# 8. Network Security

GrowFlow should minimize exposed network surfaces.

## 8.1 Publicly Exposed Surface

Only intentionally public endpoints should be internet-accessible.

Expected public application surface:

- frontend
- required FastAPI HTTPS endpoint
- authentication/OAuth callbacks
- required health endpoints according to deployment policy

Database, internal worker interfaces, internal job mechanisms, and secret stores must not be exposed as public APIs.

## 8.2 Database Boundary

Application services communicate with PostgreSQL/Supabase through controlled infrastructure.

The frontend must never connect directly using privileged database credentials.

The backend owns privileged database operations.

## 8.3 Egress Controls

External calls should be limited to approved integration targets where practical:

- Supabase/PostgreSQL
- OpenRouter/provider endpoints
- GitHub
- Tavily
- OAuth providers
- email provider
- object storage
- LangSmith/observability services

Arbitrary outbound requests must not be exposed to user-controlled input.

---

# 9. HTTPS and TLS

Production traffic must use HTTPS.

Security requirements:

- TLS enabled
- secure certificate management
- HTTP redirected to HTTPS where applicable
- secure cookies where cookies are used
- no plaintext credentials in transit
- secure OAuth redirects
- no mixed-content application behavior

TLS termination must be at a trusted deployment boundary.

Internal plaintext communication should not be introduced merely for convenience where sensitive credentials or data cross a boundary.

---

# 10. CORS Security

CORS must be explicit.

Production configuration should:

- allow only known frontend origins
- avoid wildcard origins when credentials are involved
- keep development origins separate from production
- never accept arbitrary origin reflection
- validate configured origins at startup

CORS is not an authorization mechanism.

---

# 11. Security Headers

The production web/API boundary should apply appropriate security headers, including where applicable:

- Content-Security-Policy
- Strict-Transport-Security
- X-Content-Type-Options
- Referrer-Policy
- appropriate frame/embedding restrictions
- Permissions-Policy

Header configuration must account for frontend framework requirements and legitimate embedding behavior.

---

# 12. Rate Limiting

Rate limiting protects both security and infrastructure capacity.

Apply appropriate limits to:

- login
- registration
- password reset
- OAuth initiation/callback abuse surfaces
- AI requests
- blueprint generation
- assessment generation
- document upload
- RAG indexing
- GitHub synchronization
- help-request/message abuse
- expensive administrative operations
- public/unauthenticated endpoints

Rate limiting should be:

- endpoint-aware
- identity-aware where possible
- IP-aware where appropriate
- resource-aware for expensive operations
- observable
- bounded

A rate limit failure should return a clear machine-readable error such as `RATE_LIMITED`.

---

# 13. Brute-Force and Abuse Protection

Security-sensitive authentication endpoints require additional controls:

- request throttling
- progressive delays where appropriate
- suspicious activity detection
- account enumeration resistance
- generic authentication failure messages
- provider-native authentication protections where available

The system must not reveal whether an arbitrary email address belongs to a registered user through authentication recovery behavior.

---

# 14. SSRF Protection

GrowFlow integrates with external URLs and potentially processes user-provided references.

The application must defend against Server-Side Request Forgery.

Controls include:

- allowlisted integration domains where practical
- URL scheme restrictions
- reject dangerous schemes
- validate redirects
- prevent access to internal/private network ranges
- protect cloud metadata endpoints
- avoid arbitrary URL fetching through generic AI tools
- separate trusted integration adapters from arbitrary fetch functionality

Tavily and GitHub access should use their dedicated adapters rather than exposing generic server-side HTTP requests to users or agents.

---

# 15. File and Upload Security

Uploaded project files are untrusted.

Security controls include:

- maximum file size
- allowed file types
- MIME validation
- extension validation
- filename sanitization
- path traversal prevention
- safe storage keys
- archive safeguards if archives are supported
- decompression-bomb protection
- parser timeouts
- parser memory limits
- malware scanning where appropriate
- no executable upload behavior
- no arbitrary code execution

Uploaded code must be treated as data.

GrowFlow must never execute uploaded project code merely because it was uploaded or indexed.

---

# 16. Container and Runtime Hardening

Where Docker/containerization is used, production containers should follow least-privilege principles.

Recommended controls:

- minimal base images
- pinned/controlled dependencies
- non-root process execution
- read-only filesystem where practical
- no unnecessary Linux capabilities
- no privileged containers
- restricted mounted paths
- separate runtime credentials
- health checks
- resource limits
- controlled environment variables
- vulnerability scanning

The application should not require privileged operating-system access.

---

# 17. Worker Security

Workers execute high-value asynchronous operations.

Worker security must include:

- separate runtime identity where practical
- least-privilege credentials
- job authorization revalidation
- project-scope validation
- execution ownership validation
- safe input deserialization
- resource limits
- timeout controls
- retry bounds
- idempotency
- stale-state protection
- no arbitrary job execution from client input

A queued job must not be treated as permanently authorized merely because authorization existed when the job was created.

Before sensitive work executes:

```text
Queued Job
   ↓
Load current authorization context
   ↓
Validate resource/project scope
   ↓
Validate job state/version
   ↓
Execute
```

---

# 18. Background Job Security

Background jobs must be protected from:

- duplicate execution
- unauthorized execution
- stale execution
- poisoned payloads
- unbounded retries
- resource exhaustion

Every important job should have:

- job ID
- execution/correlation ID
- owner/resource context
- status
- attempt count
- timestamps
- retry policy
- failure metadata

Sensitive jobs should use explicit idempotency keys.

---

# 19. Database Security

PostgreSQL/Supabase is the canonical system of record.

Controls include:

- strong credentials
- private backend access where deployment supports it
- RLS defense in depth
- foreign-key integrity
- constraints
- restricted privileged credentials
- migration control
- backup protection
- connection limits
- query timeouts where appropriate
- safe transaction boundaries
- no raw SQL exposure to AI
- no database credentials in frontend

The Supabase service-role credential is backend-only and must never be exposed to browsers.

---

# 20. Row-Level Security

RLS provides database-level defense in depth.

RLS policies must reinforce application authorization for sensitive project/group data.

The application must still perform explicit authorization.

Correct model:

```text
Application Authorization
        +
Database RLS
        =
Defense in Depth
```

RLS must not be treated as permission to weaken service-layer authorization.

---

# 21. Storage Security

Object/file storage must enforce:

- private-by-default buckets where appropriate
- authorized access
- short-lived signed URLs when needed
- no public exposure of private project documents
- project ownership/scope validation
- safe object naming
- upload constraints
- download authorization
- deletion/version rules
- lifecycle controls

A document URL must never function as a substitute for authorization.

---

# 22. RAG Infrastructure Security

RAG is a derived knowledge layer and must preserve project isolation.

Mandatory controls:

1. authenticate requester
2. authorize requester
3. determine project scope
4. filter retrieval by authorized project
5. retrieve only authorized documents
6. pass retrieved data through context controls
7. treat content as untrusted data

There must be no unrestricted global vector search available to the AI.

Metadata should retain:

- project ID
- document ID
- document version
- chunk ID
- source/path
- embedding/index metadata

This allows security filtering and provenance.

---

# 23. Prompt Injection Defense

Retrieved documents, GitHub content, web research, uploaded files, and generated external content are untrusted.

Therefore:

> Retrieved text is data, not authority.

Controls:

- separate instructions from retrieved content
- preserve source metadata
- do not allow retrieved text to redefine system policy
- validate tool requests independently
- re-authorize every sensitive tool action
- prevent documents from granting permissions
- prevent AI-generated instructions from escalating privileges

This applies equally to:

- project documents
- source code
- README files
- GitHub content
- Tavily results
- generated documents

---

# 24. External Integration Security

Every integration must use a controlled adapter.

Examples:

```text
GitHubAdapter
TavilyAdapter
EmailAdapter
OAuthAdapter
StorageAdapter
OpenRouterGateway
```

Security responsibilities include:

- credential isolation
- timeout
- rate limits
- input validation
- output validation
- error normalization
- retry policy
- logging without secrets
- provider-specific security controls

Application services must not contain provider-specific credential logic.

---

# 25. OAuth Security

Google and GitHub OAuth must follow secure OAuth practices.

Controls include:

- validated redirect URIs
- state validation
- PKCE where applicable
- secure callback handling
- provider token protection
- token minimization
- no provider secrets in frontend
- account-linking validation
- rejection of unexpected providers
- secure failure handling

OAuth identity must map deterministically to the GrowFlow application identity.

---

# 26. GitHub Security

GrowFlow's GitHub functionality is monitoring-only.

Therefore the integration should not receive write permissions that are unnecessary for monitoring.

Required principle:

> Do not request repository-management permissions when read/monitoring permissions are sufficient.

GitHub credentials/tokens must:

- remain backend-controlled
- never enter AI prompts unnecessarily
- never be exposed to students/mentors/admins
- never appear in logs

---

# 27. Tavily Security

Tavily is used for current web research.

Security boundaries:

- requests originate through the Tavily adapter
- API credentials remain backend-only
- queries are validated
- response content is treated as untrusted evidence
- retrieved content cannot authorize application actions
- timeouts and rate limits apply
- failures degrade research functionality without corrupting canonical project state

---

# 28. Email Security

Email is an external side effect.

Controls include:

- centralized EmailAdapter
- validated recipient addresses
- template-controlled content
- no arbitrary header injection
- provider credentials isolated
- retry with idempotency
- delivery failures observable
- no sensitive content unless explicitly permitted

Email should not become a privileged command channel.

---

# 29. AI Tool Security

AI tools must be typed and narrow.

Bad:

```text
execute_sql(sql)
```

Better:

```text
get_project_overview(project_id)
get_project_tasks(project_id)
get_project_risks(project_id)
get_group_students(group_id)
search_project_documents(project_id, query)
get_github_activity(project_id)
```

Every tool call independently validates authorization.

AI reasoning cannot override authorization.

---

# 30. Admin Infrastructure Security

Admin access is powerful but bounded.

Default:

> Metadata-first, minimum necessary information.

Controlled investigation follows:

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

Admin must not gain infrastructure-level privileges merely because the user has the ADMIN application role.

Infrastructure administrator credentials and application-admin credentials remain separate concerns.

No impersonation is permitted.

---

# 31. Logging Security

Security logs must never contain:

- passwords
- raw API keys
- OAuth client secrets
- access tokens
- refresh tokens
- database passwords
- full sensitive document contents
- unnecessary private AI conversation content

Logs should use:

- correlation IDs
- execution IDs
- job IDs
- safe resource identifiers
- error codes
- security event types

Sensitive values must be redacted before logging.

---

# 32. Observability Security

Observability is not an authorization bypass.

LangSmith, logs, metrics, and traces must follow privacy and access policies.

Tracing should prefer:

- metadata
- identifiers
- timing
- model information
- token usage
- error information

over indiscriminate capture of private user content.

Sensitive payload capture must be explicitly justified and controlled.

---

# 33. Audit Security

Audit events are distinct from normal telemetry.

Audit records should cover security-sensitive actions such as:

- account status changes
- role changes
- controlled investigations
- privileged administrative actions
- authorization-sensitive changes
- security events
- credential/configuration events where appropriate

Audit records should be append-oriented and protected from ordinary modification.

---

# 34. Dependency and Supply-Chain Security

GrowFlow depends on Python packages, frontend packages, container images, frameworks, AI libraries, and external SDKs.

Security controls:

- dependency lock files
- controlled version updates
- vulnerability scanning
- dependency review
- removal of unused packages
- trusted package sources
- container image scanning
- reproducible builds where practical
- CI security gates for critical vulnerabilities

Dependencies should not be added merely because they are convenient.

---

# 35. Configuration Security

Configuration is environment-specific.

Required separation:

```text
Development
    ≠
Staging
    ≠
Production
```

Controls:

- separate credentials
- separate databases/projects where appropriate
- separate OAuth configuration
- separate AI provider credentials
- separate storage
- separate observability environments
- environment-specific CORS
- environment-specific logging behavior

Production secrets must never be copied into development environments.

---

# 36. Startup Security

The application should fail fast when mandatory infrastructure configuration is invalid.

Startup validation should detect:

- missing required secrets
- invalid URLs
- invalid CORS configuration
- incompatible environment configuration
- missing required provider settings
- invalid database configuration
- invalid storage configuration
- invalid observability configuration

Unsafe partial startup should be avoided.

---

# 37. Runtime Resource Protection

Infrastructure must defend against resource exhaustion.

Controls include:

- request body limits
- file-size limits
- AI token/output limits
- worker concurrency limits
- database connection limits
- job queue limits
- timeout controls
- retry bounds
- parser limits
- memory/CPU limits
- backpressure

Expensive operations should not be allowed to consume unlimited resources.

---

# 38. AI-Specific Resource Protection

AI workloads can become disproportionately expensive.

Controls include:

- request limits
- per-user/project quotas where appropriate
- model capability policies
- maximum context sizes
- maximum output sizes
- bounded regeneration
- bounded retries
- provider rate-limit handling
- five-key pool health management
- cost/usage observability

AI failures must not trigger uncontrolled recursive retries.

---

# 39. Security for Project Isolation

Project isolation is a fundamental security invariant.

A request involving:

```text
project_id
document_id
task_id
risk_id
github_repository_id
rag_document_id
ai_execution_id
```

must not be trusted solely because the identifier was supplied by an authenticated client.

The backend must establish the relationship between the resource and the authorized project/user/group.

---

# 40. Cross-Role Security

The same canonical resource may be viewed by different roles.

Security must distinguish:

- who can view
- what they can view
- what they can change
- which project/group scope applies
- whether privacy restrictions apply

Example:

```text
Student
  → own project

Mentor
  → authorized group/project students

Admin
  → platform metadata
  → deeper protected data only through controlled investigation
```

Role checks alone are insufficient.

---

# 41. Security for State-Changing AI

AI must not directly mutate canonical state.

Secure flow:

```text
User Request
    ↓
AI / Agent
    ↓
Structured Output
    ↓
Pydantic Validation
    ↓
QA / Policy Validation
    ↓
Explicit Confirmation where required
    ↓
Deterministic Domain Service
    ↓
Authorization
    ↓
Database Transaction
```

This protects the canonical state from:

- hallucinated mutations
- malformed output
- unauthorized changes
- prompt injection
- stale execution results

---

# 42. Stale Execution Protection

Long-running AI/workers can finish after project state has changed.

Before persistence:

- verify execution is still valid
- verify project/version relationship
- verify required authorization context
- verify no conflicting newer operation exists

A stale result must not overwrite a newer valid project state.

---

# 43. Security During Project Changes

The project-change workflow must preserve security:

```text
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

Each stage operates only on authorized project context.

A project-change request cannot be used to cross project boundaries or retrieve unrelated project information.

---

# 44. SSE Security

SSE streams can expose execution information.

Controls:

- authenticated connection
- execution ownership/scope validation
- authorization on stream establishment
- no arbitrary execution IDs
- safe event payloads
- no secret leakage
- reconnect authorization
- termination when execution access is revoked

SSE is a transport mechanism, not a permission mechanism.

---

# 45. Backup and Recovery Security

Backups may contain highly sensitive information.

Protect:

- database backups
- document storage backups
- configuration backups
- audit records
- generated documents
- RAG metadata

Controls:

- restricted backup access
- encryption where supported
- retention policy
- recovery testing
- separation from normal application credentials
- secure deletion according to retention requirements

A backup must not become an easier path to private project data.

---

# 46. Incident Response

Security incidents should follow a defined operational process:

```text
Detect
  ↓
Classify
  ↓
Contain
  ↓
Investigate
  ↓
Recover
  ↓
Verify
  ↓
Document
  ↓
Improve
```

Potential triggers:

- credential exposure
- repeated unauthorized access
- suspicious login activity
- storage exposure
- database access anomaly
- AI credential compromise
- dependency vulnerability
- container compromise
- abnormal resource consumption

Incident handling must preserve audit evidence where possible.

---

# 47. Security Severity

A practical severity model:

| Severity | Meaning |
|---|---|
| Critical | Credential compromise, cross-project data access, major production compromise |
| High | Privilege escalation, sensitive data exposure, serious authentication bypass |
| Medium | Significant abuse potential with limited scope |
| Low | Limited security weakness or defense-in-depth issue |

Critical and high-risk issues should block production release until addressed or explicitly accepted through the project's security process.

---

# 48. Security Testing

Infrastructure security must be tested through:

## Authentication

- brute-force resistance
- OAuth callback validation
- token handling
- session behavior

## Authorization

- horizontal privilege escalation
- vertical privilege escalation
- project isolation
- group isolation
- admin boundaries

## Infrastructure

- CORS
- security headers
- TLS
- rate limiting
- request limits
- container permissions
- configuration validation

## File Security

- malicious filenames
- path traversal
- oversized files
- invalid MIME types
- archive abuse
- parser failures

## AI Security

- prompt injection
- unauthorized tools
- cross-project retrieval
- secret leakage
- stale execution
- excessive retries

## Integration Security

- SSRF
- OAuth manipulation
- invalid webhooks
- provider failures
- token leakage

## Operational Security

- worker crash
- duplicate jobs
- replay
- credential rotation
- recovery
- backup restoration

---

# 49. Security Verification Matrix

| Area | Required Verification |
|---|---|
| Secrets | No secret committed or exposed |
| Auth | Unauthorized access rejected |
| RBAC | Role boundaries enforced |
| Project isolation | Cross-project access rejected |
| RLS | DB defense-in-depth verified |
| Storage | Unauthorized files inaccessible |
| RAG | Cross-project retrieval impossible |
| AI | Tools cannot bypass authorization |
| Workers | Authorization revalidated |
| SSE | Unauthorized streams rejected |
| Rate limiting | Abuse controls activate |
| SSRF | Internal targets rejected |
| Uploads | Unsafe files rejected |
| OAuth | State/redirect validation works |
| Containers | Non-root/minimal runtime verified |
| Dependencies | Vulnerability scanning active |
| Logging | Sensitive values redacted |
| Admin | Investigation controls enforced |
| Backups | Access restricted and recovery tested |

---

# 50. Security Ownership Model

| Security Concern | Primary Owner |
|---|---|
| User authentication | Supabase Auth + Identity |
| Application authorization | Authorization boundary |
| Project isolation | Domain/Application + RLS |
| Secrets | Deployment/Infrastructure |
| AI keys | AI Provider Gateway |
| Database security | Database/Infrastructure |
| Storage security | Storage layer |
| Worker security | Worker runtime |
| RAG security | Knowledge/RAG layer |
| Integration credentials | Integration adapters |
| Network security | Deployment/Infrastructure |
| Runtime hardening | Deployment/Infrastructure |
| Audit | Audit service |
| Security telemetry | Observability |
| Security testing | QA/Security verification |

No single component owns every security concern.

---

# 51. Security vs Availability

Security controls must not unnecessarily destroy platform availability.

When an optional integration fails:

```text
GitHub failure
    ↓
GitHub functionality degraded
    ↓
Core project remains usable
```

When AI quota is exhausted:

```text
AI unavailable
    ↓
AI generation unavailable
    ↓
Canonical project state preserved
```

When email fails:

```text
Email failure
    ↓
In-app notification remains available
```

Security and resilience therefore operate together.

---

# 52. What Infrastructure Security Must Not Do

6M explicitly does not introduce:

- Kubernetes
- service mesh
- microservices
- dedicated API gateway infrastructure
- Kafka
- RabbitMQ
- distributed identity platform
- custom secrets platform
- custom WAF platform
- custom SIEM
- custom encryption system without need
- autonomous security agents
- unrestricted firewall complexity
- unnecessary network segmentation
- arbitrary outbound HTTP services
- infrastructure that duplicates managed Supabase/deployment capabilities without justification

The architecture remains intentionally lean.

---

# 53. Final Infrastructure Security Architecture

```text
                         INTERNET
                            |
                    HTTPS / TLS Boundary
                            |
                       Frontend
                            |
                    FastAPI Application
                            |
             +--------------+--------------+
             |                             |
       Authorization                 Rate Limits
             |                             |
             +--------------+--------------+
                            |
                    Application Services
                            |
        +-------------------+-------------------+
        |                   |                   |
    PostgreSQL          Storage             Workers
      + RLS                                  |
        |                                    |
        |                              Authorization
        |                              Revalidation
        |                                    |
        |                         +----------+----------+
        |                         |                     |
        |                       RAG              AI Gateway
        |                                             |
        |                                      Provider Keys
        |                                             |
        |                                         OpenRouter
        |
        +-------------------+
                            |
                       Audit / Logs
                            |
                    Observability / LangSmith
```

Security is enforced across every boundary rather than concentrated in one component.

---

# 54. Infrastructure Security Invariants

The following are mandatory architectural invariants:

1. No production secret exists in source code.
2. No privileged secret reaches the frontend.
3. No AI agent receives raw provider credentials.
4. No AI agent receives unrestricted database access.
5. No client-supplied identifier bypasses resource authorization.
6. No project can retrieve another project's private RAG data.
7. No uploaded file is executed merely because it was uploaded.
8. No arbitrary server-side URL fetch is exposed to untrusted input.
9. No worker executes sensitive work without authorization revalidation.
10. No stale AI execution overwrites newer canonical state.
11. No public storage URL substitutes for authorization.
12. No authentication endpoint provides unnecessary account enumeration information.
13. No external integration receives more permission than required.
14. No security-sensitive value is written to logs.
15. No production environment reuses development secrets.
16. No unlimited AI retries or regeneration loops exist.
17. No admin role automatically grants unrestricted private-content access.
18. No infrastructure component bypasses the central security boundary.
19. Security failures must be observable.
20. Security controls must be tested, not merely documented.

---

# 55. Relationship to Previous Phase 6 Documents

6M depends on and reinforces the preceding architecture:

```text
6A Backend
   ↓
6B Database
   ↓
6C API
   ↓
6D Authentication & Security
   ↓
6E AI Infrastructure
   ↓
6F Agent Execution
   ↓
6G RAG & Documents
   ↓
6H Jobs & Events
   ↓
6I External Integrations
   ↓
6J Observability
   ↓
6K Storage & Files
   ↓
6L Deployment & Runtime
   ↓
6M Infrastructure Security
   ↓
6N Backend Architecture Finalization
```

6M therefore acts as the final infrastructure-security layer before Phase 6 consolidation.

---

# 56. Final Design Decision

GrowFlow uses a **defense-in-depth infrastructure security architecture** built around:

- managed authentication
- centralized application authorization
- PostgreSQL/RLS
- private storage
- centralized AI Provider Gateway
- typed integration adapters
- secure worker execution
- project-scoped RAG
- strict file handling
- SSRF protection
- rate limiting
- environment isolation
- secret isolation
- container hardening
- secure observability
- append-oriented auditing
- controlled administrative investigation
- security testing
- operational recovery

The design deliberately avoids unnecessary security infrastructure.

> **Secure the boundaries that matter, enforce authorization at every layer, isolate secrets and workloads, protect project data, and keep the platform operationally recoverable.**

---

# 57. Freeze Status

**Subphase 6M — Infrastructure Security is documented as FINAL.**

This document establishes the infrastructure-security requirements that the final **6N Backend Architecture Finalization** must consolidate with 6A–6L.

**6M is documentation only. It does not constitute implementation.**

**Next planned document: 6N — Backend Architecture Finalization, consolidation of Phase 6 and final freeze.**
