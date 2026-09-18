"""
GrowFlow — Workspace Extension Route Endpoints (Batch 06: S27–S33).

Implements workspace extensions under /api/v1/projects/{project_id}:
- /github, /github/connect, /github/sync, /github/disconnect (S27)
- /activity (S28)
- /ai-mentor, /ai-mentor/chat, /ai-mentor/execute-action (S29)
- /help-requests, /help-requests/{request_id} (S30)
- /mentor-notes, /mentor-notes/{note_id}/acknowledge (S31)
- /changes, /changes/analyze, /changes/{change_id}, /changes/{change_id}/confirm (S32 & S33)
- /blueprint-versions, /blueprint-versions/{version_number}
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, Query, status

from backend.app.api.dependencies.auth import CurrentUserDep
from backend.app.api.dependencies.services import (
    ActivityServiceDep,
    AIMentorServiceDep,
    GitHubServiceDep,
    HelpRequestServiceDep,
    MentorFeedbackServiceDep,
    ProjectChangeServiceDep,
)
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.workspace_extensions import (
    AIMentorExecuteActionPayload,
    AIMentorSendMessagePayload,
    GitHubConnectPayload,
    HelpRequestCreatePayload,
    ProjectChangeAnalyzePayload,
    ProjectChangeConfirmPayload,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/projects/{project_id}", tags=["Workspace Extensions"])


# ============================================================================
# GitHub (S27)
# ============================================================================

@router.get(
    "/github",
    summary="Get GitHub Integration Status",
    status_code=status.HTTP_200_OK,
)
async def get_github(
    project_id: UUID,
    current_user: CurrentUserDep,
    github_service: GitHubServiceDep,
) -> JSONResponse:
    res = await github_service.get_integration(project_id, current_user)
    return success_response(message="GitHub integration retrieved.", data=res)


@router.post(
    "/github/connect",
    summary="Connect GitHub Repository",
    status_code=status.HTTP_200_OK,
)
async def connect_github(
    project_id: UUID,
    payload: GitHubConnectPayload,
    current_user: CurrentUserDep,
    github_service: GitHubServiceDep,
) -> JSONResponse:
    res = await github_service.connect_repository(
        project_id=project_id,
        current_user=current_user,
        repository_url=payload.repository_url,
        repository_name=payload.repository_name,
        default_branch=payload.default_branch,
    )
    return success_response(message="GitHub repository connected.", data=res)


@router.post(
    "/github/sync",
    summary="Synchronize GitHub Observation",
    status_code=status.HTTP_200_OK,
)
async def sync_github(
    project_id: UUID,
    current_user: CurrentUserDep,
    github_service: GitHubServiceDep,
) -> JSONResponse:
    res = await github_service.sync_repository(project_id, current_user)
    return success_response(message="GitHub repository synchronized.", data=res)


@router.post(
    "/github/disconnect",
    summary="Disconnect GitHub Repository",
    status_code=status.HTTP_200_OK,
)
async def disconnect_github(
    project_id: UUID,
    current_user: CurrentUserDep,
    github_service: GitHubServiceDep,
) -> JSONResponse:
    res = await github_service.disconnect_repository(project_id, current_user)
    return success_response(message="GitHub repository disconnected.", data=res)


# ============================================================================
# Activity (S28)
# ============================================================================

@router.get(
    "/activity",
    summary="List Canonical Project Activity Audit Trail",
    status_code=status.HTTP_200_OK,
)
async def get_activity(
    project_id: UUID,
    current_user: CurrentUserDep,
    activity_service: ActivityServiceDep,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> JSONResponse:
    events = await activity_service.get_project_activity(
        project_id=project_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return success_response(message="Project activity trail retrieved.", data=events)


# ============================================================================
# AI Mentor (S29)
# ============================================================================

@router.get(
    "/ai-mentor",
    summary="Get AI Mentor Consultation History",
    status_code=status.HTTP_200_OK,
)
async def get_ai_mentor(
    project_id: UUID,
    current_user: CurrentUserDep,
    ai_mentor_service: AIMentorServiceDep,
) -> JSONResponse:
    res = await ai_mentor_service.get_conversation_history(project_id, current_user)
    return success_response(message="AI Mentor consultation retrieved.", data=res)


@router.post(
    "/ai-mentor/chat",
    summary="Send Message to AI Mentor",
    status_code=status.HTTP_200_OK,
)
async def chat_ai_mentor(
    project_id: UUID,
    payload: AIMentorSendMessagePayload,
    current_user: CurrentUserDep,
    ai_mentor_service: AIMentorServiceDep,
) -> JSONResponse:
    res = await ai_mentor_service.send_message(
        project_id=project_id,
        current_user=current_user,
        content=payload.content,
    )
    return success_response(message="Message processed.", data=res)


@router.post(
    "/ai-mentor/execute-action",
    summary="Confirm Suggested Action from AI Mentor",
    status_code=status.HTTP_200_OK,
)
async def execute_ai_action(
    project_id: UUID,
    payload: AIMentorExecuteActionPayload,
    current_user: CurrentUserDep,
    ai_mentor_service: AIMentorServiceDep,
) -> JSONResponse:
    res = await ai_mentor_service.execute_suggested_action(
        project_id=project_id,
        current_user=current_user,
        action_type=payload.action_type,
        payload=payload.payload,
    )
    return success_response(message="Suggested action executed.", data=res)


# ============================================================================
# Help Requests (S30)
# ============================================================================

@router.get(
    "/help-requests",
    summary="List Project Help Requests",
    status_code=status.HTTP_200_OK,
)
async def list_help_requests(
    project_id: UUID,
    current_user: CurrentUserDep,
    help_service: HelpRequestServiceDep,
) -> JSONResponse:
    requests = await help_service.list_help_requests(project_id, current_user)
    return success_response(message="Help requests retrieved.", data=requests)


@router.post(
    "/help-requests",
    summary="Create Project Help Request",
    status_code=status.HTTP_201_CREATED,
)
async def create_help_request(
    project_id: UUID,
    payload: HelpRequestCreatePayload,
    current_user: CurrentUserDep,
    help_service: HelpRequestServiceDep,
) -> JSONResponse:
    req = await help_service.create_help_request(
        project_id=project_id,
        current_user=current_user,
        subject=payload.subject,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
    )
    return success_response(message="Help request created.", data=req, status_code=status.HTTP_201_CREATED)


@router.get(
    "/help-requests/{request_id}",
    summary="Get Project Help Request Detail",
    status_code=status.HTTP_200_OK,
)
async def get_help_request(
    project_id: UUID,
    request_id: UUID,
    current_user: CurrentUserDep,
    help_service: HelpRequestServiceDep,
) -> JSONResponse:
    req = await help_service.get_help_request(project_id, request_id, current_user)
    return success_response(message="Help request detail retrieved.", data=req)


# ============================================================================
# Mentor Feedback (S31)
# ============================================================================

@router.get(
    "/mentor-notes",
    summary="List Mentor Feedback Notes",
    status_code=status.HTTP_200_OK,
)
async def list_mentor_notes(
    project_id: UUID,
    current_user: CurrentUserDep,
    feedback_service: MentorFeedbackServiceDep,
) -> JSONResponse:
    notes = await feedback_service.list_mentor_notes(project_id, current_user)
    return success_response(message="Mentor notes retrieved.", data=notes)


@router.post(
    "/mentor-notes/{note_id}/acknowledge",
    summary="Acknowledge Mentor Feedback Note",
    status_code=status.HTTP_200_OK,
)
async def acknowledge_mentor_note(
    project_id: UUID,
    note_id: UUID,
    current_user: CurrentUserDep,
    feedback_service: MentorFeedbackServiceDep,
) -> JSONResponse:
    res = await feedback_service.acknowledge_note(project_id, note_id, current_user)
    return success_response(message="Mentor note acknowledged.", data=res)


# ============================================================================
# Project Changes & Blueprint Versions (S32 & S33)
# ============================================================================

@router.get(
    "/changes",
    summary="List Project Change Proposals",
    status_code=status.HTTP_200_OK,
)
async def list_project_changes(
    project_id: UUID,
    current_user: CurrentUserDep,
    change_service: ProjectChangeServiceDep,
) -> JSONResponse:
    changes = await change_service.list_change_requests(project_id, current_user)
    return success_response(message="Project changes retrieved.", data=changes)


@router.post(
    "/changes/analyze",
    summary="Analyze Project Change Impact",
    status_code=status.HTTP_201_CREATED,
)
async def analyze_project_change(
    project_id: UUID,
    payload: ProjectChangeAnalyzePayload,
    current_user: CurrentUserDep,
    change_service: ProjectChangeServiceDep,
) -> JSONResponse:
    res = await change_service.analyze_change(
        project_id=project_id,
        current_user=current_user,
        change_title=payload.change_title,
        change_description=payload.change_description,
        change_type=payload.change_type,
    )
    return success_response(message="Impact analysis completed.", data=res, status_code=status.HTTP_201_CREATED)


@router.get(
    "/changes/{change_id}",
    summary="Get Project Change Detail",
    status_code=status.HTTP_200_OK,
)
async def get_project_change(
    project_id: UUID,
    change_id: UUID,
    current_user: CurrentUserDep,
    change_service: ProjectChangeServiceDep,
) -> JSONResponse:
    change = await change_service.get_change_request(project_id, change_id, current_user)
    return success_response(message="Change request detail retrieved.", data=change)


@router.post(
    "/changes/{change_id}/confirm",
    summary="Confirm Project Change and Regenerate Blueprint",
    status_code=status.HTTP_200_OK,
)
async def confirm_project_change(
    project_id: UUID,
    change_id: UUID,
    payload: ProjectChangeConfirmPayload,
    current_user: CurrentUserDep,
    change_service: ProjectChangeServiceDep,
) -> JSONResponse:
    res = await change_service.confirm_change(
        project_id=project_id,
        change_id=change_id,
        current_user=current_user,
        idempotency_key=payload.idempotency_key,
    )
    return success_response(message="Change confirmed and blueprint regenerated.", data=res)


@router.get(
    "/blueprint-versions",
    summary="List Non-destructive Blueprint Versions",
    status_code=status.HTTP_200_OK,
)
async def list_blueprint_versions(
    project_id: UUID,
    current_user: CurrentUserDep,
    change_service: ProjectChangeServiceDep,
) -> JSONResponse:
    versions = await change_service.list_blueprint_versions(project_id, current_user)
    return success_response(message="Blueprint versions retrieved.", data=versions)


@router.get(
    "/blueprint-versions/{version_number}",
    summary="Get Specific Blueprint Version Snapshot",
    status_code=status.HTTP_200_OK,
)
async def get_blueprint_version(
    project_id: UUID,
    version_number: int,
    current_user: CurrentUserDep,
    change_service: ProjectChangeServiceDep,
) -> JSONResponse:
    ver = await change_service.get_blueprint_version(project_id, version_number, current_user)
    return success_response(message=f"Blueprint version {version_number} retrieved.", data=ver)
