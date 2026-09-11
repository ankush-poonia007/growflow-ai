# GrowFlow — Part 6I
# External Integrations Architecture — Final Specification

**Status:** FROZEN
**Part:** 6I
**System:** GrowFlow
**Scope:** GitHub integration, Tavily web research, Google OAuth, GitHub OAuth, email delivery, external-provider adapters, credential handling, scopes, synchronization, retries, rate limits, timeouts, failure isolation, provenance, background execution, authorization, security, observability, testing, and explicit integration non-goals.

---

# 1. Purpose

Part 6I defines how GrowFlow integrates with external platforms and providers without allowing those systems to become accidental authorities over GrowFlow's canonical state.

The integration principle is:

> **External systems are capabilities and sources of information; GrowFlow remains the authority for GrowFlow application state.**

The primary integrations are:

```text
GitHub
Tavily
Google OAuth
GitHub OAuth
Email
```

The architecture also defines the adapter boundary used to isolate provider-specific behavior.

---

# 2. Integration Philosophy

GrowFlow should integrate with external services through explicit boundaries:

```text
Application / Domain
        ↓
Integration Interface
        ↓
Provider Adapter
        ↓
External Service
```

Provider-specific SDKs, HTTP details, credentials, retry policies, and response normalization belong behind the integration boundary.

Domain services must not depend directly on:

```text
GitHub SDK
Tavily SDK/API
Google OAuth client
Email provider SDK
```

---

# 3. External Integration Principles

1. External providers are not canonical GrowFlow state.
2. Provider access is authorized before use.
3. Provider credentials never reach the frontend.
4. Provider credentials never reach AI agents directly.
5. Provider-specific behavior stays behind adapters.
6. External failures must be isolated where possible.
7. Retries are bounded.
8. Rate limits are respected.
9. Timeouts are explicit.
10. External responses are validated before use.
11. Stored external data has provenance.
12. Background integrations revalidate authorization.
13. Integration activity is observable.
14. Provider changes should minimize domain impact.
15. Integration capabilities remain least-privilege.
16. Monitoring integrations must not silently become management capabilities.

---

# 4. Integration Inventory

| Integration | Primary Purpose | Authority |
|---|---|---|
| GitHub | Project repository/activity monitoring | External source |
| Tavily | Current web research | External evidence |
| Google OAuth | Authentication | Authentication provider |
| GitHub OAuth | Authentication/integration authorization | Authentication provider |
| Email | Optional notification delivery | Delivery channel |

---

# 5. Integration Boundary

Logical backend structure:

```text
backend/
└── app/
    ├── domain/
    │   └── integrations/
    └── infrastructure/
        ├── github/
        ├── tavily/
        ├── email/
        └── ...
```

The exact directory layout follows 6A and may evolve without changing the architectural boundary.

---

# 6. Adapter Pattern

Each external service should have an explicit adapter/interface.

Examples:

```text
GitHubAdapter
TavilyAdapter
EmailAdapter
GoogleOAuthAdapter
GitHubOAuthAdapter
```

The application depends on typed interfaces/contracts.

Infrastructure implements them.

---

# 7. Provider-Neutral Contracts

Application code should consume normalized contracts rather than provider-specific response objects.

Example:

```text
GitHub API response
        ↓
GitHubAdapter
        ↓
Normalized RepositoryActivity
        ↓
Application Service
```

This prevents provider response shapes from spreading through the system.

---

# 8. External Client Responsibilities

Adapters own:

- provider authentication;
- request construction;
- provider-specific serialization;
- provider-specific error parsing;
- timeout configuration;
- retry classification;
- rate-limit interpretation;
- response normalization.

Adapters do not own GrowFlow business rules.

---

# 9. Application Service Responsibilities

Application services own:

- authorization;
- use-case orchestration;
- persistence;
- domain rules;
- integration result interpretation;
- event creation where required.

The adapter should not decide whether a GrowFlow project is healthy, complete, or at risk.

---

# 10. Authorization Boundary

External integration execution follows:

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
Integration Authorization
 ↓
Provider Adapter
```

The adapter is not an authorization bypass.

---

# 11. Background Authorization

For asynchronous integrations:

```text
Authorized at request time
```

does not automatically mean:

```text
Authorized at execution time
```

Workers must revalidate relevant authorization/resource state before sensitive work.

---

# 12. Credential Architecture

Credentials are stored through secure runtime configuration/secret management.

Examples:

```text
OAuth client secrets
GitHub integration credentials
Tavily API key
Email credentials
```

must never be committed to source control.

---

# 13. Credential Exposure Rules

Credentials must never be exposed through:

- frontend bundles;
- API responses;
- logs;
- exceptions;
- AI prompts;
- agent context;
- RAG documents;
- telemetry.

---

# 14. Environment Separation

External credentials are environment-specific:

```text
Development
Staging
Production
```

Development credentials must not provide production access.

---

# 15. Credential Rotation

Integrations must support credential replacement without changing domain code.

Rotation should be possible through:

```text
Secret/configuration management
        ↓
Typed settings
        ↓
