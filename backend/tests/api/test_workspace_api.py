"""
GrowFlow Batch S15–S17 — API Tests for Student Project Workspace Foundation.

Covers:
1. S15 Project Overview:
   - Owner access returns 200 with canonical project identity, health, progress, assessment summary, and blueprint status.
   - Cross-student access returns 403 Forbidden.
   - Nonexistent project returns 404 Not Found.
   - Unauthenticated request returns 401 Unauthorized.
2. S16 Blueprint Workspace Sections:
   - Retrieving canonical sections (e.g. tech_stack, specifications) returns 200 with structured and markdown data.
   - Retrieving invalid section key returns 404 SECTION_NOT_FOUND.
   - Cross-student access returns 403 Forbidden.
3. S17 Blueprint Document Viewer & Download:
   - Retrieving document (e.g. readme, full) returns 200 with available_documents list and formatted Markdown.
   - Retrieving invalid document key returns 404 DOCUMENT_NOT_FOUND.
   - Raw markdown download returns 200 with Content-Disposition attachment header and text/markdown content type.
   - Cross-student download returns 403 Forbidden.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_blueprint_service, get_project_service
from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.application.services.project_service import ProjectService
from backend.app.domain.assessment.models import AssessmentStatus
from backend.app.domain.blueprint.models import (
    CANONICAL_BLUEPRINT_SECTION_ORDER,
    BlueprintQAStatus,
    BlueprintSectionKey,
    BlueprintStatus,
)
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.assessment import AssessmentModel, AssessmentResultModel
from backend.app.infrastructure.database.models.blueprint import BlueprintModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.assessment_repository import AssessmentRepository
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from collections.abc import Generator
    from backend.app.config.settings import Settings

_TEST_SECRET = "workspace-test-secret-at-least-32-chars-long-123"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_jwt(
    user_id: uuid.UUID,
    email: str = "test@example.com",
    role: str = "STUDENT",
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": _TEST_AUDIENCE,
        "iss": _TEST_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=3600)).timestamp()),
        "app_metadata": {"role": role},
    }
    return jwt.encode(payload, _TEST_SECRET, algorithm="HS256")


@pytest.fixture
def auth_settings(test_settings: Settings) -> Settings:
    test_settings.auth.JWT_SECRET = _TEST_SECRET
    test_settings.auth.JWT_AUDIENCE = _TEST_AUDIENCE
    test_settings.auth.JWT_ISSUER = _TEST_ISSUER
    test_settings.database.DATABASE_URL = None
    return test_settings


@pytest.fixture
def owner_student_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_student_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def project_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def owner_token(owner_student_id: uuid.UUID) -> str:
    return _make_jwt(owner_student_id, "owner@example.com", UserRole.STUDENT.value)


@pytest.fixture
def other_token(other_student_id: uuid.UUID) -> str:
    return _make_jwt(other_student_id, "other@example.com", UserRole.STUDENT.value)


@pytest.fixture
def sample_project(owner_student_id: uuid.UUID, project_id: uuid.UUID) -> ProjectInstanceModel:
    proj = ProjectInstanceModel()
    proj.id = str(project_id)
    proj.student_id = str(owner_student_id)
    proj.name = "Precision Agriculture Drone System"
    proj.problem = "Crop monitoring inefficiencies in large fields"
    proj.proposed_solution = "Autonomous multi-rotor drone with multispectral telemetry"
    proj.complexity = ProjectComplexity.INTERMEDIATE.value
    proj.current_phase = ProjectPhase.BLUEPRINT.value
    proj.health = ProjectHealth.HEALTHY.value
    proj.status = ProjectStatus.ACTIVE.value
    proj.progress_percentage = 35
    proj.project_definition_id = None
    proj.source_definition_version_id = None
    proj.group_id = None
    proj.deadline = datetime.now(UTC) + timedelta(days=45)
    proj.created_at = datetime.now(UTC)
    proj.updated_at = datetime.now(UTC)
    return proj


@pytest.fixture
def completed_assessment(project_id: uuid.UUID, owner_student_id: uuid.UUID) -> AssessmentModel:
    asm = AssessmentModel()
    asm.id = str(uuid.uuid4())
    asm.project_instance_id = str(project_id)
    asm.student_id = str(owner_student_id)
    asm.status = AssessmentStatus.COMPLETED.value
    asm.current_question_index = 15
    asm.total_questions = 15
    asm.started_at = datetime.now(UTC) - timedelta(minutes=15)
    asm.completed_at = datetime.now(UTC)
    asm.created_at = datetime.now(UTC) - timedelta(minutes=15)
    asm.updated_at = datetime.now(UTC)
    return asm


@pytest.fixture
def approved_blueprint(project_id: uuid.UUID, owner_student_id: uuid.UUID) -> BlueprintModel:
    bp = BlueprintModel()
    bp.id = str(uuid.uuid4())
    bp.project_instance_id = str(project_id)
    bp.student_id = str(owner_student_id)
    bp.status = BlueprintStatus.APPROVED.value
    bp.current_step = "COMPLETED"
    bp.progress_percent = 100
    bp.qa_status = BlueprintQAStatus.PASS.value
    bp.qa_score = 88
    bp.content = {
        "project_profile": {
            "problem": "Crop monitoring inefficiencies in large fields",
            "proposed_solution": "Autonomous multi-rotor drone with multispectral telemetry",
            "complexity": "INTERMEDIATE",
            "domain": "Precision Agriculture",
        },
        "tech_stack": {
            "stack": [
                {"category": "Backend", "technology": "FastAPI", "purpose": "Core Telemetry API", "why_selected": "High throughput async"},
                {"category": "Database", "technology": "PostgreSQL", "purpose": "Mission Store", "why_selected": "Relational integrity"},
            ]
        },
        "features": {
            "features": [
                {"id": "F01", "name": "Mission Planner", "priority": "P0", "description": "Waypoint generator", "acceptance_criteria": "Geofence containment"},
            ]
        },
        "specifications": {
            "api_specifications": [
                {
                    "endpoint": "/api/v1/missions",
                    "method": "POST",
                    "description": "Create flight mission",
                    "auth": "STUDENT",
                    "request_body": "{}",
                    "response": "{ mission_id: UUID }",
                }
            ],
            "data_models": ["MissionPlan (id, project_id, status)"],
        },
        "mvp": {
            "scope": "End to end mission flight plan and telemetry ingest.",
            "inclusions": ["Waypoint engine", "Telemetry storage"],
            "exclusions": ["Swarm coordination"],
            "success_metrics": ["0 geofence anomalies"],
        },
        "duration": {
            "total_estimated_weeks": 6,
            "contingency_buffer_days": 5,
            "timeline_phases": [
                {"phase": "Foundation", "duration_weeks": 2.0, "focus": "Schema & API"}
            ],
        },
        "risks": {
            "technical_risks": [
                {"id": "R01", "title": "Telemetry packet drop", "severity": "HIGH", "mitigation": "Exponential backoff"}
            ]
        },
        "tasks": {
            "tasks": [
                {"id": "T01", "name": "Implement mission boundary polygon check", "category": "Core"}
            ]
        },
        "milestones": {
            "milestones_schedule": [
                {"gate": "M1", "name": "Architecture Frozen", "deliverable": "Specs and models verified"}
            ]
        },
        "readme": {
            "title": "Precision Agriculture Drone System — Architecture Specs",
            "overview": "Production blueprint for autonomous UAV flight control.",
            "quickstart": "uvicorn backend.app.main:app",
            "architecture_summary": "Layered FastAPI architecture with transactional outbox.",
        },
    }
    bp.approved_at = datetime.now(UTC)
    bp.created_at = datetime.now(UTC)
    bp.updated_at = datetime.now(UTC)
    return bp


@pytest.fixture
def client(
    auth_settings: Settings,
    owner_student_id: uuid.UUID,
    other_student_id: uuid.UUID,
    sample_project: ProjectInstanceModel,
    completed_assessment: AssessmentModel,
    approved_blueprint: BlueprintModel,
) -> Generator[TestClient, None, None]:
    app = create_app(settings=auth_settings)

    project_store: dict[str, ProjectInstanceModel] = {str(sample_project.id): sample_project}
    assessment_store: dict[str, AssessmentModel] = {str(completed_assessment.project_instance_id): completed_assessment}
    blueprints_store: dict[str, BlueprintModel] = {str(approved_blueprint.project_instance_id): approved_blueprint}

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    async def _p_get_by_id(pid):
        return project_store.get(str(pid))
    async def _p_get_profile(pid):
        return None
    async def _p_list_technologies(pid):
        return []
    async def _p_list_phase_history(pid):
        return []
    async def _p_list_health_history(pid):
        return []

    mock_project_repo.get_by_id.side_effect = _p_get_by_id
    mock_project_repo.get_profile.side_effect = _p_get_profile
    mock_project_repo.list_technologies.side_effect = _p_list_technologies
    mock_project_repo.list_phase_history.side_effect = _p_list_phase_history
    mock_project_repo.list_health_history.side_effect = _p_list_health_history

    mock_assessment_repo = AsyncMock(spec=AssessmentRepository)
    async def _a_get_by_project(pid):
        return assessment_store.get(str(pid))
    async def _a_get_result(pid):
        res = AssessmentResultModel()
        res.id = str(uuid.uuid4())
        res.project_instance_id = str(pid)
        res.overall_score = 85
        res.readiness_tier = "HIGH"
        res.dimension_scores = {
            "problem_clarity": 90,
            "architecture_readiness": 85,
            "technical_feasibility": 82,
            "delivery_confidence": 83,
        }
        res.technical_gaps = [{"id": "G01", "severity": "MEDIUM", "description": "Edge buffer capacity"}]
        res.recommendations = ["Implement robust flash ring buffer for telemetry"]
        return res
    mock_assessment_repo.get_by_project_id.side_effect = _a_get_by_project
    mock_assessment_repo.get_result_by_project_id.side_effect = _a_get_result

    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    async def _bp_get_by_proj(pid):
        return blueprints_store.get(str(pid))
    mock_blueprint_repo.get_by_project_id.side_effect = _bp_get_by_proj

    mock_user_repo = AsyncMock(spec=UserRepository)
    async def _get_user_by_id(uid):
        uid_str = str(uid)
        if uid_str == str(owner_student_id):
            return UserModel(
                id=uid_str,
                email="owner@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
                full_name="Alex Rivera",
            )
        elif uid_str == str(other_student_id):
            return UserModel(
                id=uid_str,
                email="other@example.com",
                role=UserRole.STUDENT.value,
                status=AccountStatus.ACTIVE.value,
                full_name="Other Student",
            )
        return None
    mock_user_repo.get_by_id.side_effect = _get_user_by_id

    mock_outbox_service = AsyncMock()

    proj_service = ProjectService(
        project_repo=mock_project_repo,
        group_repo=AsyncMock(),
        technology_repo=AsyncMock(),
        outbox_service=mock_outbox_service,
        assessment_repo=mock_assessment_repo,
        blueprint_repo=mock_blueprint_repo,
    )

    bp_service = BlueprintService(
        blueprint_repo=mock_blueprint_repo,
        project_repo=mock_project_repo,
        assessment_repo=mock_assessment_repo,
        project_service=proj_service,
        outbox_service=mock_outbox_service,
    )

    app.dependency_overrides[get_project_service] = lambda: proj_service
    app.dependency_overrides[get_blueprint_service] = lambda: bp_service
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()

    with patch("backend.app.infrastructure.repositories.user_repository.UserRepository.get_by_id", side_effect=_get_user_by_id), \
         patch("backend.app.api.dependencies.auth.UserRepository") as user_repo_cls:
        user_repo_cls.return_value.get_by_id = _get_user_by_id
        with TestClient(app, raise_server_exceptions=False) as client_instance:
            yield client_instance


# ==============================================================================
# S15: Project Overview Tests
# ==============================================================================


def test_project_overview_owner_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/overview",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]

    # Canonical project identity
    assert data["id"] == str(project_id)
    assert data["name"] == "Precision Agriculture Drone System"
    assert data["current_phase"] == ProjectPhase.BLUEPRINT.value
    assert data["health"] == ProjectHealth.HEALTHY.value
    assert data["progress_percentage"] == 35
    assert data["is_mentor_project"] is False

    # Enriched Assessment Summary
    assert data["assessment_summary"] is not None
    assert data["assessment_summary"]["status"] == AssessmentStatus.COMPLETED.value
    assert data["assessment_summary"]["overall_score"] == 85
    assert data["assessment_summary"]["readiness_tier"] == "HIGH"
    assert data["assessment_summary"]["dimension_scores"]["problem_clarity"] == 90

    # Enriched Blueprint Summary
    assert data["blueprint_summary"] is not None
    assert data["blueprint_summary"]["status"] == BlueprintStatus.APPROVED.value
    assert data["blueprint_summary"]["qa_status"] == BlueprintQAStatus.PASS.value
    assert data["blueprint_summary"]["qa_score"] == 88
    assert data["blueprint_summary"]["total_sections"] == 10
    assert data["blueprint_summary"]["approved_at"] is not None


def test_project_overview_cross_student_forbidden(
    client: TestClient,
    project_id: uuid.UUID,
    other_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/overview",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_project_overview_nonexistent_project_404(
    client: TestClient,
    owner_token: str,
):
    fake_id = uuid.uuid4()
    resp = client.get(
        f"/api/v1/projects/{fake_id}/overview",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PROJECT_NOT_FOUND"


# ==============================================================================
# S16: Blueprint Workspace Section Tests
# ==============================================================================


def test_blueprint_section_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
):
    # 1. Test tech_stack section
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/sections/tech_stack",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["section_key"] == "tech_stack"
    assert data["title"] == "Technology Stack & Architecture"
    assert "stack" in data["structured_content"]
    assert "FastAPI" in data["markdown"]
    assert "| Category | Technology |" in data["markdown"]

    # 2. Test specifications section
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/sections/specifications",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["section_key"] == "specifications"
    assert "api_specifications" in data["structured_content"]
    assert "/api/v1/missions" in data["markdown"]


def test_blueprint_section_invalid_key_404(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/sections/invalid_section_key",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "SECTION_NOT_FOUND"


def test_blueprint_section_cross_student_forbidden(
    client: TestClient,
    project_id: uuid.UUID,
    other_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/sections/tech_stack",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 403


# ==============================================================================
# S17: Blueprint Document Viewer & Download Tests
# ==============================================================================


def test_blueprint_document_view_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/documents/readme",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["document_key"] == "readme"
    assert data["title"] == "README & Setup Guide"
    assert data["version"] == "1.0.0"
    assert data["status"] == BlueprintStatus.APPROVED.value
    assert data["format"] == "markdown"
    assert "Precision Agriculture Drone System" in data["markdown"]
    assert len(data["available_documents"]) >= 10


def test_blueprint_document_master_full_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/documents/full",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["document_key"] == "full"
    assert data["title"] == "Complete Master Blueprint"
    assert "Master Architectural Blueprint" in data["markdown"]
    assert "Technology Stack" in data["markdown"]
    assert "Core System Features" in data["markdown"]


def test_blueprint_document_invalid_key_404(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/documents/nonexistent_doc",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_blueprint_document_raw_download_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/documents/readme/raw",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]
    assert "precision-agriculture-drone-system-readme.md" in resp.headers["content-disposition"]
    assert "Precision Agriculture Drone System" in resp.text


def test_blueprint_document_raw_cross_student_forbidden(
    client: TestClient,
    project_id: uuid.UUID,
    other_token: str,
):
    resp = client.get(
        f"/api/v1/projects/{project_id}/blueprint/documents/readme/raw",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 403


def test_unauthenticated_requests_return_401(
    client: TestClient,
    project_id: uuid.UUID,
):
    # Overview
    r1 = client.get(f"/api/v1/projects/{project_id}/overview")
    assert r1.status_code == 401

    # Section
    r2 = client.get(f"/api/v1/projects/{project_id}/blueprint/sections/tech_stack")
    assert r2.status_code == 401

    # Document
    r3 = client.get(f"/api/v1/projects/{project_id}/blueprint/documents/readme")
    assert r3.status_code == 401

    # Raw download
    r4 = client.get(f"/api/v1/projects/{project_id}/blueprint/documents/readme/raw")
    assert r4.status_code == 401
