"""
GrowFlow — Mentor Student Supervision Service.

Implements cross-group student supervision queries for:
- M10: Mentor Students Directory
- M11: Student Detail
- M12: Student Projects
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from backend.app.api.schemas.mentor_supervision import (
    MentorStudentDetailSchema,
    MentorStudentGroupSummarySchema,
    MentorStudentSummarySchema,
)
from backend.app.api.schemas.project import ProjectResponseSchema
from backend.app.domain.organization.models import GroupMembershipStatus
from backend.app.domain.project.models import ProjectStatus
from backend.app.shared.exceptions import AuthorizationException, NotFoundException

if TYPE_CHECKING:
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.profile_repository import ProfileRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.user_repository import UserRepository


class MentorStudentService:
    """Service providing authorized student supervision queries across mentor cohorts."""

    def __init__(
        self,
        user_repo: UserRepository,
        group_repo: GroupRepository,
        project_repo: ProjectRepository,
        profile_repo: ProfileRepository,
    ) -> None:
        self._user_repo = user_repo
        self._group_repo = group_repo
        self._project_repo = project_repo
        self._profile_repo = profile_repo

    async def list_supervised_students(
        self,
        mentor_id: uuid.UUID | str,
        *,
        group_id: uuid.UUID | str | None = None,
        search: str | None = None,
    ) -> list[MentorStudentSummarySchema]:
        """List distinct students enrolled in groups supervised by the mentor with project metrics."""
        members = await self._group_repo.list_supervised_students(
            mentor_id=mentor_id,
            group_id=group_id,
            search=search,
        )

        # Aggregate students by user id
        students_map: dict[str, dict] = {}
        for user, membership, grp in members:
            uid = str(user.id)
            if uid not in students_map:
                students_map[uid] = {
                    "student_id": uid,
                    "full_name": user.full_name or user.email,
                    "email": user.email,
                    "avatar_url": user.avatar_url,
                    "groups": [],
                }
            students_map[uid]["groups"].append(
                MentorStudentGroupSummarySchema(
                    group_id=str(grp.id),
                    group_name=grp.name,
                    joined_at=membership.joined_at,
                    membership_status=membership.status,
                )
            )

        if not students_map:
            return []

        # Load mentor groups for project filtering
        mentor_groups = await self._group_repo.list_by_mentor(mentor_id)
        mentor_group_ids = {str(g.id) for g in mentor_groups}

        # Query projects for these students in mentor's cohorts
        result: list[MentorStudentSummarySchema] = []
        for uid, sdata in students_map.items():
            all_projs = await self._project_repo.list_by_student(uid)
            supervised_projs = [
                p for p in all_projs if p.group_id and str(p.group_id) in mentor_group_ids
            ]
            active_projs = [
                p for p in supervised_projs if p.status == ProjectStatus.ACTIVE.value
            ]

            latest_proj = supervised_projs[0] if supervised_projs else None

            summary = MentorStudentSummarySchema(
                student_id=sdata["student_id"],
                full_name=sdata["full_name"],
                email=sdata["email"],
                avatar_url=sdata["avatar_url"],
                groups=sdata["groups"],
                project_count=len(supervised_projs),
                active_project_count=len(active_projs),
                latest_phase=latest_proj.current_phase if latest_proj else None,
                latest_health=latest_proj.health if latest_proj else None,
            )
            result.append(summary)

        return result

    async def get_supervised_student_detail(
        self,
        mentor_id: uuid.UUID | str,
        student_id: uuid.UUID | str,
    ) -> MentorStudentDetailSchema:
        """Fetch read-only student supervision detail, enforcing mentor authorization."""
        user = await self._user_repo.get_by_id(student_id)
        if not user:
            raise NotFoundException(f"Student {student_id} not found.", code="USER_NOT_FOUND")

        is_supervised = await self._group_repo.is_student_supervised_by_mentor(
            student_id=student_id,
            mentor_id=mentor_id,
        )
        if not is_supervised:
            raise AuthorizationException(
                "You do not supervise this student.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )

        profile = await self._profile_repo.get_student_profile(student_id)

        # Enrolled groups under this mentor
        mentor_groups = await self._group_repo.list_by_mentor(mentor_id)
        mentor_group_map = {str(g.id): g for g in mentor_groups}

        memberships = await self._group_repo.list_student_memberships(
            student_id, status=GroupMembershipStatus.ACTIVE.value
        )
        group_summaries: list[MentorStudentGroupSummarySchema] = []
        for m in memberships:
            if str(m.group_id) in mentor_group_map:
                grp = mentor_group_map[str(m.group_id)]
                group_summaries.append(
                    MentorStudentGroupSummarySchema(
                        group_id=str(grp.id),
                        group_name=grp.name,
                        joined_at=m.joined_at,
                        membership_status=m.status,
                    )
                )

        # Supervised projects
        all_projs = await self._project_repo.list_by_student(student_id)
        supervised_projs = [
            p for p in all_projs if p.group_id and str(p.group_id) in mentor_group_map
        ]

        proj_schemas = [
            ProjectResponseSchema(
                id=str(p.id),
                student_id=str(p.student_id),
                group_id=str(p.group_id) if p.group_id else None,
                project_definition_id=str(p.project_definition_id) if p.project_definition_id else None,
                source_definition_version_id=str(p.source_definition_version_id) if p.source_definition_version_id else None,
                name=p.name,
                problem=p.problem,
                proposed_solution=p.proposed_solution,
                complexity=p.complexity,
                current_phase=p.current_phase,
                health=p.health,
                progress_percentage=p.progress_percentage,
                status=p.status,
                deadline=p.deadline,
                started_at=p.started_at,
                completed_at=p.completed_at,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in supervised_projs
        ]

        return MentorStudentDetailSchema(
            student_id=str(user.id),
            full_name=user.full_name or user.email,
            email=user.email,
            avatar_url=user.avatar_url,
            bio=profile.bio if profile else None,
            goals=profile.goals if profile else None,
            interests=profile.interests if profile else None,
            groups=group_summaries,
            projects=proj_schemas,
        )

    async def list_supervised_student_projects(
        self,
        mentor_id: uuid.UUID | str,
        student_id: uuid.UUID | str,
    ) -> list[ProjectResponseSchema]:
        """List project instances belonging to a supervised student within the mentor's cohorts."""
        user = await self._user_repo.get_by_id(student_id)
        if not user:
            raise NotFoundException(f"Student {student_id} not found.", code="USER_NOT_FOUND")

        is_supervised = await self._group_repo.is_student_supervised_by_mentor(
            student_id=student_id,
            mentor_id=mentor_id,
        )
        if not is_supervised:
            raise AuthorizationException(
                "You do not supervise this student.",
                code="AUTH_FORBIDDEN_RESOURCE",
            )

        mentor_groups = await self._group_repo.list_by_mentor(mentor_id)
        mentor_group_ids = {str(g.id) for g in mentor_groups}

        all_projs = await self._project_repo.list_by_student(student_id)
        supervised_projs = [
            p for p in all_projs if p.group_id and str(p.group_id) in mentor_group_ids
        ]

        return [
            ProjectResponseSchema(
                id=str(p.id),
                student_id=str(p.student_id),
                group_id=str(p.group_id) if p.group_id else None,
                project_definition_id=str(p.project_definition_id) if p.project_definition_id else None,
                source_definition_version_id=str(p.source_definition_version_id) if p.source_definition_version_id else None,
                name=p.name,
                problem=p.problem,
                proposed_solution=p.proposed_solution,
                complexity=p.complexity,
                current_phase=p.current_phase,
                health=p.health,
                progress_percentage=p.progress_percentage,
                status=p.status,
                deadline=p.deadline,
                started_at=p.started_at,
                completed_at=p.completed_at,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in supervised_projs
        ]