Adapter
```

---

# 16. OAuth Overview

GrowFlow uses external OAuth providers for authentication/integration authorization.

Primary OAuth providers:

```text
Google
GitHub
```

Supabase Auth remains the authentication authority established in 6D.

---

# 17. OAuth Boundary

Logical flow:

```text
Browser
 ↓
GrowFlow/Supabase OAuth flow
 ↓
Google/GitHub
 ↓
Authorization
 ↓
Callback
 ↓
Supabase Auth
 ↓
GrowFlow identity mapping
```

The exact callback implementation remains deployment-specific.

---

# 18. OAuth Security

OAuth flows must protect against:

- CSRF;
- authorization-code interception;
- redirect manipulation;
- state mismatch;
- invalid callback;
- account-linking confusion.

Only allowlisted redirect destinations should be accepted.

---

# 19. Google OAuth

Google OAuth provides:

- authentication;
- identity information required for account creation/login.

GrowFlow should request only the scopes necessary for the selected authentication flow.

---

# 20. GitHub OAuth

GitHub OAuth may support:

- authentication;
- GitHub integration authorization where explicitly required.

Scopes must be minimum necessary for the capabilities being used.

GrowFlow does not request repository-management permissions merely because GitHub integration exists.

---

# 21. OAuth Account Mapping

OAuth identity must map deterministically to the GrowFlow application identity.

The canonical relationship is:

```text
OAuth identity
 ↓
Supabase Auth identity
 ↓
GrowFlow users
```

Account-linking behavior must avoid accidental creation of duplicate application identities.

---

# 22. OAuth Failure Handling

Handle:

- user denial;
- expired authorization;
- invalid callback;
- provider outage;
- revoked authorization;
- invalid state;
- account mismatch.

The user should receive a safe, actionable result without provider secrets/details.

---

# 23. OAuth Revocation

If an external authorization is revoked:

```text
GrowFlow detects/receives failure
 ↓
integration marked unavailable/requires reauthorization
```

Core project state remains intact.

---

# 24. GitHub Integration Purpose

GitHub integration is monitoring-only.

It provides project context such as:

- repository metadata;
- repository activity;
- commits/activity where supported;
- monitoring information.

It does not become a project execution authority.

---

# 25. GitHub Non-Goals

GrowFlow does not initially use the integration to:

- edit repositories;
- write code;
- create issues;
- modify pull requests;
- merge pull requests;
- manage repository settings;
- manage CI/CD;
- administer GitHub organizations.

---

# 26. GitHub Data Flow

```text
GitHub
  ↓
GitHubAdapter
  ↓
Normalize
  ↓
Validate
  ↓
Persist useful metadata/activity
  ↓
Project/mentor/admin projections
```

---

# 27. GitHub Connection

A project/user GitHub connection should contain only the metadata necessary to maintain the integration.

Sensitive tokens remain protected by the authentication/secret boundary.

---

# 28. GitHub Repository Association

A repository association must be authorized for the relevant user/project.

A repository identifier alone does not establish permission.

---

# 29. GitHub Monitoring Scope

The integration should retrieve only information required for GrowFlow monitoring.

Avoid broad repository synchronization by default.

---

# 30. GitHub Synchronization

GitHub activity may be synchronized through background jobs.

Conceptual flow:

```text
Scheduled/triggered sync
 ↓
Revalidate authorization
 ↓
GitHubAdapter
 ↓
Fetch changes
 ↓
Normalize
 ↓
Persist
 ↓
Emit relevant event
```

---

# 31. GitHub Sync Frequency

The exact cadence is an operational configuration.

It should be proportional to:

- project workload;
- GitHub API limits;
- required freshness;
- infrastructure cost.

Avoid unnecessary high-frequency polling.

---

# 32. GitHub Rate Limits

The adapter must recognize provider rate-limit responses.

Behavior:

```text
Rate limited
 ↓
record provider state
 ↓
respect retry/reset information
 ↓
defer synchronization
```

Do not repeatedly hammer the provider.

---

# 33. GitHub Failure

If GitHub is unavailable:

```text
GitHub monitoring = degraded/stale
```

but:

```text
project execution
tasks
milestones
core application
```

continue where possible.

---

# 34. GitHub Staleness

The UI should distinguish:

```text
recent activity
```

from:

```text
last known activity
```

when synchronization is delayed.

Do not present stale external data as real-time certainty.

---

# 35. GitHub Data Provenance

Persist useful metadata such as:

```text
provider
repository
external identifier
observed timestamp
source/update timestamp where available
```

This allows users and operators to understand the origin of the data.

---

# 36. GitHub Activity Authority

GitHub activity can inform:

- project activity;
- mentor monitoring;
- AI context;
- operational signals.

It must not directly determine canonical:

- task completion;
- milestone completion;
- project phase;
- project health.

Deterministic GrowFlow services own those states.

---

# 37. GitHub AI Context

AI may retrieve authorized GitHub monitoring data through a typed integration tool.

Flow:

```text
AI Mentor
 ↓
Authorized GitHub Tool
 ↓
GitHub Integration Service
 ↓
Persisted/approved GitHub data
 ↓
