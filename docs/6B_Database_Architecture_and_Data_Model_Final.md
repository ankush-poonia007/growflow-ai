# GrowFlow — Part 6B: Database Architecture & Data Model
## Final Frozen Specification

**Project:** GrowFlow  
**Part:** 6B — Database Foundation & Data Model  
**Status:** FROZEN  
**Database:** PostgreSQL via Supabase  
**Architecture:** Modular Monolith  
**Source of Truth:** PostgreSQL

---

# 1. Purpose

Part 6B defines GrowFlow's database foundation, canonical relational data model, entity relationships, integrity rules, persistence boundaries, indexing strategy, authorization model, history/versioning strategy, and database-level architectural constraints.

The database is the authoritative source of truth for GrowFlow's structured application state.

Generated Markdown, AI responses, RAG/vector data, GitHub data, cached projections, and UI state must not silently become competing sources of truth.

---

# 2. Core Database Decision

GrowFlow will use:

- **PostgreSQL** as the canonical relational database.
- **Supabase** as the managed PostgreSQL/platform layer.
- Repository/Data Access Pattern from Part 6A.
- PostgreSQL-first architecture rather than Supabase-SDK-first application design.

Application code accesses persistence through repositories/data-access components rather than scattering raw database operations throughout routes or business services.

Supabase-specific capabilities may be used where appropriate, but the domain model remains relational and database-platform independent wherever practical.

---

# 3. Database Principles

1. PostgreSQL is the canonical source of truth.
2. Use a relational-first schema.
3. Use normalized tables for stable domain concepts.
4. Use JSONB only for naturally flexible metadata.
5. Enforce important invariants at database level where practical.
6. Use foreign keys for referential integrity.
7. Combine application authorization with database authorization.
8. Use Row Level Security (RLS) as defense in depth.
9. Use UUID identifiers.
10. Store timestamps consistently in UTC.
11. Preserve meaningful state-change history.
12. Version only entities that genuinely require versioning.
13. Do not introduce blanket soft deletion.
14. Do not introduce blanket versioning.
15. AI-generated output is not automatically authoritative.
16. Generated Markdown is a representation of structured state.
17. RAG/vector storage does not replace relational metadata.
18. External integration data is stored only when useful to the product.
19. Indexes are driven by actual query/access patterns.
20. Cascading deletes are used cautiously.
21. Schema evolution occurs through migrations.
22. Database ownership follows domain ownership.
23. Current state and historical state are deliberately separated.
24. Retryable operations must be designed for idempotency.
25. Security-sensitive records require explicit authorization boundaries.

---

# 4. Entity Landscape

The database is organized into these logical domains:

1. Identity & Access
2. Organization
3. Projects
4. Assessment
5. Blueprint & Planning
6. Execution
7. Communication
8. Knowledge & Documents
9. Integrations
10. AI & Agents
11. Platform & Events
12. Security & Audit

The schema is modular logically even though PostgreSQL is deployed as one database.

---

# 5. Identity & Access

## 5.1 users

Canonical application identity record.

Suggested fields:

- `id` — UUID, primary key
- `email`
- `full_name`
- `role`
- `status`
- `avatar_url`
- `last_login_at`
- `created_at`
- `updated_at`

Roles:

- ADMIN
- MENTOR
- STUDENT

Account statuses:

- ACTIVE
- INACTIVE
- SUSPENDED

Passwords are never stored as plaintext in this application database.

The exact authentication storage/integration decision is finalized in the authentication/security phase.

---

## 5.2 student_profiles

Student-specific profile data.

Core fields:

- `user_id` — FK to users
- `student_id` — unique platform/student identifier
- `bio`
- `goals`
- `interests`
- `created_at`
- `updated_at`

Technology relationships are normalized rather than stored as uncontrolled arrays.

---

## 5.3 mentor_profiles

Mentor-specific profile data.

Core fields:

- `user_id`
- `mentor_id`
- `bio`
- `specialization`
- `created_at`
- `updated_at`

---

## 5.4 user_preferences

User-level preferences.

Examples:

- email notification preference
- notification configuration
- timezone
- other non-critical user preferences

Flexible preference metadata may use JSONB where appropriate.

---

## 5.5 technologies

Canonical technology catalogue.

Fields:

- `id`
- `name`
- `category`
- `created_at`
- `updated_at`

---

## 5.6 student_technologies

Many-to-many relationship between students and technologies.

Fields:

- `student_id`
- `technology_id`
- `proficiency`
- `relationship_type`

Relationship types:

- KNOWN
- WORKED_WITH
- INTERESTED_IN

A uniqueness constraint prevents duplicate student/technology relationships of the same type.

---

# 6. Organization

## 6.1 groups

Mentor-managed student groups.

Fields:

- `id`
- `mentor_id`
- `name`
- `join_code`
- `status`
- `created_at`
- `updated_at`

A join code is unique within the platform.

---

## 6.2 group_memberships

Student/group relationship.

Fields:

- `id`
- `group_id`
- `student_id`
- `status`
- `joined_at`
- `left_at`
- `created_at`

Membership is modeled separately so the system can support:

