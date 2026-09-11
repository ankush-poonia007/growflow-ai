# 🌱 GrowFlow — Mentor Side Specification

**Status:** Approved / Frozen for feature discussion  
**Scope:** Mentor-side product functionality, UX structure, communication, monitoring, AI access, and architectural principles.

---

## 1. Mentor-Side Purpose

The mentor acts as a **project supervisor** across one or more groups.

GrowFlow gives the mentor a structured way to:

- Organize students into groups
- Create and maintain project definitions
- Assign projects to students
- Monitor project progress
- Monitor project health and risks
- Track milestones and tasks
- View GitHub activity
- Compare student performance
- Identify students requiring attention
- Communicate with students
- Ask an AI mentor questions about authorized student/project data

### Core hierarchy

```text
MENTOR
  │
  ├── Group A
  │     ├── Student 1
  │     │      └── Independent Project Instance(s)
  │     ├── Student 2
  │     │      └── Independent Project Instance(s)
  │     └── Student 3
  │            └── Independent Project Instance(s)
  │
  ├── Group B
  │     ├── Student 4
  │     └── Student 5
  │
  └── Group C
        └── ...
```

The mentor's primary relationship is:

> **Mentor → Groups → Students → Independent Projects → Roadmaps → Tasks/Milestones → Progress/Health/Risks**

---

# 2. Mentor Feature Specification

| Module | Feature | Status | Final Definition |
|---|---|---|---|
| Authentication | Mentor registration | ✅ Keep | Mentor can create a mentor account. |
| Authentication | Mentor login | ✅ Keep | Secure login with role-based access. |
| Authentication | Google authentication | ✅ Keep | OAuth-based mentor authentication. |
| Authentication | GitHub authentication | ✅ Keep | OAuth-based mentor authentication. |
| Authentication | Password hashing | ✅ Keep | Passwords are securely hashed and never stored as plaintext. |
| Groups | Create group | ⭐ Core | Mentor can create multiple groups. |
| Groups | Generate Group ID | ⭐ Core | Unique shareable join code for students. |
| Groups | Multiple groups | ⭐ Core | One mentor can manage multiple groups. |
| Groups | Student joining | ⭐ Core | Students join through the group join code. |
| Groups | Membership | ⭐ Core | Group membership controls access and visibility. |
| Students | View all students | ⭐ Core | Mentor can see authorized students across groups. |
| Students | View group students | ⭐ Core | Mentor can restrict the view to the selected group. |
| Students | Search | ⭐ Core | Search by student name or student ID. |
| Students | Filter | ⭐ Core | Filter by project/status/health/progress and supported metrics. |
| Students | Sort | ⭐ Core | Sort by supported project and activity metrics. |
| Students | Scope-based search/filter/sort | ⭐ Core | Same query controls operate at mentor-wide and group scope. |
| Students | Student detail | ⭐ Core | Click a student to view detailed project/progress information. |
| Projects | Create mentor project | ⭐ Core | Mentor can create reusable project definitions/templates. |
| Projects | Multiple projects | ⭐ Core | Mentor can maintain multiple project definitions. |
| Projects | Assign project | ⭐ Core | Mentor can assign a project to a student. |
| Projects | Additional assignments | ✅ Keep | A mentor-created project can later be assigned to additional students. |
| Projects | Independent instances | 🔒 Critical | Each student's assigned project has independent state and progress. |
| Group Dashboard | Group overview | ⭐ Core | Aggregate student/project analytics for the selected group. |
| Group Dashboard | Group progress | ✅ Keep | Aggregate progress across group projects. |
| Group Dashboard | Group health | ✅ Keep | Aggregate health view. |
| Group Dashboard | At-risk dashboard | ⭐ Core | Dedicated group-level view for students/projects requiring attention. |
| Group Dashboard | Risk indicators | ⭐ Core | Explain significant risk conditions and reasons. |
| Group Dashboard | Top performers | ✅ Keep | Top 5 performers within the selected group. |
| Global Dashboard | Cross-group overview | ⭐ Core | Aggregate information across all mentor groups. |
| Global Dashboard | Top 5 students | ✅ Keep | Top performers across the mentor's authorized groups. |
| Global Dashboard | Global search/filter/sort | ⭐ Core | Controls operate across all authorized students. |
| Ranking | Student ranking | ✅ Keep | Use transparent deterministic performance metrics. |
| Ranking | Project health | ✅ Keep | One ranking input. |
| Ranking | Progress | ✅ Keep | One ranking input. |
| Ranking | Milestones | ✅ Keep | One ranking input. |
| Ranking | Tasks | ✅ Keep | One ranking input. |
| Ranking | Duration/deadline adherence | ✅ Keep | One ranking input. |
| Ranking | Idea score | ⚠️ Limited | Informational; should not dominate execution ranking. |
| GitHub | Connect GitHub | ✅ Keep | Student connects a repository to a project. |
| GitHub | Commit history | ✅ Keep | Mentor can view connected project's commit activity. |
| GitHub | Commit count | ✅ Keep | Useful project activity metric. |
| GitHub | Recent activity | ⭐ Core | Shows latest meaningful repository activity. |
| AI Mentor | Mentor AI chat | ⭐ Core | Mentor can ask questions about authorized students/projects. |
| AI Mentor | Group-scoped chat | 🔒 Critical | AI chat is bound to the selected group context. |
| AI Mentor | Student questions | ✅ Keep | Ask about an individual student. |
| AI Mentor | Project questions | ✅ Keep | Ask about an individual project. |
| AI Mentor | Group questions | ✅ Keep | Ask aggregate questions about a group. |
| AI Mentor | SQL-based answers | ⭐ Core | Structured questions should use database querying/tools. |
| AI Mentor | AI reasoning | ⭐ Core | Complex analytical questions use AI reasoning over authorized data. |
| Communication | Mentor notes | ⭐ Core | Mentor can send project/help notes to students. |
| Communication | Student sees mentor notes | ⭐ Core | Notes appear in a dedicated student notes area. |
| Communication | Note timestamp | ✅ Keep | Creation date/time is recorded. |
| Communication | Note history | ✅ Keep | Persistent note history. |
| Communication | Student help requests | ⭐ Core | Student can request help from the mentor. |
| Communication | Mentor help section | ⭐ Core | Mentor sees incoming student help requests. |
| Communication | Help timestamp | ✅ Keep | Date/time is recorded. |
| Communication | Help status/history | ⭐ Core | Track requests such as Open → In Progress → Resolved. |
| Notifications | Mentor notifications | ⭐ Core | Important project, risk, and help events. |
| Notifications | At-risk alerts | ⭐ Core | Surface students/projects requiring attention. |
| Notifications | Help notifications | ⭐ Core | Notify mentor about new student help requests. |
| Security | Group data isolation | 🔒 Critical | Mentor can only access authorized group data. |
| Security | Student data isolation | 🔒 Critical | No cross-mentor or unauthorized student leakage. |
| Security | AI context isolation | 🔒 Critical | AI receives only authorized data for the active scope. |

