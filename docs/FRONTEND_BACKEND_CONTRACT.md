# GrowFlow — Frontend → Backend Contract Reference

## 1. Document Control

### 1.1 Purpose
This document serves as the single authoritative engineering contract and implementation reference for the GrowFlow backend engineering team. It describes the complete, frozen frontend interface contract—including routes, typed API client functions, HTTP methods, request payloads, response data models, authentication semantics, role-based authorization rules, Server-Sent Events (SSE) lifecycles, background execution states, and error envelopes.

### 1.2 Status & Source of Truth
- **Frontend Status:** `COMPLETE + FROZEN` (Officially sealed following the Phase 9 Batch 7 Final Verification & Freeze Audit with 0 blocking defects, 0 type errors, and 513/513 passing test suites).
- **Primary Source of Truth:** The active frontend codebase located under `frontend/src/`, specifically:
  - Router definition: `frontend/src/router/index.tsx`
  - API client & HTTP transport: `frontend/src/lib/api/client.ts`
  - TypeScript contract schemas: `frontend/src/lib/api/types/*.ts`
  - Authentication engine: `frontend/src/auth/AuthProvider.tsx`, `ProtectedRoute.tsx`, `returnTo.ts`
  - Shared & Layout components: `frontend/src/components/`, `frontend/src/layouts/`
  - Workspace views: `frontend/src/pages/Student/`, `frontend/src/pages/Mentor/`, `frontend/src/pages/Admin/`
  - Client state & telemetry hooks: `frontend/src/hooks/`
- **Secondary Reference:** Prior Phase 8 / Phase 9 audit reports and backend route controllers (`backend/app/api/routes/*.py`).

### 1.3 Scope & Intended Audience
- **Scope:** Complete end-to-end interface definition encompassing all 127 canonical frontend routes, 149 domain-specific typed API methods, 16 domain type modules, 8 approved notification event types, 10 system state primitives, and 29 Admin governance views.
- **Intended Audience:** Backend engineers, database architects, AI system developers, QA engineers, and infrastructure operators.

### 1.4 Frontend Freeze Invariant
The frontend implementation is **STRICTLY FROZEN**. No backend requirement may arbitrarily alter, rename, omit, or restructure frontend contract expectations without formal architectural review. Backend application services and controllers must adapt to the schemas, HTTP semantics, query conventions, and envelope structures documented herein.

### 1.5 Contract Confidence Classification
Every contract element in this document is labeled with one of the following evidence-based confidence ratings:
1. `VERIFIED`: Supported by active code in both `frontend/src/` and `backend/app/` and confirmed during regression audits.
2. `IMPLEMENTED`: Fully present and active in the frontend client and consuming views; backend implementation is established.
3. `REQUIRES VERIFICATION`: Frontend demonstrates clear consumption; backend persistence or domain behavior requires verification during backend development.
4. `CONTRACT CLARIFICATION`: A minor divergence (such as query filtering or optional ID property) corrected and documented during Batch 3.
5. `MISSING BACKEND SUPPORT`: An established frontend expectation where dedicated backend route or handler is not yet implemented.

---

## 2. System Architecture from the Frontend Perspective

### 2.1 Client-Server Topology

```text
  +-------------------------------------------------------------------------+
  |                        Browser Client (React 19)                        |
  |  - Pure Vanilla CSS Design System (Custom Tokens, Dark/Light Palettes)   |
  |  - React Router DOM v7 Routing with Safe returnTo Deep-Link Guards      |
  |  - Supabase Auth SDK (JWT Token Lifecycle & Session Listener)           |
  |  - Resilient State Stores & Reactive Hooks (useNotifications, useSearch)|
  +-------------------------------------------------------------------------+
                                      |
                                      | 1. Bearer JWT (Authorization Header)
                                      | 2. Native EventSource with Query Token (?token=)
                                      v
  +-------------------------------------------------------------------------+
  |                     GrowFlow Canonical API Client                       |
  |  - File: frontend/src/lib/api/client.ts                                 |
  |  - Base URL: VITE_API_BASE_URL (normalized without trailing slash)       |
  |  - Automatic Bearer Injection from Supabase Session                     |
  |  - Canonical Envelope Unwrapper: { success: true, data: T }             |
  |  - Normalized ApiClientError Model (401, 403, 404, 422, 5xx, Network)   |
  +-------------------------------------------------------------------------+
                                      |
                                      | REST / JSON / Server-Sent Events
                                      v
  +-------------------------------------------------------------------------+
  |                        FastAPI Backend Gateway                          |
  |  - Authentication Middleware & verify_account_active Guard              |
  |  - Role Dependencies (RequireStudent, RequireMentor, RequireAdmin)      |
  |  - Standard Envelope Generator (success_response, error_response)       |
  |  - CORS & Rate Limiting (429) & Exception Handlers                     |
  +-------------------------------------------------------------------------+
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
  +-------------------------------+         +-------------------------------+
  |     Domain Services & DB      |         |  AI Orchestration & Outbox   |
  |  - Student, Mentor, Admin     |         |  - LangGraph Multi-Agent Flow |
  |  - Projects & Lifecycles      |         |  - AI Provider Gateway        |
  |  - Assessment & Blueprints    |         |  - Background Job Queue       |
  |  - Tasks, Milestones, Risks   |         |  - SSE Event Stream Engine    |
  |  - PostgreSQL Persistence     |         |  - Transactional Outbox Worker|
  +-------------------------------+         +-------------------------------+
```

### 2.2 Strict Architectural Separation of Concerns

| Concern | Frontend Responsibilities | Backend Responsibilities |
|---|---|---|
| **Authentication** | Collect credentials, manage Supabase session storage, attach Bearer token to API requests, sanitize `returnTo` redirects. | Cryptographic verification of JWT, extract user identity, enforce active account status (`ACTIVE` vs `SUSPENDED`/`INACTIVE`). |
| **Authorization & Roles** | Guard routes via `ProtectedRoute` for calm UI feedback and workplace routing. | **Strictly Authoritative**. Enforce row-level ownership, group membership, supervision bounds, and admin governance. |
| **AI Generation** | Render progress bars, trigger generation/retry jobs, listen to SSE streams, surface QA scores and markdown reports. | **Strictly Server-Side**. Model selection, LLM provider routing, prompt formatting, LangGraph execution, QA evaluation, database commits. **Frontend NEVER contacts AI providers directly.** |
| **Lifecycle Transitions** | Dispatch transition intents, display confirmation modals, update UI indicators. | Validate state machine invariants (e.g. Stage 3 approved before Planning), persist transition history, emit domain events. |
| **Search & Discovery** | Keystroke debouncing (300ms), Ctrl+K modal presentation, query cancellation on rapid typing. | Role-scoped SQL query filtering, relevance scoring, bounded pagination (max 50). |
| **Notifications** | Poll unread counts, render dropdown badges, trigger optimistic read updates, handle SSE events. | Domain event subscription, recipient resolution based on the 8 canonical event types, persist notifications table. |
| **Error Handling** | Map HTTP codes to UX feedback (banners, modals, field errors), gracefully degrade to polling if SSE drops. | Emit canonical error envelope `{ success: false, error: { code, message, details } }` with standardized machine codes. |

---

## 3. Frontend Route Inventory

The frozen frontend establishes 127 canonical surfaces partitioned across 7 structural categories:
1. **PUBLIC (P01–P05):** Unauthenticated public pages
2. **AUTH (A01–A09):** Authentication, registration, password recovery, and admin entry
3. **SHARED (X01–X05):** Cross-role utility and profile surfaces
4. **STUDENT / BUILD (S01–S33):** Core student workspace and project lifecycle
5. **MENTOR / SUPERVISE (M01–M36):** Supervision, group management, and definition authoring
6. **ADMIN / GOVERN (AD01–AD29):** Platform governance, AI observatory, health, and audit
7. **SYSTEM (SYS01–SYS10):** Universal system and fallback states

### 3.1 Public Routes (P01–P05)

| Page ID | Page Name | Actual Frontend Route | Role | Auth Required | Backend Dependency | API Calls Used | Mutations | Primary Response Data | Deep-Link / Notes |
|---|---|---|---|---|---|---|---|---|---|
| **P01** | Landing | `/` | Public | None | None | None | None | Marketing copy, static hero | Public entry point |
| **P02** | Features | `/features` | Public | None | None | None | None | Feature catalog | Direct navigation |
| **P03** | Documentation | `/documentation` | Public | None | None | None | None | Architectural docs | Direct navigation |
| **P04** | Contact | `/contact` | Public | None | Contact Service | `submitContact` (`POST /api/v1/contact`) | Submits inquiry | `{ success: true, message: string }` | Form submission with validation |
| **P05** | Architecture Showcase | `/showcase` | Public | None | None | None | None | Showcase architectural schemas | Public project demonstration |

### 3.2 Authentication Routes (A01–A09)

| Page ID | Page Name | Actual Frontend Route | Role | Auth Required | Backend Dependency | API Calls Used | Mutations | Primary Response Data | Deep-Link / Notes |
|---|---|---|---|---|---|---|---|---|---|
| **A01** | Student Sign In | `/auth/student/sign-in` | Public (Auth) | None | Supabase Auth + `/auth/me` | `signInWithPassword`, `getCurrentUser` | Authenticates session | `Session`, `CurrentUserIdentity` | Respects sanitized `?returnTo=` |
| **A02** | Student Registration | `/auth/student/register` | Public (Auth) | None | Supabase Auth | `signUp` | Creates Supabase auth account | `Session` or email confirmation | Role defaulted to STUDENT |
| **A03** | Student Password Recovery | `/auth/student/recover` | Public (Auth) | None | Supabase Auth | `resetPasswordForEmail` | Sends recovery link | `{ error: null }` | Password reset flow |
| **A04** | Mentor Sign In | `/auth/mentor/sign-in` | Public (Auth) | None | Supabase Auth + `/auth/me` | `signInWithPassword`, `getCurrentUser` | Authenticates session | `Session`, `CurrentUserIdentity` | Default destination: `/mentor/overview` |
| **A05** | Mentor Registration | `/auth/mentor/register` | Public (Auth) | None | Supabase Auth | `signUp` | Creates mentor candidate user | `Session` or email confirmation | Role assigned via metadata |
| **A06** | Mentor Password Recovery | `/auth/mentor/recover` | Public (Auth) | None | Supabase Auth | `resetPasswordForEmail` | Sends recovery link | `{ error: null }` | Mentor reset flow |
| **A07** | Student Onboarding | Handled Inline | STUDENT | Session Required | Student Profile API | `getStudentProfile`, `updateStudentProfile` | Completes initial profile setup | `StudentProfile` | Integrated into first project creation (`/student/projects/new`) |
| **A08** | Mentor Onboarding | Handled Inline | MENTOR | Session Required | Mentor Profile API | `getMentorProfile`, `updateMentorProfile` | Completes mentor bio/specialization | `MentorProfileResponse` | Integrated into initial group setup (`/mentor/groups/new`) |
| **A09** | Protected Admin Entry | `/auth/admin/sign-in` | Public (Auth) | None | Supabase Auth + `/auth/me` | `signInWithPassword`, `getCurrentUser` | Authenticates admin | `Session`, `CurrentUserIdentity` (Role=ADMIN) | Strict admin login; no public self-registration |

### 3.3 Shared Platform Routes & Surfaces (X01–X05)

| Page ID | Surface Name | Actual Frontend Route / Trigger | Role | Auth Required | Backend Dependency | API Calls Used | Mutations | Primary Response Data | Deep-Link / Notes |
|---|---|---|---|---|---|---|---|---|---|
| **X01** | Global Search | Modal / `Ctrl+K` in Header | Any Auth | Active Session | Search Service | `searchWorkspace` (`GET /api/v1/search`) | None | `SearchResponseData` (results with optional `id`) | Keyboard shortcut wired across all workspace headers |
| **X02** | Notifications | Popover in Header | Any Auth | Active Session | Notifications API | `getNotifications`, `getUnreadNotificationCount`, `markNotificationRead`, `markAllNotificationsRead` | Marks notifications as read | `NotificationItem[]`, `unread_count` | Scoped to authenticated user recipient |
| **X03** | User Profile | `/profile` (Student), `/mentor/profile`, `/admin/profile` | Per-Role | Active Session | User Profile Services | `getStudentProfile`, `getMentorProfile`, `getCurrentUser` | Updates profile fields | `StudentProfile`, `MentorProfileResponse` | Role-partitioned URLs |
| **X04** | User Settings | `/settings`, `/mentor/settings`, `/admin/settings` | Per-Role | Active Session | Preferences API | `getUserPreferences`, `updateUserPreferences` | Updates notification/timezone settings | `UserPreferencesResponse` | Consistent across roles |
| **X05** | Share | Inline Action | Student/Mentor | Active Session | None | Clipboard API | Copies share link | Native URL | Implemented as inline project URL copy |

### 3.4 Student Workspace Routes — BUILD (S01–S33)

All student workspace routes require `role === 'STUDENT'` and an `ACTIVE` account status. Handled by `AuthenticatedLayout` and `ProtectedRoute`.

| Page ID | Page Name | Actual Route | Backend Dependency | API Calls Used | Mutations | Primary Response Data | Deep-Link / Notes |
|---|---|---|---|---|---|---|---|
| **S01** | Dashboard | `/student/dashboard` | Project, Groups, Activity | `getProjects`, `getStudentGroups`, `getStudentProfile` | None | `ProjectResponse[]`, `GroupResponse[]` | Workspace home |
| **S02** | Projects | `/student/projects` | Project Service | `getProjects` | None | `ProjectResponse[]` | Filterable by phase & health |
| **S03** | Create Your Own Project | `/student/projects/new` | Project Service | `createProject` | Creates project instance | `ProjectResponse` | Redirects to S15/S07 upon creation |
| **S04** | Mentor Project Catalog | `/student/projects/mentor-catalog` | Definition Service | `getMentorProjectCatalog` | None | `ProjectDefinitionCatalogItem[]` | Discovers mentor templates |
| **S05** | Catalog Detail / Selection | `/student/projects/mentor-catalog/:definitionId` | Definition Service | `getMentorProjectDefinition`, `selectMentorProject` | Instantiates linked project | `ProjectResponse` | Instantiates linked project |
| **S06** | Project Information / Profile | `/student/projects/:projectId/profile` | Project Service | `getProjectOverview`, `updateProject` | Updates project metadata | `ProjectOverviewResponse` | Profile editing |
| **S07** | Assessment Intro | `/student/projects/:projectId/assessment` (`INTRO`) | Assessment Service | `getAssessmentStatus`, `startAssessment` | Starts assessment session | `AssessmentStartResponse` | Multi-state assessment view |
| **S08** | Assessment Question | Same route (`QUESTION`) | Assessment Service | `getAssessmentQuestion`, `submitAssessmentAnswer` | Submits answer | `AssessmentAnswerSubmitResponse` | Questions 1..15 |
| **S09** | Adaptive Assessment | Same route (`QUESTION`) | Assessment Service | `getAssessmentQuestion`, `submitAssessmentAnswer` | Submits dynamic answer | `AssessmentQuestion` (`is_adaptive=true`) | Questions 11..15 |
| **S10** | Assessment Completion | Same route (`COMPLETION`) | Assessment Service | `completeAssessment` | Finalizes assessment | `AssessmentResultResponse` | Transition gate to results |
| **S11** | Assessment Result | Same route (`RESULT`) | Assessment Service | `getAssessmentResult` | None | `AssessmentResultResponse` | Displays readiness tier & radar |
| **S12** | Blueprint Generation | `/student/projects/:projectId/blueprint` | Blueprint SSE / Job | `getBlueprintStatus`, `startBlueprintGeneration`, `subscribeBlueprintEvents` | Starts generation job | `BlueprintStatusResponse` | Real-time SSE streaming |
| **S13** | Blueprint Failure / Recovery | Same route (`FAILED`) | Blueprint Service | `retryBlueprintGeneration` | Retries failed synthesis | `BlueprintStatusResponse` | Targeted or full retry |
| **S14** | Blueprint QA / Approval | Same route (`REVIEW`) | Blueprint Service | `approveBlueprint` | Approves blueprint & unlocks planning | `BlueprintApprovalResponse` | Locks Stage 3 blueprint |
| **S15** | Project Overview | `/student/projects/:projectId/overview` | Project & Execution | `getProjectOverview` | None | `ProjectOverviewResponse` | Canonical project overview |
| **S16** | Blueprint Workspace | `/student/projects/:projectId/blueprint/workspace` | Blueprint Service | `getBlueprintContent` | None | `BlueprintContentResponse` (`content` dict) | 10 canonical sections |
| **S17** | Blueprint Document Viewer | `/student/projects/:projectId/blueprint/documents[/:key]` | Blueprint Service | `getBlueprintDocument`, `downloadBlueprintDocument` | None | `BlueprintDocumentDetail` | Markdown rendering & raw download |
| **S18** | Tasks | `/student/projects/:projectId/tasks` | Execution Service | `getTasks`, `createTask` | Creates new task | `TaskResponse[]` | Filterable task board |
| **S19** | Task Detail | `/student/projects/:projectId/tasks/:taskId` | Execution Service | `getTask`, `updateTask`, `deleteTask` | Updates/deletes task | `TaskResponse` | Granular task properties |
| **S20** | Milestones | `/student/projects/:projectId/milestones` | Execution Service | `getMilestones`, `createMilestone` | Creates milestone | `MilestoneResponse[]` | Gate deliverable milestones |
| **S21** | Milestone Detail | `/student/projects/:projectId/milestones/:mId` | Execution Service | `getMilestone`, `updateMilestone` | Updates milestone | `MilestoneResponse` | Linked tasks and progress |
| **S22** | Risks | `/student/projects/:projectId/risks` | Execution Service | `getRisks`, `createRisk` | Creates risk | `RiskResponse[]` | Severity & probability matrix |
| **S23** | Risk Detail | `/student/projects/:projectId/risks/:riskId` | Execution Service | `getRisk`, `updateRisk`, `deleteRisk` | Updates/deletes risk | `RiskResponse` | Mitigation strategy tracking |
| **S24** | Roadmap | `/student/projects/:projectId/roadmap` | Execution Service | `getRoadmap` | None | `RoadmapResponse` | Milestones & grouped tasks |
| **S25** | Documents | `/student/projects/:projectId/documents` | Execution Service | `getDocuments`, `createDocument` | Uploads/creates doc | `DocumentResponse[]` | Project document repository |
| **S26** | Document Detail | `/student/projects/:projectId/documents/:docId` | Execution Service | `getDocument`, `updateDocument`, `downloadDocument` | Updates doc | `DocumentResponse` | Markdown document viewer |
| **S27** | GitHub | `/student/projects/:projectId/github` | Extensions Service | `getGitHubIntegration`, `connectGitHub`, `syncGitHub`, `disconnectGitHub` | Connects/syncs repo | `GitHubIntegrationResponse` | Read-only commit observation |
| **S28** | Activity | `/student/projects/:projectId/activity` | Extensions Service | `getProjectActivity` | None | `ActivityItemResponse[]` | Paginated domain events |
| **S29** | AI Mentor | `/student/projects/:projectId/ai-mentor` | Extensions / AI | `getAIMentorHistory`, `sendAIMentorMessage`, `executeAIOperation` | Sends chat / executes action | `AIMentorConversationResponse` | Scoped AI assistant |
| **S30** | Help Requests | `/student/projects/:projectId/help-requests` | Extensions Service | `getHelpRequests`, `createHelpRequest`, `getHelpRequest` | Creates help request | `HelpRequestResponse[]` | Student help request queue |
| **S31** | Mentor Feedback | `/student/projects/:projectId/mentor-feedback` | Extensions Service | `getMentorNotes`, `acknowledgeMentorNote` | Acknowledges note | `MentorNoteResponse[]` | Feedback from supervising mentor |
| **S32** | Project Changes | `/student/projects/:projectId/changes` | Extensions / AI | `getProjectChanges`, `analyzeProjectChange` | Analyzes scope change | `ProjectChangeResponse[]` | Impact analysis review |
| **S33** | Change Detail & Result | `/student/projects/:projectId/changes/:cId` | Extensions / AI | `getProjectChange`, `confirmProjectChange`, `getBlueprintVersions` | Confirms regeneration | `ProjectChangeResponse`, `BlueprintVersionResponse` | Candidate version promotion |

