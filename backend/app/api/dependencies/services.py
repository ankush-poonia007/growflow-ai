"""
GrowFlow — FastAPI Application Service Dependencies.

Provides dependency injection providers for domain and application services.

Architecture ref:
  6A § 18 — Dependency injection supplies services and repositories.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from backend.app.api.dependencies.database import DbSession  # noqa: TC001
from backend.app.application.services.group_service import GroupService
from backend.app.application.services.outbox_service import OutboxService
from backend.app.application.services.profile_service import ProfileService
from backend.app.application.services.project_definition_service import (
    ProjectDefinitionService,
)
from backend.app.application.services.project_service import ProjectService
from backend.app.infrastructure.repositories.group_repository import GroupRepository
from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository
from backend.app.infrastructure.repositories.profile_repository import ProfileRepository
from backend.app.infrastructure.repositories.project_definition_repository import (
    ProjectDefinitionRepository,
)
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.technology_repository import (
    TechnologyRepository,
)
from backend.app.infrastructure.repositories.user_repository import UserRepository


def get_outbox_service(session: DbSession) -> OutboxService:
    repo = OutboxRepository(session)
    return OutboxService(repo)


def get_profile_service(session: DbSession) -> ProfileService:
    profile_repo = ProfileRepository(session)
    user_repo = UserRepository(session)
    tech_repo = TechnologyRepository(session)
    return ProfileService(profile_repo, user_repo, tech_repo)


def get_group_service(session: DbSession) -> GroupService:
    group_repo = GroupRepository(session)
    outbox_service = get_outbox_service(session)
    return GroupService(group_repo, outbox_service)


def get_project_definition_service(session: DbSession) -> ProjectDefinitionService:
    def_repo = ProjectDefinitionRepository(session)
    proj_repo = ProjectRepository(session)
    outbox_service = get_outbox_service(session)
    return ProjectDefinitionService(def_repo, proj_repo, outbox_service)


def get_project_service(session: DbSession) -> ProjectService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    tech_repo = TechnologyRepository(session)
    outbox_service = get_outbox_service(session)
    return ProjectService(proj_repo, grp_repo, tech_repo, outbox_service)


# Type aliases for dependency injection
OutboxServiceDep = Annotated[OutboxService, Depends(get_outbox_service)]
ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]
GroupServiceDep = Annotated[GroupService, Depends(get_group_service)]
ProjectDefinitionServiceDep = Annotated[
    ProjectDefinitionService, Depends(get_project_definition_service)
]
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
