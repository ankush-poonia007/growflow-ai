"""
GrowFlow — Mentor Profile Route Endpoints.

Implements /api/v1/mentors/me per Phase 6C.

Architecture ref:
  6C § 10 — User and Profile APIs (mentors/me)
"""

from __future__ import annotations

from typing import Any
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Query, status
from fastapi.responses import (
    JSONResponse,  # noqa: TC002 — evaluated at runtime by FastAPI route inspection
)

from backend.app.api.dependencies.auth import RequireMentor  # noqa: TC001
from backend.app.api.dependencies.services import (  # noqa: TC001
    ActivityServiceDep,
    BlueprintServiceDep,
    ExecutionServiceDep,
    GitHubServiceDep,
    HelpRequestServiceDep,
    MentorAIServiceDep,
    MentorFeedbackServiceDep,
    MentorOverviewServiceDep,
    MentorStudentServiceDep,
    ProfileServiceDep,
    ProjectServiceDep,
)
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.mentor_supervision import (
    HelpRequestRespondPayload,
    MentorAIChatPayload,
    MentorAIChatResponse,
    MentorAIStatusResponse,
    MentorHelpRequestSummarySchema,
    MentorNoteCreatePayload,
    MentorNoteItemSchema,
    MentorProjectInstanceDetailSchema,
    MentorProjectInstanceSummarySchema,
    MentorStudentDetailSchema,
    MentorStudentSummarySchema,
)
from backend.app.api.schemas.profile import (
    MentorProfileResponseSchema,
    MentorProfileUpdateSchema,
)
from backend.app.api.schemas.project import ProjectResponseSchema

router = APIRouter(prefix="/mentors", tags=["Mentors"])


