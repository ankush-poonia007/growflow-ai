# GrowFlow — Part 5B: Student Application Architecture
## Final V1 Specification

**Status:** FROZEN  
**Part:** 5B — Student Application  
**Depends on:** Part 5A — Application Foundation, Part 4 — AI Agent Architecture

---

# 1. Purpose

Part 5B defines the complete Student-side application experience inside GrowFlow.

The Student application is designed around one central principle:

> **The Dashboard tells the student what needs attention; the Project Workspace is where the student actually works on the project.**

The application connects:

```text
Project Creation
→ Assessment
→ AI Understanding
→ Project Blueprint
→ Execution
→ Monitoring
→ AI Mentor
→ Human Mentor
→ Completion
```

---

# 2. Student Application Information Architecture

```text
STUDENT APP
│
├── Dashboard
│
├── Projects
│   ├── All Projects
│   ├── Create Project
│   │   ├── Create Own Project
│   │   └── Select Mentor Project
│   │
│   └── Project Workspace
│       ├── Overview
│       ├── Blueprint
│       ├── Tasks
│       ├── Milestones
│       ├── Risks
│       ├── Documents
│       ├── GitHub
│       ├── Activity
│       └── AI Mentor
│
├── Mentor
│   ├── Mentor Information
│   ├── Mentor Notes
│   └── Help Requests
│
├── Notifications
│
└── Profile / Settings
```

Profile and Settings remain in the fixed bottom section of the Left Navigation as defined in Part 5A.

---

# 3. Student Dashboard

## Purpose

The Dashboard is the student's command center.

It should answer:

> **What is happening with my projects, and what should I do next?**

It should not become an analytics-heavy dashboard.

## Recommended information hierarchy

1. Next Recommended Action
2. Current Project
3. Health / Deadline
4. Recent Activity
5. Overall Project Statistics

---

# 4. Dashboard Content

The Dashboard can contain:

- student name
- Student ID
- active projects
- completed projects
- ongoing projects
- planned projects
- overall progress
- current project
- group
- mentor
- mentor notifications
- pending help requests
- recent activity
- next recommended action
- project-oriented profile summary

Example:

```text
Good morning, Student

Active Projects     Overall Progress     At Risk     Due Soon
      3                    68%              1           2

CURRENT PROJECT
AI Document Assistant
Progress: 72%
Phase: Implementation
Health: Healthy
Deadline: 24 days

[ Open Project ]

NEXT RECOMMENDED ACTION
Complete API Integration

[ View Task ]

RECENT ACTIVITY
✓ Milestone completed
⚠ Risk identified
✓ GitHub activity detected
```

---

# 5. Multiple Projects

A Student can have multiple project instances.

The Dashboard therefore must not assume that one project is permanently active.

The Projects page provides access to all authorized student projects.

---

# 6. Projects Page

The Projects page contains:

- project search
- filters
- sorting
- project cards/list
- Create Project action

Example:

```text
My Projects

[ Search projects... ]     [ Filter ] [ Sort ]

[ + Create Project ]

Project A
72% • Healthy • Implementation

Project B
31% • At Risk • Planning

Project C
100% • Completed
```

---

# 7. Project Creation

There are two project-creation paths.

```text
Create Project
       │
       ├── Create Your Own Project
       │
       └── Select Mentor Project
```

Both paths eventually enter the same assessment pipeline.

---

# 8. Create Your Own Project

Student provides:

- project name
- project complexity
- problem statement
- proposed solution
- optional preferred technology stack
- duration
- deadline
- optional GitHub repository

The entered information is saved as a draft so the student can recover from an interrupted workflow.

---

# 9. Select Mentor Project

The student can view mentor-created project definitions they are authorized to access.

Each available project may show:

- project name
- complexity
- short description
- mentor
- relevant project information

Student can:

- view details
- select the project

Selecting the mentor project creates an **independent Student Project Instance**.

---

# 10. Independent Project Instance

A mentor-created project definition is not the student's actual shared project state.

