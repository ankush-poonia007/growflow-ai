# GrowFlow — Student Side Specification

## Updated Version

**Project:** GrowFlow  
**Module:** Student Side  
**Status:** Updated version pending final approval  
**Last Updated:** September 10, 2026

---

# 1. Student Side Purpose

The Student side is the execution environment where a student:

1. Creates or selects a project.
2. Provides an initial project profile.
3. Completes a structured AI assessment.
4. Receives an enriched project understanding.
5. Generates a complete Project Blueprint and supporting documentation.
6. Executes the project through tasks and milestones.
7. Monitors progress, health, risks, deadlines, and GitHub activity.
8. Uses the AI Mentor for project and technical guidance.
9. Stores project files in an isolated workspace for project-specific RAG.
10. Communicates with the assigned mentor.

The core principle is:

> GrowFlow should reduce the student's planning and documentation workload while providing a reliable system for actually executing the project.

---

# 2. Student Authentication & Identity

## Features

- Student registration
- Student login
- Email/password authentication
- Google OAuth
- GitHub OAuth
- Secure password hashing
- Password strength validation: Weak, Basic, Strong
- Role-based authentication
- Unique Student ID
- Student profile
- Project-oriented preferences
- Technology experience
- Technologies previously used
- Technologies interested in learning
- Project interests and goals

The unique Student ID can be used by mentors to locate and manage students within authorized groups.

---

# 3. Student Dashboard

The dashboard is the student's central control panel.

## Dashboard Information

- Student name
- Student ID
- Active projects
- Completed projects
- Ongoing projects
- Planned projects
- Overall project progress
- Current/active project
- Group enrollment
- Mentor information
- Mentor notifications
- Pending help requests
- Recent activity
- Next recommended action

## Quick Profile

Relevant project-oriented information may include:

- Technologies the student knows
- Technologies previously used
- Technologies the student wants to learn
- Project interests
- Learning goals
- Relevant project preferences

GrowFlow should avoid excessive personality/taste profiling that does not materially improve project mentoring.

---

# 4. Project Creation & Selection

A student can start a project in two ways.

## Option A — Create Own Project

The student provides:

- Project name
- Project type/complexity: Basic, Intermediate, Advanced
- Problem statement
- Proposed solution
- Preferred technology stack — optional
- Project duration
- Deadline
- GitHub repository — optional

## Option B — Select Mentor Project

A student can select an existing mentor-created project.

The selected mentor project becomes the foundation for the student's own independent project instance.

### Mandatory Assessment Rule

Regardless of whether the student creates their own project or selects a mentor-created project, the student **always completes the AI Q/A assessment**.

The assessment is therefore not conditional on project origin.

```text
Own Project ------------------+
                              |
                              v
                       Initial Project Profile
                              |
Mentor Project ---------------+
                              |
                              v
                       Student AI Assessment
                              |
                              v
                       Enriched Project Profile
```

A mentor project is a starting project definition, not a reason to skip understanding the individual student's knowledge, goals, confidence, and intended implementation.

---

# 5. Student Skill Level vs Project Complexity

These are separate properties.

## Student Skill Level

- Beginner
- Intermediate
- Advanced

## Project Complexity

- Basic
- Intermediate
- Advanced

Example:

> Beginner student + Advanced project

should not automatically block the project.

Instead, GrowFlow may recommend:

- reducing scope
- additional learning requirements
- a more realistic duration
- simpler technologies
- additional milestones

The student's skill level describes the student; project complexity describes the project.

---

# 6. AI Project Assessment — 15 Questions

The AI assessment is a core Student feature.

Every student completes the assessment regardless of whether they created their own project or selected a mentor project.

## Question Structure

| Question Type | Count | Purpose |
|---|---:|---|
| Core questions | 10 | Consistent assessment of knowledge, confidence, goals, understanding, and expectations |
| Dynamic project-specific questions | 5 | Deep assessment based directly on the selected project |
| **Total** | **15** | Complete project/student assessment |

## 6.1 Core Questions

The 10 standardized questions should assess areas such as:

- Existing technical knowledge
- Previous project experience
- Understanding of the proposed problem
- Understanding of the proposed solution
- Technical confidence
- Expected implementation depth
- Desired learning depth
- Project ambition
- Constraints or limitations
- Learning and project goals

## 6.2 Dynamic Questions

The remaining 5 questions are generated specifically for the project.

The AI should consider:

- Project profile
- Problem statement
- Proposed solution
- Project type
- Project complexity
- Technologies
- Intended functionality
- Student skill level
- Student's previous answers

