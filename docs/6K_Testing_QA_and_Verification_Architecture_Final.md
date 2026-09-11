# GrowFlow — Part 6K
# Testing, Quality Assurance & Verification Architecture — Final Specification

**Status:** FROZEN  
**Part:** 6K  
**System:** GrowFlow  
**Scope:** Testing strategy, test architecture, unit/integration/API/E2E/security testing, database and RLS verification, AI/agent evaluation, RAG evaluation, event/worker reliability testing, frontend testing, contract testing, regression testing, performance testing, failure-injection testing, deployment verification, test data, fixtures, CI quality gates, release gates, coverage strategy, defect classification, quality ownership, and explicit testing non-goals.

---

# 1. Purpose

Part 6K defines how GrowFlow proves that the architecture actually works.

The objective is not to maximize test count or code coverage.

The objective is:

> **Verify that every important system invariant, workflow, security boundary, AI behavior, integration boundary, and production-critical path behaves correctly under normal, invalid, concurrent, and failure conditions.**

GrowFlow is a system with:

- deterministic domain logic;
- role-based authorization;
- project isolation;
- AI agents;
- RAG;
- background jobs;
- domain events;
- external integrations;
- asynchronous execution;
- persistent execution state;
- deployment infrastructure.

Therefore testing must operate at multiple levels.

---

# 2. Quality Philosophy

GrowFlow follows:

```text
Test the contract
+
Test the behavior
+
Test the boundary
+
Test the failure
+
Test the security
+
Test the recovery
```

A successful test suite must prove more than:

```text
"the code runs"
```

It must prove:

```text
"the system preserves its architectural guarantees."
```

---

# 3. Testing Pyramid

Initial testing model:

```text
                    E2E
                   /   \
              API / Workflow
                 /       \
          Integration   Security
             /             \
        Domain / Services / AI
              /           \
             Unit Tests
```

Most tests should remain fast and deterministic.

Expensive AI/E2E tests should be targeted.

---

# 4. Test Categories

GrowFlow uses:

1. Unit tests
2. Domain/service tests
3. Repository/data-access tests
4. Integration tests
5. API tests
6. Contract tests
7. Security tests
8. AI/agent tests
9. RAG tests
10. Event/worker tests
11. Frontend tests
12. End-to-end tests
13. Performance tests
14. Failure/recovery tests
15. Deployment/smoke tests
16. Regression/evaluation tests

---

# 5. Unit Tests

Unit tests verify isolated logic.

Examples:

- progress calculation;
- health calculation;
- project lifecycle rules;
- risk classification;
- task state transitions;
- milestone state transitions;
- permission predicates;
- response mapping;
- configuration validation;
- chunking utilities;
- retry calculations.

---

# 6. Unit Test Principle

Unit tests should not require:

- production database;
- external AI;
- GitHub;
- Tavily;
- email;
- LangSmith.

Dependencies should be mocked/faked at appropriate boundaries.

---

# 7. Domain Testing

Domain tests are especially important because deterministic domain services own canonical state.

Test:

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

---

# 8. Project Lifecycle Tests

Verify legal transitions:

```text
IDEA
→ ASSESSMENT
→ BLUEPRINT
→ PLANNING
→ IMPLEMENTATION
→ TESTING
→ DEPLOYMENT
→ COMPLETED
```

Invalid transitions must be rejected.

---

# 9. Task State Tests

Test:

- start;
- complete;
- block;
- cancel;
- invalid transition;
- duplicate completion;
- unauthorized transition;
- stale update.

---

# 10. Milestone Tests

Test:

- creation;
- start;
- completion;
- blocking;
- task dependency;
- progress propagation;
- invalid transitions.

---

# 11. Progress Tests

Verify progress is deterministic.

Example:

```text
Task completion
→ milestone progress
→ project progress
```

AI must not directly overwrite the authoritative progress value.

---

# 12. Health Tests

Verify health responds correctly to defined inputs such as:

- overdue tasks;
- blocked work;
- inactivity;
- risks;
- deadline pressure;
- implementation state.

Exact scoring remains deterministic and defined by domain logic.

---

# 13. Risk Tests

Test:

- risk creation;
- severity;
- status;
- mitigation;
- resolution;
- acceptance;
- history.

---

# 14. Project Change Tests

The canonical workflow:

```text
REQUEST
→ IMPACT ANALYSIS
→ CONFIRMATION
→ REGENERATION
→ QA
→ COMPLETION
```

must be tested as a state machine.

---

# 15. Definition/Instance Isolation Tests

Critical invariant:

> Updating a Project Definition must not automatically modify existing Project Instances.

Tests must prove:

```text
Definition update
→ existing instance unchanged
→ new assignment receives new version
```

---

# 16. Assessment Tests

Verify:

- 10 core questions;
- 5 dynamic questions;
- one question at a time;
- answer persistence;
- sequential generation;
- previous-answer context;
- accumulated relevant context;
- project context;
- completion;
- result persistence;
- recovery after interruption.

---

# 17. Dynamic Assessment Security

A generated question must never receive unauthorized project/user context.

Test that context is:

```text
relevant
+
authorized
+
project-scoped
```

---

# 18. Blueprint Tests

Verify:

- all required document sections;
- valid structured output;
- version creation;
- persistence;
- renderer output;
- QA gate;
- failure handling;
- retry;
- regeneration;
- stale execution protection.

---

# 19. Blueprint Consistency Tests

Test relationships such as:

```text
Project Profile
↔ Technology
↔ Features
↔ MVP
↔ Specification
↔ Timeline
↔ Risks
↔ Tasks
↔ Milestones
↔ README
```

Contradictions should be detected by validation/QA.

---

# 20. Repository Tests

Repositories should be tested against the database contract.

Verify:

- create;
- retrieve;
- update;
- delete where allowed;
- filtering;
- pagination;
- transactions;
- concurrency;
- authorization-aware queries where applicable.

---

# 21. Database Integration Tests

Use a dedicated test database/environment.

Never run destructive integration tests against production.

Test:

- foreign keys;
- constraints;
- indexes where relevant;
- migrations;
- transaction behavior;
- RLS.

---

# 22. Migration Tests

Every migration should be tested.

Minimum:

```text
Known schema
→ migration
→ expected schema
→ application compatibility
```

---

# 23. Migration Regression

A new migration must not silently:

- remove required constraints;
- weaken RLS;
- break repositories;
- invalidate existing records;
- create incompatible application state.

---

# 24. RLS Tests

RLS is defense in depth.

Tests must prove:

```text
Student A
→ Project A = allowed
→ Project B = denied
```

and:

```text
Mentor Group A
→ Group A = allowed
→ Group B = denied
```

Admin behavior follows its controlled privacy boundary.

---

# 25. Authorization Matrix Tests

Test combinations:

```text
Role
+
Resource
+
Ownership/Group
+
Action
+
Privacy
```

Examples:

| Actor | Resource | Expected |
|---|---|---|
| Student | Own project | Allowed |
| Student | Other project | Denied |
| Mentor | Authorized group project | Allowed |
| Mentor | Unrelated group | Denied |
| Admin | Basic platform metadata | Allowed |
| Admin | Private content | Controlled investigation |

---

# 26. API Tests

API tests verify:

- routing;
- validation;
- authentication;
- authorization;
- status codes;
- response schema;
- error schema;
- pagination;
- filtering;
- idempotency;
- SSE behavior.

---

# 27. API Contract Tests

Every public endpoint should maintain a predictable contract.

Test:

```text
Request schema
→ service
→ response schema
```

Pydantic contracts should be exercised directly.

---

# 28. Error Contract Tests

Verify canonical error structure:

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

Machine-readable error codes must remain stable where they are public contracts.

---

# 29. HTTP Semantics Tests

Verify correct use of:

```text
200
201
202
204
400
401
403
404
409
422
429
500
502
503
```

Do not return 200 for every failure.

---

# 30. Idempotency Tests

Where idempotency is required:

```text
same request
+
same idempotency key
→
no duplicate business effect
```

Test duplicate requests and retry behavior.

---

# 31. Concurrent Request Tests

Test:

- double task completion;
- simultaneous project updates;
- duplicate help-request actions;
- concurrent definition assignment;
- simultaneous project-change confirmation.

Only one valid state transition should win where the business rule requires it.

---

# 32. Optimistic Concurrency

Where versioning/version checks are used:

```text
Version 5
 ↓
Client A updates
 → Version 6
 ↓
Client B submits Version 5
 → Conflict
```

Test this explicitly.

---

# 33. SSE Tests

Verify:

- execution stream;
- event ordering;
- reconnect;
- completion;
- failure;
- cancellation;
- browser disconnect;
- unauthorized stream access.

---

# 34. SSE Security

A user must not subscribe to:

```text
another user's execution
```

or:

```text
another project's stream
```

even if the execution ID is guessed.

---

# 35. AI Provider Gateway Tests

Test:

- provider request;
- timeout;
- retry;
- rate limit;
- cooldown;
- key rotation;
- fallback;
- provider unavailable;
- quota exhaustion;
- streaming;
- error normalization.

---

# 36. Five-Key Pool Tests

Test:

```text
Key 1 unavailable
→ Key 2
```

and:

```text
all keys exhausted
→ QUOTA_EXHAUSTED
```

No unauthorized credential should be attempted.

---

# 37. Retry Tests

Verify:

- bounded attempts;
- exponential backoff;
- jitter;
- retryable vs non-retryable errors;
- no infinite loops.

---

# 38. AI Structured Output Tests

Every agent contract should test:

```text
valid output
→ accepted
```

and:

```text
invalid schema
→ rejected
```

Malformed AI output must never silently become canonical state.

---

# 39. Agent Contract Tests

Each of the 12 agents should have:

- typed input contract;
- typed output contract;
- required context;
- validation;
- expected failure behavior.

---

# 40. Twelve-Agent Coverage

Required agent test coverage:

```text
1. Idea
2. Scope
3. Technology
4. Features
5. Specification
6. MVP
7. Timeline/Duration
8. Risk
9. Task
10. Milestone
11. README
12. QA/Judge
```

---

# 41. Agent Dependency Tests

Test the LangGraph workflow:

```text
Project + Assessment
→ Idea
→ Scope
→ parallel agents
→ Specification
→ Timeline
→ Risk
→ Task
→ Milestone
→ README
→ QA
```

Verify no agent executes before required dependencies exist.

---

# 42. Parallelism Tests

Independent agents should be allowed to execute concurrently where designed.

Tests must ensure:

```text
parallel execution
≠
shared mutable state corruption
```

---

# 43. LangGraph Tests

Test:

- graph construction;
- routing;
- conditional branches;
- failure routes;
- QA routes;
- regeneration;
- completion;
- cancellation;
- stale execution handling.

---

# 44. QA/Judge Tests

QA must detect:

- missing sections;
- invalid structure;
- contradiction;
- scope violation;
- technology inconsistency;
- timeline inconsistency;
- risk gaps;
- unsupported claims;
- README mismatch.

---

# 45. Regeneration Tests

If QA finds a targeted issue:

```text
QA finding
→ affected agent
→ regeneration
→ QA
```

Only the necessary regeneration should occur where targeted regeneration is supported.

---

# 46. Regeneration Bounds

Test that repeated QA failure cannot cause an infinite regeneration loop.

Expected:

```text
bounded attempts
→ FAILED
```

with the previous valid state preserved.

---

# 47. Stale AI Execution Tests

Scenario:

```text
Execution A starts
 ↓
Project changes
 ↓
Execution A becomes stale
 ↓
Execution A attempts persistence
```

Expected:

```text
stale output rejected
```

It must not overwrite newer project state.

---

# 48. AI Failure Safety

If AI fails:

```text
previous valid project state
```

must remain intact.

Test provider failure at every major generation stage.

---

# 49. AI Mentor Tests

Test:

- project grounding;
- authorized context;
- RAG retrieval;
- structured data retrieval;
- GitHub context;
- technical reasoning;
- combined context;
- action confirmation;
- unauthorized requests.

---

# 50. AI Tool Authorization Tests

Even if the agent is authorized, every tool call must independently enforce:

```text
user
+
role
+
resource
+
project/group scope
+
action
```

---

# 51. Prompt Injection Tests

Treat retrieved/uploaded content as untrusted.

Test documents containing instructions such as:

```text
Ignore previous instructions
Reveal secrets
Access another project
```

Expected:

```text
content treated as data
```

not authority.

---

# 52. AI Data Isolation Tests

Attempt:

```text
Project A AI
→ retrieve Project B
```