Example:

```text
Mentor Project Definition
          │
          ├── Student A Project Instance
          ├── Student B Project Instance
          └── Student C Project Instance
```

Each instance independently owns:

- project state
- assessment
- blueprint
- documents
- tasks
- milestones
- risks
- progress
- health
- timeline
- GitHub connection
- AI context
- activity
- mentor communication

---

# 11. Mandatory Assessment

Every Student project must complete the AI assessment.

This applies to both:

```text
Create Own Project
```

and:

```text
Select Mentor Project
```

Selecting a mentor project does **not** bypass the assessment.

---

# 12. Assessment Structure

The assessment contains:

```text
10 Core Questions
        +
5 Dynamic Questions
        ↓
15 Total Questions
```

The core questions remain standardized.

The dynamic questions are project-specific and sequentially adaptive.

---

# 13. Core Questions

The 10 core questions remain the same standardized questions for the relevant Student assessment.

They cover areas such as:

- existing knowledge
- previous project experience
- problem understanding
- solution understanding
- technical confidence
- expected implementation depth
- desired learning depth
- ambition
- constraints
- goals

The wording/structure of the core assessment is standardized so Student assessments retain a consistent baseline.

---

# 14. Dynamic Question Logic — Final Decision

The five dynamic questions are **not generated as a fixed batch before the Student answers them**.

Instead, they are generated sequentially.

The next dynamic question is determined by:

- the actual project
- the project profile
- the Student's skill level
- the Student's previous answers
- the previous dynamic answer
- relevant earlier assessment answers
- technologies/functionality involved

Therefore:

```text
Project Context
      +
Core Assessment
      ↓
Dynamic Question 1
      ↓
Student Answer
      ↓
Analyze Answer
      ↓
Dynamic Question 2
      ↓
Student Answer
      ↓
Analyze Answer
      ↓
Dynamic Question 3
      ↓
Student Answer
      ↓
...
      ↓
Dynamic Question 5
```

This creates genuine adaptive assessment rather than five generic follow-up questions.

---

# 15. Dynamic Question Quality Rule

Each dynamic question must have a clear reason for existing.

The system should be able to determine:

> **What information is this question trying to discover that is not already known?**

A dynamic question should therefore be influenced by the previous answer and should materially improve the Project Profile.

The system should avoid:

- generic conversational questions
- repetitive questions
- questions whose answers do not affect project understanding
- repeating information already established
- arbitrary curiosity questions

---

# 16. Assessment UX

The Student should see one question at a time.

Example:

```text
Question 12 of 15

━━━━━━━━━━━━━━━━━━━━░░░

Question:
How do you plan to handle real-time
synchronization between multiple users?

[ Answer ]

[ Back ]                    [ Next ]
```

The interface should show progress clearly.

The Student should be able to move through the assessment without seeing a giant 15-question form.

---

# 17. Assessment Completion

After Question 15:

```text
Assessment Complete ✓

GrowFlow is analyzing your project
and technical context.

[ Continue ]
```

The assessment is persisted before the AI analysis begins.

---

# 18. AI Assessment

The system analyzes:

- project information
- 10 core answers
- 5 adaptive answers
- Student skill
- project complexity
- constraints
- technology context

Output:

> **Enriched Project Understanding**

This becomes important input to the Project Profile and downstream Blueprint workflow.

---

# 19. Assessment Result Presentation

The Student can receive a concise useful summary.

Example:

```text
PROJECT UNDERSTANDING

Skill Level
Intermediate

Project Complexity
Advanced

Alignment
Good — some areas require learning

Technical Confidence
Moderate

Learning Depth
High

Recommended Focus
Backend architecture + API integration
```

The result is guidance rather than an absolute judgment of the Student.

---

# 20. Project Blueprint

After assessment:

```text
Project Understanding
        ↓
Generate Project Blueprint
```

The Blueprint is the main transition from project idea to executable project plan.

---

# 21. Blueprint Generation

The Student sees generation progress.

