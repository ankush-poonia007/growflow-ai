"""
GrowFlow S05 Gate 2 — PostgreSQL Row-Level Concurrency Integration Tests.

These tests run against a real PostgreSQL database instance that honors
SELECT ... FOR UPDATE row-level locking semantics.

They verify:
1. Same-student concurrent selection:
   Two genuinely independent database transactions attempting to select
   the same definition for the same student concurrently.
   Exactly one transaction succeeds (creates project instance, profile, outbox event).
   Exactly one transaction is serialized, detects duplicate active instance, and raises 409 (PROJECT_ALREADY_SELECTED).
   Zero orphan or partial records exist.

2. Different-student concurrent selection:
   Two genuinely independent database transactions for two different students
   selecting the same definition concurrently.
   Both transactions succeed without blocking each other globally on the mentor definition.
   Both instances are pinned to the active version snapshot.

SAFETY:
- All test entities use uniquely generated UUIDs.
- Full teardown cleanup is executed in finally blocks.
- Tests are skipped automatically if DATABASE_URL is not configured.
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid

import pytest
from sqlalchemy import select, text

from backend.app.application.services.outbox_service import OutboxService
from backend.app.application.services.project_definition_service import (
    ProjectDefinitionService,
)
from backend.app.config.settings import DatabaseSettings
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectDefinitionStatus,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.infrastructure.database.engine import (
    build_async_engine,
    build_async_session_factory,
)
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
    ProjectInstanceModel,
    ProjectProfileModel,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository
from backend.app.infrastructure.repositories.project_definition_repository import (
    ProjectDefinitionRepository,
)
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import ConflictException

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def _resolve_database_url() -> str | None:
    url = os.environ.get("DATABASE_URL") or os.environ.get("ALEMBIC_DATABASE_URL")
    if not url:
        try:
            from backend.app.config import get_settings

            url = get_settings().database.DATABASE_URL
        except Exception:
            pass
    return url


_DATABASE_URL = _resolve_database_url()
pytestmark = pytest.mark.skipif(
    not _DATABASE_URL,
    reason="DATABASE_URL not set — skipping live PostgreSQL concurrency integration tests",
)


def _make_concurrency_db_settings() -> DatabaseSettings:
    """Create DatabaseSettings configured for concurrent sessions against live PostgreSQL."""
    return DatabaseSettings(
        DATABASE_URL=_DATABASE_URL,
        POOL_SIZE=5,
        MAX_OVERFLOW=5,
        POOL_TIMEOUT_SECONDS=15,
        POOL_RECYCLE_SECONDS=300,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_same_student_concurrent_selection_postgresql() -> None:
    """
    PROVE: Under real PostgreSQL row-level SELECT ... FOR UPDATE locking,
    two independent concurrent transactions selecting the same definition for the
    SAME student result in exactly ONE success and exactly ONE 409 Conflict.
    """
    settings = _make_concurrency_db_settings()
    engine = build_async_engine(settings)
    factory = build_async_session_factory(engine)

    mentor_id = uuid.uuid4()
    student_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()

    created_project_ids: list[str] = []

    try:
        # 1. Setup test fixture entities
        async with factory() as setup_session:
            mentor_user = UserModel(
                id=str(mentor_id),
                email=f"mentor_{mentor_id}@example.com",
                role=UserRole.MENTOR.value,
                status=AccountStatus.ACTIVE.value,
            )
            student_user = UserModel(
                id=str(student_id),
                email=f"student_{student_id}@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
            )
            setup_session.add_all([mentor_user, student_user])
            await setup_session.flush()

            definition = ProjectDefinitionModel(
                id=str(def_id),
                owner_mentor_id=str(mentor_id),
                name="PostgreSQL Same-Student Concurrency Definition",
                status=ProjectDefinitionStatus.ACTIVE.value,
                current_version_id=str(ver_id),
            )
            version = ProjectDefinitionVersionModel(
                id=str(ver_id),
                project_definition_id=str(def_id),
                version_number=1,
                name="PostgreSQL Same-Student Concurrency Definition v1",
                problem="Concurrent student selection race condition",
                proposed_solution="PostgreSQL SELECT ... FOR UPDATE student row locking",
                complexity=ProjectComplexity.INTERMEDIATE.value,
                description="Testing row lock serialization across independent sessions",
                constraints="PostgreSQL dialect required",
                assumptions="Row lock blocks concurrent reader-writers on student tuple",
                technology_snapshot=[{"name": "PostgreSQL", "version": "17"}],
                created_by=str(mentor_id),
            )
            setup_session.add_all([definition, version])
            await setup_session.commit()

        # 2. Concurrently execute selection from two independent sessions
        async def attempt_select(worker_id: int):
            async with factory() as session:
                def_repo = ProjectDefinitionRepository(session)
                proj_repo = ProjectRepository(session)
                outbox_repo = OutboxRepository(session)
                outbox_svc = OutboxService(outbox_repo)
                service = ProjectDefinitionService(def_repo, proj_repo, outbox_svc)

                try:
                    instance = await service.select_definition(
                        definition_id=def_id,
                        student_id=student_id,
                        correlation_id=f"corr-same-{worker_id}",
                    )
                    await session.commit()
                    return ("SUCCESS", str(instance.id), worker_id)
                except ConflictException as exc:
                    await session.rollback()
                    return ("CONFLICT", exc.code, exc.status_code, worker_id)
                except Exception as exc:
                    await session.rollback()
                    return ("ERROR", str(exc), worker_id)

        results = await asyncio.gather(
            attempt_select(1),
            attempt_select(2),
        )

        successes = [r for r in results if r[0] == "SUCCESS"]
        conflicts = [r for r in results if r[0] == "CONFLICT"]

        # Exactly 1 success and exactly 1 conflict
        assert len(successes) == 1, f"Expected exactly 1 SUCCESS, got {len(successes)}: {results}"
        assert len(conflicts) == 1, f"Expected exactly 1 CONFLICT, got {len(conflicts)}: {results}"

        # Conflict must have canonical error code and 409 status code
        assert conflicts[0][1] == "PROJECT_ALREADY_SELECTED"
        assert conflicts[0][2] == 409

        successful_project_id = successes[0][1]
        created_project_ids.append(successful_project_id)

        # 3. Verify database state
        async with factory() as verify_session:
            # Exactly 1 active ProjectInstance
            inst_result = await verify_session.execute(
                select(ProjectInstanceModel).where(
                    ProjectInstanceModel.student_id == str(student_id),
                    ProjectInstanceModel.project_definition_id == str(def_id),
                )
            )
            instances = inst_result.scalars().all()
            assert len(instances) == 1
            instance = instances[0]
            assert instance.id == successful_project_id
            assert instance.status == ProjectStatus.ACTIVE.value
            assert instance.current_phase == ProjectPhase.IDEA.value
            assert instance.health == ProjectHealth.HEALTHY.value
            assert instance.source_definition_version_id == str(ver_id)

            # Exactly 1 ProjectProfile
            prof_result = await verify_session.execute(
                select(ProjectProfileModel).where(
                    ProjectProfileModel.project_instance_id == successful_project_id
                )
            )
            profiles = prof_result.scalars().all()
            assert len(profiles) == 1
            profile = profiles[0]
            assert profile.objective == "Testing row lock serialization across independent sessions"
            assert profile.constraints == "PostgreSQL dialect required"
            assert profile.assumptions == "Row lock blocks concurrent reader-writers on student tuple"
            assert profile.scope == "Concurrent student selection race condition"
            assert (
                profile.expected_outcome
                == "PostgreSQL SELECT ... FOR UPDATE student row locking"
            )

            # Exactly 1 DomainEvent
            event_result = await verify_session.execute(
                select(DomainEventModel).where(
                    DomainEventModel.project_instance_id == successful_project_id
                )
            )
            events = event_result.scalars().all()
            assert len(events) == 1
            event = events[0]
            assert event.event_type == DomainEventType.PROJECT_CREATED.value
            assert event.actor_role == "STUDENT"
            assert event.actor_id == str(student_id)
            assert event.metadata_json.get("selected_from_definition") is True
            assert event.metadata_json.get("project_definition_id") == str(def_id)
            assert event.metadata_json.get("version_number") == 1

    finally:
        # Teardown: clean up all inserted records
        async with factory() as cleanup_session:
            for pid in created_project_ids:
                await cleanup_session.execute(
                    text("DELETE FROM domain_events WHERE project_instance_id = :pid"),
                    {"pid": pid},
                )
                await cleanup_session.execute(
                    text("DELETE FROM project_profiles WHERE project_instance_id = :pid"),
                    {"pid": pid},
                )
                await cleanup_session.execute(
                    text("DELETE FROM project_instances WHERE id = :pid"),
                    {"pid": pid},
                )
            await cleanup_session.execute(
                text("DELETE FROM project_definition_versions WHERE project_definition_id = :did"),
                {"did": str(def_id)},
            )
            await cleanup_session.execute(
                text("DELETE FROM project_definitions WHERE id = :did"),
                {"did": str(def_id)},
            )
            await cleanup_session.execute(
                text("DELETE FROM users WHERE id IN (:mid, :sid)"),
                {"mid": str(mentor_id), "sid": str(student_id)},
            )
            await cleanup_session.commit()
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_different_students_concurrent_selection_postgresql() -> None:
    """
    PROVE: Under real PostgreSQL row-level locking, two different students selecting
    the SAME definition concurrently both succeed. The row lock is scoped to each student's
    row and does not block other students or serialize on the mentor definition globally.
    """
    settings = _make_concurrency_db_settings()
    engine = build_async_engine(settings)
    factory = build_async_session_factory(engine)

    mentor_id = uuid.uuid4()
    student_a_id = uuid.uuid4()
    student_b_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()

    created_project_ids: list[str] = []

    try:
        # 1. Setup test fixture entities
        async with factory() as setup_session:
            mentor_user = UserModel(
                id=str(mentor_id),
                email=f"mentor_{mentor_id}@example.com",
                role=UserRole.MENTOR.value,
                status=AccountStatus.ACTIVE.value,
            )
            student_a = UserModel(
                id=str(student_a_id),
                email=f"student_a_{student_a_id}@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
            )
            student_b = UserModel(
                id=str(student_b_id),
                email=f"student_b_{student_b_id}@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
            )
            setup_session.add_all([mentor_user, student_a, student_b])
            await setup_session.flush()

            definition = ProjectDefinitionModel(
                id=str(def_id),
                owner_mentor_id=str(mentor_id),
                name="PostgreSQL Multi-Student Concurrency Definition",
                status=ProjectDefinitionStatus.ACTIVE.value,
                current_version_id=str(ver_id),
            )
            version = ProjectDefinitionVersionModel(
                id=str(ver_id),
                project_definition_id=str(def_id),
                version_number=1,
                name="PostgreSQL Multi-Student Concurrency Definition v1",
                problem="Multi-student concurrent selection",
                proposed_solution="Per-student row locking without global definition contention",
                complexity=ProjectComplexity.INTERMEDIATE.value,
                description="Test non-blocking distinct student selections",
                created_by=str(mentor_id),
            )
            setup_session.add_all([definition, version])
            await setup_session.commit()

        # 2. Concurrently execute selection for both students from independent sessions
        async def execute_student_selection(sid: uuid.UUID):
            async with factory() as session:
                def_repo = ProjectDefinitionRepository(session)
                proj_repo = ProjectRepository(session)
                outbox_repo = OutboxRepository(session)
                outbox_svc = OutboxService(outbox_repo)
                service = ProjectDefinitionService(def_repo, proj_repo, outbox_svc)

                instance = await service.select_definition(
                    definition_id=def_id,
                    student_id=sid,
                    correlation_id=f"corr-diff-{sid}",
                )
                await session.commit()
                return (
                    "SUCCESS",
                    str(instance.id),
                    str(instance.student_id),
                    str(instance.source_definition_version_id),
                )

        results = await asyncio.gather(
            execute_student_selection(student_a_id),
            execute_student_selection(student_b_id),
        )

        assert len(results) == 2
        assert results[0][0] == "SUCCESS"
        assert results[1][0] == "SUCCESS"

        id_a, id_b = results[0][1], results[1][1]
        assert id_a != id_b, "Project instance IDs must be distinct"
        created_project_ids.extend([id_a, id_b])

        # Both instances are pinned to exact active version
        assert results[0][3] == str(ver_id)
        assert results[1][3] == str(ver_id)

        # 3. Check DB state
        async with factory() as verify_session:
            inst_res = await verify_session.execute(
                select(ProjectInstanceModel).where(
                    ProjectInstanceModel.project_definition_id == str(def_id)
                )
            )
            instances = inst_res.scalars().all()
            assert len(instances) == 2, f"Expected 2 instances in DB, got {len(instances)}"

            student_ids_in_db = {i.student_id for i in instances}
            assert student_ids_in_db == {str(student_a_id), str(student_b_id)}

            for inst in instances:
                assert inst.status == ProjectStatus.ACTIVE.value
                assert inst.source_definition_version_id == str(ver_id)

            # Both profiles exist
            prof_res = await verify_session.execute(
                select(ProjectProfileModel).where(
                    ProjectProfileModel.project_instance_id.in_(created_project_ids)
                )
            )
            profiles = prof_res.scalars().all()
            assert len(profiles) == 2

            # Both domain events exist
            event_res = await verify_session.execute(
                select(DomainEventModel).where(
                    DomainEventModel.project_instance_id.in_(created_project_ids)
                )
            )
            events = event_res.scalars().all()
            assert len(events) == 2
            for event in events:
                assert event.event_type == DomainEventType.PROJECT_CREATED.value
                assert event.metadata_json.get("selected_from_definition") is True

    finally:
        # Teardown: clean up all inserted records
        async with factory() as cleanup_session:
            if created_project_ids:
                for pid in created_project_ids:
                    await cleanup_session.execute(
                        text("DELETE FROM domain_events WHERE project_instance_id = :pid"),
                        {"pid": pid},
                    )
                    await cleanup_session.execute(
                        text("DELETE FROM project_profiles WHERE project_instance_id = :pid"),
                        {"pid": pid},
                    )
                    await cleanup_session.execute(
                        text("DELETE FROM project_instances WHERE id = :pid"),
                        {"pid": pid},
                    )
            await cleanup_session.execute(
                text("DELETE FROM project_definition_versions WHERE project_definition_id = :did"),
                {"did": str(def_id)},
            )
            await cleanup_session.execute(
                text("DELETE FROM project_definitions WHERE id = :did"),
                {"did": str(def_id)},
            )
            await cleanup_session.execute(
                text("DELETE FROM users WHERE id IN (:mid, :sa, :sb)"),
                {"mid": str(mentor_id), "sa": str(student_a_id), "sb": str(student_b_id)},
            )
            await cleanup_session.commit()
        await engine.dispose()
