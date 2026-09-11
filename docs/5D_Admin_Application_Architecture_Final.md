# GrowFlow — Part 5D: Admin Application Architecture
## Final Specification — Frozen

**Status:** FINAL / FROZEN  
**Part:** 5D — Admin Application Architecture  
**Product:** GrowFlow  
**Depends On:** Part 5A — Application Foundation, Part 5B — Student Application Architecture, Part 5C — Mentor Application Architecture, Part 4 — AI Agent Architecture

---

# 1. Purpose

The Admin application is the platform-level governance, observability, monitoring, and controlled-intervention layer of GrowFlow.

The Admin is **not a super-user version of a Mentor** and does not operate student projects on their behalf.

The three application roles have deliberately different responsibilities:

| Role | Primary Responsibility |
|---|---|
| Student | Build and execute the project |
| Mentor | Supervise students and projects |
| Admin | Govern, observe, analyze, monitor, and intervene when necessary |

The Admin application must provide enough visibility to determine:

- Is the platform operating correctly?
- Are users, groups, and projects behaving normally?
- Are AI systems and agents operating correctly?
- Are costs and usage under control?
- Is RAG/document infrastructure healthy?
- Are there security or authorization concerns?
- Are there platform-wide patterns that require intervention?

At the same time, Admin access must **not become unrestricted access to private user content**.

---

# 2. Core Admin Philosophy

Admin operates according to five principles:

1. **Observe** — understand what is happening across the platform.
2. **Analyze** — identify patterns, anomalies, failures, and risks.
3. **Govern** — manage platform-level accounts, access, policies, and operational controls.
4. **Investigate** — inspect additional information only when a legitimate reason exists and access is authorized.
5. **Intervene Carefully** — take only explicitly permitted administrative actions.

Admin should primarily be a **control tower**, not an operator of student work.

---

# 3. Changes From the Previous Admin Proposal

The approved version expands the Admin application in several important ways.

## 3.1 Admin AI Scope Expanded

The previous proposal focused mainly on platform operations.

The final Admin AI additionally provides **basic cross-platform information retrieval**.

Admin AI can answer authorized questions such as:

- How many active students are on the platform?
- How many mentors are registered?
- Which groups exist?
- Which projects are active?
- What projects are currently at risk?
- Which students belong to a particular group?
- Which mentor manages a group?
- What is the current status of a project instance?
- How many AI requests occurred today?
- Which agents have the highest failure rate?
- Which projects have the most blocked tasks?
- Is the AI gateway experiencing elevated failures?

This is different from unrestricted private-data access.

Admin AI can retrieve **basic platform/entity information by default**, while deeper private inspection remains controlled.

## 3.2 Controlled Investigation Is Explicitly Added

Admin does not receive permanent "view everything" authority.

The investigation lifecycle is:

**Request → Authorization → Minimum Required Data → Inspection → Audit Log**

This applies whenever deeper inspection of protected/private information is necessary.

## 3.3 Admin Project View Is Expanded

Admin can open the same **Project Instance information structure** available to a Mentor, but in a platform-monitoring/read-oriented mode.

Admin does not become the project's Mentor.

## 3.4 AI Observatory Is Full-Scope

The final AI Observatory contains:

- AI Usage
- Agent Executions
- AI Traces
- AI Quality

This is required because GrowFlow is a serious agentic system rather than a simple chatbot.

## 3.5 Account Management Remains Controlled

Admin can:

- View
- Activate
- Deactivate
- Suspend
- Review

Admin cannot impersonate users or operate as them.

---

# 4. Shared Application Foundation

The Admin application inherits the common shell defined in Part 5A.

## 4.1 Layout

The application uses:

- Fixed Top Navigation
- Persistent Left Navigation
- Independently scrolling Main Content
- Collapsible icon-only Left Navigation
- Scrollable main navigation list
- Fixed Profile + Settings area at bottom of Left Navigation
- Mobile drawer behavior
- No unnecessary nested scrollbars

## 4.2 Top Navigation

Admin Top Navigation contains:

