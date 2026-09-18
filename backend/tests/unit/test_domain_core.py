"""
GrowFlow Gate 05 — Unit Tests for Core Domain Models, Enums, and State Machines.

Tests domain invariants without external dependencies:
- Phase state machine transitions (allowed sequential, backwards, rejected skips/terminals)
- Health states, complexity, and status enumerations
- Group membership & status enumerations
- Project definition immutability & versioning logic
- Domain event envelope structure and outbox records
- Application service logic with repository mocks
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock
import uuid

import pytest

from backend.app.application.services.group_service import GroupService
from backend.app.application.services.outbox_service import OutboxService
from backend.app.application.services.profile_service import ProfileService
from backend.app.application.services.project_definition_service import (
    ProjectDefinitionService,
)
from backend.app.application.services.project_service import ProjectService
from backend.app.domain.identity import (
    AccountStatus,
    CurrentUser,
    TechnologyRelationshipType,
    UserRole,
)
from backend.app.domain.organization.models import (
    GroupMembershipStatus,
    GroupStatus,
)
from backend.app.domain.project.models import (
    CANONICAL_PHASE_ORDER,
    ProjectComplexity,
    ProjectDefinitionStatus,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
    can_transition_phase,
)
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.profile import (
    MentorProfileModel,
    StudentProfileModel,
)
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
    ProjectInstanceModel,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    ConflictException,
    NotFoundException,
)

# ============================================================================
# 1. PHASE STATE MACHINE & ENUM TESTS
# ============================================================================


def test_canonical_phase_order():
    """Verify exact 8 canonical phases in defined sequence."""
    expected = [
        ProjectPhase.IDEA,
        ProjectPhase.ASSESSMENT,
        ProjectPhase.BLUEPRINT,
        ProjectPhase.PLANNING,
        ProjectPhase.IMPLEMENTATION,
        ProjectPhase.TESTING,
        ProjectPhase.DEPLOYMENT,
        ProjectPhase.COMPLETED,
    ]
    assert expected == CANONICAL_PHASE_ORDER
    assert len(CANONICAL_PHASE_ORDER) == 8


def test_valid_forward_phase_transitions():
    """Sequential forward transitions must always be allowed."""
    for i in range(len(CANONICAL_PHASE_ORDER) - 1):
        curr = CANONICAL_PHASE_ORDER[i]
        nxt = CANONICAL_PHASE_ORDER[i + 1]
        assert can_transition_phase(curr, nxt) is True


def test_invalid_forward_phase_skips_rejected():
    """Direct skips over intermediate phases must return False."""
    assert can_transition_phase(ProjectPhase.IDEA, ProjectPhase.IMPLEMENTATION) is False
    assert can_transition_phase(ProjectPhase.ASSESSMENT, ProjectPhase.DEPLOYMENT) is False
    assert can_transition_phase(ProjectPhase.PLANNING, ProjectPhase.COMPLETED) is False


def test_same_phase_transition_rejected():
    """Transitioning to the exact same phase must return False."""
    assert can_transition_phase(ProjectPhase.IMPLEMENTATION, ProjectPhase.IMPLEMENTATION) is False


def test_completed_phase_is_terminal():
    """COMPLETED phase is terminal and cannot transition to any phase."""
    for phase in ProjectPhase:
        assert can_transition_phase(ProjectPhase.COMPLETED, phase) is False


def test_domain_enum_values():
    """Verify all domain enumeration string values match architectural contracts."""
    assert ProjectPhase.IDEA.value == "IDEA"
    assert ProjectPhase.ASSESSMENT.value == "ASSESSMENT"
    assert ProjectPhase.BLUEPRINT.value == "BLUEPRINT"
    assert ProjectPhase.PLANNING.value == "PLANNING"
    assert ProjectPhase.IMPLEMENTATION.value == "IMPLEMENTATION"
    assert ProjectPhase.TESTING.value == "TESTING"
    assert ProjectPhase.DEPLOYMENT.value == "DEPLOYMENT"
    assert ProjectPhase.COMPLETED.value == "COMPLETED"

    assert ProjectHealth.HEALTHY.value == "HEALTHY"
    assert ProjectHealth.WARNING.value == "WARNING"
    assert ProjectHealth.CRITICAL.value == "CRITICAL"

    assert ProjectComplexity.BEGINNER.value == "BEGINNER"
    assert ProjectComplexity.INTERMEDIATE.value == "INTERMEDIATE"
    assert ProjectComplexity.ADVANCED.value == "ADVANCED"

    assert ProjectStatus.DRAFT.value == "DRAFT"
    assert ProjectStatus.ACTIVE.value == "ACTIVE"
    assert ProjectStatus.PAUSED.value == "PAUSED"
    assert ProjectStatus.ARCHIVED.value == "ARCHIVED"
    assert ProjectStatus.COMPLETED.value == "COMPLETED"

    assert GroupStatus.ACTIVE.value == "ACTIVE"
    assert GroupStatus.ARCHIVED.value == "ARCHIVED"

    assert GroupMembershipStatus.ACTIVE.value == "ACTIVE"
    assert GroupMembershipStatus.LEFT.value == "LEFT"
    assert GroupMembershipStatus.REMOVED.value == "REMOVED"

    assert TechnologyRelationshipType.KNOWN.value == "KNOWN"
    assert TechnologyRelationshipType.WORKED_WITH.value == "WORKED_WITH"
    assert TechnologyRelationshipType.INTERESTED_IN.value == "INTERESTED_IN"


# ============================================================================
# 2. DOMAIN EVENT ENUM & MODEL TESTS
# ============================================================================


def test_domain_event_types():
    """Test standard domain event types."""
    assert DomainEventType.PROJECT_CREATED.value == "ProjectCreated"
    assert DomainEventType.PROJECT_PHASE_CHANGED.value == "ProjectPhaseChanged"
    assert DomainEventType.PROJECT_HEALTH_CHANGED.value == "ProjectHealthChanged"
    assert DomainEventType.PROJECT_DEFINITION_CREATED.value == "ProjectDefinitionCreated"
    assert DomainEventType.PROJECT_DEFINITION_ASSIGNED.value == "ProjectDefinitionAssigned"
    assert DomainEventType.GROUP_CREATED.value == "GroupCreated"
    assert DomainEventType.STUDENT_JOINED_GROUP.value == "StudentJoinedGroup"


def test_domain_event_model_creation():
    """Test DomainEventModel instantiation and default status."""
    evt = DomainEventModel(
        event_type=DomainEventType.PROJECT_CREATED.value,
        actor_role="STUDENT",
        resource_type="project_instance",
        resource_id=str(uuid.uuid4()),
        status="PENDING",
        attempt_count=0,
    )
    assert evt.status == "PENDING"
    assert evt.attempt_count == 0


# ============================================================================
# 3. PROFILE SERVICE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_profile_service_student_flow():
    """Test ProfileService get and update for student profile."""
    user_id = uuid.uuid4()
    mock_user = UserModel(
        id=user_id,
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
        full_name="Student Test",
    )

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = mock_user

    profile_repo = AsyncMock()
    profile_repo.get_student_profile.return_value = None
    created_profile = StudentProfileModel(
        user_id=str(user_id),
        student_id="STU-1234",
        bio="Test Bio",
    )
    profile_repo.create_or_update_student_profile.return_value = created_profile

    tech_repo = AsyncMock()
    tech_repo.get_student_technologies.return_value = []

    service = ProfileService(
        profile_repo=profile_repo,
        user_repo=user_repo,
        technology_repo=tech_repo,
    )

    profile, techs = await service.get_or_create_student_profile(user_id)
    assert profile.user_id == str(user_id)
    assert profile.student_id == "STU-1234"
    assert techs == []

    # Update profile
    profile_repo.create_or_update_student_profile.return_value = StudentProfileModel(
        user_id=str(user_id),
        student_id="STU-1234",
        bio="Updated Bio",
        goals="Become a Staff Engineer",
    )
    upd_profile, _ = await service.update_student_profile(
        user_id,
        bio="Updated Bio",
        goals="Become a Staff Engineer",
    )
    assert upd_profile.bio == "Updated Bio"
    assert upd_profile.goals == "Become a Staff Engineer"


@pytest.mark.asyncio
async def test_profile_service_mentor_flow():
    """Test ProfileService get and update for mentor profile."""
    user_id = uuid.uuid4()
    mock_user = UserModel(
        id=user_id,
        email="mentor@example.com",
        role=UserRole.MENTOR.value,
        status=AccountStatus.ACTIVE.value,
        full_name="Mentor Test",
    )

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = mock_user

    profile_repo = AsyncMock()
    profile_repo.get_mentor_profile.return_value = None
    created_profile = MentorProfileModel(
        user_id=str(user_id),
        mentor_id="MEN-1234",
        bio="Senior Architect",
        specialization="Distributed Systems",
    )
    profile_repo.create_or_update_mentor_profile.return_value = created_profile

    tech_repo = AsyncMock()

    service = ProfileService(
        profile_repo=profile_repo,
        user_repo=user_repo,
        technology_repo=tech_repo,
    )

    mentor_profile = await service.get_or_create_mentor_profile(user_id)
    assert mentor_profile.user_id == str(user_id)
    assert mentor_profile.mentor_id == "MEN-1234"


# ============================================================================
# 4. GROUP SERVICE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_group_service_create_and_join():
    """Test GroupService group creation and student join with invite code."""
    mentor_id = uuid.uuid4()
    student_id = uuid.uuid4()

    group_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    created_group = GroupModel(
        id=uuid.uuid4(),
        mentor_id=str(mentor_id),
        name="Cohort 2026",
        join_code="JOIN1234",
        status=GroupStatus.ACTIVE.value,
    )
    group_repo.get_by_join_code.return_value = None
    group_repo.create_group.return_value = created_group

    service = GroupService(group_repo=group_repo, outbox_service=outbox_svc)

    group = await service.create_group(mentor_id=mentor_id, name="Cohort 2026")
    assert group.mentor_id == str(mentor_id)
    assert group.name == "Cohort 2026"
    outbox_svc.emit.assert_called_once()

    # Join group
    group_repo.get_by_join_code.return_value = created_group
    group_repo.get_active_membership_for_student.return_value = None
    membership = GroupMembershipModel(
        group_id=str(created_group.id),
        student_id=str(student_id),
        status=GroupMembershipStatus.ACTIVE.value,
    )
    group_repo.add_membership.return_value = membership

    joined = await service.join_group(student_id=student_id, join_code="JOIN1234")
    assert joined.group_id == str(created_group.id)
    assert joined.student_id == str(student_id)


@pytest.mark.asyncio
async def test_group_service_join_invalid_code():
    """Joining with an unknown join code raises NotFoundException."""
    group_repo = AsyncMock()
    group_repo.get_by_join_code.return_value = None
    service = GroupService(group_repo=group_repo, outbox_service=AsyncMock(spec=OutboxService))

    with pytest.raises(NotFoundException, match="Invalid group join code"):
        await service.join_group(student_id=uuid.uuid4(), join_code="NONEXISTENT")


@pytest.mark.asyncio
async def test_group_service_join_inactive_group():
    """Joining an inactive or archived group raises BusinessRuleException."""
    group_repo = AsyncMock()
    inactive_group = GroupModel(
        id=uuid.uuid4(),
        mentor_id=str(uuid.uuid4()),
        name="Archived Group",
        join_code="INACTIVE1",
        status=GroupStatus.ARCHIVED.value,
    )
    group_repo.get_by_join_code.return_value = inactive_group
    service = GroupService(group_repo=group_repo, outbox_service=AsyncMock(spec=OutboxService))

    with pytest.raises(BusinessRuleException, match="Cannot join an inactive or archived group"):
        await service.join_group(student_id=uuid.uuid4(), join_code="INACTIVE1")


# ============================================================================
# 5. PROJECT DEFINITION SERVICE & IMMUTABILITY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_project_definition_version_immutability():
    """Updating a definition must increment the version and create a new immutable version record."""
    mentor_id = uuid.uuid4()
    mentor_user = CurrentUser(
        user_id=mentor_id,
        email="mentor@example.com",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
        full_name="Mentor Test",
    )

    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    created_def = ProjectDefinitionModel(
        id=uuid.uuid4(),
        owner_mentor_id=str(mentor_id),
        name="E-Commerce Microservices",
        status=ProjectDefinitionStatus.ACTIVE.value,
    )
    created_ver1 = ProjectDefinitionVersionModel(
        id=uuid.uuid4(),
        project_definition_id=str(created_def.id),
        version_number=1,
        name="E-Commerce Microservices",
        problem="Monolith is slow",
        proposed_solution="Split into microservices",
        created_by=str(mentor_id),
    )
    def_repo.create_definition.return_value = created_def
    def_repo.create_version.return_value = created_ver1

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    # 1. Create definition
    definition, version = await service.create_definition(
        mentor_id=mentor_id,
        name="E-Commerce Microservices",
        problem="Monolith is slow",
        proposed_solution="Split into microservices",
    )
    assert definition.id == created_def.id
    assert version.version_number == 1
    def_repo.create_definition.assert_called_once()
    def_repo.create_version.assert_called_once()

    # 2. Update definition -> triggers new version (v2)
    def_repo.get_by_id.return_value = created_def
    def_repo.get_latest_version.return_value = created_ver1

    created_ver2 = ProjectDefinitionVersionModel(
        id=uuid.uuid4(),
        project_definition_id=str(created_def.id),
        version_number=2,
        name="E-Commerce Microservices v2",
        problem="Monolith is slow and hard to scale",
        proposed_solution="Split into event-driven microservices",
        created_by=str(mentor_id),
    )
    def_repo.create_version.return_value = created_ver2

    _, upd_ver = await service.update_definition(
        definition_id=created_def.id,
        current_user=mentor_user,
        name="E-Commerce Microservices v2",
        problem="Monolith is slow and hard to scale",
        proposed_solution="Split into event-driven microservices",
    )
    assert upd_ver.version_number == 2
    assert upd_ver.name == "E-Commerce Microservices v2"
    # Ensure previous version v1 is left intact and create_version was called for v2
    assert def_repo.create_version.call_count == 2


@pytest.mark.asyncio
async def test_project_definition_unauthorized_update():
    """A mentor cannot update another mentor's project definition."""
    owner_mentor_id = uuid.uuid4()
    other_mentor_id = uuid.uuid4()

    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    target_def = ProjectDefinitionModel(
        id=uuid.uuid4(),
        owner_mentor_id=str(owner_mentor_id),
        name="Secret Project",
        status=ProjectDefinitionStatus.ACTIVE.value,
    )
    def_repo.get_by_id.return_value = target_def

    other_user = CurrentUser(
        user_id=other_mentor_id,
        email="intruder@example.com",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
        full_name="Intruder Mentor",
    )

    with pytest.raises(
        AuthorizationException,
        match="Access to this project definition is denied",
    ):
        await service.update_definition(
            definition_id=target_def.id,
            current_user=other_user,
            name="Hacked Title",
        )


