# GrowFlow — Admin Side Specification

## Finalized Version

**Project:** GrowFlow  
**Module:** Admin Side  
**Status:** Approved / Frozen  
**Last Updated:** September 10, 2026

---

# 1. Admin Side Purpose

The Admin side is the platform-wide governance and observability layer of GrowFlow.

The core distinction is:

> **Mentor manages students and projects. Student manages and executes their project. Admin manages, observes, governs, and monitors the entire GrowFlow platform.**

Admin should not become a "super-mentor" who manually manages student projects.

The Admin side focuses on:

1. Platform monitoring
2. User and access monitoring
3. Project monitoring
4. AI observability
5. Agent monitoring
6. Cost and usage monitoring
7. System health
8. Security and audit
9. Platform analytics
10. Controlled administrative intervention

---

# 2. Admin Overview Dashboard

The Admin Overview is the central platform control panel.

## Platform Statistics

- Total mentors
- Active mentors
- Inactive mentors
- Total students
- Active students
- Total groups
- Active groups
- Total projects
- Active projects
- Completed projects
- Projects at risk
- Total AI conversations
- Total AI requests
- Total generated documents
- Total files stored
- GitHub-connected projects

## Platform Health

- System health
- API health
- Database health
- AI service health
- RAG service health
- GitHub integration health
- Authentication/OAuth health
- Storage usage
- Error rate

## Quick Alerts

Examples:

- AI error rate increased
- Project risk levels increased
- AI usage exceeded expected threshold
- Database latency elevated
- Storage approaching capacity
- External API rate limits reached

The Admin should be able to identify important platform problems without navigating through every section.

---

# 3. Mentor Monitoring

Admin can monitor all mentors across the platform.

## Mentor List

The mentor overview can show:

- Mentor
- Groups
- Students
- Projects
- Active students
- At-risk students
- AI usage
- Last activity
- Account status

## Mentor Capabilities

Admin can:

- Search mentors
- Filter mentors
- Sort mentors
- View mentor profile
- View groups created by mentor
- View students associated with mentor
- View projects associated with mentor
- View mentor activity
- View mentor AI usage
- View mentor-related system events

## Mentor Detail

```text
Mentor
 |
 +-- Profile
 +-- Groups
 |    +-- Students
 |    +-- Projects
 |
 +-- Activity
 +-- AI Usage
 +-- Notifications
 +-- Account Status
```

Admin visibility does not automatically mean unrestricted modification authority.

---

# 4. Group Monitoring

Admin can monitor every group across GrowFlow.

## Group Information

- Group name
- Group ID
- Mentor
- Number of students
- Active students
- Projects
- Average progress
- At-risk students
- Group activity
- Last activity

Admin should be able to navigate:

```text
Admin
  |
  v
Mentor
  |
  v
Group
  |
  v
Students
  |
  v
Projects
```

This gives Admin a complete platform-wide organizational view.

---

# 5. Student Monitoring

Admin has a global student directory.

## Student Information

- Student name
- Student ID
- Mentor
- Group
- Projects
- Project status
- Progress
- Health
- Last activity
- GitHub connection
- AI usage
- Account status

## Student Capabilities

Admin can:

- Search students
- Filter students
- Sort students
- View student profile
- View groups
- View projects
- View activity
- View usage
- Review account status

The default philosophy is:

> **Observe first; intervene only when administrative intervention is genuinely required.**

---

# 6. Project Monitoring

Admin gets a platform-wide view of projects.

## Project Information

- Project name
- Student
- Mentor
- Group
- Project type
- Complexity
- Current phase
- Progress
- Health
- Deadline
- Risk level
- Last activity
- Blueprint status
- Documentation status
- GitHub activity

## Global Project Filters

### Project Status

- Planned
- Active
- Completed
- Archived

### Health

- Healthy
- Warning
- At Risk

### Phase

- Documentation
- Planning
- Implementation
- Testing
- Deployment
- Completed

Admin can answer:

> What is happening across the entire GrowFlow platform?

---

# 7. AI Behaviour Monitoring

AI observability is a core Admin capability because GrowFlow is an agentic AI system.

Admin should not only see how many AI requests occurred.

Admin should be able to understand:

> **How the AI system is behaving.**

## AI Usage Metrics

- Total AI requests
- Requests per day
- Requests per hour
- Requests by user
- Requests by mentor
- Requests by student
- Requests by project
- Requests by agent
- Average response time
- Input token usage
- Output token usage
- Failed requests
- Retry rate
- Model usage
- Provider usage

---

# 8. Agent Monitoring

Once the final agent architecture is established, Admin should have an Agent Observatory.

Potential agents include:

```text
Agents
 |
 +-- Idea Agent
 +-- Scope Agent
 +-- Technology Agent
 +-- Timeline Agent
 +-- Risk Agent
 +-- Documentation Agent
 +-- QA/Judge Agent
```

