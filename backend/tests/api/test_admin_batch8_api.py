"""
GrowFlow Phase 7 Batch 8 — Tests for Admin System Health, Security & Audit APIs.

Validates:
- AD19: GET /api/v1/admin/health
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role returning subsystems and pool metrics
- AD20: GET /api/v1/admin/health/{component_id}
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with component diagnostics
  - 404 Not Found for unknown component
- AD24: GET /api/v1/admin/security/overview
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with user posture and audit metrics
- AD25: GET /api/v1/admin/security/audit
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with pagination and filtering
- AD26: GET /api/v1/admin/security/investigations
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role returning governed inspection targets
- AD27: GET /api/v1/admin/security/investigations/{investigation_id}
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 404 Not Found for non-existent / unconfigured investigation ticket
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock
import uuid

from fastapi.testclient import TestClient
import pytest

from backend.app.api.dependencies.auth import get_current_user
from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_admin_service
from backend.app.api.schemas.admin import (
    AdminAuditEventItemSchema,
    AdminAuditLogResponseSchema,
    AdminAuditSummaryMetricsSchema,
    AdminInspectableResourceSchema,
    AdminInvestigationOverviewResponseSchema,
    AdminSecurityOverviewSchema,
    AdminSubsystemDetailSchema,
    AdminSubsystemSummarySchema,
    AdminSystemHealthMetricsSchema,
    AdminSystemHealthResponseSchema,
    AdminUserSecurityPostureSchema,
)
from backend.app.application.services.admin_service import AdminService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.shared.exceptions import NotFoundException


async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture(autouse=True)
def override_db(app):
    app.dependency_overrides[get_db_session] = _mock_db_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="admin@growflow.test",
        role=UserRole.ADMIN,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="mentor@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="student@growflow.test",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


# ---------------------------------------------------------------------------
# AD19 — System Health Tests
# ---------------------------------------------------------------------------

def test_admin_health_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/health")
    assert res.status_code == 401


def test_admin_health_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/health")
    assert res.status_code == 403


def test_admin_health_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/health")
    assert res.status_code == 403


def test_admin_health_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.get_system_health.return_value = AdminSystemHealthResponseSchema(
        overall_status="OPERATIONAL",
        environment="test",
        version="0.1.0",
        timestamp=now,
        subsystems=[
            AdminSubsystemSummarySchema(
                id="api",
                name="API Runtime Process",
                status="OPERATIONAL",
                type="CORE",
                details="FastAPI test runtime",
            ),
            AdminSubsystemSummarySchema(
                id="database",
                name="PostgreSQL Persistence",
                status="OPERATIONAL",
                type="DATABASE",
                details="Pool size: 5",
            ),
        ],
        metrics=AdminSystemHealthMetricsSchema(
            outbox_pending=0,
            outbox_failed=0,
            outbox_published=10,
            active_ai_keys=1,
            db_pool_size=5,
            db_connected=True,
        ),
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/health")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["overall_status"] == "OPERATIONAL"
    assert len(body["data"]["subsystems"]) == 2
    assert body["data"]["metrics"]["db_connected"] is True


@pytest.mark.asyncio
async def test_admin_health_real_service_storage_config():
    """Verify that AdminService.get_system_health executes without AttributeError on settings."""
    mock_session = AsyncMock()
    mock_outbox = AsyncMock()
    mock_outbox.get_counts_by_status.return_value = {
        "pending": 0,
        "published": 10,
        "failed": 0,
        "total": 10,
    }
    service = AdminService(
        session=mock_session,
        user_repo=AsyncMock(),
        profile_repo=AsyncMock(),
        group_repo=AsyncMock(),
        project_repo=AsyncMock(),
        technology_repo=AsyncMock(),
        outbox_repo=mock_outbox,
    )

    result = await service.get_system_health()
    assert isinstance(result, AdminSystemHealthResponseSchema)
    storage_subsystems = [s for s in result.subsystems if s.id == "storage"]
    assert len(storage_subsystems) == 1
    storage_sub = storage_subsystems[0]
    assert storage_sub.status in ("CONFIGURED", "UNCONFIGURED")
    assert storage_sub.type == "STORAGE"
    assert "Bucket:" in storage_sub.details


def test_admin_health_endpoint_real_service_live(client: TestClient, app, admin_user):
    """End-to-end endpoint verification: GET /api/v1/admin/health does not fail with HTTP 500."""
    mock_session = AsyncMock()
    mock_outbox = AsyncMock()
    mock_outbox.get_counts_by_status.return_value = {
        "pending": 0,
        "published": 10,
        "failed": 0,
        "total": 10,
    }
    real_service = AdminService(
        session=mock_session,
        user_repo=AsyncMock(),
        profile_repo=AsyncMock(),
        group_repo=AsyncMock(),
        project_repo=AsyncMock(),
        technology_repo=AsyncMock(),
        outbox_repo=mock_outbox,
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: real_service

    res = client.get("/api/v1/admin/health")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "subsystems" in body["data"]
    subsystem_ids = [s["id"] for s in body["data"]["subsystems"]]
    assert "storage" in subsystem_ids
    assert "api" in subsystem_ids
    assert "database" in subsystem_ids


@pytest.mark.asyncio
async def test_admin_component_detail_storage_real_service():
    """Verify AdminService.get_component_detail('storage') correctly reads settings.auth.STORAGE_BUCKET."""
    mock_session = AsyncMock()
    mock_outbox = AsyncMock()
    service = AdminService(
        session=mock_session,
        user_repo=AsyncMock(),
        profile_repo=AsyncMock(),
        group_repo=AsyncMock(),
        project_repo=AsyncMock(),
        technology_repo=AsyncMock(),
        outbox_repo=mock_outbox,
    )

    detail = await service.get_component_detail("storage")
    assert isinstance(detail, AdminSubsystemDetailSchema)
    assert detail.id == "storage"
    assert detail.type == "STORAGE"
    assert detail.status in ("CONFIGURED", "UNCONFIGURED")
    assert "bucket_name" in detail.configuration



# ---------------------------------------------------------------------------
# AD20 — Component Detail Tests
# ---------------------------------------------------------------------------

def test_admin_component_detail_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/health/database")
    assert res.status_code == 401


def test_admin_component_detail_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/health/database")
    assert res.status_code == 403


def test_admin_component_detail_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.get_component_detail.return_value = AdminSubsystemDetailSchema(
        id="database",
        name="PostgreSQL Persistence",
        status="OPERATIONAL",
        type="DATABASE",
        environment="test",
        checked_at=now,
        configuration={"pool_size": 5},
        diagnostics={"connectivity_confirmed": True},
        recent_failures=[],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/health/database")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["id"] == "database"
    assert body["data"]["status"] == "OPERATIONAL"


def test_admin_component_detail_unknown_404(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_component_detail.side_effect = NotFoundException(
        "Component 'non_existent' is not recognized.",
        code="COMPONENT_NOT_FOUND",
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/health/non_existent")
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "COMPONENT_NOT_FOUND"


# ---------------------------------------------------------------------------
# AD24 — Security & Audit Overview Tests
# ---------------------------------------------------------------------------

def test_admin_security_overview_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/security/overview")
    assert res.status_code == 401


def test_admin_security_overview_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/security/overview")
    assert res.status_code == 403


def test_admin_security_overview_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_security_overview.return_value = AdminSecurityOverviewSchema(
        user_posture=AdminUserSecurityPostureSchema(
            total_users=25,
            active_users=24,
            inactive_users=0,
            suspended_users=1,
            admin_count=2,
            mentor_count=5,
            student_count=18,
        ),
        audit_summary=AdminAuditSummaryMetricsSchema(
            total_events=120,
            outbox_delivery_failures=0,
        ),
        recent_security_relevant_events=[],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/security/overview")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["user_posture"]["suspended_users"] == 1
    assert body["data"]["audit_summary"]["total_events"] == 120


# ---------------------------------------------------------------------------
# AD25 — Audit Log Tests
# ---------------------------------------------------------------------------

def test_admin_audit_log_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/security/audit")
    assert res.status_code == 401


def test_admin_audit_log_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/security/audit")
    assert res.status_code == 403


def test_admin_audit_log_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.list_audit_log.return_value = AdminAuditLogResponseSchema(
        total=1,
        limit=50,
        offset=0,
        events=[
            AdminAuditEventItemSchema(
                id=str(uuid.uuid4()),
                event_type="ProjectCreated",
                title="Project Created",
                description="Project workspace initialized.",
                actor_id=str(uuid.uuid4()),
                actor_role="STUDENT",
                resource_type="project",
                resource_id=str(uuid.uuid4()),
                project_instance_id=str(uuid.uuid4()),
                group_id=str(uuid.uuid4()),
                correlation_id="corr-123",
                status="PUBLISHED",
                occurred_at=now,
                metadata={"title": "Demo Project"},
            )
        ],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/security/audit?limit=10&actor_role=STUDENT")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert body["data"]["events"][0]["event_type"] == "ProjectCreated"
    mock_service.list_audit_log.assert_called_once()


# ---------------------------------------------------------------------------
# AD26 — Investigation Requests (Governed Inspection) Tests
# ---------------------------------------------------------------------------

def test_admin_investigations_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/security/investigations")
    assert res.status_code == 401


def test_admin_investigations_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/security/investigations")
    assert res.status_code == 403


def test_admin_investigations_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_investigation_overview.return_value = AdminInvestigationOverviewResponseSchema(
        framework_status="GOVERNED_INSPECTION_ACTIVE",
        disclaimer="Governed Inspection Surface",
        total_flagged=1,
        flagged_resources=[
            AdminInspectableResourceSchema(
                resource_type="USER",
                resource_id=str(uuid.uuid4()),
                label="Suspended User",
                detail="Account suspended",
                flag_reason="ACCOUNT_SUSPENDED",
                flagged_at=datetime.now(UTC),
                canonical_inspection_url="/admin/students/123",
            )
        ],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/security/investigations")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["total_flagged"] == 1
    assert body["data"]["flagged_resources"][0]["flag_reason"] == "ACCOUNT_SUSPENDED"


# ---------------------------------------------------------------------------
# AD27 — Investigation Detail Tests
# ---------------------------------------------------------------------------

def test_admin_investigation_detail_unauthenticated(client: TestClient):
    res = client.get(f"/api/v1/admin/security/investigations/{uuid.uuid4()}")
    assert res.status_code == 401


def test_admin_investigation_detail_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get(f"/api/v1/admin/security/investigations/{uuid.uuid4()}")
    assert res.status_code == 403


def test_admin_investigation_detail_not_found(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_investigation_detail.side_effect = NotFoundException(
        "Investigation record not found. Note: Persistent investigation tickets are not configured in the current canonical schema.",
        code="INVESTIGATION_NOT_FOUND",
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    test_id = str(uuid.uuid4())
    res = client.get(f"/api/v1/admin/security/investigations/{test_id}")
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVESTIGATION_NOT_FOUND"
