# GrowFlow Gate 09 — Unit 6 Implementation Analysis
## Student-Facing Blueprint Generation & Monitoring Experience

---

### 1. Executive Summary & Status
- **Gate:** Gate 09 — AI Blueprint Generation
- **Unit:** Unit 6 — Student Blueprint Generation & Monitoring Experience
- **Task Type:** ANALYSIS-ONLY (No code implementation, no package installation, no git commits)
- **Status:** READY FOR UNIT 6 IMPLEMENTATION
- **Primary Deliverable:** `docs/gate09_unit6_analysis.md`

Unit 5 has authoritatively completed and verified the real-time Server-Sent Events (SSE) streaming infrastructure on the backend (`BlueprintEventManager`, bounded subscriber queues, non-blocking dispatch, 50-event ring buffer replay, monotonic event IDs, and 15-second keepalive heartbeats).

Unit 6 defines how the existing frontend (`frontend/src/pages/Student/StudentBlueprint/`) consumes this streaming contract to deliver a world-class, accessible, and resilient student blueprint generation and monitoring experience. The experience encompasses the entire frozen backend lifecycle:
```
IDEA 
  → SCOPE 
  → [TECHNOLOGY / FEATURES / MVP] (Parallel Fan-Out) 
  → SPECIFICATION (Fan-In Join) 
  → TIMELINE 
  → RISK 
  → TASK 
  → MILESTONE 
  → README 
  → QA / JUDGE 
  → (Targeted Regeneration if needed) 
  → CANONICAL BLUEPRINT COMMIT & APPROVAL
```

---

### 2. Authoritative References
1. `GrowFlow Student Side Updated Specification`
2. `GrowFlow Part 6A — Backend Architecture`
3. `GrowFlow Part 6B — Database Architecture`
4. `GrowFlow Part 6C — API Architecture`
5. `GrowFlow Part 6D — Authentication & Security Architecture`
6. `GrowFlow Part 6E — AI Provider Gateway & Model Architecture`
7. `GrowFlow Part 6F — AI Agent Architecture & Orchestration`
8. `GrowFlow Part 6G — RAG Knowledge & Document Intelligence Architecture`
9. `GrowFlow Part 6H — Event-Driven Runtime, Background Jobs & Reliability`
10. `GrowFlow Part 6M — Infrastructure Security`
11. `Gate 09 spec resolution & frozen decisions`
12. `docs/gate09_unit1_analysis.md` & `docs/implementation/GATE_09_UNIT_1_EVIDENCE.md`
13. `docs/gate09_unit2_analysis.md` & `docs/implementation/GATE_09_UNIT_2_EVIDENCE.md`
14. `docs/gate09_unit3_analysis.md` & `docs/implementation/GATE_09_UNIT_3_EVIDENCE.md`
15. `docs/gate09_unit4_analysis.md` & `docs/implementation/GATE_09_UNIT_4_EVIDENCE.md`
16. `docs/gate09_unit5_analysis.md` & `docs/implementation/GATE_09_UNIT_5_EVIDENCE.md`
17. `docs/FRONTEND_BACKEND_CONTRACT.md`

---

### 3. Current Frontend Audit
A comprehensive audit of the active frontend codebase (`frontend/src/`) reveals the current implementation baseline:

#### 3.1 Existing Surface Components
1. **`StudentBlueprint.tsx` (`frontend/src/pages/Student/StudentBlueprint/StudentBlueprint.tsx`):**
   - Main page component mapped to route `/student/projects/:projectId/blueprint`.
   - Manages state machine: `isLoading`, `isStarting`, `isRetrying`, `isApproving`, `error`, `isStaleGeneration`.
   - Implements `startLiveTracking` with native `EventSource` subscription and transparent fallback to 1.5s polling.
   - Conditionally renders 6 stage views:
     - `isPrereqBlocked` -> `BlueprintPrerequisiteBlock`
     - `APPROVED` -> `BlueprintApprovedView`
     - `isReadyForReview` (`READY_FOR_APPROVAL`, `COMPLETED`, `GENERATED`) -> `BlueprintReviewApproval`
     - `isFailed` (`FAILED`, `QA_REJECTED`) -> `BlueprintFailureView`
     - `isGenerating` (`GENERATING`, `VALIDATING`) -> `BlueprintGeneratingProgress`
     - Default -> `BlueprintNotStarted`
