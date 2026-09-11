# GrowFlow — Part 5C: Mentor Application Architecture
## Final V1 Specification

**Status:** FROZEN  
**Part:** 5C — Mentor Application  
**Depends on:** Part 5A — Application Foundation, Part 5B — Student Application, Part 4 — AI Agent Architecture

---

# 1. Purpose

Part 5C defines the Mentor-side application experience.

The Mentor application is designed around one principle:

> **The Mentor supervises, understands, guides, and monitors students and projects without taking ownership of student execution.**

The Mentor application therefore focuses on:

- group supervision
- student monitoring
- project-definition management
- student project observation
- risk identification
- performance visibility
- human mentorship
- AI-assisted analysis
- project activity
- authorized GitHub activity

The Mentor does not become an administrator or project operator.

---

# 2. Shared Application Foundation

All authentication, navigation, shell, sharing, scrolling, responsive behavior, profile/settings placement, and common authorization rules are inherited from **Part 5A**.

They are not redesigned in Part 5C.

Shared rules include:

- separate Mentor authentication
- Google OAuth
- GitHub OAuth
- password recovery
- fixed Top Navigation
- persistent Left Navigation
- Top Navigation Share action
- Top Navigation Notifications
- Top Navigation Search
- Profile at the bottom of the Left Navigation
- Settings at the bottom of the Left Navigation
- collapsible icon-only sidebar
- independent content scrolling
- fixed bottom Profile/Settings area
- responsive mobile drawer

The Mentor application only defines what is unique to the Mentor role.

---

# 3. Mentor Application Information Architecture

```text
MENTOR APP
│
├── Overview
│
├── Groups
│   └── Group Workspace
│
├── Students
│   └── Student Detail
│
├── Projects
│   ├── Project Definitions
│   └── Student Project Instances
│
├── At Risk
│
├── AI Mentor
│
├── Notifications
│
└── Profile / Settings
```

---

# 4. Mentor Overview

## Purpose

The Mentor Overview is the Mentor's command center.

Its primary question is:

> **Who needs my attention?**

The Mentor should be able to understand the overall situation and quickly reach the students/projects requiring attention.

---

# 5. Overview Information Hierarchy

The recommended priority is:

1. Students/projects needing attention
2. At-risk projects
3. Group health
4. Top five performers
5. Overall platform statistics within the Mentor's scope
6. Recent activity

The Overview should be action-oriented rather than becoming an excessive analytics dashboard.

---

# 6. Overview Statistics

The Mentor can see scoped statistics such as:

- groups
- students
- projects
- average progress
- healthy projects
- at-risk projects
- completed projects
- ongoing projects
- planned projects

Example:

```text
Groups       Students       Projects       At Risk
   4            42             38             6
```

All values are restricted to the Mentor's authorized scope.

---

# 7. Students Needing Attention

The Overview should prominently identify students/projects requiring Mentor attention.

Example:

```text
STUDENTS NEEDING ATTENTION

Student A
Project: AI Assistant
Reason: Deadline approaching + incomplete milestone
[ View ]

Student B
Project: Recommendation System
Reason: No meaningful activity for 8 days
[ View ]
```

The Mentor should be able to move directly from the attention item to the relevant Student Detail or Project Instance.

---

# 8. Group Health

The Overview can summarize each authorized group.

Example:

```text
GROUP HEALTH

Group A     Healthy      82% avg progress
Group B     Healthy      74% avg progress
Group C     At Risk      51% avg progress
Group D     Healthy      88% avg progress
```

The Mentor can open a group to enter its Group Workspace.

---

# 9. Top Five Performers

The Top 5 ranking remains part of the Mentor Overview.

The ranking uses a transparent deterministic scoring system based on approved project-execution indicators such as:

- progress
- milestone completion
- task completion
- consistency/activity
- health
- deadline adherence

Idea Score must not dominate execution ranking.

The ranking should be explainable.

---

# 10. Recent Activity

The Mentor Overview can show meaningful recent activity across the Mentor's authorized scope.

Examples:

```text
✓ Student completed milestone
⚠ Project became at risk
💬 New help request
📄 Blueprint regenerated
```

The Mentor can navigate to the related resource.

---

# 11. Groups