@pytest.mark.asyncio
async def test_project_definition_service_list_catalog():
    """Service list_catalog method delegates cleanly to repository list_active_catalog."""
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    mock_catalog_data = [
        (
            ProjectDefinitionModel(
                id=uuid.uuid4(),
                owner_mentor_id=str(uuid.uuid4()),
                name="Catalog Project",
                status=ProjectDefinitionStatus.ACTIVE.value,
            ),
            ProjectDefinitionVersionModel(
                id=uuid.uuid4(),
                version_number=1,
                name="Catalog Project",
                problem="Problem",
                proposed_solution="Solution",
                created_by=str(uuid.uuid4()),
                complexity=ProjectComplexity.INTERMEDIATE.value,
            ),
        )
    ]
    def_repo.list_active_catalog.return_value = mock_catalog_data

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    items = await service.list_catalog()
    assert len(items) == 1
    assert items[0][0].name == "Catalog Project"
    def_repo.list_active_catalog.assert_called_once()


# ============================================================================
# 6. PROJECT SERVICE TESTS & DETERMINISTIC LIFECYCLE
# ============================================================================


@pytest.mark.asyncio
async def test_project_service_create_and_lifecycle():
    """Test ProjectService creation, phase transition, health updates, and outbox emission."""
    student_id = uuid.uuid4()
    student_user = CurrentUser(
        user_id=student_id,
        email="student@example.com",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        full_name="Student Test",
    )

    proj_repo = AsyncMock()
    group_repo = AsyncMock()
    tech_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    created_instance = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(student_id),
        name="AI Travel Planner",
        problem="Planning trips is time consuming",
        proposed_solution="Automated itinerary engine",
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
    )
    proj_repo.create_project_instance.return_value = created_instance

    service = ProjectService(
        project_repo=proj_repo,
        group_repo=group_repo,
        technology_repo=tech_repo,
        outbox_service=outbox_svc,
    )

    # 1. Create project
    instance = await service.create_project(
        student_id=student_id,
        name="AI Travel Planner",
        problem="Planning trips is time consuming",
        proposed_solution="Automated itinerary engine",
    )
    assert instance.student_id == str(student_id)
    assert instance.current_phase == ProjectPhase.IDEA.value
    assert instance.health == ProjectHealth.HEALTHY.value
    outbox_svc.emit.assert_called_once()

    # 2. Transition phase: IDEA -> ASSESSMENT (Valid canonical next step)
    proj_repo.get_by_id.return_value = created_instance
    updated = await service.transition_phase(
        project_id=instance.id,
        current_user=student_user,
        target_phase=ProjectPhase.ASSESSMENT.value,
        reason="Moving from ideation to initial assessment",
    )
    assert updated.current_phase == ProjectPhase.ASSESSMENT.value
    proj_repo.record_phase_transition.assert_called_once()

    # 3. Transition phase: ASSESSMENT -> DEPLOYMENT (Invalid Jump -> BusinessRuleException)
    with pytest.raises(BusinessRuleException, match="Invalid phase transition"):
        await service.transition_phase(
            project_id=instance.id,
            current_user=student_user,
            target_phase=ProjectPhase.DEPLOYMENT.value,
        )

    # 4. Update health: HEALTHY -> WARNING
    health_updated = await service.update_health(
        project_id=instance.id,
        current_user=student_user,
        new_health=ProjectHealth.WARNING.value,
        reason="Blocker on API key acquisition",
    )
    assert health_updated.health == ProjectHealth.WARNING.value
    proj_repo.record_health_transition.assert_called_once()


