"""
GrowFlow — Admin Governance Pydantic Schemas.

Defines response models for AD01–AD05 governance views:
- AD01: Platform overview statistics
- AD02: Mentor directory
- AD03: Mentor detail
- AD04: Student directory
- AD05: Student detail

Architecture ref:
  Phase 7 Batch 7 Part 1 — Admin Foundation & People Governance
  docs/3_Admin_Side_Final_Specification.md § 2-5
  docs/5D_Admin_Application_Architecture_Final.md § 1-3
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class AdminOverviewResponseSchema(BaseModel):
    """Platform-wide operational & governance statistics."""
    model_config = ConfigDict(from_attributes=True)

    total_mentors: int = Field(..., description="Total mentor accounts")
    active_mentors: int = Field(..., description="Active mentor accounts")
    total_students: int = Field(..., description="Total student accounts")
    active_students: int = Field(..., description="Active student accounts")
    total_groups: int = Field(..., description="Total supervised cohorts")
    active_groups: int = Field(..., description="Active supervised cohorts")
    total_projects: int = Field(..., description="Total student project instances")
    active_projects: int = Field(..., description="Active student project instances")
    completed_projects: int = Field(..., description="Completed student project instances")
    at_risk_projects: int = Field(..., description="Projects with Warning or Critical health")


class AdminMentorSummarySchema(BaseModel):
    """Mentor summary item for Admin Mentor Directory (AD02)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="Mentor email address")
    full_name: str = Field(..., description="Mentor full name")
    role: str = Field(..., description="Account role (MENTOR)")
    status: str = Field(..., description="Account status (ACTIVE, SUSPENDED, etc.)")
    avatar_url: str | None = Field(None, description="Optional avatar URL")
    mentor_id: str | None = Field(None, description="Mentor business ID/code")
    designation: str | None = Field(None, description="Professional title")
    organization: str | None = Field(None, description="Affiliated organization/university")
    specialization: str | None = Field(None, description="Technical domain specialization")
    group_count: int = Field(0, description="Total cohorts created by mentor")
    student_count: int = Field(0, description="Total active students supervised across cohorts")
    project_count: int = Field(0, description="Total projects across cohorts")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AdminCohortSummarySchema(BaseModel):
    """Cohort summary within mentor or student detail view."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Group UUID")
    name: str = Field(..., description="Group name")
    join_code: str = Field(..., description="Group unique join code")
    status: str = Field(..., description="Group status")
    student_count: int = Field(0, description="Enrolled students count")
    project_count: int = Field(0, description="Group projects count")
    created_at: datetime = Field(..., description="Group creation timestamp")


class AdminSupervisedStudentSchema(BaseModel):
    """Student summary within mentor detail view."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Student User UUID")
    full_name: str = Field(..., description="Student full name")
    email: str = Field(..., description="Student email")
    group_name: str = Field(..., description="Cohort name")
    active_projects_count: int = Field(0, description="Count of active projects")


class AdminMentorDetailSchema(BaseModel):
    """Detailed mentor governance view (AD03)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="Mentor email address")
    full_name: str = Field(..., description="Mentor full name")
    role: str = Field(..., description="Account role")
    status: str = Field(..., description="Account status")
    avatar_url: str | None = Field(None, description="Optional avatar URL")
    mentor_id: str | None = Field(None, description="Mentor business ID/code")
    designation: str | None = Field(None, description="Professional title")
    organization: str | None = Field(None, description="Affiliated organization/university")
    bio: str | None = Field(None, description="Biography")
    specialization: str | None = Field(None, description="Domain specialization")
    skills: list[str] = Field(default_factory=list, description="Skill keywords")
    max_students: int | None = Field(None, description="Max student capacity")
    is_accepting_students: bool = Field(True, description="Capacity status")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    groups: list[AdminCohortSummarySchema] = Field(default_factory=list, description="Supervised cohorts")
    supervised_students: list[AdminSupervisedStudentSchema] = Field(default_factory=list, description="Enrolled students")


class AdminStudentSummarySchema(BaseModel):
    """Student summary item for Admin Student Directory (AD04)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="Student email address")
    full_name: str = Field(..., description="Student full name")
    role: str = Field(..., description="Account role (STUDENT)")
    status: str = Field(..., description="Account status (ACTIVE, etc.)")
    avatar_url: str | None = Field(None, description="Optional avatar URL")
    student_id: str | None = Field(None, description="Student business ID")
    college: str | None = Field(None, description="Educational institution")
    branch: str | None = Field(None, description="Academic department/branch")
    year_of_study: int | None = Field(None, description="Year of study")
    primary_track: str | None = Field(None, description="Primary learning track")
    group_count: int = Field(0, description="Enrolled cohorts count")
    project_count: int = Field(0, description="Total project instances")
    active_project_count: int = Field(0, description="Active projects count")
    at_risk_project_count: int = Field(0, description="Projects at risk")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AdminStudentProjectSchema(BaseModel):
    """Project instance summary within student detail view."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project instance UUID")
    name: str = Field(..., description="Project name")
    track: str = Field(default="General", description="Project track")
    current_phase: str = Field(..., description="Current lifecycle phase")
    health: str = Field(..., description="Health status (HEALTHY, WARNING, CRITICAL)")
    progress_percentage: int = Field(0, description="Overall progress percentage")
    status: str = Field(..., description="Project status (ACTIVE, COMPLETED, etc.)")
    group_name: str | None = Field(None, description="Associated cohort name if any")
    created_at: datetime = Field(..., description="Project creation timestamp")


class AdminStudentTechnologySchema(BaseModel):
    """Skill proficiency item within student detail view."""
    model_config = ConfigDict(from_attributes=True)

    technology_id: str = Field(..., description="Technology UUID")
    technology_name: str = Field(..., description="Technology display name")
    proficiency_level: str = Field(..., description="Proficiency level")


class AdminStudentMembershipSchema(BaseModel):
    """Cohort membership within student detail view."""
    model_config = ConfigDict(from_attributes=True)

    group_id: str = Field(..., description="Cohort UUID")
    group_name: str = Field(..., description="Cohort name")
    mentor_name: str = Field(..., description="Cohort supervising mentor name")
    status: str = Field(..., description="Membership status")
    joined_at: datetime = Field(..., description="Joined timestamp")


class AdminStudentDetailSchema(BaseModel):
    """Detailed student governance view (AD05)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="Student email address")
    full_name: str = Field(..., description="Student full name")
    role: str = Field(..., description="Account role")
    status: str = Field(..., description="Account status")
    avatar_url: str | None = Field(None, description="Optional avatar URL")
    student_id: str | None = Field(None, description="Student business ID")
    enrollment_number: str | None = Field(None, description="Institutional enrollment number")
    college: str | None = Field(None, description="College or institution")
    branch: str | None = Field(None, description="Academic branch")
    year_of_study: int | None = Field(None, description="Year of study")
    cgpa: float | None = Field(None, description="Current CGPA")
    primary_track: str | None = Field(None, description="Selected primary track")
    headline: str | None = Field(None, description="Profile headline")
    bio: str | None = Field(None, description="Student bio")
    target_role: str | None = Field(None, description="Target career role")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    technologies: list[AdminStudentTechnologySchema] = Field(default_factory=list, description="Self-reported skills")
    groups: list[AdminStudentMembershipSchema] = Field(default_factory=list, description="Enrolled cohorts")
    projects: list[AdminStudentProjectSchema] = Field(default_factory=list, description="Student projects")