Groups are the primary organizational structure for Mentor supervision.

The Mentor can:

- create groups
- generate a unique Group ID/join code
- view groups
- open a group
- see group students
- see group projects
- monitor group health
- access group-level AI assistance

Group management intentionally remains minimal.

The Mentor is not given an extensive administrative group-management suite.

---

# 12. Create Group

The basic group-creation flow is:

```text
Create Group
    ↓
Group Name
    ↓
Generate Group ID / Join Code
    ↓
Group Created
```

Example:

```text
Group Name:
AI Engineering — Batch 2026

Join Code:
GF-AI26-X7K4
```

The generated join code can be provided to students.

---

# 13. Minimal Group Management

V1 intentionally avoids unnecessary group-management complexity.

The Mentor does not need a large management system for:

- complex group configuration
- elaborate permissions
- advanced group administration
- unnecessary organizational hierarchy

The Group Workspace is primarily for supervision.

Any additional group lifecycle operations should be introduced only if a concrete platform requirement emerges.

---

# 14. Group Workspace

Opening a group provides the Mentor with a focused group environment.

Recommended group navigation:

```text
Students | Projects | At Risk | Activity | AI Mentor
```

This is confirmed as the standard Group Workspace structure.

---

# 15. Group Students

The Students section shows all students belonging to the selected group.

Recommended table:

```text
Student       Project          Progress   Health   Last Activity
───────────────────────────────────────────────────────────────
Student A     AI Assistant       82%      Healthy      Today
Student B     Chatbot            61%      Warning      2 days
Student C     CV System          42%      At Risk      8 days
Student D     RAG System         91%      Healthy      Today
```

The Mentor can:

- search
- filter
- sort
- open Student Detail

---

# 16. Group Projects

The Projects section shows project instances associated with students in that group.

It should provide visibility into:

- project
- student
- progress
- health
- current phase
- deadline
- risk
- last activity

The Mentor can open the relevant Student Project Instance.

---

# 17. Group At Risk

The Group At Risk section provides a scoped view of problems within the selected group.

It uses the same explanation model as the global Mentor At-Risk page:

- reason
- category
- impact
- recommended action

This allows the Mentor to focus on the group without reviewing the entire Mentor portfolio.

---

# 18. Group Activity

Group Activity shows meaningful project/student events for the selected group.

Examples:

```text
Today
✓ Student A completed Authentication

Yesterday
⚠ Student B project became at risk

Sep 8
💬 Student C submitted a Help Request
```

Activity should link to the relevant resource.

---

# 19. Group AI Mentor

Each group can be analyzed through the Mentor AI.

The AI receives only the authorized group scope and can answer questions such as:

```text
How is this group performing?

Which students need attention?

Which projects are behind schedule?

Why is Student A at risk?

Who has been inactive recently?
```

The AI follows the Mentor AI boundaries defined later in this document.

---

# 20. Students

The global Students page contains all students the Mentor is authorized to access.

Recommended controls:

```text
[ Search students... ]

[ Group ] [ Health ] [ Status ] [ Progress ]
```

The table can contain:

- student
- group
- project
- progress
- health
- current phase
- last activity

The Mentor can search, filter, sort, and open a Student Detail page.

---

# 21. Student Query Scope

The same shared query abstraction defined earlier remains the preferred application model:

```text
StudentQueryService(
    mentor_id,
    group_id optional,
    search,
    filters,
    sort
)
```

When viewing all Mentor-authorized students:

```text
group_id = null
```

When viewing students inside a group:

```text
group_id = selected_group
```

This avoids building separate search/filter implementations for global and group contexts.

---

# 22. Student Detail

Student Detail is one of the most important Mentor screens.

It should provide a consolidated understanding of the student.

Example:

```text
STUDENT

Name
Student ID
Group

Projects

Selected Project:
AI Document Assistant

Progress       72%
Health         Healthy
Phase          Implementation
Deadline       24 days

────────────────────────

Idea Score
Technologies
Current Milestone
Blocked Tasks
Risks
GitHub Activity
Last Activity
```

---

# 23. Student Detail Navigation

Recommended contextual sections:

```text
Overview | Projects | Activity | Mentor Notes | Help Requests
```