AI Context
```

The AI does not receive raw GitHub credentials.

---

# 38. GitHub RAG Boundary

GitHub source code is not automatically indexed into project RAG in V1.

If this changes later, it requires an explicit architecture decision and security/scale analysis.

---

# 39. GitHub Webhook Boundary

Webhooks may be introduced if freshness requirements justify them.

If used:

- validate signatures;
- authenticate source;
- deduplicate events;
- authorize project mapping;
- persist safely;
- process asynchronously.

Polling remains acceptable where sufficient.

---

# 40. Tavily Integration Purpose

Tavily provides current web research for GrowFlow's AI workflows.

Primary uses include:

- researching existing solutions;
- checking current APIs;
- checking current platform capabilities;
- finding current technical evidence;
- supporting MVP analysis.

---

# 41. Tavily Is Evidence, Not Authority

Tavily results are:

```text
research evidence
```

not automatic project truth.

The AI/domain workflow must evaluate and validate evidence before incorporating it into project outputs.

---

# 42. Tavily Data Flow

```text
Agent
 ↓
Authorized Tavily Tool
 ↓
TavilyAdapter
 ↓
Search
 ↓
Normalize
 ↓
Evidence/provenance
 ↓
MVP/Research workflow
```

---

# 43. Tavily Credentials

Tavily credentials are backend-only.

They must never reach:

- browser;
- agent prompt;
- frontend state;
- documents;
- logs.

---

# 44. Tavily Search Scope

Research requests should be:

- relevant to the current project;
- bounded;
- authorized;
- purpose-specific.

Do not expose Tavily as an unrestricted general network primitive to agents.

---

# 45. Tavily Result Validation

Validate:

- response structure;
- URLs;
- titles;
- snippets/content where returned;
- provider status.

Malformed results must not silently become trusted evidence.

---

# 46. Tavily Provenance

Research records should preserve useful provenance such as:

```text
query
source URL
title
retrieved timestamp
provider
relevance/context metadata where available
```

This supports auditability and later review.

---

# 47. Tavily Research Storage

Current web research is stored separately from canonical project state.

Research sources may be associated with the relevant blueprint/MVP workflow.

They do not automatically become project knowledge documents.

---

# 48. Tavily RAG Boundary

Tavily research is not automatically indexed into the project's persistent RAG knowledge base.

This prevents temporary/current web evidence from being confused with uploaded/project-owned knowledge.

---

# 49. Tavily Failure

If Tavily is unavailable:

```text
research capability = degraded
```

The system should not fabricate current-web evidence.

The affected workflow should either:

- use previously valid evidence where appropriate; or
- fail clearly/retry according to the workflow policy.

---

# 50. Tavily Rate Limits

The integration must respect provider limits.

Use:

```text
bounded retry
+
backoff
+
rate-limit awareness
```

No infinite retries.

---

# 51. Tavily Security

Treat web content as untrusted.

Search results can contain:

```text
prompt injection
malicious URLs
misleading claims
unsafe instructions
```

Retrieved content is data, not executable authority.

---

# 52. Email Integration Purpose

Email is an optional notification delivery channel.

Canonical notification state remains:

```text
GrowFlow Notification Service
```

Email is only a delivery mechanism.

---

# 53. Email Data Flow

```text
Domain Event
 ↓
Notification Service
 ↓
In-App Notification
 ↓
Optional Email Adapter
 ↓
Email Provider
```

Email failure must not remove the in-app notification.

---

# 54. Email Adapter

The adapter owns:

- provider API/SMTP details;
- authentication;
- request formatting;
- provider errors;
- retry classification;
- delivery response normalization.

It does not own notification business rules.

---

# 55. Email Idempotency

Repeated event delivery must not unintentionally generate uncontrolled duplicate emails.

Use appropriate notification/delivery identifiers to support deduplication.

---

# 56. Email Retry

Transient failures may retry with bounded backoff.

Permanent failures should transition to an appropriate failed/degraded delivery state rather than retry forever.

---

# 57. Email Rate Limits

Respect provider limits.

Notification bursts should be bounded or queued rather than overwhelming the provider.

---

# 58. Email Preferences

Where user preferences exist, the Notification Service determines whether email delivery is enabled.

The email adapter does not decide user preferences.

---

# 59. Email Failure Isolation

Expected behavior:

```text
Email unavailable
 ↓
In-app notification remains
 ↓
Delivery failure observable
```

Core project operations continue.

---

# 60. External Integration Error Model

Normalize provider failures into GrowFlow integration-level categories:

```text
AUTHENTICATION_FAILED
AUTHORIZATION_FAILED
RATE_LIMITED
TIMEOUT
UNAVAILABLE
INVALID_RESPONSE
NOT_FOUND
CONFLICT
PROVIDER_ERROR
NETWORK_ERROR
```

Provider-specific details remain inside adapter diagnostics where safe.

---

# 61. Retry Classification

Retry only errors that are plausibly transient.

Generally retryable:

```text
timeout
temporary network failure
provider unavailable
temporary rate limit
```

Generally non-retryable:

```text
invalid credentials
invalid request
permanent authorization denial
unsupported operation
malformed input
```

Exact provider behavior is adapter-specific.

---

# 62. Backoff

Use bounded exponential backoff with jitter.

Do not use:

```text
infinite retries
```

---

# 63. Timeout Strategy

Every external request should have an explicit timeout appropriate to its operation.

Timeouts prevent:

```text
external provider
→ worker/API indefinitely blocked
```

---

# 64. Circuit/Degradation Behavior

A provider that repeatedly fails may be temporarily marked unavailable/cooldown according to the integration implementation.

This should prevent cascading failure.

---

# 65. External Failure Isolation

The platform should degrade by capability:

```text
GitHub failure
→ GitHub monitoring degraded

