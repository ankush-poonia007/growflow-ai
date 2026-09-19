"""
GrowFlow — Database ORM Models Package.

Registers all SQLAlchemy ORM models with Base.metadata.
"""

from backend.app.infrastructure.database.models.assessment import (
    AssessmentAnswerModel,
    AssessmentModel,
    AssessmentQuestionModel,
    AssessmentQuestionTemplateModel,
    AssessmentResultModel,
)
from backend.app.infrastructure.database.models.blueprint import (
    BlueprintJobModel,
    BlueprintModel,
)
from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectMilestoneModel,
    ProjectRiskModel,
    ProjectTaskModel,
)
from backend.app.infrastructure.database.models.notification import (
    NotificationModel,
)
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.profile import (
    MentorProfileModel,
    StudentProfileModel,
    StudentTechnologyModel,
    TechnologyModel,
    UserPreferenceModel,
)
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
    ProjectHealthHistoryModel,
    ProjectInstanceModel,
    ProjectPhaseHistoryModel,
    ProjectProfileModel,
    ProjectTechnologyModel,
)
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

__all__ = [
    "AIMentorConversationModel",
    "AIMentorMessageModel",
    "AssessmentAnswerModel",
    "AssessmentModel",
    "AssessmentQuestionModel",
    "AssessmentQuestionTemplateModel",
    "AssessmentResultModel",
    "BlueprintJobModel",
    "BlueprintModel",
    "DomainEventModel",
    "GroupMembershipModel",
    "GroupModel",
    "MentorProfileModel",
    "NotificationModel",
    "ProjectBlueprintVersionModel",
    "ProjectChangeRequestModel",
    "ProjectDefinitionModel",
    "ProjectDefinitionVersionModel",
    "ProjectDocumentModel",
    "ProjectGitHubIntegrationModel",
    "ProjectHealthHistoryModel",
    "ProjectHelpRequestModel",
    "ProjectInstanceModel",
    "ProjectMentorNoteModel",
    "ProjectMilestoneModel",
    "ProjectPhaseHistoryModel",
    "ProjectProfileModel",
    "ProjectRiskModel",
    "ProjectTaskModel",
    "ProjectTechnologyModel",
    "StudentProfileModel",
    "StudentTechnologyModel",
    "TechnologyModel",
    "UserModel",
    "UserPreferenceModel",
]

