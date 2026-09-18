"""
GrowFlow — Workspace Extension Repositories (Batch 06: S27–S33).

Provides persistence operations for:
- GitHub integrations (observation/read cache)
- Blueprint versions (non-destructive historical snapshots)
- Project change requests (impact analysis & regeneration lifecycle)
- AI mentor conversations & messages
- Project help requests (student questions/blockers)
- Project mentor notes (advisory & actionable mentor notes)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy import delete, func, select

from backend.app.infrastructure.database.models.organization import GroupModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.database.models.workspace_extensions import (
    AIMentorConversationModel,
    AIMentorMessageModel,
    ProjectBlueprintVersionModel,
    ProjectChangeRequestModel,
    ProjectGitHubIntegrationModel,
    ProjectHelpRequestModel,
    ProjectMentorNoteModel,
)
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence
    from sqlalchemy.ext.asyncio import AsyncSession


class GitHubIntegrationRepository(BaseRepository[ProjectGitHubIntegrationModel]):
    """Repository managing GitHub external observation integration state."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectGitHubIntegrationModel)

    async def get_by_project(self, project_id: uuid.UUID | str) -> ProjectGitHubIntegrationModel | None:
        stmt = select(ProjectGitHubIntegrationModel).where(
            ProjectGitHubIntegrationModel.project_instance_id == str(project_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def upsert(
        self,
        project_id: uuid.UUID | str,
        repository_name: str,
        repository_url: str,
        default_branch: str = "main",
        connection_status: str = "CONNECTED",
        commit_count: int = 0,
        cached_commits_preview: list[dict[str, Any]] | None = None,
        sync_error: str | None = None,
    ) -> ProjectGitHubIntegrationModel:
        integration = await self.get_by_project(project_id)
        if not integration:
            integration = ProjectGitHubIntegrationModel(
                id=uuid.uuid4(),
                project_instance_id=str(project_id),
                repository_name=repository_name,
                repository_url=repository_url,
                default_branch=default_branch,
                connection_status=connection_status,
                commit_count=commit_count,
                cached_commits_preview=cached_commits_preview,
                last_sync_at=datetime.now(UTC),
                sync_error=sync_error,
            )
            return await self.add(integration)

        integration.repository_name = repository_name
        integration.repository_url = repository_url
        integration.default_branch = default_branch
        integration.connection_status = connection_status
        integration.commit_count = commit_count
        if cached_commits_preview is not None:
            integration.cached_commits_preview = cached_commits_preview
        integration.last_sync_at = datetime.now(UTC)
        integration.sync_error = sync_error
        await self._session.flush()
        return integration


class BlueprintVersionRepository(BaseRepository[ProjectBlueprintVersionModel]):
    """Repository managing immutable historical blueprint snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectBlueprintVersionModel)

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectBlueprintVersionModel]:
        stmt = (
            select(ProjectBlueprintVersionModel)
            .where(ProjectBlueprintVersionModel.project_instance_id == str(project_id))
            .order_by(ProjectBlueprintVersionModel.version_number.desc())
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_version(
        self, blueprint_id: uuid.UUID | str, version_number: int
    ) -> ProjectBlueprintVersionModel | None:
        stmt = select(ProjectBlueprintVersionModel).where(
            ProjectBlueprintVersionModel.blueprint_id == str(blueprint_id),
            ProjectBlueprintVersionModel.version_number == version_number,
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_version_number(self, blueprint_id: uuid.UUID | str) -> int:
        stmt = select(func.coalesce(func.max(ProjectBlueprintVersionModel.version_number), 0)).where(
            ProjectBlueprintVersionModel.blueprint_id == str(blueprint_id)
        )
        res = await self._session.execute(stmt)
        return int(res.scalar() or 0)


class ProjectChangeRepository(BaseRepository[ProjectChangeRequestModel]):
    """Repository managing formal project change proposals and regeneration outcomes."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectChangeRequestModel)

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectChangeRequestModel]:
        stmt = (
            select(ProjectChangeRequestModel)
            .where(ProjectChangeRequestModel.project_instance_id == str(project_id))
            .order_by(ProjectChangeRequestModel.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, change_id: uuid.UUID | str) -> ProjectChangeRequestModel | None:
        stmt = select(ProjectChangeRequestModel).where(ProjectChangeRequestModel.id == str(change_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: str) -> ProjectChangeRequestModel | None:
        if not idempotency_key:
            return None
        stmt = select(ProjectChangeRequestModel).where(
            ProjectChangeRequestModel.idempotency_key == idempotency_key
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class AIMentorRepository:
    """Repository managing AI Mentor conversation threads and messages."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_conversation(
        self,
        project_id: uuid.UUID | str,
        student_id: uuid.UUID | str,
        title: str = "Project Consultation",
    ) -> AIMentorConversationModel:
        stmt = (
            select(AIMentorConversationModel)
            .where(
                AIMentorConversationModel.project_instance_id == str(project_id),
                AIMentorConversationModel.student_id == str(student_id),
            )
            .order_by(AIMentorConversationModel.created_at.asc())
        )
        res = await self._session.execute(stmt)
        conv = res.scalar_one_or_none()
        if not conv:
            conv = AIMentorConversationModel(
                id=uuid.uuid4(),
                project_instance_id=str(project_id),
                student_id=str(student_id),
                title=title,
            )
            self._session.add(conv)
            await self._session.flush()
        return conv

    async def list_messages(
        self,
        conversation_id: uuid.UUID | str,
        limit: int = 50,
    ) -> list[AIMentorMessageModel]:
        stmt = (
            select(AIMentorMessageModel)
            .where(AIMentorMessageModel.conversation_id == str(conversation_id))
            .order_by(AIMentorMessageModel.created_at.asc())
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def add_message(
        self,
        conversation_id: uuid.UUID | str,
        role: str,
        content: str,
        sources: list[dict[str, Any]] | None = None,
        suggested_action: dict[str, Any] | None = None,
    ) -> AIMentorMessageModel:
        msg = AIMentorMessageModel(
            id=uuid.uuid4(),
            conversation_id=str(conversation_id),
            role=role,
            content=content,
            sources=sources or [],
            suggested_action=suggested_action,
        )
        self._session.add(msg)
        await self._session.flush()
        return msg


class HelpRequestRepository(BaseRepository[ProjectHelpRequestModel]):
    """Repository managing student-initiated help requests."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectHelpRequestModel)

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectHelpRequestModel]:
        stmt = (
            select(ProjectHelpRequestModel)
            .where(ProjectHelpRequestModel.project_instance_id == str(project_id))
            .order_by(ProjectHelpRequestModel.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, request_id: uuid.UUID | str) -> ProjectHelpRequestModel | None:
        stmt = select(ProjectHelpRequestModel).where(ProjectHelpRequestModel.id == str(request_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_mentor_help_requests_detailed(
        self,
        project_ids: Sequence[str | uuid.UUID],
        status: str | None = None,
    ) -> list[tuple[ProjectHelpRequestModel, ProjectInstanceModel, UserModel, GroupModel | None]]:
        if not project_ids:
            return []
        stmt = (
            select(ProjectHelpRequestModel, ProjectInstanceModel, UserModel, GroupModel)
            .join(ProjectInstanceModel, ProjectInstanceModel.id == ProjectHelpRequestModel.project_instance_id)
            .join(UserModel, UserModel.id == ProjectHelpRequestModel.student_id)
            .outerjoin(GroupModel, GroupModel.id == ProjectInstanceModel.group_id)
            .where(ProjectHelpRequestModel.project_instance_id.in_([str(pid) for pid in project_ids]))
        )
        if status:
            stmt = stmt.where(ProjectHelpRequestModel.status == status.upper())
        stmt = stmt.order_by(ProjectHelpRequestModel.created_at.desc())
        res = await self._session.execute(stmt)
        return list(res.all())

    async def get_detailed_by_id(
        self, request_id: uuid.UUID | str
    ) -> tuple[ProjectHelpRequestModel, ProjectInstanceModel, UserModel, GroupModel | None] | None:
        stmt = (
            select(ProjectHelpRequestModel, ProjectInstanceModel, UserModel, GroupModel)
            .join(ProjectInstanceModel, ProjectInstanceModel.id == ProjectHelpRequestModel.project_instance_id)
            .join(UserModel, UserModel.id == ProjectHelpRequestModel.student_id)
            .outerjoin(GroupModel, GroupModel.id == ProjectInstanceModel.group_id)
            .where(ProjectHelpRequestModel.id == str(request_id))
        )
        res = await self._session.execute(stmt)
        return res.first()

    async def update_response(
        self,
        request_id: uuid.UUID | str,
        mentor_response: str,
        status: str = "RESOLVED",
    ) -> ProjectHelpRequestModel | None:
        req = await self.get_by_id(request_id)
        if req:
            now = datetime.now(UTC)
            req.mentor_response = mentor_response.strip()
            req.status = status.upper()
            req.updated_at = now
            if status.upper() == "RESOLVED":
                req.resolved_at = now
            else:
                req.resolved_at = None
            await self._session.flush()
            await self._session.refresh(req)
        return req


class MentorNoteRepository(BaseRepository[ProjectMentorNoteModel]):
    """Repository managing mentor feedback and advisory notes."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=ProjectMentorNoteModel)

    async def list_by_project(self, project_id: uuid.UUID | str) -> list[ProjectMentorNoteModel]:
        stmt = (
            select(ProjectMentorNoteModel)
            .where(ProjectMentorNoteModel.project_instance_id == str(project_id))
            .order_by(ProjectMentorNoteModel.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def list_by_project_detailed(
        self, project_id: uuid.UUID | str
    ) -> list[tuple[ProjectMentorNoteModel, UserModel | None]]:
        stmt = (
            select(ProjectMentorNoteModel, UserModel)
            .outerjoin(UserModel, UserModel.id == ProjectMentorNoteModel.mentor_id)
            .where(ProjectMentorNoteModel.project_instance_id == str(project_id))
            .order_by(ProjectMentorNoteModel.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return list(res.all())

    async def list_by_projects(
        self, project_ids: Sequence[str | uuid.UUID]
    ) -> list[tuple[ProjectMentorNoteModel, ProjectInstanceModel, UserModel | None]]:
        if not project_ids:
            return []
        stmt = (
            select(ProjectMentorNoteModel, ProjectInstanceModel, UserModel)
            .join(ProjectInstanceModel, ProjectInstanceModel.id == ProjectMentorNoteModel.project_instance_id)
            .outerjoin(UserModel, UserModel.id == ProjectMentorNoteModel.mentor_id)
            .where(ProjectMentorNoteModel.project_instance_id.in_([str(pid) for pid in project_ids]))
            .order_by(ProjectMentorNoteModel.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return list(res.all())

    async def get_by_id(self, note_id: uuid.UUID | str) -> ProjectMentorNoteModel | None:
        stmt = select(ProjectMentorNoteModel).where(ProjectMentorNoteModel.id == str(note_id))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def mark_acknowledged(self, note_id: uuid.UUID | str) -> ProjectMentorNoteModel | None:
        note = await self.get_by_id(note_id)
        if note:
            now = datetime.now(UTC)
            note.status = "ACKNOWLEDGED"
            note.updated_at = now
            await self._session.flush()
            await self._session.refresh(note)
        return note