Tavily failure
→ current research degraded

Email failure
→ email delivery degraded

OAuth provider failure
→ affected authentication flow degraded
```

Unrelated core services should remain available.

---

# 66. Integration State

Where useful, persist integration state such as:

```text
CONNECTED
ACTIVE
DEGRADED
RATE_LIMITED
REAUTH_REQUIRED
DISABLED
FAILED
```

The exact state machine depends on the integration.

---

# 67. Synchronization State

For synchronized integrations, track safe operational metadata:

```text
last_sync_started
last_sync_completed
last_success
last_failure
next_attempt
cursor/checkpoint where applicable
```

Do not store unnecessary provider payloads.

---

# 68. Incremental Synchronization

Where the provider supports it, prefer incremental synchronization using:

- timestamps;
- cursors;
- event identifiers;
- provider checkpoints.

Avoid repeatedly downloading the entire dataset.

---

# 69. Idempotent Synchronization

Repeated synchronization must not create duplicate canonical records.

Use external identifiers and appropriate uniqueness constraints.

---

# 70. External Data Retention

Store external data only when it provides ongoing product value.

Avoid retaining entire provider responses when normalized metadata is sufficient.

---

# 71. External Data Deletion

When an integration is disconnected, GrowFlow should follow the defined data-retention policy.

Credentials/tokens should be revoked/removed where appropriate.

Useful historical project metadata may have separate retention rules.

---

# 72. Integration Disconnect

Disconnect should:

- stop future synchronization;
- revoke/delete stored authorization material where applicable;
- mark integration unavailable;
- preserve unrelated project state.

---

# 73. Integration Reconnection

Reconnection should:

```text
authorize
 ↓
validate
 ↓
associate
 ↓
sync/reconcile
```

without duplicating existing external records.

---

# 74. External Identifier Mapping

External records should use a stable mapping such as:

```text
provider
+
external_id
+
GrowFlow resource
```

to prevent duplicate associations.

---

# 75. Provider Response Validation

External responses are untrusted input.

Validate before:

```text
persistence
AI context
domain interpretation
```

---

# 76. External Input Security

Validate:

- URLs;
- identifiers;
- response sizes;
- payload structure;
- MIME/content where applicable;
- redirect targets.

---

# 77. SSRF Boundary

Any integration that accepts or retrieves arbitrary URLs must use controlled outbound access.

Do not allow user/AI-provided URLs to become unrestricted server-side network requests.

Block or restrict:

```text
localhost
private networks
cloud metadata endpoints
internal services
```

where applicable.

---

# 78. Web Research URL Safety

Tavily results may contain arbitrary URLs.

The application must not automatically fetch every returned URL with privileged internal network access.

---

# 79. GitHub URL Safety

GitHub repository URLs and identifiers must be normalized/validated.

Do not turn arbitrary user-provided URLs into unrestricted outbound requests.

---

# 80. OAuth Redirect Safety

Only configured callback/redirect destinations are valid.

Never trust an arbitrary redirect URL supplied by the client.

---

# 81. External Payload Limits

Apply limits to external responses where practical:

```text
response size
items
pagination
processing duration
```

This protects workers and memory.

---

# 82. Provider Pagination

Adapters should handle provider pagination explicitly.

Application services should receive bounded normalized results rather than uncontrolled provider pages.

---

# 83. Provider API Evolution

Provider API changes should be isolated in adapters.

Tests should detect:

```text
contract change
→ adapter failure
```

before it silently affects domain behavior.

---

# 84. External Integration Testing

Testing follows 6K.

Required categories:

- unit adapter tests;
- contract tests;
- integration tests;
- failure tests;
- authorization tests;
- rate-limit tests;
- timeout tests;
- security tests;
- live staging smoke tests where justified.

---

# 85. Adapter Unit Tests

Mock provider responses.

Test:

```text
success
timeout
rate limit
auth failure
invalid response
provider error
```

---

# 86. Contract Fixtures

Maintain representative provider fixtures where practical.

Fixtures should cover:

- normal response;
- pagination;
- empty response;
- malformed response;
- provider error;
- changed response shape.

---

# 87. Live Provider Tests

Live external tests should be limited to:

- staging;
- deployment validation;
- scheduled health verification where useful.

They should not be required for every local development test.

---

# 88. GitHub Integration Tests

Test:

```text
OAuth/connection
repository association
activity retrieval
pagination
rate limit
revocation
stale sync
duplicate sync
provider outage
```

---

# 89. Tavily Integration Tests

Test:

```text
search
result normalization
provenance
rate limit
timeout
provider outage
malformed response
prompt-injection content
```

---

# 90. Email Integration Tests

Test:

```text
notification
delivery
failure
retry
deduplication
provider outage
```

---

# 91. OAuth Integration Tests

Test:

```text
successful login
denial
invalid state
invalid callback
redirect manipulation
account mapping
revoked authorization
duplicate identity prevention
```

---

# 92. Integration Authorization Tests

Attempt:

```text
Student A
→ GitHub data for Project B
```

Expected:

```text
blocked
```

Similarly test mentor/group scope and admin privacy rules.

---

# 93. Integration Secret Tests

Verify credentials do not appear in:

- API responses;
- logs;
- frontend;
- AI traces;
- exceptions;
- activity events.

---

# 94. Background Integration Tests

Simulate:

```text
job submitted
→ authorization changes
→ worker starts
```

Verify the worker revalidates required authorization/state.

---

# 95. Integration Event Tests

Where external changes produce GrowFlow events:

```text
External observation
 ↓
