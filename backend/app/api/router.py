"""
GrowFlow — Root API Router Composition.

Mounts all sub-routers under the approved /api/v1 prefix per Phase 6C.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import (
    assessment,
    auth,
    blueprint,
    contact,
    execution,
    groups,
    health,
    mentors,
    project_definitions,
    projects,
    students,
    users,
    workspace_extensions,
    admin,
    search,
    notifications,
)

api_v1_router = APIRouter(prefix="/api/v1")
api_router = APIRouter(prefix="/api")

# Mount foundational routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(contact.router)

# Mount Gate 05 Core Domain routers
api_v1_router.include_router(users.router)
api_v1_router.include_router(students.router)
api_v1_router.include_router(mentors.router)
api_v1_router.include_router(groups.router)
api_v1_router.include_router(project_definitions.router)
api_v1_router.include_router(projects.router)
api_v1_router.include_router(assessment.router)
api_v1_router.include_router(blueprint.router)
api_v1_router.include_router(execution.router)
api_v1_router.include_router(workspace_extensions.router)
api_v1_router.include_router(admin.router)

# Mount Gate 13 Search and Notifications
api_v1_router.include_router(search.router)
api_v1_router.include_router(notifications.router)

# Mount /api aliases for direct /api/search and /api/notifications calls
api_router.include_router(search.router)
api_router.include_router(notifications.router)

__all__ = ["api_v1_router", "api_router"]