@pytest.mark.asyncio
async def test_project_cross_user_isolation():
    """A student must NOT be able to view or transition another student's project."""
    student_a_id = uuid.uuid4()
    student_b_id = uuid.uuid4()

    student_b_user = CurrentUser(
        user_id=student_b_id,
        email="student_b@example.com",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
        full_name="Student B",
    )

    proj_repo = AsyncMock()
    group_repo = AsyncMock()
    tech_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectService(
        project_repo=proj_repo,
        group_repo=group_repo,
        technology_repo=tech_repo,
        outbox_service=outbox_svc,
    )

    project_a = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(student_a_id),
        name="Student A's Project",
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
    )
    proj_repo.get_by_id.return_value = project_a

    with pytest.raises(AuthorizationException, match="Access to this project is denied"):
        await service.get_project(project_id=project_a.id, current_user=student_b_user)

    with pytest.raises(AuthorizationException, match="Access to this project is denied"):
        await service.transition_phase(
            project_id=project_a.id,
            current_user=student_b_user,
            target_phase=ProjectPhase.ASSESSMENT.value,
        )


@pytest.mark.asyncio
async def test_project_mentor_cannot_transition_phase():
    """A mentor may view a group project but cannot transition the student's project phase."""
    student_id = uuid.uuid4()
    mentor_id = uuid.uuid4()
    group_id = uuid.uuid4()

    mentor_user = CurrentUser(
        user_id=mentor_id,
        email="mentor@example.com",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
        full_name="Mentor Test",
    )

    proj_repo = AsyncMock()
    group_repo = AsyncMock()
    tech_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    group = GroupModel(
        id=group_id,
        mentor_id=str(mentor_id),
        name="Cohort",
        join_code="CODE1234",
    )
    group_repo.get_by_id.return_value = group

    project = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(student_id),
        group_id=str(group_id),
        name="Student's Project",
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
    )
    proj_repo.get_by_id.return_value = project

    service = ProjectService(
        project_repo=proj_repo,
        group_repo=group_repo,
        technology_repo=tech_repo,
        outbox_service=outbox_svc,
    )

    # Mentor can view the project in their group
    viewed = await service.get_project(project_id=project.id, current_user=mentor_user)
    assert viewed.id == project.id

    # But mentor cannot transition the student's phase
    with pytest.raises(
        AuthorizationException,
        match="Only the project owner may transition the project phase",
    ):
        await service.transition_phase(
            project_id=project.id,
            current_user=mentor_user,
            target_phase=ProjectPhase.ASSESSMENT.value,
        )