- multiple groups
- membership history
- authorization
- future membership states

Current membership should be represented explicitly rather than inferred only from historical rows.

---

# 7. Projects

GrowFlow deliberately separates reusable mentor project definitions from student-owned project instances.

## 7.1 project_definitions

Reusable mentor-created project templates/definitions.

Fields:

- `id`
- `owner_mentor_id`
- `name`
- `status`
- `current_version_id`
- `created_at`
- `updated_at`

Statuses:

- DRAFT
- ACTIVE
- ARCHIVED

---

## 7.2 project_definition_versions

Versioned definition snapshots.

Fields include:

- `id`
- `project_definition_id`
- `version_number`
- `name`
- `problem`
- `proposed_solution`
- `complexity`
- `description`
- `duration`
- `constraints`
- `assumptions`
- `technology_snapshot`
- `created_by`
- `created_at`

### Critical rule

Updating a Project Definition does **not** mutate existing student Project Instances.

New assignments receive the latest definition version.

Existing students remain on their existing project state unless they explicitly adopt a change through the canonical project-change workflow.

---

## 7.3 project_instances

Independent student project instances.

Fields:

- `id`
- `student_id`
- `group_id`
- `project_definition_id` — nullable
- `source_definition_version_id` — nullable
- `name`
- `problem`
- `proposed_solution`
- `complexity`
- `current_phase`
- `health`
- `progress_percentage`
- `status`
- `deadline`
- `started_at`
- `completed_at`
- `created_at`
- `updated_at`

A student-created project has no mentor Project Definition relationship.

A mentor-assigned project records the source definition/version from which the instance originated.

### Current-state ownership

`project_instances` is the canonical owner of:

- current project phase
- current project health
- current cached progress
- current project lifecycle/status

Historical transitions are stored separately.

No separate `project_execution_state` table is required for these same current-state fields unless a future scaling requirement establishes a concrete need.

---

# 8. Assessment

Every project instance must complete the GrowFlow assessment flow.

## 8.1 assessment_question_templates

Versioned templates for standardized questions.

Used for the 10 core assessment questions.

Fields:

- `id`
- `version`
- `sequence_number`
- `question_text`
- `active`
- `created_at`

---

## 8.2 assessments

Assessment instance for a project.

Fields:

- `id`
- `project_instance_id`
- `status`
- `total_questions`
- `completed_questions`
- `score`
- `started_at`
- `completed_at`
- `created_at`
- `updated_at`

Statuses:

- NOT_STARTED
- IN_PROGRESS
- COMPLETED
- FAILED

---

## 8.3 assessment_questions

Persisted questions presented to the student.

Fields:

- `id`
- `assessment_id`
- `sequence_number`
- `question_type`
- `question_text`
- `generation_metadata`
- `generated_from_question_id`
- `created_at`

Question types:

- CORE
- DYNAMIC

Dynamic questions are generated sequentially.

Each dynamic question may reference the previous relevant question through `generated_from_question_id`.

The assessment can therefore reconstruct the adaptive question chain from persisted questions and ordered answers.

---

## 8.4 assessment_answers

Student answers.

Fields:

- `id`
- `question_id`
- `answer_text`
- `answered_at`
- `metadata`

The answer history provides the accumulated context required by the adaptive assessment workflow.

---

# 9. Blueprint

## 9.1 blueprints

Canonical blueprint container for a project instance.

Fields:

- `id`
- `project_instance_id`
- `current_version_id`
- `status`
- `created_at`
- `updated_at`

---

## 9.2 blueprint_versions

Versioned blueprint generation.

Fields:

- `id`
- `blueprint_id`
- `version_number`
- `generation_type`
- `generation_status`
- `generated_by`
- `assessment_snapshot_reference`
- `created_at`
- `completed_at`

Generation types:

- INITIAL
- REGENERATED
- CHANGE_WORKFLOW

Generation context should remain traceable without blindly duplicating the entire project state inside every generation record.

---

# 10. Project Profile

## 10.1 project_profiles

Structured project profile.

Fields include:

- `project_instance_id`
- `objective`
- `target_users`
- `project_type`
- `student_skill_context`
- `goals`
- `scope`
- `expected_outcome`
- `constraints`
- `assumptions`
- `context`
- `version`
- `created_at`
- `updated_at`

The Project Profile is structured application state, not merely Markdown text.

---

# 11. Project Technologies

## 11.1 project_technologies

Project-specific technology decisions.

Fields:

- `project_instance_id`
- `technology_id`
- `category`
- `purpose`
- `why_selected`
- `appropriateness`
- `student_understanding`
- `usage_context`

This allows GrowFlow to distinguish:

- what the project uses
- why it uses it
- whether it is appropriate
- what the student understands
- where it is used

---

# 12. Features & Specifications

## 12.1 features

Structured feature records.

Fields:

- `id`
- `project_instance_id`
- `blueprint_version_id`
- `title`
- `description`
- `priority`
- `status`
- `order_index`
- `created_at`
- `updated_at`

Priority values:

- MUST
- SHOULD
- GOOD_TO_HAVE
- OUT_OF_SCOPE