- Global Search
- Notifications
- Share Current View

The Share action simply copies the current authorized page/view URL.

The URL itself never grants access.

Authorization is always enforced by the backend.

## 4.3 Admin Route Security

The Admin route is intentionally not exposed as a normal public navigation destination.

However:

> A hidden route is not a security mechanism.

Admin security requires:

- authenticated session
- ADMIN role
- backend authorization
- protected API endpoints
- server-side authorization checks
- audit logging for sensitive actions
- appropriate session/token security

---

# 5. Final Admin Navigation

The Admin Left Navigation is:

1. **Overview**
2. **Mentors**
3. **Students**
4. **Groups**
5. **Projects**
6. **AI Observatory**
   - AI Usage
   - Agent Executions
   - AI Traces
   - AI Quality
7. **Cost & Usage**
8. **System Health**
9. **Documents & RAG**
10. **Security & Audit**
11. **Platform Analytics**
12. **Profile**
13. **Settings**

The Admin navigation is platform-oriented rather than project-execution-oriented.

---

# 6. Admin Overview

## 6.1 Primary Question

The Admin Overview answers:

> **"Is the platform operating correctly, and is anything requiring intervention?"**

## 6.2 Priority Order

The page is deliberately ordered:

1. **Critical Alerts**
2. **System Health**
3. **AI / Infrastructure**
4. **Platform Statistics**
5. **Recent Activity**

This prevents the dashboard from becoming a collection of decorative statistics.

---

# 7. Critical Alerts

The Overview surfaces actionable platform alerts.

Possible categories:

- AI provider failure spike
- AI rate-limit pressure
- elevated AI latency
- database latency
- database errors
- storage problems
- RAG indexing failures
- embedding failures
- vector retrieval failures
- OAuth failures
- GitHub integration failures
- worker/queue failures
- authentication/security anomalies
- unusual API error rates
- external integration degradation

Every alert should provide:

- severity
- category
- timestamp
- affected subsystem
- short explanation
- current status
- recommended administrative action where appropriate

---

# 8. System Health Summary

The Admin sees health for major platform components.

## Components

- FastAPI/backend
- PostgreSQL/Supabase
- AI gateway
- OpenRouter/provider connectivity
- model providers
- RAG pipeline
- vector store
- object/file storage
- background workers
- task queues
- GitHub integration
- Google OAuth
- GitHub OAuth
- external APIs

## Health Information

Where applicable:

- status
- latency
- request count
- error rate
- recent failures
- uptime/availability information
- queue/backlog state
- last successful operation
- last failure

---

# 9. AI / Infrastructure Summary

The Overview highlights:

- AI requests
- current AI failures
- AI latency
- token usage
- active provider/key-pool health
- agent failures
- regeneration/retry activity
- RAG health
- document generation failures

This section provides an immediate operational picture before the Admin enters the full AI Observatory.

---

# 10. Platform Statistics

Core statistics include:

- total mentors
- active/inactive mentors
- total students
- active/inactive students
- total groups
- active groups
- total project definitions
- total student project instances
- active projects
- completed projects
- at-risk projects
- AI requests
- stored documents/files
- indexed documents
- GitHub-connected projects

Statistics are informational and must not become substitutes for actionable health information.

---

# 11. Recent Activity

The Overview shows relevant platform activity such as:

- account events
- group creation
- project creation
- project assignment
- blueprint generation
- agent execution
- major AI failures
- security events
- RAG indexing events
- administrative actions
- important system events

Sensitive content is not displayed merely because an event exists.

---

# 12. Mentors

The Mentor section provides a platform-level directory and monitoring view.

## 12.1 Mentor Directory

Admin can:

- search mentors
- filter mentors
- sort mentors
- view account status
- view group relationships
- view student/project associations
- view activity metadata
- review platform usage

## 12.2 Mentor Detail

Mentor detail can include:

- identity/basic account information
- account status
- groups
- student counts
- project counts
- activity
- AI usage
- recent platform events
- relevant alerts