### 3.5 Mentor Workspace Routes — SUPERVISE (M01–M36)

All mentor workspace routes require `role === 'MENTOR'` and an `ACTIVE` account status. Handled by `MentorLayout` and `ProtectedRoute`.

| Page ID | Page Name | Actual Route | Backend Dependency | API Calls Used | Mutations | Primary Response Data | Notes |
|---|---|---|---|---|---|---|---|
| **M01** | Mentor Overview | `/mentor/overview` | Mentor Service | `getMentorOverview` | None | `MentorOverviewResponse` | Portfolio KPIs & active groups |
| **M02** | Groups Directory | `/mentor/groups` | Groups Service | `getMentorGroups` | None | `GroupResponse[]` | Supervised cohorts |
| **M03** | Group Creation | `/mentor/groups/new` | Groups Service | `createMentorGroup` | Creates cohort & join code | `GroupResponse` | Generates unique join code |
| **M04** | Group Workspace | `/mentor/groups/:groupId` | Groups Service | `getMentorGroup` | None | `GroupResponse` | Cohort hub |
| **M05** | Group Students | `/mentor/groups/:groupId/students` | Groups Service | `getGroupStudents` | None | `GroupStudentResponse[]` | Enrolled students |
| **M06** | Group Projects | `/mentor/groups/:groupId/projects` | Groups Service | `getGroupProjects` | None | `ProjectResponse[]` | Projects in cohort |
| **M07** | Group At Risk | `/mentor/groups/:groupId/at-risk` | Mentors Service | `getMentorAtRiskProjects` (`group_id`) | None | `MentorProjectInstanceSummary[]` | Filtered at-risk cohort projects |
| **M08** | Group Activity | `/mentor/groups/:groupId/activity` | Groups Service | `getGroupActivity` | None | `ActivityItemResponse[]` | Cohort domain audit events |
| **M09** | Group AI Mentor | `/mentor/groups/:groupId/ai` | Groups / AI | `getGroupAIStatus`, `sendGroupAIMessage` | Dispatches group prompt | `MentorAIChatResponse` | Scoped cohort AI assistant |
| **M10** | Students Directory | `/mentor/students` | Mentor Service | `getMentorStudents` | None | `MentorStudentSummary[]` | Supervised student directory |
| **M11** | Student Detail | `/mentor/students/:studentId` | Mentor Service | `getMentorStudent` | None | `MentorStudentDetail` | Student profile & instances |
| **M12** | Student Projects | `/mentor/students/:studentId/projects` | Mentor Service | `getMentorStudentProjects` | None | `MentorProjectInstanceSummary[]` | Student-specific project portfolio |
| **M13** | Student Activity | `/mentor/students/:studentId/activity` | Mentor Service | `getMentorStudentActivity` | None | `ActivityItemResponse[]` | Student-specific activity timeline |
| **M14** | Student Mentor Notes | Managed per instance | Extensions Service | `getMentorProjectNotes`, `createMentorNote` | Posts note | `MentorNoteItem[]` | Handled via project instance notes |
| **M15** | Student Help Requests | Managed via M33 | Mentor Service | `getMentorHelpRequests` | None | `MentorHelpRequestSummary[]` | Filterable by student/group |
| **M16** | Projects Directory | `/mentor/projects` | Definition Service | `getMentorDefinitions` | None | `ProjectDefinition[]` | Project definitions authored |
| **M17** | Project Definitions | `/mentor/projects` | Definition Service | `getMentorDefinitions` | None | `ProjectDefinition[]` | Same as M16 |
| **M18** | Definition Detail | `/mentor/projects/:definitionId` | Definition Service | `getMentorDefinition`, `getDefinitionVersions` | None | `ProjectDefinition` | Definition versions & assignments |
| **M19** | Create Definition | `/mentor/projects/new` | Definition Service | `createMentorDefinition` | Creates project definition | `ProjectDefinition` | Authoring project definition |
| **M20** | Edit Definition | `/mentor/projects/:definitionId/edit` | Definition Service | `getMentorDefinition`, `updateMentorDefinition` | Updates definition | `ProjectDefinition` | Creates new version if published |
| **M21** | Definition Assignment | `/mentor/projects/:definitionId/assign` | Definition Service | `assignMentorDefinition` | Assigns to student | `{ success: true }` | Direct student assignment |
| **M22** | Project Instances | `/mentor/project-instances` | Mentor Service | `getMentorProjectInstances` | None | `MentorProjectInstanceSummary[]` | All supervised instances grid |
| **M23** | Instance Detail | `/mentor/project-instances/:projectId` | Mentor Service | `getMentorProjectInstance` | None | `MentorProjectInstanceDetail` | Single instance inspection |
| **M24** | Instance Blueprint | `/mentor/project-instances/:projectId/blueprint` | Mentor Service | `getMentorInstanceBlueprint` | None | `MentorBlueprintInspectionResponse` | Inspects blueprint content & QA |
| **M25** | Instance Tasks | `/mentor/project-instances/:projectId/tasks` | Mentor Service | `getMentorInstanceTasks` | None | `TaskResponse[]` | Read-only inspection of tasks |
| **M26** | Instance Milestones | `/mentor/project-instances/:projectId/milestones` | Mentor Service | `getMentorInstanceMilestones` | None | `MilestoneResponse[]` | Read-only inspection of milestones |
| **M27** | Instance Risks | `/mentor/project-instances/:projectId/risks` | Mentor Service | `getMentorInstanceRisks` | None | `RiskResponse[]` | Read-only inspection of risks |
| **M28** | Instance Documents | `/mentor/project-instances/:projectId/documents` | Mentor Service | `getMentorInstanceDocuments` | None | `DocumentResponse[]` | Read-only inspection of documents |
| **M29** | Instance GitHub | `/mentor/project-instances/:projectId/github` | Mentor Service | `getMentorInstanceGitHub` | None | `GitHubIntegrationResponse` | Read-only commit observation |
| **M30** | Instance Activity | `/mentor/project-instances/:projectId/activity` | Mentor Service | `getMentorInstanceActivity` | None | `ActivityItemResponse[]` | Project audit event trail |
| **M31** | At Risk Directory | `/mentor/at-risk` | Mentor Service | `getMentorAtRiskProjects` | None | `MentorProjectInstanceSummary[]` | Supervised projects with warning/critical health |
| **M32** | At Risk Detail | `/mentor/at-risk/:projectId` | Mentor Service | `getMentorAtRiskProject` | None | `MentorProjectInstanceDetail` | Diagnostic deep dive |
| **M33** | Mentor Help Requests | `/mentor/help-requests` | Mentor Service | `getMentorHelpRequests`, `getMentorHelpRequest`, `respondMentorHelpRequest` | Submits response | `MentorHelpRequestSummary[]` | Resolves student blockers |
| **M34** | Mentor Notes | Managed per instance | Mentor Service | `createMentorNote`, `getMentorProjectNotes` | Posts note | `MentorNoteItem` | Per-project instance notes |
| **M35** | Mentor Activity | `/mentor/activity` | Mentor Service | `getMentorPortfolioActivity` | None | `ActivityItemResponse[]` | Portfolio-wide activity stream |
| **M36** | Mentor AI | `/mentor/ai` | Mentor / AI | `getMentorAIStatus`, `sendMentorAIMessage` | Dispatches prompt | `MentorAIChatResponse` | Portfolio supervision AI assistant |

### 3.6 Admin Workspace Routes — GOVERN (AD01–AD29)

All admin routes require `role === 'ADMIN'` and an `ACTIVE` account status. Handled by `AdminLayout` and `ProtectedRoute`.

| Page ID | Page Name | Actual Route | Backend Dependency | API Calls Used | Primary Response Data | Notes |
|---|---|---|---|---|---|---|
| **AD01** | Overview | `/admin/overview` | Admin Service | `getAdminOverview` | `AdminOverviewResponse` | Platform counters & KPIs |
| **AD02** | Mentor Directory | `/admin/mentors` | Admin Service | `getAdminMentors` | `AdminMentorSummary[]` | Filterable by search & status |
| **AD03** | Mentor Detail | `/admin/mentors/:mentorId` | Admin Service | `getAdminMentor` | `AdminMentorDetail` | Cohorts, students, bio |
| **AD04** | Student Directory | `/admin/students` | Admin Service | `getAdminStudents` | `AdminStudentSummary[]` | Filterable by track & status |
| **AD05** | Student Detail | `/admin/students/:studentId` | Admin Service | `getAdminStudent` | `AdminStudentDetail` | Projects, technologies, cohorts |
| **AD06** | Groups Directory | `/admin/groups` | Admin Service | `getAdminGroups` | `AdminGroupSummary[]` | Cohorts across all mentors |
| **AD07** | Group Detail | `/admin/groups/:groupId` | Admin Service | `getAdminGroup` | `AdminGroupDetail` | Members, projects, mentor link |
| **AD08** | Projects Governance | `/admin/projects` | Admin Service | `getAdminProjects` | `AdminProjectSummary[]` | Central project instance register |
| **AD09** | Definition Monitoring | `/admin/definitions` | Admin Service | `getAdminDefinitions` | `AdminProjectDefinitionSummary[]` | Platform templates monitoring |
| **AD10** | Instance Monitoring | `/admin/instances` | Admin Service | `getAdminInstancesMonitoring` | `AdminInstanceMonitoringResponse` | Instance summary & health counts |
| **AD11** | AI Observatory | `/admin/ai` | Admin / AI Gateway | `getAdminAIObservatory` | `AdminAIObservatoryResponse` | Gateway posture, active jobs, KPIs |
| **AD12** | AI Usage | `/admin/ai/usage` | Admin / AI Gateway | `getAdminAIUsage` | `AdminAIUsageResponse` | Trends, volume, capabilities |
| **AD13** | Agent Executions | `/admin/ai/executions` | Admin / AI Gateway | `getAdminAIExecutions` | `AdminAIExecutionsResponse` | Filterable background jobs list |
| **AD14** | AI Trace Detail | `/admin/ai/executions/:eId` | Admin / AI Gateway | `getAdminAITraceDetail` | `AdminAITraceDetailResponse` | Pipeline stages, QA scores, telemetry |
| **AD15** | AI Quality | `/admin/ai/quality` | Admin / AI Gateway | `getAdminAIQuality` | `AdminAIQualityResponse` | QA pass rate, score distribution |
| **AD16** | Cost & Usage | `/admin/ai/cost` | Admin / AI Gateway | `getAdminAICost` | `AdminAICostResponse` | Model usage & telemetry posture |
| **AD17** | Cost Breakdown | `/admin/ai/cost/:dimension` | Admin / AI Gateway | `getAdminAICostDimension` | `AdminAICostDimensionResponse` | Dimension breakdown |
| **AD18** | API Key Pool | `/admin/ai/keys` | Admin / AI Gateway | `getAdminAIKeys` | `AdminAIKeysResponse` | Rotation strategy & key slots |
| **AD19** | System Health | `/admin/system-health` | Admin / Health | `getAdminSystemHealth` | `AdminSystemHealthResponse` | Subsystems, outbox queue, DB pool |
| **AD20** | Component Detail | `/admin/system-health/:cId` | Admin / Health | `getAdminComponentDetail` | `AdminSubsystemDetail` | Diagnostics & failure logs |
| **AD21** | Documents & RAG | `/admin/documents` | Admin / RAG | `getAdminDocuments` | `AdminDocumentsResponse` | Generated docs & sizes |
| **AD22** | RAG Monitoring | `/admin/documents/rag` | Admin / RAG | `getAdminRAGDiagnostics` | `AdminRAGDiagnostics` | Vector store, embeddings, chunks |
| **AD23** | Document Generation | `/admin/documents/generation` | Admin / Document | `getAdminGenerationJobs` | `AdminGenerationJobsResponse` | Doc generation jobs queue |
| **AD24** | Security Overview | `/admin/security` | Admin / Security | `getAdminSecurityOverview` | `AdminSecurityOverview` | User postures, outbox failures |
| **AD25** | Audit Log | `/admin/security/audit` | Admin / Security | `getAdminAuditLog` | `AdminAuditLogResponse` | Paginated audit event trail |
| **AD26** | Investigations | `/admin/security/investigations` | Admin / Security | `getAdminInvestigations` | `AdminInvestigationOverviewResponse` | Flagged security resources |
| **AD27** | Investigation Detail | `/admin/security/investigations/:iId` | Admin / Security | `getAdminInvestigationDetail` | Resource detail | Deep inspection of flagged entity |
| **AD28** | Platform Analytics | `/admin/analytics` | Admin / Analytics | `getAdminAnalytics` | `AdminPlatformAnalyticsResponse` | Platform distributions |
| **AD29** | Analytics Detail | `/admin/analytics/:dim` | Admin / Analytics | `getAdminAnalyticsDimension` | `AdminAnalyticsDimensionDetail` | Detailed dimension breakdowns |

### 3.7 System & Error State Surfaces (SYS01–SYS10)

| ID | State Name | Actual Frontend Representation | Trigger Condition | Backend Implication | Recovery / Navigation |
|---|---|---|---|---|---|
| **SYS01** | Not Found | Route `/404` and wildcard `*` | Unmatched client route or API 404 response | Return standard 404 envelope for non-existent entities | Button returning to user dashboard |
| **SYS02** | Forbidden | Route `/403` and inline `ForbiddenView` | User role mismatch or cross-tenant boundary breach | Return HTTP 403 with machine-readable error code | Switch workspace or return to authorized role |
| **SYS03** | Authentication Required | Route `/401` or redirect to login | Unauthenticated or expired Supabase JWT session | Return HTTP 401 with code `AUTH_MISSING_TOKEN` | Redirect to login preserving safe `returnTo` |
| **SYS04** | Account Status | Route `/account-status` | Backend reports `SUSPENDED` or `INACTIVE` status | Return HTTP 403 with `AUTH_ACCOUNT_SUSPENDED` or `AUTH_ACCOUNT_INACTIVE` | Contact administrator |
| **SYS05** | Error Boundary | Root/Workspace `ErrorBoundary` | Unhandled runtime exception | None (client crash shield) | "Reload Application" button |
| **SYS06** | Network Error | Inline `NetworkErrorState` | Failed fetch / fetch network exception (`status === 0`) | Server unreachable or CORS blocked | "Retry Request" trigger |
| **SYS07** | AI Unavailable | Inline `AIServiceUnavailableNotice` | LLM Gateway returns 503 or `ai_available === false` | Provider gateway timeout or rate exhaustion | Graceful non-blocking degradation |
| **SYS08** | AI Execution Failed | Inline `AIExecutionFailedState` | Blueprint or synthesis job status reaches `FAILED` | Emit error details and preserve previous version | "Retry Generation" action |
| **SYS09** | AI Execution Progress | Inline `AIExecutionProgressState` | Blueprint or job status is `GENERATING` / `RUNNING` | Stream SSE progress updates | Real-time progress bar |
| **SYS10** | RAG Processing | Inline `RAGProcessingState` | Vector indexing in progress | Asynchronous chunking/embedding | Non-blocking background notice |


## 4. API Client Master Inventory

The GrowFlow centralized API client (`frontend/src/lib/api/client.ts`) defines **149 pure, typed domain functions** and 1 core HTTP transport engine (`apiFetch<T>`). Every function automatically injects the active Supabase Bearer JWT token (with an explicit query parameter exception for SSE streams), validates the response, unwraps the canonical envelope `{ success: true, message: string, data: T }`, and maps failures to a normalized `ApiClientError`.

### 4.1 Master Inventory Table