The Mentor can select one of the student's project instances.

When a project is selected, project-specific information updates accordingly.

---

# 24. Multiple Student Projects

If a Student has multiple projects:

```text
Student A

Projects

● AI Assistant
  72% • Healthy

○ Recommendation Engine
  31% • At Risk
```

Selecting a project opens its corresponding independent project context.

The Mentor must never confuse multiple project instances belonging to the same Student.

---

# 25. Project Definitions vs Student Project Instances

This distinction is fundamental to GrowFlow.

The Mentor's Projects area has two conceptual categories:

```text
Project Definitions
        +
Student Project Instances
```

They are not the same entity.

---

# 26. Project Definition

A Project Definition is the reusable project foundation created by a Mentor.

Example:

```text
AI Document Assistant
Mentor Project Definition
```

It can be assigned to multiple students.

---

# 27. Student Project Instance

A Student Project Instance is the actual independent project owned/executed by a specific Student.

Example:

```text
AI Document Assistant
Student: Student A
Progress: 72%
```

Every instance independently owns:

- project profile
- assessment
- Blueprint
- tasks
- milestones
- risks
- progress
- health
- timeline
- documents
- GitHub
- AI context
- activity

---

# 28. Project Definition Relationship

```text
                  Mentor
                    │
                    ▼
           Project Definition
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Student A   Student B   Student C
     Instance     Instance    Instance
```

The definition is reusable.

The instances are independent.

---

# 29. Creating a Project Definition

The Mentor can create a project definition using information such as:

- project name
- problem statement
- proposed solution
- complexity
- project description
- suggested technologies
- expected functionality
- project expectations
- constraints

The Mentor creates the reusable foundation.

The student's actual project instance still follows the Student-side assessment and Blueprint process.

---

# 30. Assignment of Project Definitions

The Mentor can assign a project definition to one or more students.

Example:

```text
AI Document Assistant

[ Assign Students ]

☑ Student A
☑ Student B
☐ Student C
☑ Student D

[ Assign ]
```

Each selected Student receives a separate project instance.

---

# 31. Project Definition Editing

A Mentor may modify an existing Project Definition even after students have already been assigned to it.

However:

> **Editing the Project Definition does not modify existing Student Project Instances.**

This prevents a Mentor-side template change from silently changing active student projects.

---

# 32. Existing Student Instances Remain Unchanged

Suppose the Mentor changes:

```text
Project Definition
Version 1
```

to:

```text
Project Definition
Version 2
```

Existing instances continue using their existing project context.

Example:

```text
Project Definition V2
        │
        ├── New Student → receives V2 foundation
        │
        ├── Existing Student A → remains on existing instance
        ├── Existing Student B → remains on existing instance
        └── Existing Student C → remains on existing instance
```

No automatic project-state mutation occurs.

---

# 33. Notification of Project Definition Update

When a Project Definition is changed after students have already been assigned:

> **A concise informational Mentor Note/notification is sent to the affected existing students.**

The notification informs them that the Mentor has updated the shared project definition.

It does not automatically alter their project.

Example:

```text
Mentor Update

Your mentor has updated the project definition
for the project template you originally selected.

Your current project remains unchanged.

Review the update if relevant to your project.
```

The notification is intentionally lightweight.

There is no automatic migration.

---

# 34. Existing Students Decide What to Do

An existing Student may choose to act on the updated Mentor definition.

If the Student wants to adopt the new direction:

```text
Updated Mentor Definition
        ↓
Student reviews change
        ↓
Student communicates with AI agents / AI Mentor
        ↓
Student updates Project Profile if needed
        ↓
Blueprint impact/re-generation workflow
        ↓
New project plan
        ↓
Student continues execution
```

The Student remains in control of the existing project instance.

---

# 35. No Automatic Migration

GrowFlow must not automatically:

- replace the Student's Project Profile
- replace the Student's Blueprint
- change tasks
- change milestones
- change duration
- change risks
- change technologies
- change progress
- change the current phase

because of a Mentor Project Definition update.

This protects project continuity and student ownership.

---

# 36. Student-Initiated Update Path

If an existing Student wants to incorporate the Mentor's updated direction, the Student can use the established project-change workflow.

The Student can:

