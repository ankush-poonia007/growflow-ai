"""
GrowFlow — Integration Test Suite for Persistent Demo / QA Dataset.

Verifies:
1. All 11 accounts (3 Mentors, 8 Students) successfully authenticate through Supabase GoTrue Auth.
2. Backend /api/v1/auth/me resolves authoritative roles (MENTOR, STUDENT) for each account.
3. Group and cohort structure:
   - Elena supervises 3 students (Aarav, Riya, Kabir)
   - Arjun supervises 3 students (Anaya, Vihaan, Meera)
   - Sofia supervises 2 students (Arjun Gupta, Isha)
4. Cross-Mentor Security Isolation Matrix:
   - Mentor Elena accesses own supervised projects (200 OK)
   - Mentor Elena attempting to access Mentor Arjun's student project receives 403 Forbidden
   - Mentor Arjun accesses own supervised projects (200 OK)
   - Mentor Arjun attempting to access Mentor Elena's student project receives 403 Forbidden
   - Mentor Sofia cohort isolation
5. Student Isolation Boundary:
   - Student Aarav accesses own project instance (200 OK)
   - Student Aarav attempting to access Student Riya's project receives 403 Forbidden
6. Risk & At-Risk Directory (M31/M32/M07):
   - Mentor Elena sees only WARNING and CRITICAL projects in her cohort (Riya, Kabir)
   - Mentor Arjun sees only WARNING and CRITICAL projects in his cohort (Anaya, Vihaan)
   - Mentor Sofia sees 0 at-risk projects (all HEALTHY)
7. Mentor Project Deep Inspection (M24-M30):
   - Blueprint, Tasks, Milestones, Risks, Documents, Activity endpoints render 200 OK
"""

from __future__ import annotations

import os
import sys
import pytest
import requests

DEMO_PASSWORD = "GrowFlow2026!Demo"
API_BASE_URL = os.environ.get("GROWFLOW_API_URL", "http://127.0.0.1:8000/api/v1")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://qdqdiizjhtvtbuskqeun.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_TuY2ylJE8gXgL5TC5SoxLg_kMc8aY4P")

MENTOR_ACCOUNTS = [
    {"email": "mentor.elena@growflow.ai", "name": "Dr. Elena Vance", "id": "11111111-2222-3333-4444-555555555555"},
    {"email": "mentor.arjun@growflow.ai", "name": "Dr. Arjun Mehta", "id": "11111111-2222-3333-4444-555555555556"},
    {"email": "mentor.sofia@growflow.ai", "name": "Dr. Sofia Chen", "id": "11111111-2222-3333-4444-555555555557"},
]

STUDENT_ACCOUNTS = [
    {"email": "student.aarav@growflow.ai", "name": "Aarav Patel", "project_id": "bbbbbbbb-0001-0000-0000-000000000001"},
    {"email": "student.riya@growflow.ai", "name": "Riya Sharma", "project_id": "bbbbbbbb-0002-0000-0000-000000000002"},
    {"email": "student.kabir@growflow.ai", "name": "Kabir Verma", "project_id": "bbbbbbbb-0003-0000-0000-000000000003"},
    {"email": "student.anaya@growflow.ai", "name": "Anaya Iyer", "project_id": "bbbbbbbb-0004-0000-0000-000000000004"},
    {"email": "student.vihaan@growflow.ai", "name": "Vihaan Reddy", "project_id": "bbbbbbbb-0005-0000-0000-000000000005"},
    {"email": "student.meera@growflow.ai", "name": "Meera Nair", "project_id": "bbbbbbbb-0006-0000-0000-000000000006"},
    {"email": "student.arjun@growflow.ai", "name": "Arjun Gupta", "project_id": "bbbbbbbb-0007-0000-0000-000000000007"},
    {"email": "student.isha@growflow.ai", "name": "Isha Malhotra", "project_id": "bbbbbbbb-0008-0000-0000-000000000008"},
]


def authenticate(email: str, password: str = DEMO_PASSWORD) -> str:
    """Helper to authenticate directly against Supabase GoTrue endpoint."""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"email": email, "password": password}, timeout=10)
    assert resp.status_code == 200, f"Failed to authenticate {email}: {resp.text}"
    data = resp.json()
    return data["access_token"]