| # | Frontend Method | HTTP | Backend Path | Request Body | Response Type | Role | Consumer Surface | Operation | Error States |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `getCurrentUser` | GET | `/api/v1/auth/me` | None | `CurrentUserIdentity` | Any Auth | AuthProvider, Guards | Read | 401, 403 |
| 2 | `getStudentProfile` | GET | `/api/v1/students/me` | None | `StudentProfile` | STUDENT | Profile, Dashboard | Read | 401, 403, 404 |
| 3 | `updateStudentProfile` | PATCH | `/api/v1/students/me` | `StudentProfileUpdatePayload` | `StudentProfile` | STUDENT | Profile (X03) | Mutation | 400, 401, 403, 422 |
| 4 | `getProjects` | GET | `/api/v1/projects` | None | `ProjectResponse[]` | STUDENT | Dashboard (S01), Projects (S02) | Read | 401, 403 |
| 5 | `getProject` | GET | `/api/v1/projects/:id` | None | `ProjectResponse` | STUDENT | Project Views (S06–S33) | Read | 401, 403, 404 |
| 6 | `getProjectOverview` | GET | `/api/v1/projects/:id/overview` | None | `ProjectOverviewResponse` | STUDENT | Overview (S15), Profile (S06) | Read | 401, 403, 404 |
| 7 | `createProject` | POST | `/api/v1/projects` | `ProjectCreatePayload` | `ProjectResponse` | STUDENT | Create Project (S03) | Mutation | 400, 401, 403, 422 |
| 8 | `updateProject` | PATCH | `/api/v1/projects/:id` | `ProjectUpdatePayload` | `ProjectResponse` | STUDENT | Project Profile (S06) | Mutation | 400, 401, 403, 404, 422 |
| 9 | `transitionProjectPhase` | POST | `/api/v1/projects/:id/phase` | `ProjectPhaseTransitionPayload` | `ProjectResponse` | STUDENT | Overview (S15) | Mutation | 400, 401, 403, 404, 422 |
| 10 | `updateProjectHealth` | POST | `/api/v1/projects/:id/health` | `ProjectHealthUpdatePayload` | `ProjectResponse` | STUDENT | Overview (S15) | Mutation | 400, 401, 403, 404, 422 |
| 11 | `getMentorProjectCatalog` | GET | `/api/v1/project-definitions/catalog` | None | `ProjectDefinitionCatalogItem[]` | STUDENT | Catalog (S04) | Read | 401, 403 |
| 12 | `getMentorProjectDefinition` | GET | `/api/v1/project-definitions/catalog/:id` | None | `ProjectDefinitionCatalogItem` | STUDENT | Catalog Detail (S05) | Read | 401, 403, 404 |
| 13 | `selectMentorProject` | POST | `/api/v1/project-definitions/catalog/:id/select` | None | `ProjectResponse` | STUDENT | Catalog Detail (S05) | Mutation | 401, 403, 404 |
| 14 | `getAssessmentStatus` | GET | `/api/v1/projects/:id/assessment/status` | None | `AssessmentSessionStatus` | STUDENT | Assessment (S07–S11) | Read | 401, 403, 404 |
| 15 | `startAssessment` | POST | `/api/v1/projects/:id/assessment/start` | None | `AssessmentStartResponse` | STUDENT | Assessment Intro (S07) | Mutation | 401, 403, 404 |
| 16 | `getAssessmentQuestion` | GET | `/api/v1/projects/:id/assessment/questions/:idx` | None | `AssessmentQuestionResponse` | STUDENT | Assessment Question (S08, S09) | Read | 401, 403, 404 |
| 17 | `submitAssessmentAnswer` | POST | `/api/v1/projects/:id/assessment/answers` | `AssessmentAnswerSubmitPayload` | `AssessmentAnswerSubmitResponse` | STUDENT | Assessment Question (S08, S09) | Mutation | 400, 401, 403, 422 |
| 18 | `completeAssessment` | POST | `/api/v1/projects/:id/assessment/complete` | None | `AssessmentResultResponse` | STUDENT | Assessment Completion (S10) | Mutation | 400, 401, 403, 422 |
| 19 | `getAssessmentResult` | GET | `/api/v1/projects/:id/assessment/result` | None | `AssessmentResultResponse` | STUDENT | Assessment Result (S11) | Read | 401, 403, 404 |
| 20 | `getBlueprintStatus` | GET | `/api/v1/projects/:id/blueprint/status` | None | `BlueprintStatusResponse` | STUDENT | Blueprint (S12–S14) | Read | 401, 403, 404 |
| 21 | `startBlueprintGeneration` | POST | `/api/v1/projects/:id/blueprint/generate` | None | `BlueprintStatusResponse` | STUDENT | Blueprint Generation (S12) | Mutation | 401, 403, 404 |
| 22 | `retryBlueprintGeneration` | POST | `/api/v1/projects/:id/blueprint/retry` | `BlueprintRetryRequest` | `BlueprintStatusResponse` | STUDENT | Blueprint Failure (S13) | Mutation | 400, 401, 403, 404 |
| 23 | `getBlueprintContent` | GET | `/api/v1/projects/:id/blueprint/content` | None | `BlueprintContentResponse` | STUDENT | Blueprint Workspace (S16) | Read | 401, 403, 404 |
| 24 | `approveBlueprint` | POST | `/api/v1/projects/:id/blueprint/approve` | None | `BlueprintApprovalResponse` | STUDENT | Blueprint Approval (S14) | Mutation | 401, 403, 404 |
| 25 | `getBlueprintSection` | GET | `/api/v1/projects/:id/blueprint/sections/:key` | None | `BlueprintSectionDetail` | STUDENT | Blueprint Workspace (S16) | Read | 401, 403, 404 |
| 26 | `getBlueprintDocument` | GET | `/api/v1/projects/:id/blueprint/documents/:key` | None | `BlueprintDocumentDetail` | STUDENT | Blueprint Viewer (S17) | Read | 401, 403, 404 |
| 27 | `subscribeBlueprintEvents`| GET | `/api/v1/projects/:id/blueprint/events` | None (Query Token) | SSE Stream | STUDENT | Blueprint Gen (S12) | Read (SSE) | 401, 403 |
| 28 | `downloadBlueprintDocument`| GET | `/api/v1/projects/:id/blueprint/documents/:key/raw` | None | Markdown Octet | STUDENT | Blueprint Viewer (S17) | Read | 401, 403, 404 |
| 29 | `getTasks` | GET | `/api/v1/projects/:id/tasks` | None | `TaskResponse[]` | STUDENT | Tasks (S18) | Read | 401, 403, 404 |
| 30 | `getTask` | GET | `/api/v1/projects/:id/tasks/:taskId` | None | `TaskResponse` | STUDENT | Task Detail (S19) | Read | 401, 403, 404 |
| 31 | `createTask` | POST | `/api/v1/projects/:id/tasks` | `TaskCreatePayload` | `TaskResponse` | STUDENT | Tasks (S18) | Mutation | 400, 401, 403, 422 |
| 32 | `updateTask` | PATCH | `/api/v1/projects/:id/tasks/:taskId` | `TaskUpdatePayload` | `TaskResponse` | STUDENT | Task Detail (S19) | Mutation | 400, 401, 403, 404, 422 |
| 33 | `deleteTask` | DELETE | `/api/v1/projects/:id/tasks/:taskId` | None | `void` | STUDENT | Task Detail (S19) | Mutation | 401, 403, 404 |
| 34 | `getMilestones` | GET | `/api/v1/projects/:id/milestones` | None | `MilestoneResponse[]` | STUDENT | Milestones (S20) | Read | 401, 403, 404 |
| 35 | `getMilestone` | GET | `/api/v1/projects/:id/milestones/:mId`| None | `MilestoneResponse` | STUDENT | Milestone Detail (S21) | Read | 401, 403, 404 |
| 36 | `createMilestone` | POST | `/api/v1/projects/:id/milestones` | `MilestoneCreatePayload` | `MilestoneResponse` | STUDENT | Milestones (S20) | Mutation | 400, 401, 403, 422 |
| 37 | `updateMilestone` | PATCH | `/api/v1/projects/:id/milestones/:mId`| `MilestoneUpdatePayload` | `MilestoneResponse` | STUDENT | Milestone Detail (S21) | Mutation | 400, 401, 403, 404, 422 |
| 38 | `getRisks` | GET | `/api/v1/projects/:id/risks` | None | `RiskResponse[]` | STUDENT | Risks (S22) | Read | 401, 403, 404 |
| 39 | `getRisk` | GET | `/api/v1/projects/:id/risks/:rId` | None | `RiskResponse` | STUDENT | Risk Detail (S23) | Read | 401, 403, 404 |
| 40 | `createRisk` | POST | `/api/v1/projects/:id/risks` | `RiskCreatePayload` | `RiskResponse` | STUDENT | Risks (S22) | Mutation | 400, 401, 403, 422 |
| 41 | `updateRisk` | PATCH | `/api/v1/projects/:id/risks/:rId` | `RiskUpdatePayload` | `RiskResponse` | STUDENT | Risk Detail (S23) | Mutation | 400, 401, 403, 404, 422 |
| 42 | `deleteRisk` | DELETE | `/api/v1/projects/:id/risks/:rId` | None | `void` | STUDENT | Risk Detail (S23) | Mutation | 401, 403, 404 |
| 43 | `getRoadmap` | GET | `/api/v1/projects/:id/roadmap` | None | `RoadmapResponse` | STUDENT | Roadmap (S24) | Read | 401, 403, 404 |
| 44 | `getDocuments` | GET | `/api/v1/projects/:id/documents` | None | `DocumentResponse[]` | STUDENT | Documents (S25) | Read | 401, 403, 404 |
| 45 | `getDocument` | GET | `/api/v1/projects/:id/documents/:docId`| None | `DocumentResponse` | STUDENT | Document Detail (S26) | Read | 401, 403, 404 |
| 46 | `createDocument` | POST | `/api/v1/projects/:id/documents` | `DocumentCreatePayload` | `DocumentResponse` | STUDENT | Documents (S25) | Mutation | 400, 401, 403, 422 |
| 47 | `updateDocument` | PATCH | `/api/v1/projects/:id/documents/:docId`| `DocumentUpdatePayload` | `DocumentResponse` | STUDENT | Document Detail (S26) | Mutation | 400, 401, 403, 404, 422 |
| 48 | `downloadDocument` | GET | `/api/v1/projects/:id/documents/:docId/download` | None | Raw Markdown | STUDENT | Document Detail (S26) | Read | 401, 403, 404 |
| 49 | `getGitHubIntegration` | GET | `/api/v1/projects/:id/github` | None | `GitHubIntegrationResponse` | STUDENT | GitHub (S27) | Read | 401, 403, 404 |
| 50 | `connectGitHub` | POST | `/api/v1/projects/:id/github/connect` | `GitHubConnectPayload` | `GitHubIntegrationResponse` | STUDENT | GitHub (S27) | Mutation | 400, 401, 403, 422 |
| 51 | `syncGitHub` | POST | `/api/v1/projects/:id/github/sync` | None | `GitHubIntegrationResponse` | STUDENT | GitHub (S27) | Mutation | 401, 403, 404 |
| 52 | `disconnectGitHub` | DELETE | `/api/v1/projects/:id/github/disconnect` | None | `GitHubIntegrationResponse` | STUDENT | GitHub (S27) | Mutation | 401, 403, 404 |
| 53 | `getProjectActivity` | GET | `/api/v1/projects/:id/activity` | None | `ActivityItemResponse[]` | STUDENT | Activity (S28) | Read | 401, 403, 404 |
| 54 | `getAIMentorHistory` | GET | `/api/v1/projects/:id/ai-mentor` | None | `AIMentorConversationResponse` | STUDENT | AI Mentor (S29) | Read | 401, 403, 404 |
| 55 | `sendAIMentorMessage` | POST | `/api/v1/projects/:id/ai-mentor/chat` | `{ content: string }` | `AIMentorSendResponse` | STUDENT | AI Mentor (S29) | Mutation | 400, 401, 403, 422, 503 |
| 56 | `executeAIOperation` | POST | `/api/v1/projects/:id/ai-mentor/execute-action` | `{ action_type, payload }` | `any` | STUDENT | AI Mentor (S29) | Mutation | 400, 401, 403, 422 |
| 57 | `getHelpRequests` | GET | `/api/v1/projects/:id/help-requests` | None | `HelpRequestResponse[]` | STUDENT | Help Requests (S30) | Read | 401, 403, 404 |
| 58 | `createHelpRequest` | POST | `/api/v1/projects/:id/help-requests` | `HelpRequestCreatePayload` | `HelpRequestResponse` | STUDENT | Help Requests (S30) | Mutation | 400, 401, 403, 422 |
| 59 | `getHelpRequest` | GET | `/api/v1/projects/:id/help-requests/:reqId` | None | `HelpRequestResponse` | STUDENT | Help Requests (S30) | Read | 401, 403, 404 |
| 60 | `getMentorNotes` | GET | `/api/v1/projects/:id/mentor-notes` | None | `MentorNoteResponse[]` | STUDENT | Mentor Feedback (S31) | Read | 401, 403, 404 |
| 61 | `acknowledgeMentorNote`| POST | `/api/v1/projects/:id/mentor-notes/:nId/acknowledge` | None | `MentorNoteResponse` | STUDENT | Mentor Feedback (S31) | Mutation | 401, 403, 404 |
| 62 | `getProjectChanges` | GET | `/api/v1/projects/:id/changes` | None | `ProjectChangeResponse[]` | STUDENT | Project Changes (S32) | Read | 401, 403, 404 |
| 63 | `getProjectChange` | GET | `/api/v1/projects/:id/changes/:cId` | None | `ProjectChangeResponse` | STUDENT | Change Detail (S33) | Read | 401, 403, 404 |
| 64 | `analyzeProjectChange` | POST | `/api/v1/projects/:id/changes/analyze` | `ProjectChangeAnalyzePayload` | `ProjectChangeResponse` | STUDENT | Project Changes (S32) | Mutation | 400, 401, 403, 422 |
| 65 | `confirmProjectChange` | POST | `/api/v1/projects/:id/changes/:cId/confirm` | `ProjectChangeConfirmPayload` | `ProjectChangeResponse` | STUDENT | Change Detail (S33) | Mutation | 400, 401, 403, 404 |
| 66 | `getBlueprintVersions`| GET | `/api/v1/projects/:id/blueprint-versions` | None | `BlueprintVersionResponse[]` | STUDENT | Changes (S32, S33) | Read | 401, 403, 404 |
| 67 | `getBlueprintVersion` | GET | `/api/v1/projects/:id/blueprint-versions/:ver` | None | `BlueprintVersionResponse` | STUDENT | Change Detail (S33) | Read | 401, 403, 404 |
| 68 | `getMentorOverview` | GET | `/api/v1/mentors/overview` | None | `MentorOverviewResponse` | MENTOR | Mentor Overview (M01) | Read | 401, 403 |
| 69 | `getMentorGroups` | GET | `/api/v1/groups` | None | `GroupResponse[]` | MENTOR | Groups Directory (M02) | Read | 401, 403 |
| 70 | `createMentorGroup` | POST | `/api/v1/groups` | `GroupCreatePayload` | `GroupResponse` | MENTOR | Create Group (M03) | Mutation | 400, 401, 403, 422 |
| 71 | `getMentorGroup` | GET | `/api/v1/groups/:id` | None | `GroupResponse` | MENTOR | Group Workspace (M04) | Read | 401, 403, 404 |
| 72 | `getGroupStudents` | GET | `/api/v1/groups/:id/students` | None | `GroupStudentResponse[]` | MENTOR | Group Students (M05) | Read | 401, 403, 404 |
| 73 | `getGroupProjects` | GET | `/api/v1/groups/:id/projects` | None | `ProjectResponse[]` | MENTOR | Group Projects (M06) | Read | 401, 403, 404 |
| 74 | `getStudentGroups` | GET | `/api/v1/groups` | None | `GroupResponse[]` | STUDENT | Student Dashboard (S01) | Read | 401, 403 |
| 75 | `joinGroup` | POST | `/api/v1/groups/join` | `{ join_code: string }` | `GroupMembershipResponse` | STUDENT | Student Dashboard (S01) | Mutation | 400, 401, 403, 404, 422 |
| 76 | `getMentorHelpRequests`| GET | `/api/v1/mentors/help-requests` | None | `MentorHelpRequestSummary[]`| MENTOR | Help Requests (M33) | Read | 401, 403 |
| 77 | `getMentorHelpRequest` | GET | `/api/v1/mentors/help-requests/:reqId`| None | `MentorHelpRequestSummary` | MENTOR | Help Requests (M33) | Read | 401, 403, 404 |
| 78 | `respondMentorHelpRequest`| POST | `/api/v1/mentors/help-requests/:reqId/respond` | `HelpRequestRespondPayload` | `MentorHelpRequestSummary` | MENTOR | Help Requests (M33) | Mutation | 400, 401, 403, 404, 422 |
| 79 | `createMentorNote` | POST | `/api/v1/mentors/notes` | `MentorNoteCreatePayload` | `MentorNoteItem` | MENTOR | Instance Notes (M34) | Mutation | 400, 401, 403, 422 |
| 80 | `getMentorProjectNotes`| GET | `/api/v1/mentors/project-instances/:pId/notes` | None | `MentorNoteItem[]` | MENTOR | Instance Notes (M34) | Read | 401, 403, 404 |
| 81 | `getMentorDefinitions` | GET | `/api/v1/project-definitions` | None | `ProjectDefinition[]` | MENTOR | Definitions (M16, M17) | Read | 401, 403 |
| 82 | `getMentorDefinition` | GET | `/api/v1/project-definitions/:id` | None | `ProjectDefinition` | MENTOR | Definition Detail (M18) | Read | 401, 403, 404 |
| 83 | `createMentorDefinition`| POST | `/api/v1/project-definitions` | `ProjectDefinitionCreatePayload` | `ProjectDefinition` | MENTOR | Create Definition (M19) | Mutation | 400, 401, 403, 422 |
| 84 | `updateMentorDefinition`| PATCH | `/api/v1/project-definitions/:id` | `ProjectDefinitionUpdatePayload` | `ProjectDefinition` | MENTOR | Edit Definition (M20) | Mutation | 400, 401, 403, 404, 422 |
| 85 | `getDefinitionVersions`| GET | `/api/v1/project-definitions/:id/versions` | None | `ProjectDefinitionVersion[]` | MENTOR | Definition Detail (M18) | Read | 401, 403, 404 |
| 86 | `getDefinitionVersion` | GET | `/api/v1/project-definitions/:id/versions/:vId` | None | `ProjectDefinitionVersion` | MENTOR | Definition Detail (M18) | Read | 401, 403, 404 |
| 87 | `assignMentorDefinition`| POST | `/api/v1/project-definitions/:id/assign` | `ProjectDefinitionAssignPayload` | `{ success: true }` | MENTOR | Assign Definition (M21) | Mutation | 400, 401, 403, 422 |
| 88 | `getMentorStudents` | GET | `/api/v1/mentors/students` | None | `MentorStudentSummary[]` | MENTOR | Students Directory (M10) | Read | 401, 403 |
| 89 | `getMentorStudent` | GET | `/api/v1/mentors/students/:sId` | None | `MentorStudentDetail` | MENTOR | Student Detail (M11) | Read | 401, 403, 404 |
| 90 | `getMentorStudentProjects`| GET | `/api/v1/mentors/students/:sId/projects` | None | `MentorProjectInstanceSummary[]`| MENTOR | Student Projects (M12) | Read | 401, 403, 404 |
| 91 | `getMentorProjects` | GET | `/api/v1/mentors/projects/instances` | None | `MentorProjectInstanceSummary[]`| MENTOR | Projects Directory (M16) | Read | 401, 403 |
| 92 | `getMentorProjectInstances`| GET | `/api/v1/mentors/project-instances` | None | `MentorProjectInstanceSummary[]`| MENTOR | Project Instances (M22) | Read | 401, 403 |
| 93 | `getMentorProjectInstance`| GET | `/api/v1/mentors/project-instances/:pId` | None | `MentorProjectInstanceDetail` | MENTOR | Instance Detail (M23) | Read | 401, 403, 404 |
| 94 | `getMentorAtRiskProjects`| GET | `/api/v1/mentors/at-risk` | Query: `health, group_id` | `MentorProjectInstanceSummary[]`| MENTOR | At Risk Directory (M31) | Read | 401, 403 |
| 95 | `getMentorAtRiskProject`| GET | `/api/v1/mentors/at-risk/:pId` | None | `MentorProjectInstanceDetail` | MENTOR | At Risk Detail (M32) | Read | 401, 403, 404 |
| 96 | `getMentorInstanceBlueprint`| GET | `/api/v1/mentors/project-instances/:pId/blueprint` | None | `MentorBlueprintInspectionResponse`| MENTOR | Instance Blueprint (M24) | Read | 401, 403, 404 |
| 97 | `getMentorInstanceTasks`| GET | `/api/v1/mentors/project-instances/:pId/tasks` | None | `TaskResponse[]` | MENTOR | Instance Tasks (M25) | Read | 401, 403, 404 |
| 98 | `getMentorInstanceMilestones`| GET | `/api/v1/mentors/project-instances/:pId/milestones` | None | `MilestoneResponse[]` | MENTOR | Instance Milestones (M26) | Read | 401, 403, 404 |
| 99 | `getMentorInstanceRisks`| GET | `/api/v1/mentors/project-instances/:pId/risks` | None | `RiskResponse[]` | MENTOR | Instance Risks (M27) | Read | 401, 403, 404 |
| 100| `getMentorInstanceDocuments`| GET | `/api/v1/mentors/project-instances/:pId/documents` | None | `DocumentResponse[]` | MENTOR | Instance Documents (M28) | Read | 401, 403, 404 |
| 101| `getMentorInstanceGitHub`| GET | `/api/v1/mentors/project-instances/:pId/github` | None | `GitHubIntegrationResponse` | MENTOR | Instance GitHub (M29) | Read | 401, 403, 404 |
| 102| `getMentorInstanceActivity`| GET | `/api/v1/mentors/project-instances/:pId/activity` | None | `ActivityItemResponse[]` | MENTOR | Instance Activity (M30) | Read | 401, 403, 404 |
| 103| `getGroupActivity` | GET | `/api/v1/groups/:id/activity` | None | `ActivityItemResponse[]` | MENTOR | Group Activity (M08) | Read | 401, 403, 404 |
| 104| `getMentorStudentActivity`| GET | `/api/v1/mentors/students/:sId/activity` | None | `ActivityItemResponse[]` | MENTOR | Student Activity (M13) | Read | 401, 403, 404 |
| 105| `getMentorPortfolioActivity`| GET | `/api/v1/mentors/activity` | None | `ActivityItemResponse[]` | MENTOR | Mentor Activity (M35) | Read | 401, 403 |
| 106| `getGroupAIStatus` | GET | `/api/v1/groups/:id/ai/status` | None | `MentorAIStatusResponse` | MENTOR | Group AI (M09) | Read | 401, 403, 404 |
| 107| `sendGroupAIMessage` | POST | `/api/v1/groups/:id/ai/chat` | `MentorAIChatPayload` | `MentorAIChatResponse` | MENTOR | Group AI (M09) | Mutation | 400, 401, 403, 422 |
| 108| `getMentorAIStatus` | GET | `/api/v1/mentors/ai/status` | None | `MentorAIStatusResponse` | MENTOR | Mentor AI (M36) | Read | 401, 403 |
| 109| `sendMentorAIMessage` | POST | `/api/v1/mentors/ai/chat` | `MentorAIChatPayload` | `MentorAIChatResponse` | MENTOR | Mentor AI (M36) | Mutation | 400, 401, 403, 422 |
| 110| `getMentorProfile` | GET | `/api/v1/mentors/me` | None | `MentorProfileResponse` | MENTOR | Mentor Profile (X03) | Read | 401, 403 |
| 111| `updateMentorProfile` | PATCH | `/api/v1/mentors/me` | `MentorProfileUpdatePayload` | `MentorProfileResponse` | MENTOR | Mentor Profile (X03) | Mutation | 400, 401, 403, 422 |
| 112| `getUserPreferences` | GET | `/api/v1/users/me/preferences` | None | `UserPreferencesResponse` | Any Auth | Settings (X04) | Read | 401, 403 |
| 113| `updateUserPreferences`| PATCH | `/api/v1/users/me/preferences` | `UserPreferencesUpdatePayload`| `UserPreferencesResponse` | Any Auth | Settings (X04) | Mutation | 400, 401, 403, 422 |
| 114| `getAdminOverview` | GET | `/api/v1/admin/overview` | None | `AdminOverviewResponse` | ADMIN | Admin Overview (AD01) | Read | 401, 403 |
| 115| `getAdminMentors` | GET | `/api/v1/admin/mentors` | None | `AdminMentorSummary[]` | ADMIN | Mentor Directory (AD02) | Read | 401, 403 |
| 116| `getAdminMentor` | GET | `/api/v1/admin/mentors/:mentorId` | None | `AdminMentorDetail` | ADMIN | Mentor Detail (AD03) | Read | 401, 403, 404 |
| 117| `getAdminStudents` | GET | `/api/v1/admin/students` | None | `AdminStudentSummary[]` | ADMIN | Student Directory (AD04) | Read | 401, 403 |
| 118| `getAdminStudent` | GET | `/api/v1/admin/students/:studentId` | None | `AdminStudentDetail` | ADMIN | Student Detail (AD05) | Read | 401, 403, 404 |
| 119| `getAdminGroups` | GET | `/api/v1/admin/groups` | None | `AdminGroupSummary[]` | ADMIN | Groups Directory (AD06) | Read | 401, 403 |
| 120| `getAdminGroup` | GET | `/api/v1/admin/groups/:groupId` | None | `AdminGroupDetail` | ADMIN | Group Detail (AD07) | Read | 401, 403, 404 |
| 121| `getAdminProjects` | GET | `/api/v1/admin/projects` | None | `AdminProjectSummary[]` | ADMIN | Projects (AD08) | Read | 401, 403 |
| 122| `getAdminDefinitions` | GET | `/api/v1/admin/definitions` | None | `AdminProjectDefinitionSummary[]`| ADMIN | Definitions (AD09) | Read | 401, 403 |
| 123| `getAdminDefinition` | GET | `/api/v1/admin/definitions/:dId` | None | `AdminProjectDefinitionDetail` | ADMIN | Definition Detail (AD09) | Read | 401, 403, 404 |
| 124| `getAdminInstancesMonitoring`| GET | `/api/v1/admin/instances` | None | `AdminInstanceMonitoringResponse`| ADMIN | Instances Monitoring (AD10) | Read | 401, 403 |
| 125| `getAdminInstanceDetail`| GET | `/api/v1/admin/instances/:projectId` | None | `AdminProjectInstanceDetail` | ADMIN | Instance Detail (AD10) | Read | 401, 403, 404 |
| 126| `getAdminSystemHealth`| GET | `/api/v1/admin/health` | None | `AdminSystemHealthResponse` | ADMIN | System Health (AD19) | Read | 401, 403 |
| 127| `getAdminComponentDetail`| GET | `/api/v1/admin/health/:cId` | None | `AdminSubsystemDetail` | ADMIN | Component Detail (AD20) | Read | 401, 403, 404 |
| 128| `getAdminSecurityOverview`| GET | `/api/v1/admin/security/overview` | None | `AdminSecurityOverview` | ADMIN | Security Overview (AD24) | Read | 401, 403 |
| 129| `getAdminAuditLog` | GET | `/api/v1/admin/security/audit` | None | `AdminAuditLogResponse` | ADMIN | Audit Log (AD25) | Read | 401, 403 |
| 130| `getAdminInvestigations`| GET | `/api/v1/admin/security/investigations` | None | `AdminInvestigationOverviewResponse`| ADMIN | Investigations (AD26) | Read | 401, 403 |
| 131| `getAdminInvestigationDetail`| GET | `/api/v1/admin/security/investigations/:iId`| None | `any` | ADMIN | Investigation Detail (AD27)| Read | 401, 403, 404 |
| 132| `getAdminDocuments` | GET | `/api/v1/admin/documents` | None | `AdminDocumentsResponse` | ADMIN | Documents & RAG (AD21) | Read | 401, 403 |
| 133| `getAdminRAGDiagnostics`| GET | `/api/v1/admin/documents/rag` | None | `AdminRAGDiagnostics` | ADMIN | RAG Monitoring (AD22) | Read | 401, 403 |
| 134| `getAdminGenerationJobs`| GET | `/api/v1/admin/documents/generation` | None | `AdminGenerationJobsResponse` | ADMIN | Doc Generation (AD23) | Read | 401, 403 |
| 135| `getAdminAnalytics` | GET | `/api/v1/admin/analytics` | None | `AdminPlatformAnalyticsResponse`| ADMIN | Platform Analytics (AD28) | Read | 401, 403 |
| 136| `getAdminAnalyticsDimension`| GET | `/api/v1/admin/analytics/:dim` | None | `AdminAnalyticsDimensionDetail` | ADMIN | Analytics Detail (AD29) | Read | 401, 403, 404 |
| 137| `getAdminAIObservatory`| GET | `/api/v1/admin/ai/observatory` | None | `AdminAIObservatoryResponse` | ADMIN | AI Observatory (AD11) | Read | 401, 403 |
| 138| `getAdminAIUsage` | GET | `/api/v1/admin/ai/usage` | None | `AdminAIUsageResponse` | ADMIN | AI Usage (AD12) | Read | 401, 403 |
| 139| `getAdminAIExecutions`| GET | `/api/v1/admin/ai/executions` | None | `AdminAIExecutionsResponse` | ADMIN | Agent Executions (AD13) | Read | 401, 403 |
| 140| `getAdminAITraceDetail`| GET | `/api/v1/admin/ai/executions/:eId` | None | `AdminAITraceDetailResponse` | ADMIN | AI Trace Detail (AD14) | Read | 401, 403, 404 |
| 141| `getAdminAIQuality` | GET | `/api/v1/admin/ai/quality` | None | `AdminAIQualityResponse` | ADMIN | AI Quality (AD15) | Read | 401, 403 |
| 142| `getAdminAICost` | GET | `/api/v1/admin/ai/cost` | None | `AdminAICostResponse` | ADMIN | Cost & Usage (AD16) | Read | 401, 403 |
| 143| `getAdminAICostDimension`| GET | `/api/v1/admin/ai/cost/:dim` | None | `AdminAICostDimensionResponse`| ADMIN | Cost Breakdown (AD17) | Read | 401, 403, 404 |
| 144| `getAdminAIKeys` | GET | `/api/v1/admin/ai/keys` | None | `AdminAIKeysResponse` | ADMIN | Key Pool (AD18) | Read | 401, 403 |
| 145| `searchWorkspace` | GET | `/api/v1/search` | Query: `q, category, limit` | `SearchResponseData` | Any Auth | Global Search (X01) | Read | 400, 401, 403 |
| 146| `getNotifications` | GET | `/api/v1/notifications` | Query: `limit, offset, unread_only`| `NotificationItem[]` | Any Auth | Notifications (X02) | Read | 401, 403 |
| 147| `getUnreadNotificationCount`| GET | `/api/v1/notifications/unread-count` | None | `UnreadCountResponse` | Any Auth | Notifications (X02) | Read | 401, 403 |
| 148| `markNotificationRead`| PATCH | `/api/v1/notifications/:id/read` | None | `NotificationItem` | Any Auth | Notifications (X02) | Mutation | 401, 403, 404 |
| 149| `markAllNotificationsRead`| POST | `/api/v1/notifications/mark-all-read` | None | `MarkAllReadResponse` | Any Auth | Notifications (X02) | Mutation | 401, 403 |