2. **`BlueprintGeneratingProgress.tsx` (`frontend/src/pages/Student/StudentBlueprint/components/BlueprintGeneratingProgress.tsx`):**
   - Displays linear progress track, circular percentage (`completedCount / total * 100`), and a checklist of 10 canonical sections.
   - **Gaps Identified:**
     - Treats all 10 sections as strictly sequential (`idx + 1`, "Each section is generated sequentially").
     - Does NOT reflect the parallel execution of `technology`, `features`, and `mvp`.
     - Does NOT display the QA Judge evaluation step.
     - Does NOT display targeted regeneration indicators (attempt number, target section).
     - Does NOT offer a "Cancel Generation" action button during active synthesis.
3. **`StudentBlueprintWorkspace.tsx` (`frontend/src/pages/Student/StudentBlueprintWorkspace/StudentBlueprintWorkspace.tsx`):**
   - Route: `/student/projects/:projectId/blueprint/workspace`.
   - Interactive structured view rendering tables for Tech Stack, feature cards, and REST API specification endpoints.
4. **`StudentBlueprintDocumentViewer.tsx` (`frontend/src/pages/Student/StudentBlueprintDocumentViewer/StudentBlueprintDocumentViewer.tsx`):**
   - Route: `/student/projects/:projectId/blueprint/documents/:documentKey`.
   - Markdown viewer supporting Preview vs Raw Markdown toggle and `.md` file download.

#### 3.2 Existing API Client & Types
1. **`client.ts` (`frontend/src/lib/api/client.ts`):**
   - `subscribeBlueprintEvents(projectId, onUpdate, onError)`: Opens `new EventSource(`${API_BASE_URL}/api/v1/projects/${projectId}/blueprint/events?token=...`)`, listens to `'update'` event, parses JSON, returns unsubscribe function.
   - `getBlueprintStatus(projectId)`: Calls `GET /api/v1/projects/:projectId/blueprint/status`.
   - `startBlueprintGeneration(projectId)`: Calls `POST /api/v1/projects/:projectId/blueprint/generate`.
   - `retryBlueprintGeneration(projectId, payload)`: Calls `POST /api/v1/projects/:projectId/blueprint/retry`.
   - `approveBlueprint(projectId)`: Calls `POST /api/v1/projects/:projectId/blueprint/approve`.
   - `getBlueprintContent(projectId)`: Calls `GET /api/v1/projects/:projectId/blueprint/content`.
   - **Gap Identified:** `cancelBlueprintGeneration(projectId)` is **MISSING** from `client.ts` despite being implemented in the backend (`POST /api/v1/projects/{projectId}/blueprint/cancel`).
2. **`types/blueprint.ts` (`frontend/src/lib/api/types/blueprint.ts`):**
   - `BlueprintStatus`: `'NOT_STARTED' | 'GENERATING' | 'GENERATED' | 'VALIDATING' | 'QA_REJECTED' | 'READY_FOR_APPROVAL' | 'COMPLETED' | 'FAILED' | 'APPROVED'`.
   - **Gaps Identified:**
     - `'CANCELLED'` is missing from `BlueprintStatus`.
     - `BlueprintStatusResponse` lacks the enriched Unit 5 fields: `event_id`, `event_type`, `event_version`, `job_id`, `generation_number`, `current_step`, `progress_percent`, `regeneration_attempt`, `regeneration_target`, `qa_score`, `error_message`, `failed_output_key`.

---

### 4. Unit 5 Backend Contract Audit
The backend SSE route (`GET /api/v1/projects/{project_id}/blueprint/events`) delivers structured JSON payloads on the `update` event:

```text
id: <project_id>_<generation_number>_<sequence:03d>
event: update
retry: 2000
data: {
  "id": "...",
  "blueprint_id": "...",
  "project_instance_id": "...",
  "project_id": "...",
  "student_id": "...",
  "status": "GENERATING" | "READY_FOR_APPROVAL" | "APPROVED" | "FAILED" | "QA_REJECTED" | "CANCELLED",
  "current_step": "idea" | "scope" | "technology" | "features" | "mvp" | "specification" | "timeline" | "risk" | "task" | "milestone" | "readme" | "qa_judge" | "completed" | "cancelled" | "regeneration_router",
  "progress_percent": 5..100,
  "current_stage": 0..10,
  "generation_progress": {
    "completed_sections": ["..."],
    "total_sections": 10,
    "in_progress_section": "..." | null,
    "failed_sections": ["..."]
  },
  "error_message": "..." | null,
  "failed_output_key": "..." | null,
  "qa_status": "PASS" | "FAIL" | "PENDING" | null,
  "qa_score": 0..100 | null,
  "qa_feedback": { ... } | null,
  "approved_at": "..." | null,
  "created_at": "..." | null,
  "updated_at": "2026-09-20T12:00:00Z",
  "event_id": "proj_001_1_005",
  "event_type": "job.started" | "node.started" | "node.completed" | "qa.evaluated" | "regeneration.started" | "job.completed" | "job.failed" | "job.cancelled" | "snapshot",
  "event_version": "1.0.0",
  "job_id": "job-uuid",
  "generation_number": 1,
  "timestamp": "2026-09-20T12:00:00Z",
  "regeneration_attempt": 0..2,
  "regeneration_target": "timeline" | null,
  "active_job": { "id": "...", "status": "RUNNING" } | null
}
```