# ============================================================
# AD06 — Groups Directory Schemas
# ============================================================

class AdminGroupSummarySchema(BaseModel):
    """Group summary item for Admin Groups Directory (AD06)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Group UUID")
    name: str = Field(..., description="Cohort/Group name")
    join_code: str = Field(..., description="Unique join code")
    status: str = Field(..., description="Cohort status (ACTIVE, ARCHIVED, etc.)")
    mentor_id: str = Field(..., description="Supervising mentor user UUID")
    mentor_name: str = Field(..., description="Supervising mentor full name")
    mentor_email: str = Field(..., description="Supervising mentor email")
    student_count: int = Field(0, description="Enrolled students count")
    project_count: int = Field(0, description="Active projects count in cohort")
    created_at: datetime = Field(..., description="Group creation timestamp")
    updated_at: datetime = Field(..., description="Group last updated timestamp")


# ============================================================
# AD07 — Group Detail Schemas
# ============================================================

class AdminGroupMemberSchema(BaseModel):
    """Student member within Admin Group Detail (AD07)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Membership record UUID")
    student_id: str = Field(..., description="Student user UUID")
    full_name: str = Field(..., description="Student full name")
    email: str = Field(..., description="Student email")
    avatar_url: str | None = Field(None, description="Student avatar URL")
    status: str = Field(..., description="Membership status")
    joined_at: datetime = Field(..., description="Timestamp student joined cohort")


class AdminGroupProjectSchema(BaseModel):
    """Project instance associated with cohort in Admin Group Detail (AD07)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project instance UUID")
    name: str = Field(..., description="Project name")
    student_id: str = Field(..., description="Student owner UUID")
    student_name: str = Field(..., description="Student full name")
    current_phase: str = Field(..., description="Lifecycle phase")
    health: str = Field(..., description="Project health")
    progress_percentage: int = Field(0, description="Progress percentage")
    status: str = Field(..., description="Project status")
    created_at: datetime = Field(..., description="Project creation timestamp")


class AdminGroupDetailSchema(BaseModel):
    """Detailed group governance view (AD07)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Group UUID")
    name: str = Field(..., description="Cohort/Group name")
    join_code: str = Field(..., description="Unique join code")
    status: str = Field(..., description="Cohort status")
    created_at: datetime = Field(..., description="Group creation timestamp")
    updated_at: datetime = Field(..., description="Group last updated timestamp")
    mentor_id: str = Field(..., description="Supervising mentor UUID")
    mentor_name: str = Field(..., description="Supervising mentor full name")
    mentor_email: str = Field(..., description="Supervising mentor email")
    mentor_avatar_url: str | None = Field(None, description="Supervising mentor avatar URL")
    mentor_specialization: str | None = Field(None, description="Supervising mentor specialization")
    student_count: int = Field(0, description="Total enrolled students")
    project_count: int = Field(0, description="Total project instances")
    active_project_count: int = Field(0, description="Active project instances count")
    members: list[AdminGroupMemberSchema] = Field(default_factory=list, description="Enrolled students list")
    projects: list[AdminGroupProjectSchema] = Field(default_factory=list, description="Cohort project instances")


# ============================================================
# AD08 & AD10 — Project Summary & Monitoring Schemas
# ============================================================

class AdminProjectSummarySchema(BaseModel):
    """Project instance summary for Admin Projects Directory (AD08) and Monitoring (AD10)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project instance UUID")
    name: str = Field(..., description="Project name")
    student_id: str = Field(..., description="Student owner UUID")
    student_name: str = Field(..., description="Student full name")
    student_email: str = Field(..., description="Student email")
    mentor_id: str | None = Field(None, description="Supervising mentor UUID")
    mentor_name: str | None = Field(None, description="Supervising mentor full name")
    group_id: str | None = Field(None, description="Cohort UUID")
    group_name: str | None = Field(None, description="Cohort name")
    current_phase: str = Field(..., description="Current lifecycle phase")
    health: str = Field(..., description="Project health")
    progress_percentage: int = Field(0, description="Progress percentage")
    status: str = Field(..., description="Project status")
    complexity: str = Field("INTERMEDIATE", description="Project complexity")
    source_definition_name: str | None = Field(None, description="Source project definition name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")


# ============================================================
# AD09 — Project Definition Monitoring Schemas
# ============================================================

class AdminProjectDefinitionSummarySchema(BaseModel):
    """Project definition summary for Admin Project Definition Monitoring (AD09)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project definition UUID")
    name: str = Field(..., description="Project definition title")
    owner_mentor_id: str = Field(..., description="Owning mentor UUID")
    owner_mentor_name: str = Field(..., description="Owning mentor full name")
    owner_mentor_email: str = Field(..., description="Owning mentor email")
    status: str = Field(..., description="Definition status (DRAFT, ACTIVE, ARCHIVED)")
    current_version_id: str | None = Field(None, description="Current pinned version UUID")
    current_version_number: int | None = Field(None, description="Current pinned version number")
    complexity: str | None = Field(None, description="Complexity from latest version")
    instance_count: int = Field(0, description="Active student project adoptions count")
    version_count: int = Field(0, description="Total immutable versions count")
    created_at: datetime = Field(..., description="Definition creation timestamp")
    updated_at: datetime = Field(..., description="Definition updated timestamp")


class AdminProjectDefinitionVersionSchema(BaseModel):
    """Immutable version snapshot within definition detail (AD09)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Version UUID")
    version_number: int = Field(..., description="Sequential version number")
    name: str = Field(..., description="Version title")
    problem: str = Field("", description="Problem statement")
    proposed_solution: str = Field("", description="Proposed solution")
    complexity: str = Field(..., description="Complexity")
    description: str = Field("", description="Description")
    duration: str = Field("", description="Duration estimate")
    constraints: str = Field("", description="Constraints")
    assumptions: str = Field("", description="Assumptions")
    technology_snapshot: list[Any] = Field(default_factory=list, description="Technology snapshot array")
    created_by: str = Field(..., description="Author user UUID")
    created_at: datetime = Field(..., description="Version creation timestamp")


class AdminProjectInstanceRefSchema(BaseModel):
    """Student project instance reference using a definition."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project instance UUID")
    name: str = Field(..., description="Project instance title")
    student_name: str = Field(..., description="Student full name")
    current_phase: str = Field(..., description="Current phase")
    health: str = Field(..., description="Project health")
    status: str = Field(..., description="Project status")