Example:

```text
Generating Project Blueprint

✓ Project Profile
✓ Technology Stack
✓ Features
✓ Specifications
✓ MVP
✓ Duration
⟳ Risk Documentation
○ Tasks
○ Milestones
○ README
```

The system should expose meaningful progress rather than only displaying a generic loading spinner.

---

# 22. Blueprint Generation Failure

If an agent/document fails:

```text
Blueprint Generation

✓ Project Profile
✓ Technology Stack
✓ Features
✕ Specifications

Specification generation failed.

[ Retry ]
```

Successful valid outputs remain available.

The retry process follows Part 4's version-aware targeted recovery architecture.

---

# 23. Blueprint QA

The generated Blueprint passes through:

```text
Generation
    ↓
Validation
    ↓
QA / Judge
    ↓
PASS / FAIL
```

If QA fails:

```text
QA
 ↓
Affected Outputs
 ↓
Targeted Regeneration
 ↓
Validation
 ↓
QA Again
```

If QA passes:

```text
Approved Blueprint
```

---

# 24. Project Workspace

The Project Workspace is the central Student execution environment.

Contextual navigation:

```text
Project Name

Overview
Blueprint
Tasks
Milestones
Risks
Documents
GitHub
Activity
AI Mentor
```

The Project Workspace is reached through:

```text
Projects
   ↓
Select Project
   ↓
Project Workspace
```

---

# 25. Project Overview

The Overview answers:

> **Where does my project stand right now?**

It contains:

- project name
- health
- idea score
- progress
- current phase
- technology stack
- duration
- deadline
- days remaining
- current milestone
- blocked tasks
- risks
- GitHub activity
- last activity
- next recommended action

---

# 26. Tasks

Tasks represent executable work.

Recommended filters:

```text
All
TODO
IN_PROGRESS
BLOCKED
COMPLETED
```

Example:

```text
Authentication API
IN_PROGRESS
Due: Sep 14

Database Setup
COMPLETED

OAuth Integration
BLOCKED

API Testing
TODO
```

Student can update task state through the authorized application interface.

The backend then recalculates dependent state deterministically.

---

# 27. Deterministic State Chain

```text
Task State
    ↓
Milestone State
    ↓
Progress
    ↓
Phase
    ↓
Health
```

AI may explain or recommend.

AI does not arbitrarily calculate or overwrite authoritative project state.

---

# 28. Milestones

Milestones provide higher-level checkpoints.

Example:

```text
✓ Project Foundation
✓ Authentication
● Core Implementation
○ Testing
○ Deployment
```

Selecting a milestone reveals:

- purpose
- related tasks
- target date
- completion criteria
- progress
- blockers

---

# 29. Risks

Risks have their own dedicated Project Workspace page.

The Risk page is not treated as a generic document viewer.

It contains the structured risk-management experience defined in the Student specification.

It can show:

- risk
- probability
- impact
- reason
- early warning
- prevention
- mitigation
- recommended action

---

# 30. Blueprint Document Viewer — Final UX Decision

The generated Blueprint documents should have a dedicated document-viewing experience.

The user requested that when viewing the Blueprint documentation, there should be a **small horizontal navigation bar at the top of the document content**.

Conceptually:

```text
+-------------------------------------------------------------+
| Idea | Scope | Tech Stack | Specification | Features | MVP |
| Duration | README | ...                                    |
+-------------------------------------------------------------+
|                                                             |
|                  CURRENT DOCUMENT                           |
|                                                             |
|                  Document Content                           |
|                                                             |
+-------------------------------------------------------------+
```

The first document is opened automatically by default.

---

# 31. Blueprint Document Navigation Rules

The mini document navigation:

- appears at the top of the Blueprint document viewer
- contains document names
- allows one-click switching
- opens the first document by default
- keeps the current document active
- does not include documents that already have their own dedicated Project Workspace page

The navigation is a document switcher, not another global application navigation system.

---

# 32. Documents Excluded from the Blueprint Mini Navigation