Dynamic questions must be high-quality and materially useful. They must not be generic conversational questions.

## Assessment Flow

```text
Initial Project Profile
        +
Student Skill Level
        |
        v
10 Core Questions
        |
        v
Project Analysis
        |
        v
5 Dynamic Project-Specific Questions
        |
        v
Student Answers
        |
        v
AI Assessment
        |
        v
Enriched Project Profile
```

The assessment produces a secondary/enriched project profile representing both what the project is intended to become and what the student currently understands and wants to achieve.

---

# 7. Generate Project Blueprint

The earlier narrow concept of a traditional "roadmap" is replaced by:

> **Generate Project Blueprint**

The Blueprint represents the complete project foundation rather than only a sequence of future steps.

Blueprint generation is a multi-document generation workflow.

---

# 8. Blueprint Documentation

The Blueprint generation system creates separate Markdown documents.

The documents are generated from the complete available project context, including:

- Initial project profile
- Mentor project definition, if applicable
- Student assessment
- Student skill level
- Project complexity
- Problem statement
- Proposed solution
- Technology preferences
- AI-enriched project profile
- Project scope
- Intended features
- Project duration

## Core Generated Documents

### 8.1 Project Profile

Defines the complete understanding of the project.

May contain:

- Project name
- Problem
- Proposed solution
- Objective
- Target users
- Project type
- Complexity
- Student skill level
- Project goals
- Scope
- Intended outcome
- Constraints
- Assumptions
- Project context

### 8.2 Technology Stack

Defines:

- Programming languages
- Frameworks
- Libraries
- Database
- APIs
- AI/ML technologies
- Authentication
- Deployment technologies
- Supporting tools

For each major technology, the document should explain:

- What it is
- Why it is needed
- Why it fits the project
- What the student needs to understand
- Where it will be used

### 8.3 Features & Specifications

Defines:

- Must-have features
- Should-have features
- Good-to-have features
- Out-of-scope features

Important features should have clear specifications such as:

- Purpose
- Expected behavior
- Dependencies
- Technical considerations
- Acceptance expectations

### 8.4 MVP Definition

Clearly defines:

- What is being built
- Application type: web, desktop, mobile, game, or other appropriate type
- Core MVP functionality
- Major components
- Scope boundaries
- What is deliberately excluded
- Why this MVP is appropriate

If AI is part of the project, the document can explain project-specific concepts such as:

- Chatbot
- AI assistant
- Agent
- Multi-agent orchestration

These explanations should be tied to the actual project.

### 8.5 Project Duration

Defines the complete development timeline.

### 8.6 Risk Documentation

Defines possible project risks and how to overcome them.

### 8.7 README

Provides a concise single-file overview of the complete project.

### 8.8 Tasks & Milestones

Defines the work that will later be managed through the Student project execution system.

---

# 9. Duration Documentation

Duration is represented as a dedicated structured document.

For each phase, it should clearly identify:

- Start date
- End date
- Phase name
- What the student will do
- Phase objective
- Expected outcome
- Dependencies
- Estimated duration

The document should also provide:

- Total project duration
- Phase-by-phase duration
- Final completion date
- Major completion milestones

Duration generation should consider:

- Project complexity
- Student skill level
- Scope
- Technology stack
- Number of features
- Dependencies
- Available project duration

---

# 10. Risk Agent & Risk Documentation

A dedicated Risk Agent/system identifies possible project risks.

## Risk Categories

- Implementation difficulties
- Technology difficulties
- Technology limitations
- API issues
- Third-party service failures
- Authentication problems
- Database problems
- AI/LLM issues
- Integration problems
- Deployment problems
- Hosting limitations
- Cost/API usage
- Time constraints
- Scope creep
- Learning difficulties
- Security problems
- Performance problems
- Dependency problems
- GitHub issues
- Unexpected complexity

For each significant risk, the documentation should define:

```text
Risk
 |
 +-- Probability
 |
 +-- Impact
 |
 +-- Why it may happen
 |
 +-- Early warning signs
 |
 +-- Prevention
 |
 +-- Mitigation
 |
 +-- What the student should do if it occurs
```

The risk document should be practical and actionable, not simply a list of generic risks.

---

# 11. Final Project README

The README is the compact master overview.

It should briefly mention:

- Project idea
- Project profile
- Objective
- Technology stack
- Features
- Specifications
- MVP
- Scope
- Duration
- Major phases
- Risks
- Tasks
- Milestones
- Project structure
- References to dedicated documentation

The README should not duplicate every dedicated document in full.