- review the new information
- communicate with the AI Mentor/agents
- update the Project Profile
- regenerate affected Blueprint outputs
- continue with the new project plan

The application therefore supports change without silently mutating the project.

---

# 37. Mentor Project View

The Mentor can see how a Project Definition is being used.

Example:

```text
AI Document Assistant

Project Definition
Assigned Students: 8

Student Instances
────────────────────────

Student A    72%    Healthy
Student B    64%    Healthy
Student C    41%    At Risk
Student D    89%    Healthy
```

The Mentor can move from the definition to individual student instances.

---

# 38. At-Risk Dashboard

The Mentor has a dedicated global:

```text
At Risk
```

page.

The purpose is to answer:

> **Which students/projects require intervention or attention right now?**

---

# 39. At-Risk Presentation

The page should not display only health colors.

Example:

```text
6 PROJECTS AT RISK

CRITICAL

Student A
Deadline approaching
3 milestones incomplete

Student B
No meaningful activity
for 9 days

WARNING

Student C
Technology integration
blocked
```

---

# 40. Risk Explanation

Each at-risk item should explain:

- reason
- category
- impact
- relevant project state
- recommended Mentor action

Example:

```text
AT RISK

Reason:
Deadline approaching with
2 incomplete milestones.

Category:
Deadline / Task Delay

Impact:
High

Recommended Mentor Action:
Check progress with student.
```

This follows the previously frozen At-Risk architecture.

---

# 41. At-Risk Categories

Potential categories include:

- scope
- deadline/time
- inactivity
- technology
- task/milestone delay
- AI/project quality
- deployment

The system should use the categories defined in the canonical risk model.

---

# 42. At-Risk Filters and Sorting

The Mentor can filter by:

- group
- risk category
- severity
- project phase
- deadline
- inactivity
- technology
- task/milestone delay

The Mentor can sort by:

- severity
- deadline proximity
- longest inactivity
- progress
- last activity

---

# 43. Ranking

The Mentor retains the Top 5 performer ranking.

The score remains deterministic and explainable.

Candidate factors:

```text
Progress
+
Milestone completion
+
Task completion
+
Consistency/activity
+
Health
+
Deadline adherence
```

Idea Score is not the dominant execution metric.

---

# 44. GitHub Mentor View

The Mentor can monitor GitHub activity for authorized Student Project Instances.

Visible information can include:

- repository connection status
- commit count
- recent commits
- last meaningful activity
- activity trends

The Mentor cannot manage the repository.

---

# 45. GitHub Exclusions

V1 excludes:

- repository editing
- issue management
- pull-request management
- CI/CD management
- repository administration
- code editing through GrowFlow

GitHub remains an observation/integration source.

---

# 46. Mentor Notes

Mentor Notes are the primary direct Mentor → Student communication mechanism.

A Mentor can create:

```text
Mentor Note

Title
Message

[ Send Note ]
```

The Student receives the note through the appropriate notification and Mentor views.

---

# 47. Mentor Note Boundary

A Mentor Note is communication, not automatic project-state modification.

Example:

```text
Mentor:
"Please complete OAuth by Friday."
```

This does not automatically change:

- task status
- deadline
- milestone
- progress
- health
- project phase

The Student remains responsible for execution.

---

# 48. Help Requests

Students can submit Help Requests.

Mentors can view and manage the request lifecycle.

Example:

```text
Help Requests

OPEN          4
IN PROGRESS   2
RESOLVED     17
```

Example request:

```text
Student A
Deployment issue
OPEN

[ View ]
```

---

# 49. Help Request Lifecycle

```text
Student
   ↓
Help Request
   ↓
OPEN
   ↓
Mentor reviews
   ↓
IN_PROGRESS
   ↓
Mentor assists
   ↓
RESOLVED
```

This is a real workflow rather than an unstructured messaging system.

---

# 50. Communication Scope

The V1 Mentor communication mechanisms are intentionally limited to:

1. Mentor Notes
2. Help Requests

No additional communication suite is required for V1.

This keeps the platform focused and avoids unnecessary chat/collaboration architecture.

---

# 51. Mentor AI

The Mentor receives a dedicated AI assistant.

The Mentor AI is different from the Student AI Mentor.