class AdminProjectDefinitionDetailSchema(BaseModel):
    """Detailed definition governance view with version tree and adoptions (AD09)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project definition UUID")
    name: str = Field(..., description="Project definition title")
    owner_mentor_id: str = Field(..., description="Owning mentor UUID")
    owner_mentor_name: str = Field(..., description="Owning mentor full name")
    owner_mentor_email: str = Field(..., description="Owning mentor email")
    status: str = Field(..., description="Definition status")
    current_version_id: str | None = Field(None, description="Current pinned version UUID")
    current_version_number: int | None = Field(None, description="Current pinned version number")
    complexity: str | None = Field(None, description="Complexity")
    instance_count: int = Field(0, description="Active adoptions count")
    version_count: int = Field(0, description="Total versions count")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")
    versions: list[AdminProjectDefinitionVersionSchema] = Field(default_factory=list, description="Immutable version tree")
    assigned_instances: list[AdminProjectInstanceRefSchema] = Field(default_factory=list, description="Adopted student instances")


# ============================================================
# AD10 — Project Instance Monitoring & Canonical Detail Schemas
# ============================================================

class AdminInstanceSummarySchema(BaseModel):
    """KPI metrics for project instance monitoring (AD10)."""
    model_config = ConfigDict(from_attributes=True)

    total_instances: int = Field(0, description="Total instances")
    healthy_count: int = Field(0, description="Healthy instances")
    warning_count: int = Field(0, description="Warning instances")
    critical_count: int = Field(0, description="Critical instances")
    completed_count: int = Field(0, description="Completed instances")


class AdminInstanceMonitoringResponseSchema(BaseModel):
    """Response payload for /admin/instances monitoring endpoint (AD10)."""
    model_config = ConfigDict(from_attributes=True)

    summary: AdminInstanceSummarySchema
    instances: list[AdminProjectSummarySchema] = Field(default_factory=list)


class AdminPhaseTransitionSchema(BaseModel):
    """Phase transition history record."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="History record UUID")
    previous_phase: str = Field(..., description="Previous lifecycle phase")
    new_phase: str = Field(..., description="New lifecycle phase")
    reason: str = Field("", description="Transition reason")
    changed_at: datetime = Field(..., description="Transition timestamp")


class AdminHealthTransitionSchema(BaseModel):
    """Health transition history record."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="History record UUID")
    previous_health: str = Field(..., description="Previous health status")
    new_health: str = Field(..., description="New health status")
    reason: str = Field("", description="Transition reason")
    changed_at: datetime = Field(..., description="Transition timestamp")


class AdminProjectInstanceDetailSchema(BaseModel):
    """Detailed project instance governance view (Canonical detail URL for AD08/AD10)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project instance UUID")
    name: str = Field(..., description="Project title")
    problem: str = Field("", description="Problem statement")
    proposed_solution: str = Field("", description="Proposed solution")
    complexity: str = Field("INTERMEDIATE", description="Project complexity")
    current_phase: str = Field(..., description="Current lifecycle phase")
    health: str = Field(..., description="Current health status")
    progress_percentage: int = Field(0, description="Progress percentage")
    status: str = Field(..., description="Project status")
    deadline: datetime | None = Field(None, description="Target deadline")
    started_at: datetime | None = Field(None, description="Started timestamp")
    completed_at: datetime | None = Field(None, description="Completed timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")

    # Student context
    student_id: str = Field(..., description="Student owner UUID")
    student_name: str = Field(..., description="Student full name")
    student_email: str = Field(..., description="Student email")
    student_avatar_url: str | None = Field(None, description="Student avatar URL")

    # Mentor & Group context
    mentor_id: str | None = Field(None, description="Supervising mentor UUID")
    mentor_name: str | None = Field(None, description="Supervising mentor full name")
    mentor_email: str | None = Field(None, description="Supervising mentor email")
    group_id: str | None = Field(None, description="Cohort UUID")
    group_name: str | None = Field(None, description="Cohort name")

    # Pinned definition context
    definition_id: str | None = Field(None, description="Pinned definition UUID")
    definition_name: str | None = Field(None, description="Pinned definition title")
    version_number: int | None = Field(None, description="Pinned definition version number")

    # Profile metadata
    profile_objective: str | None = Field(None, description="Project profile objective")
    profile_target_users: str | None = Field(None, description="Target users")
    profile_project_type: str | None = Field(None, description="Project type")
    profile_student_skill_context: str | None = Field(None, description="Student skill context")
    profile_goals: str | None = Field(None, description="Goals")
    profile_scope: str | None = Field(None, description="Scope")
    profile_expected_outcome: str | None = Field(None, description="Expected outcome")
    profile_constraints: str | None = Field(None, description="Constraints")
    profile_assumptions: str | None = Field(None, description="Assumptions")

    # Audit history
    phase_history: list[AdminPhaseTransitionSchema] = Field(default_factory=list, description="Phase transition log")
    health_history: list[AdminHealthTransitionSchema] = Field(default_factory=list, description="Health transition log")


# ============================================================
# AD19 & AD20 — System Health & Component Detail Schemas
# ============================================================