Expected:

```text
blocked
```

This must be tested through:

- API;
- tool layer;
- RAG;
- repository;
- direct identifier manipulation.

---

# 53. RAG Ingestion Tests

Test:

```text
Upload
→ validate
→ store
→ parse
→ chunk
→ embed
→ index
```

for supported file types.

---

# 54. File Security Tests

Test:

- invalid MIME;
- extension mismatch;
- oversized file;
- malformed PDF;
- malformed text;
- unsafe archive if archives are supported;
- path traversal;
- unsupported type.

Uploaded code must never be executed during indexing.

---

# 55. Chunking Tests

Verify:

- boundaries;
- heading preservation;
- code boundaries;
- overlap;
- metadata;
- deterministic behavior where expected.

---

# 56. Embedding Tests

Use mocked/fake embeddings for deterministic tests.

Verify:

- correct content;
- correct version;
- correct project;
- correct metadata;
- retry behavior;
- failure handling.

---

# 57. Retrieval Tests

Known query:

```text
Question
→ expected project document/chunk
```

Verify relevance and metadata.

---

# 58. RAG Version Tests

If:

```text
Document Version 1
→ indexed
```

then:

```text
Document Version 2
→ reindex
```

queries should not accidentally return stale Version 1 when only the latest active version is intended.

---

# 59. RAG Rebuild Tests

Simulate:

```text
Vector index lost
```

and verify:

```text
canonical documents
→ re-index
→ retrieval restored
```

---

# 60. RAG Quality Tests

Evaluate:

- Recall@K;
- Precision@K;
- MRR;
- zero-result rate;
- latency;
- citation/provenance coverage.

Exact thresholds are quality-policy configuration.

---

# 61. RAG Security Regression

Any change to:

- metadata filtering;
- retrieval;
- embeddings;
- chunking;
- vector schema;

must run project-isolation tests.

---

# 62. Document Synchronization Tests

Verify:

```text
Structured state
→ renderer
→ document version
→ RAG indexing
```

and:

```text
new document version
→ old derived index invalidated/retired
```

---

# 63. Event Tests

Test:

- event creation;
- transaction boundaries;
- outbox persistence;
- publication;
- handler;
- retry;
- duplicate delivery;
- dead-letter behavior.

---

# 64. Transactional Outbox Test

Critical scenario:

```text
Database transaction
+
domain change
+
outbox event
```

must commit atomically.

If the transaction fails:

```text
domain state = unchanged
outbox event = absent
```

---

# 65. Duplicate Event Tests

Deliver the same event twice.

Expected:

```text
one business effect
```

for idempotent handlers.

---

# 66. Event Ordering

Where ordering is semantically required, test it.

Do not assume global ordering across all events.

---

# 67. Worker Tests

Test:

- job claiming;
- processing;
- success;
- failure;
- retry;
- cancellation;
- timeout;
- crash recovery;
- stale job recovery;
- duplicate claim prevention.

---

# 68. Worker Crash Test

Simulate:

```text
Worker starts job
 ↓
Worker dies
```

Expected:

```text
job recoverable
```

without duplicate destructive effects.

---

# 69. Job State Tests

Verify:

```text
QUEUED
RUNNING
COMPLETED
FAILED
CANCELLED
```

and relevant domain-specific states.

---

# 70. Queue Backlog Tests

Simulate increased job volume.

Verify:

- bounded concurrency;
- queue growth visibility;
- no memory explosion;
- eventual processing;
- appropriate alerts.

---

# 71. Background Authorization Tests

A job created by a user may execute later.

At execution time, revalidate authorization and resource state where required.

Test:

```text
Authorized at submission
→ authorization/resource changes
→ worker execution
```

---

# 72. GitHub Integration Tests

Mock GitHub responses.

Test:

- connection;
- repository metadata;
- activity;
- rate limit;
- timeout;
- unavailable;
- changed repository;
- stale activity.

No repository management operations should accidentally be enabled.

---

# 73. Tavily Integration Tests

Test:

- research request;
- timeout;
- rate limit;
- malformed response;
- unavailable;
- evidence persistence;
- provenance.

Web evidence must not automatically become authoritative project state.

---

# 74. Email Integration Tests

Test:

- notification creation;
- email dispatch;
- failure;
- retry;
- duplicate prevention.

In-app notification state must survive email failure.

---

# 75. Storage Integration Tests

Test:

- upload;
- download authorization;
- version;
- deletion;
- signed URL where used;
- missing object;
- storage outage.

---

# 76. Frontend Testing

Frontend tests should cover:

- navigation;
- authentication;
- role switching;
- protected routes;
- project workspace;
- assessment;
- blueprint progress;
- document viewer;
- tasks;
- milestones;
- risks;
- notifications;
- AI Mentor;
- SSE states.

---

# 77. Frontend Authorization UX

Verify unauthorized resources do not render simply because a route is manually entered.

Backend remains authoritative.

---

# 78. UI State Tests

Test:

```text
Loading
Empty
Success
Error
Retry
Unauthorized
Not Found
Processing
Completed
```

for important screens.

---

# 79. AI Streaming UX Tests

Verify:

- initial focus;
- streaming response;
- user scroll;
- manual departure from stream;
- no forced scroll-back;
- completion;
- failure;
- reconnect.

---

# 80. Document Viewer Tests

Verify:

```text
View
Preview
Raw Markdown
Download
```

and that Download returns only the currently open document/version as intended.

---

# 81. Role-Specific UI Tests

Student:

```text
own projects only
```

Mentor:

```text
authorized groups/students/projects
```

Admin:

```text
platform observability
+
controlled private access
```

---

# 82. End-to-End Testing

E2E tests validate complete user journeys.

High-value journeys include:

### Student

```text
Register
→ Create Project
→ Assessment
→ Blueprint
→ Planning
→ Task
→ Progress
```

### Mentor

```text
Login
→ Create Group
→ Add Student
→ Create Project Definition
→ Assign
→ Monitor
```

### Admin

```text
Login
→ Overview
→ System Health
→ AI Observatory
→ Authorized Investigation
→ Audit
```

---

# 83. Student E2E Journey

At least one complete path should verify:

```text
Student
→ Project
→ 15-question assessment
→ Blueprint
→ Tasks
→ Milestone
→ Progress
→ Health
```

---

# 84. Mentor E2E Journey

Verify:

```text
Mentor
→ Group
→ Student
→ Project Instance
→ At Risk
→ Mentor Note
→ Help Request
```

---

# 85. Admin E2E Journey

Verify:

```text
Admin
→ Platform Overview
→ AI Observatory
→ Project monitoring
→ Controlled investigation
→ Audit record
```

---

# 86. Cross-Role E2E

Important scenario:

```text
Student completes task
 ↓
Domain event
 ↓
Progress changes
 ↓
Health recalculates
 ↓
Mentor projection updates
 ↓
Notification
 ↓
Activity
```

This verifies 6E/6H integration.

---

# 87. Definition Update E2E

Verify:

```text
Mentor updates definition
 ↓
existing instance unchanged
 ↓
new assignment gets new version
 ↓
existing student receives notification
```

---

# 88. Project Change E2E

Verify:

```text
Student requests change
 ↓
Impact analysis
 ↓
Confirmation
 ↓
Regeneration
 ↓
QA
 ↓
New version
```

---

# 89. Failure E2E

Simulate provider failure during blueprint generation.

Expected:

```text
Execution failed/degraded
+
user receives clear status
+
previous valid blueprint preserved
+
retry/recovery possible
```

---

# 90. Security Testing

Security testing is mandatory.

Areas:

- authentication;
- authorization;
- RLS;
- project isolation;
- group isolation;
- file security;
- prompt injection;
- SSRF;
- path traversal;
- XSS;
- CSRF where applicable;
- rate limiting;
- secret leakage;
- admin privacy;
- OAuth.

---

# 91. Authentication Security Tests

Test:

- invalid credentials;
- expired session;
- invalid refresh;
- password reset;
- OAuth state;
- account status;
- suspended user.

---

# 92. Authorization Security Tests

Test:

```text
horizontal privilege escalation
vertical privilege escalation
resource ID guessing
project scope bypass
group scope bypass
```

---

# 93. IDOR Testing

Attempt:

```text
GET /projects/{other_project_id}
```

with an otherwise valid user.

Expected:

```text
403 or 404 according to security policy
```

and no protected data leakage.

---

# 94. Admin Security Tests

Verify:

- non-admin cannot access Admin;
- admin cannot impersonate users;
- private content requires controlled investigation;
- investigation is audited.

---

# 95. File Security Testing

Test:

```text
../
absolute paths
malformed files
oversized files
unsafe content
```

and verify safe rejection.

---

# 96. SSRF Testing

External URL inputs must be validated where applicable.

Test attempts to access:

```text
localhost
private network
metadata endpoints
internal services
```

Expected:

```text
blocked
```

---

# 97. Prompt Injection Testing

Use adversarial documents and web results.

Verify:

```text
retrieved content
≠
trusted instruction
```

---

# 98. Secret Leakage Tests

Search:

- logs;
- API responses;
- frontend bundle;
- AI traces where applicable;
- error messages;

for:

```text
API keys
tokens
passwords
secrets
```

---

# 99. Rate-Limit Tests

Verify:

- login protection;
- AI request limits;
- expensive operation limits;
- abusive request behavior.

---

# 100. Performance Testing

Performance testing focuses on bottlenecks that matter.

Measure:

- API latency;
- database latency;
- worker throughput;
- queue latency;
- AI execution;
- RAG retrieval;
- document indexing;
- SSE connection behavior.

---

# 101. API Performance

Measure:

```text
P50
P95
P99
```

for important endpoints.

---

# 102. Database Performance

Test representative workloads:

- project queries;
- mentor student queries;
- dashboard queries;
- task/milestone queries;
- notification queries;
- RAG metadata queries.

---

# 103. Dashboard Performance

Mentor/Admin dashboards must not execute uncontrolled N+1 queries.

Performance tests should identify query explosion.

---

# 104. Worker Throughput

Measure:

```text
jobs/minute
average duration
P95 duration
queue age
```

under representative workload.

---

# 105. AI Performance

Track:

```text
time to first token
total generation latency
agent workflow duration
QA duration
```

where applicable.

---

# 106. RAG Performance

Measure:

```text
embedding latency
retrieval latency
context assembly
end-to-end RAG latency
```

---

# 107. Load Testing

Load testing should be scenario-based.

Examples:

```text
many students reading dashboards
many assessment submissions
multiple blueprint executions
RAG indexing burst
notification burst
```

---

# 108. Concurrency Testing

Particularly test:

```text
multiple AI executions
multiple workers
multiple task updates
multiple event handlers
```

---

# 109. Stress Testing

Stress testing should identify:

```text
failure threshold
```

rather than merely maximize requests.

---

# 110. Backpressure Testing

Generate more jobs than workers can process.

Verify:

```text
queue grows
system remains bounded
alerts trigger
workers eventually drain
```

---

# 111. Failure Injection

Test controlled failures:

- database unavailable;
- AI provider timeout;
- all AI keys exhausted;
- RAG unavailable;
- storage failure;
- GitHub failure;
- Tavily failure;
- email failure;
- worker crash;
- event handler failure;
- LangSmith unavailable.

---

# 112. Failure Isolation

Verify:

```text
Email failure
→ core project works

GitHub failure
→ project execution works

LangSmith failure
→ AI can continue where safe

Tavily failure
→ blueprint can follow defined degraded behavior
```

---

# 113. Database Failure

Test API behavior when PostgreSQL is unavailable.

Expected:

```text
controlled error
+
observability
+
no corrupted state
```

---

# 114. AI Provider Failure

Test:

```text
timeout
→ retry
→ fallback if valid
→ failure if exhausted
```

---

# 115. Quota Exhaustion

Expected:

```text
QUOTA_EXHAUSTED
```

with:

```text
no infinite retries
no unauthorized credential use
```

---

# 116. RAG Failure

If RAG fails:

```text
AI should not silently invent retrieved context.
```

The system should follow the defined degraded behavior.

---

# 117. Worker Recovery

Test:

```text
worker crash
→ job becomes recoverable
→ new worker claims
→ result persists once
```

---

# 118. Event Recovery

Test:

```text
handler fails
→ retry
→ succeeds
```

and:

```text
repeated failure
→ dead-letter/review state
```

---

# 119. Deployment Testing

Before production:

```text
Build
→ deploy staging
→ migration
→ health
→ smoke
→ integration
→ security
```

---

# 120. Production Smoke Tests