*(Note: Direct HTTP integration points outside client.ts include Public Contact `POST /api/v1/contact` in Contact.tsx and health probes `GET /health`, `GET /health/live`, `GET /health/ready`)*.

---

## 5. API Contract Details

This section documents canonical endpoint contracts organized by functional domain.

### 5.1 Authentication Domain

#### Endpoint: GET /api/v1/auth/me
- **Purpose:** Authoritative identity and role resolution called immediately upon session restoration or change.
- **Authentication:** Bearer JWT required in `Authorization: Bearer <token>` header.
- **Authorization:** Any authenticated user.
- **Path / Query Parameters:** None.
- **Request Body:** None.
- **Response Envelope:**
```json
{
  "success": true,
  "message": "User authorization profile retrieved",
  "data": {
    "id": "usr_998877",
    "email": "student@university.edu",
    "role": "STUDENT",
    "status": "ACTIVE",
    "full_name": "Alex Johnson"
  }
}
```
- **Frontend Usage:** Consumed by `fetchUserAuthorization` in `AuthProvider.tsx`. If status is `SUSPENDED` or `INACTIVE`, backend returns HTTP 403 with code `AUTH_ACCOUNT_SUSPENDED` or `AUTH_ACCOUNT_INACTIVE`.

---

### 5.2 Projects & Lifecycle Domain