class AdminSubsystemSummarySchema(BaseModel):
    """Subsystem overview item for AD19."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique subsystem identifier")
    name: str = Field(..., description="Human-readable subsystem name")
    status: str = Field(..., description="OPERATIONAL, CONFIGURED, DEGRADED, CRITICAL, UNAVAILABLE")
    type: str = Field(..., description="Category: CORE, DATABASE, AI, MESSAGING, INTEGRATION, STORAGE")
    details: str = Field(..., description="Brief operational summary or diagnostic signal")


class AdminSystemHealthMetricsSchema(BaseModel):
    """Core health metrics for AD19."""
    model_config = ConfigDict(from_attributes=True)

    outbox_pending: int = Field(0, description="Count of pending outbox events")
    outbox_failed: int = Field(0, description="Count of failed outbox events")
    outbox_published: int = Field(0, description="Count of successfully published events")
    active_ai_keys: int = Field(0, description="Count of configured AI provider keys")
    db_pool_size: int = Field(0, description="Configured DB pool size")
    db_connected: bool = Field(True, description="Database connection confirmed")


class AdminSystemHealthResponseSchema(BaseModel):
    """Platform-wide system health aggregation (AD19)."""
    model_config = ConfigDict(from_attributes=True)

    overall_status: str = Field(..., description="OPERATIONAL, DEGRADED, CRITICAL")
    environment: str = Field(..., description="Application environment")
    version: str = Field("0.1.0", description="Application version")
    timestamp: datetime = Field(..., description="Health evaluation timestamp")
    subsystems: list[AdminSubsystemSummarySchema] = Field(default_factory=list, description="Subsystem status list")
    metrics: AdminSystemHealthMetricsSchema = Field(..., description="Key health metrics")


class AdminSubsystemDetailSchema(BaseModel):
    """Detailed component diagnostic inspection (AD20)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Component identifier")
    name: str = Field(..., description="Component human-readable name")
    status: str = Field(..., description="Status: OPERATIONAL, CONFIGURED, DEGRADED, CRITICAL, UNAVAILABLE")
    type: str = Field(..., description="Component category")
    environment: str = Field(..., description="Application environment")
    checked_at: datetime = Field(..., description="Inspection timestamp")
    configuration: dict[str, Any] = Field(default_factory=dict, description="Safe configuration signals (no secrets)")
    diagnostics: dict[str, Any] = Field(default_factory=dict, description="Safe diagnostic signals")
    recent_failures: list[dict[str, Any]] = Field(default_factory=list, description="Recent domain event failures")


# ============================================================
# AD24 — Security & Audit Overview Schemas
# ============================================================

class AdminUserSecurityPostureSchema(BaseModel):
    """User account governance distribution for AD24."""
    model_config = ConfigDict(from_attributes=True)

    total_users: int = Field(0, description="Total registered user accounts")
    active_users: int = Field(0, description="Active accounts")
    inactive_users: int = Field(0, description="Inactive accounts")
    suspended_users: int = Field(0, description="Suspended accounts")
    admin_count: int = Field(0, description="Administrator accounts")
    mentor_count: int = Field(0, description="Mentor accounts")
    student_count: int = Field(0, description="Student accounts")


class AdminAuditSummaryMetricsSchema(BaseModel):
    """Audit events summary for AD24."""
    model_config = ConfigDict(from_attributes=True)

    total_events: int = Field(0, description="Total canonical domain events")
    outbox_delivery_failures: int = Field(0, description="Events with failed delivery")


class AdminSecurityOverviewSchema(BaseModel):
    """Platform security & audit overview (AD24)."""
    model_config = ConfigDict(from_attributes=True)

    user_posture: AdminUserSecurityPostureSchema = Field(..., description="User account security posture")
    audit_summary: AdminAuditSummaryMetricsSchema = Field(..., description="Audit volume and delivery summary")
    recent_security_relevant_events: list[dict[str, Any]] = Field(default_factory=list, description="Recent governance-relevant domain events")


# ============================================================
# AD25 — Audit Log Schemas
# ============================================================