Only safe operations.

Verify:

- frontend;
- authentication;
- API;
- database;
- worker;
- notifications;
- safe AI path where appropriate.

No destructive production test.

---

# 121. Contract Testing With External Providers

Where practical, use mocked contract fixtures for:

- OpenRouter;
- GitHub;
- Tavily;
- email;
- storage.

External APIs should not make the entire CI suite dependent on live services.

---

# 122. Live Integration Tests

A small controlled live integration suite may exist for:

- staging;
- scheduled verification;
- deployment validation.

It should not be required for every local test run.

---

# 123. Test Doubles

Use:

```text
Mocks
Fakes
Stubs
Fixtures
Test containers/environments
```

according to the test boundary.

Do not mock the system so heavily that integration bugs become invisible.

---

# 124. Test Database

Prefer isolated test database/environment.

The test suite should control its data lifecycle.

---

# 125. Test Data Principles

Test data should be:

- deterministic;
- isolated;
- minimal;
- synthetic;
- reproducible.

---

# 126. Production Data

Do not use raw production user data as ordinary test fixtures.

If production-derived data is necessary, sanitize/minimize it.

---

# 127. Test Factories

Create reusable factories for:

```text
User
Student
Mentor
Group
Project Definition
Project Instance
Assessment
Blueprint
Task
Milestone
Risk
Document
Execution
Notification
```

Avoid manually constructing huge records repeatedly.

---

# 128. Test Fixtures

Fixtures should establish:

```text
authorized student
authorized mentor
admin
group
project
documents
AI execution
```

as needed.

---

# 129. Deterministic Time

Time-dependent tests should control time.

Test:

- deadlines;
- inactivity;
- cooldown;
- token expiry;
- notification timestamps;
- stale execution.

---

# 130. Deterministic IDs

Where practical, tests may use predictable IDs or factory-generated IDs.

Do not depend on random IDs to assert business behavior.

---

# 131. Coverage Strategy

Coverage is a signal, not the goal.

Prioritize high coverage for:

- authorization;
- state transitions;
- repositories;
- domain services;
- AI boundaries;
- RAG isolation;
- event handlers;
- critical API paths.

---

# 132. Coverage Anti-Pattern

Do not write meaningless tests solely to increase:

```text
coverage percentage
```

---

# 133. Critical Path Coverage

The following must have strong coverage:

```text
Authentication
Authorization
Project isolation
Project lifecycle
Assessment
Blueprint generation
Task completion
Milestone progression
Project change
AI Gateway
RAG retrieval
Events
Workers
Notifications
Admin investigation
```

---

# 134. Regression Suite

Every production defect should become a regression test when practical.

Flow:

```text
Bug
 ↓
Root Cause
 ↓
Regression Test
 ↓
Fix
 ↓
CI
```

---

# 135. Defect Classification

Useful categories:

```text
BUG
SECURITY
DATA INTEGRITY
PERFORMANCE
AI QUALITY
RAG QUALITY
DEPLOYMENT
INTEGRATION
UX
```

---

# 136. Severity

Suggested:

```text
Critical
High
Medium
Low
```

Security/data-integrity defects receive special priority.

---

# 137. Quality Gates

A release should not proceed when:

- critical tests fail;
- critical security tests fail;
- migrations fail;
- core authorization tests fail;
- production build fails;
- critical AI contract tests fail.

---

# 138. AI Quality Gate

AI changes should pass relevant:

```text
schema validation
+
QA tests
+
regression evaluation
+
security tests
```

---

# 139. RAG Quality Gate

RAG changes should pass:

```text
retrieval tests
+
project isolation
+
version consistency
+
performance checks
```

---

# 140. Security Gate

Security-critical changes require:

```text
authorization tests
+
RLS tests
+
negative tests
+
secret scanning
```

---

# 141. Migration Gate

Schema changes require:

```text
migration test
+
application compatibility
+
RLS validation
+
rollback/recovery understanding
```

---

# 142. CI Pipeline

Final logical CI:

```text
Commit
 ↓
Format/Lint
 ↓
Type Check
 ↓
Unit Tests
 ↓
Domain Tests
 ↓
Integration Tests
 ↓
API Tests
 ↓
Security Tests
 ↓
AI Tests
 ↓
RAG Tests
 ↓
Build
 ↓
E2E where appropriate
 ↓
Artifact
```

---

# 143. Fast CI vs Full CI

Not every test needs to run at every stage.

## Fast feedback

- formatting;
- lint;
- type;
- unit.

## PR/full validation

- integration;
- API;
- security;
- AI/RAG targeted.

## Release

- E2E;
- performance smoke;
- deployment;
- staging validation.

---

# 144. Test Parallelization

Independent test suites can run concurrently.

Avoid parallel tests that share mutable state without isolation.

---

# 145. Flaky Tests

Flaky tests are defects in the test system.

Do not normalize:

```text
retry until green
```

as the permanent solution.

---

# 146. Flaky Test Policy

When a test is flaky:

```text
Identify
→ isolate
→ diagnose
→ fix
```

Temporary quarantine should be explicit and tracked.

---

# 147. AI Test Flakiness

LLM outputs can vary.

Therefore tests should prefer:

```text
structured assertions
+
semantic constraints
+
evaluation thresholds
```

instead of exact full-text matching.

---

# 148. AI Deterministic Tests

Use mocked model responses for:

- domain integration;
- schema tests;
- workflow branching;
- failure handling.

Use real models for:

- evaluation;
- quality regression;
- representative end-to-end validation.

---

# 149. Prompt Tests

Prompt changes should test:

- required output;
- constraints;
- grounding;
- safety;
- tool behavior.

---

# 150. Agent Regression Dataset

Maintain representative cases for:

```text
basic project
intermediate project
advanced project
different technology stacks
different durations
different student skill levels
```

---

# 151. AI Edge Cases

Test projects with:

- very small scope;
- very broad scope;
- conflicting requirements;
- missing technology;
- unusual technology;
- unrealistic deadline;
- insufficient information;
- contradictory assessment answers.

---

# 152. Assessment Edge Cases

Test:

```text
short answers
long answers
empty where allowed
ambiguous answers
contradictory answers
rapid submission
duplicate submission
```

---

# 153. Blueprint Edge Cases

Test:

```text
minimal project
complex project
no optional tech
many technologies
short duration
long duration
tight deadline
high risk
```