Admin is monitoring the mentor relationship, not acting as the mentor.

---

# 13. Students

## 13.1 Student Directory

Admin can:

- search
- filter
- sort
- view account status
- view group relationship
- view project relationships
- view platform activity metadata

## 13.2 Student Detail

The Admin can see platform-level information such as:

- identity/basic account information
- account status
- group
- mentor relationship
- project count
- selected/current project
- project status
- activity metadata
- relevant alerts
- AI usage metadata

Basic student/project information is available to Admin without requiring a private-content investigation.

Deeper protected content remains governed by the investigation workflow.

---

# 14. Groups

## 14.1 Group Directory

Admin can inspect:

- group name
- group status
- mentor
- student count
- project count
- active projects
- at-risk projects
- recent activity

## 14.2 Group Detail

Group detail can include:

- mentor relationship
- students
- project definitions
- project instances
- group activity
- group-level health
- AI usage metadata
- relevant alerts

Admin does not perform normal mentor operations inside the group.

---

# 15. Projects

Admin uses the same conceptual distinction established for Mentor:

### Project Definitions

Reusable mentor-created project definitions/templates.

### Student Project Instances

Independent project instances created for individual students.

Admin can inspect both types.

---

# 16. Admin Project Instance View

Admin can open a Student Project Instance using the same information structure as Mentor, including:

- Project Overview
- Project Profile
- Blueprint
- Tasks
- Milestones
- Risks
- Documents
- GitHub monitoring
- Activity
- AI Mentor-related metadata where authorized

However, the Admin view is:

> **Read-oriented + platform-monitoring-oriented**

Admin does not:

- complete tasks
- change student progress
- edit milestones
- rewrite roadmaps
- manage GitHub
- act as Mentor
- directly operate the project

---

# 17. Project Definition Monitoring

Admin can inspect:

- definition metadata
- owning mentor
- assignment count
- associated student instances
- creation/update activity
- usage statistics

Admin does not become the owner of the definition.

---

# 18. AI Observatory

The AI Observatory is a first-class operational subsystem.

It contains four areas:

1. **AI Usage**
2. **Agent Executions**
3. **AI Traces**
4. **AI Quality**

---

# 19. AI Usage

Admin can inspect:

- total AI requests
- requests by hour/day
- requests by user
- requests by mentor
- requests by student
- requests by project
- requests by agent
- requests by model
- requests by provider
- token usage
- average latency
- failure rate
- retries
- regeneration frequency

The objective is operational visibility rather than surveillance of private conversation content.

---

# 20. Agent Executions

Every meaningful agent execution should be observable.

Metrics include:

- execution count
- agent
- project
- user
- start time
- duration
- status
- success/failure
- retries
- model/provider
- token usage
- error category
- regeneration trigger where applicable

This is particularly important for the 12-agent architecture.

---

# 21. AI Traces

AI traces provide execution-level observability.

A trace may contain:

- execution ID
- user/project context
- timestamp
- orchestrator execution
- agent sequence
- dependencies
- agent status
- input/output metadata
- validation result
- retries
- model/provider
- token counts
- latency
- errors
- regeneration events

Detailed model tracing should integrate with **LangSmith** where applicable.

Raw private prompt/content inspection is not automatically exposed to every Admin view.

---

# 22. AI Quality

AI quality monitoring covers:

- blueprint generation success/failure
- structured-output validation failures
- QA/Judge results
- targeted regeneration frequency
- full regeneration frequency
- agent disagreement
- repeated failures
- user feedback
- ratings
- reported hallucinations
- quality warnings
- invalid/incomplete generated documentation
- agent-level quality patterns

The goal is to answer:

> **"Is GrowFlow's agentic system producing reliable outputs?"**

---

# 23. Cost & Usage

The Cost & Usage area tracks operational consumption.

Views include:

- daily usage
- weekly usage
- monthly usage
- token consumption
- model usage
- provider usage
- agent usage
- project usage
- student usage
- mentor usage

Where cost data is available, show:

- estimated cost
- cost by model
- cost by provider
- cost by agent
- cost by project
- cost trend

---

# 24. API Key Pool Monitoring

GrowFlow uses a five-key AI API pool for resilience and rate-limit/error handling.

Admin may see metadata such as:

- key identifier/alias
- provider
- status
- request count
- failure count
- rate-limit events
- last successful request
- last failure
- current health

Admin must **never see the actual API key secrets**.

The key pool is an infrastructure-resilience mechanism, not a mechanism for bypassing provider policies or limits.

---

# 25. System Health

System Health provides deeper operational diagnostics than the Overview.

Subsystems:

- API
- database
- storage
- workers
- queues
- AI gateway
- providers
- RAG
- vector store
- embeddings
- document processing
- GitHub
- OAuth
- external APIs

For each subsystem, Admin can inspect appropriate:

- health
- latency
- throughput
- failures
- recent incidents
- backlog
- dependency status

---

# 26. Documents & RAG

This section provides operational monitoring for the document and RAG system.

## Document Monitoring

Track:

- uploaded documents
- generated documents
- processing status
- parsing failures
- generation failures
- processing latency
- document counts
- file/storage metadata

## RAG Monitoring

Track:

- indexed document count
- indexing failures
- parsing failures
- chunking failures
- embedding failures
- retrieval failures
- retrieval latency
- vector-store health
- queue/backlog
- knowledge-base size

Metadata is the default administrative view.

Document contents are not automatically exposed globally.

---

# 27. Document Generation Monitoring

Because GrowFlow generates multiple structured project documents, Admin can monitor:

- generation attempts
- successful generations
- failed generations
- retries
- regeneration frequency
- generation latency
- QA failures
- affected agent
- affected project
- failure categories

This allows the platform team to distinguish between application failures and AI-generation failures.

---

# 28. Security & Audit

Security & Audit is append-oriented from the application perspective.

Admin can review events such as:

- login/security events
- authorization failures
- role changes
- account status changes
- sensitive administrative actions
- investigation requests
- investigation approvals
- investigation access
- security alerts
- OAuth events
- integration authorization events
- AI/tool authorization failures

Audit records should preserve enough context to establish:

**who → did what → to what → when → why/authorization context → result**

Audit records should not be casually editable or deleted through normal Admin UI.

---

# 29. Account Management

Admin account actions are intentionally limited to:

### View
Inspect account information and authorized platform metadata.

### Activate
Restore an inactive account where permitted.

### Deactivate
Disable account access without deleting historical records.

### Suspend
Temporarily block account access for a security, abuse, or operational reason.

### Review
Open the account's platform-level history and relevant audit information.

---

# 30. Explicitly Prohibited Account Action

Admin does **not** have:

- user impersonation
- "login as user"
- operation as a student
- operation as a mentor
- bypassing role boundaries

This keeps auditability and accountability clear.

---

# 31. Controlled Investigation

Some legitimate administrative cases require deeper inspection.

Examples may include:

- security investigation
- serious platform incident
- suspected authorization failure
- data-integrity investigation
- abuse investigation
- support escalation requiring protected information

The Admin must not automatically receive permanent unrestricted access.

The lifecycle is:

## Step 1 — Request

Admin identifies the reason for deeper inspection.

## Step 2 — Authorization

The system validates that the Admin and investigation type are authorized.

## Step 3 — Minimum Required Data

Only the smallest relevant scope is exposed.

Examples:

- one student
- one project
- one document
- one interaction
- one time window
- one incident

## Step 4 — Inspection

Authorized information becomes temporarily available for the investigation.

## Step 5 — Audit Log

The system records:

- requesting Admin
- reason
- authorization
- scope
- accessed resource
- timestamp
- result/action

This creates accountability without blocking legitimate platform administration.

---

# 32. Privacy Boundary

The default privacy model is:

> **Metadata-first, controlled content inspection.**

Admin can access platform-level operational information needed for governance.

Admin does not automatically receive unrestricted access to:

- private AI conversations
- private mentor/student communication
- arbitrary project files
- arbitrary document contents
- unrelated RAG content