@pytest.fixture(scope="module")
def mentor_tokens() -> dict[str, str]:
    tokens = {}
    for m in MENTOR_ACCOUNTS:
        tokens[m["email"]] = authenticate(m["email"])
    return tokens


@pytest.fixture(scope="module")
def student_tokens() -> dict[str, str]:
    tokens = {}
    for s in STUDENT_ACCOUNTS:
        tokens[s["email"]] = authenticate(s["email"])
    return tokens


class TestDemoAuthenticationAndRoleResolution:
    """Verify all 11 accounts can authenticate and resolve backend-authoritative roles."""

    @pytest.mark.parametrize("mentor", MENTOR_ACCOUNTS)
    def test_mentor_auth_and_me(self, mentor, mentor_tokens):
        token = mentor_tokens[mentor["email"]]
        resp = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200, f"/auth/me failed for mentor {mentor['email']}: {resp.text}"
        payload = resp.json()["data"]
        assert payload["role"] == "MENTOR"
        assert payload["email"] == mentor["email"]

    @pytest.mark.parametrize("student", STUDENT_ACCOUNTS)
    def test_student_auth_and_me(self, student, student_tokens):
        token = student_tokens[student["email"]]
        resp = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200, f"/auth/me failed for student {student['email']}: {resp.text}"
        payload = resp.json()["data"]
        assert payload["role"] == "STUDENT"
        assert payload["email"] == student["email"]


class TestMentorCohortIsolationMatrix:
    """Verify strict supervisory cohort isolation between mentors."""

    def test_mentor_elena_project_directory(self, mentor_tokens):
        token = mentor_tokens["mentor.elena@growflow.ai"]
        resp = requests.get(
            f"{API_BASE_URL}/mentors/project-instances",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200
        projects = resp.json()["data"]
        assert len(projects) == 3
        student_emails = {p["student_email"] for p in projects}
        assert student_emails == {
            "student.aarav@growflow.ai",
            "student.riya@growflow.ai",
            "student.kabir@growflow.ai",
        }

    def test_mentor_arjun_project_directory(self, mentor_tokens):
        token = mentor_tokens["mentor.arjun@growflow.ai"]
        resp = requests.get(
            f"{API_BASE_URL}/mentors/project-instances",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200
        projects = resp.json()["data"]
        assert len(projects) == 3
        student_emails = {p["student_email"] for p in projects}
        assert student_emails == {
            "student.anaya@growflow.ai",
            "student.vihaan@growflow.ai",
            "student.meera@growflow.ai",
        }

    def test_mentor_sofia_project_directory(self, mentor_tokens):
        token = mentor_tokens["mentor.sofia@growflow.ai"]
        resp = requests.get(
            f"{API_BASE_URL}/mentors/project-instances",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200
        projects = resp.json()["data"]
        assert len(projects) == 2
        student_emails = {p["student_email"] for p in projects}
        assert student_emails == {
            "student.arjun@growflow.ai",
            "student.isha@growflow.ai",
        }

    def test_cross_mentor_access_denial(self, mentor_tokens):
        elena_token = mentor_tokens["mentor.elena@growflow.ai"]
        arjun_token = mentor_tokens["mentor.arjun@growflow.ai"]

        aarav_proj = "bbbbbbbb-0001-0000-0000-000000000001"  # Supervised by Elena
        anaya_proj = "bbbbbbbb-0004-0000-0000-000000000004"  # Supervised by Arjun

        # Elena accesses Aarav -> 200 OK
        r1 = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{aarav_proj}",
            headers={"Authorization": f"Bearer {elena_token}"},
            timeout=10,
        )
        assert r1.status_code == 200

        # Elena attempts to access Anaya -> 403 Forbidden
        r2 = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{anaya_proj}",
            headers={"Authorization": f"Bearer {elena_token}"},
            timeout=10,
        )
        assert r2.status_code == 403

        # Arjun accesses Anaya -> 200 OK
        r3 = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{anaya_proj}",
            headers={"Authorization": f"Bearer {arjun_token}"},
            timeout=10,
        )
        assert r3.status_code == 200

        # Arjun attempts to access Aarav -> 403 Forbidden
        r4 = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{aarav_proj}",
            headers={"Authorization": f"Bearer {arjun_token}"},
            timeout=10,
        )
        assert r4.status_code == 403