The exact agent list is determined later during the Agent Architecture phase.

## Agent Metrics

Admin can monitor:

- Agent executions
- Success rate
- Failure rate
- Average execution time
- Retry count
- Token usage
- Model used
- Errors
- Recent executions

Example:

```text
Risk Agent
-------------------------
Executions:       1,248
Success Rate:     98.1%
Failures:         24
Avg Duration:     4.8 sec
Avg Tokens:       2,431
```

---

# 9. AI Trace / Execution Monitoring

For complex AI workflows, Admin should be able to inspect individual executions.

Example:

```text
Blueprint Generation
        |
        +-- Idea Analysis .............. OK
        +-- Scope Analysis ............. OK
        +-- Technology Analysis ........ OK
        +-- Feature Analysis ........... OK
        +-- MVP Analysis ............... OK
        +-- Duration Analysis .......... FAILED
        +-- Risk Analysis .............. NOT STARTED
```

Admin can see:

- Execution ID
- User/project
- Start time
- Completion time
- Agents executed
- Agent execution order
- Status
- Errors
- Retry attempts
- Model/provider
- Token usage
- Latency

This provides the foundation for AI observability tools such as LangSmith.

---

# 10. AI Quality Monitoring

Infrastructure success does not necessarily mean AI quality is good.

Admin should also monitor whether AI outputs are producing useful results.

## Potential Quality Metrics

- Blueprint generation success
- Failed generations
- QA/Judge scores
- Validation failures
- Structured-output failures
- Agent disagreement
- Retry frequency
- User regeneration frequency
- AI feedback/ratings
- Hallucination/error reports

Example:

```text
Technology Agent
-------------------------
Executions:       2,431
Success:          98.7%
Validation:       97.2%
Avg QA Score:     87/100
Regenerations:    4.8%
```

---

# 11. Cost & Usage Monitoring

Cost monitoring is a core Admin responsibility because GrowFlow depends on external AI/API services.

## Overall Cost

- Total AI cost
- Daily cost
- Weekly cost
- Monthly cost
- Cost per user
- Cost per project
- Cost per agent
- Cost per model
- Cost per provider

Example:

```text
AI COST

Today:              $4.82
This Week:         $28.43
This Month:       $117.64

Highest Cost:
Blueprint Generation

Highest Agent Cost:
Documentation Agent
```

The exact cost calculation will depend on the selected providers/models and their pricing.

---

# 12. API Key Pool Monitoring

GrowFlow may use multiple API keys for resilience and rate-limit-aware rotation.

Admin should monitor the operational status of the key pool.

Example:

```text
API Key Pool
 |
 +-- Key 1 -> Healthy
 +-- Key 2 -> Healthy
 +-- Key 3 -> Rate Limited
 +-- Key 4 -> Healthy
 +-- Key 5 -> Error
```

Admin can see:

- Key status
- Request count
- Error count
- Rate-limit events
- Provider failures
- Last successful request
- Usage distribution

## Security Requirement

**The actual API keys must never be displayed in the Admin UI.**

Only safe operational metadata and status are exposed.

Multiple keys are for resilience and controlled rate-limit handling, not for bypassing provider restrictions.

---

# 13. System Health

Admin has a technical system-health dashboard.

## Infrastructure

- Backend status
- Database status
- Storage status
- Vector store status
- Queue/background workers
- AI gateway
- External API integrations

## Performance

- API latency
- Error rate
- Request rate
- Database latency
- AI latency
- RAG latency
- Document generation latency

Example:

```text
SYSTEM HEALTH

API             Healthy
Database        Healthy
RAG             Healthy
AI Gateway      Degraded
GitHub API      Healthy
Storage         Healthy
Workers         Healthy
```

---

# 14. RAG Monitoring

GrowFlow contains project-specific workspaces and RAG.

Admin should monitor the RAG pipeline at a system level.

## RAG Metrics

- Documents indexed
- Documents failed to index
- Embedding failures
- Retrieval failures
- Vector-store status
- RAG latency
- Project knowledge-base size
- Processing queue
- Parsing failures

The default Admin view should expose **metadata and operational information**, not the full content of private student documents.

---

# 15. Document Generation Monitoring

The Blueprint system is a multi-document generation workflow, so Admin should be able to monitor it.

## Generation States

```text
Blueprint Generation
 |
 +-- Successful
 +-- Failed
 +-- Partial
 +-- Retrying
 +-- Regenerated
```

## Metrics

- Generation attempts
- Successful documents
- Failed documents
- Retry count
- Recovery success
- Regeneration frequency
- Average generation time
- Agent responsible for failure
- Most frequently failing document type

Example:

> `technology_stack.md` has failed generation 18 times this week.

This becomes an actionable platform-level signal.

---

# 16. Security & Audit Logs

Security and auditability are core Admin requirements.

Admin should have an audit trail for important platform events.

## Examples

- User registered
- User logged in
- OAuth connection
- Group created
- Student joined group
- Project created
- Project assigned
- Blueprint generated
- Document regenerated
- AI execution failed
- Permission denied
- Account status changed
- Admin action performed

Example:

```text
14:32:11
Student #1024
Generated Blueprint
Project: AI Study Assistant

14:34:07
Risk Agent
Execution failed

14:35:12
System
Blueprint generation retry started
```

Audit logs should be append-only from the application perspective.

---

# 17. Account & Access Management

Admin can perform legitimate platform-level account management.

## Potential Actions

- View account
- Activate/deactivate account
- Suspend account
- Review role
- Review authentication status
- Review group relationships

## Roles

```text
ADMIN
MENTOR
STUDENT
```

Admin should not receive arbitrary authority to manipulate project execution simply because they have administrative access.

---

# 18. Platform Analytics

Admin should have higher-level platform analytics.

## User Analytics

- New students
- New mentors
- Active users
- Activity trends
- Retention/activity indicators

## Project Analytics

- Projects created
- Projects completed
- Average completion time
- Average progress
- Common project types
- Common technologies
- Common project risks

## AI Analytics

- AI requests
- Most-used agents
- Most-used AI features
- Failure rates
- Costs
- Quality scores
- Regeneration rates

---

# 19. Admin Notifications & Alerts

Admin should receive alerts for important platform events.

## Infrastructure Alerts

> Database error rate increased.

## AI Alerts

> Blueprint generation failure rate exceeded threshold.

## Cost Alerts

> AI spending exceeded the configured daily threshold.

## Security Alerts

> Unusual authentication failures detected.

## Storage Alerts

> Workspace storage reached 80%.

## API Alerts

> Provider rate limits are being reached frequently.

The exact thresholds should be configurable during the technical/admin configuration phase.

---

# 20. Global Admin Search

A global search is useful for platform administration.

The Admin can search by:

- Student name
- Student ID
- Mentor name
- Group ID
- Group name
- Project name
- Project ID
- Execution ID
- Relevant platform identifiers

Example:

```text
Search: Rahul

Results
 |
 +-- Student
 +-- Mentor relationship
 +-- Group
 +-- Projects
 +-- Activity
 +-- AI executions
```

This allows rapid investigation without manually navigating through every section.

---

# 21. Privacy & Administrative Investigation Model

This is a finalized architectural decision.

## Default: Metadata-Only Visibility

Admin normally sees:

- Usage metadata
- Counts
- Status
- Performance metrics
- Project metadata
- AI execution metadata
- Error information
- Audit events
- Operational health

Admin does **not** automatically receive unrestricted access to:

- Full private student conversations
- Full student document content
- Private workspace files
- Sensitive project material

## Controlled Administrative Investigation

When a legitimate administrative investigation is required, authorized Admin access may allow deeper inspection.

Examples:

- Investigating an AI failure
- Investigating a security incident
- Investigating abuse
- Investigating a data-integrity issue
- Diagnosing a serious platform error

The deeper-access workflow should be:

```text
Administrative Need
        |
        v
Authorized Investigation
        |
        v
Controlled Access
        |
        v
Required Data Only
        |
        v
Audit Logged
```

This means:

> **A = default metadata-only visibility**

and

> **B = controlled, authorized investigation access**

is the approved privacy model.

Full unrestricted visibility is explicitly not the default.

---

# 22. What Admin Should NOT Do

Admin should not become another project-management role.

The following are excluded from normal Admin responsibilities:

- Manually changing student progress
- Completing student tasks
- Editing student milestones
- Writing student roadmaps
- Managing GitHub repositories
- Acting as the student's mentor
- Manually modifying AI-generated project plans as a normal workflow
- Editing student project documents as a normal workflow
- Unrestricted access to private student content
- Bypassing application authorization
- Bypassing group/project data isolation

The Admin principle is:

> **Observe, govern, investigate, configure, and intervene only when necessary.**

---

# 23. Recommended Admin V1 Structure