A document should not appear in the mini document navigation if its content already has its own dedicated Project Workspace page.

For V1, this means dedicated operational/project-management pages such as:

- Risks
- Tasks
- Milestones

are not duplicated inside the Blueprint document switcher.

This prevents duplicate navigation paths and inconsistent representations.

The dedicated page remains the authoritative user-facing operational experience.

---

# 33. Blueprint Document Set

The mini document navigation can contain the Blueprint's documentation-oriented documents, for example:

```text
Idea
Scope
Technology Stack
Specification
Features
MVP
Duration
README
```

The exact display order follows the Blueprint dependency/order defined by the system.

The UI may shorten long names for readability, while the underlying document type remains explicit.

---

# 34. Default Document

When the Blueprint document viewer opens:

> **The first document is opened automatically.**

The Student does not need to click a document before seeing content.

Example:

```text
Blueprint

[Idea] Scope Tech Stack Specification Features MVP Duration README

--------------------------------------------------------------

IDEA

Document content...
```

---

# 35. Current Document Download

The document viewer has a simple Download action.

Example:

```text
[ Download ↓ ]
```

Behavior:

```text
Current Open Document
        ↓
Download
        ↓
Current document downloaded
```

The download action applies to the currently selected document only.

There is no need for a complex document-download manager.

---

# 36. Document Viewing Modes

The Student can:

- View
- Preview
- Code / Raw Markdown
- Download

No full document editor is provided.

No Google Docs-style editing interface is provided.

---

# 37. Documents vs Blueprint Viewer

The Project Workspace can contain a dedicated Documents section for accessing generated/uploaded project files.

The Blueprint viewer is specifically optimized for navigating the structured Blueprint documents.

This avoids mixing:

- Blueprint documentation
- arbitrary uploaded project files
- operational project-management pages

into one overloaded interface.

---

# 38. GitHub

The GitHub page provides monitoring information:

- connected repository
- commit count
- recent commits
- last meaningful activity
- activity trends

V1 does not provide:

- repository editing
- issue management
- pull-request management
- CI/CD management
- repository administration

---

# 39. Activity

The Activity page provides a chronological project timeline.

Examples:

```text
Today
✓ Authentication task completed

Yesterday
⚠ Risk updated

Sep 8
✓ Milestone completed

Sep 7
📄 Blueprint regenerated

Sep 6
💬 Mentor sent a note
```

Relevant events include:

- task completion
- milestone events
- blueprint generation
- document generation
- document regeneration
- GitHub activity
- risk events
- mentor notes
- help requests
- project profile changes
- technology/scope changes

---

# 40. AI Mentor

The AI Mentor is a dedicated Project Workspace section.

The AI Mentor should automatically understand the current project.

It may use:

- current project state
- Blueprint outputs
- tasks
- milestones
- risks
- project-specific RAG
- uploaded files
- GitHub information
- technical reasoning
- authorized tools

The Student should not repeatedly explain the project context.

---

# 41. AI Mentor Context

```text
Student
   ↓
Current Project
   ↓
Authorization
   ↓
Project Context
   ├── Project State
   ├── Blueprint
   ├── RAG
   ├── GitHub
   └── Authorized Tools
           ↓
       AI Mentor
```

Project isolation remains mandatory.

---

# 42. AI Chat — Streaming UX

The AI Mentor has a special streaming behavior.

When a new response begins generating, the interface should automatically position the Student at the **current generated response**.

The system does not simply lock the entire chat to the bottom.

It specifically follows the currently generated assistant response.

---

# 43. Streaming Lock Behavior — Final Decision

Suppose the Student is viewing an earlier section of the conversation and sends a new message.

When the AI begins streaming:

```text
Student message
      ↓
AI starts generating
      ↓
Viewport moves to current response
      ↓
Streaming response remains visible
```

The current generated response becomes the temporary focus.

---

# 44. Student Can Scroll During Generation

The Student is not trapped in the streaming position.

While the AI is generating, the Student may:

- scroll upward
- read older messages
- scroll through the current response
- inspect earlier content
- move away from the generated response

The system must not repeatedly force-scroll the Student back to the bottom on every streamed token.

This is critical.

---

# 45. Streaming Auto-Focus Rules

The recommended behavior is:

### At response start

Move the viewport to the current generated response.

### While Student remains following the response

Keep the current response visible as it grows.

### If Student manually scrolls away

Stop forcibly repositioning the viewport.

Allow the Student to read wherever they choose.

### If Student returns to the current response

The generated content continues streaming normally.

### Result

The system provides:

> **initial auto-focus, followed by user-controlled scrolling.**

It does not create an annoying "scroll hijack."

---

# 46. Streaming Example

```text
Before request:

Message 1
Message 2
Message 3
Student asks question
Message 4
```

AI starts:

```text
Message 4
AI response: The first step is...
                   ↑
             current focus
```

The response streams:

```text
AI response:
The first step is to configure...
Then create...
Then validate...
```

Student can now scroll upward:

```text
Message 1
Message 2
Message 3
```

The response continues generating in the background.

The viewport is not forcibly returned to the response.

This gives the Student control while preserving visibility of the current generation.

---

# 47. AI State-Changing Actions

Normal AI conversation does not modify project state.

Example:

```text
"What is JWT?"
```

No state change.

For:

```text
"I completed authentication."
```

AI may respond:

```text
Authentication is currently IN_PROGRESS.

Would you like me to mark it COMPLETED?

[ Confirm ] [ Cancel ]
```

Only explicit confirmation triggers the deterministic backend state update.

---

# 48. Human Mentor

The Student has a separate Mentor section.

It contains:

- mentor information
- group information
- mentor notes
- help requests
- request status

This is intentionally separate from AI Mentor.

---

# 49. AI Mentor vs Human Mentor

| AI Mentor | Human Mentor |
|---|---|
| AI assistance | Human supervision |
| Technical help | Mentorship |
| Project reasoning | Mentor guidance |
| Troubleshooting | Review/support |
| Project-context-aware | Assigned mentor relationship |

They complement each other.

---

# 50. Help Requests

Student can create a Help Request.

Example:

```text
Subject:
Deployment Problem

Description:
My deployment fails after...

[ Send Request ]
```

Lifecycle:

```text
OPEN
  ↓
IN_PROGRESS
  ↓
RESOLVED
```

The Student can see current status and history.

---

# 51. Next Recommended Action

The Next Recommended Action appears in:

1. Student Dashboard
2. Project Overview

Example:

```text
NEXT RECOMMENDED ACTION

Complete OAuth integration.

Why:
Authentication milestone is blocked
until OAuth is implemented.

[ View Task ]
```

Recommendations should be grounded in actual project state.

They should not be generic motivational messages.

---

# 52. Blocked Tasks

Blocked tasks receive special treatment.

Example:

```text
⚠ BLOCKED

OAuth Integration

Blocked because:
OAuth credentials are not configured.

[ Get AI Help ]
[ View Task ]
[ Ask Mentor ]
```

AI can help troubleshoot.

The Student can also escalate to the human mentor.

---

# 53. Student Notifications

Notifications can include:

- mentor notes
- help request updates
- project risks
- deadline warnings
- milestone events
- Blueprint completion
- Blueprint failure
- document regeneration
- GitHub activity warnings
- recommended actions

Notifications are accessed from the global Top Navigation as defined in Part 5A.

---

# 54. Student Search

Search remains in the global Top Navigation.

Student search is restricted to authorized student/project information.

Potential search targets:

- projects
- tasks
- milestones
- documents
- project content

Search must not expose another Student's resources.

---

# 55. Student Scrolling

All Student pages inherit the Part 5A scrolling rules:

- Top Navigation fixed
- Left Navigation persistent
- Left Navigation list independently scrollable when necessary
- Profile/Settings bottom block fixed
- Main Content independently scrollable
- browser window is not the primary application scroll container