---

# 154. RAG Edge Cases

Test:

- empty project knowledge base;
- one document;
- many documents;
- duplicate content;
- updated document;
- unsupported file;
- corrupted file;
- no relevant retrieval.

---

# 155. Notification Edge Cases

Test:

- duplicate event;
- email unavailable;
- read/unread race;
- multiple notifications;
- notification preference changes.

---

# 156. Help Request Edge Cases

Test:

```text
Open
→ In Progress
→ Resolved
```

including invalid transitions and duplicate resolution.

---

# 157. Mentor Note Tests

Mentor notes must:

- belong to authorized mentor/group/project context;
- not mutate project state;
- appear in correct activity/projection where defined.

---

# 158. GitHub Monitoring Tests

Verify monitoring cannot mutate:

- repository;
- issues;
- PRs;
- code;
- CI/CD.

---

# 159. Admin Investigation Tests

Verify:

```text
Request
→ Authorization
→ Minimum Required Data
→ Inspection
→ Audit
```

and that unauthorized investigation fails.

---

# 160. Privacy Regression Tests

A test should verify that default Admin views do not expose:

- private AI conversation content;
- private documents;
- unnecessary file content.

---

# 161. Data Integrity Tests

Test:

- orphan records;
- foreign-key violations;
- duplicate versions;
- inconsistent progress;
- stale project state;
- missing event references.

---

# 162. Reconciliation Tests

Simulate inconsistent derived state.

Example:

```text
Document exists
but RAG index missing
```

Expected:

```text
reconciliation detects
→ reindex/recovery path
```

---

# 163. Observability Tests

From 6I:

Verify:

- correlation IDs;
- execution IDs;
- job IDs;
- structured logs;
- metrics;
- LangSmith association;
- error codes;
- secret redaction.

---

# 164. Deployment Observability Tests

After deployment verify:

```text
API logs
Worker logs
Metrics
Health
AI traces
RAG telemetry
```

are functioning.

---

# 165. Disaster Recovery Tests

Verify:

```text
database restore
+
application deployment
+
worker startup
+
RAG rebuild
```

at the required operational cadence.

---

# 166. Backup Restore Test

A successful backup restore must demonstrate:

```text
database restored
→ migrations compatible
→ application reads data
→ authorization still works
```

---

# 167. RAG Disaster Test

Simulate vector loss:

```text
documents retained
→ RAG index rebuilt
→ retrieval restored
```

---

# 168. Worker Disaster Test

Simulate worker loss:

```text
jobs persisted
→ replacement worker
→ processing resumes
```

---

# 169. Release Verification Matrix

| Area | Required |
|---|---|
| Build | Yes |
| Unit | Yes |
| Integration | Yes |
| API | Yes |
| Security | Yes |
| RLS | Yes |
| AI contracts | Yes |
| RAG isolation | Yes |
| E2E critical paths | Yes |
| Migration | If schema changed |
| Performance | For relevant changes |
| Deployment smoke | Production release |

---

# 170. Test Ownership

| Area | Primary Responsibility |
|---|---|
| Domain | Backend |
| API | Backend |
| Database/RLS | Backend/Data |
| Security | Backend/Security |
| AI Gateway | AI/Backend |
| Agents | AI |
| RAG | Knowledge/AI |
| Workers | Runtime |
| Events | Runtime/Domain |
| Frontend | Frontend |
| E2E | Cross-functional |
| Deployment | DevOps |
| AI Quality | AI/QA |

---

# 171. Test Environment Architecture

```text
Developer
   ↓
Local Tests
   ↓
CI
   ↓
Isolated Test DB
   ↓
Staging
   ↓
Production Smoke
```

External providers should be mocked unless live validation is specifically required.

---

# 172. Test Environment Isolation

Never allow:

```text
test
→ production database
```

or:

```text
test
→ production storage
```

by accident.

Configuration validation should help prevent this.

---

# 173. Production Safety

Production tests must be:

- safe;
- non-destructive;
- scoped;
- observable;
- reversible.

---

# 174. Quality Ownership

Quality is not only the QA/Judge Agent.

Responsibility is shared:

```text
Developer
+
Domain
+
Security
+
AI
+
RAG
+
Runtime
+
Deployment
```

---

# 175. QA/Judge Agent Boundary

The QA/Judge Agent evaluates generated project outputs.

It does not replace:

- software testing;
- security testing;
- integration testing;
- deployment verification.

---

# 176. AI Evaluation vs Software Testing

These are separate.

### Software testing

> Does the system behave correctly?

### AI evaluation

> Is the model/agent output useful, grounded, and consistent?

Both are required.

---

# 177. RAG Evaluation vs RAG Integration Testing

### Integration

> Does indexing/retrieval work technically?

### Evaluation

> Does retrieval return useful information?

Both are required.

---

# 178. Security Testing vs Authorization Logic Tests

Unit authorization tests verify rules.

Security testing attempts to break those rules.

Both are required.

---

# 179. Testability Architecture Rule

Every important dependency should have a testable boundary:

```text
Provider
→ Adapter/Gateway

Storage
→ Adapter

Email
→ Adapter

GitHub
→ Adapter

Tavily
→ Adapter

Vector Store
→ Adapter
```

---

# 180. No Test-Only Business Logic

Do not create a second implementation solely for tests.

Use controlled test doubles at defined boundaries.

---

# 181. Contract Stability

Tests should protect important contracts:

```text
API
AI structured outputs
events
repositories
worker jobs
document versions
```

---

# 182. Event Contract Tests

Verify event schema compatibility:

```text
event_type
event_id
actor
resource
project
group
timestamp
correlation
metadata
```

---

# 183. Job Contract Tests

Verify job payloads are:

- typed;
- version-aware where needed;
- serializable;
- recoverable;
- authorized.

---

# 184. API Backward Compatibility

When modifying an existing endpoint, test clients using the current contract.

Breaking changes require deliberate API versioning.

---

# 185. Schema Compatibility

Database changes should be tested against:

```text
existing application version
+
new application version
```

when rolling deployments require compatibility.

---

# 186. Performance Regression

A feature should not silently introduce:

```text
N+1 queries
unbounded retrieval
unbounded context
unbounded retries
```

---

# 187. Resource Exhaustion Tests

Test limits for:

- file upload;
- request payload;
- AI context;
- chunk count;
- worker concurrency;
- database connections;
- queue depth.

---

# 188. Memory Safety

Document/RAG processing must remain bounded.

Large documents should not cause uncontrolled memory growth.

---

# 189. Timeout Tests

Every external/long-running boundary should have defined timeout behavior.

Test:

```text
provider timeout
storage timeout
GitHub timeout
Tavily timeout
database timeout
```

---

# 190. Cancellation Tests

Where cancellation is supported:

```text
Cancel request
→ execution state
→ worker behavior
→ persisted result
```

must remain consistent.

---

# 191. Browser Disconnect Tests

Test:

```text
browser disconnects
→ server execution continues
→ result persists
→ reconnect retrieves state
```

---

# 192. Reconnect Tests

SSE reconnect should not:

- duplicate execution;
- duplicate state mutation;
- expose another execution.

---

# 193. Notification Delivery Tests

Verify:

```text
event
→ notification
```

is idempotent where required.

---

# 194. Activity Timeline Tests

Verify role-based projections from canonical events.

The timeline must not become a second source of truth.

---

# 195. Admin Analytics Tests

Admin statistics should match authoritative queries.

Analytics should not invent values or silently diverge from domain state.

---

# 196. Cost Tests

Cost reporting should:

- use reliable provider usage;
- clearly distinguish estimates;
- not fabricate prices;
- remain consistent with gateway metadata.

---

# 197. Time/Timezone Tests

Backend timestamps remain UTC.

Test:

- deadline calculation;
- display conversion;
- inactivity;
- scheduled jobs;
- notification timing.

---

# 198. Locale Tests

Where UI supports localization, verify dates/numbers/text rendering without changing canonical UTC storage.

---

# 199. Accessibility Testing

Important frontend flows should test:

- keyboard navigation;
- focus;
- labels;
- semantic controls;
- readable errors;
- modal/drawer accessibility.

---

# 200. Responsive Testing

Verify key layouts across:

- desktop;
- tablet;
- mobile.

Especially:

```text
Left Nav
Project Workspace
Assessment
AI Mentor
Documents
```

---

# 201. Browser Compatibility

Test supported production browsers.

Exact browser matrix is release policy.

---

# 202. Visual Regression

Visual regression testing may be used for stable high-value screens.

It is optional initially and should not become a blocker for every minor UI change unless justified.

---

# 203. Accessibility Regression

Critical accessibility defects should become regression tests.

---

# 204. Test Reporting

CI should clearly report:

```text
passed
failed
skipped
flaky/quarantined
coverage
security
AI evaluation
```

---

# 205. Test Artifacts

Retain useful artifacts for failed CI:

- logs;
- screenshots;
- traces;
- API responses where safe;
- test reports.

Do not upload secrets/private production data.

---

# 206. E2E Failure Diagnostics

A failed E2E should correlate:

```text
test
→ request
→ correlation ID
→ execution/job
→ logs
→ trace
```

where applicable.

---

# 207. Test Naming

Tests should describe behavior.

Prefer:

```text
student_cannot_access_other_project
```

over:

```text
test_project_4
```

---

# 208. Test Organization

Recommended:

```text
tests/
├── unit/
├── domain/
├── repositories/
├── integration/
├── api/
├── security/
├── ai/
├── rag/
├── workers/
├── events/
├── e2e/
├── performance/
└── fixtures/
```

The exact directory structure may evolve without changing the testing architecture.

---

# 209. Test Execution Strategy

Fast:

```text
unit/domain
```

Medium:

```text
integration/API/security
```

Slow:

```text
E2E/performance/live AI evaluation
```

This keeps developer feedback practical.

---

# 210. Local Development

Developers should be able to run:

```text
lint
type-check
unit
targeted integration
```

without requiring every production dependency.

---

# 211. Pre-Commit Checks

Lightweight checks may include:

- formatting;
- linting;
- obvious secret scanning.

Do not put the full E2E suite into every commit hook.

---

# 212. Pull Request Checks

PR validation should include relevant:

```text
unit
integration
API
security
AI/RAG
```

depending on changed areas.

---

# 213. Change-Aware Testing

Examples:

### API change

Run:

```text
API
integration
contract
security
```

### RAG change

Run:

```text
RAG
security
AI evaluation
performance
```

### Database change

Run:

```text
migration
repository
RLS
integration
```

### Agent change

Run:

```text
AI
workflow
QA
regression
security
```

---

# 214. Full Release Suite

Before a major release:

```text
Full unit
+
Full integration
+
API
+
security
+
AI evaluation
+
RAG evaluation
+
critical E2E
+
deployment validation
```

---

# 215. Release Blockers

Release must be blocked for:

```text
Critical security failure
Critical data integrity failure
Core workflow failure
Migration failure
Broken authentication
Broken project isolation
Unrecoverable worker failure
Critical AI contract failure
```

---

# 216. Non-Blocking Findings

Examples may include:

```text
minor UI issue
non-critical telemetry gap
non-critical performance regression
```

subject to release policy.

---

# 217. Quality Trend Monitoring

Track over time:

```text
test failure rate
flaky rate
security defects
AI QA failure
RAG relevance
production defects
rollback frequency
```

This helps identify systemic quality problems.

---

# 218. Production Defect Feedback Loop

```text
Production Incident
 ↓
Diagnosis
 ↓
Root Cause
 ↓
Regression Test
 ↓
Fix
 ↓
CI
 ↓
Release
```

---

# 219. AI Production Feedback Loop

```text
User/Mentor Feedback
 ↓
AI Quality Analysis
 ↓
Evaluation Case
 ↓
Regression Suite
 ↓
Prompt/Agent/RAG Change
 ↓
Evaluation
 ↓
Release
```

---

# 220. Security Feedback Loop

```text
Security Finding
 ↓
Reproduce
 ↓
Fix
 ↓
Regression Test
 ↓
Security Suite
 ↓
Release
```

---

# 221. No False Confidence

Passing tests do not prove absence of all defects.

The objective is systematic risk reduction.

---

# 222. Testing and Architecture Freeze

Testing must validate the architecture already frozen in:

```text
6A–6J
```

It should not silently introduce:

- new services;
- new databases;
- new queues;
- new authorization models;
- new AI agents.

---

# 223. Testing Non-Goals

6K does not require:

- 100% code coverage;
- exhaustive UI snapshot testing;
- live external API calls in every test;
- exact LLM text matching;
- autonomous AI test generation as a dependency;
- separate test microservices;
- separate QA platform;
- dedicated performance cluster;
- complex fuzzing infrastructure;
- formal verification of the entire system;
- mutation testing as a mandatory gate;
- production data in tests.

---

# 224. Final Quality Architecture

```text
                    CODE CHANGE
                         │
                         ▼
                    FAST CHECKS
                  /       |       \
                 ▼        ▼        ▼
              Lint      Type     Unit
                 \        |        /
                  └───────┼───────┘
                          ▼
                   INTEGRATION
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
            API        SECURITY       AI/RAG
             │            │            │
             └────────────┼────────────┘
                          ▼
                     E2E / RELEASE
                          │
                          ▼
                       STAGING
                          │
                          ▼
                    PRODUCTION
                          │
                          ▼
                     OBSERVE
                          │
                          ▼
                  INCIDENT / FEEDBACK
                          │
                          ▼
                  REGRESSION TEST
```

---

# 225. Final AI Quality Architecture

```text
Agent
 ↓
Structured Output
 ↓
Pydantic
 ↓
Domain Validation
 ↓
QA/Judge
 ↓
Evaluation
 ↓
Accept / Regenerate / Fail
 ↓
Regression Dataset
```

---

# 226. Final Security Verification Architecture

```text
Authentication
 ↓
Role Authorization
 ↓
Resource Authorization
 ↓
Project/Group Scope
 ↓
Action Permission
 ↓
Privacy
 ↓
RLS
 ↓
Security Tests
```

---

# 227. Final Reliability Verification Architecture

```text
Job
 ↓
Worker
 ↓
Event
 ↓
Retry
 ↓
Failure
 ↓
Recovery
 ↓
Idempotency
 ↓
Observability
 ↓
Recovery Test
```

---

# 228. Final Deployment Verification

```text
Build
 ↓
Migration
 ↓
Deploy
 ↓
Health
 ↓
Smoke
 ↓
Security
 ↓
AI/RAG
 ↓
Observe
```

---

# 229. Complete 6A–6K Architecture

```text
6A  Backend Architecture
 ↓
6B  Database Architecture
 ↓
6C  API Architecture
 ↓
6D  Authentication & Security
 ↓
6E  AI Provider Gateway & Models
 ↓
6F  AI Agents & Orchestration
 ↓
6G  RAG & Knowledge
 ↓
6H  Events, Workers & Reliability
 ↓
6I  Observability & AI Evaluation
 ↓
6J  Deployment, Infrastructure & DevOps
 ↓
6K  Testing, QA & Verification
```

The architecture now closes the engineering loop:

```text
DESIGN
 ↓
IMPLEMENT
 ↓
EXECUTE
 ↓
OBSERVE
 ↓
TEST
 ↓
VERIFY
 ↓
RELEASE
 ↓
MONITOR
 ↓
IMPROVE
```

---

# 230. Final 6K Principles

1. Test deterministic business rules heavily.
2. Test authorization negatively, not only positively.
3. Test project and group isolation.
4. Test RLS as defense in depth.
5. Test AI contracts independently of live models.
6. Test AI quality separately from software correctness.
7. Test RAG relevance separately from RAG availability.
8. Test every critical background workflow.
9. Test retries and recovery.
10. Test idempotency.
11. Test stale execution protection.
12. Test migration compatibility.
13. Test external integration failures.
14. Test provider quota exhaustion.
15. Test worker crashes.
16. Test event duplication.
17. Test browser disconnect recovery.
18. Test SSE authorization.
19. Test secret redaction.
20. Test prompt injection.
21. Test SSRF/path traversal/file security.
22. Test admin privacy boundaries.
23. Test controlled investigations.
24. Test critical frontend journeys.
25. Test cross-role event propagation.
26. Use synthetic test data.
27. Never use production data casually.
28. Keep tests deterministic where possible.
29. Do not hide flaky tests behind unlimited retries.
30. Treat production defects as regression-test opportunities.
31. Use AI evaluation datasets for model/agent changes.
32. Use RAG evaluation for retrieval changes.
33. Test deployment, not just code.
34. Verify backups through restoration.
35. Keep quality gates proportional to risk.
36. Do not chase coverage percentages without behavioral value.
37. Do not introduce infrastructure solely to support testing.
38. Preserve the frozen architecture.
39. Make critical failures reproducible.
40. Quality is a continuous engineering responsibility.

---

# 231. Implementation Boundary

The testing architecture is frozen, while these implementation choices remain open:

- exact Python testing framework configuration;
- exact frontend testing framework;
- exact E2E framework;
- exact test database strategy;
- exact containerized test environment;
- exact CI provider;
- exact coverage threshold;
- exact AI evaluation framework;
- exact RAG evaluation datasets;
- exact performance-testing tool;
- exact security scanner;
- exact dependency scanner;
- exact browser matrix;
- exact visual regression tooling;
- exact live integration-test cadence.

These are implementation decisions and must not alter the architectural testing model.

---

# 232. Part 6K Freeze Statement

**Part 6K — Testing, Quality Assurance & Verification Architecture is architecturally FROZEN.**

GrowFlow now has a complete verification model covering:

- unit testing;
- domain testing;
- repository testing;
- database integration;
- migrations;
- RLS;
- authorization;
- API contracts;
- error contracts;
- idempotency;
- concurrency;
- SSE;
- AI Provider Gateway;
- five-key quota behavior;
- structured AI outputs;
- all 12 agents;
- LangGraph orchestration;
- QA/Judge;
- regeneration;
- stale execution protection;
- AI Mentor;
- prompt injection;
- project-scoped RAG;
- document processing;
- embeddings;
- retrieval;
- RAG quality;
- events;
- transactional outbox;
- workers;
- retries;
- recovery;
- external integrations;
- frontend;
- E2E workflows;
- performance;
- load/concurrency;
- failure injection;
- deployment;
- disaster recovery;
- observability;
- security;
- privacy;
- test data;
- CI/CD;
- regression;
- release gates;
- AI quality evaluation.

The final principle is:

> **GrowFlow is not considered production-ready because it builds successfully. It is production-ready when its critical contracts, state transitions, security boundaries, AI behavior, integrations, failure recovery, and deployment behavior have been systematically verified.**

**6K is frozen.**