---

## 12.2 feature_specs

Technical specification for a feature.

Fields:

- `id`
- `feature_id`
- `behavior`
- `dependencies`
- `technical_requirements`
- `acceptance_criteria`
- `created_at`
- `updated_at`

Specifications are structured so the system can reason over individual requirements rather than parsing a giant Markdown file.

---

# 13. MVP

## 13.1 mvps

MVP definition for a project/blueprint version.

Fields:

- `id`
- `project_instance_id`
- `blueprint_version_id`
- `definition`
- `exclusions`
- `research_summary`
- `created_at`
- `updated_at`

---

## 13.2 mvp_features

Many-to-many relationship between MVPs and features.

Fields:

- `mvp_id`
- `feature_id`

---

# 14. Research Sources

## 14.1 research_sources

Stores provenance for external research used in planning/MVP generation.

Fields:

- `id`
- `project_instance_id`
- `blueprint_version_id`
- `source_type`
- `title`
- `url`
- `summary`
- `retrieved_at`
- `metadata`

Research evidence informs planning but does not become the authority for project state.

Current web/API information is expected to be gathered through the planned Tavily integration.

---

# 15. Timeline / Duration

## 15.1 project_timelines

Timeline associated with a project/blueprint version.

Fields:

- `id`
- `project_instance_id`
- `blueprint_version_id`
- `planned_start_date`
- `planned_end_date`
- `total_duration_days`
- `created_at`
- `updated_at`

---

## 15.2 timeline_phases

Detailed phase plan.

Fields:

- `id`
- `timeline_id`
- `phase`
- `start_date`
- `end_date`
- `objective`
- `expected_outcome`
- `dependencies`
- `order_index`

The timeline considers:

- complexity
- student skill
- project scope
- technologies
- features
- dependencies
- available duration

---

# 16. Risks

## 16.1 risks

Structured project risk records.

Fields:

- `id`
- `project_instance_id`
- `blueprint_version_id`
- `category`
- `title`
- `description`
- `probability`
- `impact`
- `severity`
- `warning_signs`
- `prevention`
- `mitigation`
- `recommended_action`
- `status`
- `created_at`
- `updated_at`
- `resolved_at`

Risk categories include:

- implementation
- technology
- APIs
- third-party
- authentication
- database
- AI
- integration
- deployment
- hosting
- cost
- time
- scope creep
- learning
- security
- performance
- dependencies
- GitHub
- unexpected complexity

Statuses:

- OPEN
- MONITORED
- MITIGATED
- RESOLVED
- ACCEPTED

---

## 16.2 risk_history

Preserves meaningful risk state transitions.

Fields:

- `id`
- `risk_id`
- `previous_status`
- `new_status`
- `changed_by`
- `reason`
- `changed_at`

---

# 17. Tasks

## 17.1 tasks

Authoritative execution tasks.

Fields:

- `id`
- `project_instance_id`
- `milestone_id` — nullable
- `blueprint_version_id`
- `title`
- `description`
- `status`
- `priority`
- `order_index`
- `due_date`
- `started_at`
- `completed_at`
- `created_at`
- `updated_at`

Statuses:

- TODO
- IN_PROGRESS
- BLOCKED
- COMPLETED
- CANCELLED

A task may belong to one milestone or remain unassigned.

Task completion is authoritative application state.

---

# 18. Milestones

## 18.1 milestones

Milestone records.

Fields:

- `id`
- `project_instance_id`
- `blueprint_version_id`
- `title`
- `description`
- `status`
- `target_date`
- `order_index`
- `completed_at`
- `created_at`
- `updated_at`

Statuses:

- NOT_STARTED
- IN_PROGRESS
- BLOCKED
- COMPLETED

---

# 19. Execution State

GrowFlow uses a deterministic execution model:

**Task → Milestone → Progress → Phase → Health**

The canonical current values are owned by `project_instances`:

- `progress_percentage`
- `current_phase`
- `health`
- `status`

History tables preserve important transitions.

Progress is calculated deterministically from authoritative execution state rather than arbitrarily assigned by an AI model.

A cached progress percentage may be stored on `project_instances` for efficient reads, but it remains a deterministic projection and must be recalculable from authoritative task/milestone state.

---

# 20. Project Phase History

## 20.1 project_phase_history

Fields:

- `id`
- `project_instance_id`
- `previous_phase`
- `new_phase`
- `reason`
- `changed_at`
- `triggered_by`

This preserves lifecycle transitions.

---

# 21. Project Health History

## 21.1 project_health_history

Fields:

- `id`
- `project_instance_id`
- `previous_health`
- `new_health`
- `reason`
- `contributing_factors`
- `calculated_at`

Health is determined by deterministic project-state logic.

AI may analyze and recommend but cannot directly overwrite canonical health.

---

# 22. Project Change Workflow

## 22.1 project_change_requests

Canonical persistence for project-change workflows.

Fields:

- `id`
- `project_instance_id`
- `requested_by`
- `change_type`
- `description`
- `impact_analysis`
- `status`
- `created_at`
- `confirmed_at`
- `completed_at`

Statuses:

- REQUESTED
- ANALYZING
- AWAITING_CONFIRMATION
- CONFIRMED
- REGENERATING
- QA
- COMPLETED
- FAILED
- CANCELLED

There is no dedicated Change/Impact Agent.

Impact analysis is handled by the orchestration/application workflow.

Canonical process:

**Impact Analysis → Confirmation → Regeneration → QA → Persistence**

Existing project state is never silently migrated.

---

# 23. Communication

## 23.1 mentor_notes

Mentor-created notes.

Fields:

- `id`
- `mentor_id`
- `student_id` — nullable
- `group_id` — nullable
- `project_instance_id` — nullable
- `content`
- `created_at`
- `updated_at`

Mentor Notes are communication/observation records and do not directly mutate project execution state.

---

## 23.2 help_requests

Student-to-mentor support requests.

Fields:

- `id`
- `student_id`
- `mentor_id`
- `project_instance_id`
- `title`
- `description`
- `status`
- `created_at`
- `updated_at`
- `resolved_at`

Statuses:

- OPEN
- IN_PROGRESS
- RESOLVED

---

## 23.3 help_request_messages

Conversation messages attached to a help request.

Fields:

- `id`
- `help_request_id`
- `sender_id`
- `message`
- `created_at`

---

## 23.4 notifications

Centralized in-app notification records.

Fields:

- `id`
- `recipient_id`
- `notification_type`
- `title`
- `message`
- `resource_type`
- `resource_id`
- `read_at`
- `created_at`
- `metadata`

Notifications are generated from canonical domain events through the Notification Service.

Email is an optional delivery channel.

---

# 24. Documents & Knowledge

## 24.1 documents

Logical document identity.

Fields:

- `id`
- `project_instance_id`
- `document_type`
- `current_version_id`
- `status`
- `created_at`
- `updated_at`

---

## 24.2 document_versions

Versioned generated/manual document representations.

Fields:

- `id`
- `document_id`
- `version_number`
- `content_reference`
- `content_hash`
- `generation_type`
- `generated_by_execution_id`
- `created_at`

Large document content may be stored in object storage, while PostgreSQL retains authoritative metadata, references, hashes, and version information.

Generated Markdown is therefore a representation of structured state, not the primary source of truth.

---

# 25. RAG Metadata

## 25.1 rag_documents

Tracks indexed document versions.

Fields:

- `id`
- `document_id`
- `document_version_id`
- `project_instance_id`
- `status`
- `chunk_count`
- `indexed_at`

---

## 25.2 rag_chunks

Tracks chunks used for retrieval.

Fields:

- `id`
- `rag_document_id`
- `chunk_index`
- `content_hash`
- `vector_reference`
- `token_count`
- `metadata`

Vector implementation is intentionally abstracted and is finalized in the RAG/infrastructure phase.

PostgreSQL remains the authority for document/project association and authorization metadata.

---

## 25.3 rag_index_jobs

RAG indexing work is represented as an asynchronous job/workflow.

The implementation records job identity, target document/version, state, timestamps, retry information, and error information as required by the worker architecture.

Exact operational fields are finalized in the worker/event infrastructure phase.

---

# 26. GitHub Integration

GrowFlow supports **monitoring only**.

## 26.1 github_connections

Fields:

- `id`
- `user_id`
- `provider`
- `external_account_id`
- `status`
- `created_at`
- `updated_at`

---

## 26.2 github_repositories

Fields:

- `id`
- `project_instance_id`
- `connection_id`
- `external_repository_id`
- `full_name`
- `default_branch`
- `url`
- `status`
- `last_synced_at`

---

## 26.3 github_activity

Fields:

- `id`
- `repository_id`
- `activity_type`
- `external_id`
- `occurred_at`
- `summary`
- `metadata`

No GitHub repository management, issue editing, PR editing, commit manipulation, or other write-management is part of the database/application contract.

---

# 27. AI & Agent Execution

## 27.1 ai_executions

Top-level AI execution record.

Fields:

- `id`
- `user_id`
- `project_instance_id` — nullable
- `execution_type`
- `status`
- `provider`
- `model`
- `started_at`
- `completed_at`
- `duration_ms`
- `input_token_count`
- `output_token_count`
- `total_token_count`
- `error_code`
- `error_message`
- `correlation_id`
- `created_at`

Statuses:

- QUEUED
- RUNNING
- COMPLETED
- FAILED
- CANCELLED

---

## 27.2 agent_executions

Individual agent execution records.

Fields:

- `id`
- `ai_execution_id`
- `agent_type`
- `sequence_number`
- `status`
- `started_at`
- `completed_at`
- `duration_ms`
- `retry_count`
- `provider`
- `model`
- `input_tokens`
- `output_tokens`
- `error_code`
- `error_metadata`

The 12 approved agent types are:

1. Idea Agent
2. Scope Agent
3. Technology Agent
4. Features Agent
5. Specification Agent
6. MVP Agent
7. Timeline/Duration Agent
8. Risk Agent
9. Task Agent
10. Milestone Agent
11. README Agent
12. QA/Judge Agent