# ============================================================================
# 8. S05 MENTOR PROJECT DETAIL & SELECTION UNIT TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_get_catalog_item_success():
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    mentor_id = uuid.uuid4()

    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_id),
        name="Active Definition",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    version = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Active Definition",
        problem="Bottlenecks",
        proposed_solution="Solution",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        description="Desc",
        created_by=str(mentor_id),
    )
    def_repo.get_active_catalog_item.return_value = (definition, version)

    d, v = await service.get_catalog_item(def_id)
    assert d.id == def_id
    assert v.id == ver_id
    def_repo.get_active_catalog_item.assert_awaited_once_with(def_id)


@pytest.mark.asyncio
async def test_get_catalog_item_not_found_or_inactive():
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    def_repo.get_active_catalog_item.return_value = None

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_catalog_item(uuid.uuid4())
    assert exc_info.value.code == "PROJECT_DEFINITION_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_catalog_item_missing_version():
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    def_id = uuid.uuid4()
    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(uuid.uuid4()),
        name="Active Without Version",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=None,
    )
    def_repo.get_active_catalog_item.return_value = (definition, None)

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_catalog_item(def_id)
    assert exc_info.value.code == "PROJECT_DEFINITION_NO_VERSION"


@pytest.mark.asyncio
async def test_select_definition_success_and_version_pinning():
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    student_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    mentor_id = uuid.uuid4()

    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_id),
        name="AI Pipeline",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    version = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="AI Pipeline v1",
        problem="Model training latency",
        proposed_solution="Distributed training",
        complexity=ProjectComplexity.ADVANCED.value,
        description="Build distributed training",
        constraints="GPU required",
        assumptions="PyTorch",
        created_by=str(mentor_id),
    )

    def_repo.get_active_catalog_item.return_value = (definition, version)
    proj_repo.get_active_by_student_and_definition.return_value = None

    async def fake_create_instance(**kwargs):
        return ProjectInstanceModel(
            id=uuid.uuid4(),
            student_id=str(kwargs["student_id"]),
            project_definition_id=str(kwargs["project_definition_id"]),
            source_definition_version_id=str(kwargs["source_definition_version_id"]),
            name=kwargs["name"],
            problem=kwargs["problem"],
            proposed_solution=kwargs["proposed_solution"],
            complexity=kwargs["complexity"],
            current_phase=kwargs["current_phase"],
            health=kwargs["health"],
            progress_percentage=0,
            status=kwargs["status"],
        )

    proj_repo.create_project_instance.side_effect = fake_create_instance

    # Execute selection
    instance = await service.select_definition(
        definition_id=def_id,
        student_id=student_id,
        correlation_id="corr-123",
    )

    # Verify lock on student was acquired
    proj_repo.lock_student_for_update.assert_awaited_once_with(student_id)

    # Verify duplicate active check was performed
    proj_repo.get_active_by_student_and_definition.assert_awaited_once_with(
        student_id=student_id,
        project_definition_id=def_id,
    )

    # Verify instance values
    assert instance.student_id == str(student_id)
    assert instance.project_definition_id == str(def_id)
    assert instance.source_definition_version_id == str(ver_id)
    assert instance.current_phase == ProjectPhase.IDEA.value
    assert instance.health == ProjectHealth.HEALTHY.value
    assert instance.status == ProjectStatus.ACTIVE.value
    assert instance.progress_percentage == 0

    # Verify profile creation called with version snapshot content
    proj_repo.create_or_update_profile.assert_awaited_once_with(
        project_instance_id=instance.id,
        objective="Build distributed training",
        constraints="GPU required",
        assumptions="PyTorch",
        scope="Model training latency",
        expected_outcome="Distributed training",
    )

    # Verify outbox event emitted
    outbox_svc.emit.assert_awaited_once_with(
        event_type=DomainEventType.PROJECT_CREATED.value,
        actor_role="STUDENT",
        resource_type="project_instance",
        resource_id=str(instance.id),
        actor_id=student_id,
        project_instance_id=instance.id,
        metadata={
            "project_name": "AI Pipeline v1",
            "selected_from_definition": True,
            "project_definition_id": str(def_id),
            "version_number": 1,
        },
        correlation_id="corr-123",
    )

    # Definition and version must remain completely unmutated
    assert definition.status == ProjectDefinitionStatus.ACTIVE.value
    assert definition.current_version_id == str(ver_id)
    assert definition.owner_mentor_id == str(mentor_id)


