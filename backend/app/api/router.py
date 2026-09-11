"""
GrowFlow — Root API Router Composition.

Mounts all sub-routers under the approved /api/v1 prefix per Phase 6C.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import health

api_v1_router = APIRouter(prefix="/api/v1")

# Mount foundational routers
api_v1_router.include_router(health.router)

__all__ = ["api_v1_router"]
