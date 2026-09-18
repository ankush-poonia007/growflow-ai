"""
GrowFlow — Admin Governance Route Endpoints.

Implements /api/v1/admin routes for platform monitoring:
- GET /api/v1/admin/overview: Platform statistics (AD01)
- GET /api/v1/admin/mentors: Mentor directory (AD02)
- GET /api/v1/admin/mentors/{mentor_id}: Mentor detail (AD03)
- GET /api/v1/admin/students: Student directory (AD04)
- GET /api/v1/admin/students/{student_id}: Student detail (AD05)

Authorization:
- Strictly guarded with RequireAdmin (HTTP 403 for Students & Mentors, HTTP 401 for Unauthenticated)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, Query, status

from backend.app.api.dependencies.auth import RequireAdmin  # noqa: TC001
from backend.app.api.dependencies.services import AdminServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.admin import (
    AdminAICostDimensionResponseSchema,
    AdminAICostResponseSchema,
    AdminAIExecutionsResponseSchema,
    AdminAIKeysResponseSchema,
    AdminAIObservatoryResponseSchema,
    AdminAIQualityResponseSchema,
    AdminAITraceDetailResponseSchema,
    AdminAIUsageResponseSchema,
    AdminAnalyticsDimensionDetailSchema,
    AdminAuditLogResponseSchema,
    AdminDocumentsResponseSchema,
    AdminGenerationJobsResponseSchema,
    AdminGroupDetailSchema,
    AdminGroupSummarySchema,
    AdminInstanceMonitoringResponseSchema,
    AdminInvestigationOverviewResponseSchema,
    AdminMentorDetailSchema,
    AdminMentorSummarySchema,
    AdminOverviewResponseSchema,
    AdminPlatformAnalyticsResponseSchema,
    AdminProjectDefinitionDetailSchema,
    AdminProjectDefinitionSummarySchema,
    AdminProjectInstanceDetailSchema,
    AdminProjectSummarySchema,
    AdminRAGDiagnosticsSchema,
    AdminSecurityOverviewSchema,
    AdminStudentDetailSchema,
    AdminStudentSummarySchema,
    AdminSubsystemDetailSchema,
    AdminSystemHealthResponseSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/admin", tags=["Admin Governance"])


@router.get(
    "/overview",
    summary="Get Platform Overview Metrics (AD01)",
    response_model=AdminOverviewResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_overview(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve platform-wide operational statistics from canonical database records."""
    metrics = await admin_service.get_overview_metrics()
    return success_response(
        message="Platform overview metrics retrieved successfully.",
        data=metrics.model_dump(),
    )