@router.get(
    "/me",
    summary="Get Mentor Profile",
    response_model=MentorProfileResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_mentor_me(
    current_user: RequireMentor,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    profile = await profile_service.get_or_create_mentor_profile(current_user.user_id)
    data = MentorProfileResponseSchema(
        user_id=str(profile.user_id),
        mentor_id=profile.mentor_id,
        bio=profile.bio,
        specialization=profile.specialization,
    ).model_dump()
    return success_response(message="Mentor profile retrieved.", data=data)


@router.patch(
    "/me",
    summary="Update Mentor Profile",
    response_model=MentorProfileResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_mentor_me(
    payload: MentorProfileUpdateSchema,
    current_user: RequireMentor,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    profile = await profile_service.update_mentor_profile(
        user_id=current_user.user_id,
        bio=payload.bio,
        specialization=payload.specialization,
    )
    data = MentorProfileResponseSchema(
        user_id=str(profile.user_id),
        mentor_id=profile.mentor_id,
        bio=profile.bio,
        specialization=profile.specialization,
    ).model_dump()
    return success_response(message="Mentor profile updated.", data=data)


@router.get(
    "/overview",
    summary="Get Mentor Workspace Overview",
    status_code=status.HTTP_200_OK,
)
async def get_mentor_overview(
    current_user: RequireMentor,
    overview_service: MentorOverviewServiceDep,
) -> JSONResponse:
    overview_data = await overview_service.get_mentor_overview(current_user.user_id)
    return success_response(message="Mentor overview retrieved.", data=overview_data)


# ============================================================================
# M10: Mentor Students Directory
# ============================================================================
@router.get(
    "/students",
    summary="List Supervised Students across Groups",
    response_model=list[MentorStudentSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_supervised_students(
    current_user: RequireMentor,
    mentor_student_service: MentorStudentServiceDep,
    group_id: UUID | None = Query(None, description="Optional group filter"),
    search: str | None = Query(None, description="Optional search by student name or email"),
) -> JSONResponse:
    students = await mentor_student_service.list_supervised_students(
        mentor_id=current_user.user_id,
        group_id=group_id,
        search=search,
    )
    return success_response(
        message="Supervised students retrieved.",
        data=[s.model_dump() for s in students],
    )


# ============================================================================
# M11: Student Detail
# ============================================================================
@router.get(
    "/students/{student_id}",
    summary="Get Supervised Student Detail",
    response_model=MentorStudentDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_supervised_student(
    student_id: UUID,
    current_user: RequireMentor,
    mentor_student_service: MentorStudentServiceDep,
) -> JSONResponse:
    student = await mentor_student_service.get_supervised_student_detail(
        mentor_id=current_user.user_id,
        student_id=student_id,
    )
    return success_response(
        message="Supervised student retrieved.",
        data=student.model_dump(),
    )


# ============================================================================
# M12: Student Projects
# ============================================================================
@router.get(
    "/students/{student_id}/projects",
    summary="List Supervised Student Projects",
    response_model=list[ProjectResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_supervised_student_projects(
    student_id: UUID,
    current_user: RequireMentor,
    mentor_student_service: MentorStudentServiceDep,
) -> JSONResponse:
    projects = await mentor_student_service.list_supervised_student_projects(
        mentor_id=current_user.user_id,
        student_id=student_id,
    )
    return success_response(
        message="Supervised student projects retrieved.",
        data=[p.model_dump() for p in projects],
    )


# ============================================================================
# M13: Supervised Student Activity
# ============================================================================
@router.get(
    "/students/{student_id}/activity",
    summary="List Supervised Student Activity (M13)",
    status_code=status.HTTP_200_OK,
)
async def list_supervised_student_activity(
    student_id: UUID,
    current_user: RequireMentor,
    activity_service: ActivityServiceDep,
    limit: int = Query(50, ge=1, le=100, description="Max events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> JSONResponse:
    activity = await activity_service.get_student_activity(
        student_id=student_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="Supervised student activity retrieved.",
        data=activity,
    )


# ============================================================================
# M16: Mentor Projects Directory
# ============================================================================
@router.get(
    "/projects/instances",
    summary="List Supervised Project Instances (Directory)",
    response_model=list[MentorProjectInstanceSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_supervised_project_instances_directory(
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    group_id: UUID | None = Query(None, description="Optional group filter"),
    phase: str | None = Query(None, description="Optional phase filter"),
    health: str | None = Query(None, description="Optional health filter"),
    status_filter: str | None = Query(None, alias="status", description="Optional status filter"),
    search: str | None = Query(None, description="Optional search by project or student name"),
) -> JSONResponse:
    projects = await project_service.list_supervised_projects(
        mentor_id=current_user.user_id,
        group_id=group_id,
        phase=phase,
        health=health,
        status=status_filter,
        search=search,
    )
    return success_response(
        message="Supervised project instances retrieved.",
        data=[p.model_dump() for p in projects],
    )


# ============================================================================
# M22: Student Project Instances
# ============================================================================
@router.get(
    "/project-instances",
    summary="List Student Project Instances (Monitoring Grid)",
    response_model=list[MentorProjectInstanceSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_student_project_instances(
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    group_id: UUID | None = Query(None, description="Optional group filter"),
    phase: str | None = Query(None, description="Optional phase filter"),
    health: str | None = Query(None, description="Optional health filter"),
    status_filter: str | None = Query(None, alias="status", description="Optional status filter"),
    search: str | None = Query(None, description="Optional search by project or student name"),
) -> JSONResponse:
    projects = await project_service.list_supervised_projects(
        mentor_id=current_user.user_id,
        group_id=group_id,
        phase=phase,
        health=health,
        status=status_filter,
        search=search,
    )
    return success_response(
        message="Student project instances retrieved.",
        data=[p.model_dump() for p in projects],
    )


# ============================================================================
# M23: Project Instance Detail
# ============================================================================
@router.get(
    "/project-instances/{project_id}",
    summary="Get Project Instance Detail",
    response_model=MentorProjectInstanceDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_supervised_project_instance(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
) -> JSONResponse:
    detail = await project_service.get_supervised_project_detail(
        project_id=project_id,
        mentor_id=current_user.user_id,
    )
    return success_response(
        message="Project instance details retrieved.",
        data=detail.model_dump(),
    )


def _serialize_blueprint_session(bp: Any) -> dict[str, Any]:
    if not bp:
        return {}
    feedback_dict = None
    if getattr(bp, "qa_feedback", None):
        feedback_dict = {
            "status": bp.qa_feedback.status.value if hasattr(bp.qa_feedback.status, "value") else str(bp.qa_feedback.status),
            "score": bp.qa_feedback.score,
            "summary": bp.qa_feedback.summary,
            "evaluated_criteria": getattr(bp.qa_feedback, "evaluated_criteria", {}),
            "issues": [
                {
                    "section": i.section,
                    "severity": i.severity,
                    "description": i.description,
                    "recommendation": i.recommendation,
                }
                for i in getattr(bp.qa_feedback, "issues", [])
            ],
            "recommendations": getattr(bp.qa_feedback, "recommendations", []),
        }

    return {
        "id": str(bp.id),
        "project_instance_id": str(bp.project_instance_id),
        "student_id": str(bp.student_id),
        "status": bp.status.value if hasattr(bp.status, "value") else str(bp.status),
        "current_step": getattr(bp, "current_step", None),
        "progress_percent": getattr(bp, "progress_percent", 0),
        "error_message": getattr(bp, "error_message", None),
        "failed_output_key": getattr(bp, "failed_output_key", None),
        "qa_status": bp.qa_status.value if hasattr(bp.qa_status, "value") else str(bp.qa_status),
        "qa_score": getattr(bp, "qa_score", None),
        "qa_feedback": feedback_dict,
        "approved_at": bp.approved_at.isoformat() if getattr(bp, "approved_at", None) else None,
        "created_at": bp.created_at.isoformat() if getattr(bp, "created_at", None) else None,
        "updated_at": bp.updated_at.isoformat() if getattr(bp, "updated_at", None) else None,
    }


# ============================================================================
# M24: Supervised Project Instance Blueprint
# ============================================================================
@router.get(
    "/project-instances/{project_id}/blueprint",
    summary="Get Supervised Project Instance Blueprint (M24)",
    status_code=status.HTTP_200_OK,
)
async def get_supervised_project_blueprint(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    blueprint_service: BlueprintServiceDep,
) -> JSONResponse:
    detail = await project_service.get_supervised_project_detail(
        project_id=project_id,
        mentor_id=current_user.user_id,
    )
    bp = await blueprint_service.get_status(project_id, current_user)
    content = await blueprint_service.get_content(project_id, current_user)

    data = {
        "project": detail.model_dump(),
        "blueprint": _serialize_blueprint_session(bp),
        "content": content,
    }
    return success_response(
        message="Supervised project blueprint retrieved.",
        data=data,
    )


# ============================================================================
# M25: Supervised Project Instance Tasks
# ============================================================================
@router.get(
    "/project-instances/{project_id}/tasks",
    summary="List Supervised Project Instance Tasks (M25)",
    status_code=status.HTTP_200_OK,
)
async def list_supervised_project_tasks(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    execution_service: ExecutionServiceDep,
    status_filter: str | None = Query(None, alias="status", description="Optional status filter"),
    priority: str | None = Query(None, description="Optional priority filter"),
    milestone_id: str | None = Query(None, description="Optional milestone filter"),
    phase: str | None = Query(None, description="Optional phase filter"),
    search: str | None = Query(None, description="Optional search by task code or title"),
) -> JSONResponse:
    await project_service.assert_mentor_supervises_project(project_id, current_user.user_id)
    tasks = await execution_service.list_tasks(
        project_id=project_id,
        current_user=current_user,
        status=status_filter,
        priority=priority,
        milestone_id=milestone_id,
        phase=phase,
        search=search,
    )
    return success_response(
        message="Supervised project tasks retrieved.",
        data=[t.model_dump() for t in tasks],
    )


# ============================================================================
# M26: Supervised Project Instance Milestones
# ============================================================================
@router.get(
    "/project-instances/{project_id}/milestones",
    summary="List Supervised Project Instance Milestones (M26)",
    status_code=status.HTTP_200_OK,
)
async def list_supervised_project_milestones(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    await project_service.assert_mentor_supervises_project(project_id, current_user.user_id)
    milestones = await execution_service.list_milestones(
        project_id=project_id,
        current_user=current_user,
    )
    return success_response(
        message="Supervised project milestones retrieved.",
        data=[m.model_dump() for m in milestones],
    )


# ============================================================================
# M27: Supervised Project Instance Risks
# ============================================================================
@router.get(
    "/project-instances/{project_id}/risks",
    summary="List Supervised Project Instance Risks (M27)",
    status_code=status.HTTP_200_OK,
)
async def list_supervised_project_risks(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    execution_service: ExecutionServiceDep,
    status_filter: str | None = Query(None, alias="status", description="Optional status filter"),
    severity: str | None = Query(None, description="Optional severity filter"),
    search: str | None = Query(None, description="Optional search by title"),
) -> JSONResponse:
    await project_service.assert_mentor_supervises_project(project_id, current_user.user_id)
    risks = await execution_service.list_risks(
        project_id=project_id,
        current_user=current_user,
        status=status_filter,
        severity=severity,
        search=search,
    )
    return success_response(
        message="Supervised project risks retrieved.",
        data=[r.model_dump() for r in risks],
    )


# ============================================================================
# M28: Supervised Project Instance Documents
# ============================================================================
@router.get(
    "/project-instances/{project_id}/documents",
    summary="List Supervised Project Instance Documents (M28)",
    status_code=status.HTTP_200_OK,
)
async def list_supervised_project_documents(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    execution_service: ExecutionServiceDep,
    doc_type: str | None = Query(None, description="Optional doc type filter"),
    status_filter: str | None = Query(None, alias="status", description="Optional status filter"),
    search: str | None = Query(None, description="Optional search by title"),
) -> JSONResponse:
    await project_service.assert_mentor_supervises_project(project_id, current_user.user_id)
    documents = await execution_service.list_documents(
        project_id=project_id,
        current_user=current_user,
        doc_type=doc_type,
        status=status_filter,
        search=search,
    )
    return success_response(
        message="Supervised project documents retrieved.",
        data=[d.model_dump() for d in documents],
    )


# ============================================================================
# M29: Supervised Project Instance GitHub Observation
# ============================================================================
@router.get(
    "/project-instances/{project_id}/github",
    summary="Get Supervised Project Instance GitHub Integration (M29)",
    status_code=status.HTTP_200_OK,
)
async def get_supervised_project_github(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    github_service: GitHubServiceDep,
) -> JSONResponse:
    await project_service.assert_mentor_supervises_project(project_id, current_user.user_id)
    integration = await github_service.get_integration(
        project_id=project_id,
        current_user=current_user,
    )
    return success_response(
        message="Supervised project GitHub integration retrieved.",
        data=integration,
    )


# ============================================================================
# M30: Supervised Project Instance Activity
# ============================================================================
@router.get(
    "/project-instances/{project_id}/activity",
    summary="List Supervised Project Instance Activity (M30)",
    status_code=status.HTTP_200_OK,
)
async def list_supervised_project_activity(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    activity_service: ActivityServiceDep,
    limit: int = Query(50, ge=1, le=100, description="Max events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> JSONResponse:
    await project_service.assert_mentor_supervises_project(project_id, current_user.user_id)
    activity = await activity_service.get_project_activity(
        project_id=project_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="Supervised project activity retrieved.",
        data=activity,
    )



# ============================================================================
# M31: Global At-Risk Directory
# ============================================================================
@router.get(
    "/at-risk",
    summary="List Global At-Risk Projects across Groups",
    response_model=list[MentorProjectInstanceSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_at_risk_projects(
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
    group_id: UUID | None = Query(None, description="Optional group filter"),
    health: str | None = Query(None, description="Optional health filter (WARNING or CRITICAL)"),
) -> JSONResponse:
    projects = await project_service.list_at_risk_projects(
        mentor_id=current_user.user_id,
        group_id=group_id,
        health=health,
    )
    return success_response(
        message="At-risk projects retrieved.",
        data=[p.model_dump() for p in projects],
    )


# ============================================================================
# M32: Global At-Risk Detail
# ============================================================================
@router.get(
    "/at-risk/{project_id}",
    summary="Get Global At-Risk Project Detail",
    response_model=MentorProjectInstanceDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_at_risk_project(
    project_id: UUID,
    current_user: RequireMentor,
    project_service: ProjectServiceDep,
) -> JSONResponse:
    detail = await project_service.get_at_risk_project_detail(
        project_id=project_id,
        mentor_id=current_user.user_id,
    )
    return success_response(
        message="At-risk project details retrieved.",
        data=detail.model_dump(),
    )


# ============================================================================
# M33: Mentor Help Requests Inbox & Response
# ============================================================================
@router.get(
    "/help-requests",
    summary="List Help Requests across Supervised Cohorts",
    response_model=list[MentorHelpRequestSummarySchema],
    status_code=status.HTTP_200_OK,
)
async def list_mentor_help_requests(
    current_user: RequireMentor,
    help_service: HelpRequestServiceDep,
    status_filter: str | None = Query(None, alias="status", description="Filter by status: OPEN, RESOLVED, IN_PROGRESS"),
    group_id: UUID | None = Query(None, description="Optional group filter"),
) -> JSONResponse:
    requests = await help_service.list_mentor_help_requests(
        mentor_id=current_user.user_id,
        status=status_filter,
        group_id=group_id,
    )
    return success_response(
        message="Mentor help requests retrieved.",
        data=requests,
    )


@router.get(
    "/help-requests/{request_id}",
    summary="Get Detailed Help Request Context",
    response_model=MentorHelpRequestSummarySchema,
    status_code=status.HTTP_200_OK,
)
async def get_mentor_help_request_detail(
    request_id: UUID,
    current_user: RequireMentor,
    help_service: HelpRequestServiceDep,
) -> JSONResponse:
    detail = await help_service.get_mentor_help_request(
        mentor_id=current_user.user_id,
        request_id=request_id,
    )
    return success_response(
        message="Help request details retrieved.",
        data=detail,
    )


@router.post(
    "/help-requests/{request_id}/respond",
    summary="Respond to Supervised Student Help Request",
    response_model=MentorHelpRequestSummarySchema,
    status_code=status.HTTP_200_OK,
)
async def respond_to_help_request(
    request_id: UUID,
    payload: HelpRequestRespondPayload,
    current_user: RequireMentor,
    help_service: HelpRequestServiceDep,
) -> JSONResponse:
    updated = await help_service.respond_help_request(
        mentor_id=current_user.user_id,
        request_id=request_id,
        mentor_response=payload.mentor_response,
        status=payload.status,
    )
    return success_response(
        message="Help request response recorded.",
        data=updated,
    )


# ============================================================================
# M34: Mentor Notes & Feedback Management
# ============================================================================
@router.post(
    "/notes",
    summary="Create Mentor Note or Feedback on a Project Instance",
    response_model=MentorNoteItemSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_mentor_note(
    payload: MentorNoteCreatePayload,
    current_user: RequireMentor,
    feedback_service: MentorFeedbackServiceDep,
) -> JSONResponse:
    note = await feedback_service.create_mentor_note(
        mentor_id=current_user.user_id,
        project_id=payload.project_instance_id,
        title=payload.title,
        message=payload.message,
        note_type=payload.note_type,
        related_resource_type=payload.related_resource_type,
        related_resource_id=payload.related_resource_id,
    )
    return success_response(
        message="Mentor note created successfully.",
        data=note,
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/project-instances/{project_id}/notes",
    summary="List All Mentor Notes for a Project Instance",
    response_model=list[MentorNoteItemSchema],
    status_code=status.HTTP_200_OK,
)
async def list_mentor_instance_notes(
    project_id: UUID,
    current_user: RequireMentor,
    feedback_service: MentorFeedbackServiceDep,
) -> JSONResponse:
    notes = await feedback_service.list_mentor_notes_for_project(
        mentor_id=current_user.user_id,
        project_id=project_id,
    )
    return success_response(
        message="Project mentor notes retrieved.",
        data=notes,
    )


# ============================================================================
# M35: Mentor Portfolio Activity
# ============================================================================
@router.get(
    "/activity",
    summary="List Mentor Portfolio Activity (M35)",
    status_code=status.HTTP_200_OK,
)
async def list_mentor_portfolio_activity(
    current_user: RequireMentor,
    activity_service: ActivityServiceDep,
    limit: int = Query(50, ge=1, le=100, description="Max events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> JSONResponse:
    activity = await activity_service.get_mentor_activity(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="Mentor portfolio activity retrieved.",
        data=activity,
    )


# ============================================================================
# M36: Mentor Portfolio AI Status & Chat
# ============================================================================
@router.get(
    "/ai/status",
    summary="Get Mentor Portfolio AI Status (M36)",
    response_model=MentorAIStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_mentor_ai_status(
    current_user: RequireMentor,
    mentor_ai_service: MentorAIServiceDep,
) -> JSONResponse:
    status_info = await mentor_ai_service.get_mentor_ai_status(
        current_user=current_user,
    )
    return success_response(
        message="Mentor AI status retrieved.",
        data=status_info,
    )


@router.post(
    "/ai/chat",
    summary="Consult Mentor Portfolio AI (M36)",
    response_model=MentorAIChatResponse,
    status_code=status.HTTP_200_OK,
)
async def chat_mentor_portfolio_ai(
    payload: MentorAIChatPayload,
    current_user: RequireMentor,
    mentor_ai_service: MentorAIServiceDep,
) -> JSONResponse:
    result = await mentor_ai_service.chat_mentor(
        current_user=current_user,
        message=payload.message,
        history=payload.history,
    )
    return success_response(
        message="Mentor AI consultation response received.",
        data=result,
    )