#### Endpoint: GET /api/v1/projects
- **Purpose:** List all project instances accessible to the authenticated caller.
- **Authentication:** Bearer JWT.
- **Authorization:** STUDENT (returns student's own instances); MENTOR (returns supervised instances).
- **Response Envelope:**
```json
{
  "success": true,
  "data": [
    {
      "id": "proj_001",
      "student_id": "usr_998877",
      "group_id": "grp_101",
      "project_definition_id": null,
      "source_definition_version_id": null,
      "name": "Distributed Event Pipeline",
      "problem": "High-throughput stream processing latency",
      "proposed_solution": "Distributed Kafka worker architecture",
      "complexity": "INTERMEDIATE",
      "current_phase": "BLUEPRINT",
      "health": "HEALTHY",
      "progress_percentage": 25,
      "status": "ACTIVE",
      "deadline": "2026-12-15T00:00:00Z",
      "started_at": "2026-09-01T10:00:00Z",
      "completed_at": null,
      "created_at": "2026-09-01T10:00:00Z",
      "updated_at": "2026-09-18T14:30:00Z"
    }
  ]
}
```

#### Endpoint: POST /api/v1/projects
- **Purpose:** Create an independent student project instance.
- **Authentication:** Bearer JWT.
- **Authorization:** STUDENT.
- **Request Payload:**
```json
{
  "name": "Cloud Native Microservices",
  "problem": "Legacy monolithic deployment bottleneck",
  "proposed_solution": "Containerized service mesh using Kubernetes",
  "complexity": "ADVANCED",
  "technologies": ["Go", "Kubernetes", "gRPC"],
  "deadline": "2026-11-30T00:00:00Z",
  "group_id": "grp_101"
}
```
- **Response:** `201 Created` returning created `ProjectResponse`.

#### Endpoint: POST /api/v1/projects/{projectId}/phase
- **Purpose:** Advance or transition project lifecycle phase according to canonical state machine.
- **Authentication:** Bearer JWT.
- **Authorization:** STUDENT (must own project).
- **Request Payload:**
```json
{
  "target_phase": "PLANNING",
  "reason": "Blueprint approved by student and QA passed"
}
```
- **Response:** `200 OK` returning updated `ProjectResponse`.

---

### 5.3 Assessment Domain

#### Endpoint: POST /api/v1/projects/{projectId}/assessment/start
- **Purpose:** Initialize or resume the 15-question project assessment session.
- **Authentication:** Bearer JWT.
- **Authorization:** STUDENT.
- **Response Data:**
```json
{
  "success": true,
  "data": {
    "session": {
      "project_id": "proj_001",
      "project_name": "Distributed Event Pipeline",
      "current_phase": "ASSESSMENT",
      "status": "IN_PROGRESS",
      "current_question_index": 1,
      "total_questions": 15,
      "answered_count": 0,
      "progress_percentage": 0
    },
    "current_question": {
      "id": "q_01",
      "order_index": 1,
      "category": "ARCHITECTURAL_SCOPE",
      "question_text": "What is the primary architectural boundary of your service?",
      "help_text": "Consider whether services share databases or communicate via RPC",
      "question_type": "MULTIPLE_CHOICE",
      "options": [
        { "value": "SHARED_DB", "label": "Shared Database", "description": "Multiple services query the same schemas" },
        { "value": "EVENT_DRIVEN", "label": "Event Driven", "description": "Services emit domain events asynchronously" }
      ],
      "is_adaptive": false
    }
  }
}
```

#### Endpoint: POST /api/v1/projects/{projectId}/assessment/answers
- **Purpose:** Submit an answer for an assessment question.
- **Request Payload:**
```json
{
  "question_index": 1,
  "selected_option": "EVENT_DRIVEN",
  "text_response": "We will utilize Kafka with protobuf schemas"
}
```
- **Response Data:**
```json
{
  "success": true,
  "data": {
    "answer": {
      "id": "ans_01",
      "assessment_id": "asm_100",
      "question_id": "q_01",
      "question_index": 1,
      "question_text": "What is the primary architectural boundary of your service?",
      "question_type": "MULTIPLE_CHOICE",
      "selected_option": "EVENT_DRIVEN"
    },
    "current_question_index": 2,
    "next_question_index": 2,
    "answered_count": 1,
    "total_questions": 15,
    "is_complete_eligible": false
  }
}
```

---

### 5.4 Blueprint Domain (Stage 3)

#### Endpoint: GET /api/v1/projects/{projectId}/blueprint/status
- **Purpose:** Polling check for blueprint synthesis stage, active background job, and QA scorecard.
- **Authentication:** Bearer JWT.
- **Authorization:** STUDENT (or supervising MENTOR).
- **Response Data:**
```json
{
  "success": true,
  "data": {
    "blueprint_id": "bp_550",
    "project_id": "proj_001",
    "status": "READY_FOR_APPROVAL",
    "current_stage": 3,
    "qa_status": "PASSED",
    "qa_feedback": {
      "score": 88,
      "status": "PASSED",
      "evaluated_criteria": {
        "architectural_completeness": 90,
        "technical_depth": 85,
        "risk_mitigation": 89
      },
      "summary": "Robust microservice blueprint meeting all architectural thresholds."
    },
    "generation_progress": {
      "completed_sections": ["project_profile", "tech_stack", "features", "specifications", "mvp", "duration", "risks", "tasks", "milestones", "readme"],
      "total_sections": 10,
      "in_progress_section": null,
      "failed_sections": []
    },
    "active_job": null
  }
}
```

#### Endpoint: GET /api/v1/projects/{projectId}/blueprint/content
- **Purpose:** Fetch full synthesized blueprint sections.
- **Authentication:** Bearer JWT.
- **Critical Contract Requirement (B3-01):** Must return dictionary of synthesized sections under property `content` (NOT `sections`).
- **Response Data:**
```json
{
  "success": true,
  "data": {
    "project_instance_id": "proj_001",
    "blueprint_id": "bp_550",
    "project_id": "proj_001",
    "status": "READY_FOR_APPROVAL",
    "qa_status": "PASSED",
    "qa_score": 88,
    "content": {
      "project_profile": { "title": "Project Profile", "markdown": "# Profile Content..." },
      "tech_stack": { "title": "Tech Stack", "markdown": "## Selected Technologies..." },
      "features": { "title": "Features", "markdown": "## Core Capabilities..." },
      "specifications": { "title": "Specifications", "markdown": "## Data Models..." },
      "mvp": { "title": "MVP Scope", "markdown": "## Minimum Viable Deliverables..." },
      "duration": { "title": "Duration", "markdown": "## 12-Week Roadmap..." },
      "risks": { "title": "Risks", "markdown": "## Technical Hazards..." },
      "tasks": { "title": "Tasks", "markdown": "## Granular Breakdown..." },
      "milestones": { "title": "Milestones", "markdown": "## Gate Checkpoints..." },
      "readme": { "title": "README", "markdown": "# Project README..." }
    }
  }
}
```

#### Endpoint: POST /api/v1/projects/{projectId}/blueprint/retry
- **Purpose:** Retry failed or targeted blueprint sections.
- **Critical Contract Requirement (B3-02):** Targeted retries submit `target_output_key`.
- **Request Payload:**
```json
{
  "target_output_key": "tech_stack"
}
```
*(When full retry is desired, payload is omitted or `target_output_key: null`)*.

#### Endpoint: POST /api/v1/projects/{projectId}/blueprint/approve
- **Purpose:** Formally lock approved blueprint and enable transition to Stage 4 Planning.
- **Response Data (B3-06):**
```json
{
  "success": true,
  "message": "Blueprint approved successfully",
  "data": {
    "success": true,
    "status": "APPROVED",
    "approved_at": "2026-09-18T16:00:00Z"
  }
}
```

#### Endpoint: GET /api/v1/projects/{projectId}/blueprint/events
- **Purpose:** Server-Sent Events (SSE) stream for real-time generation progress updates.
- **Authentication Exception:** Accepts JWT strictly via query parameter (`?token=<jwt>`) due to native browser `EventSource` header constraints.
- **MIME Type:** `text/event-stream; charset=utf-8`.
- **Event Wire Format:**
```text
: keep-alive

retry: 2000
id: proj_001_1726675200_1
event: update
data: {"blueprint_id":"bp_550","project_id":"proj_001","status":"GENERATING","current_stage":3,"generation_progress":{"completed_sections":["project_profile"],"total_sections":10,"in_progress_section":"tech_stack","failed_sections":[]}}

```


## 6. Frontend Type System

The frontend domain model is governed by 16 structured TypeScript definition modules under `frontend/src/lib/api/types/`. The backend data schemas (Pydantic models and SQLAlchemy domain entities) must adhere strictly to these types.

### 6.1 Authentication & Identity Domain (`auth.ts`)

```typescript
export type UserRole = 'STUDENT' | 'MENTOR' | 'ADMIN';
export type AccountStatus = 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';

export interface CurrentUserIdentity {
  id: string;               // Canonical user UUID
  email: string;            // Validated user email
  role: UserRole;           // Authoritative role resolved by /api/v1/auth/me
  status: AccountStatus;    // Account lifecycle posture
  full_name: string;        // Display name
}
```
- **Consumers:** `AuthProvider.tsx`, `ProtectedRoute.tsx`, `AuthHeader.tsx`, all layout headers.
- **Backend Model:** `backend/app/domain/identity/models.py`, `UserResponseSchema`.

### 6.2 Student Profile Domain (`student.ts`)

```typescript
export interface StudentTechnologyItem {
  id: string;
  technology_id: string;
  name?: string;
  category?: string;
  proficiency_level?: string;
}

export interface StudentProfile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  college?: string | null;
  branch?: string | null;
  year_of_study?: number | null;
  cgpa?: number | null;
  primary_track?: string | null;
  headline?: string | null;
  bio?: string | null;
  target_role?: string | null;
  skills: string[];
  technologies: StudentTechnologyItem[];
  created_at: string;
  updated_at: string;
}

export interface StudentProfileUpdatePayload {
  college?: string;
  branch?: string;
  year_of_study?: number;
  cgpa?: number;
  primary_track?: string;
  headline?: string;
  bio?: string;
  target_role?: string;
  skills?: string[];
}
```

### 6.3 Project Lifecycle Domain (`project.ts`)

```typescript
export type ProjectPhase =
  | 'IDEA'
  | 'ASSESSMENT'
  | 'BLUEPRINT'
  | 'PLANNING'
  | 'IMPLEMENTATION'
  | 'TESTING'
  | 'DEPLOYMENT'
  | 'COMPLETED';

export type ProjectHealth = 'HEALTHY' | 'WARNING' | 'CRITICAL';
export type ProjectComplexity = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
export type ProjectStatus = 'DRAFT' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'ARCHIVED';

export interface ProjectResponse {
  id: string;
  student_id: string;
  group_id: string | null;
  project_definition_id: string | null;
  source_definition_version_id: string | null;
  name: string;
  problem: string;
  proposed_solution: string;
  complexity: ProjectComplexity | string | null;
  current_phase: ProjectPhase | string;
  health: ProjectHealth | string;
  progress_percentage: number;
  status: ProjectStatus | string;
  deadline: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProjectOverviewResponse extends ProjectResponse {
  is_mentor_project?: boolean;
  days_remaining: number | null;
  profile: ProjectProfileData | null;
  technologies: ProjectTechnologyItem[];
  recent_activity: ProjectRecentActivity;
  assessment_summary?: AssessmentOverviewSummary | null;
  blueprint_summary?: BlueprintOverviewSummary | null;
}
```

### 6.4 Assessment Domain (`assessment.ts`)

```typescript
export type AssessmentStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED';
export type QuestionType = 'MULTIPLE_CHOICE' | 'TEXT';
export type AssessmentReadinessTier = 'HIGH' | 'MODERATE' | 'NEEDS_REFINEMENT';

export interface AssessmentQuestionOption {
  value: string;
  label: string;
  description: string;
}

export interface AssessmentQuestion {
  id: string;
  order_index: number;
  category: string;
  question_text: string;
  help_text: string;
  question_type: QuestionType;
  options: AssessmentQuestionOption[];
  is_adaptive: boolean;
  context_badge?: string | null;
}

export interface AssessmentResultResponse {
  id: string;
  assessment_id: string;
  project_instance_id: string;
  skill_level: string;
  project_complexity: string;
  alignment: string;
  technical_confidence: string;
  learning_depth: string;
  recommended_focus: string;
  summary: string;
  overall_score: number;
  readiness_tier: AssessmentReadinessTier;
  dimension_scores: Record<string, number>;
  identified_gaps: Array<{ area: string; severity: string; description: string }>;
  recommendations: Array<{ phase: string; action: string }>;
  created_at?: string | null;
}
```

### 6.5 Blueprint Domain (`blueprint.ts`)

```typescript
export type BlueprintStatus =
  | 'NOT_STARTED'
  | 'GENERATING'
  | 'GENERATED'
  | 'VALIDATING'
  | 'QA_REJECTED'
  | 'READY_FOR_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'APPROVED';

export type BlueprintQAStatus = 'PENDING' | 'IN_REVIEW' | 'PASSED' | 'FAILED';

export type BlueprintSectionKey =
  | 'project_profile'
  | 'tech_stack'
  | 'features'
  | 'specifications'
  | 'mvp'
  | 'duration'
  | 'risks'
  | 'tasks'
  | 'milestones'
  | 'readme';

export interface BlueprintQAFeedback {
  score: number;
  status: BlueprintQAStatus;
  evaluated_criteria?: Record<string, number>; // B3-05 Verified Contract
  summary?: string;
  issues?: Array<{
    section: string;
    severity: string;
    description: string;
    recommendation: string;
  }>;
  strengths?: string[];
  gaps?: string[];
  recommendations?: string[];
  evaluated_at?: string;
}

export interface BlueprintStatusResponse {
  blueprint_id: string;
  project_id: string;
  status: BlueprintStatus;
  current_stage: number;
  qa_status: BlueprintQAStatus;
  qa_feedback?: BlueprintQAFeedback | null;
  generation_progress: {
    completed_sections: BlueprintSectionKey[];
    total_sections: number;
    in_progress_section?: BlueprintSectionKey | null;
    failed_sections?: BlueprintSectionKey[];
  };
  active_job?: {
    id: string;
    job_type: 'FULL_GENERATION' | 'SECTION_RETRY';
    status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
    error_message?: string | null;
    failed_sections: BlueprintSectionKey[];
    created_at: string;
  } | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface BlueprintContentResponse {
  project_instance_id?: string;
  blueprint_id?: string;
  project_id?: string;
  status: BlueprintStatus;
  qa_status?: BlueprintQAStatus;
  qa_score?: number | null;
  content: Record<string, unknown>; // B3-01 Verified Contract: uses content, NOT sections
  qa_feedback?: BlueprintQAFeedback | null;
}

export interface BlueprintApprovalResponse {
  success?: boolean;
  status: BlueprintStatus | string;
  approved_at: string;
  blueprint_id?: string;           // Optional per B3-06
  project_id?: string;             // Optional per B3-06
  message?: string;
}

export interface BlueprintRetryRequest {
  target_output_key?: string | null; // B3-02 Verified Contract: targeted section key
}
```

### 6.6 Execution Domain: Tasks, Milestones, Risks, Roadmap, Documents (`execution.ts`)

```typescript
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'COMPLETED';
export type TaskPhase = 'PLANNING' | 'IMPLEMENTATION' | 'TESTING' | 'DEPLOYMENT';

export interface TaskResponse {
  id: string;
  project_instance_id: string;
  milestone_id: string | null;
  task_code: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  category: string;
  phase: TaskPhase;
  due_date: string | null;
  dependencies: string[];
  acceptance_criteria: string[];
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export type MilestoneStatus = 'UPCOMING' | 'IN_PROGRESS' | 'COMPLETED' | 'AT_RISK';

export interface MilestoneResponse {
  id: string;
  project_instance_id: string;
  title: string;
  description: string;
  gate_code: string;
  target_date: string | null;
  status: MilestoneStatus;
  progress_percent: number;
  deliverables: string[];
  section_order: number;
  task_count: number;
  completed_task_count: number;
  tasks: TaskResponse[];
  created_at: string;
  updated_at: string;
}

export type RiskSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type RiskProbability = 'LOW' | 'MEDIUM' | 'HIGH';
export type RiskImpact = 'LOW' | 'MEDIUM' | 'HIGH';
export type RiskStatus = 'OPEN' | 'MITIGATING' | 'RESOLVED' | 'ACCEPTED';

export interface RiskResponse {
  id: string;
  project_instance_id: string;
  risk_code: string;
  title: string;
  description: string;
  severity: RiskSeverity;
  probability: RiskProbability;
  impact: RiskImpact;
  status: RiskStatus;
  mitigation: string;
  owner: string;
  review_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface RoadmapResponse {
  project_id: string;
  project_name: string;
  current_phase: string;
  summary: {
    total_milestones: number;
    completed_milestones: number;
    total_tasks: number;
    completed_tasks: number;
    overdue_tasks_count: number;
    blocked_tasks_count: number;
    current_phase: string;
    overall_progress: number;
  };
  milestones: Array<{
    id: string;
    gate_code: string;
    title: string;
    description: string;
    status: MilestoneStatus;
    progress_percent: number;
    target_date: string | null;
    deliverables: string[];
    tasks: TaskResponse[];
  }>;
  grouped_tasks: {
    overdue: TaskResponse[];
    blocked: TaskResponse[];
    in_progress: TaskResponse[];
    upcoming: TaskResponse[];
    completed: TaskResponse[];
  };
}

export type DocumentType = 'BLUEPRINT' | 'ARCHITECTURE' | 'SPECIFICATION' | 'README' | 'REPORT' | 'GENERAL';
export type DocumentStatus = 'ACTIVE' | 'ARCHIVED' | 'DRAFT';

export interface DocumentResponse {
  id: string;
  project_instance_id: string;
  document_key: string;
  title: string;
  doc_type: DocumentType;
  format: string;
  content: string;
  version: string;
  status: DocumentStatus;
  source: string;
  created_at: string;
  updated_at: string;
}
```

### 6.7 Workspace Extensions Domain (`workspaceExtensions.ts`)

```typescript
export interface GitHubIntegrationResponse {
  id: string | null;
  project_instance_id: string;
  repository_name: string;
  repository_url: string;
  connection_status: 'NOT_CONNECTED' | 'CONNECTED' | 'SYNCING' | 'ERROR';
  default_branch: string;
  commit_count: number;
  last_sync_at: string | null;
  sync_error: string | null;
  cached_commits_preview: Array<{
    sha: string;
    message: string;
    author: string;
    date: string;
  }>;
}

export interface AIMentorMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources: Array<{ title: string; section?: string }>;
  suggested_action: {
    action_type: string;
    label: string;
    payload: Record<string, any>;
  } | null;
  created_at: string | null;
}

export interface AIMentorConversationResponse {
  conversation_id: string;
  project_instance_id: string;
  title: string;
  ai_available: boolean;
  messages: AIMentorMessage[];
}

export interface HelpRequestResponse {
  id: string;
  project_instance_id: string;
  student_id: string;
  subject: string;
  description: string;
  category: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: 'OPEN' | 'IN_REVIEW' | 'RESOLVED';
  mentor_response: string | null;
  resolved_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface MentorNoteResponse {
  id: string;
  project_instance_id: string;
  mentor_id: string | null;
  title: string;
  message: string;
  note_type: 'INFORMATIONAL' | 'ACTIONABLE' | 'FEEDBACK';
  status: 'UNREAD' | 'ACKNOWLEDGED';
  related_resource_type: string | null;
  related_resource_id: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ImpactAnalysis {
  affected_sections: string[];
  affected_tasks_count: number;
  total_tasks_count?: number;
  total_milestones_count?: number;
  estimated_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  analysis_narrative: string;
  duration_impact?: string;
  recommended_action?: string;
}

export interface ProjectChangeResponse {
  id: string;
  project_instance_id: string;
  student_id: string;
  change_title: string;
  change_description: string;
  change_type: 'SCOPE' | 'TECH_STACK' | 'ARCHITECTURE' | 'SCHEDULE';
  status: 'ANALYZED' | 'CONFIRMED' | 'COMPLETED' | 'REJECTED';
  idempotency_key: string | null;
  impact_analysis: ImpactAnalysis;
  source_blueprint_version_number: number;
  resulting_blueprint_version_number: number | null;
  qa_score: number | null;
  qa_feedback: Record<string, any> | null;
  created_at: string | null;
  updated_at: string | null;
}
```

### 6.8 Search & Notifications Domain (`search.ts`, `notifications.ts`)

```typescript
export interface SearchResultItem {
  id?: string | null;       // B3-04 Verified Contract
  title: string;
  subtitle: string;
  resource_type: string;
  url: string;
  badge: string;
  metadata: Record<string, unknown>;
}

export interface SearchResponseData {
  query: string;
  workplace: 'BUILD' | 'SUPERVISE' | 'GOVERN';
  total: number;
  results: SearchResultItem[];
}

export interface NotificationItem {
  id: string;
  user_id: string;
  actor_id?: string | null;
  actor_role?: string | null;
  title: string;
  message: string;
  notification_type: string;
  category: string;
  resource_type?: string | null;
  resource_id?: string | null;
  link: string;
  is_read: boolean;
  read_at?: string | null;
  created_at: string;
}
```

---

## 7. Important Verified Contracts

During Phase 9 Batch 3 contract closure, six critical interface alignments were verified and permanently frozen. The backend development phase must strictly respect these frozen contracts:

### B3-01: Blueprint Content Envelope Property Name
- **Frozen Contract:** Blueprint synthesized sections are returned under property `content` (a dictionary mapping canonical section keys to section objects), **NOT** `sections`.
- **Backend Model:** `BlueprintContentResponse(..., content=content)` in `backend/app/api/schemas/blueprint.py`.
- **Frontend Consumption:** `const sections = blueprintContent?.content || {}` in `StudentBlueprintWorkspace.tsx` and `client.ts`.
- **Rule:** Backend must never rename `content` to `sections`.

### B3-02: Targeted Blueprint Retry Payload Structure
- **Frozen Contract:** When a student requests a retry for a specific failed or rejected section, the request body payload is serialized as:
```json
{
  "target_output_key": "tech_stack"
}
```
- **Rule:** Full generation retry omits the body or sends `{ target_output_key: null }`. The backend must not expect an array named `sections`.

### B3-03: Mentor At-Risk Filtering Query Parameters
- **Frozen Contract:** `GET /api/v1/mentors/at-risk` accepts the following query parameters:
  - `health`: optional string filter (`"WARNING"` or `"CRITICAL"`)
  - `group_id`: optional UUID filter for supervised cohort
- **Rule:** Backend does not accept a server-side text `search` query parameter on this endpoint; client-side searching is applied over the returned array.

### B3-04: Global Search Item Schema Optional Identifier
- **Frozen Contract:** `SearchResultItem` provides an optional `id?: string | null` alongside `title`, `subtitle`, `resource_type`, `url`, `badge`, and `metadata`.
- **Rule:** When an entity has a canonical UUID, backend supplies it in `id` for stable React list rendering.

### B3-05: Blueprint QA Evaluated Criteria Field Name
- **Frozen Contract:** The scorecard criteria returned in `BlueprintQAFeedback` is supplied under `evaluated_criteria: Record<string, number>`, **NOT** `rubric`.
- **Rule:** Backend must serialize the dictionary of criterion scores (e.g., `{"architectural_completeness": 85}`) under `evaluated_criteria`.

### B3-06: Blueprint Approval Response Envelope
- **Frozen Contract:** `POST /api/v1/projects/{projectId}/blueprint/approve` returns:
```json
{
  "success": true,
  "status": "APPROVED",
  "approved_at": "2026-09-18T16:00:00Z"
}
```
- **Rule:** `blueprint_id` and `project_id` are optional in the response envelope since they are already known from the request path. Backend is not required to inject redundant ID fields.


## 8. Authentication Contract

The frontend relies on Supabase Auth for client session management, credential collection, and JWT issuance, combined with the backend's authoritative `/api/v1/auth/me` endpoint for application identity and role resolution.

### 8.1 JWT Transport & Headers
- **Standard Requests:** Every request dispatched via `apiFetch<T>` injects the Supabase access token in the `Authorization` header:
  `Authorization: Bearer <jwt_access_token>`
- **SSE Exception:** Browser native `EventSource` does not permit custom headers. For `GET /api/v1/projects/{projectId}/blueprint/events`, the JWT token is passed as a URL query parameter:
  `?token=${encodeURIComponent(token)}`
  The backend dependency explicitly supports query token extraction strictly for endpoints ending in `/events`. Normal REST endpoints reject query-based tokens.

### 8.2 Session Lifecycle & Authoritative Role Resolution
1. **Initial Boot:** `AuthProvider` calls `supabase.auth.getSession()`.
2. **Session Restoration:** Upon acquiring a session, `AuthProvider` immediately fetches backend authorization via `GET /api/v1/auth/me`.
3. **Authoritative Roles:** The frontend never assumes roles from JWT claims or user metadata alone; the backend response from `/api/v1/auth/me` determines whether the user is `STUDENT`, `MENTOR`, or `ADMIN`.
4. **Session Change Listener:** `supabase.auth.onAuthStateChange` triggers re-resolution on `SIGNED_IN`, `TOKEN_REFRESHED`, and `USER_UPDATED`. On `SIGNED_OUT`, state is set to `UNAUTHENTICATED`.

### 8.3 Account Status Lifecycle Boundary
- **Active Account:** `status === 'ACTIVE'` grants normal access to role-authorized workspaces.
- **Suspended Account:** `status === 'SUSPENDED'` triggers backend HTTP 403 with error code `AUTH_ACCOUNT_SUSPENDED`. `AuthProvider` sets user status to `SUSPENDED` and `ProtectedRoute` immediately renders the `AccountStatus` view (SYS04), halting workspace access.
- **Inactive Account:** `status === 'INACTIVE'` triggers backend HTTP 403 with error code `AUTH_ACCOUNT_INACTIVE`. Handled identically to suspended accounts.

### 8.4 Deep-Link Preservation & Safe returnTo Handling
When an unauthenticated caller attempts to access a protected workspace URL (e.g., `/student/projects/proj-100/blueprint`), `ProtectedRoute` captures the current URL in `?returnTo=` and redirects to the appropriate login page (`/auth/student/sign-in`, `/auth/mentor/sign-in`, `/auth/admin/sign-in`).
- **Security Validation:** `returnTo.ts` enforces strict sanitization against open redirect attacks:
  - Must begin with a single slash `/`.
  - Rejects protocol prefixes (`http:`, `https:`).
  - Rejects protocol-relative URLs (`//attacker.com`).
  - Rejects backslash escapes (`/\\attacker.com`).
  - Rejects control characters and `javascript:` URIs.

### 8.5 401 vs 403 vs 404 HTTP Semantics
- **401 Unauthorized:** Missing, malformed, or expired JWT. Triggers session invalidation and redirect to login.
- **403 Forbidden:** Valid JWT, but the user is forbidden from accessing the target resource due to:
  - Account suspension/inactivity (`AUTH_ACCOUNT_SUSPENDED`, `AUTH_ACCOUNT_INACTIVE`).
  - Role mismatch (`ROLE_MISMATCH`).
  - Cross-tenant or cross-student resource access.
- **404 Not Found:** Entity does not exist or does not belong to the user's accessible scope.

---

## 9. Authorization & Role Model Contract

GrowFlow implements three canonical role boundaries:
- **Student = BUILD**
- **Mentor = SUPERVISE**
- **Admin = GOVERN**

```text
                +----------------------------------------+
                |           GrowFlow Platform            |
                +----------------------------------------+
                     /              |               \
                    /               |                \
                   v                v                 v
        +---------------+   +---------------+   +---------------+
        |    STUDENT    |   |    MENTOR     |   |     ADMIN     |
        |     BUILD     |   |   SUPERVISE   |   |    GOVERN     |
        +---------------+   +---------------+   +---------------+
        | Own Projects  |   | Cohort Groups |   | User Accounts |
        | Own Tasks     |   | Student Projs |   | System Health |
        | Own Blueprint |   | Definitions   |   | AI Observatory|
        | Assessment    |   | Help Queue    |   | Audit Logs    |
        | AI Mentor     |   | Mentor Notes  |   | RAG Posture   |
        +---------------+   +---------------+   +---------------+
```

### 9.1 Boundary Enforcement Rules
1. **Frontend Route Guards Are UX Shields, Not Security:** `ProtectedRoute` prevents role collision in the browser UI, but backend route dependencies (`RequireStudent`, `RequireMentor`, `RequireAdmin`) are strictly authoritative.
2. **Student Isolation:** Students may read and mutate only project instances where `student_id == current_user.id`. Any attempt to query or modify another student's project must return `404 Not Found` (or `403 Forbidden`).
3. **Mentor Supervision:** Mentors may supervise only student instances enrolled in groups they supervise (`mentor_id == current_user.id`) or specifically assigned to them.
4. **Admin Governance:** Admin accounts have platform-wide governance access across all entities (AD01–AD29). However, admins do not perform student operational mutations (e.g. they do not generate blueprints or submit assessment answers).
5. **No Public Admin Registration:** The admin workspace is accessed only through `/auth/admin/sign-in`. There is no public self-service sign-up for Admin accounts.

---

## 10. Project Lifecycle Contract

GrowFlow models an 8-phase canonical project lifecycle state machine:

```text
  [ IDEA ]
     │
     ▼
  [ ASSESSMENT ]  ──> (15 Questions: 10 Core + 5 Adaptive)
     │
     ▼
  [ BLUEPRINT ]   ──> (AI Synthesis -> QA Judge -> Student Approval)
     │
     ▼
  [ PLANNING ]    ──> (Milestones, Task Breakdown, Risk Identification)
     │
     ▼
  [ IMPLEMENTATION ]  (GitHub Commits, Task Progress, Execution)
     │
     ▼
  [ TESTING ]     ──> (Verification & Acceptance Criteria)
     │
     ▼
  [ DEPLOYMENT ]  ──> (Production Release & Documentation)
     │
     ▼
  [ COMPLETED ]
```

### 10.1 Lifecycle Entity Relationships
- **Project Instance:** Root entity holding phase (`current_phase`), health (`health`), and progress percentage (`progress_percentage`).
- **Milestones:** Canonical stage deliverables and gate checkpoints.
- **Tasks:** Granular work items mapped to phases and milestones.
- **Progress Invariant:** Task completion increments milestone progress, which aggregates into overall project progress percentage.
- **Phase Advancement:** Handled via `POST /api/v1/projects/{id}/phase`. Advancing past `BLUEPRINT` strictly requires `status === 'APPROVED'` in Stage 3.

---

## 11. Assessment Contract

The assessment workflow evaluates student skill, project alignment, and technical complexity through a 15-question structured interview.

### 11.1 Session Structure
- **Questions 1 to 10:** Standardized core questions covering architectural boundaries, tech stack familiarity, data model requirements, and deployment goals.
- **Questions 11 to 15:** Dynamic, adaptive questions generated based on previous answers, flagged with `is_adaptive: true`.
- **Eligibility:** Reaching `answered_count >= 15` sets `is_complete_eligible: true` in `AssessmentAnswerSubmitResponse`.

### 11.2 Result Synthesis
Calling `POST /api/v1/projects/{id}/assessment/complete` finalizes the session and computes:
- `overall_score`: 0 to 100.
- `readiness_tier`: `'HIGH'` (score >= 80), `'MODERATE'` (score 60–79), `'NEEDS_REFINEMENT'` (score < 60).
- `dimension_scores`: Breakdown across dimensions (e.g. `architecture`, `feasibility`, `stack_depth`, `security`).
- `identified_gaps`: Specific technical risks discovered during the assessment.
- `recommendations`: Prescribed focus areas for blueprint generation.

---

## 12. Blueprint Contract (Stage 3 Synthesis)

Blueprint synthesis is the core AI-driven architectural engine of GrowFlow.

### 12.1 Canonical 10 Sections
Synthesis generates exactly 10 canonical sections in deterministic order:
1. `project_profile` (Profile & Domain Context)
2. `tech_stack` (Architecture & Technical Stack)
3. `features` (System Modules & Features)
4. `specifications` (Data Models & Schemas)
5. `mvp` (Minimum Viable Scope)
6. `duration` (Sprint & Timeline Plan)
7. `risks` (Technical Risks & Mitigations)
8. `tasks` (Granular Work Breakdown)
9. `milestones` (Stage Deliverable Gates)
10. `readme` (Production README Guide)

### 12.2 Lifecycle & Atomic Promotion
```text
  Approved V1 (Active)
       │
       ▼ (Student requests scope change)
  Change Request & Impact Analysis
       │
       ▼ (Student confirms regeneration)
  Candidate V2 (Synthesizing in background)
       │
       ▼ (LangGraph execution & QA evaluation)
  QA Evaluation (Score & Criteria)
       │
  ┌────┴────────────────────────┐
  ▼                             ▼
QA Passed (>= 70)             QA Rejected (< 70)
  │                             │
  ▼                             ▼
Ready For Approval            Targeted / Full Retry
  │                             │
  ▼ (Student approves)          │ (V1 remains active!)
Atomic Promotion
  │
  ▼
Approved V2 (V1 Superseded)
```

- **Failure Isolation:** Generation or validation failures in candidate versions must **NEVER** overwrite or corrupt the previously approved blueprint version. The active approved blueprint remains intact.

### 12.3 Status Invariants
- `NOT_STARTED`: Initial state prior to generation.
- `GENERATING`: Background LangGraph execution active.
- `VALIDATING`: AI Judge QA scoring in progress.
- `QA_REJECTED`: QA score failed to meet threshold (< 70). Requires targeted retry.
- `READY_FOR_APPROVAL`: QA passed; awaiting student review.
- `APPROVED`: Student approved; blueprint locked; Stage 4 Planning unlocked.
- `FAILED`: Unhandled synthesis failure; triggers retry options.

---

## 13. Background Job & Server-Sent Events (SSE) Contract

GrowFlow implements asynchronous execution for long-running AI synthesis tasks.

### 13.1 SSE Connection Lifecycle
1. **Client Connection:** `subscribeBlueprintEvents()` instantiates `new EventSource(url + '?token=' + token)`.
2. **Event Format:**
   - Name: `event: update`
   - ID: `id: <projectId>_<timestamp>_<seq>`
   - Keepalive: `: keep-alive\n\n` emitted every 15 seconds to prevent gateway timeout.
   - Reconnect: `retry: 2000` instructed to client.
3. **Terminal States:** When `status` reaches `["READY_FOR_APPROVAL", "APPROVED", "FAILED", "QA_REJECTED"]`, the backend sends the final event and closes the HTTP stream.
4. **Client Teardown:** `StudentBlueprint.tsx` detects terminal status, closes the `EventSource`, and calls `getBlueprintContent()`.

### 13.2 Polling Fallback
If the SSE stream fails due to browser network disconnect or proxy blockage (`es.onerror`), the frontend transparently falls back to polling `GET /api/v1/projects/{id}/blueprint/status` every 1500ms until a terminal state is reached.

---

## 14. AI Contract & Provider Gateway

### 14.1 Strict Server-Side Isolation
- **Invariant:** The frontend **NEVER** holds provider API keys (OpenRouter, OpenAI, Anthropic, Gemini) and **NEVER** calls AI provider APIs directly.
- All AI capabilities are mediated by the backend **AI Provider Gateway** and orchestrated via **LangGraph agents**.
- Responses delivered to the frontend are structured domain schemas, not raw model completions.

### 14.2 AI Mentor vs Mentor AI
- **Student AI Mentor (S29):** Scoped strictly to the student's project instance. Reads project profile, assessment result, and approved blueprint. Can suggest actions with structured payloads.
- **Mentor AI (M09, M36):** Scoped to cohort groups or the mentor's supervised portfolio. Provides pedagogical assistance and detects at-risk patterns.


## 15. Tasks, Milestones, Risks, and Roadmap Contracts

The execution phase (Stage 4 Planning through Stage 7 Deployment) tracks granular delivery.

### 15.1 Tasks Contract
- **Endpoints:**
  - `GET /api/v1/projects/{id}/tasks`
  - `POST /api/v1/projects/{id}/tasks`
  - `GET /api/v1/projects/{id}/tasks/{taskId}`
  - `PATCH /api/v1/projects/{id}/tasks/{taskId}`
  - `DELETE /api/v1/projects/{id}/tasks/{taskId}`
- **Statuses:** `'TODO'`, `'IN_PROGRESS'`, `'BLOCKED'`, `'COMPLETED'`.
- **Phases:** `'PLANNING'`, `'IMPLEMENTATION'`, `'TESTING'`, `'DEPLOYMENT'`.
- **Priorities:** `'LOW'`, `'MEDIUM'`, `'HIGH'`, `'CRITICAL'`.
- **Invariants:** Deleting a task requires confirmation. Completed tasks require setting `completed_at` timestamp.

### 15.2 Milestones Contract
- **Endpoints:**
  - `GET /api/v1/projects/{id}/milestones`
  - `POST /api/v1/projects/{id}/milestones`
  - `GET /api/v1/projects/{id}/milestones/{milestoneId}`
  - `PATCH /api/v1/projects/{id}/milestones/{milestoneId}`
- **Statuses:** `'UPCOMING'`, `'IN_PROGRESS'`, `'COMPLETED'`, `'AT_RISK'`.
- **Fields:** `gate_code` (e.g. `"GATE-01"`), `deliverables` (string array), `progress_percent` (0–100), `target_date`.
- **Aggregation:** `task_count` and `completed_task_count` reflect linked tasks.

### 15.3 Risks Contract
- **Endpoints:**
  - `GET /api/v1/projects/{id}/risks`
  - `POST /api/v1/projects/{id}/risks`
  - `GET /api/v1/projects/{id}/risks/{riskId}`
  - `PATCH /api/v1/projects/{id}/risks/{riskId}`
  - `DELETE /api/v1/projects/{id}/risks/{riskId}`
- **Fields:** `severity` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), `probability` (`LOW`, `MEDIUM`, `HIGH`), `impact` (`LOW`, `MEDIUM`, `HIGH`), `status` (`OPEN`, `MITIGATING`, `RESOLVED`, `ACCEPTED`), `mitigation`, `owner`, `review_date`.