@pytest.mark.asyncio
async def test_select_definition_duplicate_active_rejected():
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    student_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()

    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(uuid.uuid4()),
        name="AI Pipeline",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    version = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="AI Pipeline",
        problem="P",
        proposed_solution="S",
        created_by=str(uuid.uuid4()),
    )

    def_repo.get_active_catalog_item.return_value = (definition, version)

    existing_instance = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(student_id),
        project_definition_id=str(def_id),
        status=ProjectStatus.ACTIVE.value,
    )
    proj_repo.get_active_by_student_and_definition.return_value = existing_instance

    with pytest.raises(ConflictException) as exc_info:
        await service.select_definition(
            definition_id=def_id,
            student_id=student_id,
        )
    assert exc_info.value.code == "PROJECT_ALREADY_SELECTED"

    # Must NOT create a new instance or emit events
    proj_repo.create_project_instance.assert_not_called()
    outbox_svc.emit.assert_not_called()


@pytest.mark.asyncio
async def test_select_definition_version_pinning_remains_intact_when_definition_updates():
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    student_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver1_id = uuid.uuid4()
    ver2_id = uuid.uuid4()
    mentor_id = uuid.uuid4()

    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_id),
        name="Edge Computing",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver1_id),
    )
    version_1 = ProjectDefinitionVersionModel(
        id=ver1_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Edge Computing v1",
        problem="Bandwidth constraints",
        proposed_solution="Local inference",
        created_by=str(mentor_id),
    )

    # Step 1: Student selects version 1
    def_repo.get_active_catalog_item.return_value = (definition, version_1)
    proj_repo.get_active_by_student_and_definition.return_value = None

    async def fake_create_instance(**kwargs):
        return ProjectInstanceModel(
            id=uuid.uuid4(),
            student_id=str(kwargs["student_id"]),
            project_definition_id=str(kwargs["project_definition_id"]),
            source_definition_version_id=str(kwargs["source_definition_version_id"]),
            name=kwargs["name"],
            problem=kwargs["problem"],
            proposed_solution=kwargs["proposed_solution"],
            complexity=kwargs["complexity"],
            current_phase=kwargs["current_phase"],
            health=kwargs["health"],
            progress_percentage=0,
            status=kwargs["status"],
        )

    proj_repo.create_project_instance.side_effect = fake_create_instance

    student_instance = await service.select_definition(
        definition_id=def_id,
        student_id=student_id,
    )
    assert student_instance.source_definition_version_id == str(ver1_id)

    # Step 2: Mentor updates definition to Version 2
    definition.current_version_id = str(ver2_id)
    version_2 = ProjectDefinitionVersionModel(
        id=ver2_id,
        project_definition_id=str(def_id),
        version_number=2,
        name="Edge Computing v2",
        problem="Bandwidth constraints",
        proposed_solution="Local inference with Quantization",
        created_by=str(mentor_id),
    )
    def_repo.get_active_catalog_item.return_value = (definition, version_2)

    # Step 3: Verify the student's instance is STILL pinned to version 1
    assert student_instance.source_definition_version_id == str(ver1_id)
    assert student_instance.source_definition_version_id != str(ver2_id)