Project Workspace components should avoid unnecessary nested scrollbars.

---

# 56. Student End-to-End Journey

```text
Student Login
      ↓
Student Dashboard
      ↓
Create / Select Project
      ↓
Project Information
      ↓
10 Core Questions
      ↓
5 Adaptive Dynamic Questions
      ↓
AI Assessment
      ↓
Enriched Project Understanding
      ↓
Generate Project Blueprint
      ↓
Specialized Agent Workflow
      ↓
Validation
      ↓
QA / Judge
      ↓
Approved Blueprint
      ↓
Project Workspace
      ↓
Tasks + Milestones + Risks
      ↓
Implementation
      ↓
GitHub + Activity
      ↓
AI Mentor + Human Mentor
      ↓
Testing
      ↓
Deployment
      ↓
Completed
```

---

# 57. Student Architecture Relationship

```text
                 STUDENT DASHBOARD
                        │
                        ▼
                  PROJECTS
                        │
               +--------+--------+
               |                 |
               ▼                 ▼
          CREATE OWN       MENTOR PROJECT
               |                 |
               +--------+--------+
                        ▼
                  ASSESSMENT
                        │
                        ▼
                 AI UNDERSTANDING
                        │
                        ▼
                PROJECT BLUEPRINT
                        │
                        ▼
                PROJECT WORKSPACE
                        │
        +---------------+----------------+
        |        |       |       |       |
        ▼        ▼       ▼       ▼       ▼
     Tasks   Milestones Risks  GitHub  Activity
        |        |       |
        +--------+-------+
                 │
                 ▼
          Progress / Health
                 │
        +--------+---------+
        ▼                  ▼
    AI Mentor         Human Mentor
```

---

# 58. Final Student Application Decisions

| Area | Final Decision |
|---|---|
| Dashboard | Action-oriented command center |
| Multiple projects | Supported |
| Project creation | Two paths |
| Own project | Full project profile input |
| Mentor project | Creates independent Student Project Instance |
| Assessment | Mandatory for both paths |
| Core questions | 10 standardized |
| Dynamic questions | 5 sequentially adaptive |
| Dynamic dependency | Previous answer + accumulated relevant context |
| Assessment UX | One question at a time |
| AI assessment | After all 15 |
| Blueprint | Main planning system |
| Blueprint generation | Visible agent/document progress |
| Blueprint failure | Targeted retry/recovery |
| QA | Required quality gate |
| Project Workspace | Central execution environment |
| Tasks | Dedicated page |
| Milestones | Dedicated page |
| Risks | Dedicated page |
| Blueprint documents | Dedicated document viewer |
| Blueprint mini-nav | Horizontal top document switcher |
| First Blueprint document | Opens automatically |
| Dedicated operational pages | Excluded from Blueprint mini-nav |
| Blueprint download | Download currently opened document |
| Document editing | Not provided |
| GitHub | Monitoring only |
| Activity | Project timeline |
| AI Mentor | Project-context-aware |
| AI state mutation | Explicit confirmation required |
| AI streaming | Current-response auto-focus |
| Streaming scroll | User can scroll away during generation |
| Streaming force-scroll | Disabled after manual departure |
| Human Mentor | Separate from AI Mentor |
| Help Requests | Open → In Progress → Resolved |
| Next Recommended Action | Dashboard + Project Overview |
| Blocked Tasks | AI help + mentor escalation |
| Notifications | Global Top Navigation |
| Search | Global Top Navigation, role/project scoped |

---

# 59. Decision Log — New Changes Requested

This section records the new changes introduced after the initial Part 5B proposal.

---

## Change 1 — Blueprint Document Mini Navigation

### User requirement

When viewing the project documentation, provide a small top navigation containing the main document names.

Example:

```text
Idea | Scope | Tech Stack | Specification | Features | MVP | Duration | README
```

### Solution

Added a dedicated **Blueprint Document Viewer** with a horizontal document switcher.

The first document opens automatically.