normalized event
 ↓
domain/event service
 ↓
notification/activity/projection
```

Events must remain idempotent.

---

# 96. GitHub Activity Event

Example:

```text
GitHub activity detected
→ GitHubActivityDetected
→ persist/notify/project projection as defined
```

The event does not directly overwrite project health.

---

# 97. Email Event Boundary

Email delivery status is an operational/delivery concern.

It must not redefine the underlying GrowFlow notification itself.

---

# 98. Tavily Research Event Boundary

Research completion may update:

```text
research source state
```

and relevant AI execution context.

It does not directly mutate arbitrary project state.

---

# 99. Integration Observability

Every important integration operation should be traceable through:

```text
correlation_id
+
execution_id/job_id where applicable
+
provider
+
operation
+
duration
+
status
+
error category
```

---

# 100. Sensitive Telemetry

Do not log:

- OAuth authorization codes;
- access tokens;
- refresh tokens;
- API keys;
- email credentials;
- sensitive provider payloads unnecessarily.

---

# 101. Integration Metrics

Useful metrics include:

```text
requests
successes
failures
timeouts
rate limits
latency
retries
reconnections
sync duration
sync freshness
```

---

# 102. Provider Health

Admin/operational observability may expose:

```text
GitHub health
Tavily health
Email health
OAuth health
```

without exposing credentials.

---

# 103. Integration Alerts

Alert when there is meaningful operational degradation, such as:

- sustained GitHub sync failures;
- repeated Tavily failures;
- email delivery failure spikes;
- OAuth callback failures;
- provider rate-limit exhaustion.

Avoid alerting on isolated transient failures unless operationally significant.

---

# 104. Integration Health and Core Health

An external integration can be degraded without marking the entire platform unavailable.

Example:

```text
Email = DEGRADED
Platform = HEALTHY
```

unless the failed dependency is genuinely critical to the affected platform capability.

---

# 105. AI Integration Boundary

AI agents may use integration tools only through authorized application/tool boundaries.

Example:

```text
Agent
 ↓
Typed GitHub/Tavily Tool
 ↓
Authorization
 ↓
Adapter
 ↓
Provider
```

No agent receives provider credentials.

---

# 106. Tool Least Privilege

Integration tools should expose only the operations required by the agent.

For example:

```text
GitHub monitoring tool
→ read repository/activity
```

not:

```text
GitHub administration tool
```

---

# 107. Tool Input Validation

Agent-provided integration parameters must be validated exactly like user-provided parameters.

Never trust an LLM-generated identifier or URL merely because it came from an internal agent.

---

# 108. Integration Data in RAG

External integration data should not automatically enter RAG.

Each source requires an explicit indexing policy.

Current V1:

```text
GitHub source code → not automatically indexed
Tavily research → not automatically indexed
```

Project-owned uploaded/generated documents remain the primary RAG knowledge sources.

---

# 109. Integration Data in AI Context

Context builder should include external data only when:

- relevant;
- authorized;
- fresh enough;
- provenance is available;
- within context budget.

---

# 110. External Evidence and AI Claims

AI-generated statements based on external providers should retain provenance where useful.

The system must distinguish:

```text
provider evidence
```

from:

```text
AI inference
```

---

# 111. Integration Caching

Caching may be introduced where provider limits/performance justify it.

Initial caching should remain narrow and correctness-aware.

Do not cache sensitive authorization data broadly.

---

# 112. Stale Cache Protection

Cached external information must have an appropriate freshness policy.

Do not present stale GitHub activity or current web research as live information without qualification.

---

# 113. Integration Concurrency

Concurrent synchronization jobs for the same integration/resource should be controlled to prevent:

- duplicate requests;
- race conditions;
- inconsistent checkpoints;
- provider abuse.

---

# 114. Integration Job Idempotency

Jobs should use stable idempotency/resource keys where appropriate.

Example:

```text
github-sync:{project_id}:{repository_id}
```

is an implementation pattern, not a mandatory literal key.

---

# 115. Integration Cancellation

Long-running integration work should support cancellation where practical.

Cancellation must leave persisted state consistent.

---

# 116. Provider Unavailability Recovery

Recovery flow:

```text
Failure
 ↓
Record
 ↓
Backoff/Cooldown
 ↓
Retry
 ↓
Success
 ↓
Reconcile freshness
```

---

# 117. Reconciliation

If external synchronization becomes inconsistent:

```text
Persisted checkpoint
+
provider state
        ↓
