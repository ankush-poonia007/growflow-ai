"""
GrowFlow — Mentor Overview Service Implementation.

Aggregates truthful mentor workspace metrics from groups and project instances
without mock data or synthetic placeholders.

Architecture ref:
  Phase 7 § M01 — Mentor Overview
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from backend.app.domain.organization.models import GroupMembershipStatus
from backend.app.domain.project.models import ProjectHealth
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository

logger = get_logger("growflow.application.mentor_overview_service")


class MentorOverviewService:
    """Service aggregating metrics and status for the mentor's supervised workspace."""

    def __init__(
        self,
        group_repo: GroupRepository,
        project_repo: ProjectRepository,
    ) -> None:
        self._group_repo = group_repo
        self._project_repo = project_repo

    async def get_mentor_overview(self, mentor_id: uuid.UUID) -> dict[str, Any]:
        """Aggregate total groups, supervised students, projects, and at-risk counts."""
        groups = await self._group_repo.list_by_mentor(mentor_id)

        all_student_ids: set[str] = set()
        total_projects = 0
        total_at_risk = 0
        groups_summary: list[dict[str, Any]] = []

        for grp in groups:
            members = await self._group_repo.list_group_members(
                grp.id, status=GroupMembershipStatus.ACTIVE.value
            )
            for membership, _ in members:
                all_student_ids.add(str(membership.student_id))

            projects = await self._project_repo.list_by_group(grp.id)
            at_risk_in_group = sum(
                1
                for p in projects
                if p.health in (ProjectHealth.WARNING.value, ProjectHealth.CRITICAL.value)
            )

            total_projects += len(projects)
            total_at_risk += at_risk_in_group

            groups_summary.append(
                {
                    "id": str(grp.id),
                    "name": grp.name,
                    "join_code": grp.join_code,
                    "status": grp.status,
                    "student_count": len(members),
                    "project_count": len(projects),
                    "at_risk_count": at_risk_in_group,
                    "created_at": grp.created_at.isoformat() if grp.created_at else None,
                }
            )

        return {
            "total_groups": len(groups),
            "total_students": len(all_student_ids),
            "total_projects": total_projects,
            "at_risk_projects": total_at_risk,
            "groups": groups_summary,
        }