When deeper access is legitimately required, it must pass through the controlled investigation workflow.

---

# 33. Admin AI

Admin AI is a dedicated platform intelligence layer.

It follows:

**Observe → Analyze → Explain → Recommend**

It is not simply a chatbot attached to the Admin dashboard.

---

# 34. Admin AI — Default Capabilities

Admin AI can retrieve and explain authorized basic information across the platform.

Examples:

### Platform

- "How many active students are there?"
- "How many mentors are currently active?"
- "How many projects are in progress?"

### Groups

- "Which groups currently have the most at-risk projects?"
- "Who mentors Group X?"
- "How many students are in this group?"

### Students

- "What group is this student in?"
- "How many projects does this student have?"
- "What is the current status of their active project?"

### Mentors

- "How many students does this mentor currently supervise?"
- "Which groups belong to this mentor?"

### Projects

- "What projects are currently at risk?"
- "Which projects have the most blocked tasks?"
- "Which project instances are overdue?"

### AI

- "Which agent has the highest failure rate?"
- "How many blueprint generations failed today?"
- "Which model is producing the most retries?"

### Infrastructure

- "Is the AI gateway healthy?"
- "Are RAG indexing failures increasing?"
- "Which subsystem currently has elevated latency?"

These are examples of authorized operational retrieval, not a fixed command list.

---

# 35. Admin AI — Investigation Boundary

Admin AI may detect that a deeper investigation could be useful.

It must not silently bypass the privacy boundary.

For example:

> "There is an unusual project failure pattern. A deeper inspection of the affected project's protected document content may help determine the cause."

The system should then require the appropriate investigation authorization rather than exposing protected content automatically.

---

# 36. Admin AI Data Sources

Admin AI may use:

### Structured Platform Data

- users
- roles
- groups
- projects
- project instances
- tasks
- milestones
- risks
- progress
- health
- AI usage
- agent executions
- system health
- audit metadata

### RAG / Documents

Only where the Admin is authorized to access the relevant content.

### GitHub

Only through the authorized GitHub integration and monitoring layer.

### AI Observability

- LangSmith traces
- execution metadata
- validation results
- quality metrics

### Infrastructure Metrics

- API
- DB
- queues
- storage
- providers
- vector infrastructure

### LLM Reasoning

Used for:

- correlation
- explanation
- anomaly interpretation
- recommendations
- operational summaries

---

# 37. Admin AI Authorization

Admin AI must never receive unrestricted database access.

The preferred architecture is:

**Admin AI → Authorized Tool Layer → Scoped Data → LLM Reasoning**

Each tool enforces:

- ADMIN role
- resource scope
- privacy rules
- investigation authorization where required
- allowed fields
- audit requirements

The LLM itself does not decide whether it is allowed to retrieve private information.

---

# 38. Admin AI Actions

Admin AI is primarily:

- Observe
- Analyze
- Explain
- Recommend

It should not autonomously perform destructive or high-impact administrative actions.

Examples of recommendations:

- investigate provider failure
- review repeated agent failures
- inspect RAG indexing backlog
- review account security events
- examine a project with unusual failure patterns

Administrative state-changing actions remain explicit and controlled.

---

# 39. Admin Search

Admin Global Search can search across authorized platform entities:

- mentors
- students
- groups
- project definitions
- project instances
- relevant operational records

Search results should expose only fields appropriate to the Admin's normal access level.

Private content is not globally searchable by default.

---

# 40. Notifications

Admin notifications should focus on operational events:

- critical system failures
- AI provider incidents
- elevated error rates
- security alerts
- RAG failures
- storage problems
- OAuth/integration failures
- major agent-quality degradation
- approved investigation events
- important platform alerts

Notifications should be actionable rather than noisy.

---

# 41. Admin Activity Model

The Admin application should distinguish:

### Platform Activity

Events occurring naturally across GrowFlow.

### Administrative Activity

Actions explicitly performed by Admin.

### Investigation Activity