class TestStudentProjectIsolation:
    """Verify students can only access their own project instances."""

    def test_student_own_project_and_cross_student_denial(self, student_tokens):
        aarav_token = student_tokens["student.aarav@growflow.ai"]
        aarav_proj = "bbbbbbbb-0001-0000-0000-000000000001"
        riya_proj = "bbbbbbbb-0002-0000-0000-000000000002"

        # Aarav accesses own project -> 200 OK
        r1 = requests.get(
            f"{API_BASE_URL}/projects/{aarav_proj}",
            headers={"Authorization": f"Bearer {aarav_token}"},
            timeout=10,
        )
        assert r1.status_code == 200
        assert r1.json()["data"]["id"] == aarav_proj

        # Aarav attempts to access Riya's project -> 403 Forbidden
        r2 = requests.get(
            f"{API_BASE_URL}/projects/{riya_proj}",
            headers={"Authorization": f"Bearer {aarav_token}"},
            timeout=10,
        )
        assert r2.status_code == 403


class TestAtRiskSupervision:
    """Verify at-risk queries (WARNING and CRITICAL) correctly filter cohorts."""

    def test_elena_at_risk_projects(self, mentor_tokens):
        token = mentor_tokens["mentor.elena@growflow.ai"]
        resp = requests.get(
            f"{API_BASE_URL}/mentors/at-risk",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200
        items = resp.json()["data"]
        assert len(items) == 2
        emails = {item["student_email"] for item in items}
        assert emails == {"student.riya@growflow.ai", "student.kabir@growflow.ai"}

    def test_arjun_at_risk_projects(self, mentor_tokens):
        token = mentor_tokens["mentor.arjun@growflow.ai"]
        resp = requests.get(
            f"{API_BASE_URL}/mentors/at-risk",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200
        items = resp.json()["data"]
        assert len(items) == 2
        emails = {item["student_email"] for item in items}
        assert emails == {"student.anaya@growflow.ai", "student.vihaan@growflow.ai"}

    def test_sofia_at_risk_projects(self, mentor_tokens):
        token = mentor_tokens["mentor.sofia@growflow.ai"]
        resp = requests.get(
            f"{API_BASE_URL}/mentors/at-risk",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200
        items = resp.json()["data"]
        assert len(items) == 0  # Both students are HEALTHY


class TestMentorDeepInspectionSurfaces:
    """Verify deep inspection endpoints (M24-M30) return canonical structured data."""

    def test_supervised_inspection_routes(self, mentor_tokens):
        token = mentor_tokens["mentor.elena@growflow.ai"]
        proj_id = "bbbbbbbb-0003-0000-0000-000000000003"  # Kabir (PLANNING, has tasks, blueprint, risks)

        # M24 Blueprint
        r_bp = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{proj_id}/blueprint",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert r_bp.status_code == 200
        assert r_bp.json()["data"]["blueprint"]["status"] == "APPROVED"

        # M25 Tasks
        r_tsk = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{proj_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert r_tsk.status_code == 200
        tasks = r_tsk.json()["data"]
        assert len(tasks) == 10

        # M26 Milestones
        r_ms = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{proj_id}/milestones",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert r_ms.status_code == 200
        milestones = r_ms.json()["data"]
        assert len(milestones) == 4

        # M27 Risks
        r_rsk = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{proj_id}/risks",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert r_rsk.status_code == 200
        risks = r_rsk.json()["data"]
        assert len(risks) == 2

        # M28 Documents
        r_doc = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{proj_id}/documents",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert r_doc.status_code == 200
        docs = r_doc.json()["data"]
        assert len(docs) == 5

        # M30 Activity
        r_act = requests.get(
            f"{API_BASE_URL}/mentors/project-instances/{proj_id}/activity",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert r_act.status_code == 200
        activity = r_act.json()["data"]
        assert len(activity) >= 6