The Student AI focuses on:

> **How do I build my project?**

The Mentor AI focuses on:

> **How are my students/projects doing, and what requires my attention?**

---

# 52. Mentor AI Operating Model

The Mentor AI follows:

```text
Observe
   ↓
Analyze
   ↓
Explain
   ↓
Recommend
```

It does not become a control interface for modifying Student project state.

---

# 53. Mentor AI Questions

Examples:

### Group

```text
How is Group A performing?
```

### Students

```text
Which students have been inactive recently?
```

### Projects

```text
Which projects are behind schedule?
```

### Risks

```text
Why is Student A at risk?
```

### Performance

```text
Who are the top performers in this group?
```

### Activity

```text
What changed in Student B's project this week?
```

### Documents

```text
What technology is Student B using?
```

---

# 54. Mentor AI Context

The Mentor AI receives only authorized context.

```text
Mentor Identity
      ↓
Authorized Groups
      ↓
Authorized Students
      ↓
Authorized Project Instances
      ↓
Relevant Data
      ↓
AI Tools / RAG / GitHub / Reasoning
```

The AI must never bypass application authorization.

---

# 55. Mentor AI Source Routing

The source depends on the question.

## Structured state

```text
"Which students are at risk?"
```

→ project/database state tools.

## Project documentation

```text
"What does Student A's README say?"
```

→ authorized project-scoped RAG.

## GitHub

```text
"Has Student B committed recently?"
```

→ GitHub integration.

## Complex analysis

```text
"Why is Group A falling behind?"
```

→ structured state + activity + risks + relevant documents + reasoning.

---

# 56. Mentor AI Authorization

Authorization must happen before the AI receives data.

Incorrect:

```text
AI
 ↓
Full database
 ↓
Figure out what it can show
```

Correct:

```text
Mentor Request
 ↓
Authorization
 ↓
Authorized data/tool scope
 ↓
AI
```

This preserves Group, Student, Project, and RAG isolation.

---

# 57. Mentor AI State Mutation

Mentor AI must not directly manipulate Student project state.

For example:

```text
"Mark Student A's task complete."
```

The AI must not perform the action because Mentor permissions do not include direct student execution control.

The AI remains:

```text
Observe → Analyze → Explain → Recommend
```

---

# 58. Mentor AI Recommendations

The AI can recommend Mentor actions.

Example:

```text
Student A is blocked by deployment.

Recommended:
Contact the student through a Mentor Note
or review their open Help Request.
```

The Mentor explicitly chooses the action.

The AI does not silently send messages or alter project state.

---

# 59. Mentor Notifications

Mentor notifications focus on events that may require attention:

- new Help Requests
- student/project becomes at risk
- deadline warnings
- important project events
- milestone events
- meaningful inactivity
- student requests
- relevant system alerts

Notifications remain in the shared Top Navigation.

---

# 60. Mentor Activity

Activity can be viewed at multiple scopes:

```text
Group Activity
Student Activity
Project Activity
```

All use the same underlying activity model.

This allows the Mentor to move from:

```text
Portfolio
 ↓
Group
 ↓
Student
 ↓
Project
 ↓
Event
```

without maintaining separate activity systems.

---

# 61. Mentor Search, Filter, and Sort

Mentor search remains role-scoped.

The Mentor can search authorized:

- students
- groups
- projects

Filtering and sorting remain available where useful.

Authorization must be applied before results are returned.

---

# 62. Mentor Navigation

Final proposed navigation:

```text
Overview

Groups
  └── Group Workspace

Students
  └── Student Detail

Projects
  ├── Project Definitions
  └── Student Project Instances

At Risk

AI Mentor

Notifications

────────────────

Profile
Settings
```

Profile and Settings remain fixed at the bottom of the Left Navigation according to Part 5A.

---

# 63. Mentor Application Flow

```text
                    MENTOR
                      │
                      ▼
                  Overview
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
      Groups       Students       Projects
        │             │             │
        ▼             ▼             ▼
     Group          Student      Definitions
    Workspace       Detail          │
        │             │             ▼
        │             │          Assigned
        │             │          Students
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                   At Risk
                      │
                      ▼
                Mentor AI
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
       Analyze/Monitor      Recommend
            │                   │
            └─────────┬─────────┘
                      ▼
               Mentor Action
              Note / Help / Review
```