---

# 3. Scope-Based Search, Filter & Sort

Search, filtering, and sorting are a **single shared capability with a variable data scope**.

There are two primary scopes.

### Mentor / Base Scope

The mentor sees all students authorized for that mentor across all groups.

```text
Mentor
 ├── Group A → Students
 ├── Group B → Students
 └── Group C → Students

        ↓

Global Search
Global Filter
Global Sort

        ↓

All authorized students
```

### Group Scope

When the mentor enters a particular group, the same controls operate only on students in that group.

```text
Mentor
   ↓
Selected Group
   ↓
Group Students
   ↓
Search / Filter / Sort
```

### Scope model

| Scope | Data Visible | Operations |
|---|---|---|
| Mentor / Base level | All students authorized for that mentor across all groups | Search + Filter + Sort |
| Group level | Only students belonging to the selected group | Search + Filter + Sort |

### Recommended implementation abstraction

Use one shared query service conceptually similar to:

```text
StudentQueryService
    │
    ├── mentor_id
    ├── group_id (optional)
    ├── search
    ├── filters
    └── sort
```

If `group_id` is supplied:

```text
Results = Students in selected group
```

If `group_id` is not supplied:

```text
Results = All students authorized for mentor
```

This avoids implementing separate global and group search systems.

---

# 4. Mentor Dashboard Structure

GrowFlow uses a **progressive-disclosure model**:

```text
All Authorized Students
          ↓
        Group
          ↓
       Student
          ↓
       Project
          ↓
Detailed Monitoring
```

## 4.1 Mentor Overview

The global mentor dashboard should provide:

- Total groups
- Total students
- Total projects
- Overall project progress
- Overall project health
- Completed projects
- Ongoing projects
- Planned projects
- Top 5 performers
- At-risk overview
- Search/filter/sort controls
- All authorized students table

Conceptual layout:

```text
┌──────────────────────────────────────────────┐
│              MENTOR OVERVIEW                 │
├──────────────────────────────────────────────┤
│ Groups     Students     Projects             │
│  8          126          104                 │
│                                              │
│ Overall Progress       Projects At Risk      │
│ 67%                    12                    │
│                                              │
│ Top 5 Students                              │
│                                              │
│ Search / Filter / Sort                       │
│                                              │
│ All Students Table                           │
└──────────────────────────────────────────────┘
```

## 4.2 Group Dashboard

When a mentor enters a specific group:

```text
┌──────────────────────────────────────────────┐
│ GROUP: B.Tech AI Projects                    │
├──────────────────────────────────────────────┤
│ Students    Projects    Avg Progress         │
│ 32          29           71%                  │
│                                              │
│ 🚨 At Risk: 5                                │
│ ⚠ Needs Attention: 7                         │
│ ✓ On Track: 20                               │
│                                              │
│ Top 5 Students                               │
│                                              │
│ Student Table                                │
└──────────────────────────────────────────────┘
```

The group dashboard should include:

- Group statistics
- Average progress
- Group health
- At-risk students
- Students requiring attention
- Top performers
- Group-scoped search/filter/sort

## 4.3 Student Detail

Selecting a student should expose that student's authorized project information:

```text
Student
   ↓
Project(s)
   ↓
Selected Project
   ├── Health
   ├── Idea Score
   ├── Phase
   ├── Progress
   ├── Tasks
   ├── Milestones
   ├── Risks
   ├── GitHub Activity
   ├── Documents
   ├── AI Activity
   ├── Mentor Notes
   └── Help Requests
```

---

# 5. Student Table

The mentor should have a persistent table of students.

Example:

| Student ID | Name | Project | Phase | Health | Progress | Last Activity |
|---|---|---|---|---:|---:|---|
| GF1021 | Aman | AI RAG Assistant | Implementation | 82 | 67% | 2 hours ago |
| GF1022 | Ravi | E-Commerce | Planning | 71 | 43% | 1 day ago |
| GF1023 | Neha | Chatbot | Testing | 91 | 88% | Today |

### Table behavior

- Alphabetical ordering by default
- Clickable student ID/name
- Search
- Filter
- Sort
- Pagination where required
- Scope-aware data visibility

The same table concept works at:

1. Mentor-wide scope
2. Group scope

---

# 6. At-Risk Dashboard

The at-risk view is a **separate dashboard at group level**.

It should not simply display a red health number. It should explain **why** a project/student is considered at risk.

Example:

| Student | Project | Health | Progress | Risk | Last Activity |
|---|---|---:|---:|---|---|
| Rahul | AI Assistant | 42 | 38% | Deadline | 6 days ago |
| Aman | E-Commerce | 51 | 44% | Inactivity | 4 days ago |
| Priya | RAG App | 57 | 49% | Scope | 2 days ago |

Example explanation:

> **Risk:** Project deadline approaching  
> **Reason:** 4 milestones remain incomplete with 12 days remaining.

Potential risk categories include:

- Scope risk
- Deadline/time risk
- Inactivity risk
- Technology risk
- Task/milestone delay
- AI/project-quality risk
- Deployment risk
- Other project-specific risks

---

# 7. Student Ranking & Performance

Student ranking is retained but must be **transparent and execution-oriented**.

GrowFlow should not use an opaque arbitrary score or complex ML ranking in V1.

### Candidate performance dimensions

| Metric | Role |
|---|---|
| Progress | Core execution metric |
| Milestone completion | Core execution metric |
| Task completion | Core execution metric |
| Consistency/activity | Supporting metric |
| Project health | Supporting metric |
| Deadline adherence | Supporting metric |
| Idea score | Informational; limited ranking influence |

### Important principle

A student with a mediocre idea but excellent execution should not automatically rank below a student with a brilliant idea who has made little progress.

Therefore:

> **Execution should dominate performance ranking; idea quality should be informative rather than decisive.**

The exact weighting/formula will be defined during the technical/metrics phase.

---