### 15.4 Roadmap Contract
- **Endpoint:** `GET /api/v1/projects/{id}/roadmap`
- **Aggregation Invariant:** Returns unified summary (`total_milestones`, `completed_milestones`, `total_tasks`, `completed_tasks`, `overdue_tasks_count`, `blocked_tasks_count`, `overall_progress`) alongside milestone timeline and grouped task queues (`overdue`, `blocked`, `in_progress`, `upcoming`, `completed`).

---

## 16. Documents & RAG Contract

### 16.1 Canonical Project Documents vs Derived RAG Data
- **Canonical Documents:** Persisted in PostgreSQL (`DocumentResponse`) representing project specifications, architecture briefs, blueprints, and READMEs. Editable and downloadable as raw Markdown.
- **RAG Data:** Ephemeral vector embeddings derived from canonical documents. RAG data is strictly rebuildable and never treated as a source of truth.

### 16.2 Document Endpoints
- `GET /api/v1/projects/{id}/documents` (Filterable by `doc_type`, `status`, `search`)
- `POST /api/v1/projects/{id}/documents`
- `GET /api/v1/projects/{id}/documents/{docId}`
- `PATCH /api/v1/projects/{id}/documents/{docId}`
- `GET /api/v1/projects/{id}/documents/{docId}/download` (Serves `text/markdown`)

---

## 17. GitHub Integration Contract

### 17.1 External Observation Only
- **Core Rule:** GitHub is an external observation and verification channel. GrowFlow does **NOT** synthesize a synthetic GitHub database or attempt write operations (such as code commits or PR merges).
- **Endpoints:**
  - `GET /api/v1/projects/{id}/github`
  - `POST /api/v1/projects/{id}/github/connect` (`{ repository_url, default_branch }`)
  - `POST /api/v1/projects/{id}/github/sync`
  - `DELETE /api/v1/projects/{id}/github/disconnect`
- **Response Shape:** Returns `GitHubIntegrationResponse` containing `connection_status` (`'NOT_CONNECTED'`, `'CONNECTED'`, `'SYNCING'`, `'ERROR'`), `commit_count`, `last_sync_at`, `sync_error`, and `cached_commits_preview` (latest commits with sha, message, author, date).

---

## 18. Activity Contract