---

# 64. Mentor vs Student Responsibility

| Capability | Student | Mentor |
|---|---|---|
| Create own project | Yes | — |
| Create project definition | — | Yes |
| Execute project | Yes | — |
| Complete own tasks | Yes | — |
| Manage own project | Yes | Observe |
| View student progress | — | Yes |
| View group progress | — | Yes |
| Identify risks | System/AI | Yes |
| Respond to risks | Execute | Guide |
| Send Mentor Note | — | Yes |
| Create Help Request | Yes | Respond |
| AI assistance | Student AI | Mentor AI |
| GitHub management | No | No |
| View GitHub activity | Own | Authorized students |
| Change student progress manually | No | No |
| Complete student task | No | No |
| Edit student Blueprint directly | No | No |
| Modify student project instance from template change | No | No |

---

# 65. Project Definition Change Model

This is a formal application rule.

## Mentor changes a Project Definition

```text
Project Definition Updated
        │
        ├── New students
        │      ↓
        │   receive updated definition
        │
        └── Existing students
               ↓
          project unchanged
               ↓
          concise notification
```

Existing project instances remain authoritative for those students.

---

# 66. Existing Student Response to a Definition Change

An existing student may independently decide that the new Mentor direction is useful.

The Student can:

```text
Review update
    ↓
Consult AI Mentor / relevant agents
    ↓
Update Project Profile if desired
    ↓
Run project-change / Blueprint impact workflow
    ↓
Regenerate affected Blueprint outputs
    ↓
Continue execution
```

The Mentor does not force this migration.

---

# 67. Why This Model Is Used

This prevents a reusable Mentor project definition from becoming a dangerous shared mutable state.

Without this rule:

```text
Mentor edits template
      ↓
All active students change
      ↓
Existing tasks/roadmaps become inconsistent
```

With the approved model:

```text
Mentor edits definition
      ↓
Definition changes for future assignments
      ↓
Existing instances remain stable
      ↓
Students choose whether to adapt
```

This preserves:

- student ownership
- project continuity
- Blueprint consistency
- deterministic project state
- safe project evolution

---

# 68. Security and Authorization

Mentor access is constrained by:

```text
Mentor
 ↓
Authorized Groups
 ↓
Group Membership
 ↓
Authorized Students
 ↓
Authorized Project Instances
```

The same boundaries apply to:

- UI
- API
- database queries
- AI tools
- RAG
- GitHub data

A Mentor cannot access unrelated groups or students.

---

# 69. Final Mentor Application Decisions

| Area | Final Decision |
|---|---|
| Overview | Attention-oriented |
| Primary question | Who needs my attention? |
| Groups | Yes |
| Group Workspace | Students / Projects / At Risk / Activity / AI Mentor |
| Group management | Minimal |
| Students | Global authorized student view |
| Student Detail | Consolidated |
| Multiple student projects | Supported |
| Projects | Split into Definitions / Student Instances |
| Project Definition | Reusable Mentor-created foundation |
| Student Instance | Independent project state |
| Project assignment | Creates independent instances |
| Definition editing | Allowed |
| Definition update effect on existing instances | None |
| New students after update | Receive updated definition |
| Existing students after update | Remain unchanged |
| Existing-student notification | Concise update notification |
| Existing student adaptation | Optional, Student-controlled |
| Automatic migration | No |
| At Risk | Dedicated page |
| Risk explanation | Reason + category + impact + recommended action |
| Ranking | Transparent deterministic Top 5 |
| GitHub | Monitoring only |
| Mentor Notes | Yes |
| Help Requests | Yes |
| Other communication system | No |
| Mentor AI | Yes |
| Mentor AI model | Observe → Analyze → Explain → Recommend |
| Mentor AI state mutation | No |
| Activity | Group / Student / Project scopes |
| Search | Authorized scope |
| Profile | Bottom Left Navigation |
| Settings | Bottom Left Navigation |
| Shared shell | Inherited from Part 5A |

---

# 70. Decision Log — Questions and Final Solutions

This section records the feedback received during Part 5C design and the solution adopted.

