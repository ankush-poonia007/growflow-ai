"""
GrowFlow Phase 7 Batch 9 — Tests for Admin Documents, RAG & Platform Analytics APIs.

Validates:
- AD21: GET /api/v1/admin/documents
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin with pagination, search, doc_type filtering
- AD22: GET /api/v1/admin/documents/rag
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin returning truthful deferred integration status
- AD23: GET /api/v1/admin/documents/generation
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin returning generation runs from blueprint_jobs
- AD28: GET /api/v1/admin/analytics
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin returning macro telemetry and phase/health distributions
- AD29: GET /api/v1/admin/analytics/{dimension}
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for valid dimensions: projects, users, documents, activity
  - 404 Not Found for invalid dimensions
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
import uuid

from fastapi.testclient import TestClient
import pytest

from backend.app.api.dependencies.auth import get_current_user
from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_admin_service
from backend.app.api.schemas.admin import (
    AdminAnalyticsDimensionDetailSchema,
    AdminAnalyticsOverviewMetricsSchema,
    AdminDocumentItemSchema,
    AdminDocumentsResponseSchema,
    AdminGenerationJobItemSchema,
    AdminGenerationJobsResponseSchema,
    AdminGenerationJobsSummarySchema,
    AdminPlatformAnalyticsResponseSchema,
    AdminRAGDiagnosticsSchema,
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
# AD21 — Documents Inventory Tests
# ---------------------------------------------------------------------------

def test_admin_documents_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/documents")
    assert res.status_code == 401


def test_admin_documents_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/documents")
    assert res.status_code == 403


def test_admin_documents_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/documents")
    assert res.status_code == 403


def test_admin_documents_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    doc_id = str(uuid.uuid4())
    proj_id = str(uuid.uuid4())
    mock_service.list_platform_documents.return_value = AdminDocumentsResponseSchema(
        total=1,
        limit=50,
        offset=0,
        summary={"BLUEPRINT": 1},
        documents=[
            AdminDocumentItemSchema(
                id=doc_id,
                project_instance_id=proj_id,
                project_name="AI Campus Hub",
                document_key="master_blueprint",
                title="Master Architecture Blueprint",
                doc_type="BLUEPRINT",
                format="markdown",
                version="1.0",
                status="ACTIVE",
                source="BLUEPRINT_INIT",
                size_bytes=2048,
                created_at=now,
                updated_at=now,
            )
        ],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/documents?doc_type=BLUEPRINT&limit=25&offset=0")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert len(body["data"]["documents"]) == 1
    doc = body["data"]["documents"][0]
    assert doc["title"] == "Master Architecture Blueprint"
    assert doc["project_name"] == "AI Campus Hub"
    assert doc["size_bytes"] == 2048


# ---------------------------------------------------------------------------
# AD22 — RAG Monitoring Diagnostics Tests
# ---------------------------------------------------------------------------

def test_admin_rag_diagnostics_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/documents/rag")
    assert res.status_code == 401


def test_admin_rag_diagnostics_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/documents/rag")
    assert res.status_code == 403


def test_admin_rag_diagnostics_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_rag_diagnostics.return_value = AdminRAGDiagnosticsSchema(
        status="DEFERRED_INTEGRATION",
        vector_store_type="NONE_CONFIGURED",
        embedding_model="openai/text-embedding-3-small",
        target_chunk_size=1000,
        target_chunk_overlap=150,
        target_top_k=8,
        index_generated_documents=True,
        eligible_documents_count=15,
        disclaimer="Vector database integration is deferred in Gate 09. Document chunking and embedding storage are currently inactive.",
        recent_events=[],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/documents/rag")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["status"] == "DEFERRED_INTEGRATION"
    assert body["data"]["vector_store_type"] == "NONE_CONFIGURED"
    assert body["data"]["target_chunk_size"] == 1000
    assert "apiKey" not in str(body)
    assert "secret" not in str(body)


# ---------------------------------------------------------------------------
# AD23 — Document Generation Runs Tests
# ---------------------------------------------------------------------------

def test_admin_generation_jobs_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/documents/generation")
    assert res.status_code == 401


def test_admin_generation_jobs_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/documents/generation")
    assert res.status_code == 403


def test_admin_generation_jobs_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    job_id = str(uuid.uuid4())
    mock_service.list_generation_jobs.return_value = AdminGenerationJobsResponseSchema(
        total=1,
        limit=50,
        offset=0,
        summary=AdminGenerationJobsSummarySchema(
            total=1,
            completed=1,
            failed=0,
            running=0,
            pending=0,
            average_duration_seconds=42.5,
        ),
        jobs=[
            AdminGenerationJobItemSchema(
                id=job_id,
                blueprint_id=str(uuid.uuid4()),
                project_instance_id=str(uuid.uuid4()),
                project_name="IoT Health Tracker",
                job_type="FULL_GENERATION",
                target_output="master_blueprint",
                status="COMPLETED",
                current_step="completed",
                progress_percent=100,
                error=None,
                duration_seconds=42,
                started_at=now,
                completed_at=now,
                created_at=now,
            )
        ],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/documents/generation?status=COMPLETED")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert body["data"]["summary"]["completed"] == 1
    assert body["data"]["jobs"][0]["status"] == "COMPLETED"
    assert body["data"]["jobs"][0]["duration_seconds"] == 42


# ---------------------------------------------------------------------------
# AD28 — Platform Analytics Overview Tests
# ---------------------------------------------------------------------------

def test_admin_analytics_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/analytics")
    assert res.status_code == 401


def test_admin_analytics_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/analytics")
    assert res.status_code == 403


def test_admin_analytics_success(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_platform_analytics.return_value = AdminPlatformAnalyticsResponseSchema(
        overview=AdminAnalyticsOverviewMetricsSchema(
            total_users=100,
            total_students=85,
            total_mentors=15,
            total_groups=10,
            active_groups=8,
            total_projects=35,
            active_projects=28,
            completed_projects=5,
            at_risk_projects=2,
            total_definitions=12,
            total_documents=64,
            total_generation_jobs=30,
            total_domain_events=450,
            total_help_requests=18,
        ),
        project_phase_distribution={"IDEA": 5, "EXECUTION": 20, "COMPLETED": 5},
        project_health_distribution={"HEALTHY": 28, "WARNING": 2, "CRITICAL": 0},
        user_status_distribution={"ACTIVE": 95, "INACTIVE": 5},
        task_status_distribution={"TODO": 50, "IN_PROGRESS": 30, "DONE": 120},
        document_type_distribution={"BLUEPRINT": 30, "SPECIFICATION": 20, "README": 14},
        generation_job_distribution={"COMPLETED": 28, "FAILED": 2},
        help_request_status_distribution={"OPEN": 4, "RESOLVED": 14},
        activity_volume_recent=120,
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/analytics")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["overview"]["total_users"] == 100
    assert body["data"]["project_phase_distribution"]["EXECUTION"] == 20
    assert body["data"]["activity_volume_recent"] == 120


# ---------------------------------------------------------------------------
# AD29 — Analytics Dimension Detail Tests
# ---------------------------------------------------------------------------

def test_admin_analytics_dimension_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/analytics/projects")
    assert res.status_code == 401


def test_admin_analytics_dimension_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/analytics/projects")
    assert res.status_code == 403


@pytest.mark.parametrize("dim", ["projects", "users", "documents", "activity"])
def test_admin_analytics_valid_dimensions(client: TestClient, app, admin_user, dim: str):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_analytics_dimension_detail.return_value = AdminAnalyticsDimensionDetailSchema(
        dimension=dim,
        title=f"{dim.capitalize()} Analytics",
        description=f"Detailed telemetry for {dim}.",
        summary={"count": 10},
        breakdown=[{"category": "test", "count": 10}],
        recent_records=[],
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get(f"/api/v1/admin/analytics/{dim}")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["dimension"] == dim


def test_admin_analytics_invalid_dimension_404(client: TestClient, app, admin_user):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_analytics_dimension_detail.side_effect = NotFoundException(
        "Analytics dimension 'invalid_dim' is not recognized. Valid dimensions: projects, users, documents, activity",
        code="ANALYTICS_DIMENSION_NOT_FOUND",
    )

    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/analytics/invalid_dim")
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ANALYTICS_DIMENSION_NOT_FOUND"


# ---------------------------------------------------------------------------
# Direct AdminService Batch 9 Execution Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_service_rag_diagnostics_live():
    mock_session = AsyncMock()
    mock_outbox = AsyncMock()
    mock_outbox.list_platform_events.return_value = []
    service = AdminService(
        session=mock_session,
        user_repo=AsyncMock(),
        profile_repo=AsyncMock(),
        group_repo=AsyncMock(),
        project_repo=AsyncMock(),
        technology_repo=AsyncMock(),
        outbox_repo=mock_outbox,
        document_repo=AsyncMock(),
        blueprint_repo=AsyncMock(),
    )
    # mock session execute for eligible documents count
    mock_res = MagicMock()
    mock_res.scalar.return_value = 10
    mock_session.execute.return_value = mock_res

    rag = await service.get_rag_diagnostics()
    assert isinstance(rag, AdminRAGDiagnosticsSchema)
    assert rag.status == "DEFERRED_INTEGRATION"
    assert rag.vector_store_type == "NONE_CONFIGURED"
    assert rag.eligible_documents_count == 10


@pytest.mark.asyncio
async def test_admin_service_documents_listing_live():
    mock_session = AsyncMock()
    mock_doc_repo = AsyncMock()
    now = datetime.now(UTC)
    mock_doc = AsyncMock()
    mock_doc.id = uuid.uuid4()
    mock_doc.project_instance_id = uuid.uuid4()
    mock_doc.document_key = "spec_key"
    mock_doc.title = "Tech Spec"
    mock_doc.doc_type = "SPECIFICATION"
    mock_doc.format = "markdown"
    mock_doc.version = "1.0"
    mock_doc.status = "ACTIVE"
    mock_doc.source = "BLUEPRINT_INIT"
    mock_doc.content = "Sample content string"
    mock_doc.created_at = now
    mock_doc.updated_at = now

    mock_doc_repo.count_platform_documents.return_value = 1
    mock_doc_repo.list_platform_documents.return_value = [(mock_doc, "Smart Home Hub")]

    # summary query mock
    mock_res = MagicMock()
    mock_res.all.return_value = [("SPECIFICATION", 1)]
    mock_session.execute.return_value = mock_res

    service = AdminService(
        session=mock_session,
        user_repo=AsyncMock(),
        profile_repo=AsyncMock(),
        group_repo=AsyncMock(),
        project_repo=AsyncMock(),
        technology_repo=AsyncMock(),
        document_repo=mock_doc_repo,
    )

    docs = await service.list_platform_documents(limit=10, offset=0)
    assert isinstance(docs, AdminDocumentsResponseSchema)
    assert docs.total == 1
    assert len(docs.documents) == 1
    assert docs.documents[0].project_name == "Smart Home Hub"
    assert docs.documents[0].size_bytes == len("Sample content string")