#### 4.1 Reconnection & Terminal Guarantees
- **Heartbeat:** `: keep-alive\n\n` emitted every 15 seconds.
- **Reconnection:** Client automatically transmits `Last-Event-ID` header; backend replays missed events from the 50-event ring buffer (scoped to current `generation_number`).
- **Terminal Closure:** Server terminates connection upon dispatching `job.completed`, `job.failed`, `job.cancelled`, or when initial snapshot is already terminal (`READY_FOR_APPROVAL`, `APPROVED`, etc.).

---

### 5. Student Experience & Progress UX Mapping

#### 5.1 End-to-End Workflow States
| State | Trigger | Student UI Representation | Actions Available |
| :--- | :--- | :--- | :--- |
| **NOT_STARTED** | Initial page load (Stage 2 Assessment complete) | `BlueprintNotStarted`: 10-section breakdown, readiness indicator, synthesis estimate (30–60s) | "Generate Blueprint" |
| **STARTING** | Student clicks "Generate" | Primary button shows loading spinner ("Initiating Synthesis...") | Disabled |
| **GENERATING** | Backend returns `GENERATING`, SSE connected | `BlueprintGeneratingProgress`: Circular % indicator, linear progress track, active agent stage card, parallel fan-out indicator | "Cancel Generation" |
| **REGENERATING** | `regeneration.started` event received | Banner: "Refining Architecture (Attempt X of 2) — Re-evaluating [Target Section]" | "Cancel Generation" |
| **CANCELLING** | Student confirms cancellation modal | Progress banner: "Cancelling generation... Discarding in-flight work." Cancel button disabled | Disabled |
| **CANCELLED** | `job.cancelled` event received | `BlueprintCancelledView`: Notice that generation was stopped. Prior approved blueprint (if any) preserved | "Start New Generation", "Return to Project" |
| **READY_FOR_APPROVAL** | `job.completed` event received | `BlueprintReviewApproval`: QA Scorecard (Score, Passed Criteria, Findings, Strengths), 10-section preview tabs | "Approve Blueprint", "Regenerate" |
| **QA_REJECTED** | QA failed after 2 regeneration attempts | `BlueprintFailureView`: "QA Threshold Not Met (Score: X/100). Review findings or retry." | "Retry Generation", "View Findings" |
| **FAILED** | Unrecoverable error / provider failure | `BlueprintFailureView`: Truthful error message and failed section indicator | "Retry Generation" |
| **APPROVED** | Student clicks "Approve" | `BlueprintApprovedView`: "Blueprint Approved", phase advanced to PLANNING, link to Blueprint Workspace | "Open Blueprint Workspace", "View Documents" |

#### 5.2 Parallel Node Representation (Technology / Features / MVP)
- In the LangGraph backend, `scope` fans out into `technology`, `features`, and `mvp` in parallel.
- **UX Invariant:** The checklist must NOT represent these as sequential steps 3, 4, and 5.
- **Design:** Group these into a single visual card: **"Core Architecture & Scope (Parallel Synthesis)"**:
  - `technology`: "Tech Stack & Architecture" (badge: *Synthesizing...* / *Completed*)
  - `features`: "Core Features & Modules" (badge: *Synthesizing...* / *Completed*)
  - `mvp`: "MVP Scope & Validation" (badge: *Synthesizing...* / *Completed*)
  - Shows collective progress without misrepresenting execution order.

#### 5.3 QA / Judge Evaluation Step
- Once `readme` completes (90% progress), the progress checklist displays:
  - **Step 10: "Architectural QA & Schema Validation"** (95% progress)
  - Badge: *Evaluating Quality & Invariants...*
  - On pass: Advances to 100% and transitions to `BlueprintReviewApproval`.

---

### 6. Targeted Regeneration UX
When QA evaluates findings and routes to `regeneration_router`:
1. **Event Sequence:**
   `qa.evaluated (score < 75)` -> `regeneration.started (target="timeline", attempt=1)` -> `node.started ("timeline")` -> `node.completed` -> downstream nodes -> `qa.evaluated`.