reconciliation
        ↓
correct normalized state
```

Reconciliation must not arbitrarily mutate unrelated project state.

---

# 118. External Data Conflict

If external data conflicts with GrowFlow canonical state:

```text
GrowFlow canonical state wins
```

unless a specific integration contract explicitly defines otherwise.

---

# 119. Example: GitHub vs Task Completion

A GitHub commit may suggest work was performed.

It does not automatically mean:

```text
Task = COMPLETED
```

The task state remains under the defined GrowFlow workflow.

---

# 120. Example: Tavily vs Project Technology

Tavily may show that a technology is currently available or popular.

It does not automatically change:

```text
Project Technology
```

without the appropriate blueprint/project workflow.

---

# 121. Example: Email vs Notification

Email delivery failure does not mean:

```text
Notification = absent
```

The notification remains in GrowFlow.

---

# 122. Provider Account Limits

Provider account quotas are external constraints.

GrowFlow must surface useful degraded states rather than pretending unlimited capacity.

---

# 123. Integration Cost Awareness

Integration frequency and payload size should be proportional to product value.

Avoid:

```text
high-frequency polling
+
full dataset synchronization
```

without a concrete requirement.

---

# 124. Integration Configuration

Centralized typed configuration should contain:

```text
provider URLs
timeouts
retry limits
rate-limit behavior
OAuth configuration
feature enablement
credentials/secrets references
```

Adapters consume typed configuration through dependency injection.

---

# 125. No Direct Environment Reads

Integration adapters should not independently parse `.env`.

They receive configuration through the centralized settings/dependency system from 6A.

---

# 126. Provider SDK Boundary

Provider SDKs, where used, remain infrastructure dependencies.

They must not leak into:

```text
domain entities
domain services
API DTOs
frontend contracts
```

---

# 127. Integration Domain Model

The domain may define provider-neutral concepts such as:

```text
ExternalRepository
RepositoryActivity
ResearchSource
NotificationDelivery
OAuthIdentity
IntegrationStatus
```

Provider-specific payloads remain infrastructure-level.

---

# 128. Persistence Boundary

Only useful normalized external data should be persisted.

Avoid turning GrowFlow's database into a mirror of every provider API.

---

# 129. External Data Ownership

| Data | Authority |
|---|---|
| GitHub activity observation | GitHub source |
| GrowFlow project state | GrowFlow |
| Tavily research result | Tavily/web source |
| Blueprint decision | GrowFlow workflow |
| Email delivery status | Email provider/adapter |
| Notification state | GrowFlow |
| OAuth identity authentication | Supabase Auth |
| GrowFlow role | GrowFlow |

---

# 130. Integration Privacy

External data must follow the same project/group privacy boundaries as GrowFlow data.

A connected provider does not grant unrestricted access to unrelated GrowFlow resources.

---

# 131. Disconnect Privacy

After disconnect:

- future provider access stops;
- stored credentials are invalidated/removed as appropriate;
- retained data follows policy;
- AI tools cannot continue using revoked authorization.

---

# 132. Provider Permission Changes

If a provider changes scopes/permissions:

```text
detect failure
→ mark reauthorization required
→ stop affected operations
→ notify user where appropriate
```

Do not repeatedly attempt unauthorized operations.

---

# 133. External API Version Changes

Adapter-level compatibility should isolate provider API changes.

Before changing adapter behavior:

```text
fixture tests
+
integration tests
+
staging validation
```

should be updated.

---

# 134. Webhook Security

If webhooks are introduced:

- validate provider signature;
- reject malformed requests;
- deduplicate events;
- persist before asynchronous processing where appropriate;
- authorize mapped resources;
- never trust payloads blindly.

---

# 135. Polling Security

Polling credentials and authorization must remain server-side.

Polling jobs must respect provider limits and resource scope.

---

# 136. External Integration Failure Matrix

| Failure | Expected Behavior |
|---|---|
| GitHub unavailable | Monitoring degraded |
| GitHub rate limited | Backoff/defer |
| GitHub authorization revoked | Reauthorization required |
| Tavily unavailable | Research degraded |
| Tavily rate limited | Backoff/defer |
| Email unavailable | In-app notification continues |
| Email rate limited | Queue/retry |
| Google OAuth unavailable | Google login degraded |
| GitHub OAuth unavailable | GitHub OAuth degraded |
| Invalid provider response | Fail safely + observe |
| Network timeout | Bounded retry |
| Credential invalid | Stop retry + reconfigure |

---

# 137. Integration Security Checklist

```text
[ ] Provider credentials backend-only
[ ] Secrets externalized
[ ] OAuth state protected
[ ] Redirects allowlisted
[ ] Minimum OAuth scopes
[ ] GitHub monitoring-only
[ ] Agent tools least-privilege
[ ] URLs validated
[ ] SSRF protections
[ ] Provider responses validated
[ ] Rate limits respected
[ ] Timeouts configured
[ ] Retries bounded
[ ] Sensitive telemetry redacted
[ ] Background authorization revalidated
[ ] Integration data project-scoped
```

---

# 138. Integration Reliability Checklist

```text
[ ] Adapter boundary
[ ] Normalized contracts
[ ] Idempotent synchronization
[ ] External identifiers
[ ] Checkpoints where needed
[ ] Retry classification
[ ] Backoff
[ ] Failure state
[ ] Reconciliation
[ ] Provider degradation
[ ] Job recovery
[ ] Observability
```

---

# 139. Integration Testing Checklist

```text
[ ] Unit adapter tests
[ ] Contract fixtures
[ ] Authorization tests
[ ] Rate-limit tests
[ ] Timeout tests
[ ] Failure tests
[ ] OAuth tests
[ ] GitHub tests
[ ] Tavily tests
[ ] Email tests
[ ] Security tests
[ ] Staging live tests where justified
```

---

# 140. Integration Observability Checklist

```text
[ ] Correlation IDs
[ ] Job/execution IDs
[ ] Provider operation
[ ] Latency
[ ] Success/failure
[ ] Retry count
[ ] Rate limits
[ ] Sync freshness
[ ] Provider health
[ ] Error categories
[ ] Secret redaction
```

---

# 141. External Integration Architecture

```text
                     GrowFlow
                        │
                Application Services
                        │
              Integration Interfaces
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
 GitHub Adapter    Tavily Adapter    Email Adapter
        │               │                │
        ▼               ▼                ▼
     GitHub           Tavily        Email Provider


              Authentication Boundary
                        │
                 ┌──────┴──────┐
                 ▼             ▼
             Google OAuth   GitHub OAuth
                 │             │
                 └──────┬──────┘
                        ▼
                   Supabase Auth
                        │
                        ▼
                 GrowFlow Identity