### 18.1 Domain Event Sourced
- **Rule:** Activity timelines are derived from real domain events published to the transactional outbox/event store. The frontend never accepts fabricated activity entries.
- **Payload Shape (`ActivityItemResponse`):**
  - `id`: Event UUID
  - `event_type`: Canonical event name (e.g., `"TaskCompleted"`, `"BlueprintApproved"`)
  - `title`: Human-readable summary
  - `description`: Extended narrative
  - `actor_role`: `"STUDENT"` | `"MENTOR"` | `"ADMIN"` | `"SYSTEM"`
  - `actor_id`: Actor UUID
  - `resource_type`: `"project"` | `"task"` | `"blueprint"` | `"milestone"`
  - `resource_id`: Entity UUID
  - `occurred_at`: ISO8601 timestamp
  - `metadata`: Contextual dictionary

---

## 19. Help Requests & Mentor Feedback / Notes

### 19.1 Student Help Requests
- Student submits blocker via `POST /api/v1/projects/{id}/help-requests` with `subject`, `description`, `category`, `priority`.
- Supervising mentor inspects requests on `GET /api/v1/mentors/help-requests` and responds via `POST /api/v1/mentors/help-requests/{reqId}/respond` with `mentor_response` and `status: 'RESOLVED'`.

### 19.2 Mentor Notes & Feedback
- Mentor posts notes on a project instance via `POST /api/v1/mentors/notes` (payload specifies `project_instance_id`, `title`, `message`, `note_type`).
- Student views notes on S31 (`GET /api/v1/projects/{id}/mentor-notes`) and acknowledges them via `POST /api/v1/projects/{id}/mentor-notes/{nId}/acknowledge`.

---

## 20. Project Change & Regeneration Contract

When a project requires structural changes during execution, GrowFlow executes a controlled 4-step workflow:

```text
  [ 1. Analyze Change ]
         │ (POST /projects/{id}/changes/analyze)
         ▼
  [ 2. Impact Review ]   ──> Surfaces affected sections, risk level, & task delta
         │ (Student inspects on S32)
         ▼
  [ 3. Confirm Intent ]  ──> Dispatches confirmation with idempotency_key
         │ (POST /projects/{id}/changes/{cId}/confirm)
         ▼
  [ 4. Candidate V2 ]    ──> Synthesizes candidate version without touching V1;
                             promotes atomically upon student approval.
```

- **Operational Invariant:** The change workflow must **NOT** silently delete or mutate existing completed tasks, milestones, or external GitHub links without student confirmation.

---

## 21. Global Search Contract

### 21.1 Search Architecture
- **Endpoint:** `GET /api/v1/search?q={query}&category={category}&limit={limit}`
- **Debounce:** Frontend debounces keystrokes by 300ms.
- **Categories:** `"projects"`, `"tasks"`, `"documents"`, `"groups"`, `"users"`, `"definitions"`, or omitted for all.
- **Limit:** Default 20, max 50.
- **Result Item:** `SearchResultItem` provides optional `id?: string | null` (per B3-04), `title`, `subtitle`, `resource_type`, `url`, `badge`, and `metadata`.

### 21.2 Role-Aware Scope Matrix
- **Student (`BUILD`):** Own project instances, own tasks, own milestones, own documents, active mentor definitions catalog, own help requests.
- **Mentor (`SUPERVISE`):** Supervised cohort groups, supervised students, supervised project instances, supervised tasks, help requests, authored definitions.
- **Admin (`GOVERN`):** Platform-wide user accounts, groups, project definitions, project instances, domain events, security investigations, platform documents.

---

## 22. Notification Contract

### 22.1 Endpoints
- `GET /api/v1/notifications?limit=20&offset=0&unread_only=false`
- `GET /api/v1/notifications/unread-count` (returns `{ unread_count: number }`)
- `PATCH /api/v1/notifications/{id}/read`
- `POST /api/v1/notifications/mark-all-read` (returns `{ marked_count: number }`)

### 22.2 The Eight Approved Notification Event Types
The backend event dispatcher emits notifications strictly matching these 8 canonical event types:
1. **`MentorNoteCreated`:** Mentor posts a note on student project. Recipient: Project student.
2. **`MentorNoteAcknowledged`:** Student acknowledges note. Recipient: Supervising mentor.
3. **`HelpRequestCreated`:** Student files help request. Recipient: Supervising mentor.
4. **`HelpRequestResponded`:** Mentor answers help request. Recipient: Student.
5. **`BlueprintGenerated`:** Blueprint synthesis reaches `READY_FOR_APPROVAL`. Recipient: Student.
6. **`BlueprintApproved`:** Student approves blueprint. Recipient: Student + Supervising mentor.
7. **`ProjectChangeRequested`:** Scope change analyzed. Recipient: Supervising mentor.
8. **`ProjectChangeCompleted`:** Scope change confirmed & promoted. Recipient: Student + Supervising mentor. Unrelated students or mentors must **NOT** be notified.


## 23. Admin Frontend Contract (AD01–AD29)

The Admin workspace provides platform governance across 9 core functional areas:

### 23.1 Overview (AD01)
- **Route:** `/admin/overview`
- **Endpoint:** `GET /api/v1/admin/overview`
- **Response Shape:** `AdminOverviewResponse` (`total_mentors`, `active_mentors`, `total_students`, `active_students`, `total_groups`, `active_groups`, `total_projects`, `active_projects`, `completed_projects`, `at_risk_projects`).

### 23.2 People Governance (AD02–AD05)
- **AD02 Mentor Directory:** `GET /api/v1/admin/mentors?search=&status=` -> `AdminMentorSummary[]`
- **AD03 Mentor Detail:** `GET /api/v1/admin/mentors/{mentorId}` -> `AdminMentorDetail` (Cohorts, supervised students, bio)
- **AD04 Student Directory:** `GET /api/v1/admin/students?search=&track=&status=` -> `AdminStudentSummary[]`
- **AD05 Student Detail:** `GET /api/v1/admin/students/{studentId}` -> `AdminStudentDetail` (Enrolled cohorts, technologies, project portfolio)

### 23.3 Group Governance (AD06–AD07)
- **AD06 Groups Directory:** `GET /api/v1/admin/groups?search=&status=` -> `AdminGroupSummary[]`
- **AD07 Group Detail:** `GET /api/v1/admin/groups/{groupId}` -> `AdminGroupDetail` (Assigned mentor, student roster, active projects)

### 23.4 Project Governance (AD08–AD10)
- **AD08 Projects Directory:** `GET /api/v1/admin/projects?search=&phase=&health=&status=` -> `AdminProjectSummary[]`
- **AD09 Definition Monitoring:** `GET /api/v1/admin/definitions` -> `AdminProjectDefinitionSummary[]`, detail via `/admin/definitions/{dId}`
- **AD10 Instance Monitoring:** `GET /api/v1/admin/instances` -> `AdminInstanceMonitoringResponse` (Instance health breakdown: healthy, warning, critical counts)

### 23.5 AI Observatory (AD11–AD18)
- **AD11 AI Observatory:** `GET /api/v1/admin/ai/observatory` -> `AdminAIObservatoryResponse` (Gateway posture, active background jobs, key rotation strategy)
- **AD12 AI Usage:** `GET /api/v1/admin/ai/usage` -> `AdminAIUsageResponse` (Time trend, capability breakdown, project distributions)
- **AD13 Agent Executions:** `GET /api/v1/admin/ai/executions?status=&job_type=&project_id=&limit=&offset=` -> `AdminAIExecutionsResponse`
- **AD14 AI Trace Detail:** `GET /api/v1/admin/ai/executions/{eId}` -> `AdminAITraceDetailResponse` (Pipeline stages, QA judge scorecard, domain events)
- **AD15 AI Quality:** `GET /api/v1/admin/ai/quality` -> `AdminAIQualityResponse` (Pass rates, criteria averages, score distribution)
- **AD16 Cost & Usage:** `GET /api/v1/admin/ai/cost` -> `AdminAICostResponse` (Execution volume, active models, billing telemetry posture)
- **AD17 Cost Breakdown:** `GET /api/v1/admin/ai/cost/{dimension}` -> `AdminAICostDimensionResponse`
- **AD18 API Key Pool:** `GET /api/v1/admin/ai/keys` -> `AdminAIKeysResponse` (Active slots, masked identifiers, rotation state)

### 23.6 System Health (AD19–AD20)
- **AD19 System Health:** `GET /api/v1/admin/health` -> `AdminSystemHealthResponse` (Subsystems: DB pool, transactional outbox pending/failed, AI keys)
- **AD20 Component Detail:** `GET /api/v1/admin/health/{cId}` -> `AdminSubsystemDetail` (Diagnostics and recent failure log)

### 23.7 Documents & RAG (AD21–AD23)
- **AD21 Platform Documents:** `GET /api/v1/admin/documents` -> `AdminDocumentsResponse`
- **AD22 RAG Diagnostics:** `GET /api/v1/admin/documents/rag` -> `AdminRAGDiagnostics` (Vector store type, embedding model, top_k, chunk size)
- **AD23 Document Generation Jobs:** `GET /api/v1/admin/documents/generation` -> `AdminGenerationJobsResponse`

### 23.8 Security & Audit (AD24–AD27)
- **AD24 Security Overview:** `GET /api/v1/admin/security/overview` -> `AdminSecurityOverview` (User postures: active, suspended, inactive)
- **AD25 Audit Log:** `GET /api/v1/admin/security/audit?search=&actor_role=&event_type=&limit=&offset=` -> `AdminAuditLogResponse`
- **AD26 Investigations:** `GET /api/v1/admin/security/investigations` -> `AdminInvestigationOverviewResponse` (Flagged security resources)
- **AD27 Investigation Detail:** `GET /api/v1/admin/security/investigations/{iId}` -> Resource inspection detail

### 23.9 Platform Analytics (AD28–AD29)
- **AD28 Platform Analytics:** `GET /api/v1/admin/analytics` -> `AdminPlatformAnalyticsResponse` (Phase distributions, health ratios, task completion rates)
- **AD29 Analytics Dimension Detail:** `GET /api/v1/admin/analytics/{dimension}` -> `AdminAnalyticsDimensionDetail`

---

## 24. System State Contract (SYS01–SYS10)

| State ID | Name | Trigger | Frontend Behavior | Backend Requirement | Dedicated Route? |
|---|---|---|---|---|---|
| **SYS01** | Not Found | Route mismatch or 404 response | Displays NotFound page with return dashboard button | Return 404 envelope when entity missing | Yes (`/404`, `*`) |
| **SYS02** | Forbidden | Role mismatch or cross-tenant query | Renders `ForbiddenView` with role error explanation | Return 403 with code `ROLE_MISMATCH` | Yes (`/403`) & inline |
| **SYS03** | Auth Required | Unauthenticated request or expired token | Redirects to login with safe `?returnTo=` | Return 401 with code `AUTH_MISSING_TOKEN` | Yes (`/401`) & redirect |
| **SYS04** | Account Status | Backend returns suspended or inactive | Renders `AccountStatus` view (read-only notice) | Return 403 with `AUTH_ACCOUNT_SUSPENDED` or `AUTH_ACCOUNT_INACTIVE` | Yes (`/account-status`) |
| **SYS05** | Error Boundary | React unhandled exception | Displays crash shield with incident ID and reload trigger | None (client-only shield) | No (class boundary) |
| **SYS06** | Network Error | Fetch failure / status 0 | Renders `NetworkErrorState` with retry button | Ensure CORS allows `VITE_API_BASE_URL` | No (inline component) |
| **SYS07** | AI Unavailable | Gateway returns 503 or `ai_available: false` | Displays `AIServiceUnavailableNotice` non-blocking banner | Return graceful fallback flag | No (inline component) |
| **SYS08** | AI Execution Failed| Blueprint or synthesis reaches `FAILED` | Renders `AIExecutionFailedState` with retry options | Surface sanitized error message | No (inline component) |
| **SYS09** | AI Progress | Background synthesis in progress | Renders `AIExecutionProgressState` with progress bar | Stream SSE events or status polling | No (inline component) |
| **SYS10** | RAG Processing | Document embedding in progress | Displays `RAGProcessingState` banner | Asynchronous background indexing | No (inline component) |

---

## 25. Error Handling Contract

The frontend standardizes all error processing through `ApiClientError` (`frontend/src/lib/api/errors.ts`) and expects the backend canonical error envelope:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Project instance proj_999 was not found",
    "details": {
      "resource_id": "proj_999",
      "resource_type": "project_instance"
    }
  },
  "meta": {
    "timestamp": "2026-09-18T16:45:00Z",
    "request_id": "req_abc123"
  }
}
```

### 25.1 Canonical Machine-Readable Error Codes
- **Authentication:** `AUTH_MISSING_TOKEN`, `AUTH_INVALID_TOKEN_FORMAT`, `AUTH_USER_NOT_FOUND`.
- **Authorization & Account:** `AUTH_ACCOUNT_SUSPENDED`, `AUTH_ACCOUNT_INACTIVE`, `ROLE_MISMATCH`, `PROJECT_ACCESS_DENIED`.
- **Validation:** `VALIDATION_ERROR`, `INVALID_PHASE_TRANSITION`, `INVALID_PAYLOAD`.
- **Resources:** `RESOURCE_NOT_FOUND`, `RESOURCE_ALREADY_EXISTS`, `CONFLICT`.
- **AI & Reliability:** `AI_GATEWAY_TIMEOUT`, `AI_PROVIDER_UNAVAILABLE`, `RATE_LIMIT_EXCEEDED`.

---

## 26. Offline & Network Resilience Contract

1. **Browser Online/Offline Detection:** `OfflineBanner` monitors `window.addEventListener('online' | 'offline')`.
2. **Zero Speculative Writes:** When offline, the frontend disables form submission and mutation triggers. It does **NOT** synthesize optimistic offline writes to avoid data corruption.
3. **SSE Disruption Recovery:** If a network drop interrupts an SSE stream, the frontend attempts automatic reconnection via EventSource backoff, followed by polling fallback to `/status`.

---

## 27. Responsive Dependencies & UI Constraints

1. **Bounded List Payloads:** Frontend list components expect default page bounds (e.g., `limit: 20` for notifications and audit logs; `limit: 50` for search) to preserve 60fps rendering across mobile and desktop.
2. **Debounced Query Execution:** All search inputs are debounced by 300ms. Backend query planners should anticipate spaced keystroke bursts rather than character-by-character queries.
3. **Drawer & Modal Layouts:** Mobile drawers and popovers render summary representations; heavy detail objects are queried on-demand when opening detail routes.

---

## 28. Environment & Configuration Contract

### 28.1 Browser-Safe Variables (`frontend/.env.example`)
The frontend runtime exposes **ONLY** the following browser-safe variables via `import.meta.env`:
- `VITE_API_BASE_URL`: Base URL for the FastAPI backend (e.g. `http://localhost:8000`). Trimmed of trailing slashes.
- `VITE_SUPABASE_URL`: Public Supabase project URL.
- `VITE_SUPABASE_ANON_KEY`: Public anonymous client key (safe for browser with Supabase RLS).
- `VITE_APP_ENV`: `"development"` | `"production"`.
- `VITE_APP_NAME`: Application name (`"GrowFlow"`).

### 28.2 Strict Prohibition of Server Secrets
The following secrets must **NEVER** be placed in frontend configuration, environment files, or client-side bundles:
- `SUPABASE_SERVICE_ROLE_KEY`
- Database connection strings or PostgreSQL passwords
- LLM Provider keys (OpenRouter, OpenAI, Anthropic, Gemini)
- LangSmith API keys or Tavily search keys
- JWT signing secrets or private keys

---

## 29. Security Contract

1. **Bearer Authentication:** All non-public REST requests must provide a valid JWT via the `Authorization` header.
2. **Query Token Exception:** `?token=` is restricted exclusively to `/api/v1/projects/{id}/blueprint/events`.
3. **Fail-Closed Access:** Unauthenticated or unauthorized calls must fail closed with 401 or 403.
4. **Tenant Isolation:** Cross-tenant queries between students or unassigned mentors must be rejected by backend authorization dependencies.
5. **Redirect Defense:** All `returnTo` login redirects must validate through `getSafeReturnTo()` to prevent open redirect vulnerabilities.


## 30. Frontend → Backend Dependency Matrix