Idea + Scope may be coordinated together for the documentation flow, but their responsibilities remain conceptually distinct.

---

## 27.3 ai_execution_events

Streaming/progress events associated with an AI execution.

Fields:

- `id`
- `ai_execution_id`
- `event_type`
- `sequence_number`
- `payload`
- `created_at`

Examples:

- EXECUTION_STARTED
- AGENT_STARTED
- AGENT_PROGRESS
- AGENT_COMPLETED
- QA_STARTED
- QA_COMPLETED
- EXECUTION_COMPLETED
- EXECUTION_FAILED

---

## 27.4 ai_quality_results

QA/Judge results.

Fields:

- `id`
- `ai_execution_id`
- `agent_execution_id` — nullable
- `quality_type`
- `score`
- `passed`
- `findings`
- `regeneration_required`
- `created_at`

QA/Judge may trigger targeted regeneration through the orchestrator.

The database does not allow the AI layer to bypass deterministic domain services.

---

# 28. AI Provider Key Pool

## 28.1 ai_provider_keys

Stores operational metadata for the configured AI key pool.

Fields:

- `id`
- `provider`
- `key_alias`
- `status`
- `rate_limit_state`
- `failure_count`
- `last_used_at`
- `cooldown_until`
- `updated_at`

Actual provider secrets are not stored as ordinary database values.

The planned five-key pool exists for resilient provider access, rotation, rate-limit/error handling, and availability management.

Application components do not directly choose individual keys.

---

# 29. Domain Events

## 29.1 domain_events

Canonical cross-role activity/event records.

Fields:

- `id`
- `event_type`
- `actor_id`
- `actor_role`
- `resource_type`
- `resource_id`
- `project_instance_id` — nullable
- `group_id` — nullable
- `visibility`
- `metadata`
- `correlation_id`
- `occurred_at`
- `processed_at`

Representative event types:

- TaskCompleted
- TaskBlocked
- MilestoneCompleted
- ProjectProgressChanged
- ProjectPhaseChanged
- ProjectHealthChanged
- RiskCreated
- RiskUpdated
- RiskResolved
- HelpRequestCreated
- HelpRequestUpdated
- HelpRequestResolved
- MentorNoteCreated
- BlueprintGenerationStarted
- BlueprintGenerationCompleted
- AgentExecutionStarted
- AgentExecutionCompleted
- GitHubActivityDetected
- DocumentGenerated
- DocumentUpdated
- RAGIndexCompleted
- SecurityEventDetected
- AccountStatusChanged

The event model supports role-based activity projections.

---

# 30. Transactional Outbox

GrowFlow prefers a transactional outbox approach for reliable internal event dispatch.

A business transaction may:

1. change authoritative application state
2. create the corresponding domain/outbox event
3. commit both atomically

A background processor later dispatches the event to notification/activity/integration handlers.

This avoids introducing Kafka or another distributed event platform without a concrete scaling requirement.

Exact outbox implementation may use the `domain_events` persistence model or a dedicated outbox table if operational requirements make that cleaner during implementation.

---

# 31. Security & Audit

## 31.1 audit_events

Append-oriented security/audit records.

Fields:

- `id`
- `actor_id`
- `actor_role`
- `action`
- `resource_type`
- `resource_id`
- `result`
- `reason`
- `metadata`
- `correlation_id`
- `occurred_at`

Audit records are not ordinary editable business records.

---

## 31.2 admin_investigations

Controlled administrative inspection workflow.

Fields:

- `id`
- `admin_id`
- `target_type`
- `target_id`
- `reason`
- `status`
- `requested_at`
- `authorized_at`
- `completed_at`

Controlled investigation flow:

**Request → Authorization → Minimum Required Data → Inspection → Audit Log**

Default administration is metadata-first.

Private/deeper content is not unrestricted by default.

---

## 31.3 account_status_history

Account lifecycle history.

Fields:

- `id`
- `user_id`
- `previous_status`
- `new_status`
- `changed_by`
- `reason`
- `changed_at`

---

# 32. Canonical Relationship Model

Core relationships:

```text
User
 ├── Student Profile
 │    └── Student Technologies
 │
 └── Mentor Profile

Mentor
 └── Groups
      └── Group Memberships
           └── Students

Mentor
 └── Project Definitions
      └── Definition Versions
           └── Project Instances

Student
 └── Project Instances

Project Instance
 ├── Assessment
 │    ├── Questions
 │    └── Answers
 │
 ├── Project Profile
 ├── Technologies
 ├── Blueprint
 │    └── Blueprint Versions
 │         ├── Features
 │         │    └── Specifications
 │         ├── MVP
 │         │    └── MVP Features
 │         ├── Timeline
 │         │    └── Timeline Phases
 │         └── Research Sources
 │
 ├── Tasks
 ├── Milestones
 ├── Risks
 │    └── Risk History
 ├── Phase History
 ├── Health History
 ├── Project Change Requests
 ├── Documents
 │    └── Document Versions
 │         └── RAG Documents
 │              └── RAG Chunks
 ├── GitHub Repositories
 │    └── GitHub Activity
 ├── AI Executions
 │    └── Agent Executions
 │         └── Quality Results
 ├── Notifications
 ├── Communication
 └── Domain Events
```