# 8. Top 5 Students

The mentor should have:

### Global Top 5

Top five performers across all groups authorized for that mentor.

### Group Top 5

Top five performers within the selected group.

```text
Mentor
 ├── Global Top 5
 │
 └── Selected Group
       └── Group Top 5
```

The ranking must remain explainable.

Example:

```text
Aman — 91/100

Progress          28/30
Milestones        22/25
Tasks             18/20
Consistency         9/10
Health              9/10
Deadline            5/5
────────────────────────
Total               91/100
```

The exact scoring weights are intentionally deferred to the metrics/technical phase.

---

# 9. GitHub Integration Boundary

GitHub is treated as **evidence of project activity**, not as a replacement for GitHub.

## Mentor V1 GitHub visibility

- Connected repository
- Commit count
- Recent commits/activity
- Last meaningful activity
- Lightweight project activity metrics

Example:

```text
Repository: github.com/student/project

Commits this week: 14
Commits this month: 47
Last activity: Today
```

## Explicitly outside Mentor V1

- Full GitHub issue management
- Pull-request management
- Repository editing
- CI/CD management
- Complete GitHub clone

---

# 10. Mentor AI Architecture

The Mentor AI should be a **tool-using assistant**, not a chatbot that blindly receives the entire database.

```text
                    Mentor Question
                           │
                           ↓
                   Mentor AI / Router
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
          SQL/Data     Project Data   RAG/Docs
              │            │            │
              └────────────┼────────────┘
                           ↓
                     AI Reasoning
                           ↓
                         Answer
```

## 10.1 SQL/Data Tool

Use structured querying for questions such as:

> "How many students are in this group?"

> "How many projects are currently in implementation?"

> "Which students completed the most milestones?"

These are database/analytics problems.

## 10.2 Project Data

Use authoritative project state for:

- Project phase
- Task state
- Milestone state
- Project health
- Progress
- Risks
- Deadlines
- Activity

## 10.3 RAG / Documents

Use the RAG layer for document-oriented information where appropriate.

Examples:

> "What does this student's project documentation say about the MVP?"

> "What technology was selected for this project and why?"

## 10.4 AI Reasoning

Complex questions may combine multiple sources.

Example:

> "Why is Aman considered at risk?"

Potentially requires:

```text
Project State
+
Tasks
+
Milestones
+
Risk Information
+
Activity
+
Documents
        ↓
AI Reasoning
        ↓
Explanation
```

### Core principle

> **The Mentor AI should use tools and authorized data sources rather than receiving unrestricted raw database contents.**

---

# 11. Mentor AI Chat Boundary

Mentor AI chat is **group-scoped**.

Example:

```text
Mentor
   ↓
Group A
   ↓
AI Mentor
   ↓
Students in Group A
```

The AI must not accidentally retrieve Group B students while the mentor is operating inside Group A.

At mentor-wide scope:

```text
Mentor
   ↓
Global Mentor Context
   ↓
All authorized groups
   ↓
All authorized students/projects
```

The active scope becomes part of the authorization boundary.

---

# 12. Mentor ↔ Student Communication

GrowFlow has two persistent communication directions.

## 12.1 Mentor → Student: Mentor Notes

The mentor can send a note to a student.

Example:

> "Your current project scope is becoming too large. Please review the MVP before continuing."

The student sees it in a dedicated Notes area.

Each note should contain:

- Sender
- Recipient
- Note content
- Project/group context where applicable
- Creation date
- Creation time
- Read/unread state if implemented
- Persistent history

Conceptual flow:

```text
Mentor
   ↓
Mentor Note
   ↓
Student
   ↓
Student Notes Dashboard
```

## 12.2 Student → Mentor: Help Requests

The student can request help from the mentor.

Example:

> "I'm stuck integrating authentication. Can you help me decide between JWT and session authentication?"

The mentor sees the request in a dedicated **Student Help** section.

Each request should contain:

- Student
- Project
- Request content
- Date
- Time
- Status
- Response/history

Recommended lifecycle:

```text
OPEN
  ↓
IN PROGRESS
  ↓
RESOLVED
```

Conceptual flow:

```text
Student
   ↓
Ask Mentor / Help Request
   ↓
Mentor
   ↓
Student Help Section
```

---

# 13. Mentor Notifications

Mentor notifications should focus on events requiring attention.

Examples:

```text
🚨 Student project became at-risk
⚠ Project deadline approaching
⚠ Student has been inactive
📩 New student help request
✓ Important milestone completed
```

V1 notification categories:

- At-risk alerts
- Student help requests
- Important project events

Notifications should be tied to real events, not decorative UI.

---

# 14. Canonical Project-State Architecture

This is a major architectural decision.

GrowFlow should have **one canonical project state**.

```text
                    CANONICAL PROJECT STATE
                              │
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
         Student UI       Mentor UI        AI Agents
              │               │               │
              └───────────────┼───────────────┘
                              ↓
                       PostgreSQL/Supabase
```

The database is the **source of truth**.

Neither the Mentor dashboard nor the AI should maintain a separate independent version of project progress.

---

# 15. AI Does Not Own Core Project State

AI agents can:

- Analyze
- Recommend
- Summarize
- Generate
- Explain
- Identify possible risks
- Suggest roadmap changes

But deterministic application/database logic should control authoritative state such as:

- Task completion
- Milestone completion
- Project progress calculations
- Group membership
- Authorization
- Core status transitions

Example:

```text
Task 1 ✓
Task 2 ✓
Task 3 ✓
Task 4 ○

        ↓

Task completion calculation

        ↓

Milestone status
```

If all required milestone tasks are complete:

```text
All required tasks = COMPLETE
        ↓
Milestone = COMPLETE
```

This should not depend on an LLM making an arbitrary decision.

---

# 16. Independent Project Instances

A mentor-created project should be treated as a **project definition/template**.

When assigned to multiple students, each student gets an independent project instance.

```text
Mentor Project Definition
"AI Resume Analyzer"
             │
       ┌─────┼─────┐
       ↓     ↓     ↓
   Student A B     C
   Instance  Instance Instance
      1        2       3
```

Each instance can have different:

- Roadmap
- Tasks
- Milestones
- Progress
- Documents
- Chat history
- Risks
- Health
- GitHub repository
- Timeline

This is a critical database/domain distinction.

---

# 17. Data & Security Boundaries

Authorization must exist across every relevant layer.

```text
Mentor
  │
  ├── Authorized Group A
  │     ├── Student 1
  │     └── Student 2
  │
  └── Authorized Group B
        ├── Student 3
        └── Student 4
```

If operating inside Group A:

```text
AI Context
   ↓
Group A
   ↓
Student 1 + Student 2
```

Student 3 and Student 4 must not be accessible through that context.

### Required security boundaries

- API authorization
- Database query authorization
- Group membership validation
- Student/project access validation
- RAG retrieval filtering
- AI tool authorization
- Mentor-wide scope validation
- Group-level scope validation

### Non-negotiable principle

> **AI context must never bypass application authorization.**

---

# 18. Mentor V1 — Final Build Boundary

```text
MENTOR
│
├── Authentication
│   ├── Registration
│   ├── Login
│   ├── Google OAuth
│   ├── GitHub OAuth
│   └── Secure password handling
│
├── Mentor Dashboard
│   ├── Global statistics
│   ├── Overall project health
│   ├── Overall progress
│   ├── Top 5 performers
│   └── At-risk overview
│
├── Groups
│   ├── Create group
│   ├── Generate join code
│   ├── View group
│   ├── Group dashboard
│   └── Group analytics
│
├── Students
│   ├── All students
│   ├── Group students
│   ├── Search
│   ├── Filter
│   ├── Sort
│   └── Student detail
│
├── Projects
│   ├── Create project
│   ├── Project definitions/templates
│   └── Assign project
│
├── Project Monitoring
│   ├── Phase
│   ├── Health
│   ├── Progress
│   ├── Tasks
│   ├── Milestones
│   ├── Risks
│   ├── Documents
│   └── GitHub activity
│
├── At-Risk Dashboard
│   ├── At-risk students
│   ├── Risk categories
│   ├── Risk explanations
│   └── Last activity
│
├── AI Mentor
│   ├── Group questions
│   ├── Student questions
│   ├── Project questions
│   ├── SQL/data tools
│   ├── RAG/document access
│   └── AI reasoning
│
├── Communication
│   ├── Mentor Notes
│   ├── Student Help Requests
│   ├── Responses
│   ├── Timestamps
│   └── Status tracking
│
└── Notifications
    ├── At-risk alerts
    ├── Help requests
    └── Important project events
```

