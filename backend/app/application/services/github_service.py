"""
GrowFlow — GitHub External Integration Service (S27).

Coordinates external observation and monitoring metadata for linked GitHub repositories.
Acts strictly as an observation/read cache model; does NOT act as a canonical git store.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
import uuid

from backend.app.infrastructure.database.models.workspace_extensions import ProjectGitHubIntegrationModel
from backend.app.shared.events.domain_event import DomainEventType, EventVisibility
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)
from backend.app.application.services.authorization_helpers import (
    verify_project_read_access,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import ProjectInstanceModel
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.workspace_extension_repositories import (
        GitHubIntegrationRepository,
    )

logger = get_logger("growflow.application.github_service")


class GitHubService:
    """Service managing external GitHub repository observation."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        github_repo: GitHubIntegrationRepository,
        outbox_service: OutboxService,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._github_repo = github_repo
        self._outbox_service = outbox_service

    async def _verify_project_access(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> ProjectInstanceModel:
        return await verify_project_read_access(
            self._project_repo, self._group_repo, project_id, current_user
        )

    def _verify_can_modify(self, project: ProjectInstanceModel, current_user: CurrentUser) -> None:
        if current_user.is_admin:
            return
        if current_user.is_student and str(project.student_id) == str(current_user.user_id):
            return
        raise AuthorizationException("Only the project owner can modify integrations.", code="AUTH_FORBIDDEN_ACTION")

    async def get_integration(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        integration = await self._github_repo.get_by_project(project.id)
        if not integration:
            return {
                "project_instance_id": str(project.id),
                "repository_name": "",
                "repository_url": "",
                "connection_status": "NOT_CONNECTED",
                "default_branch": "main",
                "commit_count": 0,
                "last_sync_at": None,
                "sync_error": None,
                "cached_commits_preview": [],
            }

        return {
            "id": str(integration.id),
            "project_instance_id": str(integration.project_instance_id),
            "repository_name": integration.repository_name,
            "repository_url": integration.repository_url,
            "connection_status": integration.connection_status,
            "default_branch": integration.default_branch,
            "commit_count": integration.commit_count,
            "last_sync_at": integration.last_sync_at.isoformat() if integration.last_sync_at else None,
            "sync_error": integration.sync_error,
            "cached_commits_preview": integration.cached_commits_preview or [],
        }

    async def connect_repository(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        repository_url: str,
        repository_name: str | None = None,
        default_branch: str = "main",
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        repo_name = repository_name
        if not repo_name:
            clean_url = repository_url.rstrip("/").removesuffix(".git")
            repo_name = clean_url.split("/")[-1] if "/" in clean_url else "repository"

        # Mock initial derived commit observation preview for display
        initial_commits = [
            {
                "sha": "a1b2c3d4e5f67890",
                "message": "Initial project scaffolding & architecture setup",
                "author": current_user.email.split("@")[0],
                "date": datetime.now(UTC).isoformat(),
            },
            {
                "sha": "f7e8d9c0b1a23456",
                "message": "docs: add system design and technical specification",
                "author": current_user.email.split("@")[0],
                "date": datetime.now(UTC).isoformat(),
            },
        ]

        integration = await self._github_repo.upsert(
            project_id=project.id,
            repository_name=repo_name,
            repository_url=repository_url,
            default_branch=default_branch,
            connection_status="CONNECTED",
            commit_count=len(initial_commits),
            cached_commits_preview=initial_commits,
            sync_error=None,
        )

        await self._outbox_service.enqueue(
            event_type=DomainEventType.GITHUB_CONNECTED,
            actor_role=current_user.role,
            resource_type="ProjectGitHubIntegration",
            resource_id=str(integration.id),
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            visibility=EventVisibility.STUDENT.value,
            metadata={"repository_name": repo_name, "repository_url": repository_url},
        )

        return await self.get_integration(project_id, current_user)

    async def sync_repository(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        integration = await self._github_repo.get_by_project(project.id)
        if not integration or integration.connection_status != "CONNECTED":
            raise NotFoundException("No active GitHub connection to sync.", code="GITHUB_NOT_CONNECTED")

        # Refresh commit preview with latest simulated timestamp and count
        commits = integration.cached_commits_preview or []
        new_commit = {
            "sha": uuid.uuid4().hex[:16],
            "message": f"feat: sync updates and verification checkpoint #{len(commits) + 1}",
            "author": current_user.email.split("@")[0],
            "date": datetime.now(UTC).isoformat(),
        }
        updated_commits = [new_commit] + commits[:9]

        updated = await self._github_repo.upsert(
            project_id=project.id,
            repository_name=integration.repository_name,
            repository_url=integration.repository_url,
            default_branch=integration.default_branch,
            connection_status="CONNECTED",
            commit_count=len(updated_commits),
            cached_commits_preview=updated_commits,
            sync_error=None,
        )

        await self._outbox_service.enqueue(
            event_type=DomainEventType.GITHUB_SYNCED,
            actor_role=current_user.role,
            resource_type="ProjectGitHubIntegration",
            resource_id=str(updated.id),
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            visibility=EventVisibility.STUDENT.value,
            metadata={"commit_count": len(updated_commits)},
        )

        return await self.get_integration(project_id, current_user)

    async def disconnect_repository(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        self._verify_can_modify(project, current_user)

        integration = await self._github_repo.get_by_project(project.id)
        if integration:
            await self._github_repo.upsert(
                project_id=project.id,
                repository_name=integration.repository_name,
                repository_url=integration.repository_url,
                default_branch=integration.default_branch,
                connection_status="NOT_CONNECTED",
                commit_count=0,
                cached_commits_preview=[],
                sync_error=None,
            )

        return await self.get_integration(project_id, current_user)