@pytest.mark.asyncio
async def test_concurrent_selection_serializes_and_allows_only_one_success():
    """Concurrent repeated selection requests by the same student result in at most one success and one conflict."""
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    student_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()

    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(uuid.uuid4()),
        name="Concurrent Project",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    version = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Concurrent Project v1",
        problem="Problem",
        proposed_solution="Solution",
        created_by=str(uuid.uuid4()),
    )
    def_repo.get_active_catalog_item.return_value = (definition, version)

    # Simulated DB state shared between calls:
    active_instances: dict[str, ProjectInstanceModel] = {}
    lock = asyncio.Lock()

    async def fake_lock(student_id):
        # Row lock serialization on the student
        await lock.acquire()

    async def fake_get_active(student_id, project_definition_id):
        key = f"{student_id}:{project_definition_id}"
        return active_instances.get(key)

    async def fake_create_instance(**kwargs):
        inst = ProjectInstanceModel(
            id=uuid.uuid4(),
            student_id=str(kwargs["student_id"]),
            project_definition_id=str(kwargs["project_definition_id"]),
            source_definition_version_id=str(kwargs["source_definition_version_id"]),
            name=kwargs["name"],
            problem=kwargs["problem"],
            proposed_solution=kwargs["proposed_solution"],
            complexity=kwargs["complexity"],
            current_phase=kwargs["current_phase"],
            health=kwargs["health"],
            progress_percentage=0,
            status=kwargs["status"],
        )
        active_instances[f"{kwargs['student_id']}:{kwargs['project_definition_id']}"] = inst
        return inst

    proj_repo.lock_student_for_update.side_effect = fake_lock
    proj_repo.get_active_by_student_and_definition.side_effect = fake_get_active
    proj_repo.create_project_instance.side_effect = fake_create_instance

    async def select_and_release():
        try:
            return await service.select_definition(
                definition_id=def_id,
                student_id=student_id,
            )
        finally:
            if lock.locked():
                lock.release()

    # Launch two concurrent selection calls
    results = await asyncio.gather(
        select_and_release(),
        select_and_release(),
        return_exceptions=True,
    )

    successes = [r for r in results if isinstance(r, ProjectInstanceModel)]
    conflicts = [r for r in results if isinstance(r, ConflictException)]

    assert len(successes) == 1, "Exactly one selection request must succeed"
    assert len(conflicts) == 1, "Competing selection request must receive ConflictException"
    assert conflicts[0].code == "PROJECT_ALREADY_SELECTED"