---

## Question 1 — Mentor Overview

### Decision

Use the **"Who needs my attention?"** model.

### Solution

The Overview prioritizes:

- students/projects needing attention
- at-risk projects
- group health
- top performers
- scoped statistics
- recent activity

The Mentor can move directly from a problem to the relevant student/project.

---

## Question 2 — Group Workspace

### Decision

Use:

```text
Students | Projects | At Risk | Activity | AI Mentor
```

### Solution

The Group Workspace becomes the focused supervision environment for a single group.

---

## Question 3 — Project Definitions vs Student Project Instances

### Decision

Keep them explicitly separate.

### Solution

Mentor-created Project Definitions are reusable foundations.

Student Project Instances are independent execution environments.

This distinction is enforced in both the conceptual model and application UX.

---

## Question 4 — Student Detail

### Decision

Use a consolidated Student Detail page.

### Solution

The page combines:

- identity
- group
- projects
- progress
- health
- phase
- deadlines
- risks
- tasks/blockers
- GitHub activity
- last activity

Project selection changes the project-specific context.

---

## Question 5 — At-Risk Dashboard

### Decision

Use:

```text
Reason
Category
Impact
Recommended Action
```

### Solution

The Mentor never receives only a red/yellow/green health indicator.

The application explains why the project is at risk and what the Mentor can consider doing.

---

## Question 6 — Mentor AI

### Decision

Use:

```text
Observe
→ Analyze
→ Explain
→ Recommend
```

### Solution

Mentor AI assists with understanding and decision support.

It does not directly manipulate Student project state.

---

## Question 7 — Communication

### Decision

Mentor Notes + Help Requests are sufficient for V1.

### Solution

No separate full messaging/chat/collaboration suite is introduced.

This keeps communication focused and avoids unnecessary architecture.

---

## Question 8 — Group Management

### Decision

Keep Group management minimal.

### Solution

The Mentor can create and use groups for supervision without turning Groups into an administrative management system.

The Group Workspace is the primary operational experience.

---

## Question 9 — Editing Existing Project Definitions

### Decision

Mentors can edit an existing Project Definition after students have already been assigned.

### Solution

The update affects the Project Definition for future assignments but **does not modify existing Student Project Instances**.

Existing students receive a concise notification.

---

## Question 10 — What Happens to Existing Students After a Definition Update?

### Decision

Existing students remain unchanged.

### Solution

They can optionally choose to adapt their project.

If they choose to adopt the new direction:

```text
Updated information
    ↓
AI Mentor / relevant agents
    ↓
Student Project Profile update
    ↓
Blueprint impact/re-generation
    ↓
New project plan
```

This is Student-controlled.

---

## Question 11 — Automatic Migration

### Decision

No automatic migration.

### Solution

Mentor template changes never automatically modify:

- Project Profile
- Blueprint
- Tasks
- Milestones
- Risks
- Timeline
- Progress
- Phase
- Health

of an existing Student Project Instance.

---

# 71. Final Part 5C Status

| Part | Status |
|---|---|
| Part 1 — Mentor Side | 🟢 FROZEN |
| Part 2 — Student Side | 🟢 FROZEN |
| Part 3 — Admin Side | 🟢 FROZEN |
| Part 4 — AI Agent Architecture | 🟢 FROZEN |
| Part 5A — Application Foundation | 🟢 FROZEN |
| Part 5B — Student Application Architecture | 🟢 FROZEN |
| Part 5C — Mentor Application Architecture | 🟢 **FROZEN** |

---

# 72. Part 5C Completion Statement

The GrowFlow Mentor application is now defined as a supervision and decision-support environment.

The Mentor can:

```text
Monitor
→ Understand
→ Identify Risks
→ Analyze
→ Communicate
→ Guide
```

while the Student remains responsible for:

```text
Plan
→ Execute
→ Update
→ Learn
→ Complete
```

Project Definitions are reusable Mentor foundations, while Student Project Instances remain independent and protected from silent template changes.

The Mentor AI strengthens observation and decision-making without becoming a mechanism for directly controlling Student project execution.

All shared application-shell behavior remains inherited from Part 5A, keeping GrowFlow visually and behaviorally consistent across roles.