```

---

# 142. External Integration + Worker Architecture

```text
Domain/Event/Command
        ↓
Background Job
        ↓
Authorization Revalidation
        ↓
Integration Service
        ↓
Adapter
        ↓
External Provider
        ↓
Normalized Result
        ↓
Persistence
        ↓
Event / Projection / Notification
```

---

# 143. External Integration + AI

```text
AI Agent / Mentor
        ↓
Typed Integration Tool
        ↓
Authorization
        ↓
Integration Service
        ↓
Adapter
        ↓
Provider / Stored External Data
        ↓
Validated Context
        ↓
AI Reasoning
```

AI never bypasses this chain.

---

# 144. External Integration + RAG

```text
Project Documents
        ↓
Document/RAG Pipeline
        ↓
RAG

External Integration Data
        ↓
Explicit indexing policy
        ↓
RAG only if deliberately enabled
```

V1 does not automatically index GitHub source or Tavily research.

---

# 145. External Integration + Events

```text
External observation
        ↓
Normalize
        ↓
Persist
        ↓
Domain Event
        ↓
Notification / Activity / Projection
```

Events remain idempotent and do not bypass domain ownership.

---

# 146. External Integration + Security

```text
User
 ↓
Authentication
 ↓
Role
 ↓
Resource Scope
 ↓
Action Permission
 ↓
Integration Permission
 ↓
Adapter
 ↓
Provider
```

---

# 147. External Integration + Observability

```text
Request
 ↓
Correlation ID
 ↓
Job/Execution ID
 ↓
Adapter operation
 ↓
Provider response
 ↓
Normalized result
 ↓
Persistence
 ↓
Logs / Metrics / Trace
```

---

# 148. External Integration + Deployment

Deployment must provide:

```text
provider credentials
+
OAuth configuration
+
network access
+
timeouts
+
retry configuration
+
observability
```

through environment-specific configuration.

---

# 149. External Integration + Failure Recovery

```text
Provider Failure
 ↓
Classify
 ↓
Retry if transient
 ↓
Cooldown if necessary
 ↓
Persist failure state
 ↓
Alert if meaningful
 ↓
Recover
 ↓