| Functional Area | Primary Surface | Key Backend Endpoints | Data Required | Mutation Type | Role | Status |
|---|---|---|---|---|---|---|
| **Identity & Auth** | Login, Guards, Headers | `GET /api/v1/auth/me` | `CurrentUserIdentity` | Read | Any Auth | `VERIFIED` |
| **Student Profile** | Profile (X03) | `GET/PATCH /api/v1/students/me` | `StudentProfile` | Read / Update | STUDENT | `VERIFIED` |
| **Project Lifecycle** | Overview (S15), Projects (S02) | `GET/POST /api/v1/projects`, `/phase`, `/health` | `ProjectResponse`, `ProjectOverviewResponse` | Create / Advance | STUDENT | `VERIFIED` |
| **Definition Catalog** | Catalog (S04, S05) | `GET /api/v1/project-definitions/catalog`, `/select` | `ProjectDefinitionCatalogItem` | Read / Select | STUDENT | `VERIFIED` |
| **Assessment** | Assessment (S07–S11) | `POST /start`, `GET /questions/:idx`, `POST /answers`, `POST /complete` | `AssessmentSessionStatus`, `AssessmentResultResponse` | Submit / Finalize | STUDENT | `VERIFIED` |
| **Blueprint Synthesis**| Blueprint (S12–S14) | `GET /status`, `POST /generate`, `POST /retry`, `POST /approve`, `GET /content` | `BlueprintStatusResponse`, `BlueprintContentResponse` | Generate / Approve | STUDENT | `VERIFIED` |
| **Blueprint SSE** | Blueprint (S12) | `GET /api/v1/projects/:id/blueprint/events` | SSE Stream (`BlueprintStatusResponse`) | Read (Stream) | STUDENT | `VERIFIED` |
| **Tasks & Milestones** | Tasks (S18), Milestones (S20)| `GET/POST/PATCH/DELETE /tasks`, `/milestones` | `TaskResponse[]`, `MilestoneResponse[]` | Full CRUD | STUDENT | `VERIFIED` |
| **Risks & Roadmap** | Risks (S22), Roadmap (S24) | `GET/POST/PATCH/DELETE /risks`, `GET /roadmap` | `RiskResponse[]`, `RoadmapResponse` | CRUD / Aggregation | STUDENT | `VERIFIED` |
| **Project Documents** | Documents (S25, S26) | `GET/POST/PATCH /documents`, `/download` | `DocumentResponse[]`, Raw Markdown | CRUD / Download | STUDENT | `VERIFIED` |
| **GitHub Observation** | GitHub (S27) | `GET /github`, `POST /connect`, `POST /sync`, `DELETE /disconnect` | `GitHubIntegrationResponse` | Connect / Sync | STUDENT | `VERIFIED` |
| **Activity Timeline** | Activity (S28) | `GET /api/v1/projects/:id/activity` | `ActivityItemResponse[]` | Read (Events) | STUDENT | `VERIFIED` |
| **Student AI Mentor** | AI Mentor (S29) | `GET /ai-mentor`, `POST /ai-mentor/chat`, `POST /execute-action` | `AIMentorConversationResponse` | Prompt / Action | STUDENT | `VERIFIED` |
| **Help Requests** | Help Requests (S30) | `GET/POST /help-requests` | `HelpRequestResponse[]` | Create / Read | STUDENT | `VERIFIED` |
| **Mentor Feedback** | Mentor Feedback (S31) | `GET /mentor-notes`, `POST /mentor-notes/:nId/acknowledge` | `MentorNoteResponse[]` | Acknowledge | STUDENT | `VERIFIED` |
| **Scope Changes** | Changes (S32, S33) | `GET /changes`, `POST /analyze`, `POST /confirm`, `GET /blueprint-versions` | `ProjectChangeResponse`, `BlueprintVersionResponse` | Analyze / Promote | STUDENT | `VERIFIED` |
| **Mentor Groups** | Groups (M02–M08) | `GET/POST /groups`, `/students`, `/projects`, `/activity`, `/ai` | `GroupResponse`, `GroupStudentResponse[]` | Cohort Management| MENTOR | `VERIFIED` |
| **Mentor Definitions** | Definitions (M16–M21) | `GET/POST/PATCH /project-definitions`, `/assign` | `ProjectDefinition[]`, `ProjectDefinitionVersion[]` | Template Authoring| MENTOR | `VERIFIED` |
| **Mentor Supervision** | Instances (M22–M30) | `GET /mentors/project-instances`, `/blueprint`, `/tasks`, etc. | `MentorProjectInstanceDetail` | Supervision Read | MENTOR | `VERIFIED` |
| **Mentor At Risk** | At Risk (M31, M32) | `GET /api/v1/mentors/at-risk?health=&group_id=` | `MentorProjectInstanceSummary[]` | Diagnostic Read | MENTOR | `VERIFIED` |
| **Mentor Help Queue** | Help Requests (M33) | `GET /mentors/help-requests`, `POST /respond` | `MentorHelpRequestSummary[]` | Resolution | MENTOR | `VERIFIED` |
| **Mentor Notes** | Instance Notes (M34) | `POST /api/v1/mentors/notes`, `GET /project-instances/:pId/notes` | `MentorNoteItem[]` | Note Creation | MENTOR | `VERIFIED` |
| **Mentor AI** | Mentor AI (M36) | `GET/POST /mentors/ai` | `MentorAIChatResponse` | Supervision Prompt| MENTOR | `VERIFIED` |
| **Admin Governance** | Admin (AD01–AD10) | `GET /admin/overview`, `/mentors`, `/students`, `/groups`, `/projects` | AD01–AD10 Response Models | Governance Read | ADMIN | `VERIFIED` |
| **Admin AI Obs** | AI Obs (AD11–AD18) | `GET /admin/ai/observatory`, `/usage`, `/executions`, `/cost`, `/keys` | AD11–AD18 Response Models | Observability Read| ADMIN | `VERIFIED` |
| **Admin Health & RAG**| Health/Docs (AD19–AD23)| `GET /admin/health`, `/documents`, `/rag`, `/generation` | AD19–AD23 Response Models | System Health | ADMIN | `VERIFIED` |
| **Admin Audit** | Security (AD24–AD29) | `GET /admin/security/overview`, `/audit`, `/investigations`, `/analytics` | AD24–AD29 Response Models | Audit Inspection | ADMIN | `VERIFIED` |
| **Global Search** | Modal (X01) | `GET /api/v1/search?q=&category=&limit=` | `SearchResponseData` | Scoped Query | Any Auth | `VERIFIED` |
| **Notifications** | Popover (X02) | `GET /notifications`, `/unread-count`, `PATCH /read`, `POST /mark-all-read` | `NotificationItem[]`, `unread_count` | Read Transitions | Any Auth | `VERIFIED` |
| **User Preferences** | Settings (X04) | `GET/PATCH /api/v1/users/me/preferences` | `UserPreferencesResponse` | Update Settings | Any Auth | `VERIFIED` |
| **Public Contact** | Contact (P04) | `POST /api/v1/contact` | `{ success: true, message: string }` | Inquiries | Public | `VERIFIED` |

---

## 31. Known Backend Dependencies & Open Items

An exhaustive inspection of the frozen frontend confirms that all pages have functional, validated routes or approved architectural designs:

1. **Student Onboarding (A07) & Mentor Onboarding (A08):**
   - **Current Implementation:** Handled cleanly inline during initial resource creation (`/student/projects/new` and `/mentor/groups/new`) rather than having redundant standalone interstitial routes.
   - **Backend Requirement:** Backend `PATCH /api/v1/students/me` and `PATCH /api/v1/mentors/me` support onboarding profile enrichment.
   - **Status:** Complete & validated.

2. **Mentor Notes (M14, M34) & Mentor Help Requests (M15, M33):**
   - **Current Implementation:** M14 and M34 operate per project-instance (`GET /api/v1/mentors/project-instances/{pId}/notes` and `POST /api/v1/mentors/notes`). M15 is centralized via M33 (`GET /api/v1/mentors/help-requests`).
   - **Backend Requirement:** Backend already exposes instance-scoped notes and global help requests.
   - **Status:** Complete & validated.

3. **Share Surface (X05):**
   - **Current Implementation:** Inline clipboard URL copy implemented directly within Project Overview (S15) and Project Profile (S06).
   - **Status:** Complete & validated.

---

## 32. Backend Implementation Rules Derived From Frozen Frontend

# Backend Implementation Rules Derived From Frozen Frontend

The following 18 architectural rules are non-negotiable invariants derived directly from the frozen frontend:

1. **Do Not Redesign the Frontend Contract:** Backend development must implement to the established routes, schemas, and parameter names.
2. **Backend is Authoritative for Authorization:** Frontend route guards provide UX clarity; backend dependencies must enforce row-level tenant and role ownership.
3. **Use the Canonical API Envelope:** All success responses must wrap payloads in `{ success: true, message: string, data: T }`. All failure responses must return `{ success: false, error: { code: string, message: string, details?: unknown } }`.
4. **Preserve Existing Authentication Model:** Accept Supabase JWT via `Authorization: Bearer <token>`. Never require bespoke browser session cookies.
5. **Preserve the EventSource Query Token Exception:** Accept query-based tokens (`?token=`) strictly for `/events` endpoints; reject query tokens on all standard REST endpoints.
6. **Preserve Asynchronous Background Execution:** Blueprint synthesis and heavy AI tasks must run asynchronously in background workers, reporting progress via SSE or status polling.
7. **Maintain Project-Scoped AI Isolation:** Student AI Mentor must never access or reveal unassigned project instances or foreign tenant data.
8. **Preserve Notification Recipient Rules:** Emitted notifications must strictly match the 8 canonical event types and route only to relevant project participants.
9. **Preserve the Canonical Lifecycle State Machine:** Maintain the deterministic 8-phase progression (`IDEA` -> `ASSESSMENT` -> `BLUEPRINT` -> `PLANNING` -> `IMPLEMENTATION` -> `TESTING` -> `DEPLOYMENT` -> `COMPLETED`).
10. **Do Not Fabricate Frontend Data:** Activity logs, telemetry, and commit previews must reflect real domain events or provider outputs, not synthetic hardcoded mocks.
11. **Do Not Create Duplicate API Contracts:** Use existing endpoints rather than introducing competing paths (e.g. use `/api/v1/mentors/project-instances` and `/api/v1/mentors/projects/instances` as established).
12. **Do Not Require Frontend Provider Calls:** Frontend must never make direct HTTP calls to OpenRouter, OpenAI, Anthropic, or Gemini.
13. **Do Not Silently Mutate Operational Entities During AI Regeneration:** Scope changes and candidate blueprint generation must not mutate existing approved tasks or milestones without explicit confirmation.
14. **Preserve 401, 403, and 404 Semantics:**
    - 401 for unauthenticated/expired sessions.
    - 403 for account suspension, account inactivity, or role mismatch.
    - 404 for unowned or missing entities.
15. **Preserve Idempotency on Critical Mutations:** Support `idempotency_key` on project change confirmations and blueprint generation requests.
16. **Preserve Cross-Role Resource Isolation:** A student token must never query mentor cohort management endpoints or admin governance routes.
17. **Preserve B3-01 through B3-06 Verified Contracts:**
    - Blueprint content key must be `content` (not `sections`).
    - Targeted retry payload must be `target_output_key` (not `sections`).
    - Mentor at-risk parameters must be `health` and `group_id`.
    - SearchResultItem supports optional `id`.
    - Blueprint QA criteria must be `evaluated_criteria` (not `rubric`).
    - Blueprint approval envelope must match `{ success, status, approved_at }`.
18. **Preserve Standardized Machine Error Codes:** Emit standardized error codes (`AUTH_ACCOUNT_SUSPENDED`, `AUTH_ACCOUNT_INACTIVE`, `RESOURCE_NOT_FOUND`, etc.) inside the canonical error envelope.

---

## 33. Frontend Freeze Rules

The GrowFlow frontend is officially **COMPLETE and FROZEN**.

During backend completion:
- **Zero Frontend Code Edits:** Do not modify `frontend/src/`, route definitions, types, or API client methods.
- **Contract Conflict Protocol:** If a backend requirement genuinely conflicts with the frozen frontend contract:
  1. **STOP** backend implementation on that component.
  2. Document the exact conflict and field mismatch.
  3. Formally request an architectural contract review.
  4. Do not unilaterally alter the frontend to mask a backend gap.

---

## 34. Backend Completion Checklist

### API Transport & Transports
- [ ] Canonical envelope `{ success: true, message: string, data: T }` enforced across all route handlers.
- [ ] Canonical error envelope `{ success: false, error: { code, message, details } }` returned on all exceptions.
- [ ] All 149 client functions have matching backend route controllers and HTTP verbs.
- [ ] CORS configuration permits `VITE_API_BASE_URL` with credentials.

### Authentication & Account Lifecycles
- [ ] Supabase JWT validated via public key / JWKS.
- [ ] `GET /api/v1/auth/me` returns `CurrentUserIdentity` (`id`, `email`, `role`, `status`, `full_name`).
- [ ] Suspended accounts return HTTP 403 with `AUTH_ACCOUNT_SUSPENDED`.
- [ ] Inactive accounts return HTTP 403 with `AUTH_ACCOUNT_INACTIVE`.
- [ ] Query token authentication supported strictly for endpoints ending in `/events`.

### Authorization & Tenants
- [ ] `RequireStudent` dependency guards student workspace mutations.
- [ ] `RequireMentor` dependency guards mentor supervision routes.
- [ ] `RequireAdmin` dependency guards all 29 admin governance endpoints.
- [ ] Student ownership enforced on all `/projects/{id}/*` routes.
- [ ] Mentor cohort scoping enforced on `/groups/{id}/*` routes.

### Projects & Blueprints
- [ ] 8-phase canonical lifecycle enforced.
- [ ] Sequential 10-section blueprint synthesis pipeline implemented.
- [ ] SSE stream emits keepalives, sequence IDs, and terminal state flags.
- [ ] Blueprint content serialized under property `content`.
- [ ] Targeted retry consumes `target_output_key`.
- [ ] QA Judge scorecard emits criteria under `evaluated_criteria`.

### AI & Observability
- [ ] Provider Gateway manages model routing, failover, and key rotation.
- [ ] LangGraph agents orchestrate multi-step synthesis.
- [ ] Admin AI Observatory (AD11–AD18) accurately surfaces gateway posture and job execution traces.
- [ ] Admin System Health (AD19–AD20) reports outbox queue metrics and DB pool status.

---

## 35. Contract Traceability Matrix

| Frontend Surface | Component | API Client Method | Backend Route | Backend Service | Persistence Concept |
|---|---|---|---|---|---|
| User Identity | AuthProvider | `getCurrentUser` | `GET /api/v1/auth/me` | IdentityService | Users Table (`id, role, status`) |
| Student Dashboard | StudentDashboard | `getProjects` | `GET /api/v1/projects` | ProjectService | ProjectInstances (`student_id`) |
| Project Creation | StudentProjectCreate | `createProject` | `POST /api/v1/projects` | ProjectService | ProjectInstances |
| Assessment | StudentAssessment | `submitAssessmentAnswer` | `POST /projects/:id/assessment/answers`| AssessmentService | AssessmentAnswers Table |
| Assessment Result | StudentAssessment | `getAssessmentResult` | `GET /projects/:id/assessment/result` | AssessmentService | AssessmentResults Table |
| Blueprint Stream | StudentBlueprint | `subscribeBlueprintEvents`| `GET /projects/:id/blueprint/events` | BlueprintJobService | Transactional Outbox / SSE |
| Blueprint Content | BlueprintWorkspace | `getBlueprintContent` | `GET /projects/:id/blueprint/content` | BlueprintService | Blueprints (`content` JSONB) |
| Blueprint Approval | StudentBlueprint | `approveBlueprint` | `POST /projects/:id/blueprint/approve` | BlueprintService | Blueprints (`status='APPROVED'`) |
| Task Board | StudentTasks | `createTask` | `POST /projects/:id/tasks` | ExecutionService | Tasks Table |
| Roadmap | StudentRoadmap | `getRoadmap` | `GET /projects/:id/roadmap` | ExecutionService | Milestones + Tasks Aggregation |
| GitHub Integration| StudentGitHub | `syncGitHub` | `POST /projects/:id/github/sync` | GitHubService | GitHubIntegrations Table |
| AI Mentor | StudentAIMentor | `sendAIMentorMessage` | `POST /projects/:id/ai-mentor/chat` | AIMentorService | Conversations Table |
| Scope Changes | StudentProjectChanges| `analyzeProjectChange` | `POST /projects/:id/changes/analyze` | ScopeChangeService | ProjectChanges Table |
| Mentor Overview | MentorOverview | `getMentorOverview` | `GET /api/v1/mentors/overview` | MentorService | Aggregated Cohort Metrics |
| Mentor Groups | GroupsDirectory | `createMentorGroup` | `POST /api/v1/groups` | GroupService | Groups Table (`join_code`) |
| At-Risk Directory | AtRiskDirectory | `getMentorAtRiskProjects`| `GET /api/v1/mentors/at-risk` | MentorSupervisionService | ProjectInstances (`health in ('WARNING','CRITICAL')`) |
| Help Requests Queue| MentorHelpRequests | `respondMentorHelpRequest`| `POST /mentors/help-requests/:id/respond`| HelpRequestService | HelpRequests Table |
| Admin Overview | AdminOverview | `getAdminOverview` | `GET /api/v1/admin/overview` | AdminGovernanceService | Platform KPI Aggregations |
| AI Observatory | AdminAIObservatory | `getAdminAIObservatory`| `GET /api/v1/admin/ai/observatory` | AIProviderGateway | Gateway Posture & Jobs Queue |
| System Health | AdminSystemHealth | `getAdminSystemHealth` | `GET /api/v1/admin/health` | SystemHealthService | DB Pool & Outbox Diagnostics |
| Global Search | GlobalSearchModal | `searchWorkspace` | `GET /api/v1/search` | SearchService | Role-Partitioned Full-Text Search |
| Notifications | NotificationsPopover| `getNotifications` | `GET /api/v1/notifications` | NotificationService | Notifications Table (`user_id`) |

---

## 36. Final Backend Readiness Assessment

| Domain Area | Readiness Classification | Notes & Requirements for Backend Phase |
|---|---|---|
| **Authentication** | `READY` | Supabase JWT integration verified; `/auth/me` matches identity schema. |
| **Authorization** | `READY` | Role boundaries (`STUDENT`, `MENTOR`, `ADMIN`) and account status guards established. |
| **Projects & Lifecycle**| `READY` | 8-phase state machine, phase advancement, and health update routes verified. |
| **Assessment System** | `READY` | 10 core + 5 dynamic adaptive question engine matches schema. |
| **Blueprint System** | `READY` | B3-01 (`content`), B3-02 (`target_output_key`), B3-05, B3-06 contracts verified. |
| **Tasks & Milestones** | `READY` | Full CRUD endpoints and status enums aligned. |
| **Risks & Roadmap** | `READY` | Severity matrix, roadmap summaries, and grouped tasks aligned. |
| **Documents & RAG** | `PARTIALLY READY` | Canonical documents ready; vector embedding pipeline in standby/diagnostics mode. |
| **GitHub Integration** | `READY` | Read-only observation, commit preview caching, and sync flow established. |
| **Activity Timelines** | `READY` | Domain-event derived stream schema mapped across all workspaces. |
| **AI Mentor & Mentor AI**| `READY` | Chat endpoints, action execution payloads, and availability fallbacks verified. |
| **Help Requests** | `READY` | Student creation, mentor inspection, and response resolution contracts verified. |
| **Scope Changes** | `READY` | Impact analysis, confirmation with `idempotency_key`, and versioning aligned. |
| **Search Subsystem** | `READY` | Role-aware scoping (`BUILD`, `SUPERVISE`, `GOVERN`) and B3-04 optional `id` verified. |
| **Notifications** | `READY` | The 8 approved notification event types and recipient routing verified. |
| **Admin Governance** | `READY` | All 29 Admin routes (AD01–AD29) fully documented and mapped. |
| **Background & SSE** | `READY` | Query-token exception for `/events` and polling fallback verified. |

---

## 37. Confirmation of Zero Frontend Modifications

This document was generated in an **AUDIT & SPECIFICATION MODE**:
- Zero frontend source files modified.
- Zero routes altered or removed.
- Zero TypeScript types changed.
- Zero backend production files modified.
- Zero database migrations or schemas altered.

---

## 38. Final Quality Standards

This document establishes the official technical baseline for the GrowFlow backend engineering phase. All backend code, domain models, Pydantic schemas, database migrations, and background workers must be constructed to fulfill these frozen frontend specifications without introducing contract drift.