---

# 33. Foreign-Key & Referential Integrity Strategy

Important relationships use PostgreSQL foreign keys.

Examples:

- profiles → users
- student_technologies → students/technologies
- memberships → groups/students
- definition_versions → definitions
- instances → students/groups/definitions
- assessments → project_instances
- questions → assessments
- answers → questions
- blueprints → project_instances
- blueprint_versions → blueprints
- features → project_instances/blueprint_versions
- specifications → features
- tasks/milestones/risks → project_instances
- documents → project_instances
- document_versions → documents
- RAG records → document versions/projects
- GitHub records → project instances/connections
- agent executions → AI executions
- domain events → relevant resources where applicable
- audit records → actor/resource references where appropriate

Referential integrity must prevent orphaned authoritative state.

---

# 34. Delete Strategy

Deletion behavior is domain-specific.

Default approach:

- use RESTRICT where deletion could destroy meaningful history
- use CASCADE only for true child records whose existence has no independent meaning
- prefer controlled deactivation/archive where business history matters
- never use blanket cascade deletion across an entire project without explicit design

Examples of records that generally require preservation:

- audit events
- meaningful project history
- risk history
- phase/health history
- AI execution history where needed for observability
- investigation history

---

# 35. Versioning Strategy

Versioning is used where historical reproducibility matters.

Versioned concepts include:

- mentor project definitions
- assessments/question templates
- blueprints
- project planning outputs
- documents

Not every mutable table receives versions.

Simple current-state entities such as ordinary notifications or transient operational metadata do not receive unnecessary version tables.

---

# 36. Project Blueprint Version Integrity

Blueprint-related records may reference a `blueprint_version_id` when reproducibility matters.

This provides traceability between generated planning artifacts and the blueprint version that produced them.

Tasks, milestones, features, MVP definitions, risks, timelines, and related planning artifacts must not silently become detached from the blueprint version that created them.

However, once execution begins, authoritative task/milestone execution state belongs to the project instance.

---

# 37. Deterministic State Ownership

The following are authoritative application state:

- project status
- project phase
- project health
- task status
- milestone status
- progress
- risk status
- help request status
- account status
- group membership state

AI may:

- analyze
- recommend
- explain
- generate candidate changes
- generate structured output

AI may not directly overwrite authoritative state.

All AI-driven state changes must pass through validated application/domain services.

---

# 38. Authorization & RLS

GrowFlow uses defense-in-depth authorization.

Authorization chain:

**Authentication → Role Authorization → Resource Authorization → Project/Group Scope → Action Permission → Privacy Policy → Tool/Service Execution → Audit when required**

RLS is used as a database-level defense where appropriate.

Application authorization remains mandatory.

RLS is not treated as a replacement for application-level authorization.

Project-scoped data must not become globally retrievable simply because an AI query or database query is technically possible.

---

# 39. Project Isolation

Project isolation is a first-class database rule.

Project-scoped records must be traceable to the relevant `project_instance_id` directly or through an explicit authorized relationship.

AI/RAG retrieval must enforce the same project/group/user authorization boundaries as normal application access.

No global unrestricted project retrieval is allowed for ordinary users or AI tools.

---

# 40. Indexing Strategy

Indexes are created around real access patterns.

Important expected access patterns include:

### Identity

- unique email
- unique student ID
- unique mentor ID

### Organization

- group mentor
- group join code
- group membership by group/student
- active membership queries

### Projects

- projects by student
- projects by group
- projects by mentor definition
- project status
- project phase
- project health
- deadline
- recent activity

### Execution

- tasks by project
- tasks by milestone
- tasks by status
- due dates
- milestones by project/status

### Risks

- risks by project
- risks by status/severity/category

### Communication

- notifications by recipient/read status
- help requests by mentor/student/status
- notes by student/group/project

### Documents/RAG

- documents by project/type
- document versions by document
- RAG records by project/document version
- indexing status

### AI

- executions by project/user/status
- agent executions by AI execution
- execution events by execution/sequence
- quality results by execution

### Events/Audit

- events by project/group/resource/time
- audit records by actor/resource/time

Composite indexes are added where recurring query combinations justify them.

Indexes are not added speculatively everywhere.

---

# 41. Constraints

Important database constraints include:

- primary keys
- foreign keys
- unique constraints
- not-null constraints
- controlled status values
- controlled enum-like values
- valid sequence/order values where required
- non-negative duration/token/count fields where appropriate
- valid progress range
- unique version number per versioned parent
- unique project-definition join code
- uniqueness of normalized relationship records
- valid date relationships where enforceable

Application validation remains necessary for rules that are too contextual for database constraints.

---

# 42. Progress Model

Progress is deterministic.

The authoritative source is execution state:

- tasks
- milestones
- their statuses
- project lifecycle state

`project_instances.progress_percentage` may be stored as a cached projection for efficient dashboard reads.

It must remain consistent with the deterministic calculation and be recalculable.

An AI agent cannot arbitrarily set:

```text
progress = 87%
```

without the corresponding deterministic application workflow.

