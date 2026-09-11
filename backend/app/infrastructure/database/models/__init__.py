"""
GrowFlow — Database ORM Models Package.

Registers all SQLAlchemy ORM models with Base.metadata.
"""

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

__all__ = [
    "DomainEventModel",
    "GroupMembershipModel",
    "GroupModel",
    "MentorProfileModel",
    "ProjectDefinitionModel",
    "ProjectDefinitionVersionModel",
    "ProjectHealthHistoryModel",
    "ProjectInstanceModel",
    "ProjectPhaseHistoryModel",
    "ProjectProfileModel",
    "ProjectTechnologyModel",
    "StudentProfileModel",
    "StudentTechnologyModel",
    "TechnologyModel",
    "UserModel",
    "UserPreferenceModel",
]
