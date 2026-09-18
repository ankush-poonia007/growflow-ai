"""
GrowFlow — Application Service Authorization Helpers.

Canonical authorization predicates and scoping helpers for application services.
Enforces the strict Mentor Two-Branch Supervision Rule and Cross-Role Isolation.

Architecture ref:
  6D § 2  — HTTPS -> Auth -> CurrentUser -> Role -> Resource
  6D § 17 — Resource-based authorization
  6D § 21 — Project/Resource isolation (Default Deny)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from backend.app.domain.identity.models import CurrentUser
from backend.app.shared.exceptions import AuthorizationException, NotFoundException

if TYPE_CHECKING:
    from backend.app.infrastructure.database.models.project import ProjectInstanceModel
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository


async def is_mentor_supervising_project(
    group_repo: GroupRepository | Any,
    project: Any,
    mentor_id: uuid.UUID | str,
) -> bool:
    """
    Canonical Two-Branch Mentor Supervision Rule:

    1. Cohort-assigned project (project.group_id is not None):
       Mentor access is determined strictly and exclusively by whether
       the project's assigned group belongs to this mentor.
       NEVER falls through to student enrollment check.

    2. Unassigned/individual project (project.group_id is None):
       Mentor access is granted if the student is an active member
       of any active group supervised by this mentor.
    """
    if getattr(project, "group_id", None):
        group = await group_repo.get_by_id(project.group_id)
        return bool(group and str(group.mentor_id) == str(mentor_id))

    # Unassigned / individual project branch
    student_id = getattr(project, "student_id", None)
    if not student_id:
        return False

    return bool(
        await group_repo.is_student_supervised_by_mentor(
            student_id=student_id,
            mentor_id=mentor_id,
        )
    )


async def verify_project_read_access(
    project_repo: ProjectRepository | Any,
    group_repo: GroupRepository | Any,
    project_id: uuid.UUID | str,
    current_user: CurrentUser,
) -> Any:
    """
    Canonical read access check for project-scoped application services:

    - Admin: Full governance read access
    - Student: Read access strictly if owning student (project.student_id == user.user_id)
    - Mentor: Read access governed by the canonical Two-Branch Supervision Rule
    - Default: 403 Forbidden (AUTH_FORBIDDEN_RESOURCE)
    - Nonexistent project: 404 Not Found (PROJECT_NOT_FOUND)
    """
    project = await project_repo.get_by_id(project_id)
    if project is None:
        raise NotFoundException("Project not found.", code="PROJECT_NOT_FOUND")

    if current_user.is_admin:
        return project

    if current_user.is_student and str(project.student_id) == str(current_user.user_id):
        return project

    if current_user.is_mentor and await is_mentor_supervising_project(
        group_repo, project, current_user.user_id
    ):
        return project

    raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")