```text
Dedicated Documentation
        |
        v
Detailed understanding

README
        |
        v
Quick project understanding
```

---

# 12. Task & Milestone Documentation

GrowFlow generates predefined tasks and milestones after the project definition and development plan are established.

## Task Definition

Each task should clearly define:

- Task name
- Objective
- Description
- Why it exists
- Expected output
- Dependencies
- Estimated duration
- Start date
- End date
- Related milestone
- Completion criteria

## Milestone Definition

Each milestone should clearly define:

- Milestone name
- Purpose
- What it signifies in the development journey
- Related tasks
- Expected outcome
- Completion criteria
- Target date

Task and milestone management behavior will be finalized separately.

---

# 13. Document Generation & Failure Recovery

Document generation is a recoverable multi-document workflow.

A generation run may involve multiple document-generation steps/agents.

Example:

```text
Generate Blueprint
        |
        +-- Project Profile ........ OK
        |
        +-- Technology Stack ...... OK
        |
        +-- Features .............. FAILED
        |
        +-- Remaining documents ... NOT STARTED
```

The system must not blindly restart everything when the student clicks Retry.

## Retry Behavior

When retrying, GrowFlow first compares the current project state/context against the state/context used for the previous generation attempt.

It determines:

1. Which documents were successfully generated.
2. Which documents failed.
3. Whether the project state has changed.
4. Whether those changes affect already generated documents.
5. Whether the existing generated documents remain valid.

## Case A — No Relevant Changes

If no meaningful changes affect the successfully generated documents:

```text
Previously generated documents
        |
        v
Validate existing results
        |
        v
Keep valid documents
        |
        v
Resume from failed document
        |
        v
Continue remaining generation
```

Example:

```text
Project Profile ........ OK
Technology Stack ....... OK
Features ............... FAILED
MVP .................... NOT STARTED
Duration ............... NOT STARTED

Retry
  |
  +-- No relevant changes
  |
  +-- Keep Project Profile
  +-- Keep Technology Stack
  |
  +-- Retry Features
  +-- Continue MVP
  +-- Continue Duration
```

## Case B — Relevant Changes Affect Existing Documents

If the project changed and those changes materially affect documents that were already generated:

```text
Previous generation
        |
        v
Detect project changes
        |
        v
Impact analysis
        |
        v
Previously generated document affected
        |
        v
Regenerate affected documentation
        |
        v
Continue generation
```

If the changes are broad enough to affect the complete Blueprint, all Blueprint documents should be regenerated so the documentation remains internally consistent.

## Consistency Rule

The system must never intentionally leave the project with contradictory combinations of old-state and new-state documentation.

The goal is:

> All active generated documents must represent the same canonical project state.

---

# 14. Document Storage

Generated Markdown files are stored in the student's project workspace.

Document metadata/state should track:

- Document type
- Version
- Generation status
- Creation time
- Update time
- Generation context/version
- Current/active version
- Failure status where applicable

Example:

```text
Project Workspace
|
+-- README.md
+-- project_profile.md
+-- technology_stack.md
+-- features_specifications.md
+-- mvp_definition.md
+-- project_duration.md
+-- project_risks.md
+-- tasks_milestones.md
```

Previous valid versions should be preserved where versioning is required.

---

# 15. Documents UI

The Documents section is intentionally limited.

## Student can

- View document
- Preview document
- View raw Markdown/code
- Download document

The UI provides two primary viewing modes:

```text
+-------------------------------------+
| project_profile.md                  |
|                                     |
| [ Preview ]       [ Code ]          |
|                                     |
|          DOCUMENT CONTENT           |
|                                     |
|                         [Download]  |
+-------------------------------------+
```

## Explicitly excluded

- Google Docs-style editor
- Rich document editing
- PDF editing
- Collaborative document editing
- Complex document-formatting suite

The purpose is to let the student consume and download generated documentation without turning GrowFlow into a document-editing platform.

---

# 16. Project Dashboard

Once the project is active, the student receives an operational project dashboard.

## Dashboard

- Project name
- Project health
- Idea score
- Technology stack
- Project duration
- Deadline
- Days remaining
- Overall progress
- Current phase
- Tasks
- Milestones
- Risks
- GitHub activity
- Last activity
- Next recommended action
- Blocked tasks

---

# 17. Deterministic Project State

PostgreSQL/Supabase is the canonical source of truth.

The structured project state includes:

- Project
- Phase
- Milestone
- Task
- Risk
- Health
- Progress
- Deadline
- Project metadata

The flow is:

```text
Tasks
  |
  v
Task completion
  |
  v
Milestone completion
  |
  v
Project progress
  |
  v
Project phase
  |
  v
Project health
```

AI can analyze and explain this state, but it should not arbitrarily overwrite fundamental project state.

---

# 18. Project Phases

The project phase should be determined by actual project execution rather than manually selected by the student.

Proposed lifecycle:

```text
Documentation
      |
      v
Planning
      |
      v
Implementation
      |
      v
Testing
      |
      v
Deployment
      |
      v
Completed
```

Exact transition rules will be finalized during technical design.

---

# 19. Project Workspace

Each project receives an isolated workspace.

```text
Student
|
+-- Project A
|   +-- Workspace A
|
+-- Project B
|   +-- Workspace B
|
+-- Project C
    +-- Workspace C
```

The workspace is intended for project-related files such as:

- Python files
- Markdown
- PDFs
- Documentation
- Configuration/reference files
- Other supported project resources

---

# 20. Project-Specific RAG

Workspace files can become the project's knowledge source.

Pipeline:

```text
Upload
  |
  v
Parse
  |
  v
Chunk
  |
  v
Embed
  |
  v
Vector Store
  |
  v
Project-Scoped Retrieval
  |
  v
AI Mentor
```

Strict isolation is required:

> Project A AI must not retrieve Project B documents.

This is both a functional and security requirement.

---

# 21. Student AI Mentor

The Student AI Mentor can help with:

- Project questions
- Technical questions
- Implementation guidance
- Architecture
- Tasks
- Milestones
- Documentation
- Risks
- Blueprint questions
- Uploaded files
- GitHub activity
- Current project state
- Learning questions
- Next recommended action

Source selection should depend on the question:

```text
Structured project question -> Database
Document question           -> RAG
GitHub question             -> GitHub data
Technical question          -> AI reasoning
Complex project question    -> Database + RAG + tools + reasoning
```

---

# 22. AI Action Confirmation

Normal conversation should not automatically mutate project state.

Example:

Student:
> I completed the authentication module.

AI:
> It looks like the Authentication task is complete. Would you like me to mark it as completed?

Only after explicit confirmation:

```text
Student Confirmation
        |
        v
Update Task
        |
        v
Recalculate Milestone
        |
        v
Recalculate Progress
        |
        v
Update Project State
```

A normal informational question such as:

> What is JWT?

should not change project state.

---

# 23. GitHub Integration

GitHub can optionally be connected to a project.

GrowFlow can use the repository for lightweight project monitoring:

- Commit count
- Recent commits
- Last meaningful activity
- Repository activity
- Development activity trends

V1 does not turn GrowFlow into a full GitHub management platform.

---

# 24. Student ↔ Mentor Communication

## Mentor Notes

Students can receive mentor notes associated with their project/group.

## Ask Mentor

Students can submit:

- Questions
- Problems
- Help requests
- Project issues

Request lifecycle:

```text
OPEN
  |
  v
IN_PROGRESS
  |
  v
RESOLVED
```

This connects directly to the Mentor-side Student Help functionality.

---

# 25. Activity Timeline

The project maintains an activity history.

Examples:

- Task completed
- Milestone completed
- Blueprint generated
- Document generated
- Document regenerated
- GitHub activity detected
- Risk identified
- Mentor note received
- Help request submitted
- Project profile changed
- Technology changed
- Project scope changed

This provides a clear history of project evolution.

---

# 26. Next Recommended Action

GrowFlow should help answer:

> What should I do next?

Example:

```text
NEXT ACTION

Complete JWT Authentication

Why:
2 of 3 authentication tasks are complete.

Estimated time:
4 hours

Related milestone:
Authentication Complete
```

This is an important AI-assisted execution feature.

---

# 27. Blocked Task / Help Trigger

Tasks support:

- TODO
- IN_PROGRESS
- BLOCKED
- COMPLETED

When a student marks a task as BLOCKED, GrowFlow can:

- Ask what is blocking them
- Suggest troubleshooting
- Search project documentation
- Use project RAG
- Analyze relevant risks
- Suggest next steps
- Suggest contacting the mentor

This creates a useful relationship between:

```text
Task -> AI -> Risk -> Mentor
```

---

# 28. Complete Student Architecture

