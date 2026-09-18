"""
GrowFlow — Admin Governance Application Service.

Implements cross-platform query aggregations for:
- AD01: Admin Overview (platform metrics from real canonical data)
- AD02: Mentor Directory
- AD03: Mentor Detail
- AD04: Student Directory
- AD05: Student Detail

Architecture ref:
  Phase 7 Batch 7 Part 1 — Admin Foundation & Core People Governance
  docs/3_Admin_Side_Final_Specification.md § 1-5
  docs/5D_Admin_Application_Architecture_Final.md § 1-3
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from backend.app.api.schemas.admin import (
    AdminAnalyticsDimensionDetailSchema,
    AdminAnalyticsOverviewMetricsSchema,
    AdminAuditEventItemSchema,
    AdminAuditLogResponseSchema,
    AdminAuditSummaryMetricsSchema,
    AdminCohortSummarySchema,
    AdminDocumentItemSchema,
    AdminDocumentsResponseSchema,
    AdminGenerationJobItemSchema,
    AdminGenerationJobsResponseSchema,
    AdminGenerationJobsSummarySchema,
    AdminGroupDetailSchema,
    AdminGroupMemberSchema,
    AdminGroupProjectSchema,
    AdminGroupSummarySchema,
    AdminHealthTransitionSchema,
    AdminInspectableResourceSchema,
    AdminInstanceMonitoringResponseSchema,
    AdminInstanceSummarySchema,
    AdminInvestigationOverviewResponseSchema,
    AdminMentorDetailSchema,
    AdminMentorSummarySchema,
    AdminOverviewResponseSchema,
    AdminPhaseTransitionSchema,
    AdminPlatformAnalyticsResponseSchema,
    AdminProjectDefinitionDetailSchema,
    AdminProjectDefinitionSummarySchema,
    AdminProjectDefinitionVersionSchema,
    AdminProjectInstanceDetailSchema,
    AdminProjectInstanceRefSchema,
    AdminProjectSummarySchema,
    AdminRAGDiagnosticsSchema,
    AdminSecurityOverviewSchema,
    AdminStudentDetailSchema,
    AdminStudentMembershipSchema,
    AdminStudentProjectSchema,
    AdminStudentSummarySchema,
    AdminStudentTechnologySchema,
    AdminSubsystemDetailSchema,
    AdminSubsystemSummarySchema,
    AdminSupervisedStudentSchema,
    AdminSystemHealthMetricsSchema,
    AdminSystemHealthResponseSchema,
    AdminUserSecurityPostureSchema,
    # Batch 10 Schemas
    AdminAIActiveJobSchema,
    AdminAICapabilityUsageSchema,
    AdminAICostDimensionItemSchema,
    AdminAICostDimensionResponseSchema,
    AdminAICostResponseSchema,
    AdminAIExecutionItemSchema,
    AdminAIExecutionsResponseSchema,
    AdminAIExecutionsSummarySchema,
    AdminAIGatewayPostureSchema,
    AdminAIKeySlotSchema,
    AdminAIKeysResponseSchema,
    AdminAIObservatoryKPISchema,
    AdminAIObservatoryResponseSchema,
    AdminAIProjectUsageSchema,
    AdminAIQualityResponseSchema,
    AdminAIQualityScoreDistributionSchema,
    AdminAIQualityTopIssueSchema,
    AdminAIRecentActivitySchema,
    AdminAITimeBucketSchema,
    AdminAITraceDetailResponseSchema,
    AdminAITraceDomainEventSchema,
    AdminAITracePipelineStageSchema,
    AdminAITraceQAFeedbackSchema,
    AdminAIUsageOverallVolumeSchema,
    AdminAIUsageResponseSchema,
)
from backend.app.config.settings import get_settings
from backend.app.domain.blueprint.models import CANONICAL_BLUEPRINT_SECTION_ORDER
from backend.app.domain.identity.models import AccountStatus, UserRole
from backend.app.domain.organization.models import GroupMembershipStatus, GroupStatus
from backend.app.domain.project.models import ProjectHealth, ProjectStatus
from backend.app.infrastructure.database import lifecycle as db_lifecycle
from backend.app.infrastructure.database.models.blueprint import (
    BlueprintJobModel,
    BlueprintModel,
)
from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectTaskModel,
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
)
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
    ProjectHealthHistoryModel,
    ProjectInstanceModel,
    ProjectPhaseHistoryModel,
    ProjectProfileModel,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.database.models.workspace_extensions import (
    AIMentorConversationModel,
    AIMentorMessageModel,
    ProjectBlueprintVersionModel,
    ProjectChangeRequestModel,
    ProjectHelpRequestModel,
)
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
from backend.app.infrastructure.repositories.execution_repository import DocumentRepository
from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository
from backend.app.shared.events.domain_event import OutboxStatus
from backend.app.shared.exceptions import NotFoundException
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.profile_repository import ProfileRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.technology_repository import TechnologyRepository
    from backend.app.infrastructure.repositories.user_repository import UserRepository

logger = get_logger("growflow.application.admin_service")


class AdminService:
    """Service providing authorized platform governance queries for Admin."""

    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        profile_repo: ProfileRepository,
        group_repo: GroupRepository,
        project_repo: ProjectRepository,
        technology_repo: TechnologyRepository,
        outbox_repo: OutboxRepository | None = None,
        document_repo: DocumentRepository | None = None,
        blueprint_repo: BlueprintRepository | None = None,
    ) -> None:
        self._session = session
        self._user_repo = user_repo
        self._profile_repo = profile_repo
        self._group_repo = group_repo
        self._project_repo = project_repo
        self._technology_repo = technology_repo
        self._outbox_repo = outbox_repo or OutboxRepository(session)
        self._document_repo = document_repo or DocumentRepository(session)
        self._blueprint_repo = blueprint_repo or BlueprintRepository(session)

    async def get_overview_metrics(self) -> AdminOverviewResponseSchema:
        """Aggregate truthful platform-wide metrics across users, groups, and projects."""
        # 1. User counts
        stmt_users = select(UserModel.role, UserModel.status, func.count(UserModel.id)).group_by(
            UserModel.role, UserModel.status
        )
        res_users = await self._session.execute(stmt_users)
        user_rows = res_users.all()

        total_mentors = 0
        active_mentors = 0
        total_students = 0
        active_students = 0

        for role, status, count in user_rows:
            if role == UserRole.MENTOR.value:
                total_mentors += count
                if status == AccountStatus.ACTIVE.value:
                    active_mentors += count
            elif role == UserRole.STUDENT.value:
                total_students += count
                if status == AccountStatus.ACTIVE.value:
                    active_students += count

        # 2. Group counts
        stmt_groups = select(GroupModel.status, func.count(GroupModel.id)).group_by(GroupModel.status)
        res_groups = await self._session.execute(stmt_groups)
        group_rows = res_groups.all()

        total_groups = 0
        active_groups = 0
        for status, count in group_rows:
            total_groups += count
            if status == GroupStatus.ACTIVE.value:
                active_groups += count

        # 3. Project counts
        stmt_projs = select(
            ProjectInstanceModel.status,
            ProjectInstanceModel.health,
            func.count(ProjectInstanceModel.id),
        ).group_by(ProjectInstanceModel.status, ProjectInstanceModel.health)
        res_projs = await self._session.execute(stmt_projs)
        proj_rows = res_projs.all()

        total_projects = 0
        active_projects = 0
        completed_projects = 0
        at_risk_projects = 0

        for status, health, count in proj_rows:
            total_projects += count
            if status == ProjectStatus.ACTIVE.value:
                active_projects += count
            elif status == ProjectStatus.COMPLETED.value:
                completed_projects += count

            if health in (ProjectHealth.WARNING.value, ProjectHealth.CRITICAL.value):
                at_risk_projects += count

        return AdminOverviewResponseSchema(
            total_mentors=total_mentors,
            active_mentors=active_mentors,
            total_students=total_students,
            active_students=active_students,
            total_groups=total_groups,
            active_groups=active_groups,
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            at_risk_projects=at_risk_projects,
        )

    async def list_mentors(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
    ) -> list[AdminMentorSummarySchema]:
        """List all platform mentors with joined profile and governance metadata."""
        stmt = (
            select(UserModel, MentorProfileModel)
            .outerjoin(MentorProfileModel, MentorProfileModel.user_id == UserModel.id)
            .where(UserModel.role == UserRole.MENTOR.value)
            .order_by(UserModel.created_at.desc())
        )

        if status:
            stmt = stmt.where(UserModel.status == status)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                func.lower(UserModel.full_name).ilike(term)
                | func.lower(UserModel.email).ilike(term)
                | func.lower(MentorProfileModel.specialization).ilike(term)
                | func.lower(MentorProfileModel.bio).ilike(term)
            )

        res = await self._session.execute(stmt)
        rows = res.all()

        mentor_list: list[AdminMentorSummarySchema] = []
        for user, profile in rows:
            uid = str(user.id)
            # Groups created by mentor
            groups = await self._group_repo.list_by_mentor(uid)
            group_count = len(groups)

            # Count distinct active students across cohorts
            student_ids: set[str] = set()
            project_count = 0
            for g in groups:
                members = await self._group_repo.list_group_members(
                    g.id, status=GroupMembershipStatus.ACTIVE.value
                )
                for m, _ in members:
                    student_ids.add(str(m.student_id))
                projs = await self._project_repo.list_by_group(g.id)
                project_count += len(projs)

            mentor_list.append(
                AdminMentorSummarySchema(
                    id=uid,
                    email=user.email,
                    full_name=user.full_name or user.email,
                    role=user.role,
                    status=user.status,
                    avatar_url=user.avatar_url,
                    mentor_id=profile.mentor_id if profile else None,
                    designation=getattr(profile, "designation", None) if profile else None,
                    organization=getattr(profile, "organization", None) if profile else None,
                    specialization=profile.specialization if profile else None,
                    group_count=group_count,
                    student_count=len(student_ids),
                    project_count=project_count,
                    last_login_at=user.last_login_at,
                    created_at=user.created_at,
                )
            )

        return mentor_list

    async def get_mentor_detail(self, mentor_id: uuid.UUID | str) -> AdminMentorDetailSchema:
        """Fetch full mentor detail view including cohorts, supervised students, and projects."""
        mid_str = str(mentor_id)
        stmt = (
            select(UserModel, MentorProfileModel)
            .outerjoin(MentorProfileModel, MentorProfileModel.user_id == UserModel.id)
            .where(UserModel.id == mid_str, UserModel.role == UserRole.MENTOR.value)
        )
        res = await self._session.execute(stmt)
        row = res.first()

        if not row:
            raise NotFoundException(message="Mentor not found.", code="MENTOR_NOT_FOUND")

        user, profile = row

        # Fetch cohorts
        groups = await self._group_repo.list_by_mentor(mid_str)
        cohorts_summary: list[AdminCohortSummarySchema] = []
        students_map: dict[str, AdminSupervisedStudentSchema] = {}

        for g in groups:
            members = await self._group_repo.list_group_members(
                g.id, status=GroupMembershipStatus.ACTIVE.value
            )
            projs = await self._project_repo.list_by_group(g.id)

            cohorts_summary.append(
                AdminCohortSummarySchema(
                    id=str(g.id),
                    name=g.name,
                    join_code=g.join_code,
                    status=g.status,
                    student_count=len(members),
                    project_count=len(projs),
                    created_at=g.created_at,
                )
            )

            for m, student_user in members:
                sid = str(student_user.id)
                if sid not in students_map:
                    # Count student's active projects in this group
                    student_projs = [p for p in projs if str(p.student_id) == sid]
                    students_map[sid] = AdminSupervisedStudentSchema(
                        id=sid,
                        full_name=student_user.full_name or student_user.email,
                        email=student_user.email,
                        group_name=g.name,
                        active_projects_count=len(student_projs),
                    )

        # Parse skills if available
        skills_list: list[str] = []
        raw_skills = getattr(profile, "skills", None) if profile else None
        if raw_skills:
            if isinstance(raw_skills, list):
                skills_list = [str(s) for s in raw_skills]
            elif isinstance(raw_skills, str):
                skills_list = [s.strip() for s in raw_skills.split(",") if s.strip()]
        elif profile and profile.specialization:
            skills_list = [s.strip() for s in profile.specialization.split(",") if s.strip()]

        return AdminMentorDetailSchema(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name or user.email,
            role=user.role,
            status=user.status,
            avatar_url=user.avatar_url,
            mentor_id=profile.mentor_id if profile else None,
            designation=getattr(profile, "designation", None) if profile else None,
            organization=getattr(profile, "organization", None) if profile else None,
            bio=profile.bio if profile else None,
            specialization=profile.specialization if profile else None,
            skills=skills_list,
            max_students=getattr(profile, "max_students", None) if profile else None,
            is_accepting_students=getattr(profile, "is_accepting_students", True) if profile else True,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            groups=cohorts_summary,
            supervised_students=list(students_map.values()),
        )

    async def list_students(
        self,
        *,
        search: str | None = None,
        track: str | None = None,
        status: str | None = None,
    ) -> list[AdminStudentSummarySchema]:
        """List all platform students with profile details and project governance counts."""
        stmt = (
            select(UserModel, StudentProfileModel)
            .outerjoin(StudentProfileModel, StudentProfileModel.user_id == UserModel.id)
            .where(UserModel.role == UserRole.STUDENT.value)
            .order_by(UserModel.created_at.desc())
        )

        if status:
            stmt = stmt.where(UserModel.status == status)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                func.lower(UserModel.full_name).ilike(term)
                | func.lower(UserModel.email).ilike(term)
                | func.lower(StudentProfileModel.bio).ilike(term)
                | func.lower(StudentProfileModel.goals).ilike(term)
                | func.lower(StudentProfileModel.interests).ilike(term)
            )

        res = await self._session.execute(stmt)
        rows = res.all()

        student_list: list[AdminStudentSummarySchema] = []
        for user, profile in rows:
            uid = str(user.id)

            # Get group memberships
            memberships = await self._group_repo.list_student_memberships(
                uid, status=GroupMembershipStatus.ACTIVE.value
            )

            # Get projects
            projs = await self._project_repo.list_by_student(uid)
            active_count = sum(1 for p in projs if p.status == ProjectStatus.ACTIVE.value)
            at_risk_count = sum(
                1
                for p in projs
                if p.health in (ProjectHealth.WARNING.value, ProjectHealth.CRITICAL.value)
            )

            primary_track = getattr(profile, "primary_track", None) if profile else None
            if not primary_track and projs:
                primary_track = getattr(projs[0], "complexity", None)

            if track and track.strip():
                if not primary_track or track.strip().lower() not in primary_track.lower():
                    continue

            student_list.append(
                AdminStudentSummarySchema(
                    id=uid,
                    email=user.email,
                    full_name=user.full_name or user.email,
                    role=user.role,
                    status=user.status,
                    avatar_url=user.avatar_url,
                    student_id=profile.student_id if profile else None,
                    college=getattr(profile, "college", None) if profile else None,
                    branch=getattr(profile, "branch", None) if profile else None,
                    year_of_study=getattr(profile, "year_of_study", None) if profile else None,
                    primary_track=primary_track,
                    group_count=len(memberships),
                    project_count=len(projs),
                    active_project_count=active_count,
                    at_risk_project_count=at_risk_count,
                    last_login_at=user.last_login_at,
                    created_at=user.created_at,
                )
            )

        return student_list

    async def get_student_detail(self, student_id: uuid.UUID | str) -> AdminStudentDetailSchema:
        """Fetch full student detail view including profile, skills, cohorts, and project instances."""
        sid_str = str(student_id)
        stmt = (
            select(UserModel, StudentProfileModel)
            .outerjoin(StudentProfileModel, StudentProfileModel.user_id == UserModel.id)
            .where(UserModel.id == sid_str, UserModel.role == UserRole.STUDENT.value)
        )
        res = await self._session.execute(stmt)
        row = res.first()

        if not row:
            raise NotFoundException(message="Student not found.", code="STUDENT_NOT_FOUND")

        user, profile = row

        # 1. Fetch technologies / skills
        tech_stmt = (
            select(StudentTechnologyModel, TechnologyModel)
            .join(TechnologyModel, TechnologyModel.id == StudentTechnologyModel.technology_id)
            .where(StudentTechnologyModel.student_id == sid_str)
        )
        tech_res = await self._session.execute(tech_stmt)
        tech_rows = tech_res.all()

        technologies_list = [
            AdminStudentTechnologySchema(
                technology_id=str(t.id),
                technology_name=t.name,
                proficiency_level=st.proficiency,
            )
            for st, t in tech_rows
        ]

        # 2. Fetch cohort memberships with mentors
        groups_with_mentors = await self._group_repo.list_groups_with_mentors_for_student(sid_str)
        groups_list = [
            AdminStudentMembershipSchema(
                group_id=str(g.id),
                group_name=g.name,
                mentor_name=m.full_name or m.email,
                status=g.status,
                joined_at=g.created_at,
            )
            for g, m in groups_with_mentors
        ]

        # 3. Fetch project instances
        projs = await self._project_repo.list_by_student(sid_str)
        # Map group names
        group_id_to_name = {str(g.id): g.name for g, _ in groups_with_mentors}

        projects_list = [
            AdminStudentProjectSchema(
                id=str(p.id),
                name=p.name,
                track=getattr(p, "track", None) or getattr(p, "complexity", None) or "General",
                current_phase=p.current_phase,
                health=p.health,
                progress_percentage=p.progress_percentage,
                status=p.status,
                group_name=group_id_to_name.get(str(p.group_id)) if p.group_id else None,
                created_at=p.created_at,
            )
            for p in projs
        ]

        headline = getattr(profile, "headline", None) if profile else None
        if not headline and profile and profile.goals:
            headline = profile.goals

        target_role = getattr(profile, "target_role", None) if profile else None
        if not target_role and profile and profile.interests:
            target_role = profile.interests

        primary_track = getattr(profile, "primary_track", None) if profile else None
        if not primary_track and projs:
            primary_track = getattr(projs[0], "complexity", None)

        return AdminStudentDetailSchema(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name or user.email,
            role=user.role,
            status=user.status,
            avatar_url=user.avatar_url,
            student_id=profile.student_id if profile else None,
            enrollment_number=getattr(profile, "enrollment_number", None) if profile else None,
            college=getattr(profile, "college", None) if profile else None,
            branch=getattr(profile, "branch", None) if profile else None,
            year_of_study=getattr(profile, "year_of_study", None) if profile else None,
            cgpa=float(profile.cgpa) if (profile and getattr(profile, "cgpa", None) is not None) else None,
            primary_track=primary_track,
            headline=headline,
            bio=profile.bio if profile else None,
            target_role=target_role,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            technologies=technologies_list,
            groups=groups_list,
            projects=projects_list,
        )

    # ============================================================
    # AD06 — Groups Directory
    # ============================================================

    async def list_groups(
        self,
        search: str | None = None,
        status: str | None = None,
    ) -> list[AdminGroupSummarySchema]:
        """List platform cohorts/groups with supervising mentor and enrolled counts."""
        stmt = (
            select(
                GroupModel,
                UserModel.full_name.label("mentor_name"),
                UserModel.email.label("mentor_email"),
            )
            .join(UserModel, UserModel.id == GroupModel.mentor_id)
        )
        if status and status.upper() != "ALL":
            stmt = stmt.where(GroupModel.status == status.upper())
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                GroupModel.name.ilike(term)
                | GroupModel.join_code.ilike(term)
                | UserModel.full_name.ilike(term)
                | UserModel.email.ilike(term)
            )
        stmt = stmt.order_by(GroupModel.created_at.desc())
        result = await self._session.execute(stmt)
        rows = result.all()

        # Aggregate student member counts per group
        stmt_members = (
            select(
                GroupMembershipModel.group_id,
                func.count(GroupMembershipModel.id),
            )
            .where(GroupMembershipModel.status == GroupMembershipStatus.ACTIVE.value)
            .group_by(GroupMembershipModel.group_id)
        )
        res_members = await self._session.execute(stmt_members)
        member_counts = dict(res_members.all())

        # Aggregate project instance counts per group
        stmt_projects = (
            select(
                ProjectInstanceModel.group_id,
                func.count(ProjectInstanceModel.id),
            )
            .where(ProjectInstanceModel.group_id.isnot(None))
            .group_by(ProjectInstanceModel.group_id)
        )
        res_projects = await self._session.execute(stmt_projects)
        project_counts = dict(res_projects.all())

        groups = []
        for group, mentor_name, mentor_email in rows:
            gid = str(group.id)
            groups.append(
                AdminGroupSummarySchema(
                    id=gid,
                    name=group.name,
                    join_code=group.join_code,
                    status=group.status,
                    mentor_id=str(group.mentor_id),
                    mentor_name=mentor_name or mentor_email,
                    mentor_email=mentor_email,
                    student_count=member_counts.get(gid, 0),
                    project_count=project_counts.get(gid, 0),
                    created_at=group.created_at,
                    updated_at=group.updated_at,
                )
            )
        return groups

    # ============================================================
    # AD07 — Group Detail
    # ============================================================

    async def get_group_detail(self, group_id: uuid.UUID | str) -> AdminGroupDetailSchema:
        """Retrieve detailed governance view for a single cohort/group."""
        stmt = (
            select(GroupModel, UserModel)
            .join(UserModel, UserModel.id == GroupModel.mentor_id)
            .where(GroupModel.id == str(group_id))
        )
        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            raise NotFoundException(f"Group {group_id} not found.")
        group, mentor = row

        # Fetch mentor profile for specialization
        stmt_prof = select(MentorProfileModel).where(MentorProfileModel.user_id == str(mentor.id))
        prof_res = await self._session.execute(stmt_prof)
        mentor_prof = prof_res.scalar_one_or_none()

        # Enrolled student members
        stmt_members = (
            select(GroupMembershipModel, UserModel)
            .join(UserModel, UserModel.id == GroupMembershipModel.student_id)
            .where(GroupMembershipModel.group_id == str(group_id))
            .order_by(GroupMembershipModel.joined_at.desc())
        )
        members_res = await self._session.execute(stmt_members)
        members = [
            AdminGroupMemberSchema(
                id=str(mship.id),
                student_id=str(stu.id),
                full_name=stu.full_name or stu.email,
                email=stu.email,
                avatar_url=stu.avatar_url,
                status=mship.status,
                joined_at=mship.joined_at,
            )
            for mship, stu in members_res.all()
        ]

        # Associated project instances
        stmt_projs = (
            select(ProjectInstanceModel, UserModel)
            .join(UserModel, UserModel.id == ProjectInstanceModel.student_id)
            .where(ProjectInstanceModel.group_id == str(group_id))
            .order_by(ProjectInstanceModel.created_at.desc())
        )
        projs_res = await self._session.execute(stmt_projs)
        projects = []
        active_count = 0
        for proj, stu in projs_res.all():
            if proj.status == ProjectStatus.ACTIVE.value:
                active_count += 1
            projects.append(
                AdminGroupProjectSchema(
                    id=str(proj.id),
                    name=proj.name,
                    student_id=str(stu.id),
                    student_name=stu.full_name or stu.email,
                    current_phase=proj.current_phase,
                    health=proj.health,
                    progress_percentage=proj.progress_percentage,
                    status=proj.status,
                    created_at=proj.created_at,
                )
            )

        return AdminGroupDetailSchema(
            id=str(group.id),
            name=group.name,
            join_code=group.join_code,
            status=group.status,
            created_at=group.created_at,
            updated_at=group.updated_at,
            mentor_id=str(mentor.id),
            mentor_name=mentor.full_name or mentor.email,
            mentor_email=mentor.email,
            mentor_avatar_url=mentor.avatar_url,
            mentor_specialization=mentor_prof.specialization if mentor_prof else None,
            student_count=len(members),
            project_count=len(projects),
            active_project_count=active_count,
            members=members,
            projects=projects,
        )

    # ============================================================
    # AD08 & AD10 — Projects Directory & Monitoring List
    # ============================================================

    async def list_projects(
        self,
        search: str | None = None,
        phase: str | None = None,
        health: str | None = None,
        status: str | None = None,
    ) -> list[AdminProjectSummarySchema]:
        """List platform project instances with student, mentor, cohort, and definition metadata."""
        MentorUser = aliased(UserModel, name="mentor_user")
        StudentUser = aliased(UserModel, name="student_user")

        stmt = (
            select(
                ProjectInstanceModel,
                StudentUser,
                GroupModel,
                MentorUser,
                ProjectDefinitionModel,
            )
            .join(StudentUser, StudentUser.id == ProjectInstanceModel.student_id)
            .outerjoin(GroupModel, GroupModel.id == ProjectInstanceModel.group_id)
            .outerjoin(MentorUser, MentorUser.id == GroupModel.mentor_id)
            .outerjoin(
                ProjectDefinitionModel,
                ProjectDefinitionModel.id == ProjectInstanceModel.project_definition_id,
            )
        )

        if phase and phase.upper() != "ALL":
            stmt = stmt.where(ProjectInstanceModel.current_phase == phase.upper())
        if health and health.upper() != "ALL":
            stmt = stmt.where(ProjectInstanceModel.health == health.upper())
        if status and status.upper() != "ALL":
            stmt = stmt.where(ProjectInstanceModel.status == status.upper())
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                ProjectInstanceModel.name.ilike(term)
                | StudentUser.full_name.ilike(term)
                | StudentUser.email.ilike(term)
                | MentorUser.full_name.ilike(term)
                | GroupModel.name.ilike(term)
            )

        stmt = stmt.order_by(ProjectInstanceModel.updated_at.desc())
        result = await self._session.execute(stmt)

        projects = []
        for proj, student, group, mentor, defn in result.all():
            projects.append(
                AdminProjectSummarySchema(
                    id=str(proj.id),
                    name=proj.name,
                    student_id=str(student.id),
                    student_name=student.full_name or student.email,
                    student_email=student.email,
                    mentor_id=str(mentor.id) if mentor else None,
                    mentor_name=mentor.full_name if mentor else None,
                    group_id=str(group.id) if group else None,
                    group_name=group.name if group else None,
                    current_phase=proj.current_phase,
                    health=proj.health,
                    progress_percentage=proj.progress_percentage,
                    status=proj.status,
                    complexity=getattr(proj, "complexity", "INTERMEDIATE") or "INTERMEDIATE",
                    source_definition_name=defn.name if defn else None,
                    created_at=proj.created_at,
                    updated_at=proj.updated_at,
                )
            )
        return projects

    # ============================================================
    # AD09 — Project Definition Monitoring
    # ============================================================

    async def list_definitions(
        self,
        search: str | None = None,
        status: str | None = None,
    ) -> list[AdminProjectDefinitionSummarySchema]:
        """List mentor-created project definitions with versioning and adoption metrics."""
        stmt = (
            select(
                ProjectDefinitionModel,
                UserModel,
                ProjectDefinitionVersionModel,
            )
            .join(UserModel, UserModel.id == ProjectDefinitionModel.owner_mentor_id)
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionVersionModel.id == ProjectDefinitionModel.current_version_id,
            )
        )

        if status and status.upper() != "ALL":
            stmt = stmt.where(ProjectDefinitionModel.status == status.upper())
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                ProjectDefinitionModel.name.ilike(term)
                | UserModel.full_name.ilike(term)
                | UserModel.email.ilike(term)
            )

        stmt = stmt.order_by(ProjectDefinitionModel.created_at.desc())
        result = await self._session.execute(stmt)
        rows = result.all()

        # Instance adoption counts per definition
        stmt_inst = (
            select(
                ProjectInstanceModel.project_definition_id,
                func.count(ProjectInstanceModel.id),
            )
            .where(ProjectInstanceModel.project_definition_id.isnot(None))
            .group_by(ProjectInstanceModel.project_definition_id)
        )
        res_inst = await self._session.execute(stmt_inst)
        instance_counts = dict(res_inst.all())

        # Version counts per definition
        stmt_vers = (
            select(
                ProjectDefinitionVersionModel.project_definition_id,
                func.count(ProjectDefinitionVersionModel.id),
            )
            .group_by(ProjectDefinitionVersionModel.project_definition_id)
        )
        res_vers = await self._session.execute(stmt_vers)
        version_counts = dict(res_vers.all())

        definitions = []
        for defn, mentor, cur_ver in rows:
            did = str(defn.id)
            definitions.append(
                AdminProjectDefinitionSummarySchema(
                    id=did,
                    name=defn.name,
                    owner_mentor_id=str(mentor.id),
                    owner_mentor_name=mentor.full_name or mentor.email,
                    owner_mentor_email=mentor.email,
                    status=defn.status,
                    current_version_id=str(cur_ver.id) if cur_ver else None,
                    current_version_number=cur_ver.version_number if cur_ver else None,
                    complexity=cur_ver.complexity if cur_ver else None,
                    instance_count=instance_counts.get(did, 0),
                    version_count=version_counts.get(did, 0),
                    created_at=defn.created_at,
                    updated_at=defn.updated_at,
                )
            )
        return definitions

    async def get_definition_detail(
        self, definition_id: uuid.UUID | str
    ) -> AdminProjectDefinitionDetailSchema:
        """Retrieve detailed definition governance view including immutable version tree and adoptions."""
        stmt = (
            select(
                ProjectDefinitionModel,
                UserModel,
                ProjectDefinitionVersionModel,
            )
            .join(UserModel, UserModel.id == ProjectDefinitionModel.owner_mentor_id)
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionVersionModel.id == ProjectDefinitionModel.current_version_id,
            )
            .where(ProjectDefinitionModel.id == str(definition_id))
        )
        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            raise NotFoundException(f"Project definition {definition_id} not found.")
        defn, mentor, cur_ver = row

        # Fetch immutable versions
        stmt_versions = (
            select(ProjectDefinitionVersionModel)
            .where(ProjectDefinitionVersionModel.project_definition_id == str(definition_id))
            .order_by(ProjectDefinitionVersionModel.version_number.desc())
        )
        v_res = await self._session.execute(stmt_versions)
        versions = [
            AdminProjectDefinitionVersionSchema(
                id=str(v.id),
                version_number=v.version_number,
                name=v.name,
                problem=v.problem or "",
                proposed_solution=v.proposed_solution or "",
                complexity=v.complexity,
                description=v.description or "",
                duration=v.duration or "",
                constraints=v.constraints or "",
                assumptions=v.assumptions or "",
                technology_snapshot=v.technology_snapshot or [],
                created_by=str(v.created_by),
                created_at=v.created_at,
            )
            for v in v_res.scalars().all()
        ]

        # Fetch adopted student instances
        stmt_inst = (
            select(ProjectInstanceModel, UserModel)
            .join(UserModel, UserModel.id == ProjectInstanceModel.student_id)
            .where(ProjectInstanceModel.project_definition_id == str(definition_id))
            .order_by(ProjectInstanceModel.created_at.desc())
        )
        inst_res = await self._session.execute(stmt_inst)
        assigned_instances = [
            AdminProjectInstanceRefSchema(
                id=str(p.id),
                name=p.name,
                student_name=s.full_name or s.email,
                current_phase=p.current_phase,
                health=p.health,
                status=p.status,
            )
            for p, s in inst_res.all()
        ]

        did = str(defn.id)
        return AdminProjectDefinitionDetailSchema(
            id=did,
            name=defn.name,
            owner_mentor_id=str(mentor.id),
            owner_mentor_name=mentor.full_name or mentor.email,
            owner_mentor_email=mentor.email,
            status=defn.status,
            current_version_id=str(cur_ver.id) if cur_ver else None,
            current_version_number=cur_ver.version_number if cur_ver else None,
            complexity=cur_ver.complexity if cur_ver else None,
            instance_count=len(assigned_instances),
            version_count=len(versions),
            created_at=defn.created_at,
            updated_at=defn.updated_at,
            versions=versions,
            assigned_instances=assigned_instances,
        )

    # ============================================================
    # AD10 — Project Instance Monitoring & Canonical Detail
    # ============================================================

    async def get_instances_monitoring(
        self,
        search: str | None = None,
        phase: str | None = None,
        health: str | None = None,
        status: str | None = None,
    ) -> AdminInstanceMonitoringResponseSchema:
        """Retrieve operational monitoring breakdown across all project instances."""
        instances = await self.list_projects(search=search, phase=phase, health=health, status=status)

        # Aggregate summary KPIs across all instances
        stmt_counts = select(
            ProjectInstanceModel.health,
            ProjectInstanceModel.status,
            func.count(ProjectInstanceModel.id),
        ).group_by(ProjectInstanceModel.health, ProjectInstanceModel.status)
        res_counts = await self._session.execute(stmt_counts)

        total_instances = 0
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        completed_count = 0

        for h, s, c in res_counts.all():
            total_instances += c
            if h == ProjectHealth.HEALTHY.value:
                healthy_count += c
            elif h == ProjectHealth.WARNING.value:
                warning_count += c
            elif h == ProjectHealth.CRITICAL.value:
                critical_count += c

            if s == ProjectStatus.COMPLETED.value:
                completed_count += c

        summary = AdminInstanceSummarySchema(
            total_instances=total_instances,
            healthy_count=healthy_count,
            warning_count=warning_count,
            critical_count=critical_count,
            completed_count=completed_count,
        )

        return AdminInstanceMonitoringResponseSchema(
            summary=summary,
            instances=instances,
        )

    async def get_instance_detail(
        self, project_id: uuid.UUID | str
    ) -> AdminProjectInstanceDetailSchema:
        """Retrieve canonical governance inspection detail for a student project instance."""
        MentorUser = aliased(UserModel, name="mentor_user")
        StudentUser = aliased(UserModel, name="student_user")

        stmt = (
            select(
                ProjectInstanceModel,
                StudentUser,
                GroupModel,
                MentorUser,
                ProjectDefinitionModel,
                ProjectDefinitionVersionModel,
            )
            .join(StudentUser, StudentUser.id == ProjectInstanceModel.student_id)
            .outerjoin(GroupModel, GroupModel.id == ProjectInstanceModel.group_id)
            .outerjoin(MentorUser, MentorUser.id == GroupModel.mentor_id)
            .outerjoin(
                ProjectDefinitionModel,
                ProjectDefinitionModel.id == ProjectInstanceModel.project_definition_id,
            )
            .outerjoin(
                ProjectDefinitionVersionModel,
                ProjectDefinitionVersionModel.id == ProjectInstanceModel.source_definition_version_id,
            )
            .where(ProjectInstanceModel.id == str(project_id))
        )
        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            raise NotFoundException(f"Project instance {project_id} not found.")

        proj, student, group, mentor, defn, version = row

        # Fetch profile metadata
        stmt_prof = select(ProjectProfileModel).where(
            ProjectProfileModel.project_instance_id == str(project_id)
        )
        prof_res = await self._session.execute(stmt_prof)
        profile = prof_res.scalar_one_or_none()

        # Fetch phase transition history
        stmt_phase = (
            select(ProjectPhaseHistoryModel)
            .where(ProjectPhaseHistoryModel.project_instance_id == str(project_id))
            .order_by(ProjectPhaseHistoryModel.changed_at.desc())
        )
        phase_res = await self._session.execute(stmt_phase)
        phase_history = [
            AdminPhaseTransitionSchema(
                id=str(h.id),
                previous_phase=h.previous_phase,
                new_phase=h.new_phase,
                reason=h.reason or "",
                changed_at=h.changed_at,
            )
            for h in phase_res.scalars().all()
        ]

        # Fetch health transition history
        stmt_health = (
            select(ProjectHealthHistoryModel)
            .where(ProjectHealthHistoryModel.project_instance_id == str(project_id))
            .order_by(ProjectHealthHistoryModel.changed_at.desc())
        )
        health_res = await self._session.execute(stmt_health)
        health_history = [
            AdminHealthTransitionSchema(
                id=str(h.id),
                previous_health=h.previous_health,
                new_health=h.new_health,
                reason=h.reason or "",
                changed_at=h.changed_at,
            )
            for h in health_res.scalars().all()
        ]

        return AdminProjectInstanceDetailSchema(
            id=str(proj.id),
            name=proj.name,
            problem=proj.problem or "",
            proposed_solution=proj.proposed_solution or "",
            complexity=getattr(proj, "complexity", "INTERMEDIATE") or "INTERMEDIATE",
            current_phase=proj.current_phase,
            health=proj.health,
            progress_percentage=proj.progress_percentage,
            status=proj.status,
            deadline=proj.deadline,
            started_at=proj.started_at,
            completed_at=proj.completed_at,
            created_at=proj.created_at,
            updated_at=proj.updated_at,
            student_id=str(student.id),
            student_name=student.full_name or student.email,
            student_email=student.email,
            student_avatar_url=student.avatar_url,
            mentor_id=str(mentor.id) if mentor else None,
            mentor_name=mentor.full_name if mentor else None,
            mentor_email=mentor.email if mentor else None,
            group_id=str(group.id) if group else None,
            group_name=group.name if group else None,
            definition_id=str(defn.id) if defn else None,
            definition_name=defn.name if defn else None,
            version_number=version.version_number if version else None,
            profile_objective=profile.objective if profile else None,
            profile_target_users=profile.target_users if profile else None,
            profile_project_type=profile.project_type if profile else None,
            profile_student_skill_context=profile.student_skill_context if profile else None,
            profile_goals=profile.goals if profile else None,
            profile_scope=profile.scope if profile else None,
            profile_expected_outcome=profile.expected_outcome if profile else None,
            profile_constraints=profile.constraints if profile else None,
            profile_assumptions=profile.assumptions if profile else None,
            phase_history=phase_history,
            health_history=health_history,
        )

    # ============================================================
    # Batch 8 Helper Utilities
    # ============================================================

    def _format_event_description(self, event_type: str, metadata: dict[str, Any], actor_role: str) -> tuple[str, str]:
        """Produce human-readable title and summary from canonical domain event."""
        type_titles: dict[str, tuple[str, str]] = {
            "ProjectCreated": ("Project Created", "Project workspace initialized."),
            "ProjectPhaseChanged": ("Phase Advanced", f"Phase updated to {metadata.get('new_phase', 'next phase')}."),
            "ProjectHealthChanged": ("Health Evaluation Updated", f"Project health status: {metadata.get('new_health', 'UPDATED')}."),
            "BlueprintGenerated": ("Blueprint Generated", "Architecture blueprint generated and ready for review."),
            "BlueprintApproved": ("Blueprint Approved", "Architecture blueprint reviewed, evaluated, and approved."),
            "TaskCreated": ("Task Created", f"Task '{metadata.get('title', 'New Task')}' added to board."),
            "TaskUpdated": ("Task Updated", f"Task '{metadata.get('title', 'Task')}' updated ({metadata.get('status', 'modified')})."),
            "TaskCompleted": ("Task Completed", f"Task '{metadata.get('title', 'Task')}' marked completed."),
            "MilestoneUpdated": ("Milestone Updated", f"Milestone '{metadata.get('title', 'Milestone')}' progress updated."),
            "RiskCreated": ("Risk Logged", f"Risk '{metadata.get('title', 'Risk')}' identified and tracked."),
            "RiskUpdated": ("Risk Updated", f"Risk '{metadata.get('title', 'Risk')}' mitigation status adjusted."),
            "DocumentCreated": ("Document Created", f"Document '{metadata.get('title', 'Doc')}' created."),
            "DocumentUpdated": ("Document Updated", f"Document '{metadata.get('title', 'Doc')}' content updated."),
            "GitHubConnected": ("GitHub Connected", f"Repository {metadata.get('repository_name', '')} linked."),
            "GitHubSynced": ("GitHub Synchronized", f"Repository commits synchronized ({metadata.get('commit_count', 0)} commits)."),
            "HelpRequestCreated": ("Help Request Submitted", f"Help request submitted: {metadata.get('subject', '')}."),
            "HelpRequestUpdated": ("Help Request Updated", "Help request details updated."),
            "HelpRequestResponded": ("Help Request Guidance", "Mentor guidance response provided."),
            "MentorNoteCreated": ("Mentor Note Posted", f"Mentor communication posted: {metadata.get('title', '')}."),
            "MentorNoteAcknowledged": ("Mentor Note Acknowledged", "Student acknowledged mentor feedback."),
            "ProjectChangeRequested": ("Change Proposed", f"Scope/tech change proposed: {metadata.get('change_title', '')}."),
            "ProjectChangeAnalyzed": ("Impact Analysis Complete", f"Change impact analysis evaluated for {metadata.get('change_title', '')}."),
            "ProjectChangeConfirmed": ("Change Confirmed", "Student confirmed impact analysis; blueprint regenerating."),
            "ProjectChangeCompleted": ("Regeneration Complete", f"Blueprint updated to version {metadata.get('resulting_version_number', '')}."),
            "AIMentorMessageSent": ("AI Mentor Consultation", "Discussion recorded with AI Mentor."),
            "GroupCreated": ("Cohort Initialized", f"Cohort group '{metadata.get('name', 'Cohort')}' initialized."),
            "StudentJoinedGroup": ("Student Enrolled", "Student enrolled in cohort."),
        }
        if event_type in type_titles:
            return type_titles[event_type]
        return (event_type, f"Action recorded by {actor_role}.")

    def _sanitize_metadata(self, metadata: dict[str, Any] | None) -> dict[str, Any]:
        """Strip sensitive credentials or secret tokens from governance metadata."""
        if not metadata:
            return {}
        forbidden_keys = {"token", "secret", "password", "key", "authorization", "auth", "credential", "api_key", "refresh_token"}
        sanitized: dict[str, Any] = {}
        for k, v in metadata.items():
            if any(bad in k.lower() for bad in forbidden_keys):
                continue
            if isinstance(v, (str, int, float, bool)) or v is None:
                sanitized[k] = v
            elif isinstance(v, (list, dict)):
                sanitized[k] = v
        return sanitized

    # ============================================================
    # AD19 — Admin System Health
    # ============================================================

    async def get_system_health(self) -> AdminSystemHealthResponseSchema:
        """Aggregate truthful real-time administrative system health across platform subsystems."""
        settings = get_settings()
        now = datetime.now(UTC)

        # 1. API runtime process
        subsystems: list[AdminSubsystemSummarySchema] = [
            AdminSubsystemSummarySchema(
                id="api",
                name="API Runtime Process",
                status="OPERATIONAL",
                type="CORE",
                details=f"FastAPI process active on {settings.app.HOST}:{settings.app.PORT}",
            )
        ]

        # 2. PostgreSQL database
        db_connected = db_lifecycle.is_initialised()
        db_status = "OPERATIONAL" if db_connected else ("UNCONFIGURED" if not settings.database.DATABASE_URL else "CRITICAL")
        subsystems.append(
            AdminSubsystemSummarySchema(
                id="database",
                name="PostgreSQL Persistence",
                status=db_status,
                type="DATABASE",
                details=f"Engine pool size: {settings.database.POOL_SIZE}, max overflow: {settings.database.MAX_OVERFLOW}",
            )
        )

        # 3. AI Provider Gateway
        active_ai_keys = len(settings.ai.active_keys)
        ai_status = "OPERATIONAL" if active_ai_keys > 0 else "CONFIGURED"
        subsystems.append(
            AdminSubsystemSummarySchema(
                id="ai_gateway",
                name="AI Provider Gateway",
                status=ai_status,
                type="AI",
                details=f"OpenRouter key pool: {active_ai_keys} active key(s), model: {settings.ai.DEFAULT_MODEL}",
            )
        )

        # 4. Outbox & Event Delivery
        outbox_counts = await self._outbox_repo.get_counts_by_status()
        outbox_status = "CRITICAL" if outbox_counts["failed"] > 0 else ("DEGRADED" if outbox_counts["pending"] > 20 else "OPERATIONAL")
        subsystems.append(
            AdminSubsystemSummarySchema(
                id="outbox",
                name="Transactional Outbox & Event Delivery",
                status=outbox_status,
                type="MESSAGING",
                details=f"{outbox_counts['pending']} pending, {outbox_counts['failed']} failed, {outbox_counts['published']} published",
            )
        )

        # 5. Email Service
        email_configured = bool(settings.email.GMAIL_CLIENT_ID and settings.email.GMAIL_REFRESH_TOKEN)
        email_status = "CONFIGURED" if email_configured else "UNCONFIGURED"
        subsystems.append(
            AdminSubsystemSummarySchema(
                id="email",
                name="Email Dispatcher",
                status=email_status,
                type="INTEGRATION",
                details=f"Provider: {settings.email.PROVIDER}, from: {settings.email.FROM_ADDRESS}",
            )
        )

        # 6. Storage Service
        storage_bucket = getattr(settings.auth, "STORAGE_BUCKET", None) if hasattr(settings, "auth") else None
        storage_status = "CONFIGURED" if storage_bucket else "UNCONFIGURED"
        max_upload_mb = getattr(settings.files, "MAX_UPLOAD_SIZE_MB", 25) if hasattr(settings, "files") else 25
        subsystems.append(
            AdminSubsystemSummarySchema(
                id="storage",
                name="Object Storage",
                status=storage_status,
                type="STORAGE",
                details=f"Bucket: {storage_bucket or 'Not configured'}, limit: {max_upload_mb}MB",
            )
        )

        # 7. GitHub Integration
        github_configured = bool(settings.github.CLIENT_ID)
        github_status = "CONFIGURED" if github_configured else "UNCONFIGURED"
        subsystems.append(
            AdminSubsystemSummarySchema(
                id="github",
                name="GitHub Integration",
                status=github_status,
                type="INTEGRATION",
                details="OAuth app configured" if github_configured else "GitHub integration credentials unconfigured",
            )
        )

        overall_status = "OPERATIONAL"
        if not db_connected or outbox_counts["failed"] > 0:
            overall_status = "CRITICAL"
        elif outbox_counts["pending"] > 20:
            overall_status = "DEGRADED"

        return AdminSystemHealthResponseSchema(
            overall_status=overall_status,
            environment=settings.app.ENV.value,
            version="0.1.0",
            timestamp=now,
            subsystems=subsystems,
            metrics=AdminSystemHealthMetricsSchema(
                outbox_pending=outbox_counts["pending"],
                outbox_failed=outbox_counts["failed"],
                outbox_published=outbox_counts["published"],
                active_ai_keys=active_ai_keys,
                db_pool_size=settings.database.POOL_SIZE,
                db_connected=db_connected,
            ),
        )

    # ============================================================
    # AD20 — Admin Component Detail
    # ============================================================

    async def get_component_detail(self, component_id: str) -> AdminSubsystemDetailSchema:
        """Inspect specific system component diagnostics and configuration signals."""
        settings = get_settings()
        now = datetime.now(UTC)
        comp = component_id.lower().strip()

        recent_failures_raw = await self._outbox_repo.list_recent_failures(5)
        recent_failures = [
            {
                "id": str(f.id),
                "event_type": f.event_type,
                "error": f.last_error or "Unknown failure",
                "occurred_at": f.occurred_at.isoformat() if f.occurred_at else None,
                "attempt_count": f.attempt_count,
            }
            for f in recent_failures_raw
        ]

        if comp == "api":
            return AdminSubsystemDetailSchema(
                id="api",
                name="API Runtime Process",
                status="OPERATIONAL",
                type="CORE",
                environment=settings.app.ENV.value,
                checked_at=now,
                configuration={
                    "app_name": settings.app.NAME,
                    "host": settings.app.HOST,
                    "port": settings.app.PORT,
                    "log_level": settings.app.LOG_LEVEL,
                    "debug_mode": settings.app.DEBUG,
                },
                diagnostics={
                    "runtime": "FastAPI ASGI engine",
                    "process_alive": True,
                    "correlation_middleware": "active",
                    "security_headers_middleware": "active",
                },
                recent_failures=[],
            )

        if comp == "database":
            db_connected = db_lifecycle.is_initialised()
            return AdminSubsystemDetailSchema(
                id="database",
                name="PostgreSQL Persistence",
                status="OPERATIONAL" if db_connected else "CRITICAL",
                type="DATABASE",
                environment=settings.app.ENV.value,
                checked_at=now,
                configuration={
                    "pool_size": settings.database.POOL_SIZE,
                    "max_overflow": settings.database.MAX_OVERFLOW,
                    "pool_timeout_seconds": settings.database.POOL_TIMEOUT_SECONDS,
                    "pool_recycle_seconds": settings.database.POOL_RECYCLE_SECONDS,
                    "url_configured": bool(settings.database.DATABASE_URL),
                },
                diagnostics={
                    "connectivity_confirmed": db_connected,
                    "engine_initialised": db_connected,
                    "driver": "asyncpg",
                },
                recent_failures=[],
            )

        if comp == "ai_gateway":
            active_keys = len(settings.ai.active_keys)
            return AdminSubsystemDetailSchema(
                id="ai_gateway",
                name="AI Provider Gateway",
                status="OPERATIONAL" if active_keys > 0 else "CONFIGURED",
                type="AI",
                environment=settings.app.ENV.value,
                checked_at=now,
                configuration={
                    "provider": "OpenRouter",
                    "base_url": settings.ai.OPENROUTER_BASE_URL,
                    "configured_keys_count": active_keys,
                    "fast_model": settings.ai.FAST_MODEL,
                    "standard_model": settings.ai.STANDARD_MODEL,
                    "default_model": settings.ai.DEFAULT_MODEL,
                    "fallback_model": settings.ai.FALLBACK_MODEL,
                    "timeout_seconds": settings.ai.REQUEST_TIMEOUT_SECONDS,
                    "max_retries": settings.ai.MAX_RETRIES,
                },
                diagnostics={
                    "key_rotation_active": active_keys > 1,
                    "live_keys_available": active_keys > 0,
                },
                recent_failures=[],
            )

        if comp == "outbox":
            counts = await self._outbox_repo.get_counts_by_status()
            outbox_status = "CRITICAL" if counts["failed"] > 0 else ("DEGRADED" if counts["pending"] > 20 else "OPERATIONAL")
            return AdminSubsystemDetailSchema(
                id="outbox",
                name="Transactional Outbox & Event Delivery",
                status=outbox_status,
                type="MESSAGING",
                environment=settings.app.ENV.value,
                checked_at=now,
                configuration={
                    "storage": "PostgreSQL domain_events table",
                    "atomic_enqueueing": True,
                },
                diagnostics={
                    "pending_backlog": counts["pending"],
                    "failed_events": counts["failed"],
                    "published_events": counts["published"],
                    "total_events": counts["total"],
                },
                recent_failures=recent_failures,
            )

        if comp == "email":
            configured = bool(settings.email.GMAIL_CLIENT_ID and settings.email.GMAIL_REFRESH_TOKEN)
            return AdminSubsystemDetailSchema(
                id="email",
                name="Email Dispatcher",
                status="CONFIGURED" if configured else "UNCONFIGURED",
                type="INTEGRATION",
                environment=settings.app.ENV.value,
                checked_at=now,
                configuration={
                    "provider": settings.email.PROVIDER,
                    "from_address": settings.email.FROM_ADDRESS,
                    "contact_mailbox": settings.email.CONTACT_MAILBOX,
                    "oauth_client_id_configured": bool(settings.email.GMAIL_CLIENT_ID),
                    "refresh_token_configured": bool(settings.email.GMAIL_REFRESH_TOKEN),
                },
                diagnostics={
                    "dispatcher_ready": configured,
                },
                recent_failures=[],
            )

        if comp == "storage":
            storage_bucket = getattr(settings.auth, "STORAGE_BUCKET", None) if hasattr(settings, "auth") else None
            configured = bool(storage_bucket)
            max_upload_mb = getattr(settings.files, "MAX_UPLOAD_SIZE_MB", 25) if hasattr(settings, "files") else 25
            max_archive_mb = getattr(settings.files, "MAX_ARCHIVE_SIZE_MB", 50) if hasattr(settings, "files") else 50
            return AdminSubsystemDetailSchema(
                id="storage",
                name="Object Storage",
                status="CONFIGURED" if configured else "UNCONFIGURED",
                type="STORAGE",
                environment=settings.app.ENV.value,
                checked_at=now,
                configuration={
                    "bucket_name": storage_bucket or "UNCONFIGURED",
                    "max_upload_size_mb": max_upload_mb,
                    "max_archive_size_mb": max_archive_mb,
                },
                diagnostics={
                    "bucket_configured": configured,
                },
                recent_failures=[],
            )

        if comp == "github":
            configured = bool(settings.github.CLIENT_ID)
            return AdminSubsystemDetailSchema(
                id="github",
                name="GitHub Integration",
                status="CONFIGURED" if configured else "UNCONFIGURED",
                type="INTEGRATION",
                environment=settings.app.ENV.value,
                checked_at=now,
                configuration={
                    "oauth_client_id_configured": configured,
                    "redirect_uri_configured": bool(settings.github.REDIRECT_URI),
                    "webhook_configured": bool(settings.github.WEBHOOK_SECRET),
                },
                diagnostics={
                    "integration_enabled": configured,
                },
                recent_failures=[],
            )

        raise NotFoundException(
            f"Component '{component_id}' is not recognized. Valid components: api, database, ai_gateway, outbox, email, storage, github.",
            code="COMPONENT_NOT_FOUND",
        )

    # ============================================================
    # AD24 — Admin Security & Audit Overview
    # ============================================================

    async def get_security_overview(self) -> AdminSecurityOverviewSchema:
        """Aggregate platform user posture and audit metrics (AD24)."""
        # User counts
        stmt_users = select(UserModel.role, UserModel.status, func.count(UserModel.id)).group_by(
            UserModel.role, UserModel.status
        )
        res_users = await self._session.execute(stmt_users)
        user_rows = res_users.all()

        total_users = 0
        active_users = 0
        inactive_users = 0
        suspended_users = 0
        admin_count = 0
        mentor_count = 0
        student_count = 0

        for role, status, count in user_rows:
            total_users += count
            if status == AccountStatus.ACTIVE.value:
                active_users += count
            elif status == AccountStatus.INACTIVE.value:
                inactive_users += count
            elif status == AccountStatus.SUSPENDED.value:
                suspended_users += count

            if role == UserRole.ADMIN.value:
                admin_count += count
            elif role == UserRole.MENTOR.value:
                mentor_count += count
            elif role == UserRole.STUDENT.value:
                student_count += count

        # Audit counts
        outbox_counts = await self._outbox_repo.get_counts_by_status()

        # Recent events
        recent_raw = await self._outbox_repo.list_recent_events(10)
        recent_events = []
        for evt in recent_raw:
            title, desc = self._format_event_description(evt.event_type, evt.metadata_json or {}, evt.actor_role)
            recent_events.append({
                "id": str(evt.id),
                "event_type": evt.event_type,
                "title": title,
                "description": desc,
                "actor_id": str(evt.actor_id) if evt.actor_id else None,
                "actor_role": evt.actor_role,
                "resource_type": evt.resource_type,
                "resource_id": str(evt.resource_id),
                "occurred_at": evt.occurred_at.isoformat() if evt.occurred_at else None,
                "status": evt.status,
            })

        return AdminSecurityOverviewSchema(
            user_posture=AdminUserSecurityPostureSchema(
                total_users=total_users,
                active_users=active_users,
                inactive_users=inactive_users,
                suspended_users=suspended_users,
                admin_count=admin_count,
                mentor_count=mentor_count,
                student_count=student_count,
            ),
            audit_summary=AdminAuditSummaryMetricsSchema(
                total_events=outbox_counts["total"],
                outbox_delivery_failures=outbox_counts["failed"],
            ),
            recent_security_relevant_events=recent_events,
        )

    # ============================================================
    # AD25 — Admin Audit Log
    # ============================================================

    async def list_audit_log(
        self,
        *,
        search: str | None = None,
        actor_role: str | None = None,
        event_type: str | None = None,
        resource_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AdminAuditLogResponseSchema:
        """Query platform-wide canonical audit events with filters and pagination (AD25)."""
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)

        events_raw = await self._outbox_repo.list_platform_events(
            search=search,
            actor_role=actor_role,
            event_type=event_type,
            resource_type=resource_type,
            limit=safe_limit,
            offset=safe_offset,
        )
        total = await self._outbox_repo.count_platform_events(
            search=search,
            actor_role=actor_role,
            event_type=event_type,
            resource_type=resource_type,
        )

        items: list[AdminAuditEventItemSchema] = []
        for evt in events_raw:
            title, desc = self._format_event_description(evt.event_type, evt.metadata_json or {}, evt.actor_role)
            items.append(
                AdminAuditEventItemSchema(
                    id=str(evt.id),
                    event_type=evt.event_type,
                    title=title,
                    description=desc,
                    actor_id=str(evt.actor_id) if evt.actor_id else None,
                    actor_role=evt.actor_role,
                    resource_type=evt.resource_type,
                    resource_id=str(evt.resource_id),
                    project_instance_id=str(evt.project_instance_id) if evt.project_instance_id else None,
                    group_id=str(evt.group_id) if evt.group_id else None,
                    correlation_id=evt.correlation_id or "",
                    status=evt.status,
                    occurred_at=evt.occurred_at,
                    metadata=self._sanitize_metadata(evt.metadata_json),
                )
            )

        return AdminAuditLogResponseSchema(
            total=total,
            limit=safe_limit,
            offset=safe_offset,
            events=items,
        )

    # ============================================================
    # AD26 — Governed Investigation Surface
    # ============================================================

    async def get_investigation_overview(self) -> AdminInvestigationOverviewResponseSchema:
        """Inspect candidate resources requiring administrative governance review (AD26)."""
        flagged: list[AdminInspectableResourceSchema] = []

        # 1. Suspended accounts
        stmt_suspended = select(UserModel).where(UserModel.status == AccountStatus.SUSPENDED.value).limit(10)
        res_suspended = await self._session.execute(stmt_suspended)
        for user in res_suspended.scalars().all():
            inspect_path = f"/admin/students/{user.id}" if user.role == UserRole.STUDENT.value else f"/admin/mentors/{user.id}"
            flagged.append(
                AdminInspectableResourceSchema(
                    resource_type="USER",
                    resource_id=str(user.id),
                    label=user.full_name or user.email,
                    detail=f"Account status is SUSPENDED ({user.role}). Review access and activity history.",
                    flag_reason="ACCOUNT_SUSPENDED",
                    flagged_at=user.updated_at or user.created_at,
                    canonical_inspection_url=inspect_path,
                )
            )

        # 2. Critical health projects
        stmt_critical = select(ProjectInstanceModel).where(ProjectInstanceModel.health == ProjectHealth.CRITICAL.value).limit(10)
        res_critical = await self._session.execute(stmt_critical)
        for proj in res_critical.scalars().all():
            flagged.append(
                AdminInspectableResourceSchema(
                    resource_type="PROJECT",
                    resource_id=str(proj.id),
                    label=proj.name,
                    detail="Project instance evaluated as critical health; milestones or execution slipping.",
                    flag_reason="CRITICAL_HEALTH",
                    flagged_at=proj.updated_at or proj.created_at,
                    canonical_inspection_url=f"/admin/instances/{proj.id}",
                )
            )

        # 3. Delivery failures
        recent_failures = await self._outbox_repo.list_recent_failures(5)
        for fail in recent_failures:
            flagged.append(
                AdminInspectableResourceSchema(
                    resource_type="OUTBOX_FAILURE",
                    resource_id=str(fail.id),
                    label=f"Outbox Failure: {fail.event_type}",
                    detail=fail.last_error or "Transactional domain event delivery failed.",
                    flag_reason="DELIVERY_FAILURE",
                    flagged_at=fail.occurred_at,
                    canonical_inspection_url="/admin/security/audit",
                )
            )

        return AdminInvestigationOverviewResponseSchema(
            framework_status="GOVERNED_INSPECTION_ACTIVE",
            disclaimer="Governed Inspection Surface: Inspects canonical resources requiring administrative review. Persistent investigation tickets are not configured in current schema.",
            total_flagged=len(flagged),
            flagged_resources=flagged,
        )

    # ============================================================
    # AD27 — Governed Investigation Detail
    # ============================================================

    async def get_investigation_detail(self, investigation_id: str) -> dict[str, Any]:
        """
        Inspect candidate entity or return 404.
        AD27 requires persistent investigation identity that is not present in the current canonical schema.
        """
        # Attempt to inspect as user or project if UUID
        try:
            target_uuid = uuid.UUID(investigation_id)
        except (ValueError, TypeError):
            raise NotFoundException(
                "Investigation record not found. Note: Persistent investigation tickets are not configured in the current canonical schema.",
                code="INVESTIGATION_NOT_FOUND",
            )

        # Check if matches UserModel
        user = await self._user_repo.get_by_id(target_uuid)
        if user:
            return {
                "target_type": "USER",
                "target_id": str(user.id),
                "label": user.full_name or user.email,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "inspection_mode": "CANONICAL_USER_INSPECTION",
            }

        # Check if matches ProjectInstanceModel
        proj = await self._project_repo.get_by_id(target_uuid)
        if proj:
            return {
                "target_type": "PROJECT",
                "target_id": str(proj.id),
                "label": proj.name,
                "health": proj.health,
                "phase": proj.current_phase,
                "status": proj.status,
                "created_at": proj.created_at.isoformat() if proj.created_at else None,
                "inspection_mode": "CANONICAL_PROJECT_INSPECTION",
            }

        raise NotFoundException(
            "Investigation record not found. Note: Persistent investigation tickets are not configured in the current canonical schema.",
            code="INVESTIGATION_NOT_FOUND",
        )

    # ============================================================
    # AD21 — Admin Documents Inventory
    # ============================================================

    async def list_platform_documents(
        self,
        *,
        search: str | None = None,
        doc_type: str | None = None,
        status: str | None = None,
        project_id: uuid.UUID | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AdminDocumentsResponseSchema:
        """List platform documents with project information, filtering, and summary metrics."""
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        total = await self._document_repo.count_platform_documents(
            search=search, doc_type=doc_type, status=status, project_id=project_id
        )
        doc_rows = await self._document_repo.list_platform_documents(
            search=search, doc_type=doc_type, status=status, project_id=project_id, limit=limit, offset=offset
        )

        stmt_summary = select(ProjectDocumentModel.doc_type, func.count(ProjectDocumentModel.id)).group_by(ProjectDocumentModel.doc_type)
        res_summary = await self._session.execute(stmt_summary)
        summary = {dt: count for dt, count in res_summary.all()}

        documents: list[AdminDocumentItemSchema] = []
        for doc, proj_name in doc_rows:
            size_bytes = len(doc.content.encode("utf-8")) if doc.content else 0
            documents.append(
                AdminDocumentItemSchema(
                    id=str(doc.id),
                    project_instance_id=str(doc.project_instance_id),
                    project_name=proj_name,
                    document_key=doc.document_key,
                    title=doc.title,
                    doc_type=doc.doc_type,
                    format=doc.format,
                    version=doc.version,
                    status=doc.status,
                    source=doc.source,
                    size_bytes=size_bytes,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                )
            )

        return AdminDocumentsResponseSchema(
            total=total,
            limit=limit,
            offset=offset,
            summary=summary,
            documents=documents,
        )

    # ============================================================
    # AD22 — RAG Diagnostics & Architecture Monitoring
    # ============================================================

    async def get_rag_diagnostics(self) -> AdminRAGDiagnosticsSchema:
        """Retrieve truthful RAG subsystem configuration and integration posture."""
        settings = get_settings()

        stmt_eligible = select(func.count(ProjectDocumentModel.id)).where(ProjectDocumentModel.status == "ACTIVE")
        res_eligible = await self._session.execute(stmt_eligible)
        eligible_count = res_eligible.scalar() or 0

        recent_events = await self._outbox_repo.list_platform_events(
            event_type=None,
            resource_type="project_document",
            limit=5,
            offset=0,
        )
        recent_events_formatted = [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "title": self._format_event_description(e.event_type, e.actor_role, e.resource_type)[0],
                "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
                "status": e.status,
            }
            for e in recent_events
        ]

        target_chunk_size = getattr(settings.rag, "CHUNK_SIZE", 1000) if hasattr(settings, "rag") else 1000
        target_chunk_overlap = getattr(settings.rag, "CHUNK_OVERLAP", 150) if hasattr(settings, "rag") else 150
        target_top_k = getattr(settings.rag, "TOP_K", 8) if hasattr(settings, "rag") else 8
        index_gen = getattr(settings.rag, "INDEX_GENERATED_DOCUMENTS", True) if hasattr(settings, "rag") else True
        embedding_model = getattr(settings.ai, "EMBEDDING_MODEL", "openai/text-embedding-3-small") if hasattr(settings, "ai") else "openai/text-embedding-3-small"

        return AdminRAGDiagnosticsSchema(
            status="DEFERRED_INTEGRATION",
            vector_store_type="NONE_CONFIGURED",
            embedding_model=embedding_model,
            target_chunk_size=target_chunk_size,
            target_chunk_overlap=target_chunk_overlap,
            target_top_k=target_top_k,
            index_generated_documents=index_gen,
            eligible_documents_count=eligible_count,
            disclaimer="Vector database integration is deferred in Gate 09. Document chunking and embedding storage are currently inactive.",
            recent_events=recent_events_formatted,
        )

    # ============================================================
    # AD23 — Document Generation Job Runs
    # ============================================================

    async def list_generation_jobs(
        self,
        *,
        status: str | None = None,
        job_type: str | None = None,
        project_id: uuid.UUID | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AdminGenerationJobsResponseSchema:
        """List platform synthesis runs from blueprint_jobs with summary analytics."""
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        total = await self._blueprint_repo.count_platform_jobs(
            status=status, job_type=job_type, project_id=project_id
        )
        job_rows = await self._blueprint_repo.list_platform_jobs(
            status=status, job_type=job_type, project_id=project_id, limit=limit, offset=offset
        )

        counts = await self._blueprint_repo.get_job_counts_by_status()

        stmt_durations = select(BlueprintJobModel.started_at, BlueprintJobModel.completed_at).where(
            BlueprintJobModel.status == "COMPLETED",
            BlueprintJobModel.started_at.isnot(None),
            BlueprintJobModel.completed_at.isnot(None),
        )
        res_dur = await self._session.execute(stmt_durations)
        durations = [
            (c - s).total_seconds()
            for s, c in res_dur.all()
            if c is not None and s is not None and c >= s
        ]
        avg_dur = round(sum(durations) / len(durations), 1) if durations else None

        summary = AdminGenerationJobsSummarySchema(
            total=sum(counts.values()),
            completed=counts.get("COMPLETED", 0),
            failed=counts.get("FAILED", 0),
            running=counts.get("RUNNING", 0),
            pending=counts.get("PENDING", 0),
            average_duration_seconds=avg_dur,
        )

        jobs: list[AdminGenerationJobItemSchema] = []
        for job, proj_name in job_rows:
            dur = None
            if job.started_at and job.completed_at and job.completed_at >= job.started_at:
                dur = int((job.completed_at - job.started_at).total_seconds())

            sanitized_error = None
            if job.error:
                sanitized_error = job.error.splitlines()[0][:250] if job.error else None

            jobs.append(
                AdminGenerationJobItemSchema(
                    id=str(job.id),
                    blueprint_id=str(job.blueprint_id),
                    project_instance_id=str(job.project_instance_id),
                    project_name=proj_name,
                    job_type=job.job_type,
                    target_output=job.target_output,
                    status=job.status,
                    current_step=job.current_step,
                    progress_percent=job.progress_percent,
                    error=sanitized_error,
                    duration_seconds=dur,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    created_at=job.created_at,
                )
            )

        return AdminGenerationJobsResponseSchema(
            total=total,
            limit=limit,
            offset=offset,
            summary=summary,
            jobs=jobs,
        )

    # ============================================================
    # AD28 — Platform Macro Analytics
    # ============================================================

    async def get_platform_analytics(self) -> AdminPlatformAnalyticsResponseSchema:
        """Aggregate authoritative platform macro telemetry across entities and event history."""
        # 1. Users
        stmt_users = select(UserModel.role, UserModel.status, func.count(UserModel.id)).group_by(
            UserModel.role, UserModel.status
        )
        res_users = await self._session.execute(stmt_users)
        user_rows = res_users.all()
        total_users = 0
        total_students = 0
        total_mentors = 0
        user_status_dist: dict[str, int] = {}
        for role, status, count in user_rows:
            total_users += count
            user_status_dist[status] = user_status_dist.get(status, 0) + count
            if role == UserRole.STUDENT.value:
                total_students += count
            elif role == UserRole.MENTOR.value:
                total_mentors += count

        # 2. Cohort Groups
        stmt_groups = select(GroupModel.status, func.count(GroupModel.id)).group_by(GroupModel.status)
        res_groups = await self._session.execute(stmt_groups)
        group_rows = res_groups.all()
        total_groups = sum(c for _, c in group_rows)
        active_groups = sum(c for s, c in group_rows if s == GroupStatus.ACTIVE.value)

        # 3. Project Instances
        stmt_projs = select(
            ProjectInstanceModel.current_phase,
            ProjectInstanceModel.health,
            ProjectInstanceModel.status,
            func.count(ProjectInstanceModel.id),
        ).group_by(ProjectInstanceModel.current_phase, ProjectInstanceModel.health, ProjectInstanceModel.status)
        res_projs = await self._session.execute(stmt_projs)
        proj_rows = res_projs.all()
        total_projects = 0
        active_projects = 0
        completed_projects = 0
        at_risk_projects = 0
        phase_dist: dict[str, int] = {}
        health_dist: dict[str, int] = {}
        for phase, health, status, count in proj_rows:
            total_projects += count
            phase_dist[phase] = phase_dist.get(phase, 0) + count
            health_dist[health] = health_dist.get(health, 0) + count
            if status == ProjectStatus.ACTIVE.value:
                active_projects += count
            elif status == ProjectStatus.COMPLETED.value:
                completed_projects += count
            if health in (ProjectHealth.WARNING.value, ProjectHealth.CRITICAL.value):
                at_risk_projects += count

        # 4. Project Definitions
        stmt_defs = select(func.count(ProjectDefinitionModel.id))
        res_defs = await self._session.execute(stmt_defs)
        total_defs = res_defs.scalar() or 0

        # 5. Execution Tasks
        stmt_tasks = select(ProjectTaskModel.status, func.count(ProjectTaskModel.id)).group_by(ProjectTaskModel.status)
        res_tasks = await self._session.execute(stmt_tasks)
        task_dist = {s: c for s, c in res_tasks.all()}

        # 6. Documents
        stmt_docs = select(ProjectDocumentModel.doc_type, func.count(ProjectDocumentModel.id)).group_by(ProjectDocumentModel.doc_type)
        res_docs = await self._session.execute(stmt_docs)
        doc_rows = res_docs.all()
        total_documents = sum(c for _, c in doc_rows)
        doc_type_dist = {dt: c for dt, c in doc_rows}

        # 7. Generation Jobs
        stmt_jobs = select(BlueprintJobModel.status, func.count(BlueprintJobModel.id)).group_by(BlueprintJobModel.status)
        res_jobs = await self._session.execute(stmt_jobs)
        job_rows = res_jobs.all()
        total_jobs = sum(c for _, c in job_rows)
        job_dist = {s: c for s, c in job_rows}

        # 8. Help Requests
        stmt_helps = select(ProjectHelpRequestModel.status, func.count(ProjectHelpRequestModel.id)).group_by(ProjectHelpRequestModel.status)
        res_helps = await self._session.execute(stmt_helps)
        help_rows = res_helps.all()
        total_helps = sum(c for _, c in help_rows)
        help_dist = {s: c for s, c in help_rows}

        # 9. Domain Events
        stmt_events = select(func.count(DomainEventModel.id))
        res_events = await self._session.execute(stmt_events)
        total_events = res_events.scalar() or 0

        week_ago = datetime.now(UTC) - timedelta(days=7)
        stmt_recent_events = select(func.count(DomainEventModel.id)).where(DomainEventModel.occurred_at >= week_ago)
        res_recent_events = await self._session.execute(stmt_recent_events)
        recent_events_count = res_recent_events.scalar() or 0

        overview = AdminAnalyticsOverviewMetricsSchema(
            total_users=total_users,
            total_students=total_students,
            total_mentors=total_mentors,
            total_groups=total_groups,
            active_groups=active_groups,
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            at_risk_projects=at_risk_projects,
            total_definitions=total_defs,
            total_documents=total_documents,
            total_generation_jobs=total_jobs,
            total_domain_events=total_events,
            total_help_requests=total_helps,
        )

        return AdminPlatformAnalyticsResponseSchema(
            overview=overview,
            project_phase_distribution=phase_dist,
            project_health_distribution=health_dist,
            user_status_distribution=user_status_dist,
            task_status_distribution=task_dist,
            document_type_distribution=doc_type_dist,
            generation_job_distribution=job_dist,
            help_request_status_distribution=help_dist,
            activity_volume_recent=recent_events_count,
        )

    # ============================================================
    # AD29 — Analytics Dimensional Detail
    # ============================================================

    async def get_analytics_dimension_detail(self, dimension: str) -> AdminAnalyticsDimensionDetailSchema:
        """Deep-dive analytics for a canonical dimension: projects, users, documents, activity."""
        dim = dimension.lower().strip()
        valid_dimensions = ("projects", "users", "documents", "activity")
        if dim not in valid_dimensions:
            raise NotFoundException(
                f"Analytics dimension '{dimension}' is not recognized. Valid dimensions: {', '.join(valid_dimensions)}",
                code="ANALYTICS_DIMENSION_NOT_FOUND",
            )

        if dim == "projects":
            stmt = (
                select(
                    ProjectInstanceModel.id,
                    ProjectInstanceModel.name,
                    ProjectInstanceModel.current_phase,
                    ProjectInstanceModel.health,
                    ProjectInstanceModel.progress_percentage,
                    ProjectInstanceModel.status,
                    ProjectInstanceModel.created_at,
                )
                .order_by(ProjectInstanceModel.created_at.desc())
                .limit(20)
            )
            res = await self._session.execute(stmt)
            recent_projects = [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "phase": r.current_phase,
                    "health": r.health,
                    "progress": r.progress_percentage,
                    "status": r.status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in res.all()
            ]

            stmt_counts = select(ProjectInstanceModel.current_phase, func.count(ProjectInstanceModel.id)).group_by(ProjectInstanceModel.current_phase)
            res_counts = await self._session.execute(stmt_counts)
            breakdown = [{"category": phase, "count": count} for phase, count in res_counts.all()]

            stmt_avg = select(func.avg(ProjectInstanceModel.progress_percentage)).where(ProjectInstanceModel.status == "ACTIVE")
            res_avg = await self._session.execute(stmt_avg)
            avg_progress = round(float(res_avg.scalar() or 0), 1)

            return AdminAnalyticsDimensionDetailSchema(
                dimension="projects",
                title="Projects Execution & Health Analytics",
                description="In-depth analysis of project instance lifecycle phases, health distribution, and milestone progress.",
                summary={
                    "sampled_projects_count": len(recent_projects),
                    "average_active_progress_percent": avg_progress,
                },
                breakdown=breakdown,
                recent_records=recent_projects,
            )

        elif dim == "users":
            stmt_roles = select(UserModel.role, func.count(UserModel.id)).group_by(UserModel.role)
            res_roles = await self._session.execute(stmt_roles)
            breakdown = [{"category": role, "count": count} for role, count in res_roles.all()]

            stmt_recent_users = (
                select(UserModel.id, UserModel.email, UserModel.full_name, UserModel.role, UserModel.status, UserModel.created_at)
                .order_by(UserModel.created_at.desc())
                .limit(20)
            )
            res_users = await self._session.execute(stmt_recent_users)
            recent_users = [
                {
                    "id": str(u.id),
                    "email": u.email,
                    "name": u.full_name or "—",
                    "role": u.role,
                    "status": u.status,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in res_users.all()
            ]

            return AdminAnalyticsDimensionDetailSchema(
                dimension="users",
                title="User Enrollment & Role Distribution",
                description="Comprehensive breakdown of student and mentor registrations, account statuses, and cohort engagement.",
                summary={"sampled_users_count": len(recent_users)},
                breakdown=breakdown,
                recent_records=recent_users,
            )

        elif dim == "documents":
            stmt_types = select(ProjectDocumentModel.doc_type, func.count(ProjectDocumentModel.id)).group_by(ProjectDocumentModel.doc_type)
            res_types = await self._session.execute(stmt_types)
            breakdown = [{"category": dt, "count": count} for dt, count in res_types.all()]

            stmt_recent_docs = (
                select(ProjectDocumentModel.id, ProjectDocumentModel.title, ProjectDocumentModel.doc_type, ProjectDocumentModel.status, ProjectDocumentModel.created_at)
                .order_by(ProjectDocumentModel.created_at.desc())
                .limit(20)
            )
            res_docs = await self._session.execute(stmt_recent_docs)
            recent_docs = [
                {
                    "id": str(d.id),
                    "title": d.title,
                    "type": d.doc_type,
                    "status": d.status,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in res_docs.all()
            ]

            return AdminAnalyticsDimensionDetailSchema(
                dimension="documents",
                title="Document Deliverables & Synthesis Analytics",
                description="Detailed telemetry on generated architecture blueprints, specifications, and student deliverables.",
                summary={"sampled_documents_count": len(recent_docs)},
                breakdown=breakdown,
                recent_records=recent_docs,
            )

        else:  # activity
            stmt_events = select(DomainEventModel.actor_role, func.count(DomainEventModel.id)).group_by(DomainEventModel.actor_role)
            res_events = await self._session.execute(stmt_events)
            breakdown = [{"category": role, "count": count} for role, count in res_events.all()]

            recent_events = await self._outbox_repo.list_recent_events(limit=20)
            recent_formatted = [
                {
                    "id": str(e.id),
                    "event_type": e.event_type,
                    "actor_role": e.actor_role,
                    "resource_type": e.resource_type,
                    "status": e.status,
                    "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
                }
                for e in recent_events
            ]

            return AdminAnalyticsDimensionDetailSchema(
                dimension="activity",
                title="Platform Activity & Event Velocity",
                description="Chronological audit distribution, actor participation velocity, and asynchronous event throughput.",
                summary={"sampled_events_count": len(recent_formatted)},
                breakdown=breakdown,
                recent_records=recent_formatted,
            )

    # ============================================================
    # AD11 — Admin AI Observatory
    # ============================================================

    async def get_ai_observatory(self) -> AdminAIObservatoryResponseSchema:
        """Aggregate authoritative AI operational posture, active jobs, KPIs, and recent activity (AD11)."""
        settings = get_settings()
        active_keys = len(settings.ai.active_keys)
        ai_status = "OPERATIONAL" if active_keys > 0 else "CONFIGURED"

        gateway = AdminAIGatewayPostureSchema(
            provider="OpenRouter",
            status=ai_status,
            base_url=settings.ai.OPENROUTER_BASE_URL,
            configured_key_slots=active_keys,
            total_slots=5,
            default_model=settings.ai.DEFAULT_MODEL,
            fast_model=settings.ai.FAST_MODEL,
            standard_model=settings.ai.STANDARD_MODEL,
            reasoning_model=settings.ai.REASONING_MODEL,
            fallback_model=settings.ai.FALLBACK_MODEL,
            request_timeout_seconds=settings.ai.REQUEST_TIMEOUT_SECONDS,
            max_retries=settings.ai.MAX_RETRIES,
            credential_note="Configured key count reflects presence of credentials in environment. Live provider reachability is verified per request.",
        )

        counts = await self._blueprint_repo.get_job_counts_by_status()
        completed = counts.get("COMPLETED", 0)
        failed = counts.get("FAILED", 0)
        running = counts.get("RUNNING", 0)
        total_bp_jobs = sum(counts.values())
        success_rate = round((completed / (completed + failed)) * 100, 1) if (completed + failed) > 0 else None

        stmt_durations = select(BlueprintJobModel.started_at, BlueprintJobModel.completed_at).where(
            BlueprintJobModel.status == "COMPLETED",
            BlueprintJobModel.started_at.isnot(None),
            BlueprintJobModel.completed_at.isnot(None),
        )
        res_dur = await self._session.execute(stmt_durations)
        durations = [
            (c - s).total_seconds()
            for s, c in res_dur.all()
            if c is not None and s is not None and c >= s
        ]
        avg_dur = round(sum(durations) / len(durations), 1) if durations else None

        stmt_m = select(func.count(AIMentorMessageModel.id)).where(AIMentorMessageModel.role == "assistant")
        mentor_msgs = (await self._session.execute(stmt_m)).scalar() or 0

        stmt_c = select(func.count(ProjectChangeRequestModel.id))
        change_reqs = (await self._session.execute(stmt_c)).scalar() or 0

        total_transactions = total_bp_jobs + mentor_msgs + change_reqs

        kpis = AdminAIObservatoryKPISchema(
            total_ai_transactions=total_transactions,
            blueprint_jobs_total=total_bp_jobs,
            blueprint_jobs_completed=completed,
            blueprint_jobs_failed=failed,
            success_rate_percent=success_rate,
            currently_running_jobs=running,
            average_duration_seconds=avg_dur,
            mentor_messages_total=mentor_msgs,
            change_requests_total=change_reqs,
        )

        # Active jobs
        stmt_active = (
            select(BlueprintJobModel, ProjectInstanceModel.name)
            .outerjoin(ProjectInstanceModel, BlueprintJobModel.project_instance_id == ProjectInstanceModel.id)
            .where(BlueprintJobModel.status == "RUNNING")
            .order_by(BlueprintJobModel.created_at.desc())
            .limit(10)
        )
        res_active = await self._session.execute(stmt_active)
        active_jobs = [
            AdminAIActiveJobSchema(
                id=str(job.id),
                blueprint_id=str(job.blueprint_id),
                project_instance_id=str(job.project_instance_id),
                project_name=proj_name or "Unknown Project",
                job_type=job.job_type,
                status=job.status,
                current_step=job.current_step,
                progress_percent=job.progress_percent,
                started_at=job.started_at,
                created_at=job.created_at,
            )
            for job, proj_name in res_active.all()
        ]

        # Recent AI domain events
        ai_event_types = [
            "BlueprintGenerated",
            "BlueprintApproved",
            "AIMentorMessageSent",
            "ProjectChangeRequested",
            "ProjectChangeAnalyzed",
            "ProjectChangeCompleted",
        ]
        stmt_events = (
            select(DomainEventModel)
            .where(DomainEventModel.event_type.in_(ai_event_types))
            .order_by(DomainEventModel.occurred_at.desc())
            .limit(15)
        )
        res_events = await self._session.execute(stmt_events)
        recent_activity: list[AdminAIRecentActivitySchema] = []
        for e in res_events.scalars().all():
            meta = e.metadata_json or {}
            title = meta.get("project_name") or e.event_type
            recent_activity.append(
                AdminAIRecentActivitySchema(
                    id=str(e.id),
                    activity_type="DOMAIN_EVENT",
                    title=f"{e.event_type}: {title}",
                    detail=f"Resource {e.resource_type} ({e.status}) by {e.actor_role}",
                    status=e.status,
                    project_name=meta.get("project_name"),
                    correlation_id=e.correlation_id or None,
                    timestamp=e.occurred_at,
                )
            )

        return AdminAIObservatoryResponseSchema(
            gateway=gateway,
            kpis=kpis,
            active_jobs=active_jobs,
            recent_activity=recent_activity,
        )

    # ============================================================
    # AD12 — Admin AI Usage
    # ============================================================

    async def get_ai_usage(self) -> AdminAIUsageResponseSchema:
        """Aggregate execution and transaction volume by capability, project, and time trend (AD12)."""
        counts = await self._blueprint_repo.get_job_counts_by_status()
        total_bp_jobs = sum(counts.values())

        stmt_m = select(func.count(AIMentorMessageModel.id)).where(AIMentorMessageModel.role == "assistant")
        mentor_msgs = (await self._session.execute(stmt_m)).scalar() or 0

        stmt_c = select(func.count(ProjectChangeRequestModel.id))
        change_reqs = (await self._session.execute(stmt_c)).scalar() or 0

        overall_vol = AdminAIUsageOverallVolumeSchema(
            blueprint_synthesis_jobs=total_bp_jobs,
            ai_mentor_messages=mentor_msgs,
            project_change_analyses=change_reqs,
            total_recorded_transactions=total_bp_jobs + mentor_msgs + change_reqs,
        )

        total_tx = overall_vol.total_recorded_transactions

        # Capability breakdown
        stmt_types = select(BlueprintJobModel.job_type, func.count(BlueprintJobModel.id)).group_by(BlueprintJobModel.job_type)
        res_types = await self._session.execute(stmt_types)
        job_type_counts = dict(res_types.all())

        full_gen = job_type_counts.get("FULL_GENERATION", 0)
        targeted_retry = job_type_counts.get("TARGETED_RETRY", 0)

        capability_breakdown = [
            AdminAICapabilityUsageSchema(
                capability_key="BLUEPRINT_GEN",
                label="Blueprint Master Synthesis",
                count=full_gen,
                percentage=round((full_gen / total_tx) * 100, 1) if total_tx > 0 else 0.0,
            ),
            AdminAICapabilityUsageSchema(
                capability_key="BLUEPRINT_RETRY",
                label="Blueprint Targeted Repair",
                count=targeted_retry,
                percentage=round((targeted_retry / total_tx) * 100, 1) if total_tx > 0 else 0.0,
            ),
            AdminAICapabilityUsageSchema(
                capability_key="AI_MENTOR",
                label="AI Mentor Assistant Dialogue",
                count=mentor_msgs,
                percentage=round((mentor_msgs / total_tx) * 100, 1) if total_tx > 0 else 0.0,
            ),
            AdminAICapabilityUsageSchema(
                capability_key="CHANGE_ANALYSIS",
                label="Project Change Impact Analyzer",
                count=change_reqs,
                percentage=round((change_reqs / total_tx) * 100, 1) if total_tx > 0 else 0.0,
            ),
        ]

        # Time trend (past 14 days aggregated)
        fourteen_days_ago = datetime.now(UTC) - timedelta(days=14)
        stmt_time_bp = (
            select(BlueprintJobModel.created_at)
            .where(BlueprintJobModel.created_at >= fourteen_days_ago)
            .order_by(BlueprintJobModel.created_at.asc())
        )
        res_time_bp = await self._session.execute(stmt_time_bp)
        bp_dates = [c.strftime("%Y-%m-%d") for c in res_time_bp.scalars().all() if c]

        stmt_time_m = (
            select(AIMentorMessageModel.created_at)
            .where(AIMentorMessageModel.created_at >= fourteen_days_ago, AIMentorMessageModel.role == "assistant")
            .order_by(AIMentorMessageModel.created_at.asc())
        )
        res_time_m = await self._session.execute(stmt_time_m)
        m_dates = [c.strftime("%Y-%m-%d") for c in res_time_m.scalars().all() if c]

        date_map: dict[str, dict[str, int]] = {}
        for d in bp_dates:
            date_map.setdefault(d, {"bp": 0, "m": 0})["bp"] += 1
        for d in m_dates:
            date_map.setdefault(d, {"bp": 0, "m": 0})["m"] += 1

        time_trend: list[AdminAITimeBucketSchema] = [
            AdminAITimeBucketSchema(
                date=k,
                blueprint_jobs_count=v["bp"],
                mentor_messages_count=v["m"],
                total_count=v["bp"] + v["m"],
            )
            for k, v in sorted(date_map.items())
        ]

        # Project distribution (Top 10)
        stmt_proj_jobs = (
            select(BlueprintJobModel.project_instance_id, ProjectInstanceModel.name, func.count(BlueprintJobModel.id))
            .outerjoin(ProjectInstanceModel, BlueprintJobModel.project_instance_id == ProjectInstanceModel.id)
            .group_by(BlueprintJobModel.project_instance_id, ProjectInstanceModel.name)
            .order_by(func.count(BlueprintJobModel.id).desc())
            .limit(10)
        )
        res_proj_jobs = await self._session.execute(stmt_proj_jobs)
        project_dist: list[AdminAIProjectUsageSchema] = [
            AdminAIProjectUsageSchema(
                project_id=str(pid),
                project_name=pname or "Unknown Project",
                synthesis_jobs_count=cnt,
                mentor_messages_count=0,
                total_transactions=cnt,
            )
            for pid, pname, cnt in res_proj_jobs.all()
        ]

        return AdminAIUsageResponseSchema(
            overall_volume=overall_vol,
            time_trend=time_trend,
            capability_breakdown=capability_breakdown,
            project_distribution=project_dist,
            outcome_distribution=counts,
            token_metering="UNMETERED / NOT PERSISTED",
            rate_limit_telemetry="NOT PERSISTED",
        )

    # ============================================================
    # AD13 — Admin Agent Executions
    # ============================================================

    async def list_ai_executions(
        self,
        *,
        status: str | None = None,
        job_type: str | None = None,
        project_id: uuid.UUID | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AdminAIExecutionsResponseSchema:
        """List canonical AI generation runs with filtering, pagination, and status summaries (AD13)."""
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        total = await self._blueprint_repo.count_platform_jobs(
            status=status, job_type=job_type, project_id=project_id
        )
        job_rows = await self._blueprint_repo.list_platform_jobs(
            status=status, job_type=job_type, project_id=project_id, limit=limit, offset=offset
        )
        counts = await self._blueprint_repo.get_job_counts_by_status()

        summary = AdminAIExecutionsSummarySchema(
            total=sum(counts.values()),
            completed=counts.get("COMPLETED", 0),
            failed=counts.get("FAILED", 0),
            running=counts.get("RUNNING", 0),
            pending=counts.get("PENDING", 0),
        )

        executions: list[AdminAIExecutionItemSchema] = []
        for job, proj_name in job_rows:
            dur = None
            if job.started_at and job.completed_at and job.completed_at >= job.started_at:
                dur = int((job.completed_at - job.started_at).total_seconds())

            sanitized_err = None
            if job.error:
                sanitized_err = job.error.splitlines()[0][:250]

            cap = "Blueprint Engine"
            if job.job_type == "TARGETED_RETRY":
                cap = "Blueprint Repair"

            executions.append(
                AdminAIExecutionItemSchema(
                    id=str(job.id),
                    source="blueprint_jobs",
                    project_instance_id=str(job.project_instance_id),
                    project_name=proj_name,
                    capability=cap,
                    job_type=job.job_type,
                    target_output=job.target_output,
                    status=job.status,
                    current_step=job.current_step,
                    progress_percent=job.progress_percent,
                    duration_seconds=dur,
                    error=sanitized_err,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    created_at=job.created_at,
                )
            )

        return AdminAIExecutionsResponseSchema(
            total=total,
            limit=limit,
            offset=offset,
            summary=summary,
            executions=executions,
        )

    # ============================================================
    # AD14 — Admin AI Trace Detail
    # ============================================================

    async def get_ai_trace_detail(self, execution_id: uuid.UUID | str) -> AdminAITraceDetailResponseSchema:
        """Reconstruct truthful partial multi-layer trace for an AI execution (AD14)."""
        exec_id_str = str(execution_id)
        stmt = (
            select(BlueprintJobModel, ProjectInstanceModel.name)
            .outerjoin(ProjectInstanceModel, BlueprintJobModel.project_instance_id == ProjectInstanceModel.id)
            .where(BlueprintJobModel.id == exec_id_str)
        )
        res = await self._session.execute(stmt)
        row = res.first()

        if not row:
            raise NotFoundException(
                f"AI Execution '{execution_id}' not found.", code="EXECUTION_NOT_FOUND"
            )

        job, proj_name = row

        dur = None
        if job.started_at and job.completed_at and job.completed_at >= job.started_at:
            dur = int((job.completed_at - job.started_at).total_seconds())

        sanitized_err = None
        if job.error:
            sanitized_err = job.error.splitlines()[0][:250]

        # Load linked blueprint
        stmt_bp = select(BlueprintModel).where(BlueprintModel.id == str(job.blueprint_id))
        res_bp = await self._session.execute(stmt_bp)
        blueprint = res_bp.scalars().first()

        # Build known canonical stages
        section_titles = {
            "project_profile": "Project Profile & Domain Context",
            "tech_stack": "Technology Stack & Architecture",
            "features": "Core Features & System Modules",
            "specifications": "Technical Specifications & Data Models",
            "mvp": "MVP Scope & Validation Criteria",
            "duration": "Timeline & Sprint Duration",
            "risks": "Technical Risks & Mitigations",
            "tasks": "Granular Work Breakdown",
            "milestones": "Stage Milestones & Gate Deliverables",
            "readme": "README & Setup Guide",
        }

        pipeline_stages: list[AdminAITracePipelineStageSchema] = []
        for idx, key in enumerate(CANONICAL_BLUEPRINT_SECTION_ORDER, start=1):
            title = section_titles.get(key.value, key.value.replace("_", " ").title())
            milestone_pct = idx * 10

            stage_status = "COMPLETED" if job.progress_percent >= milestone_pct else (
                "RUNNING" if job.status == "RUNNING" and job.progress_percent >= (milestone_pct - 10) else (
                    "FAILED" if job.status == "FAILED" and job.current_step == key.value else "PENDING"
                )
            )

            pipeline_stages.append(
                AdminAITracePipelineStageSchema(
                    stage_order=idx,
                    section_key=key.value,
                    title=title,
                    status=stage_status,
                    progress_milestone=milestone_pct,
                )
            )

        # QA result
        qa_result = None
        if blueprint and (blueprint.qa_score is not None or blueprint.qa_status != "PENDING"):
            fb = blueprint.qa_feedback or {}
            qa_result = AdminAITraceQAFeedbackSchema(
                qa_status=blueprint.qa_status,
                qa_score=blueprint.qa_score,
                summary=fb.get("summary", ""),
                evaluated_criteria=fb.get("evaluated_criteria", {}),
                issues=fb.get("issues", []),
                recommendations=fb.get("recommendations", []),
            )

        # Correlated domain events
        stmt_events = (
            select(DomainEventModel)
            .where(
                (DomainEventModel.resource_id == str(job.blueprint_id))
                | (DomainEventModel.project_instance_id == str(job.project_instance_id))
            )
            .order_by(DomainEventModel.occurred_at.asc())
            .limit(10)
        )
        res_events = await self._session.execute(stmt_events)
        domain_events = [
            AdminAITraceDomainEventSchema(
                id=str(e.id),
                event_type=e.event_type,
                status=e.status,
                correlation_id=e.correlation_id or "",
                occurred_at=e.occurred_at,
            )
            for e in res_events.scalars().all()
        ]

        return AdminAITraceDetailResponseSchema(
            id=str(job.id),
            blueprint_id=str(job.blueprint_id),
            project_instance_id=str(job.project_instance_id),
            project_name=proj_name or "Unknown Project",
            student_id=str(blueprint.student_id) if blueprint else None,
            job_type=job.job_type,
            target_output=job.target_output,
            status=job.status,
            current_step=job.current_step,
            progress_percent=job.progress_percent,
            duration_seconds=dur,
            sanitized_error=sanitized_err,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
            pipeline_stages=pipeline_stages,
            qa_result=qa_result,
            domain_events=domain_events,
        )

    # ============================================================
    # AD15 — Admin AI Quality
    # ============================================================

    async def get_ai_quality(self) -> AdminAIQualityResponseSchema:
        """Aggregate authoritative QA Judge scores, criteria dimensions, and issues (AD15)."""
        stmt_bps = select(BlueprintModel).where(
            (BlueprintModel.qa_score.isnot(None)) | (BlueprintModel.qa_status != "PENDING")
        )
        res_bps = await self._session.execute(stmt_bps)
        evaluated_bps = res_bps.scalars().all()

        total = len(evaluated_bps)
        passed = sum(1 for b in evaluated_bps if b.qa_status == "PASS")
        failed = sum(1 for b in evaluated_bps if b.qa_status in ("FAIL", "QA_REJECTED"))
        pending = sum(1 for b in evaluated_bps if b.qa_status == "PENDING")
        pass_rate = round((passed / total) * 100, 1) if total > 0 else None

        scores = [b.qa_score for b in evaluated_bps if b.qa_score is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else None
        min_score = min(scores) if scores else None
        max_score = max(scores) if scores else None

        # Score brackets
        r_0_49 = sum(1 for s in scores if s < 50)
        r_50_69 = sum(1 for s in scores if 50 <= s < 70)
        r_70_84 = sum(1 for s in scores if 70 <= s < 85)
        r_85_100 = sum(1 for s in scores if s >= 85)

        score_dist = AdminAIQualityScoreDistributionSchema(
            range_0_49=r_0_49,
            range_50_69=r_50_69,
            range_70_84=r_70_84,
            range_85_100=r_85_100,
        )

        # Criteria breakdown
        criteria_totals: dict[str, list[float]] = {}
        issues_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for b in evaluated_bps:
            fb = b.qa_feedback or {}
            eval_criteria = fb.get("evaluated_criteria", {})
            for crit_key, crit_val in eval_criteria.items():
                if isinstance(crit_val, (int, float)):
                    criteria_totals.setdefault(crit_key, []).append(float(crit_val))

            for issue in fb.get("issues", []):
                sec = issue.get("section", "general")
                sev = issue.get("severity", "MEDIUM")
                issues_map.setdefault((sec, sev), []).append(issue)

        criteria_averages = {
            k: round(sum(vals) / len(vals), 1)
            for k, vals in criteria_totals.items()
            if vals
        }

        top_issues: list[AdminAIQualityTopIssueSchema] = []
        for (sec, sev), issue_list in sorted(issues_map.items(), key=lambda x: len(x[1]), reverse=True)[:8]:
            sample = issue_list[0]
            top_issues.append(
                AdminAIQualityTopIssueSchema(
                    section=sec,
                    severity=sev,
                    count=len(issue_list),
                    sample_description=sample.get("description", "Issue identified by QA Judge"),
                    recommendation=sample.get("recommendation", "Review and regenerate section"),
                )
            )

        # Approval conversion: passed blueprints approved
        approved_count = sum(1 for b in evaluated_bps if b.approved_at is not None)
        approval_conversion = round((approved_count / passed) * 100, 1) if passed > 0 else None

        return AdminAIQualityResponseSchema(
            total_evaluated=total,
            passed_count=passed,
            failed_count=failed,
            pending_count=pending,
            pass_rate_percent=pass_rate,
            average_qa_score=avg_score,
            min_qa_score=min_score,
            max_qa_score=max_score,
            score_distribution=score_dist,
            criteria_averages=criteria_averages,
            top_issues=top_issues,
            approval_conversion_rate=approval_conversion,
        )

    # ============================================================
    # AD16 — Admin AI Cost & Usage
    # ============================================================

    async def get_ai_cost(self) -> AdminAICostResponseSchema:
        """Capacity and execution volume proxy accounting (AD16)."""
        settings = get_settings()

        counts = await self._blueprint_repo.get_job_counts_by_status()
        total_bp_jobs = sum(counts.values())

        stmt_m = select(func.count(AIMentorMessageModel.id)).where(AIMentorMessageModel.role == "assistant")
        mentor_msgs = (await self._session.execute(stmt_m)).scalar() or 0

        stmt_c = select(func.count(ProjectChangeRequestModel.id))
        change_reqs = (await self._session.execute(stmt_c)).scalar() or 0

        total_vol = total_bp_jobs + mentor_msgs + change_reqs

        models = list(dict.fromkeys([
            settings.ai.DEFAULT_MODEL,
            settings.ai.STANDARD_MODEL,
            settings.ai.FAST_MODEL,
            settings.ai.REASONING_MODEL,
            settings.ai.FALLBACK_MODEL,
        ]))

        return AdminAICostResponseSchema(
            execution_volume_total=total_vol,
            blueprint_jobs_count=total_bp_jobs,
            ai_mentor_messages_count=mentor_msgs,
            change_analyses_count=change_reqs,
            active_models=models,
            provider="OpenRouter",
            billing_model="DIRECT_PROVIDER_BILLED — OPENROUTER",
            cost_telemetry_state="UNMETERED / NOT PERSISTED",
            token_metering_state="UNMETERED / NOT PERSISTED",
            disclaimer="OpenRouter billing is managed upstream via external provider accounts. Per-token accounting tables and dollar pricing schedules are not configured in the current database schema.",
        )

    # ============================================================
    # AD17 — Admin Cost Breakdown
    # ============================================================

    async def get_ai_cost_dimension(self, dimension: str) -> AdminAICostDimensionResponseSchema:
        """Usage volume breakdown along canonical dimensions: agent, project, time, status (AD17)."""
        dim = dimension.lower().strip()
        supported = ("agent", "project", "time", "status")
        if dim not in supported:
            raise NotFoundException(
                f"Cost breakdown dimension '{dimension}' not found. Supported dimensions: {', '.join(supported)}.",
                code="DIMENSION_NOT_FOUND",
            )

        counts = await self._blueprint_repo.get_job_counts_by_status()
        total_bp_jobs = sum(counts.values())

        stmt_m = select(func.count(AIMentorMessageModel.id)).where(AIMentorMessageModel.role == "assistant")
        mentor_msgs = (await self._session.execute(stmt_m)).scalar() or 0

        stmt_c = select(func.count(ProjectChangeRequestModel.id))
        change_reqs = (await self._session.execute(stmt_c)).scalar() or 0

        total_tx = total_bp_jobs + mentor_msgs + change_reqs

        if dim == "agent":
            stmt_types = select(BlueprintJobModel.job_type, func.count(BlueprintJobModel.id)).group_by(BlueprintJobModel.job_type)
            res_types = await self._session.execute(stmt_types)
            job_types = dict(res_types.all())

            items = [
                AdminAICostDimensionItemSchema(
                    key="blueprint_generation",
                    label="Blueprint Master Generation",
                    execution_count=job_types.get("FULL_GENERATION", 0),
                    percentage=round((job_types.get("FULL_GENERATION", 0) / total_tx) * 100, 1) if total_tx > 0 else 0.0,
                    detail="10-output sequential architectural synthesis",
                ),
                AdminAICostDimensionItemSchema(
                    key="blueprint_repair",
                    label="Blueprint Targeted Repair",
                    execution_count=job_types.get("TARGETED_RETRY", 0),
                    percentage=round((job_types.get("TARGETED_RETRY", 0) / total_tx) * 100, 1) if total_tx > 0 else 0.0,
                    detail="Targeted section recovery runs",
                ),
                AdminAICostDimensionItemSchema(
                    key="ai_mentor",
                    label="AI Mentor Supervisory Assistant",
                    execution_count=mentor_msgs,
                    percentage=round((mentor_msgs / total_tx) * 100, 1) if total_tx > 0 else 0.0,
                    detail="Contextual dialogue and advisory responses",
                ),
                AdminAICostDimensionItemSchema(
                    key="change_analyzer",
                    label="Project Change Impact Analyzer",
                    execution_count=change_reqs,
                    percentage=round((change_reqs / total_tx) * 100, 1) if total_tx > 0 else 0.0,
                    detail="Regeneration impact analyses",
                ),
            ]
            return AdminAICostDimensionResponseSchema(
                dimension="agent",
                title="Execution Volume by AI Capability / Agent",
                metric_type="EXECUTION_VOLUME",
                total_volume=total_tx,
                items=items,
            )

        elif dim == "project":
            stmt_proj = (
                select(BlueprintJobModel.project_instance_id, ProjectInstanceModel.name, func.count(BlueprintJobModel.id))
                .outerjoin(ProjectInstanceModel, BlueprintJobModel.project_instance_id == ProjectInstanceModel.id)
                .group_by(BlueprintJobModel.project_instance_id, ProjectInstanceModel.name)
                .order_by(func.count(BlueprintJobModel.id).desc())
                .limit(20)
            )
            res_proj = await self._session.execute(stmt_proj)
            items = [
                AdminAICostDimensionItemSchema(
                    key=str(pid),
                    label=pname or "Unknown Project",
                    execution_count=cnt,
                    percentage=round((cnt / total_bp_jobs) * 100, 1) if total_bp_jobs > 0 else 0.0,
                    detail="Project instance synthesis volume",
                )
                for pid, pname, cnt in res_proj.all()
            ]
            return AdminAICostDimensionResponseSchema(
                dimension="project",
                title="Execution Volume by Project Instance",
                metric_type="EXECUTION_VOLUME",
                total_volume=total_bp_jobs,
                items=items,
            )

        elif dim == "time":
            stmt_time = (
                select(BlueprintJobModel.created_at)
                .order_by(BlueprintJobModel.created_at.asc())
            )
            res_time = await self._session.execute(stmt_time)
            dates: dict[str, int] = {}
            for c in res_time.scalars().all():
                if c:
                    d_str = c.strftime("%Y-%m-%d")
                    dates[d_str] = dates.get(d_str, 0) + 1

            items = [
                AdminAICostDimensionItemSchema(
                    key=d,
                    label=d,
                    execution_count=cnt,
                    percentage=round((cnt / total_bp_jobs) * 100, 1) if total_bp_jobs > 0 else 0.0,
                    detail=f"{cnt} recorded generation runs",
                )
                for d, cnt in sorted(dates.items())
            ]
            return AdminAICostDimensionResponseSchema(
                dimension="time",
                title="Execution Volume by Date",
                metric_type="EXECUTION_VOLUME",
                total_volume=total_bp_jobs,
                items=items,
            )

        else:  # status
            items = [
                AdminAICostDimensionItemSchema(
                    key=st,
                    label=st.replace("_", " ").title(),
                    execution_count=cnt,
                    percentage=round((cnt / total_bp_jobs) * 100, 1) if total_bp_jobs > 0 else 0.0,
                    detail=f"{cnt} jobs in {st} status",
                )
                for st, cnt in sorted(counts.items())
            ]
            return AdminAICostDimensionResponseSchema(
                dimension="status",
                title="Execution Volume by Status",
                metric_type="EXECUTION_VOLUME",
                total_volume=total_bp_jobs,
                items=items,
            )

    # ============================================================
    # AD18 — Admin API Key Pool Monitoring
    # ============================================================

    async def get_ai_keys(self) -> AdminAIKeysResponseSchema:
        """Inspect safe OpenRouter key pool slots and rotation posture (AD18)."""
        settings = get_settings()

        key_slots_raw = [
            (1, "OPENROUTER_API_KEY_1", settings.ai.OPENROUTER_API_KEY_1),
            (2, "OPENROUTER_API_KEY_2", settings.ai.OPENROUTER_API_KEY_2),
            (3, "OPENROUTER_API_KEY_3", settings.ai.OPENROUTER_API_KEY_3),
            (4, "OPENROUTER_API_KEY_4", settings.ai.OPENROUTER_API_KEY_4),
            (5, "OPENROUTER_API_KEY_5", settings.ai.OPENROUTER_API_KEY_5),
        ]

        slots: list[AdminAIKeySlotSchema] = []
        configured_count = 0

        for idx, env_name, val in key_slots_raw:
            is_configured = bool(val and not val.startswith("your-"))
            if is_configured:
                configured_count += 1
                status = "CONFIGURED"
                posture = "ACTIVE_IN_ROTATION"
                # Safe masking: show prefix sk-or- and last 4 chars, with dots in between
                clean_val = val.strip()
                if len(clean_val) >= 12:
                    masked = f"{clean_val[:6]}••••••••••••••••{clean_val[-4:]}"
                else:
                    masked = "••••••••••••••••"
            else:
                status = "NOT_CONFIGURED"
                posture = "UNCONFIGURED"
                masked = None

            slots.append(
                AdminAIKeySlotSchema(
                    slot_index=idx,
                    slot_label=f"OpenRouter Key Slot {idx}",
                    env_var_name=env_name,
                    status=status,
                    provider="OpenRouter",
                    masked_identifier=masked,
                    rotation_posture=posture,
                )
            )

        return AdminAIKeysResponseSchema(
            provider="OpenRouter",
            gateway_base_url=settings.ai.OPENROUTER_BASE_URL,
            total_slots=5,
            configured_key_count=configured_count,
            rotation_mechanism="In-Memory Round-Robin",
            rotation_runtime_state="RUNTIME_IN_MEMORY",
            slots=slots,
            security_notice=(
                "Raw API keys, authorization headers, and environment secrets are strictly redacted. "
                "Key rotation index is managed in runtime memory across configured environment slots. "
                "Individual key rate-limit, cooldown, and historical health telemetry is not persisted in the current gateway."
            ),
        )