The Student can switch documents without leaving the Blueprint experience.

---

## Change 2 — Exclude Documents With Dedicated Pages

### User requirement

Documents that already have their own Project Workspace page should not appear in the Blueprint mini navigation.

### Solution

Operational documents such as:

- Tasks
- Milestones
- Risks

remain on their dedicated pages and are excluded from the Blueprint document switcher.

This prevents duplicate navigation and inconsistent user experiences.

---

## Change 3 — Download Current Blueprint Document

### User requirement

The Student should be able to download the currently opened document directly from the document viewer.

### Solution

Added a simple Download action:

```text
Current Document
      ↓
Download
      ↓
Current document downloaded
```

No document-management dialog is required.

---

## Change 4 — Dynamic Assessment Must Depend on Previous Answers

### User requirement

The five dynamic questions must be determined by the previous question's answer.

### Solution

Changed dynamic-question generation from:

```text
Generate all 5 dynamic questions
        ↓
Ask Student
```

to:

```text
Generate Dynamic Q1
        ↓
Answer
        ↓
Analyze
        ↓
Generate Dynamic Q2
        ↓
Answer
        ↓
Analyze
        ↓
...
        ↓
Generate Dynamic Q5
```

The dynamic question engine uses accumulated relevant context rather than only the immediately preceding answer.

The 10 core questions remain standardized.

---

## Change 5 — AI Chat Streaming Scroll Behavior

### User requirement

When an AI response begins streaming, the interface should take the Student to the current generated response. However, the Student must be free to scroll away while the response continues generating.

### Solution

Implemented the concept of:

> **Initial auto-focus + user-controlled scrolling**

Behavior:

1. AI response begins.
2. View moves to the current generated response.
3. Streaming remains visible.
4. If the Student manually scrolls away, GrowFlow stops forcing the viewport back.
5. The response continues generating.
6. The Student can return to the current response whenever desired.

This avoids aggressive token-by-token auto-scrolling.

---

# 60. Existing Decisions Preserved

The new changes do **not** replace the following previously approved decisions:

- Project Workspace is the Student's central execution environment.
- Dashboard remains the command center.
- Both project-creation paths require the assessment.
- Mentor project selection creates an independent project instance.
- Blueprint generation uses specialized agents.
- QA/Judge remains the quality gate.
- Targeted regeneration remains the recovery mechanism.
- Tasks/Milestones/Risks retain dedicated pages.
- Documents remain view/preview/raw-Markdown/download oriented.
- GitHub remains monitoring-only.
- AI Mentor remains project-context-aware.
- AI state changes require explicit confirmation.
- Human Mentor remains separate from AI Mentor.
- Help Requests retain Open → In Progress → Resolved.
- Next Recommended Action remains state-grounded.
- Blocked tasks can receive AI assistance and mentor escalation.
- Global application shell and scrolling behavior remain as frozen in Part 5A.

---

# 61. Final Part 5B Status

| Part | Status |
|---|---|
| Part 1 — Mentor Side | 🟢 FROZEN |
| Part 2 — Student Side | 🟢 FROZEN |
| Part 3 — Admin Side | 🟢 FROZEN |
| Part 4 — AI Agent Architecture | 🟢 FROZEN |
| Part 5A — Application Foundation | 🟢 FROZEN |
| Part 5B — Student Application Architecture | 🟢 **FROZEN** |

---

# 62. Part 5B Completion Statement

The GrowFlow Student application is now defined as a complete project-oriented workspace.

The Student moves from:

```text
Idea
→ Assessment
→ Understanding
→ Blueprint
→ Execution
→ Monitoring
→ Assistance
→ Completion
```

The application deliberately separates:

- planning from execution
- Blueprint documents from operational pages
- AI Mentor from Human Mentor
- AI recommendations from deterministic project state
- initial streaming focus from user-controlled chat navigation

The Student application therefore provides a coherent working environment without turning GrowFlow into either a generic task manager, a document editor, or a generic chatbot.