```text
                         STUDENT
                            |
                            v
                    Authentication
                            |
                            v
                    Student Dashboard
                            |
              +-------------+-------------+
              |                           |
              v                           v
        Create Project              Mentor Project
              |                           |
              +-------------+-------------+
                            |
                            v
                  Initial Project Profile
                            |
                            v
                   Student Skill Level
                            |
                            v
                 15-Question Assessment
                    +-------+-------+
                    |               |
                10 Core         5 Dynamic
                Questions       Questions
                    |               |
                    +-------+-------+
                            |
                            v
                   Enriched Project Profile
                            |
                            v
                  Generate Project Blueprint
                            |
        +-------------------+--------------------+
        |                   |                    |
        v                   v                    v
 Project Profile      Technology Stack      Features &
                                            Specifications
        |
        +-- MVP Definition
        +-- Project Duration
        +-- Risk Documentation
        +-- README
        +-- Tasks & Milestones
                            |
                            v
                    Project Workspace
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
             RAG          Documents      GitHub
              |             |             |
              +-------------+-------------+
                            |
                            v
                       AI Mentor
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
       Project Help   Technical Help   State Guidance
                            |
                            v
                    Project Dashboard
                            |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
    Progress             Health              Next Action
       |                    |                    |
       v                    v                    v
     Tasks              Risks              Activity
       |
       v
   Milestones
       |
       v
   Mentor Communication
```

---

# 29. Final Student V1 Feature Boundary

| Area | Decision |
|---|---|
| Authentication | Keep |
| Student ID | Keep |
| Dashboard | Keep |
| Project creation | Keep |
| Mentor project selection | Keep |
| Q/A for own projects | Keep |
| Q/A for mentor projects | Keep — mandatory |
| 10 core questions | Keep |
| 5 dynamic project-specific questions | Add |
| AI-enriched profile | Keep |
| Traditional roadmap | Replace |
| Generate Project Blueprint | Core |
| Project Profile document | Core |
| Technology Stack document | Core |
| Features & Specifications document | Core |
| MVP Definition document | Core |
| Project Duration document | Core |
| Risk Documentation | Core |
| README | Core |
| Tasks & Milestones documentation | Core |
| Failed-generation recovery | Add |
| Retry impact/change check | Add |
| Resume unaffected generated documents | Add |
| Regenerate affected/all inconsistent documents | Add |
| Workspace | Keep |
| RAG | Keep |
| AI Mentor | Keep |
| Document viewing | Keep |
| Preview toggle | Keep |
| Code/Markdown toggle | Keep |
| Download | Keep |
| Full document editor | Remove |
| PDF editing | Remove |
| Project Dashboard | Keep |
| Health | Keep |
| Next Action | Add |
| Blocked Task | Add |
| Activity Timeline | Add |
| GitHub activity | Keep |
| Mentor Notes | Keep |
| Ask Mentor | Keep |
| Automatic state mutation from normal chat | Remove |
| Explicit AI action confirmation | Keep |
| AI Chat -> File Modification & Regeneration | Remove |

---

# 30. Explicitly Removed from Student V1

The following are deliberately outside the Student V1 boundary:

- Full Google Docs-style editor
- PDF editing
- Full document collaboration suite
- Arbitrary document-generation without defined purpose
- Automatic project-state changes from ordinary chat
- Manual phase selection
- Manual milestone completion when completion can be determined from tasks
- Full GitHub management
- GitHub issue/PR management
- CI/CD management
- Excessive personality/taste profiling
- Traditional roadmap as the primary generated artifact
- AI chat-based modification/regeneration of individual files

---

# 31. Final Student-Side Concept

```text
IDEA / MENTOR PROJECT
        |
        v
PROJECT PROFILE
        |
        v
15-QUESTION AI ASSESSMENT
(10 CORE + 5 DYNAMIC)
        |
        v
ENRICHED PROJECT UNDERSTANDING
        |
        v
GENERATE PROJECT BLUEPRINT
        |
        +-- Project Profile
        +-- Technology Stack
        +-- Features & Specifications
        +-- MVP Definition
        +-- Project Duration
        +-- Risk Documentation
        +-- README
        +-- Tasks & Milestones
        |
        v
PROJECT WORKSPACE
        |
        v
EXECUTION
        |
        v
TASKS -> MILESTONES -> PROGRESS
        |
        v
HEALTH + RISKS + GITHUB
        |
        v
AI MENTOR + RAG + NEXT ACTION
        |
        v
MENTOR COMMUNICATION
        |
        v
PROJECT COMPLETION
```

## Core Value Proposition

> **GrowFlow turns a student's project idea into a complete, structured, documented, executable project foundation and then helps the student actually build it.**

The generated documentation saves the student time by removing repetitive manual project-planning work while keeping the documentation aligned with the canonical project state.
