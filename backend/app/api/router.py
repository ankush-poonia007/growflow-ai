"""
GrowFlow — Root API Router Composition.

Mounts all sub-routers under the approved /api/v1 prefix per Phase 6C.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import (
    auth,
    groups,
    health,
    mentors,
    project_definitions,
    projects,
    students,
    users,
)

api_v1_router = APIRouter(prefix="/api/v1")

# Mount foundational routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)

# Mount Gate 05 Core Domain routers
api_v1_router.include_router(users.router)
api_v1_router.include_router(students.router)
api_v1_router.include_router(mentors.router)
api_v1_router.include_router(groups.router)
api_v1_router.include_router(project_definitions.router)
api_v1_router.include_router(projects.router)

__all__ = ["api_v1_router"]