---

# 43. Health Model

Project health is a deterministic application/domain result.

Potential contributing factors include:

- task delays
- blocked work
- milestone delays
- deadline pressure
- inactivity
- unresolved risks
- integration failures
- project execution signals

AI can analyze these signals and recommend actions.

AI cannot directly set the authoritative health value.

Health transitions are recorded in `project_health_history`.

---

# 44. Phase Model

Canonical project lifecycle:

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

The current phase is stored on `project_instances`.

Transitions are performed through deterministic project lifecycle services.

Phase history preserves previous/current transitions and reasons.

---

# 45. Document Source-of-Truth Rule

Structured database entities are authoritative.

Markdown documents are generated representations.

For example:

```text
Project Profile DB
       ↓
Project Profile Renderer
       ↓
Project Profile.md
```

The inverse is not automatically true.

Editing or replacing a generated Markdown document does not silently mutate authoritative project state.

Where user-approved document changes are supported, they must pass through an explicit application workflow.

---

# 46. RAG Source-of-Truth Rule

RAG is a retrieval system, not a system of record.

PostgreSQL stores:

- document identity
- project ownership
- version
- indexing state
- hashes
- chunk metadata
- authorization context

The vector layer stores/retrieves embeddings and associated retrieval data.

If the vector index conflicts with PostgreSQL metadata, PostgreSQL remains authoritative.

---

# 47. External Integration Storage

External information is persisted only when it improves:

- monitoring
- history
- synchronization
- auditability
- user experience
- deterministic application behavior

Examples:

GitHub activity may be stored because historical project monitoring is useful.

Temporary provider responses do not automatically become permanent business state.

---

# 48. AI Persistence Boundary

AI execution lifecycle is persisted independently of the browser.

Long-running execution may continue if the user closes the browser.

The database records:

- queued
- running
- completed
- failed
- cancelled

AI execution progress can be streamed to clients through SSE while persistent execution state remains in PostgreSQL.

Detailed traces primarily belong to the planned observability system/LangSmith rather than duplicating every trace payload into PostgreSQL.

---

# 49. Idempotency & Retry Safety

Retryable operations must be designed so they do not create duplicate authoritative state.

Examples:

- blueprint generation
- document generation
- RAG indexing
- GitHub synchronization
- event processing
- notifications
- AI execution steps

Potential controls include:

- unique external IDs
- execution IDs
- correlation IDs
- version identifiers
- processed timestamps
- unique constraints
- deterministic upsert behavior

---

# 50. Migration Strategy

All schema evolution uses migrations.

Rules:

1. No manual production schema drift.
2. Every structural change is represented in migration history.
3. Migrations must be reviewable.
4. Destructive migrations require explicit consideration of data preservation.
5. Seed/reference data is separated from structural migrations where practical.
6. Roll-forward recovery is preferred over risky ad-hoc production edits.

The exact migration tooling is finalized during implementation setup.

---

# 51. Timestamp Strategy

Application timestamps use UTC.

Typical fields:

- `created_at`
- `updated_at`
- `started_at`
- `completed_at`
- `occurred_at`
- `resolved_at`
- `retrieved_at`
- `indexed_at`
- `changed_at`

User-facing timezone conversion happens at the application/UI layer according to user preferences.

---

# 52. JSONB Usage Policy

JSONB is allowed for genuinely flexible data such as:

- notification metadata
- AI generation metadata
- integration metadata
- research-source metadata
- execution event payloads
- audit metadata
- configurable preferences
- flexible RAG metadata

JSONB must not be used merely to avoid designing relational tables for stable domain concepts.

For example, these remain relational:

- tasks
- milestones
- risks
- features
- project profiles
- project technologies
- assessments
- project definitions
- project instances

---

# 53. Security-Sensitive Data

Never store in ordinary application tables:

- plaintext passwords
- raw OAuth client secrets
- raw provider API keys
- private credentials
- authentication tokens unless explicitly required and securely protected
- secrets in JSONB metadata
- secrets in logs

Secret management belongs to the configuration/security architecture.

---

# 54. Admin Data Boundary

Admins can access platform/entity information required for administration.

Default admin visibility is metadata-first.

Private/deeper content requires the controlled investigation workflow:

```text
Request
  ↓
Authorization
  ↓
Minimum Required Data
  ↓
Inspection
  ↓
Audit Log
```

No database shortcut may bypass this policy.

---

# 55. Observability Boundary

PostgreSQL stores operational records required for application observability.

LangSmith/observability infrastructure is responsible for detailed AI tracing where appropriate.

Database records remain sufficient to answer operational questions such as:

- which execution ran?
- for which user/project?
- when?
- which agents ran?
- did it succeed?
- how long did it take?
- what were token counts?
- was regeneration required?

Deep trace detail does not need to be duplicated unnecessarily.

---

# 56. Database-to-Domain Ownership

Canonical ownership:

| Data | Owning Domain |
|---|---|
| User identity | Identity |
| Role/status | Identity & Access |
| Group | Organization |
| Group membership | Organization |
| Project Definition | Project |
| Definition Version | Project |
| Project Instance | Project |
| Assessment | Assessment |
| Blueprint | Project/Planning |
| Project Profile | Planning |
| Technologies | Planning/Identity |
| Features | Planning |
| Specifications | Planning |
| MVP | Planning |
| Timeline | Planning |
| Risks | Risk/Planning |
| Tasks | Execution |
| Milestones | Execution |
| Progress | Execution |
| Phase | Project Lifecycle |
| Health | Health/Risk |
| Mentor Notes | Communication |
| Help Requests | Communication |
| Notifications | Communication/Platform |
| Documents | Knowledge |
| RAG metadata | Knowledge |
| GitHub monitoring | Integrations |
| AI Executions | AI |
| Agent Executions | AI |
| AI Quality | AI |
| Domain Events | Platform |
| Audit Events | Security |
| Admin Investigations | Security |
| Account History | Identity/Security |

---

# 57. Database Architecture Rules

The following are prohibited:

- raw SQL scattered across API routes
- direct DB access from AI agents
- unrestricted AI database access
- duplicate Student/Mentor/Admin versions of the same repository logic
- giant JSON blobs replacing stable relational models
- generated Markdown as canonical state
- RAG vectors as canonical project ownership state
- blanket soft deletion
- blanket versioning
- arbitrary AI progress updates
- arbitrary AI health updates
- silent project-definition migration into existing instances
- speculative indexes everywhere
- unnecessary distributed database infrastructure
- storing provider secrets in ordinary database rows
- bypassing RLS/application authorization
- destructive cascades without domain justification

---

# 58. Final Database Architecture

The final 6B architecture is:

```text
                    GrowFlow Application
                           │
                    Application Services
                           │
                    Repository / Data Access
                           │
                    PostgreSQL / Supabase
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
   Identity            Projects           Execution
       │                   │                   │
 Organization        Assessment         Tasks/Milestones
       │                   │                   │
 Communication         Blueprint          Progress/Health
       │                   │                   │
 Knowledge           Planning             History
       │                   │
 Integrations         AI/Agents
       │                   │
       └──────────── Platform / Events ────────┘
                           │
                     Security / Audit
```

PostgreSQL remains the central authoritative data layer while specialized external systems such as vector storage, GitHub, AI providers, object storage, and LangSmith remain behind controlled integration boundaries.

---

# 59. Implementation Boundary

Part 6B defines the database architecture and logical data model.

The following are intentionally left for later implementation-specific phases:

- exact SQL migration files
- exact PostgreSQL enum implementation
- exact RLS policy SQL
- exact Supabase Auth integration
- exact repository implementations
- exact migration tool configuration
- exact vector database/provider
- exact object storage implementation
- exact worker queue implementation
- exact outbox processor
- exact AI provider gateway implementation
- exact GitHub/Tavily adapters

These decisions must not contradict the frozen logical data model.

---

# 60. Final Frozen Decisions

### Database
- PostgreSQL
- Supabase-managed platform
- PostgreSQL-first architecture

### Modeling
- relational-first
- normalized stable entities
- JSONB only where appropriate
- UUID identifiers
- UTC timestamps

### Projects
- Project Definition
- Project Definition Version
- independent Project Instance

### Assessment
- versioned core question templates
- persisted assessment questions
- sequential adaptive dynamic questions
- persisted answers

### Blueprint
- blueprint container
- blueprint versions
- structured Project Profile
- technologies
- features
- specifications
- MVP
- research provenance
- timeline

### Execution
- authoritative Tasks
- authoritative Milestones
- deterministic Progress
- canonical Phase
- canonical Health
- phase/health history

### Risks
- structured risks
- risk lifecycle
- risk history

### Change Management
- persisted Project Change Requests
- Impact Analysis → Confirmation → Regeneration → QA
- no dedicated Change/Impact Agent

### Communication
- Mentor Notes
- Help Requests
- Help Request Messages
- centralized Notifications

### Documents
- document identity
- document versions
- object-storage-compatible content references
- Markdown is representation, not source of truth

### RAG
- relational metadata
- project-scoped records
- vector layer abstracted
- RAG is retrieval, not system of record

### GitHub
- monitoring only
- connections
- repositories
- activity

### AI
- AI Executions
- Agent Executions
- AI Execution Events
- AI Quality Results
- provider-key operational metadata
- actual secrets excluded from ordinary DB storage

### Platform
- domain events
- transactional outbox approach
- canonical activity source

### Security
- audit events
- admin investigations
- account status history
- application authorization + RLS defense in depth

### Engineering
- migrations mandatory
- foreign keys
- constraints
- query-driven indexes
- controlled deletion
- retry/idempotency design
- no unnecessary infrastructure

---

# 61. Freeze Statement

**Part 6B — Database Architecture & Data Model is COMPLETE and FROZEN.**

The logical database model established here is the contract for subsequent backend implementation phases.

Future phases may refine implementation details, SQL syntax, indexes, policies, migrations, and infrastructure choices, but they must preserve the architectural decisions and ownership boundaries defined in this document unless a deliberate architecture change is explicitly approved.

**Next:** Part 6C — API Architecture.
