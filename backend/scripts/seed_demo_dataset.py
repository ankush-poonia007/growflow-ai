"""
GrowFlow — Persistent Demo / QA Dataset Seeder.

Creates a deterministic, idempotent development/demo dataset containing:
- 3 Mentor accounts (Elena Vance, Arjun Mehta, Sofia Chen)
- 8 Student accounts (Aarav, Riya, Kabir, Anaya, Vihaan, Meera, Arjun Gupta, Isha)
- 3 Supervised Groups (Elena Cohort, Arjun Cohort, Sofia Cohort)
- 8 Project Definitions & pinned Immutable Versions
- 8 Student Project Instances spanning canonical lifecycle stages (IDEA -> COMPLETED)
- Realistic Tasks, Milestones, Risks (HEALTHY, WARNING, CRITICAL), and Documents
- Historical Phase/Health transitions and Domain Events for Audit Trails

All accounts are real Supabase Auth accounts with deterministic password:
`GrowFlow2026!Demo`

Architecture ref: Phase 7 Batches 0-4, Gates 01-11, 6B § 5-11.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
import json
import os
import sys
from typing import Any

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text

from backend.app.config.settings import get_settings
from backend.app.domain.blueprint.models import BlueprintQAStatus, BlueprintStatus
from backend.app.domain.identity.models import AccountStatus, UserRole
from backend.app.domain.organization.models import GroupMembershipStatus, GroupStatus
from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectDefinitionStatus,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.infrastructure.database.lifecycle import (
    get_session_factory,
    shutdown,
    startup,
)
from backend.app.shared.events.domain_event import DomainEventType, EventVisibility, OutboxStatus

DEMO_PASSWORD = "GrowFlow2026!Demo"

# Deterministic UUIDs
MENTOR_IDS = {
    "elena": "11111111-2222-3333-4444-555555555555",
    "arjun": "11111111-2222-3333-4444-555555555556",
    "sofia": "11111111-2222-3333-4444-555555555557",
}

GROUP_IDS = {
    "elena": "aaaaaaaa-0001-0000-0000-000000000001",
    "arjun": "aaaaaaaa-0002-0000-0000-000000000002",
    "sofia": "aaaaaaaa-0003-0000-0000-000000000003",
}

STUDENT_IDS = {
    1: "22222222-0001-0000-0000-000000000001",  # Aarav Patel
    2: "22222222-0002-0000-0000-000000000002",  # Riya Sharma
    3: "22222222-0003-0000-0000-000000000003",  # Kabir Verma
    4: "22222222-0004-0000-0000-000000000004",  # Anaya Iyer
    5: "22222222-0005-0000-0000-000000000005",  # Vihaan Reddy
    6: "22222222-0006-0000-0000-000000000006",  # Meera Nair
    7: "22222222-0007-0000-0000-000000000007",  # Arjun Gupta
    8: "22222222-0008-0000-0000-000000000008",  # Isha Malhotra
}

DEFINITION_IDS = {
    1: "22222222-3333-4444-5555-666666666666",
    2: "dddddddd-0002-0000-0000-000000000002",
    3: "dddddddd-0003-0000-0000-000000000003",
    4: "dddddddd-0004-0000-0000-000000000004",
    5: "dddddddd-0005-0000-0000-000000000005",
    6: "dddddddd-0006-0000-0000-000000000006",
    7: "dddddddd-0007-0000-0000-000000000007",
    8: "dddddddd-0008-0000-0000-000000000008",
}

VERSION_IDS = {
    1: "33333333-4444-5555-6666-777777777777",
    2: "cccccccc-0002-0000-0000-000000000002",
    3: "cccccccc-0003-0000-0000-000000000003",
    4: "cccccccc-0004-0000-0000-000000000004",
    5: "cccccccc-0005-0000-0000-000000000005",
    6: "cccccccc-0006-0000-0000-000000000006",
    7: "cccccccc-0007-0000-0000-000000000007",
    8: "cccccccc-0008-0000-0000-000000000008",
}

INSTANCE_IDS = {
    1: "bbbbbbbb-0001-0000-0000-000000000001",
    2: "bbbbbbbb-0002-0000-0000-000000000002",
    3: "bbbbbbbb-0003-0000-0000-000000000003",
    4: "bbbbbbbb-0004-0000-0000-000000000004",
    5: "bbbbbbbb-0005-0000-0000-000000000005",
    6: "bbbbbbbb-0006-0000-0000-000000000006",
    7: "bbbbbbbb-0007-0000-0000-000000000007",
    8: "bbbbbbbb-0008-0000-0000-000000000008",
}


async def upsert_supabase_auth_user(
    session: Any,
    user_id: str,
    email: str,
    full_name: str,
    role: str,
    password: str = DEMO_PASSWORD,
) -> None:
    """Upsert real Supabase GoTrue auth.users and auth.identities records."""
    meta = json.dumps({"sub": user_id, "email": email, "full_name": full_name, "role": role})
    
    # 1. Upsert auth.users
    user_sql = text("""
        INSERT INTO auth.users (
            instance_id, id, aud, role, email, encrypted_password,
            email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
            created_at, updated_at, confirmation_token, recovery_token,
            email_change_token_new, email_change, email_change_token_current,
            phone_change, phone_change_token, reauthentication_token
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            CAST(:user_id AS uuid),
            'authenticated',
            'authenticated',
            :email,
            crypt(:password, gen_salt('bf', 10)),
            NOW(),
            CAST('{"provider":"email","providers":["email"]}' AS jsonb),
            CAST(:meta AS jsonb),
            NOW(),
            NOW(),
            '', '', '', '', '', '', '', ''
        )
        ON CONFLICT (id) DO UPDATE SET
            email = EXCLUDED.email,
            encrypted_password = crypt(:password, gen_salt('bf', 10)),
            email_confirmed_at = NOW(),
            raw_user_meta_data = EXCLUDED.raw_user_meta_data,
            confirmation_token = '',
            recovery_token = '',
            email_change_token_new = '',
            email_change = '',
            email_change_token_current = '',
            phone_change = '',
            phone_change_token = '',
            reauthentication_token = '',
            updated_at = NOW();
    """)
    await session.execute(user_sql, {"user_id": user_id, "email": email, "password": password, "meta": meta})

    # 2. Upsert auth.identities
    ident_sql = text("""
        INSERT INTO auth.identities (
            id, user_id, identity_data, provider, provider_id, last_sign_in_at, created_at, updated_at
        ) VALUES (
            gen_random_uuid(),
            CAST(:user_id AS uuid),
            CAST(:meta AS jsonb),
            'email',
            :user_id,
            NOW(),
            NOW(),
            NOW()
        )
        ON CONFLICT (provider, provider_id) DO UPDATE SET
            identity_data = EXCLUDED.identity_data,
            updated_at = NOW();
    """)
    await session.execute(ident_sql, {"user_id": user_id, "meta": meta})


async def seed_mentors(session: Any) -> None:
    """Seed 3 real Mentor accounts and profiles."""
    mentors_data = [
        {
            "id": MENTOR_IDS["elena"],
            "email": "mentor.elena@growflow.ai",
            "full_name": "Dr. Elena Vance",
            "mentor_id": "MTR-ELENA-001",
            "bio": "Principal Research Scientist & Autonomous Robotics Lead. Specializes in edge computing and cyber-physical systems.",
            "specialization": "Autonomous Systems, Edge Computing, Robotics, Embedded Systems",
        },
        {
            "id": MENTOR_IDS["arjun"],
            "email": "mentor.arjun@growflow.ai",
            "full_name": "Dr. Arjun Mehta",
            "mentor_id": "MTR-ARJUN-002",
            "bio": "Senior Software Architect & Fintech Systems Advisor. Expertise in cloud microservices and financial transaction safety.",
            "specialization": "Cloud Architecture, Distributed Systems, High-Frequency Trading, Fintech",
        },
        {
            "id": MENTOR_IDS["sofia"],
            "email": "mentor.sofia@growflow.ai",
            "full_name": "Dr. Sofia Chen",
            "mentor_id": "MTR-SOFIA-003",
            "bio": "Associate Professor in Health Informatics & Machine Learning. Focused on HIPAA-compliant health data architectures.",
            "specialization": "Healthcare Systems, Predictive Analytics, HIPAA Compliance, Medical ML",
        },
    ]

    for m in mentors_data:
        # Supabase auth
        await upsert_supabase_auth_user(session, m["id"], m["email"], m["full_name"], UserRole.MENTOR.value)

        # GrowFlow users table
        user_sql = text("""
            INSERT INTO users (id, email, full_name, role, status, created_at, updated_at)
            VALUES (CAST(:id AS uuid), :email, :full_name, 'MENTOR', 'ACTIVE', NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                full_name = EXCLUDED.full_name,
                role = 'MENTOR',
                status = 'ACTIVE',
                updated_at = NOW();
        """)
        await session.execute(user_sql, {"id": m["id"], "email": m["email"], "full_name": m["full_name"]})

        # Mentor profile
        prof_sql = text("""
            INSERT INTO mentor_profiles (user_id, mentor_id, bio, specialization, created_at, updated_at)
            VALUES (CAST(:user_id AS uuid), :mentor_id, :bio, :specialization, NOW(), NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                mentor_id = EXCLUDED.mentor_id,
                bio = EXCLUDED.bio,
                specialization = EXCLUDED.specialization,
                updated_at = NOW();
        """)
        await session.execute(prof_sql, {
            "user_id": m["id"],
            "mentor_id": m["mentor_id"],
            "bio": m["bio"],
            "specialization": m["specialization"],
        })


async def seed_students(session: Any) -> None:
    """Seed 8 real Student accounts and profiles."""
    students_data = [
        {
            "id": STUDENT_IDS[1],
            "email": "student.aarav@growflow.ai",
            "full_name": "Aarav Patel",
            "student_id": "STU-AARAV-001",
            "bio": "Undergraduate senior specializing in robotics and sensor networks.",
            "goals": "Develop autonomous edge navigation systems for smart agriculture.",
            "interests": "Robotics, Computer Vision, Edge Computing, Python",
        },
        {
            "id": STUDENT_IDS[2],
            "email": "student.riya@growflow.ai",
            "full_name": "Riya Sharma",
            "student_id": "STU-RIYA-002",
            "bio": "Third-year Computer Science student passionate about campus IoT applications.",
            "goals": "Build low-friction automated attendance tracking for university lecture halls.",
            "interests": "IoT, Mobile Development, Facial Recognition, FastAPI",
        },
        {
            "id": STUDENT_IDS[3],
            "email": "student.kabir@growflow.ai",
            "full_name": "Kabir Verma",
            "student_id": "STU-KABIR-003",
            "bio": "Software Engineering student focused on developer tools and productivity.",
            "goals": "Ship a unified workflow tracking platform for engineering student cohorts.",
            "interests": "Full-Stack Development, React, PostgreSQL, Docker",
        },
        {
            "id": STUDENT_IDS[4],
            "email": "student.anaya@growflow.ai",
            "full_name": "Anaya Iyer",
            "student_id": "STU-ANAYA-004",
            "bio": "Final year CS & Finance dual-degree student.",
            "goals": "Build high-integrity micro-investing and automated budget analytics engines.",
            "interests": "Fintech, Microservices, Python, Cloud Security",
        },
        {
            "id": STUDENT_IDS[5],
            "email": "student.vihaan@growflow.ai",
            "full_name": "Vihaan Reddy",
            "student_id": "STU-VIHAAN-005",
            "bio": "Information Systems senior focusing on supply chain software and inventory control.",
            "goals": "Implement real-time warehouse inventory forecasting with demand prediction.",
            "interests": "Distributed Systems, Data Engineering, REST APIs",
        },
        {
            "id": STUDENT_IDS[6],
            "email": "student.meera@growflow.ai",
            "full_name": "Meera Nair",
            "student_id": "STU-MEERA-006",
            "bio": "Computer Science student specializing in career development platforms and AI assistance.",
            "goals": "Create an automated resume analysis and internship placement pipeline.",
            "interests": "Natural Language Processing, Full-Stack Web, TypeScript",
        },
        {
            "id": STUDENT_IDS[7],
            "email": "student.arjun@growflow.ai",
            "full_name": "Arjun Gupta",
            "student_id": "STU-ARJUN-007",
            "bio": "Biomedical Engineering & CS student focusing on telehealth infrastructure.",
            "goals": "Deploy a secure WebRTC tele-appointment platform for rural clinics.",
            "interests": "Healthcare IT, WebRTC, Encryption, React",
        },
        {
            "id": STUDENT_IDS[8],
            "email": "student.isha@growflow.ai",
            "full_name": "Isha Malhotra",
            "student_id": "STU-ISHA-008",
            "bio": "Graduating Senior and EdTech researcher.",
            "goals": "Deliver an adaptive learning recommendation engine based on cognitive graphs.",
            "interests": "Graph Algorithms, Machine Learning, Next.js, FastAPI",
        },
    ]

    for s in students_data:
        # Supabase auth
        await upsert_supabase_auth_user(session, s["id"], s["email"], s["full_name"], UserRole.STUDENT.value)

        # GrowFlow users table
        user_sql = text("""
            INSERT INTO users (id, email, full_name, role, status, created_at, updated_at)
            VALUES (CAST(:id AS uuid), :email, :full_name, 'STUDENT', 'ACTIVE', NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                full_name = EXCLUDED.full_name,
                role = 'STUDENT',
                status = 'ACTIVE',
                updated_at = NOW();
        """)
        await session.execute(user_sql, {"id": s["id"], "email": s["email"], "full_name": s["full_name"]})

        # Student profile
        prof_sql = text("""
            INSERT INTO student_profiles (user_id, student_id, bio, goals, interests, created_at, updated_at)
            VALUES (CAST(:user_id AS uuid), :student_id, :bio, :goals, :interests, NOW(), NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                student_id = EXCLUDED.student_id,
                bio = EXCLUDED.bio,
                goals = EXCLUDED.goals,
                interests = EXCLUDED.interests,
                updated_at = NOW();
        """)
        await session.execute(prof_sql, {
            "user_id": s["id"],
            "student_id": s["student_id"],
            "bio": s["bio"],
            "goals": s["goals"],
            "interests": s["interests"],
        })


async def seed_groups_and_memberships(session: Any) -> None:
    """Seed 3 Groups and assign the 8 Students into their respective cohorts."""
    groups_data = [
        {
            "id": GROUP_IDS["elena"],
            "mentor_id": MENTOR_IDS["elena"],
            "name": "Autonomous Systems & Robotics Lab",
            "join_code": "ELENA001",
            "students": [STUDENT_IDS[1], STUDENT_IDS[2], STUDENT_IDS[3]],
        },
        {
            "id": GROUP_IDS["arjun"],
            "mentor_id": MENTOR_IDS["arjun"],
            "name": "Enterprise Cloud & Fintech Cohort",
            "join_code": "ARJUN002",
            "students": [STUDENT_IDS[4], STUDENT_IDS[5], STUDENT_IDS[6]],
        },
        {
            "id": GROUP_IDS["sofia"],
            "mentor_id": MENTOR_IDS["sofia"],
            "name": "Digital Health & Biomedical Informatics",
            "join_code": "SOFIA003",
            "students": [STUDENT_IDS[7], STUDENT_IDS[8], STUDENT_IDS[2]],
        },
    ]

    for g in groups_data:
        grp_sql = text("""
            INSERT INTO groups (id, mentor_id, name, join_code, status, created_at, updated_at)
            VALUES (CAST(:id AS uuid), CAST(:mentor_id AS uuid), :name, :join_code, 'ACTIVE', NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                mentor_id = EXCLUDED.mentor_id,
                name = EXCLUDED.name,
                join_code = EXCLUDED.join_code,
                status = 'ACTIVE',
                updated_at = NOW();
        """)
        await session.execute(grp_sql, {
            "id": g["id"],
            "mentor_id": g["mentor_id"],
            "name": g["name"],
            "join_code": g["join_code"],
        })

        for s_id in g["students"]:
            mem_sql = text("""
                INSERT INTO group_memberships (id, group_id, student_id, status, joined_at, created_at)
                VALUES (
                    gen_random_uuid(),
                    CAST(:group_id AS uuid),
                    CAST(:student_id AS uuid),
                    'ACTIVE',
                    NOW(),
                    NOW()
                )
                ON CONFLICT (group_id, student_id) DO UPDATE SET
                    status = 'ACTIVE';
            """)
            await session.execute(mem_sql, {"group_id": g["id"], "student_id": s_id})


async def seed_definitions_and_versions(session: Any) -> None:
    """Seed 8 Project Definitions and pinned Immutable Version snapshots."""
    defs_data = [
        {
            "idx": 1,
            "mentor_id": MENTOR_IDS["elena"],
            "name": "Autonomous Precision Agriculture Drone",
            "problem": "Inefficient manual crop inspection and delayed detection of pest infestations across large acreage.",
            "solution": "Deploy autonomous drone flight paths with multispectral imaging for early crop stress detection.",
            "complexity": ProjectComplexity.ADVANCED.value,
            "description": "Multi-rotor drone system capable of autonomous waypoint navigation, multispectral imaging, and edge ML defect detection.",
            "duration": "16 Weeks",
            "tech": [{"name": "Python"}, {"name": "ROS2"}, {"name": "PyTorch"}, {"name": "Raspberry Pi"}],
        },
        {
            "idx": 2,
            "mentor_id": MENTOR_IDS["elena"],
            "name": "Campus Smart Attendance System",
            "problem": "High lecture friction and lost instructional time due to manual roll-calling in large lecture halls.",
            "solution": "Automated facial recognition and BLE beacon proximity sensing for non-intrusive lecture hall attendance.",
            "complexity": ProjectComplexity.INTERMEDIATE.value,
            "description": "Embedded edge camera sensor streaming frames to a local inference node for real-time student check-ins.",
            "duration": "12 Weeks",
            "tech": [{"name": "FastAPI"}, {"name": "OpenCV"}, {"name": "PostgreSQL"}, {"name": "React"}],
        },
        {
            "idx": 3,
            "mentor_id": MENTOR_IDS["elena"],
            "name": "Student Productivity Platform",
            "problem": "Fragmented task management, missed assignment deadlines, and low collaboration across capstone teams.",
            "solution": "Unified workspace integrating Kanban, milestone tracking, risk registers, and automated GitHub progress sync.",
            "complexity": ProjectComplexity.INTERMEDIATE.value,
            "description": "Modern full-stack productivity suite built specifically for university engineering capstone cohorts.",
            "duration": "14 Weeks",
            "tech": [{"name": "React"}, {"name": "TypeScript"}, {"name": "FastAPI"}, {"name": "Docker"}],
        },
        {
            "idx": 4,
            "mentor_id": MENTOR_IDS["arjun"],
            "name": "Personal Finance & Micro-Investment Manager",
            "problem": "Young adults lack actionable financial intelligence and discipline for small recurring investments.",
            "solution": "Automated expense categorization, rule-based micro-investing round-ups, and portfolio risk telemetry.",
            "complexity": ProjectComplexity.ADVANCED.value,
            "description": "Event-driven financial platform with real-time transaction ingestion and automated investment triggers.",
            "duration": "16 Weeks",
            "tech": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}, {"name": "Kafka"}],
        },
        {
            "idx": 5,
            "mentor_id": MENTOR_IDS["arjun"],
            "name": "Smart Inventory Management Platform",
            "problem": "Stock-outs and inventory holding costs caused by inaccurate manual ledger counts.",
            "solution": "Barcode scanning telemetry, real-time inventory ledger, and predictive replenishment orders.",
            "complexity": ProjectComplexity.INTERMEDIATE.value,
            "description": "Distributed warehouse inventory management system with automated low-stock notifications.",
            "duration": "12 Weeks",
            "tech": [{"name": "FastAPI"}, {"name": "Redis"}, {"name": "PostgreSQL"}, {"name": "React"}],
        },
        {
            "idx": 6,
            "mentor_id": MENTOR_IDS["arjun"],
            "name": "College Placement & Internship Assistant",
            "problem": "Students struggle to match skill sets to internship requirements, and career offices lack tracking visibility.",
            "solution": "Automated resume parsing, semantic job-fit scoring, and recruiter interview scheduling pipeline.",
            "complexity": ProjectComplexity.INTERMEDIATE.value,
            "description": "Career placement platform pairing students with tailored internships based on verified course competencies.",
            "duration": "12 Weeks",
            "tech": [{"name": "Python"}, {"name": "Transformers"}, {"name": "FastAPI"}, {"name": "React"}],
        },
        {
            "idx": 7,
            "mentor_id": MENTOR_IDS["sofia"],
            "name": "Healthcare Tele-Appointment Platform",
            "problem": "Rural patients face geographical barriers and extended wait times for specialist medical consultations.",
            "solution": "End-to-end encrypted WebRTC video consultations with integrated electronic health record summary notes.",
            "complexity": ProjectComplexity.ADVANCED.value,
            "description": "HIPAA-conscious telehealth portal enabling synchronous video calls, doctor prescription notes, and appointment scheduling.",
            "duration": "16 Weeks",
            "tech": [{"name": "WebRTC"}, {"name": "React"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}],
        },
        {
            "idx": 8,
            "mentor_id": MENTOR_IDS["sofia"],
            "name": "E-Learning Recommendation Engine",
            "problem": "One-size-fits-all online curriculum leaves struggling students behind and fails to challenge advanced learners.",
            "solution": "Knowledge graph modeling of student concept mastery paired with personalized learning path recommendations.",
            "complexity": ProjectComplexity.ADVANCED.value,
            "description": "Adaptive EdTech platform analyzing quiz performance to dynamically construct personalized learning trajectories.",
            "duration": "14 Weeks",
            "tech": [{"name": "Neo4j"}, {"name": "Python"}, {"name": "FastAPI"}, {"name": "TypeScript"}],
        },
    ]

    for d in defs_data:
        def_id = DEFINITION_IDS[d["idx"]]
        ver_id = VERSION_IDS[d["idx"]]

        # 1. Project Definition
        def_sql = text("""
            INSERT INTO project_definitions (id, owner_mentor_id, name, status, current_version_id, created_at, updated_at)
            VALUES (CAST(:id AS uuid), CAST(:mentor_id AS uuid), :name, 'ACTIVE', CAST(:ver_id AS uuid), NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                owner_mentor_id = EXCLUDED.owner_mentor_id,
                name = EXCLUDED.name,
                status = 'ACTIVE',
                current_version_id = EXCLUDED.current_version_id,
                updated_at = NOW();
        """)
        await session.execute(def_sql, {
            "id": def_id,
            "mentor_id": d["mentor_id"],
            "name": d["name"],
            "ver_id": ver_id,
        })

        # 2. Project Definition Version
        ver_sql = text("""
            INSERT INTO project_definition_versions (
                id, project_definition_id, version_number, name, problem, proposed_solution,
                complexity, description, duration, constraints, assumptions, technology_snapshot,
                created_by, created_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:def_id AS uuid),
                1,
                :name,
                :problem,
                :solution,
                :complexity,
                :description,
                :duration,
                'Hardware budget limit $300; Latency < 200ms',
                'Reliable Wi-Fi network available; Modern browser client',
                CAST(:tech AS jsonb),
                CAST(:mentor_id AS uuid),
                NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                problem = EXCLUDED.problem,
                proposed_solution = EXCLUDED.proposed_solution,
                complexity = EXCLUDED.complexity,
                description = EXCLUDED.description,
                duration = EXCLUDED.duration,
                technology_snapshot = EXCLUDED.technology_snapshot;
        """)
        await session.execute(ver_sql, {
            "id": ver_id,
            "def_id": def_id,
            "name": d["name"],
            "problem": d["problem"],
            "solution": d["solution"],
            "complexity": d["complexity"],
            "description": d["description"],
            "duration": d["duration"],
            "tech": json.dumps(d["tech"]),
            "mentor_id": d["mentor_id"],
        })


async def seed_project_instances(session: Any) -> None:
    """
    Seed 8 Student Project Instances spanning canonical lifecycle states,
    with health indicators, derived progress, and structured project profiles.
    """
    instances_config = [
        {
            "idx": 1,
            "student_id": STUDENT_IDS[1],
            "group_id": GROUP_IDS["elena"],
            "mentor_id": MENTOR_IDS["elena"],
            "name": "Autonomous Precision Agriculture Drone v1",
            "phase": ProjectPhase.IDEA.value,
            "health": ProjectHealth.HEALTHY.value,
            "progress": 10,
            "status": ProjectStatus.ACTIVE.value,
            "completed_tasks": 0,
            "total_tasks": 0,
            "active_risks": "HEALTHY",
        },
        {
            "idx": 2,
            "student_id": STUDENT_IDS[2],
            "group_id": GROUP_IDS["elena"],
            "mentor_id": MENTOR_IDS["elena"],
            "name": "Campus Smart Attendance System v1",
            "phase": ProjectPhase.ASSESSMENT.value,
            "health": ProjectHealth.CRITICAL.value,  # At risk!
            "progress": 25,
            "status": ProjectStatus.ACTIVE.value,
            "completed_tasks": 0,
            "total_tasks": 2,
            "active_risks": "CRITICAL",
        },
        {
            "idx": 3,
            "student_id": STUDENT_IDS[3],
            "group_id": GROUP_IDS["elena"],
            "mentor_id": MENTOR_IDS["elena"],
            "name": "Student Productivity Platform v1",
            "phase": ProjectPhase.PLANNING.value,
            "health": ProjectHealth.WARNING.value,  # At risk!
            "progress": 41,  # 35 + int(0.65 * 10%) = 41%
            "status": ProjectStatus.ACTIVE.value,
            "completed_tasks": 1,
            "total_tasks": 10,
            "active_risks": "WARNING",
        },
        {
            "idx": 4,
            "student_id": STUDENT_IDS[4],
            "group_id": GROUP_IDS["arjun"],
            "mentor_id": MENTOR_IDS["arjun"],
            "name": "Personal Finance & Micro-Investment v1",
            "phase": ProjectPhase.IMPLEMENTATION.value,
            "health": ProjectHealth.CRITICAL.value,  # At risk!
            "progress": 54,  # 35 + int(0.65 * 30%) = 54%
            "status": ProjectStatus.ACTIVE.value,
            "completed_tasks": 3,
            "total_tasks": 10,
            "active_risks": "CRITICAL",
        },
        {
            "idx": 5,
            "student_id": STUDENT_IDS[5],
            "group_id": GROUP_IDS["arjun"],
            "mentor_id": MENTOR_IDS["arjun"],
            "name": "Smart Inventory Management Platform v1",
            "phase": ProjectPhase.IMPLEMENTATION.value,
            "health": ProjectHealth.WARNING.value,  # At risk!
            "progress": 67,  # 35 + int(0.65 * 50%) = 67%
            "status": ProjectStatus.ACTIVE.value,
            "completed_tasks": 5,
            "total_tasks": 10,
            "active_risks": "WARNING",
        },
        {
            "idx": 6,
            "student_id": STUDENT_IDS[6],
            "group_id": GROUP_IDS["arjun"],
            "mentor_id": MENTOR_IDS["arjun"],
            "name": "College Placement & Internship Assistant v1",
            "phase": ProjectPhase.TESTING.value,
            "health": ProjectHealth.HEALTHY.value,
            "progress": 80,  # 35 + int(0.65 * 70%) = 80%
            "status": ProjectStatus.ACTIVE.value,
            "completed_tasks": 7,
            "total_tasks": 10,
            "active_risks": "HEALTHY",
        },
        {
            "idx": 7,
            "student_id": STUDENT_IDS[7],
            "group_id": GROUP_IDS["sofia"],
            "mentor_id": MENTOR_IDS["sofia"],
            "name": "Healthcare Tele-Appointment Platform v1",
            "phase": ProjectPhase.DEPLOYMENT.value,
            "health": ProjectHealth.HEALTHY.value,
            "progress": 93,  # 35 + int(0.65 * 90%) = 93%
            "status": ProjectStatus.ACTIVE.value,
            "completed_tasks": 9,
            "total_tasks": 10,
            "active_risks": "HEALTHY",
        },
        {
            "idx": 8,
            "student_id": STUDENT_IDS[8],
            "group_id": GROUP_IDS["sofia"],
            "mentor_id": MENTOR_IDS["sofia"],
            "name": "E-Learning Recommendation Engine v1",
            "phase": ProjectPhase.COMPLETED.value,
            "health": ProjectHealth.HEALTHY.value,
            "progress": 100,  # 100%
            "status": ProjectStatus.COMPLETED.value,
            "completed_tasks": 10,
            "total_tasks": 10,
            "active_risks": "HEALTHY",
        },
    ]

    for p in instances_config:
        inst_id = INSTANCE_IDS[p["idx"]]
        def_id = DEFINITION_IDS[p["idx"]]
        ver_id = VERSION_IDS[p["idx"]]

        # 1. Project Instance
        completed_at_val = datetime.now(UTC) - timedelta(days=1) if p["phase"] == "COMPLETED" else None
        inst_sql = text("""
            INSERT INTO project_instances (
                id, student_id, group_id, project_definition_id, source_definition_version_id,
                name, problem, proposed_solution, complexity, current_phase, health,
                progress_percentage, status, deadline, started_at, completed_at, created_at, updated_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:student_id AS uuid),
                CAST(:group_id AS uuid),
                CAST(:def_id AS uuid),
                CAST(:ver_id AS uuid),
                :name,
                'Primary problem statement identified in definition.',
                'Proposed architectural solution approach.',
                'INTERMEDIATE',
                :phase,
                :health,
                :progress,
                :status,
                NOW() + INTERVAL '60 days',
                NOW() - INTERVAL '30 days',
                :completed_at,
                NOW() - INTERVAL '30 days',
                NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                student_id = EXCLUDED.student_id,
                group_id = EXCLUDED.group_id,
                project_definition_id = EXCLUDED.project_definition_id,
                source_definition_version_id = EXCLUDED.source_definition_version_id,
                name = EXCLUDED.name,
                current_phase = EXCLUDED.current_phase,
                health = EXCLUDED.health,
                progress_percentage = EXCLUDED.progress_percentage,
                status = EXCLUDED.status,
                completed_at = EXCLUDED.completed_at,
                updated_at = NOW();
        """)
        await session.execute(inst_sql, {
            "id": inst_id,
            "student_id": p["student_id"],
            "group_id": p["group_id"],
            "def_id": def_id,
            "ver_id": ver_id,
            "name": p["name"],
            "phase": p["phase"],
            "health": p["health"],
            "progress": p["progress"],
            "status": p["status"],
            "completed_at": completed_at_val,
        })

        # 2. Project Profile
        prof_sql = text("""
            INSERT INTO project_profiles (
                id, project_instance_id, objective, target_users, project_type,
                student_skill_context, goals, scope, expected_outcome, constraints,
                assumptions, context, version, created_at, updated_at
            ) VALUES (
                gen_random_uuid(),
                CAST(:inst_id AS uuid),
                'Deliver a production-ready engineering capstone project adhering to GrowFlow standards.',
                'Targeting university students, faculty researchers, and industry mentors.',
                'CAPSTONE_ENGINEERING',
                'Advanced full-stack systems engineering & applied machine learning.',
                'Complete all canonical milestones from assessment to deployment.',
                'End-to-end full stack architecture including automated test suites.',
                'Fully deployed verified working implementation with documentation.',
                'Budget < $300, 16-week delivery limit.',
                'Standard cloud and local compute resources available.',
                'Supervised under GrowFlow Mentor Program.',
                1,
                NOW(),
                NOW()
            )
            ON CONFLICT (project_instance_id) DO UPDATE SET
                objective = EXCLUDED.objective,
                updated_at = NOW();
        """)
        await session.execute(prof_sql, {"inst_id": inst_id})

        # 3. Blueprint (for projects >= PLANNING)
        if p["phase"] in (
            ProjectPhase.PLANNING.value,
            ProjectPhase.IMPLEMENTATION.value,
            ProjectPhase.TESTING.value,
            ProjectPhase.DEPLOYMENT.value,
            ProjectPhase.COMPLETED.value,
        ):
            bp_sql = text("""
                INSERT INTO blueprints (
                    id, project_instance_id, student_id, status, current_step,
                    progress_percent, qa_status, qa_score, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(),
                    CAST(:inst_id AS uuid),
                    CAST(:student_id AS uuid),
                    'APPROVED',
                    'COMPLETED',
                    100,
                    'PASS',
                    95,
                    NOW() - INTERVAL '20 days',
                    NOW()
                )
                ON CONFLICT (project_instance_id) DO UPDATE SET
                    status = 'APPROVED',
                    progress_percent = 100,
                    qa_status = 'PASS',
                    updated_at = NOW();
            """)
            await session.execute(bp_sql, {"inst_id": inst_id, "student_id": p["student_id"]})

        # 4. Milestones & Tasks
        await seed_milestones_and_tasks(session, inst_id, p["idx"], p["completed_tasks"], p["total_tasks"])

        # 5. Risks
        await seed_risks(session, inst_id, p["idx"], p["active_risks"])

        # 6. Documents
        await seed_documents(session, inst_id, p["idx"])

        # 7. Histories & Activity Events
        await seed_histories_and_events(session, inst_id, p["idx"], p["student_id"], p["mentor_id"], p["group_id"], p["phase"], p["health"])


async def seed_milestones_and_tasks(
    session: Any,
    inst_id: str,
    idx: int,
    completed_tasks: int,
    total_tasks: int,
) -> None:
    """Seed canonical milestones and tasks matching the target completion count."""
    milestones_data = [
        {"code": "GATE-01", "title": "Milestone 1: Project Foundation & Architecture", "order": 1},
        {"code": "GATE-02", "title": "Milestone 2: Core Implementation & API Development", "order": 2},
        {"code": "GATE-03", "title": "Milestone 3: Verification, QA & Automated Testing", "order": 3},
        {"code": "GATE-04", "title": "Milestone 4: Deployment & Final Presentation", "order": 4},
    ]

    m_ids = []
    for m_idx, m in enumerate(milestones_data, 1):
        m_id = f"e1000000-{idx:04d}-0000-0000-{m_idx:012d}"
        m_ids.append(m_id)

        # Milestone status and progress based on completed tasks
        m_progress = 0
        m_status = "UPCOMING"
        if completed_tasks >= m_idx * 3:
            m_progress = 100
            m_status = "COMPLETED"
        elif completed_tasks >= (m_idx - 1) * 3:
            m_progress = 50
            m_status = "IN_PROGRESS"

        m_sql = text("""
            INSERT INTO project_milestones (
                id, project_instance_id, title, description, gate_code,
                target_date, status, progress_percent, deliverables, section_order, created_at, updated_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:inst_id AS uuid),
                :title,
                'Deliverables and criteria for this stage.',
                :code,
                NOW() + INTERVAL '30 days',
                :status,
                :progress,
                '["Architecture Diagram", "API Specification", "Test Report"]',
                :order,
                NOW() - INTERVAL '25 days',
                NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                status = EXCLUDED.status,
                progress_percent = EXCLUDED.progress_percent,
                updated_at = NOW();
        """)
        await session.execute(m_sql, {
            "id": m_id,
            "inst_id": inst_id,
            "title": m["title"],
            "code": m["code"],
            "status": m_status,
            "progress": m_progress,
            "order": m["order"],
        })

    # Tasks
    if total_tasks == 0:
        return

    task_definitions = [
        ("TSK-001", "Setup git repository and development environment", "PLANNING", 0),
        ("TSK-002", "Define database schema and Alembic migrations", "PLANNING", 0),
        ("TSK-003", "Configure CI/CD automated linting and test pipeline", "PLANNING", 0),
        ("TSK-004", "Implement core domain models and validation rules", "IMPLEMENTATION", 1),
        ("TSK-005", "Build REST API routes and authentication dependency", "IMPLEMENTATION", 1),
        ("TSK-006", "Integrate third-party peripheral connectors / SDKs", "IMPLEMENTATION", 1),
        ("TSK-007", "Write unit test suite for business domain services", "TESTING", 2),
        ("TSK-008", "Conduct integration tests and edge failure simulations", "TESTING", 2),
        ("TSK-009", "Perform security audit and performance benchmark", "DEPLOYMENT", 3),
        ("TSK-010", "Deploy production release container and run verification", "DEPLOYMENT", 3),
    ]

    for t_idx, (t_code, t_title, t_phase, m_assigned_idx) in enumerate(task_definitions[:total_tasks], 1):
        t_id = f"a1000000-{idx:04d}-0000-0000-{t_idx:012d}"
        m_id = m_ids[m_assigned_idx]

        # Determine task status
        if t_idx <= completed_tasks:
            t_status = "COMPLETED"
            t_completed_at = datetime.now(UTC) - timedelta(days=2)
        elif t_idx == completed_tasks + 1:
            t_status = "IN_PROGRESS"
            t_completed_at = None
        elif t_idx == completed_tasks + 2 and idx in (2, 3, 4):  # Blocked task for at-risk projects
            t_status = "BLOCKED"
            t_completed_at = None
        else:
            t_status = "TODO"
            t_completed_at = None

        t_sql = text("""
            INSERT INTO project_tasks (
                id, project_instance_id, milestone_id, task_code, title, description,
                status, priority, category, phase, due_date, completed_at, created_at, updated_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:inst_id AS uuid),
                CAST(:m_id AS uuid),
                :code,
                :title,
                'Detailed execution task specification and acceptance criteria.',
                :status,
                'HIGH',
                'Core',
                :phase,
                NOW() + INTERVAL '14 days',
                :completed_at,
                NOW() - INTERVAL '20 days',
                NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                status = EXCLUDED.status,
                completed_at = EXCLUDED.completed_at,
                updated_at = NOW();
        """)
        await session.execute(t_sql, {
            "id": t_id,
            "inst_id": inst_id,
            "m_id": m_id,
            "code": t_code,
            "title": t_title,
            "status": t_status,
            "phase": t_phase,
            "completed_at": t_completed_at,
        })


async def seed_risks(session: Any, inst_id: str, idx: int, risk_level: str) -> None:
    """Seed project risks covering HEALTHY, WARNING, and CRITICAL severity."""
    risks = []
    if risk_level == "CRITICAL":
        risks = [
            {
                "r_idx": 1,
                "code": "RSK-001",
                "title": "Hardware/API Deprecation and Breaking Protocol Changes",
                "severity": "CRITICAL",
                "prob": "HIGH",
                "impact": "HIGH",
                "status": "OPEN",
                "mitigation": "Refactor SDK abstraction layer to support fallback API protocol.",
            },
            {
                "r_idx": 2,
                "code": "RSK-002",
                "title": "Severe Database Query Latency Under Peak Concurrency",
                "severity": "HIGH",
                "prob": "MEDIUM",
                "impact": "HIGH",
                "status": "OPEN",
                "mitigation": "Add composite indexes and implement Redis response cache.",
            },
        ]
    elif risk_level == "WARNING":
        risks = [
            {
                "r_idx": 1,
                "code": "RSK-001",
                "title": "Milestone Delivery Schedule Slippage",
                "severity": "HIGH",
                "prob": "HIGH",
                "impact": "MEDIUM",
                "status": "OPEN",
                "mitigation": "Descope non-essential UI animations and prioritize core endpoints.",
            },
            {
                "r_idx": 2,
                "code": "RSK-002",
                "title": "Third-Party Rate Limiting on External Geocoding",
                "severity": "MEDIUM",
                "prob": "LOW",
                "impact": "MEDIUM",
                "status": "OPEN",
                "mitigation": "Apply client-side debouncing and cache previous lookups locally.",
            },
        ]
    else:  # HEALTHY
        risks = [
            {
                "r_idx": 1,
                "code": "RSK-001",
                "title": "Minor Browser Styling Drift on Mobile Viewports",
                "severity": "LOW",
                "prob": "LOW",
                "impact": "LOW",
                "status": "OPEN",
                "mitigation": "Conduct responsive CSS sweep across 390px and 768px breakpoints.",
            },
            {
                "r_idx": 2,
                "code": "RSK-002",
                "title": "Initial Build Container Image Size Optimization",
                "severity": "MEDIUM",
                "prob": "LOW",
                "impact": "LOW",
                "status": "MITIGATED",
                "mitigation": "Adopt multi-stage Docker builds to reduce image footprint.",
            },
        ]

    for r in risks:
        r_id = f"b1000000-{idx:04d}-0000-0000-{r['r_idx']:012d}"
        r_sql = text("""
            INSERT INTO project_risks (
                id, project_instance_id, risk_code, title, description,
                severity, probability, impact, status, mitigation, owner, created_at, updated_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:inst_id AS uuid),
                :code,
                :title,
                'Identified risk factor impacting project execution velocity and stability.',
                :severity,
                :prob,
                :impact,
                :status,
                :mitigation,
                'Student',
                NOW() - INTERVAL '15 days',
                NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                severity = EXCLUDED.severity,
                status = EXCLUDED.status,
                mitigation = EXCLUDED.mitigation,
                updated_at = NOW();
        """)
        await session.execute(r_sql, {
            "id": r_id,
            "inst_id": inst_id,
            "code": r["code"],
            "title": r["title"],
            "severity": r["severity"],
            "prob": r["prob"],
            "impact": r["impact"],
            "status": r["status"],
            "mitigation": r["mitigation"],
        })


async def seed_documents(session: Any, inst_id: str, idx: int) -> None:
    """Seed canonical project documents."""
    docs = [
        {
            "d_idx": 1,
            "key": "project_overview",
            "title": "Project Overview & Vision",
            "type": "SPECIFICATION",
            "content": "# Project Overview\n\nExecutive summary of system goals, target audience, and architectural milestones.",
        },
        {
            "d_idx": 2,
            "key": "system_requirements",
            "title": "System Requirements Specification",
            "type": "SPECIFICATION",
            "content": "# Requirements\n\n- FR-01: Authentication with JWT\n- FR-02: Real-time telemetry sync\n- NFR-01: Latency < 200ms",
        },
        {
            "d_idx": 3,
            "key": "architecture_design",
            "title": "System Architecture & Component Diagram",
            "type": "ARCHITECTURE",
            "content": "# Architecture\n\nModular class-based architecture adhering to DDD patterns and SQLAlchemy transactional outbox.",
        },
        {
            "d_idx": 4,
            "key": "api_specification",
            "title": "API Specification & Contract",
            "type": "SPECIFICATION",
            "content": "# API Contract\n\n- GET /api/v1/health\n- POST /api/v1/telemetry\n- GET /api/v1/reports",
        },
        {
            "d_idx": 5,
            "key": "testing_notes",
            "title": "Verification Notes & Test Matrix",
            "type": "REPORT",
            "content": "# Test Matrix\n\n- Unit tests: 100% core domain coverage\n- Integration tests: End-to-end API verification passing.",
        },
    ]

    for d in docs:
        d_id = f"d1000000-{idx:04d}-0000-0000-{d['d_idx']:012d}"
        doc_sql = text("""
            INSERT INTO project_documents (
                id, project_instance_id, document_key, title, doc_type,
                format, content, version, status, source, created_at, updated_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:inst_id AS uuid),
                :key,
                :title,
                :type,
                'markdown',
                :content,
                '1.0.0',
                'ACTIVE',
                'STUDENT_CREATED',
                NOW() - INTERVAL '10 days',
                NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                updated_at = NOW();
        """)
        await session.execute(doc_sql, {
            "id": d_id,
            "inst_id": inst_id,
            "key": d["key"],
            "title": d["title"],
            "type": d["type"],
            "content": d["content"],
        })


async def seed_histories_and_events(
    session: Any,
    inst_id: str,
    idx: int,
    student_id: str,
    mentor_id: str,
    group_id: str,
    current_phase: str,
    current_health: str,
) -> None:
    """Seed historical phase/health transitions and canonical domain events."""
    # 1. Phase history
    ph_sql = text("""
        INSERT INTO project_phase_history (
            id, project_instance_id, previous_phase, new_phase, changed_by, reason, changed_at
        ) VALUES (
            CAST(:id AS uuid),
            CAST(:inst_id AS uuid),
            'IDEA',
            :phase,
            CAST(:student_id AS uuid),
            'Canonical progression through project milestone gates.',
            NOW() - INTERVAL '10 days'
        )
        ON CONFLICT (id) DO NOTHING;
    """)
    await session.execute(ph_sql, {
        "id": f"f1000000-{idx:04d}-0000-0000-000000000001",
        "inst_id": inst_id,
        "phase": current_phase,
        "student_id": student_id,
    })

    # 2. Health history
    hh_sql = text("""
        INSERT INTO project_health_history (
            id, project_instance_id, previous_health, new_health, changed_by, reason, changed_at
        ) VALUES (
            CAST(:id AS uuid),
            CAST(:inst_id AS uuid),
            'HEALTHY',
            :health,
            CAST(:mentor_id AS uuid),
            'Supervisory risk evaluation during cohort review.',
            NOW() - INTERVAL '5 days'
        )
        ON CONFLICT (id) DO NOTHING;
    """)
    await session.execute(hh_sql, {
        "id": f"f2000000-{idx:04d}-0000-0000-000000000001",
        "inst_id": inst_id,
        "health": current_health,
        "mentor_id": mentor_id,
    })

    # 3. Canonical Domain Events for S28 & M30 Activity Trail
    events_data = [
        {
            "e_idx": 1,
            "type": DomainEventType.PROJECT_CREATED.value,
            "actor_id": student_id,
            "role": "STUDENT",
            "meta": {"name": f"Project {idx}"},
            "days_ago": 25,
        },
        {
            "e_idx": 2,
            "type": DomainEventType.PROJECT_PHASE_CHANGED.value,
            "actor_id": student_id,
            "role": "STUDENT",
            "meta": {"previous_phase": "IDEA", "new_phase": current_phase},
            "days_ago": 18,
        },
        {
            "e_idx": 3,
            "type": DomainEventType.TASK_CREATED.value,
            "actor_id": student_id,
            "role": "STUDENT",
            "meta": {"title": "Setup development environment", "task_code": "TSK-001"},
            "days_ago": 14,
        },
        {
            "e_idx": 4,
            "type": DomainEventType.TASK_COMPLETED.value,
            "actor_id": student_id,
            "role": "STUDENT",
            "meta": {"title": "Setup development environment", "task_code": "TSK-001"},
            "days_ago": 12,
        },
        {
            "e_idx": 5,
            "type": DomainEventType.DOCUMENT_CREATED.value,
            "actor_id": student_id,
            "role": "STUDENT",
            "meta": {"title": "Project Overview & Vision", "document_key": "project_overview"},
            "days_ago": 10,
        },
        {
            "e_idx": 6,
            "type": DomainEventType.PROJECT_HEALTH_CHANGED.value,
            "actor_id": mentor_id,
            "role": "MENTOR",
            "meta": {"previous_health": "HEALTHY", "new_health": current_health},
            "days_ago": 5,
        },
    ]

    for e in events_data:
        e_id = f"e2000000-{idx:04d}-0000-0000-{e['e_idx']:012d}"
        occurred_time = datetime.now(UTC) - timedelta(days=e["days_ago"])
        e_sql = text("""
            INSERT INTO domain_events (
                id, event_type, actor_id, actor_role, resource_type, resource_id,
                project_instance_id, group_id, visibility, metadata, correlation_id,
                status, occurred_at, published_at, attempt_count
            ) VALUES (
                CAST(:id AS uuid),
                :type,
                CAST(:actor_id AS uuid),
                :role,
                'project_instance',
                :res_id,
                CAST(:inst_id AS uuid),
                CAST(:group_id AS uuid),
                'MENTOR',
                CAST(:meta AS jsonb),
                'CORR-DEMO-SEED',
                'PUBLISHED',
                :occurred_at,
                :occurred_at,
                1
            )
            ON CONFLICT (id) DO UPDATE SET
                event_type = EXCLUDED.event_type,
                metadata = EXCLUDED.metadata;
        """)
        await session.execute(e_sql, {
            "id": e_id,
            "type": e["type"],
            "actor_id": e["actor_id"],
            "role": e["role"],
            "res_id": inst_id,
            "inst_id": inst_id,
            "group_id": group_id,
            "meta": json.dumps(e["meta"]),
            "occurred_at": occurred_time,
        })


async def seed_communication(session: Any) -> None:
    """Seed initial Help Requests and Mentor Notes for Batch 5 communication verification."""
    # 1. Project Help Requests
    help_requests = [
        {
            "id": "eeeeeeee-0001-0000-0000-000000000001",
            "project_instance_id": INSTANCE_IDS[1],
            "student_id": STUDENT_IDS[1],
            "subject": "Assistance with ROS2 camera driver interface",
            "description": "Encountering intermittent frame drops during drone vision sensor calibration in Gazebo.",
            "category": "TECHNICAL",
            "priority": "HIGH",
            "status": "OPEN",
            "mentor_response": None,
            "resolved_at": None,
        },
        {
            "id": "eeeeeeee-0002-0000-0000-000000000002",
            "project_instance_id": INSTANCE_IDS[2],
            "student_id": STUDENT_IDS[2],
            "subject": "Smart contract reentrancy guard verification",
            "description": "Need guidance on OpenZeppelin ReentrancyGuard implementation across yield vaults.",
            "category": "SECURITY",
            "priority": "MEDIUM",
            "status": "RESOLVED",
            "mentor_response": "Verified the checks-effects-interactions pattern. Use the standard nonReentrant modifier on external settlement endpoints.",
            "resolved_at": datetime.now(UTC) - timedelta(days=2),
        },
        {
            "id": "eeeeeeee-0004-0000-0000-000000000004",
            "project_instance_id": INSTANCE_IDS[4],
            "student_id": STUDENT_IDS[4],
            "subject": "Kafka partition sizing for payment events",
            "description": "Estimating partition throughput for high-frequency settlement pipeline.",
            "category": "ARCHITECTURE",
            "priority": "MEDIUM",
            "status": "OPEN",
            "mentor_response": None,
            "resolved_at": None,
        },
    ]

    for hr in help_requests:
        hr_sql = text("""
            INSERT INTO project_help_requests (
                id, project_instance_id, student_id, subject, description,
                category, priority, status, mentor_response, resolved_at,
                created_at, updated_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:project_instance_id AS uuid),
                CAST(:student_id AS uuid),
                :subject,
                :description,
                :category,
                :priority,
                :status,
                :mentor_response,
                :resolved_at,
                NOW() - INTERVAL '3 days',
                NOW()
            ) ON CONFLICT (id) DO UPDATE SET
                subject = EXCLUDED.subject,
                description = EXCLUDED.description,
                status = EXCLUDED.status,
                mentor_response = EXCLUDED.mentor_response,
                resolved_at = EXCLUDED.resolved_at,
                updated_at = NOW();
        """)
        await session.execute(hr_sql, hr)

    # 2. Project Mentor Notes
    mentor_notes = [
        {
            "id": "ffffffff-0001-0000-0000-000000000001",
            "project_instance_id": INSTANCE_IDS[1],
            "mentor_id": MENTOR_IDS["elena"],
            "title": "Milestone 2 Vision Architecture Review",
            "message": "Drone sensor pipeline looks solid. Ensure real-time failover handles sensor latency over 150ms.",
            "note_type": "FEEDBACK",
            "status": "UNREAD",
            "related_resource_type": "MILESTONE",
            "related_resource_id": None,
        },
        {
            "id": "ffffffff-0002-0000-0000-000000000002",
            "project_instance_id": INSTANCE_IDS[1],
            "mentor_id": MENTOR_IDS["elena"],
            "title": "Internal Cohort Assessment — Flight Safety",
            "message": "Student progressing well ahead of schedule. Candidate for lab hardware loan.",
            "note_type": "INTERNAL",
            "status": "UNREAD",
            "related_resource_type": "PROJECT",
            "related_resource_id": None,
        },
        {
            "id": "ffffffff-0003-0000-0000-000000000003",
            "project_instance_id": INSTANCE_IDS[2],
            "mentor_id": MENTOR_IDS["elena"],
            "title": "Gas Optimization Checklist",
            "message": "Review state storage layout to avoid redundant SLOAD operations in batch transfers.",
            "note_type": "ACTIONABLE",
            "status": "ACKNOWLEDGED",
            "related_resource_type": "TASK",
            "related_resource_id": None,
        },
    ]

    for mn in mentor_notes:
        mn_sql = text("""
            INSERT INTO project_mentor_notes (
                id, project_instance_id, mentor_id, title, message,
                note_type, status, related_resource_type, related_resource_id,
                created_at, updated_at
            ) VALUES (
                CAST(:id AS uuid),
                CAST(:project_instance_id AS uuid),
                CAST(:mentor_id AS uuid),
                :title,
                :message,
                :note_type,
                :status,
                :related_resource_type,
                :related_resource_id,
                NOW() - INTERVAL '2 days',
                NOW()
            ) ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                message = EXCLUDED.message,
                note_type = EXCLUDED.note_type,
                status = EXCLUDED.status,
                updated_at = NOW();
        """)
        await session.execute(mn_sql, mn)


async def run_seed() -> None:
    """Execute complete deterministic seed operation."""
    print("=" * 60)
    print("GrowFlow — Initializing Persistent Demo / QA Dataset")
    print("=" * 60)

    settings = get_settings()
    await startup(settings.database)
    factory = get_session_factory()

    async with factory() as session:
        print("\n1. Seeding 3 Mentors (Elena Vance, Arjun Mehta, Sofia Chen)...")
        await seed_mentors(session)

        print("\n2. Seeding 8 Students (Aarav, Riya, Kabir, Anaya, Vihaan, Meera, Arjun G., Isha)...")
        await seed_students(session)

        print("\n3. Seeding 3 Supervised Groups and Memberships...")
        await seed_groups_and_memberships(session)

        print("\n4. Seeding 8 Project Definitions & Pinned Immutable Versions...")
        await seed_definitions_and_versions(session)

        print("\n5. Seeding 8 Project Instances, Milestones, Tasks, Risks, Documents, & Events...")
        await seed_project_instances(session)

        print("\n6. Seeding Initial Help Requests and Mentor Notes (Batch 5)...")
        await seed_communication(session)

        await session.commit()
        print("\nSUCCESS! All demo data committed to PostgreSQL & Supabase Auth.")

    await shutdown()
    print("=" * 60)
    print("GrowFlow Demo Dataset Seeding Complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_seed())