2. **Visual Feedback:**
   - Active step badge updates to: `Refining: Timeline & Sprint Duration (Attempt 1 of 2)`.
   - Subtle alert banner:
     > **Targeted Refinement in Progress:** The QA Judge identified opportunities to strengthen the Timeline & Sprint Duration. Upstream sections (Idea, Scope, Tech Stack, Features, MVP, Specifications) remain locked and preserved.
   - Preserves student trust by explaining *why* the progress adjusted.

---

### 7. Cancellation UX
1. **Trigger:** "Cancel Generation" button visible in `BlueprintGeneratingProgress` header.
2. **Modal Confirmation (`BlueprintCancelModal`):**
   - Title: "Cancel Blueprint Generation?"
   - Message: "Are you sure you want to stop generation? Any uncommitted architectural sections from this run will be discarded."
   - Buttons: "Keep Generating" (secondary) vs "Yes, Cancel Generation" (destructive).
3. **Optimistic Transition:**
   - Page enters `isCancelling = true`.
   - Button displays "Cancelling...".
   - Calls `cancelBlueprintGeneration(projectId)`.
4. **Completion:**
   - Backend completes cooperative cancellation and dispatches `job.cancelled`.
   - UI transitions to `BlueprintCancelledView`.
   - If cancellation races with success (`job.completed` arrived first), UI smoothly honors `READY_FOR_APPROVAL`.

---

### 8. Error States & Resilience Matrix
| Scenario | Backend Behavior | Frontend Detection | UX Action / Fallback |
| :--- | :--- | :--- | :--- |
| **Auth Expiration** | 401 Unauthorized on SSE connect | SSE `onerror` / fetch failure | Redirect to `/auth/student/sign-in?returnTo=...` |
| **Forbidden Project** | 403 Forbidden | SSE `onerror` / 403 status | Inline error: "Access Denied. You do not own this project." |
| **SSE Connection Drop** | Connection reset by network/proxy | `EventSource.onerror` triggers | Transparent fallback to `pollStatus` every 1.5s. User sees no interruption. |
| **Browser Refresh** | Active generation continues on backend | `loadInitialData` receives `status: GENERATING` | Automatically reconnects SSE and resumes live progress seamlessly. |
| **Stale Generation** | Generation running > 3 minutes | Client-side timer (`elapsed >= 180000`) | Banner: "Generation taking longer than expected. Background process still active." Option to Cancel or Retry. |
| **Malformed SSE Event** | Invalid JSON in SSE `data:` | `JSON.parse` throws in event listener | Caught in `try...catch`, logged to `console.error`, stream remains connected. |
| **Backend Restart** | Orphaned job recovered to `FAILED` | Next poll or SSE reconnect receives `status: FAILED` | UI renders `BlueprintFailureView` with option to restart. |

---

### 9. Blueprint Result & Canonical Presentation
1. **`BlueprintReviewApproval.tsx` (Review Surface):**
   - QA Scorecard with overall score (0–100), Pass/Fail badge, criteria breakdown, identified issues, and strengths.
   - Section preview tabs for all 10 canonical sections using `SafeMarkdownViewer`.
   - "Approve Blueprint" button triggers `POST /api/v1/projects/:projectId/blueprint/approve`.
2. **`StudentBlueprintWorkspace.tsx` (Workspace Surface):**
   - Structured visual display of the approved blueprint: Tech Stack tables, Feature cards with priorities, REST API specifications.
3. **`StudentBlueprintDocumentViewer.tsx` (Document Surface):**
   - Full document reading experience with Preview vs Raw Markdown toggle and direct file download.
4. **Constraint:** Frontend adheres to View/Preview/Raw/Download. No unrestricted client-side Markdown editor is permitted.

---

### 10. SSE Client Architecture & State Management
- **Protocol:** Retain browser-native `EventSource` with `?token=<jwt>` query parameter.
- **Connection Lifecycle:**
  ```text
  IDLE -> CONNECTING -> LIVE_STREAMING (or POLLING_FALLBACK) -> TERMINAL_CLOSED
  ```
- **State Store:** Managed cleanly via standard React hooks (`useState`, `useEffect`, `useCallback`, `useRef`) in `StudentBlueprint.tsx`. No external state management library (Redux/Zustand) is required or permitted.

---

### 11. Exact File-Level Implementation Plan

#### 11.1 Files to CREATE [NEW]
1. `frontend/src/pages/Student/StudentBlueprint/components/BlueprintCancelModal.tsx`:
   - Modal dialog confirming cancellation intent with accessible focus management.
2. `frontend/src/pages/Student/StudentBlueprint/components/BlueprintCancelledView.tsx`:
   - Clean state view shown when `status === 'CANCELLED'`, with action to start new generation.

