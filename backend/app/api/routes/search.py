"""
GrowFlow — Global Role-Aware Search Route Endpoints (Batch 08 / Gate 13).

Provides /api/v1/search (and /api/search) adhering to Phase 8 Batch 3 specifications:
- Role-aware filtering
- Parameterized PostgreSQL execution
- Bounded query results
- Strict authorization and tenant scoping
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Query, status

from backend.app.api.dependencies.auth import CurrentUserDep
from backend.app.api.dependencies.services import SearchServiceDep
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.search import SearchResponseDataSchema

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "",
    summary="Global Role-Aware Workspace Search",
    response_model=SearchResponseDataSchema,
    status_code=status.HTTP_200_OK,
)
async def search_workspace(
    current_user: CurrentUserDep,
    search_service: SearchServiceDep,
    q: str = Query("", max_length=100, description="Search query string"),
    category: str | None = Query(None, description="Optional category filter: projects, tasks, documents, groups, users, definitions"),
    limit: int = Query(20, ge=1, le=50, description="Maximum results"),
) -> JSONResponse:
    """
    Search across authorized resources tailored to the caller's active role.
    Excludes unauthorized resources directly at the database level.
    """
    data = await search_service.search(
        query=q,
        current_user=current_user,
        category=category,
        limit=limit,
    )
    return success_response(message="Search results retrieved.", data=data)