Protected-resource inspection performed under an approved investigation.

This distinction is important for auditability.

---

# 42. Admin Permissions Matrix

| Capability | Admin |
|---|---|
| View platform statistics | Yes |
| View mentors | Yes |
| View students | Yes |
| View groups | Yes |
| View project definitions | Yes |
| View student project instances | Yes |
| Monitor project state | Yes |
| Change student progress | No |
| Complete student tasks | No |
| Edit student roadmap | No |
| Manage GitHub | No |
| Act as Mentor | No |
| Impersonate user | No |
| Monitor AI usage | Yes |
| Monitor agent executions | Yes |
| Inspect AI traces | Yes, subject to privacy |
| Monitor AI quality | Yes |
| Monitor RAG operations | Yes |
| Manage account status | Yes, within defined actions |
| Access private content by default | No |
| Controlled investigation | Yes, when authorized |
| Audit investigation | Yes |
| Use Admin AI | Yes |

---

# 43. Relationship With Student and Mentor Applications

The Admin application must not duplicate their workflows.

## Student

Student owns execution.

## Mentor

Mentor owns supervision.

## Admin

Admin owns platform governance and observability.

Therefore:

- Student changes project execution state.
- Mentor supervises and communicates.
- Admin observes and governs the platform.

This separation prevents role overlap and unnecessary permissions.

---

# 44. Backend Architecture Implications

The Admin frontend must not be trusted to enforce permissions.

Backend enforcement is mandatory.

Suggested authorization chain:

**Request → Authentication → Role Authorization → Resource Scope → Privacy Policy → Tool/API Execution → Audit Where Required**

Admin-specific APIs should be separated logically from Student/Mentor operational APIs.

---

# 45. Auditability Requirements

Every sensitive administrative operation should be traceable.

Minimum audit metadata:

- actor ID
- actor role
- action
- resource type
- resource ID
- timestamp
- authorization context
- investigation ID where applicable
- result
- failure reason where applicable

---

# 46. Read vs Write Boundary

The Admin application is intentionally read-heavy.

### Allowed Writes

- account activation
- account deactivation
- account suspension
- authorized administrative review state where explicitly defined
- investigation request/authorization workflow
- administrative settings within approved scope

### Disallowed Operational Writes

- student task completion
- milestone completion
- project progress manipulation
- project roadmap editing
- GitHub changes
- student project execution
- mentor workflow execution

---

# 47. Performance and UX Principles

Admin pages should prioritize:

- fast operational summaries
- clear severity hierarchy
- searchable data
- filtering
- sorting
- pagination
- drill-down
- traceability
- minimal visual noise

Large datasets should not be loaded into the browser unnecessarily.

Use server-side pagination/filtering where appropriate.

---

# 48. Failure Handling

Admin views must distinguish:

- no data
- loading
- partial data
- service unavailable
- permission denied
- stale data
- query failure

A failed monitoring subsystem must not make the entire Admin application appear healthy.

The UI should clearly indicate when a metric cannot currently be retrieved.

---

# 49. Security Requirements

Admin application security must include:

- strong authentication
- role-based authorization
- backend authorization
- secure session/token handling
- protected admin routes
- least privilege
- privacy boundaries
- audit logging
- investigation authorization
- secret redaction
- API key secret protection
- secure AI tool access
- project/resource isolation

---

# 50. What Admin Explicitly Does Not Become

Admin is **not**:

- a second Mentor dashboard
- a super-student account
- a GitHub administrator
- a project editor
- a task manager
- a roadmap editor
- an unrestricted database browser
- an unrestricted private-chat viewer
- an AI agent with unrestricted tool access
- a user-impersonation mechanism

These exclusions are intentional.

---

# 51. Final Admin Application Structure