```text
ADMIN
|
+-- Overview
|   +-- Platform statistics
|   +-- System health
|   +-- Alerts
|   +-- Key metrics
|
+-- Mentors
|   +-- All mentors
|   +-- Groups
|   +-- Students
|   +-- Projects
|   +-- Activity
|
+-- Students
|   +-- All students
|   +-- Groups
|   +-- Projects
|   +-- Activity
|   +-- Usage
|
+-- Groups
|   +-- All groups
|   +-- Mentors
|   +-- Students
|   +-- Project status
|
+-- Projects
|   +-- All projects
|   +-- Progress
|   +-- Health
|   +-- Risks
|   +-- Phases
|   +-- Activity
|
+-- AI Observatory
|   +-- AI usage
|   +-- Agent executions
|   +-- AI quality
|   +-- Failures
|   +-- Retries
|   +-- Traces
|
+-- Cost & Usage
|   +-- AI costs
|   +-- API usage
|   +-- Model usage
|   +-- Provider usage
|   +-- API key health
|
+-- System Health
|   +-- API
|   +-- Database
|   +-- RAG
|   +-- Storage
|   +-- Workers
|   +-- Integrations
|
+-- Documents & RAG
|   +-- Generation status
|   +-- Failures
|   +-- Indexing
|   +-- Processing
|
+-- Security & Audit
|   +-- Audit logs
|   +-- Authentication events
|   +-- Authorization failures
|   +-- Admin actions
|
+-- Platform Analytics
    +-- User analytics
    +-- Project analytics
    +-- AI analytics
    +-- Usage trends
```

---

# 24. Complete Admin Architecture

```text
                              ADMIN
                                |
                                v
                       ADMIN DASHBOARD
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
     PEOPLE                 PROJECTS                  AI
        |                       |                       |
   +----+----+             +----+----+          +------+------+
   |         |             |         |          |             |
Mentors   Students       Groups   Projects    Agents       Quality
   |         |             |         |          |             |
   +----+----+             +----+----+          +------+------+
        |                       |                       |
        +-----------------------+-----------------------+
                                |
                                v
                         USAGE & COST
                                |
                    +-----------+-----------+
                    |           |           |
                    v           v           v
                 Models     Providers    API Keys
                                |
                                v
                         SYSTEM HEALTH
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
            API              Database             RAG
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                       SECURITY & AUDIT
                                |
                                v
                  CONTROLLED INVESTIGATION
```

---

# 25. Admin Responsibilities

The Admin role is ultimately responsible for four major responsibilities.

## 25.1 Observe

> What is happening across GrowFlow?

Monitor:

- Users
- Groups
- Projects
- AI
- Agents
- Costs
- Infrastructure

## 25.2 Analyze

> How is GrowFlow performing?

Analyze:

- Usage
- Project trends
- AI quality
- Agent performance
- Cost
- Reliability
- System health

## 25.3 Govern

> Is the platform operating securely and correctly?

Govern:

- Access
- Roles
- Security
- Audit
- Privacy
- Platform rules
- Administrative controls

## 25.4 Intervene

> Is there a genuine administrative problem requiring action?

Intervene only when necessary and within controlled authorization boundaries.

---

# 26. Final Admin V1 Feature Boundary

| Area | Decision |
|---|---|
| Admin authentication | Core |
| Role-based access | Core |
| Platform overview | Core |
| Mentor monitoring | Core |
| Student monitoring | Core |
| Group monitoring | Core |
| Project monitoring | Core |
| Global search | Core |
| AI usage monitoring | Core |
| Agent monitoring | Core |
| AI execution traces | Core |
| AI quality monitoring | Core |
| Cost monitoring | Core |
| API/provider monitoring | Core |
| API key health metadata | Core |
| System health | Core |
| RAG monitoring | Core |
| Document-generation monitoring | Core |
| Security monitoring | Core |
| Audit logs | Core |
| Account management | Core |
| Platform analytics | Core |
| Admin alerts | Core |
| Metadata-only default visibility | Core |
| Controlled investigation access | Core |
| Full unrestricted student-content access | Remove |
| Manual project execution management | Remove |
| Manual student progress manipulation | Remove |
| Full GitHub management | Remove |
| Acting as mentor | Remove |
| Normal document editing | Remove |

---

# 27. Final Admin Concept

```text
                         GROWFLOW
                            |
                            v
                          ADMIN
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
       USERS             PROJECTS              AI
        |                   |                   |
     Mentors             Groups              Agents
     Students             Status             Quality
     Groups               Health             Traces
                          Risks
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
      COST              SYSTEM HEALTH       SECURITY
        |                   |                   |
     AI usage              API               Audit
     Models                DB                Access
     Providers             RAG               Events
     API keys              Storage           Alerts
        |                   |                   |
        +-------------------+-------------------+
                            |
                            v
                  PLATFORM ANALYTICS
                            |
                            v
                  ADMIN INTERVENTION
                            |
                            v
                 CONTROLLED + AUDITED
```

## Core Admin Principle

> **Admin does not build the students' projects. Admin ensures that GrowFlow itself is healthy, secure, observable, cost-controlled, and functioning correctly for every mentor and student.**

The approved privacy model is:

> **Metadata by default + controlled, authorized, audit-logged investigation when deeper access is genuinely required.**