Reconcile
```

---

# 150. Final Integration Responsibility Matrix

| Responsibility | Owner |
|---|---|
| Provider communication | Adapter |
| Provider-specific errors | Adapter |
| Credential retrieval | Configuration/secret boundary |
| Authorization | GrowFlow authorization |
| Business rules | Domain/application |
| Persistence | Repository/domain service |
| Job execution | Worker |
| Retry orchestration | Integration/runtime |
| Notifications | Notification Service |
| Activity | Event/activity system |
| AI access | Authorized AI tools |
| RAG indexing | RAG service/policy |
| Observability | Application/runtime observability |

---

# 151. Explicit Integration Non-Goals

GrowFlow does not initially require:

- GitHub repository management;
- GitHub code writing;
- issue/PR automation;
- CI/CD management through GitHub;
- unrestricted web browsing tool;
- unrestricted arbitrary URL fetching;
- automatic indexing of all GitHub code;
- automatic indexing of Tavily results;
- email as canonical notification state;
- direct provider calls from agents;
- direct provider calls from frontend;
- provider-specific logic in domain services;
- unlimited synchronization;
- full provider data mirroring;
- complex integration orchestration infrastructure;
- separate integration microservices;
- Kafka/RabbitMQ solely for integrations;
- custom API gateway solely for integrations.

---

# 152. Implementation Boundary

The integration architecture is frozen, while these implementation choices remain open:

- exact GitHub SDK/client;
- exact Tavily client;
- exact email provider;
- exact OAuth provider configuration;
- exact webhook vs polling strategy;
- exact synchronization cadence;
- exact retry values;
- exact timeout values;
- exact provider-health thresholds;
- exact integration-state schema details;
- exact live integration-test cadence;
- exact storage location for provider credentials;
- exact monitoring provider.

These choices must preserve the adapter, authorization, security, reliability, and canonical-state boundaries defined here.

---

# 153. Relationship to 6A–6H and 6J–6M

## 6A — Backend Architecture

6I follows the layered modular-monolith and adapter boundaries.

## 6B — Database Architecture

Normalized integration metadata/activity is persisted in PostgreSQL according to domain ownership.

## 6C — API Architecture

External integration capabilities are exposed only through authorized API/application services.

## 6D — Authentication & Security

OAuth, secrets, scopes, RLS, authorization, SSRF and privacy controls are inherited.

## 6E — AI Provider Gateway

AI provider communication remains separate from application integrations. GitHub/Tavily are accessed through their own controlled adapters/tools.

## 6F — Agent Execution

Agents may use authorized GitHub/Tavily tools through the integration boundary.

## 6G — RAG

External integration data is not automatically treated as project knowledge.

## 6H — Events/Workers

Synchronization and delivery work execute through persistent background jobs/events.

## 6J — Observability

Integration operations emit logs, metrics, traces and health information.

## 6K — Storage

Integration artifacts, where any are persisted as files, follow the canonical storage architecture.

## 6L — Deployment

Provider credentials and integration runtime configuration are environment-specific.

## 6M — Infrastructure Security

Network, secret, runtime and outbound-request protections apply to all integrations.

---

# 154. Final External Integration Architecture

GrowFlow's integration architecture is:

```text
                EXTERNAL SYSTEMS
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       GitHub        Tavily       Email
          │            │            │
          └────────────┼────────────┘
                       ▼
                  Adapters
                       │
                Integration Layer
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
       Workers       AI Tools      API Services
          │            │             │
          └────────────┼─────────────┘
                       ▼
                Domain/Application
                       │
                       ▼
                  PostgreSQL
                       │
                       ▼
              Events / Notifications
```

Authentication follows its separate path:

```text
Google/GitHub OAuth
        ↓
Supabase Auth
        ↓
GrowFlow Identity
        ↓
Authorization
```

---

# 155. Final Non-Negotiable Rules

1. External providers never become accidental authorities over GrowFlow state.
2. All external services sit behind explicit adapter boundaries.
3. Provider-specific SDK models never leak into the domain.
4. Authorization occurs before integration access.
5. Background jobs revalidate authorization where required.
6. Provider credentials remain backend-only.
7. OAuth secrets remain backend-only.
8. Minimum provider scopes are required.
9. GitHub remains monitoring-only in V1.
10. GitHub data does not automatically complete tasks.
11. GitHub data does not automatically determine project health.
12. Tavily provides evidence, not project authority.
13. Tavily content is treated as untrusted data.
14. Tavily results are not automatically persistent project knowledge.
15. GitHub source is not automatically indexed into RAG in V1.
16. Email is a delivery channel, not notification authority.
17. In-app notifications survive email failure.
18. External responses are validated.
19. External URLs are treated as untrusted.
20. SSRF protections apply to outbound URL retrieval.
21. OAuth redirects are allowlisted.
22. Retries are bounded.
23. Backoff uses jitter.
24. Timeouts are explicit.
25. Rate limits are respected.
26. Synchronization is idempotent.
27. External identifiers prevent duplicate records.
28. Integration failures degrade by capability.
29. External data carries provenance where useful.
30. External data is stored only when useful.
31. Integration state is observable.
32. Sensitive telemetry is redacted.
33. AI tools use least privilege.
34. AI agents never receive provider credentials.
35. AI agents cannot bypass integration authorization.
36. Integration jobs survive worker restarts through persisted state.
37. Provider outages must not corrupt canonical project state.
38. Reconciliation is explicit.
39. Provider API changes are isolated in adapters.
40. No integration microservices are required initially.
41. No new message broker is required solely for integrations.
42. Integration complexity must be justified by actual product requirements.

---

# 156. Part 6I Freeze Statement

**Part 6I — External Integrations Architecture is architecturally FROZEN.**

GrowFlow now has a defined integration model covering:

- GitHub;
- Tavily;
- Google OAuth;
- GitHub OAuth;
- email;
- adapter interfaces;
- provider-neutral contracts;
- authorization;
- credentials;
- secret handling;
- environment separation;
- OAuth security;
- GitHub monitoring;
- GitHub synchronization;
- Tavily research;
- evidence/provenance;
- email delivery;
- rate limits;
- retries;
- backoff;
- timeouts;
- provider failure;
- degradation;
- synchronization;
- reconciliation;
- external identifiers;
- AI tool integration;
- RAG boundaries;
- event boundaries;
- background jobs;
- integration observability;
- security;
- testing;
- deployment;
- explicit non-goals.

The governing principle is:

> **Integrate external systems through narrow, typed, authorized adapters; normalize their outputs; preserve provenance; isolate their failures; and never allow an external provider to bypass GrowFlow's canonical state, authorization, or security boundaries.**

**6I is frozen.**