@router.get(
    "/mentors",
    summary="List Platform Mentors (AD02)",
    response_model=list[AdminMentorSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_admin_mentors(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by name, email, or specialization"),
    status: str | None = Query(None, description="Filter by account status"),
) -> JSONResponse:
    """List all registered mentors with governance metadata and cohort counts."""
    mentors = await admin_service.list_mentors(search=search, status=status)
    return success_response(
        message="Mentor directory retrieved successfully.",
        data=[m.model_dump() for m in mentors],
    )


@router.get(
    "/mentors/{mentor_id}",
    summary="Get Mentor Detail (AD03)",
    response_model=AdminMentorDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_mentor_detail(
    mentor_id: UUID,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve detailed governance view for a specific mentor."""
    mentor = await admin_service.get_mentor_detail(mentor_id)
    return success_response(
        message="Mentor details retrieved successfully.",
        data=mentor.model_dump(),
    )


@router.get(
    "/students",
    summary="List Platform Students (AD04)",
    response_model=list[AdminStudentSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_admin_students(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by name, email, college, or branch"),
    track: str | None = Query(None, description="Filter by primary learning track"),
    status: str | None = Query(None, description="Filter by account status"),
) -> JSONResponse:
    """List all registered students with profile details and project counts."""
    students = await admin_service.list_students(search=search, track=track, status=status)
    return success_response(
        message="Student directory retrieved successfully.",
        data=[s.model_dump() for s in students],
    )


@router.get(
    "/students/{student_id}",
    summary="Get Student Detail (AD05)",
    response_model=AdminStudentDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_student_detail(
    student_id: UUID,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve detailed governance view for a specific student."""
    student = await admin_service.get_student_detail(student_id)
    return success_response(
        message="Student details retrieved successfully.",
        data=student.model_dump(),
    )


# ============================================================
# AD06 — Groups Directory
# ============================================================

@router.get(
    "/groups",
    summary="List Platform Cohorts / Groups (AD06)",
    response_model=list[AdminGroupSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_admin_groups(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by name, join code, or mentor"),
    status: str | None = Query(None, description="Filter by cohort status (ACTIVE, ARCHIVED, etc.)"),
) -> JSONResponse:
    """List all platform cohorts/groups with supervising mentor, student counts, and project counts."""
    groups = await admin_service.list_groups(search=search, status=status)
    return success_response(
        message="Platform groups retrieved successfully.",
        data=[g.model_dump() for g in groups],
    )


# ============================================================
# AD07 — Group Detail
# ============================================================

@router.get(
    "/groups/{group_id}",
    summary="Get Group Governance Detail (AD07)",
    response_model=AdminGroupDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_group_detail(
    group_id: UUID,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve detailed governance view for a single cohort including mentor, students, and projects."""
    group = await admin_service.get_group_detail(group_id)
    return success_response(
        message="Group details retrieved successfully.",
        data=group.model_dump(),
    )


# ============================================================
# AD08 — Projects Directory
# ============================================================

@router.get(
    "/projects",
    summary="List Platform Project Instances (AD08)",
    response_model=list[AdminProjectSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_admin_projects(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by project name, student, mentor, or cohort"),
    phase: str | None = Query(None, description="Filter by lifecycle phase"),
    health: str | None = Query(None, description="Filter by health (HEALTHY, WARNING, CRITICAL)"),
    status: str | None = Query(None, description="Filter by status (ACTIVE, COMPLETED, etc.)"),
) -> JSONResponse:
    """List student project instances across all platform cohorts with lifecycle state and health."""
    projects = await admin_service.list_projects(
        search=search,
        phase=phase,
        health=health,
        status=status,
    )
    return success_response(
        message="Platform projects retrieved successfully.",
        data=[p.model_dump() for p in projects],
    )


# ============================================================
# AD09 — Project Definition Monitoring
# ============================================================

@router.get(
    "/definitions",
    summary="List Project Definitions Monitoring (AD09)",
    response_model=list[AdminProjectDefinitionSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_admin_definitions(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by definition title or owner mentor"),
    status: str | None = Query(None, description="Filter by definition status (DRAFT, ACTIVE, ARCHIVED)"),
) -> JSONResponse:
    """List mentor-created project definitions with versioning and adoption metrics."""
    definitions = await admin_service.list_definitions(search=search, status=status)
    return success_response(
        message="Project definitions retrieved successfully.",
        data=[d.model_dump() for d in definitions],
    )


@router.get(
    "/definitions/{definition_id}",
    summary="Get Project Definition Detail (AD09)",
    response_model=AdminProjectDefinitionDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_definition_detail(
    definition_id: UUID,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve detailed project definition governance view with immutable version tree and adoptions."""
    definition = await admin_service.get_definition_detail(definition_id)
    return success_response(
        message="Project definition details retrieved successfully.",
        data=definition.model_dump(),
    )


# ============================================================
# AD10 — Project Instance Monitoring & Canonical Detail
# ============================================================

@router.get(
    "/instances",
    summary="Get Project Instances Operational Monitoring (AD10)",
    response_model=AdminInstanceMonitoringResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_instances_monitoring(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by project name, student, mentor, or cohort"),
    phase: str | None = Query(None, description="Filter by lifecycle phase"),
    health: str | None = Query(None, description="Filter by health (HEALTHY, WARNING, CRITICAL)"),
    status: str | None = Query(None, description="Filter by status (ACTIVE, COMPLETED, etc.)"),
) -> JSONResponse:
    """Retrieve platform-wide operational instance monitoring KPIs and project instances list."""
    result = await admin_service.get_instances_monitoring(
        search=search,
        phase=phase,
        health=health,
        status=status,
    )
    return success_response(
        message="Project instances monitoring data retrieved successfully.",
        data=result.model_dump(),
    )


@router.get(
    "/instances/{project_id}",
    summary="Get Canonical Project Instance Governance Detail (AD10)",
    response_model=AdminProjectInstanceDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_instance_detail(
    project_id: UUID,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve canonical governance inspection detail for a single project instance."""
    detail = await admin_service.get_instance_detail(project_id)
    return success_response(
        message="Project instance governance detail retrieved successfully.",
        data=detail.model_dump(),
    )


# ============================================================
# AD19 — Admin System Health
# ============================================================

@router.get(
    "/health",
    summary="Get Platform System Health (AD19)",
    response_model=AdminSystemHealthResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_system_health(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve real-time platform administrative health and subsystem metrics."""
    health_data = await admin_service.get_system_health()
    return success_response(
        message="Platform system health retrieved successfully.",
        data=health_data.model_dump(),
    )


# ============================================================
# AD20 — Admin Component Detail
# ============================================================

@router.get(
    "/health/{component_id}",
    summary="Get System Component Detail (AD20)",
    response_model=AdminSubsystemDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_component_detail(
    component_id: str,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Inspect safe configuration and diagnostics for a specific subsystem."""
    detail = await admin_service.get_component_detail(component_id)
    return success_response(
        message="Component diagnostic details retrieved successfully.",
        data=detail.model_dump(),
    )


# ============================================================
# AD24 — Admin Security & Audit Overview
# ============================================================

@router.get(
    "/security/overview",
    summary="Get Security & Audit Overview (AD24)",
    response_model=AdminSecurityOverviewSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_security_overview(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve user security posture, account status counts, and audit volume."""
    overview = await admin_service.get_security_overview()
    return success_response(
        message="Security and audit overview retrieved successfully.",
        data=overview.model_dump(),
    )


# ============================================================
# AD25 — Admin Audit Log
# ============================================================

@router.get(
    "/security/audit",
    summary="Get Platform Audit Log (AD25)",
    response_model=AdminAuditLogResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_audit_log(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by ID, event type, or correlation ID"),
    actor_role: str | None = Query(None, description="Filter by actor role (STUDENT, MENTOR, ADMIN, SYSTEM)"),
    event_type: str | None = Query(None, description="Filter by event type"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
) -> JSONResponse:
    """Retrieve platform-wide canonical audit events with governance filtering and pagination."""
    audit_data = await admin_service.list_audit_log(
        search=search,
        actor_role=actor_role,
        event_type=event_type,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="Platform audit log retrieved successfully.",
        data=audit_data.model_dump(),
    )


# ============================================================
# AD26 — Admin Investigation Requests (Governed Inspection)
# ============================================================

@router.get(
    "/security/investigations",
    summary="List Governed Investigation Targets (AD26)",
    response_model=AdminInvestigationOverviewResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_investigations(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve candidate resources requiring administrative governance inspection."""
    investigations = await admin_service.get_investigation_overview()
    return success_response(
        message="Governed investigation candidate targets retrieved successfully.",
        data=investigations.model_dump(),
    )


# ============================================================
# AD27 — Admin Investigation Detail (Governed Inspection)
# ============================================================

@router.get(
    "/security/investigations/{investigation_id}",
    summary="Get Investigation Detail / Canonical Inspection (AD27)",
    status_code=status.HTTP_200_OK,
)
async def get_admin_investigation_detail(
    investigation_id: str,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Inspect designated canonical entity or return 404 (Persistent tickets not configured)."""
    detail = await admin_service.get_investigation_detail(investigation_id)
    return success_response(
        message="Governed entity inspection retrieved successfully.",
        data=detail,
    )


# ============================================================
# AD22 — Admin RAG Diagnostics & Subsystem Monitoring
# ============================================================

@router.get(
    "/documents/rag",
    summary="Get RAG Subsystem Diagnostics (AD22)",
    response_model=AdminRAGDiagnosticsSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_rag_diagnostics(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve truthful RAG subsystem configuration and deferred integration status."""
    diagnostics = await admin_service.get_rag_diagnostics()
    return success_response(
        message="RAG subsystem diagnostics retrieved successfully.",
        data=diagnostics.model_dump(),
    )


# ============================================================
# AD23 — Admin Document Generation Runs
# ============================================================

@router.get(
    "/documents/generation",
    summary="List Document Generation Runs (AD23)",
    response_model=AdminGenerationJobsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_generation_jobs(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    status: str | None = Query(None, description="Filter by job status: PENDING, RUNNING, COMPLETED, FAILED"),
    job_type: str | None = Query(None, description="Filter by job type: FULL_GENERATION, SECTION_REGENERATION"),
    project_id: UUID | None = Query(None, description="Filter by project instance UUID"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
) -> JSONResponse:
    """List asynchronous document generation runs and performance summaries from blueprint_jobs."""
    jobs_data = await admin_service.list_generation_jobs(
        status=status,
        job_type=job_type,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="Document generation runs retrieved successfully.",
        data=jobs_data.model_dump(),
    )


# ============================================================
# AD21 — Admin Documents & Knowledge Inventory
# ============================================================

@router.get(
    "/documents",
    summary="List Platform Documents (AD21)",
    response_model=AdminDocumentsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_documents(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    search: str | None = Query(None, description="Search by document title, key, or project name"),
    doc_type: str | None = Query(None, description="Filter by document type: BLUEPRINT, SPECIFICATION, README"),
    status: str | None = Query(None, description="Filter by status: ACTIVE, ARCHIVED"),
    project_id: UUID | None = Query(None, description="Filter by project instance UUID"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
) -> JSONResponse:
    """Retrieve platform-wide operational project documents with metadata and project linkage."""
    docs_data = await admin_service.list_platform_documents(
        search=search,
        doc_type=doc_type,
        status=status,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="Platform documents retrieved successfully.",
        data=docs_data.model_dump(),
    )


# ============================================================
# AD28 — Platform Macro Analytics
# ============================================================

@router.get(
    "/analytics",
    summary="Get Platform Analytics Overview (AD28)",
    response_model=AdminPlatformAnalyticsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_analytics(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve platform-wide macro metrics, project progression funnels, and event activity."""
    analytics = await admin_service.get_platform_analytics()
    return success_response(
        message="Platform analytics retrieved successfully.",
        data=analytics.model_dump(),
    )


# ============================================================
# AD29 — Analytics Dimension Detail
# ============================================================

@router.get(
    "/analytics/{dimension}",
    summary="Get Analytics Dimension Detail (AD29)",
    response_model=AdminAnalyticsDimensionDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_analytics_dimension(
    dimension: str,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve deep-dive analytics for a canonical dimension: projects, users, documents, activity."""
    detail = await admin_service.get_analytics_dimension_detail(dimension)
    return success_response(
        message=f"Analytics detail for '{dimension}' retrieved successfully.",
        data=detail.model_dump(),
    )


# ============================================================
# AD11 — Admin AI Observatory
# ============================================================

@router.get(
    "/ai/observatory",
    summary="Get AI Observatory Telemetry (AD11)",
    response_model=AdminAIObservatoryResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_observatory(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve high-level AI operational posture, active jobs, and recent execution events."""
    data = await admin_service.get_ai_observatory()
    return success_response(
        message="AI Observatory telemetry retrieved successfully.",
        data=data.model_dump(),
    )


# ============================================================
# AD12 — Admin AI Usage
# ============================================================

@router.get(
    "/ai/usage",
    summary="Get AI Usage & Transaction Volumes (AD12)",
    response_model=AdminAIUsageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_usage(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve transaction volumes, capability distribution, and time trend (token metering unpersisted)."""
    data = await admin_service.get_ai_usage()
    return success_response(
        message="AI usage metrics retrieved successfully.",
        data=data.model_dump(),
    )


# ============================================================
# AD13 — Admin Agent Executions
# ============================================================

@router.get(
    "/ai/executions",
    summary="List AI Executions (AD13)",
    response_model=AdminAIExecutionsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_executions(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
    status: str | None = Query(None, description="Filter by status (COMPLETED, FAILED, RUNNING, PENDING)"),
    job_type: str | None = Query(None, description="Filter by job type (FULL_GENERATION, TARGETED_RETRY)"),
    project_id: UUID | None = Query(None, description="Filter by project instance UUID"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
) -> JSONResponse:
    """List canonical AI generation runs with filtering, pagination, and status summaries."""
    data = await admin_service.list_ai_executions(
        status=status,
        job_type=job_type,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="AI executions retrieved successfully.",
        data=data.model_dump(),
    )


# ============================================================
# AD14 — Admin AI Trace Detail
# ============================================================

@router.get(
    "/ai/executions/{execution_id}",
    summary="Get AI Execution Trace Detail (AD14)",
    response_model=AdminAITraceDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_trace_detail(
    execution_id: str,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Reconstruct truthful partial multi-layer trace linking execution, stages, QA results, and events."""
    detail = await admin_service.get_ai_trace_detail(execution_id)
    return success_response(
        message="AI execution trace detail retrieved successfully.",
        data=detail.model_dump(),
    )


# ============================================================
# AD15 — Admin AI Quality
# ============================================================

@router.get(
    "/ai/quality",
    summary="Get AI Quality & QA Judge Telemetry (AD15)",
    response_model=AdminAIQualityResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_quality(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve authoritative QA Judge evaluation scores, criteria dimensions, and issues."""
    data = await admin_service.get_ai_quality()
    return success_response(
        message="AI Quality telemetry retrieved successfully.",
        data=data.model_dump(),
    )


# ============================================================
# AD16 — Admin AI Cost & Usage
# ============================================================

@router.get(
    "/ai/cost",
    summary="Get AI Capacity & Cost Posture (AD16)",
    response_model=AdminAICostResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_cost(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve capacity transaction volumes and unmetered provider billing posture (no fake dollar costs)."""
    data = await admin_service.get_ai_cost()
    return success_response(
        message="AI capacity and cost posture retrieved successfully.",
        data=data.model_dump(),
    )


# ============================================================
# AD17 — Admin Cost Breakdown
# ============================================================

@router.get(
    "/ai/cost/{dimension}",
    summary="Get AI Usage Volume Breakdown by Dimension (AD17)",
    response_model=AdminAICostDimensionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_cost_dimension(
    dimension: str,
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Retrieve transaction volume breakdown along canonical dimensions: agent, project, time, status."""
    detail = await admin_service.get_ai_cost_dimension(dimension)
    return success_response(
        message=f"Usage volume breakdown for '{dimension}' retrieved successfully.",
        data=detail.model_dump(),
    )


# ============================================================
# AD18 — Admin API Key Pool Monitoring
# ============================================================

@router.get(
    "/ai/keys",
    summary="Get API Key Pool Monitoring (AD18)",
    response_model=AdminAIKeysResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_admin_ai_keys(
    _admin: RequireAdmin,
    admin_service: AdminServiceDep,
) -> JSONResponse:
    """Inspect safe OpenRouter key pool slots, masked identifiers, and in-memory rotation posture."""
    keys_data = await admin_service.get_ai_keys()
    return success_response(
        message="API key pool monitoring data retrieved successfully.",
        data=keys_data.model_dump(),
    )


