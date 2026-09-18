"""
GrowFlow — Role-Aware Global Search Service (Batch 08 / Gate 13).

Provides backend-authoritative discovery across authorized resources based on
the authenticated user's active role/workplace. Enforces tenancy boundaries and
excludes unauthorized resources directly at the database query level.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import or_, select

from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectMilestoneModel,
    ProjectTaskModel,
)
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectInstanceModel,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.database.models.workspace_extensions import (
    ProjectChangeRequestModel,
    ProjectHelpRequestModel,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.domain.identity.models import CurrentUser


class SearchService:
    """Centralized service performing role-scoped workspace discovery."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self,
        query: str,
        current_user: CurrentUser,
        *,
        category: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Execute role-scoped search across canonical database resources.
        Returns unified results dictionary.
        """
        clean_q = query.strip()
        if not clean_q:
            workplace = "GOVERN" if current_user.is_admin else ("SUPERVISE" if current_user.is_mentor else "BUILD")
            return {
                "query": "",
                "workplace": workplace,
                "total": 0,
                "results": [],
            }

        limit = max(1, min(limit, 50))

        if current_user.is_admin:
            return await self._search_admin(clean_q, current_user, category=category, limit=limit)
        elif current_user.is_mentor:
            return await self._search_mentor(clean_q, current_user, category=category, limit=limit)
        else:
            return await self._search_student(clean_q, current_user, category=category, limit=limit)

    async def _search_student(
        self,
        q: str,
        current_user: CurrentUser,
        *,
        category: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        term = f"%{q}%"
        student_id = str(current_user.user_id)
        results: list[dict[str, Any]] = []

        # 1. Student's Own Projects
        if not category or category in ("projects", "all"):
            stmt = (
                select(ProjectInstanceModel)
                .where(
                    ProjectInstanceModel.student_id == student_id,
                    or_(
                        ProjectInstanceModel.name.ilike(term),
                        ProjectInstanceModel.problem.ilike(term),
                    ),
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for p in res.scalars().all():
                results.append({
                    "title": p.name,
                    "subtitle": f"Phase: {p.current_phase} • Health: {p.health}",
                    "resource_type": "project",
                    "url": f"/student/projects/{p.id}",
                    "badge": "PROJECT",
                    "metadata": {"phase": p.current_phase, "health": p.health, "status": p.status},
                })

        # Fetch student project IDs to scope tasks, milestones, documents
        stmt_pids = select(ProjectInstanceModel.id).where(ProjectInstanceModel.student_id == student_id)
        res_pids = await self._session.execute(stmt_pids)
        project_ids = [str(pid) for pid in res_pids.scalars().all()]

        if project_ids:
            # 2. Student's Tasks
            if not category or category in ("tasks", "all"):
                stmt = (
                    select(ProjectTaskModel)
                    .where(
                        ProjectTaskModel.project_instance_id.in_(project_ids),
                        or_(
                            ProjectTaskModel.title.ilike(term),
                            ProjectTaskModel.task_code.ilike(term),
                            ProjectTaskModel.description.ilike(term),
                        ),
                    )
                    .limit(limit)
                )
                res = await self._session.execute(stmt)
                for t in res.scalars().all():
                    results.append({
                        "title": f"{t.task_code}: {t.title}",
                        "subtitle": f"Status: {t.status} • Task code: {t.task_code}",
                        "resource_type": "task",
                        "url": f"/student/projects/{t.project_instance_id}/tasks",
                        "badge": "TASK",
                        "metadata": {"status": t.status, "project_id": t.project_instance_id},
                    })

            # 3. Student's Milestones
            if not category or category in ("milestones", "all"):
                stmt = (
                    select(ProjectMilestoneModel)
                    .where(
                        ProjectMilestoneModel.project_instance_id.in_(project_ids),
                        ProjectMilestoneModel.title.ilike(term),
                    )
                    .limit(limit)
                )
                res = await self._session.execute(stmt)
                for m in res.scalars().all():
                    results.append({
                        "title": m.title,
                        "subtitle": f"Status: {m.status} • Order: {m.sequence_order}",
                        "resource_type": "milestone",
                        "url": f"/student/projects/{m.project_instance_id}/milestones",
                        "badge": "MILESTONE",
                        "metadata": {"status": m.status, "project_id": m.project_instance_id},
                    })

            # 4. Student's Documents
            if not category or category in ("documents", "all"):
                stmt = (
                    select(ProjectDocumentModel)
                    .where(
                        ProjectDocumentModel.project_instance_id.in_(project_ids),
                        ProjectDocumentModel.title.ilike(term),
                    )
                    .limit(limit)
                )
                res = await self._session.execute(stmt)
                for d in res.scalars().all():
                    results.append({
                        "title": d.title,
                        "subtitle": f"Type: {d.doc_type} • Status: {d.status}",
                        "resource_type": "document",
                        "url": f"/student/projects/{d.project_instance_id}/documents",
                        "badge": "DOCUMENT",
                        "metadata": {"doc_type": d.doc_type, "project_id": d.project_instance_id},
                    })

        # 5. Published Mentor Project Definitions (Catalog Discovery)
        if not category or category in ("definitions", "all"):
            stmt = (
                select(ProjectDefinitionModel)
                .where(
                    ProjectDefinitionModel.status == "PUBLISHED",
                    ProjectDefinitionModel.name.ilike(term),
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for d in res.scalars().all():
                results.append({
                    "title": d.name,
                    "subtitle": f"Status: {d.status} • Catalog Definition",
                    "resource_type": "definition",
                    "url": f"/student/projects/mentor-catalog/{d.id}",
                    "badge": "CATALOG",
                    "metadata": {"status": d.status},
                })

        # 6. Own Help Requests
        if not category or category in ("help_requests", "all"):
            stmt = (
                select(ProjectHelpRequestModel)
                .where(
                    ProjectHelpRequestModel.student_id == student_id,
                    or_(
                        ProjectHelpRequestModel.subject.ilike(term),
                        ProjectHelpRequestModel.category.ilike(term),
                    ),
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for hr in res.scalars().all():
                results.append({
                    "title": hr.subject,
                    "subtitle": f"Priority: {hr.priority} • Status: {hr.status}",
                    "resource_type": "help_request",
                    "url": f"/student/projects/{hr.project_instance_id}/help",
                    "badge": "HELP",
                    "metadata": {"priority": hr.priority, "status": hr.status},
                })

        bounded = results[:limit]
        return {
            "query": q,
            "workplace": "BUILD",
            "total": len(bounded),
            "results": bounded,
        }

    async def _search_mentor(
        self,
        q: str,
        current_user: CurrentUser,
        *,
        category: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        term = f"%{q}%"
        mentor_id = str(current_user.user_id)
        results: list[dict[str, Any]] = []

        # Find mentor's supervised groups
        stmt_groups = select(GroupModel).where(GroupModel.mentor_id == mentor_id)
        res_groups = await self._session.execute(stmt_groups)
        mentor_groups = res_groups.scalars().all()
        mentor_group_ids = [str(g.id) for g in mentor_groups]

        # 1. Supervised Groups
        if not category or category in ("groups", "all"):
            for g in mentor_groups:
                if q.lower() in g.name.lower() or q.lower() in g.join_code.lower():
                    results.append({
                        "title": g.name,
                        "subtitle": f"Cohort code: {g.join_code} • Status: {g.status}",
                        "resource_type": "group",
                        "url": f"/mentor/groups/{g.id}",
                        "badge": "GROUP",
                        "metadata": {"code": g.join_code, "status": g.status},
                    })

        # Find supervised student IDs
        supervised_student_ids: list[str] = []
        if mentor_group_ids:
            stmt_members = select(GroupMembershipModel.student_id).where(
                GroupMembershipModel.group_id.in_(mentor_group_ids),
                GroupMembershipModel.status == "ACTIVE",
            )
            res_members = await self._session.execute(stmt_members)
            supervised_student_ids = [str(sid) for sid in res_members.scalars().all()]

        # 2. Supervised Students
        if supervised_student_ids and (not category or category in ("students", "all")):
            stmt = (
                select(UserModel)
                .where(
                    UserModel.id.in_(supervised_student_ids),
                    or_(
                        UserModel.full_name.ilike(term),
                        UserModel.email.ilike(term),
                    ),
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for s in res.scalars().all():
                results.append({
                    "title": s.full_name or s.email,
                    "subtitle": f"Student • {s.email}",
                    "resource_type": "student",
                    "url": f"/mentor/students/{s.id}",
                    "badge": "STUDENT",
                    "metadata": {"email": s.email},
                })

        # 3. Supervised Project Instances
        supervised_project_ids: list[str] = []
        if mentor_group_ids or supervised_student_ids:
            scope_conditions = []
            if mentor_group_ids:
                scope_conditions.append(ProjectInstanceModel.group_id.in_(mentor_group_ids))
            if supervised_student_ids:
                scope_conditions.append(ProjectInstanceModel.student_id.in_(supervised_student_ids))

            stmt = (
                select(ProjectInstanceModel)
                .where(
                    or_(*scope_conditions),
                    or_(
                        ProjectInstanceModel.name.ilike(term),
                        ProjectInstanceModel.problem.ilike(term),
                    ),
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            projects = res.scalars().all()
            for p in projects:
                supervised_project_ids.append(str(p.id))
                if not category or category in ("projects", "all"):
                    results.append({
                        "title": p.name,
                        "subtitle": f"Phase: {p.current_phase} • Health: {p.health}",
                        "resource_type": "project",
                        "url": f"/mentor/project-instances/{p.id}",
                        "badge": "PROJECT",
                        "metadata": {"phase": p.current_phase, "health": p.health},
                    })

            # 4. Tasks within Supervised Projects
            if supervised_project_ids and (not category or category in ("tasks", "all")):
                stmt_tasks = (
                    select(ProjectTaskModel)
                    .where(
                        ProjectTaskModel.project_instance_id.in_(supervised_project_ids),
                        or_(
                            ProjectTaskModel.title.ilike(term),
                            ProjectTaskModel.task_code.ilike(term),
                        ),
                    )
                    .limit(limit)
                )
                res_tasks = await self._session.execute(stmt_tasks)
                for t in res_tasks.scalars().all():
                    results.append({
                        "title": f"{t.task_code}: {t.title}",
                        "subtitle": f"Task Status: {t.status}",
                        "resource_type": "task",
                        "url": f"/mentor/project-instances/{t.project_instance_id}",
                        "badge": "TASK",
                        "metadata": {"task_code": t.task_code, "status": t.status},
                    })

            # 5. Help Requests in Scope
            if supervised_project_ids and (not category or category in ("help_requests", "all")):
                stmt_hr = (
                    select(ProjectHelpRequestModel)
                    .where(
                        ProjectHelpRequestModel.project_instance_id.in_(supervised_project_ids),
                        ProjectHelpRequestModel.subject.ilike(term),
                    )
                    .limit(limit)
                )
                res_hr = await self._session.execute(stmt_hr)
                for hr in res_hr.scalars().all():
                    results.append({
                        "title": hr.subject,
                        "subtitle": f"Priority: {hr.priority} • Status: {hr.status}",
                        "resource_type": "help_request",
                        "url": "/mentor/reviews/help-requests",
                        "badge": "HELP",
                        "metadata": {"priority": hr.priority, "status": hr.status},
                    })

            # 6. Change Requests in Scope
            if supervised_project_ids and (not category or category in ("changes", "all")):
                stmt_cr = (
                    select(ProjectChangeRequestModel)
                    .where(
                        ProjectChangeRequestModel.project_instance_id.in_(supervised_project_ids),
                        ProjectChangeRequestModel.change_title.ilike(term),
                    )
                    .limit(limit)
                )
                res_cr = await self._session.execute(stmt_cr)
                for cr in res_cr.scalars().all():
                    results.append({
                        "title": cr.change_title,
                        "subtitle": f"Type: {cr.change_type} • Status: {cr.status}",
                        "resource_type": "change_request",
                        "url": "/mentor/reviews/changes",
                        "badge": "CHANGE",
                        "metadata": {"change_type": cr.change_type, "status": cr.status},
                    })

        # 7. Mentor-Authored or Published Project Definitions
        if not category or category in ("definitions", "all"):
            stmt_defs = (
                select(ProjectDefinitionModel)
                .where(
                    or_(
                        ProjectDefinitionModel.owner_mentor_id == mentor_id,
                        ProjectDefinitionModel.status == "PUBLISHED",
                    ),
                    ProjectDefinitionModel.name.ilike(term),
                )
                .limit(limit)
            )
            res_defs = await self._session.execute(stmt_defs)
            for d in res_defs.scalars().all():
                results.append({
                    "title": d.name,
                    "subtitle": f"Status: {d.status} • Definition",
                    "resource_type": "definition",
                    "url": f"/mentor/projects/{d.id}",
                    "badge": "DEFINITION",
                    "metadata": {"status": d.status},
                })

        bounded = results[:limit]
        return {
            "query": q,
            "workplace": "SUPERVISE",
            "total": len(bounded),
            "results": bounded,
        }

    async def _search_admin(
        self,
        q: str,
        current_user: CurrentUser,
        *,
        category: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        term = f"%{q}%"
        results: list[dict[str, Any]] = []

        # 1. Platform Users
        if not category or category in ("users", "all"):
            stmt = (
                select(UserModel)
                .where(
                    or_(
                        UserModel.full_name.ilike(term),
                        UserModel.email.ilike(term),
                        UserModel.role.ilike(term),
                    )
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for u in res.scalars().all():
                results.append({
                    "title": u.full_name or u.email,
                    "subtitle": f"Role: {u.role} • Status: {u.status} • {u.email}",
                    "resource_type": "user",
                    "url": "/admin/users",
                    "badge": u.role,
                    "metadata": {"email": u.email, "role": u.role, "status": u.status},
                })

        # 2. Platform Groups
        if not category or category in ("groups", "all"):
            stmt = (
                select(GroupModel)
                .where(
                    or_(
                        GroupModel.name.ilike(term),
                        GroupModel.join_code.ilike(term),
                    )
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for g in res.scalars().all():
                results.append({
                    "title": g.name,
                    "subtitle": f"Code: {g.join_code} • Status: {g.status}",
                    "resource_type": "group",
                    "url": "/admin/groups",
                    "badge": "GROUP",
                    "metadata": {"code": g.join_code, "status": g.status},
                })

        # 3. Project Definitions
        if not category or category in ("definitions", "all"):
            stmt = (
                select(ProjectDefinitionModel)
                .where(ProjectDefinitionModel.name.ilike(term))
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for pd in res.scalars().all():
                results.append({
                    "title": pd.name,
                    "subtitle": f"Status: {pd.status} • Definition",
                    "resource_type": "definition",
                    "url": "/admin/project-definitions",
                    "badge": "DEFINITION",
                    "metadata": {"status": pd.status},
                })

        # 4. Project Instances
        if not category or category in ("projects", "all"):
            stmt = (
                select(ProjectInstanceModel)
                .where(
                    or_(
                        ProjectInstanceModel.name.ilike(term),
                        ProjectInstanceModel.problem.ilike(term),
                    )
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for p in res.scalars().all():
                results.append({
                    "title": p.name,
                    "subtitle": f"Phase: {p.current_phase} • Health: {p.health} • Status: {p.status}",
                    "resource_type": "project",
                    "url": "/admin/project-instances",
                    "badge": "PROJECT",
                    "metadata": {"phase": p.current_phase, "health": p.health, "status": p.status},
                })

        # 5. System Events / Audit Log
        if not category or category in ("events", "all"):
            stmt = (
                select(DomainEventModel)
                .where(
                    or_(
                        DomainEventModel.event_type.ilike(term),
                        DomainEventModel.resource_type.ilike(term),
                        DomainEventModel.correlation_id.ilike(term),
                    )
                )
                .order_by(DomainEventModel.occurred_at.desc())
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for ev in res.scalars().all():
                results.append({
                    "title": f"Event: {ev.event_type}",
                    "subtitle": f"Resource: {ev.resource_type} • Role: {ev.actor_role}",
                    "resource_type": "event",
                    "url": "/admin/system-health/events",
                    "badge": "AUDIT",
                    "metadata": {"event_type": ev.event_type, "actor_role": ev.actor_role},
                })

        # 6. Platform Documents
        if not category or category in ("documents", "all"):
            stmt = (
                select(ProjectDocumentModel)
                .where(
                    or_(
                        ProjectDocumentModel.title.ilike(term),
                        ProjectDocumentModel.doc_type.ilike(term),
                    )
                )
                .limit(limit)
            )
            res = await self._session.execute(stmt)
            for d in res.scalars().all():
                results.append({
                    "title": d.title,
                    "subtitle": f"Document Type: {d.doc_type} • Status: {d.status}",
                    "resource_type": "document",
                    "url": "/admin/documents",
                    "badge": "DOCUMENT",
                    "metadata": {"doc_type": d.doc_type, "status": d.status},
                })

        bounded = results[:limit]
        return {
            "query": q,
            "workplace": "GOVERN",
            "total": len(bounded),
            "results": bounded,
        }