class AdminAuditEventItemSchema(BaseModel):
    """Individual audit log record derived from canonical domain_events (AD25)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Event UUID")
    event_type: str = Field(..., description="Canonical domain event type")
    title: str = Field(..., description="Human-readable event title")
    description: str = Field(..., description="Human-readable event summary")
    actor_id: str | None = Field(None, description="Actor user UUID")
    actor_role: str = Field(..., description="Actor role: STUDENT, MENTOR, ADMIN, SYSTEM")
    resource_type: str = Field(..., description="Target resource type")
    resource_id: str = Field(..., description="Target resource ID")
    project_instance_id: str | None = Field(None, description="Project instance ID if scoped")
    group_id: str | None = Field(None, description="Cohort ID if scoped")
    correlation_id: str = Field("", description="Request correlation ID")
    status: str = Field(..., description="Outbox status: PENDING, PUBLISHED, FAILED")
    occurred_at: datetime = Field(..., description="Authoritative event timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Safe governance metadata")


class AdminAuditLogResponseSchema(BaseModel):
    """Paginated audit log response (AD25)."""
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(0, description="Total matching domain events")
    limit: int = Field(50, description="Page limit")
    offset: int = Field(0, description="Page offset")
    events: list[AdminAuditEventItemSchema] = Field(default_factory=list, description="List of audit events")


# ============================================================
# AD26 & AD27 — Governed Investigation Surface Schemas
# ============================================================

class AdminInspectableResourceSchema(BaseModel):
    """Inspectable resource entry in the Governed Investigation Entry Surface (AD26)."""
    model_config = ConfigDict(from_attributes=True)

    resource_type: str = Field(..., description="Resource category: USER, PROJECT, OUTBOX_FAILURE")
    resource_id: str = Field(..., description="Resource primary identifier")
    label: str = Field(..., description="Resource name or title")
    detail: str = Field(..., description="Why this resource warrants inspection")
    flag_reason: str = Field(..., description="SUSPENDED, CRITICAL_HEALTH, DELIVERY_FAILURE")
    flagged_at: datetime | None = Field(None, description="Timestamp of flagging or event")
    canonical_inspection_url: str = Field(..., description="Existing canonical admin inspection path")


class AdminInvestigationOverviewResponseSchema(BaseModel):
    """Governed Investigation Surface overview (AD26)."""
    model_config = ConfigDict(from_attributes=True)

    framework_status: str = Field("GOVERNED_INSPECTION_ACTIVE", description="Framework state")
    disclaimer: str = Field(
        "Governed Inspection Surface: Inspects canonical resources requiring administrative review. Persistent investigation tickets are not configured in current schema.",
        description="Truthful governance description"
    )
    total_flagged: int = Field(0, description="Total flagged resources requiring review")
    flagged_resources: list[AdminInspectableResourceSchema] = Field(default_factory=list, description="Candidate resources for inspection")


# ============================================================
# AD21 — Documents & RAG Inventory Schemas
# ============================================================

class AdminDocumentItemSchema(BaseModel):
    """Canonical document item in platform inventory (AD21)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Document UUID")
    project_instance_id: str = Field(..., description="Linked project instance UUID")
    project_name: str = Field("Unknown Project", description="Linked project title")
    document_key: str = Field(..., description="Document key slug")
    title: str = Field(..., description="Document title")
    doc_type: str = Field(..., description="Document category type (BLUEPRINT, SPECIFICATION, README, etc.)")
    format: str = Field("markdown", description="Content format")
    version: str = Field("1.0", description="Version string")
    status: str = Field("ACTIVE", description="Lifecycle status")
    source: str = Field("BLUEPRINT_INIT", description="Creation source provenance")
    size_bytes: int = Field(0, description="Truthful content size in bytes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AdminDocumentsResponseSchema(BaseModel):
    """Paginated platform documents response (AD21)."""
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(0, description="Total matching documents")
    limit: int = Field(50, description="Page limit")
    offset: int = Field(0, description="Page offset")
    summary: dict[str, int] = Field(default_factory=dict, description="Counts by doc_type / status")
    documents: list[AdminDocumentItemSchema] = Field(default_factory=list, description="Document inventory")


# ============================================================
# AD22 — RAG Diagnostics & Monitoring Schemas
# ============================================================

class AdminRAGDiagnosticsSchema(BaseModel):
    """Truthful RAG architecture and configuration diagnostics (AD22)."""
    model_config = ConfigDict(from_attributes=True)

    status: str = Field("DEFERRED_INTEGRATION", description="Truthful RAG system status")
    vector_store_type: str = Field("NONE_CONFIGURED", description="Vector database implementation")
    embedding_model: str = Field("openai/text-embedding-3-small", description="Configured embedding model")
    target_chunk_size: int = Field(1000, description="Target chunk size in tokens")
    target_chunk_overlap: int = Field(150, description="Target chunk overlap in tokens")
    target_top_k: int = Field(8, description="Target retrieval depth")
    index_generated_documents: bool = Field(True, description="Whether generated documents are targeted for indexing")
    eligible_documents_count: int = Field(0, description="Active documents in database eligible for future indexing")
    disclaimer: str = Field(
        "Vector database integration is deferred in Gate 09. Document chunking and embedding storage are currently inactive.",
        description="Truthful explanation of deferred status",
    )
    recent_events: list[dict[str, Any]] = Field(default_factory=list, description="Recent RAG/document domain events")


# ============================================================
# AD23 — Document Generation Schemas
# ============================================================

class AdminGenerationJobItemSchema(BaseModel):
    """Canonical document generation run from blueprint_jobs (AD23)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Job UUID")
    blueprint_id: str = Field(..., description="Linked blueprint UUID")
    project_instance_id: str = Field(..., description="Linked project instance UUID")
    project_name: str = Field("Unknown Project", description="Linked project name")
    job_type: str = Field("FULL_GENERATION", description="Job type: FULL_GENERATION, SECTION_REGENERATION")
    target_output: str | None = Field(None, description="Target section output key")
    status: str = Field("PENDING", description="Job status: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED")
    current_step: str | None = Field(None, description="Current step name")
    progress_percent: int = Field(0, description="Progress percentage 0-100")
    error: str | None = Field(None, description="Sanitized failure error message")
    duration_seconds: int | None = Field(None, description="Duration in seconds if started and completed")
    started_at: datetime | None = Field(None, description="Job execution start timestamp")
    completed_at: datetime | None = Field(None, description="Job completion timestamp")
    created_at: datetime = Field(..., description="Job creation timestamp")


class AdminGenerationJobsSummarySchema(BaseModel):
    """Generation jobs aggregate count summary (AD23)."""
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(0, description="Total generation jobs recorded")
    completed: int = Field(0, description="Completed jobs count")
    failed: int = Field(0, description="Failed jobs count")
    running: int = Field(0, description="Currently running jobs count")
    pending: int = Field(0, description="Pending jobs count")
    average_duration_seconds: float | None = Field(None, description="Average duration of completed jobs in seconds")


class AdminGenerationJobsResponseSchema(BaseModel):
    """Paginated document generation jobs response (AD23)."""
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(0, description="Total matching generation jobs")
    limit: int = Field(50, description="Page limit")
    offset: int = Field(0, description="Page offset")
    summary: AdminGenerationJobsSummarySchema = Field(..., description="Summary counts by status")
    jobs: list[AdminGenerationJobItemSchema] = Field(default_factory=list, description="List of generation runs")


# ============================================================
# AD28 — Platform Analytics Schemas
# ============================================================

class AdminAnalyticsOverviewMetricsSchema(BaseModel):
    """Platform macro metrics derived from canonical database records (AD28)."""
    model_config = ConfigDict(from_attributes=True)

    total_users: int = Field(0, description="Total registered accounts")
    total_students: int = Field(0, description="Total enrolled students")
    total_mentors: int = Field(0, description="Total registered mentors")
    total_groups: int = Field(0, description="Total cohort groups")
    active_groups: int = Field(0, description="Active cohort groups")
    total_projects: int = Field(0, description="Total project instances")
    active_projects: int = Field(0, description="Active project instances")
    completed_projects: int = Field(0, description="Completed project instances")
    at_risk_projects: int = Field(0, description="Warning or critical health project instances")
    total_definitions: int = Field(0, description="Total project definitions")
    total_documents: int = Field(0, description="Total project documents")
    total_generation_jobs: int = Field(0, description="Total synthesis jobs")
    total_domain_events: int = Field(0, description="Total platform domain events")
    total_help_requests: int = Field(0, description="Total student help requests")


class AdminPlatformAnalyticsResponseSchema(BaseModel):
    """Comprehensive platform analytics response (AD28)."""
    model_config = ConfigDict(from_attributes=True)

    overview: AdminAnalyticsOverviewMetricsSchema = Field(..., description="Platform macro counts")
    project_phase_distribution: dict[str, int] = Field(default_factory=dict, description="Projects by phase")
    project_health_distribution: dict[str, int] = Field(default_factory=dict, description="Projects by health")
    user_status_distribution: dict[str, int] = Field(default_factory=dict, description="Users by status")
    task_status_distribution: dict[str, int] = Field(default_factory=dict, description="Execution tasks by status")
    document_type_distribution: dict[str, int] = Field(default_factory=dict, description="Documents by type")
    generation_job_distribution: dict[str, int] = Field(default_factory=dict, description="Synthesis jobs by status")
    help_request_status_distribution: dict[str, int] = Field(default_factory=dict, description="Help requests by status")
    activity_volume_recent: int = Field(0, description="Platform events occurred in the past 7 days")


# ============================================================
# AD29 — Analytics Dimension Detail Schemas
# ============================================================

class AdminAnalyticsDimensionDetailSchema(BaseModel):
    """Dimensional analytics deep-dive payload (AD29)."""
    model_config = ConfigDict(from_attributes=True)

    dimension: str = Field(..., description="Dimension key: projects, users, documents, activity")
    title: str = Field(..., description="Dimension title")
    description: str = Field(..., description="Dimension description")
    summary: dict[str, Any] = Field(default_factory=dict, description="Key metric summaries for dimension")
    breakdown: list[dict[str, Any]] = Field(default_factory=list, description="Dimensional breakdown rows or categories")
    recent_records: list[dict[str, Any]] = Field(default_factory=list, description="Relevant recent canonical records")


# ============================================================
# AD11 — AI Observatory Schemas
# ============================================================

class AdminAIGatewayPostureSchema(BaseModel):
    """AI Provider Gateway operational posture and safe configuration summary (AD11)."""
    model_config = ConfigDict(from_attributes=True)

    provider: str = Field("OpenRouter", description="Provider abstraction name")
    status: str = Field("OPERATIONAL", description="Configuration posture: OPERATIONAL or CONFIGURED")
    base_url: str = Field("https://openrouter.ai/api/v1", description="Gateway base URL")
    configured_key_slots: int = Field(0, description="Total non-placeholder API keys configured")
    total_slots: int = Field(5, description="Total supported OpenRouter key slots")
    default_model: str = Field(..., description="Default configured LLM model")
    fast_model: str = Field(..., description="Fast configured LLM model")
    standard_model: str = Field(..., description="Standard configured LLM model")
    reasoning_model: str = Field(..., description="Reasoning configured LLM model")
    fallback_model: str = Field(..., description="Fallback configured LLM model")
    request_timeout_seconds: int = Field(60, description="Gateway HTTP client timeout")
    max_retries: int = Field(3, description="Configured maximum retries")
    credential_note: str = Field(
        "Configured key count reflects presence of credentials in environment. Live provider reachability is verified per request.",
        description="Truthful credential disclosure"
    )


class AdminAIObservatoryKPISchema(BaseModel):
    """Authoritative KPI metrics for AI Observatory (AD11)."""
    model_config = ConfigDict(from_attributes=True)

    total_ai_transactions: int = Field(0, description="Total recorded AI synthesis and execution records")
    blueprint_jobs_total: int = Field(0, description="Total blueprint synthesis runs")
    blueprint_jobs_completed: int = Field(0, description="Completed blueprint synthesis runs")
    blueprint_jobs_failed: int = Field(0, description="Failed blueprint synthesis runs")
    success_rate_percent: float | None = Field(None, description="Blueprint synthesis success percentage")
    currently_running_jobs: int = Field(0, description="Active running synthesis jobs")
    average_duration_seconds: float | None = Field(None, description="Average synthesis duration in seconds")
    mentor_messages_total: int = Field(0, description="Total AI Mentor assistant responses logged")
    change_requests_total: int = Field(0, description="Total project change impact evaluations")


class AdminAIActiveJobSchema(BaseModel):
    """Active/running AI execution record (AD11)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Job UUID")
    blueprint_id: str = Field(..., description="Linked blueprint UUID")
    project_instance_id: str = Field(..., description="Linked project UUID")
    project_name: str = Field("Unknown Project", description="Linked project name")
    job_type: str = Field(..., description="Job type: FULL_GENERATION, TARGETED_RETRY")
    status: str = Field(..., description="Job status")
    current_step: str | None = Field(None, description="Current synthesis step")
    progress_percent: int = Field(0, description="Progress percentage 0-100")
    started_at: datetime | None = Field(None, description="Execution start timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")


class AdminAIRecentActivitySchema(BaseModel):
    """Recent AI domain event or execution event record (AD11)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Event or run UUID")
    activity_type: str = Field(..., description="Activity category (SYNTHESIS_JOB, DOMAIN_EVENT, MENTOR_CHAT)")
    title: str = Field(..., description="Human-readable title")
    detail: str = Field(..., description="Activity summary or status")
    status: str = Field(..., description="Status: COMPLETED, FAILED, PUBLISHED, etc.")
    project_name: str | None = Field(None, description="Project name if linked")
    correlation_id: str | None = Field(None, description="Correlation identifier")
    timestamp: datetime = Field(..., description="Occurrence timestamp")


class AdminAIObservatoryResponseSchema(BaseModel):
    """Comprehensive AI Observatory response payload (AD11)."""
    model_config = ConfigDict(from_attributes=True)

    gateway: AdminAIGatewayPostureSchema = Field(..., description="Gateway operational posture")
    kpis: AdminAIObservatoryKPISchema = Field(..., description="Platform AI execution KPIs")
    active_jobs: list[AdminAIActiveJobSchema] = Field(default_factory=list, description="Currently running jobs")
    recent_activity: list[AdminAIRecentActivitySchema] = Field(default_factory=list, description="Recent operational AI events")
    notices: dict[str, str] = Field(
        default_factory=lambda: {
            "token_metering": "UNMETERED / NOT PERSISTED",
            "dollar_cost": "NOT PERSISTED",
            "wire_telemetry": "UNAVAILABLE",
            "key_rotation": "RUNTIME_ONLY",
        },
        description="Truthful capability disclaimers"
    )


# ============================================================
# AD12 — AI Usage Schemas
# ============================================================

class AdminAIUsageOverallVolumeSchema(BaseModel):
    """Overall execution and transaction volume by source (AD12)."""
    model_config = ConfigDict(from_attributes=True)

    blueprint_synthesis_jobs: int = Field(0, description="Total blueprint synthesis jobs")
    ai_mentor_messages: int = Field(0, description="Total AI Mentor assistant responses")
    project_change_analyses: int = Field(0, description="Total project change impact evaluations")
    total_recorded_transactions: int = Field(0, description="Total recorded AI transactions")


class AdminAITimeBucketSchema(BaseModel):
    """Time-series usage aggregation bucket (AD12)."""
    model_config = ConfigDict(from_attributes=True)

    date: str = Field(..., description="Date bucket (YYYY-MM-DD)")
    blueprint_jobs_count: int = Field(0, description="Blueprint jobs created")
    mentor_messages_count: int = Field(0, description="Mentor assistant messages sent")
    total_count: int = Field(0, description="Sum of transactions for date")


class AdminAICapabilityUsageSchema(BaseModel):
    """Usage counts grouped by AI capability (AD12)."""
    model_config = ConfigDict(from_attributes=True)

    capability_key: str = Field(..., description="Capability key (BLUEPRINT_GEN, BLUEPRINT_RETRY, AI_MENTOR, CHANGE_ANALYSIS)")
    label: str = Field(..., description="Human-readable capability label")
    count: int = Field(0, description="Total execution transactions")
    percentage: float = Field(0.0, description="Percentage of total transactions")


class AdminAIProjectUsageSchema(BaseModel):
    """Project-scoped AI execution volume (AD12)."""
    model_config = ConfigDict(from_attributes=True)

    project_id: str = Field(..., description="Project instance UUID")
    project_name: str = Field(..., description="Project name")
    synthesis_jobs_count: int = Field(0, description="Synthesis jobs recorded")
    mentor_messages_count: int = Field(0, description="Mentor messages recorded")
    total_transactions: int = Field(0, description="Total transactions for project")


class AdminAIUsageResponseSchema(BaseModel):
    """AI Usage dashboard response payload (AD12)."""
    model_config = ConfigDict(from_attributes=True)

    overall_volume: AdminAIUsageOverallVolumeSchema = Field(..., description="Overall volume counts")
    time_trend: list[AdminAITimeBucketSchema] = Field(default_factory=list, description="Usage volume over time")
    capability_breakdown: list[AdminAICapabilityUsageSchema] = Field(default_factory=list, description="Volume by capability")
    project_distribution: list[AdminAIProjectUsageSchema] = Field(default_factory=list, description="Top projects by volume")
    outcome_distribution: dict[str, int] = Field(default_factory=dict, description="Outcomes by status (COMPLETED, FAILED, etc.)")
    token_metering: str = Field("UNMETERED / NOT PERSISTED", description="Truthful token posture")
    rate_limit_telemetry: str = Field("NOT PERSISTED", description="Truthful 429 telemetry posture")


# ============================================================
# AD13 — Agent Executions Schemas
# ============================================================

class AdminAIExecutionItemSchema(BaseModel):
    """Canonical execution record item (AD13)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Job UUID")
    source: str = Field("blueprint_jobs", description="Canonical data table source")
    project_instance_id: str = Field(..., description="Linked project UUID")
    project_name: str = Field("Unknown Project", description="Linked project name")
    capability: str = Field(..., description="Capability / Engine name")
    job_type: str = Field(..., description="Execution type: FULL_GENERATION, TARGETED_RETRY, etc.")
    target_output: str | None = Field(None, description="Target section if targeted")
    status: str = Field(..., description="Execution status: COMPLETED, FAILED, RUNNING, PENDING")
    current_step: str | None = Field(None, description="Current or final synthesis step")
    progress_percent: int = Field(0, description="Progress 0-100")
    duration_seconds: int | None = Field(None, description="Execution duration in seconds")
    error: str | None = Field(None, description="Sanitized failure error message")
    started_at: datetime | None = Field(None, description="Execution start timestamp")
    completed_at: datetime | None = Field(None, description="Execution completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")


class AdminAIExecutionsSummarySchema(BaseModel):
    """Executions inventory summary counts (AD13)."""
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(0, description="Total matching executions")
    completed: int = Field(0, description="Completed runs")
    failed: int = Field(0, description="Failed runs")
    running: int = Field(0, description="Running runs")
    pending: int = Field(0, description="Pending runs")


class AdminAIExecutionsResponseSchema(BaseModel):
    """Paginated AI executions response (AD13)."""
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(0, description="Total matching executions")
    limit: int = Field(50, description="Page limit")
    offset: int = Field(0, description="Page offset")
    summary: AdminAIExecutionsSummarySchema = Field(..., description="Status breakdown counts")
    executions: list[AdminAIExecutionItemSchema] = Field(default_factory=list, description="Execution records")


# ============================================================
# AD14 — AI Trace Detail Schemas
# ============================================================

class AdminAITracePipelineStageSchema(BaseModel):
    """Canonical synthesis pipeline stage in trace (AD14)."""
    model_config = ConfigDict(from_attributes=True)

    stage_order: int = Field(..., description="Stage sequence index 1-10")
    section_key: str = Field(..., description="Section key")
    title: str = Field(..., description="Stage title")
    status: str = Field("COMPLETED", description="Stage status (COMPLETED, FAILED, PENDING)")
    progress_milestone: int = Field(..., description="Target progress percent (e.g. 10, 20...)")


class AdminAITraceQAFeedbackSchema(BaseModel):
    """Correlated QA evaluation result in trace (AD14)."""
    model_config = ConfigDict(from_attributes=True)

    qa_status: str = Field(..., description="QA status: PASS, FAIL, PENDING, QA_REJECTED")
    qa_score: int | None = Field(None, description="Evaluation score 0-100")
    summary: str = Field("", description="QA evaluator summary narrative")
    evaluated_criteria: dict[str, Any] = Field(default_factory=dict, description="Criteria breakdown")
    issues: list[dict[str, Any]] = Field(default_factory=list, description="Identified issues")
    recommendations: list[str] = Field(default_factory=list, description="Actionable recommendations")


class AdminAITraceDomainEventSchema(BaseModel):
    """Correlated domain outbox event in trace (AD14)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Event UUID")
    event_type: str = Field(..., description="Domain event type")
    status: str = Field(..., description="Outbox status: PUBLISHED, PENDING, FAILED")
    correlation_id: str = Field("", description="Correlation ID")
    occurred_at: datetime = Field(..., description="Occurrence timestamp")


class AdminAITraceDetailResponseSchema(BaseModel):
    """Truthful partial execution trace response (AD14)."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Execution / Job UUID")
    blueprint_id: str = Field(..., description="Linked blueprint UUID")
    project_instance_id: str = Field(..., description="Linked project UUID")
    project_name: str = Field("Unknown Project", description="Linked project title")
    student_id: str | None = Field(None, description="Student owner UUID")
    job_type: str = Field(..., description="Job execution type")
    target_output: str | None = Field(None, description="Target section output if targeted")
    status: str = Field(..., description="Execution status")
    current_step: str | None = Field(None, description="Current or terminal step")
    progress_percent: int = Field(0, description="Progress percentage 0-100")
    duration_seconds: int | None = Field(None, description="Execution duration in seconds")
    sanitized_error: str | None = Field(None, description="Sanitized failure message")
    started_at: datetime | None = Field(None, description="Execution start timestamp")
    completed_at: datetime | None = Field(None, description="Execution completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    pipeline_stages: list[AdminAITracePipelineStageSchema] = Field(default_factory=list, description="Known canonical pipeline stages")
    qa_result: AdminAITraceQAFeedbackSchema | None = Field(None, description="Correlated QA Judge outcome")
    domain_events: list[AdminAITraceDomainEventSchema] = Field(default_factory=list, description="Correlated domain events")
    telemetry_notices: dict[str, str] = Field(
        default_factory=lambda: {
            "http_wire_packets": "UNAVAILABLE",
            "dns_tls_timing": "UNAVAILABLE",
            "ttft": "UNAVAILABLE",
            "provider_wire_latency": "UNAVAILABLE",
            "langgraph_checkpoints": "UNAVAILABLE",
        },
        description="Truthful notice of unavailable low-level telemetry"
    )


# ============================================================
# AD15 — AI Quality Schemas
# ============================================================

class AdminAIQualityScoreDistributionSchema(BaseModel):
    """Distribution of QA Judge scores across evaluated blueprints (AD15)."""
    model_config = ConfigDict(from_attributes=True)

    range_0_49: int = Field(0, description="Score 0-49 (Critical / Fail)")
    range_50_69: int = Field(0, description="Score 50-69 (Low / Degraded)")
    range_70_84: int = Field(0, description="Score 70-84 (Acceptable / Moderate)")
    range_85_100: int = Field(0, description="Score 85-100 (High / Exemplary)")


class AdminAIQualityTopIssueSchema(BaseModel):
    """Aggregated issue category from persisted QA feedback (AD15)."""
    model_config = ConfigDict(from_attributes=True)

    section: str = Field(..., description="Blueprint section with issue")
    severity: str = Field(..., description="Issue severity: HIGH, MEDIUM, LOW")
    count: int = Field(1, description="Number of times identified")
    sample_description: str = Field(..., description="Representative issue description")
    recommendation: str = Field(..., description="Remediation guidance")


class AdminAIQualityResponseSchema(BaseModel):
    """Authoritative AI Quality & QA Judge evaluation telemetry (AD15)."""
    model_config = ConfigDict(from_attributes=True)

    total_evaluated: int = Field(0, description="Total blueprints and versions evaluated by QA Judge")
    passed_count: int = Field(0, description="Evaluations with PASS status")
    failed_count: int = Field(0, description="Evaluations with FAIL or QA_REJECTED status")
    pending_count: int = Field(0, description="Evaluations with PENDING status")
    pass_rate_percent: float | None = Field(None, description="QA Pass percentage")
    average_qa_score: float | None = Field(None, description="Mean QA score across evaluated records")
    min_qa_score: int | None = Field(None, description="Minimum recorded score")
    max_qa_score: int | None = Field(None, description="Maximum recorded score")
    score_distribution: AdminAIQualityScoreDistributionSchema = Field(..., description="Score brackets")
    criteria_averages: dict[str, float] = Field(default_factory=dict, description="Average scores by criterion")
    top_issues: list[AdminAIQualityTopIssueSchema] = Field(default_factory=list, description="Aggregated architectural issues")
    approval_conversion_rate: float | None = Field(None, description="Percentage of passed blueprints approved by student/mentor")
    deferred_capabilities: dict[str, str] = Field(
        default_factory=lambda: {
            "rag_faithfulness_evaluation": "DEFERRED",
            "automated_hallucination_benchmarking": "UNAVAILABLE",
            "student_csat_ratings": "UNAVAILABLE",
        },
        description="Truthful posture of deferred quality capabilities"
    )


# ============================================================
# AD16 — Cost & Usage Schemas
# ============================================================

class AdminAICostResponseSchema(BaseModel):
    """AI Capacity accounting and provider billing posture (AD16)."""
    model_config = ConfigDict(from_attributes=True)

    execution_volume_total: int = Field(0, description="Total recorded AI synthesis and execution runs")
    blueprint_jobs_count: int = Field(0, description="Blueprint synthesis runs")
    ai_mentor_messages_count: int = Field(0, description="AI Mentor assistant responses")
    change_analyses_count: int = Field(0, description="Change impact evaluations")
    active_models: list[str] = Field(default_factory=list, description="Configured active models")
    provider: str = Field("OpenRouter", description="AI Provider Gateway vendor")
    billing_model: str = Field("DIRECT_PROVIDER_BILLED — OPENROUTER", description="Authoritative billing model")
    cost_telemetry_state: str = Field("UNMETERED / NOT PERSISTED", description="Cost tracking state")
    token_metering_state: str = Field("UNMETERED / NOT PERSISTED", description="Token tracking state")
    disclaimer: str = Field(
        "OpenRouter billing is managed upstream via external provider accounts. Per-token accounting tables and dollar pricing schedules are not configured in the current database schema.",
        description="Truthful billing disclaimer"
    )


# ============================================================
# AD17 — Cost Breakdown Schemas
# ============================================================

class AdminAICostDimensionItemSchema(BaseModel):
    """Usage volume item within a breakdown dimension (AD17)."""
    model_config = ConfigDict(from_attributes=True)

    key: str = Field(..., description="Dimension item key / identifier")
    label: str = Field(..., description="Human-readable label")
    execution_count: int = Field(0, description="Recorded transaction volume")
    percentage: float = Field(0.0, description="Percentage of total volume")
    detail: str | None = Field(None, description="Optional context or secondary metric")


class AdminAICostDimensionResponseSchema(BaseModel):
    """Dimension-specific usage volume breakdown (AD17)."""
    model_config = ConfigDict(from_attributes=True)

    dimension: str = Field(..., description="Requested dimension: agent, project, time, status")
    title: str = Field(..., description="Dimension title")
    metric_type: str = Field("EXECUTION_VOLUME", description="Authoritative metric: EXECUTION_VOLUME (not dollar cost)")
    total_volume: int = Field(0, description="Total transactions in breakdown")
    items: list[AdminAICostDimensionItemSchema] = Field(default_factory=list, description="Breakdown items")
    cost_notice: str = Field(
        "Dollar cost breakdown is UNAVAILABLE because tokens and provider pricing schedules are unmetered in persistence. Data reflects canonical execution volume.",
        description="Truthful cost disclaimer"
    )


# ============================================================
# AD18 — API Key Pool Monitoring Schemas
# ============================================================

class AdminAIKeySlotSchema(BaseModel):
    """Safe representation of an OpenRouter API key slot (AD18)."""
    model_config = ConfigDict(from_attributes=True)

    slot_index: int = Field(..., description="Slot index (1 to 5)")
    slot_label: str = Field(..., description="Slot label e.g. OpenRouter Key Slot 1")
    env_var_name: str = Field(..., description="Associated environment variable name")
    status: str = Field(..., description="Status: CONFIGURED, NOT_CONFIGURED")
    provider: str = Field("OpenRouter", description="AI Provider name")
    masked_identifier: str | None = Field(None, description="Non-reversible safe masked identifier")
    rotation_posture: str = Field(..., description="ACTIVE_IN_ROTATION, STANDBY, or UNCONFIGURED")


class AdminAIKeysResponseSchema(BaseModel):
    """API Key Pool Monitoring response (AD18)."""
    model_config = ConfigDict(from_attributes=True)

    provider: str = Field("OpenRouter", description="AI Provider Gateway vendor")
    gateway_base_url: str = Field("https://openrouter.ai/api/v1", description="Provider API base URL")
    total_slots: int = Field(5, description="Supported key slots")
    configured_key_count: int = Field(0, description="Active configured key slots")
    rotation_mechanism: str = Field("In-Memory Round-Robin", description="Rotation algorithm")
    rotation_runtime_state: str = Field("RUNTIME_IN_MEMORY", description="Rotation persistence lifespan")
    slots: list[AdminAIKeySlotSchema] = Field(default_factory=list, description="Individual key slots")
    security_notice: str = Field(
        "Raw API keys, authorization headers, and environment secrets are strictly redacted. Key rotation index is managed in runtime memory across configured environment slots. Individual key rate-limit, cooldown, and historical health telemetry is not persisted in the current gateway.",
        description="Truthful security disclosure"
    )