```text
ADMIN APPLICATION
│
├── Overview
│   ├── Critical Alerts
│   ├── System Health
│   ├── AI / Infrastructure
│   ├── Platform Statistics
│   └── Recent Activity
│
├── Mentors
│   ├── Directory
│   └── Mentor Detail
│
├── Students
│   ├── Directory
│   └── Student Detail
│
├── Groups
│   ├── Directory
│   └── Group Detail
│
├── Projects
│   ├── Project Definitions
│   └── Student Project Instances
│       └── Project Instance Monitoring View
│
├── AI Observatory
│   ├── AI Usage
│   ├── Agent Executions
│   ├── AI Traces
│   └── AI Quality
│
├── Cost & Usage
│   ├── Usage
│   ├── Tokens
│   ├── Models
│   ├── Providers
│   ├── Agents
│   └── Key Pool Health
│
├── System Health
│   ├── API
│   ├── Database
│   ├── AI Gateway
│   ├── RAG
│   ├── Storage
│   ├── Workers
│   ├── GitHub
│   ├── OAuth
│   └── External Integrations
│
├── Documents & RAG
│   ├── Documents
│   ├── Generation
│   ├── Parsing
│   ├── Chunking
│   ├── Embeddings
│   ├── Retrieval
│   └── Vector Store
│
├── Security & Audit
│   ├── Security Events
│   ├── Admin Actions
│   ├── Investigation Requests
│   └── Investigation Audit
│
├── Platform Analytics
│   ├── Users
│   ├── Groups
│   ├── Projects
│   ├── Engagement
│   ├── Completion
│   └── AI / Platform Trends
│
├── Profile
└── Settings
```

---

# 52. Final Admin AI Architecture

```text
                    ┌─────────────────────┐
                    │      ADMIN AI       │
                    └──────────┬──────────┘
                               │
                    Observe → Analyze
                         → Explain
                         → Recommend
                               │
                 ┌─────────────┴─────────────┐
                 │     AUTHORIZED TOOLS      │
                 └─────────────┬─────────────┘
                               │
       ┌──────────────┬────────┼────────┬──────────────┐
       │              │        │        │              │
       ▼              ▼        ▼        ▼              ▼
 Platform DB     AI Usage   Agents   System Health   RAG Ops
       │              │        │        │              │
       └──────────────┴────────┼────────┴──────────────┘
                               │
                         Privacy Layer
                               │
                  ┌────────────┴────────────┐
                  │                         │
            Basic Platform Info       Protected Data
                  │                         │
              Default Access       Investigation Required
                                            │
                                   Request → Authorization
                                            ↓
                                     Minimum Data
                                            ↓
                                        Inspection
                                            ↓
                                       Audit Log
```

---

# 53. Final Decision Summary

The following decisions are now frozen for Part 5D:

| Decision | Final |
|---|---|
| Admin AI | **Yes** |
| Admin AI basic cross-platform information | **Yes** |
| Admin AI operational intelligence | **Yes** |
| Controlled Investigation | **Yes** |
| Default privacy model | **Metadata-first** |
| Investigation lifecycle | **Request → Authorization → Minimum Data → Inspection → Audit** |
| Overview priority | **Critical Alerts → System Health → AI/Infrastructure → Statistics → Recent Activity** |
| Account management | **View → Activate → Deactivate → Suspend → Review** |
| User impersonation | **No** |
| Admin project instance view | **Yes, read/monitor oriented** |
| AI Observatory | **AI Usage + Agent Executions + AI Traces + AI Quality** |
| Project execution control | **No** |
| GitHub management | **No** |
| Unrestricted private content | **No** |
| Admin role | **Govern + Observe + Analyze + Investigate + Controlled Intervene** |

---

# 54. Part 5D Freeze Statement

**Part 5D — Admin Application Architecture is FINAL and FROZEN.**

The Admin application now provides:

> **Platform-wide governance + operational observability + cross-platform basic information + serious agentic-system observability + controlled investigation + AI-powered platform intelligence.**

It deliberately avoids becoming an unrestricted super-user interface.

The resulting role boundary is:

> **Student = Build**  
> **Mentor = Supervise**  
> **Admin = Govern**

This specification should be treated as the authoritative Admin application architecture for subsequent GrowFlow planning and implementation unless a future explicitly approved change is introduced.