#### 11.2 Files to MODIFY [MODIFY]
1. `frontend/src/lib/api/types/blueprint.ts`:
   - Add `'CANCELLED'` to `BlueprintStatus`.
   - Enrich `BlueprintStatusResponse` with `event_id`, `event_type`, `event_version`, `job_id`, `generation_number`, `current_step`, `progress_percent`, `regeneration_attempt`, `regeneration_target`, `qa_score`, `error_message`, `failed_output_key`.
2. `frontend/src/lib/api/client.ts`:
   - Add `cancelBlueprintGeneration(projectId: string): Promise<BlueprintStatusResponse>`.
   - Export typed `cancelBlueprintGeneration`.
3. `frontend/src/pages/Student/StudentBlueprint/StudentBlueprint.tsx`:
   - Import `cancelBlueprintGeneration`.
   - Add `isCancelling` state and cancellation modal toggle.
   - Render `BlueprintCancelledView` when `status === 'CANCELLED'`.
   - Pass cancellation handler and active event metadata to `BlueprintGeneratingProgress`.
4. `frontend/src/pages/Student/StudentBlueprint/components/BlueprintGeneratingProgress.tsx`:
   - Render parallel stage card for `technology`, `features`, and `mvp`.
   - Render QA evaluation step.
   - Render targeted regeneration notice when `regeneration_attempt > 0`.
   - Add "Cancel Generation" button triggering the cancellation modal.
5. `frontend/src/pages/Student/StudentBlueprint/components/index.ts`:
   - Export `BlueprintCancelModal` and `BlueprintCancelledView`.
6. `frontend/src/test/studentBlueprint.test.tsx`:
   - Add test coverage for parallel stage rendering, regeneration notice, cancellation flow, and SSE event updates.

#### 11.3 Files to PRESERVE [DO NOT TOUCH]
- All backend files (`backend/app/`, `backend/migrations/`, `backend/tests/`).
- All mentor and admin frontend pages.
- Database schemas and migration versions.

---

### 12. Accessibility (a11y) & UX Performance
- **Live Progress:** `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`.
- **Milestone Announcements:** `aria-live="polite"` region announcing major phase transitions (e.g. "Scope synthesis complete. Beginning Core Architecture synthesis.") without flooding screen readers with every sub-event.
- **Cancellation Modal:** `role="dialog"`, `aria-modal="true"`, focus trapped within modal, `Escape` key closes.
- **Performance:** Lightweight React state updates; SSE listener performs zero DOM manipulations directly. Subscriptions cleanly closed in `useEffect` cleanup.

---

### 13. Test Strategy
All tests will be implemented in `frontend/src/test/studentBlueprint.test.tsx` using Vitest + React Testing Library:
1. **Initial State:** Verify `BlueprintNotStarted` renders with 10 canonical sections.
2. **Start Generation:** Clicking "Generate Blueprint" initiates API call and opens SSE.
3. **Live Progress:** Verifies progress bar advances upon receiving SSE `update` events.
4. **Parallel Group:** Verifies `technology`, `features`, and `mvp` are rendered in a parallel card group.
5. **Targeted Regeneration:** Emitting `regeneration.started` displays the refinement banner with attempt count.
6. **Cancellation Flow:**
   - Clicking "Cancel Generation" opens confirmation modal.
   - Confirming calls `cancelBlueprintGeneration`.
   - Receiving `status: CANCELLED` renders `BlueprintCancelledView`.
7. **Approval Flow:** Receiving `READY_FOR_APPROVAL` renders `BlueprintReviewApproval` with QA scorecard; clicking "Approve Blueprint" advances phase.
8. **SSE Reconnection / Polling Fallback:** Verifies that if SSE encounters an error, the client seamlessly falls back to status polling.

---

### 14. Out of Scope for Unit 6
- Modifications to AI agents, prompts, or LLM providers (Unit 1 & 3 frozen).
- Modifications to LangGraph graph topology or durable worker (Unit 4 frozen).
- Modifications to SSE backend transport or event manager (Unit 5 frozen).
- Database migrations or schema modifications (Database frozen).
- Gate 10 (Execution Management, Tasks, Milestones, Sprints).

---

### 15. Handoff to Gate 10
Upon completion of Unit 6:
- The student will have a fully autonomous, observable, and interactive AI Blueprint generation experience.
- Approving the blueprint advances the project to `PLANNING` phase.
- Gate 10 will consume the approved canonical blueprint content to initialize tasks, milestones, and project execution boards.

---

### 16. Final Verdict
# **READY FOR UNIT 6 IMPLEMENTATION**