---

# 19. Explicitly Out of Mentor V1

| Feature | Decision | Reason |
|---|---|---|
| Manual manipulation of student progress | ❌ Removed | Mentor observes/intervenes rather than overwriting authoritative progress. |
| Complex ML-based student ranking | ❌ Removed | Deterministic, explainable metrics are sufficient for V1. |
| Full GitHub management | ❌ Removed | GitHub is used primarily for project activity evidence. |
| GitHub issue/PR management | ❌ Removed | Controls scope and implementation time. |
| Repository editing | ❌ Removed | Not part of GrowFlow's core purpose. |
| CI/CD management | ❌ Removed | Outside Mentor V1 scope. |
| Mentor editing student roadmap directly | ❌ Removed | Preserves project ownership and state integrity. |
| Mentor controlling student tasks | ❌ Removed | Student/project workflow owns task state. |
| Opaque AI-generated performance score | ❌ Removed | Performance metrics must be explainable. |
| Unrestricted AI access to database data | ❌ Removed | AI must operate within explicit authorization scope. |

---

# 20. Mentor-Side Architectural Principles

### 1. One source of truth

PostgreSQL/Supabase stores canonical relationship and project state.

### 2. Scope-aware access

Mentor-wide and group-level contexts use the same query abstraction with different authorization scopes.

### 3. Independent project instances

A mentor project/template can be assigned to multiple students, but each student receives an independent project instance.

### 4. AI is a reasoning layer

Agents analyze, recommend, summarize, and interact with tools. Deterministic application logic owns core state transitions.

### 5. Group-scoped Mentor AI

AI context is restricted to the active group or authorized mentor-wide scope.

### 6. Explainability

Rankings and risk indicators must explain how/why they were produced.

### 7. Real implementation only

Every approved UI capability must have a real backend/data path before it is considered complete.

### 8. Progressive disclosure

The mentor should move naturally from:

```text
All Students
    ↓
Group
    ↓
Student
    ↓
Project
    ↓
Detailed Information
```

### 9. Least-privilege AI access

The AI receives only the data required to answer the current question within the current authorized scope.

---

# 21. Mentor-Side End-to-End Flow

```text
                         MENTOR
                           │
                           ↓
                    Create / Login
                           │
                           ↓
                    Mentor Dashboard
                           │
            ┌──────────────┼──────────────┐
            ↓              ↓              ↓
        All Groups      Projects      Notifications
            │
            ↓
      Select Group
            │
            ↓
     Group Dashboard
            │
     ┌──────┼──────┐
     ↓      ↓      ↓
  Students At-Risk AI Mentor
     │       │      │
     ↓       ↓      ↓
 Search   Risk View Questions
 Filter          │      │
 Sort            │      ↓
     │           │    SQL/RAG/
     ↓           │    Project Tools
 Student Detail  │      │
     │           │      ↓
     ↓           │    Answer
   Project       │
     │           │
 ┌───┼───────────┼────────────┐
 ↓   ↓           ↓            ↓
Tasks Milestones Risks      GitHub
 │   │           │            │
 └───┴───────────┴────────────┘
             │
             ↓
        Project Monitoring
             │
      ┌──────┴──────┐
      ↓             ↓
Mentor Note     Student Help
      ↓             ↑
   Student       Student
```

---

# 22. Mentor-Side Approval Status

| Dimension | Assessment |
|---|---|
| Product value | ⭐⭐⭐⭐⭐ Very High |
| Internship value | ⭐⭐⭐⭐⭐ Very High |
| Implementation feasibility | ⭐⭐⭐⭐½ High after scope cleanup |
| Complexity | ⭐⭐⭐⭐ Moderate to High |
| V1 scope | Manageable |
| Agentic AI relevance | ⭐⭐⭐⭐⭐ Excellent |
| Feature completeness | Approved |
| Scope status | **FROZEN FOR NOW** |
| Overall decision | **APPROVED** |

---

## Final Mentor-Side Decision

The Mentor side is now considered **approved and frozen for the current feature-design process**.

Future technical discussions may define implementation details such as:

- Database relationships
- Exact metric formulas
- API contracts
- Authorization implementation
- AI tool schemas
- Agent responsibilities
- Notification mechanisms

Those decisions **must not silently expand the approved Mentor feature scope**.

**Next planned section: Student Side.**