@pytest.mark.asyncio
async def test_select_definition_transaction_rollback_on_downstream_failure():
    """If downstream outbox emission or profile persistence fails, exception propagates to trigger rollback."""
    def_repo = AsyncMock()
    proj_repo = AsyncMock()
    outbox_svc = AsyncMock(spec=OutboxService)

    service = ProjectDefinitionService(
        definition_repo=def_repo,
        project_repo=proj_repo,
        outbox_service=outbox_svc,
    )

    student_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()

    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(uuid.uuid4()),
        name="Failure Test",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    version = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Failure Test v1",
        problem="P",
        proposed_solution="S",
        created_by=str(uuid.uuid4()),
    )
    def_repo.get_active_catalog_item.return_value = (definition, version)
    proj_repo.get_active_by_student_and_definition.return_value = None

    proj_repo.create_project_instance.return_value = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(student_id),
        project_definition_id=str(def_id),
        source_definition_version_id=str(ver_id),
        name="Failure Test v1",
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        status=ProjectStatus.ACTIVE.value,
    )

    # Downstream outbox emission fails
    outbox_svc.emit.side_effect = RuntimeError("Outbox commit failure")

    with pytest.raises(RuntimeError, match="Outbox commit failure"):
        await service.select_definition(
            definition_id=def_id,
            student_id=student_id,
        )


