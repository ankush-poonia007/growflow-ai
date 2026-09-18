"""
GrowFlow — FastAPI Application Service Dependencies.

Provides dependency injection providers for domain and application services.

Architecture ref:
  6A § 18 — Dependency injection supplies services and repositories.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from backend.app.api.dependencies.config import SettingsDep  # noqa: TC001
from backend.app.api.dependencies.database import DbSession  # noqa: TC001
from backend.app.application.services.contact_service import ContactService
from backend.app.application.services.group_service import GroupService
from backend.app.application.services.outbox_service import OutboxService
from backend.app.application.services.profile_service import ProfileService
from backend.app.application.services.project_definition_service import (
    ProjectDefinitionService,
)
from backend.app.application.services.project_service import ProjectService
from backend.app.infrastructure.email.client import GmailOAuthEmailClient
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


from backend.app.application.services.notification_service import NotificationService
from backend.app.application.services.search_service import SearchService
from backend.app.infrastructure.repositories.notification_repository import (
    NotificationRepository,
)


def get_notification_service(session: DbSession) -> NotificationService:
    notif_repo = NotificationRepository(session)
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    return NotificationService(notif_repo, proj_repo, grp_repo)


def get_search_service(session: DbSession) -> SearchService:
    return SearchService(session)


def get_outbox_service(session: DbSession) -> OutboxService:
    repo = OutboxRepository(session)
    notif_service = get_notification_service(session)
    return OutboxService(repo, notification_service=notif_service)


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
    group_repo = GroupRepository(session)
    return ProjectDefinitionService(
        def_repo, proj_repo, outbox_service, group_repo=group_repo
    )


from backend.app.application.services.assessment_service import AssessmentService
from backend.app.infrastructure.repositories.assessment_repository import AssessmentRepository
from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository


def get_project_service(session: DbSession) -> ProjectService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    tech_repo = TechnologyRepository(session)
    outbox_service = get_outbox_service(session)
    assessment_repo = AssessmentRepository(session)
    blueprint_repo = BlueprintRepository(session)
    return ProjectService(
        proj_repo,
        grp_repo,
        tech_repo,
        outbox_service,
        assessment_repo=assessment_repo,
        blueprint_repo=blueprint_repo,
    )


def get_contact_service(settings: SettingsDep) -> ContactService:
    email_client = GmailOAuthEmailClient(settings)
    return ContactService(email_client=email_client, settings=settings)


def get_assessment_service(session: DbSession) -> AssessmentService:
    assessment_repo = AssessmentRepository(session)
    project_repo = ProjectRepository(session)
    outbox_service = get_outbox_service(session)
    return AssessmentService(assessment_repo, project_repo, outbox_service)


def get_blueprint_service(session: DbSession) -> BlueprintService:
    from backend.app.infrastructure.database import lifecycle as db_lifecycle

    blueprint_repo = BlueprintRepository(session)
    project_repo = ProjectRepository(session)
    assessment_repo = AssessmentRepository(session)
    project_service = get_project_service(session)
    outbox_service = get_outbox_service(session)
    session_factory = db_lifecycle.get_session_factory()
    return BlueprintService(
        blueprint_repo=blueprint_repo,
        project_repo=project_repo,
        assessment_repo=assessment_repo,
        project_service=project_service,
        outbox_service=outbox_service,
        session_factory=session_factory,
    )


from backend.app.application.services.execution_service import ExecutionService
from backend.app.infrastructure.repositories.execution_repository import (
    DocumentRepository,
    MilestoneRepository,
    RiskRepository,
    TaskRepository,
)


def get_execution_service(session: DbSession) -> ExecutionService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    bp_repo = BlueprintRepository(session)
    milestone_repo = MilestoneRepository(session)
    task_repo = TaskRepository(session)
    risk_repo = RiskRepository(session)
    doc_repo = DocumentRepository(session)
    outbox_service = get_outbox_service(session)
    return ExecutionService(
        project_repo=proj_repo,
        group_repo=grp_repo,
        blueprint_repo=bp_repo,
        milestone_repo=milestone_repo,
        task_repo=task_repo,
        risk_repo=risk_repo,
        document_repo=doc_repo,
        outbox_service=outbox_service,
    )


from backend.app.application.services.activity_service import ActivityService
from backend.app.application.services.ai_mentor_service import AIMentorService
from backend.app.application.services.github_service import GitHubService
from backend.app.application.services.help_request_service import HelpRequestService
from backend.app.application.services.mentor_feedback_service import MentorFeedbackService
from backend.app.application.services.project_change_service import ProjectChangeService
from backend.app.infrastructure.repositories.workspace_extension_repositories import (
    AIMentorRepository,
    BlueprintVersionRepository,
    GitHubIntegrationRepository,
    HelpRequestRepository,
    MentorNoteRepository,
    ProjectChangeRepository,
)


def get_github_service(session: DbSession) -> GitHubService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    gh_repo = GitHubIntegrationRepository(session)
    outbox_service = get_outbox_service(session)
    return GitHubService(proj_repo, grp_repo, gh_repo, outbox_service)


def get_activity_service(session: DbSession) -> ActivityService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    outbox_repo = OutboxRepository(session)
    return ActivityService(proj_repo, grp_repo, outbox_repo)


def get_ai_mentor_service(session: DbSession) -> AIMentorService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    bp_repo = BlueprintRepository(session)
    task_repo = TaskRepository(session)
    milestone_repo = MilestoneRepository(session)
    ai_repo = AIMentorRepository(session)
    help_repo = HelpRequestRepository(session)
    outbox_service = get_outbox_service(session)
    return AIMentorService(
        proj_repo,
        grp_repo,
        bp_repo,
        task_repo,
        milestone_repo,
        ai_repo,
        help_repo,
        outbox_service,
    )


def get_help_request_service(session: DbSession) -> HelpRequestService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    help_repo = HelpRequestRepository(session)
    outbox_service = get_outbox_service(session)
    return HelpRequestService(proj_repo, grp_repo, help_repo, outbox_service)


def get_mentor_feedback_service(session: DbSession) -> MentorFeedbackService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    note_repo = MentorNoteRepository(session)
    outbox_service = get_outbox_service(session)
    return MentorFeedbackService(proj_repo, grp_repo, note_repo, outbox_service)


def get_project_change_service(session: DbSession) -> ProjectChangeService:
    proj_repo = ProjectRepository(session)
    grp_repo = GroupRepository(session)
    bp_repo = BlueprintRepository(session)
    task_repo = TaskRepository(session)
    milestone_repo = MilestoneRepository(session)
    bp_ver_repo = BlueprintVersionRepository(session)
    chg_repo = ProjectChangeRepository(session)
    outbox_service = get_outbox_service(session)
    return ProjectChangeService(
        proj_repo,
        grp_repo,
        bp_repo,
        task_repo,
        milestone_repo,
        bp_ver_repo,
        chg_repo,
        outbox_service,
    )


from backend.app.application.services.mentor_overview_service import MentorOverviewService
from backend.app.application.services.mentor_student_service import MentorStudentService


def get_mentor_overview_service(session: DbSession) -> MentorOverviewService:
    grp_repo = GroupRepository(session)
    proj_repo = ProjectRepository(session)
    return MentorOverviewService(grp_repo, proj_repo)


def get_mentor_student_service(session: DbSession) -> MentorStudentService:
    user_repo = UserRepository(session)
    grp_repo = GroupRepository(session)
    proj_repo = ProjectRepository(session)
    prof_repo = ProfileRepository(session)
    return MentorStudentService(user_repo, grp_repo, proj_repo, prof_repo)


from backend.app.application.services.mentor_ai_service import MentorAIService


def get_mentor_ai_service(session: DbSession) -> MentorAIService:
    grp_repo = GroupRepository(session)
    proj_repo = ProjectRepository(session)
    task_repo = TaskRepository(session)
    milestone_repo = MilestoneRepository(session)
    risk_repo = RiskRepository(session)
    help_repo = HelpRequestRepository(session)
    outbox_service = get_outbox_service(session)
    doc_repo = DocumentRepository(session)
    return MentorAIService(
        group_repo=grp_repo,
        project_repo=proj_repo,
        task_repo=task_repo,
        milestone_repo=milestone_repo,
        risk_repo=risk_repo,
        help_request_repo=help_repo,
        outbox_service=outbox_service,
        document_repo=doc_repo,
    )


# Type aliases for dependency injection
OutboxServiceDep = Annotated[OutboxService, Depends(get_outbox_service)]
ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]
GroupServiceDep = Annotated[GroupService, Depends(get_group_service)]
ProjectDefinitionServiceDep = Annotated[
    ProjectDefinitionService, Depends(get_project_definition_service)
]
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]
AssessmentServiceDep = Annotated[AssessmentService, Depends(get_assessment_service)]
BlueprintServiceDep = Annotated[BlueprintService, Depends(get_blueprint_service)]
ExecutionServiceDep = Annotated[ExecutionService, Depends(get_execution_service)]
GitHubServiceDep = Annotated[GitHubService, Depends(get_github_service)]
ActivityServiceDep = Annotated[ActivityService, Depends(get_activity_service)]
AIMentorServiceDep = Annotated[AIMentorService, Depends(get_ai_mentor_service)]
MentorAIServiceDep = Annotated[MentorAIService, Depends(get_mentor_ai_service)]
HelpRequestServiceDep = Annotated[HelpRequestService, Depends(get_help_request_service)]
MentorFeedbackServiceDep = Annotated[MentorFeedbackService, Depends(get_mentor_feedback_service)]
ProjectChangeServiceDep = Annotated[ProjectChangeService, Depends(get_project_change_service)]
MentorOverviewServiceDep = Annotated[MentorOverviewService, Depends(get_mentor_overview_service)]
MentorStudentServiceDep = Annotated[MentorStudentService, Depends(get_mentor_student_service)]


from backend.app.application.services.admin_service import AdminService
from backend.app.infrastructure.repositories.technology_repository import TechnologyRepository


def get_admin_service(session: DbSession) -> AdminService:
    user_repo = UserRepository(session)
    prof_repo = ProfileRepository(session)
    grp_repo = GroupRepository(session)
    proj_repo = ProjectRepository(session)
    tech_repo = TechnologyRepository(session)
    return AdminService(
        session=session,
        user_repo=user_repo,
        profile_repo=prof_repo,
        group_repo=grp_repo,
        project_repo=proj_repo,
        technology_repo=tech_repo,
    )


AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
