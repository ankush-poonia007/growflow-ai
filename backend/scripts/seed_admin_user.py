"""
GrowFlow — Provision Admin User for Local Development and QA.

Seeds a deterministic Admin account:
Email: admin@growflow.ai
Password: GrowFlow2026!Demo
Role: ADMIN
Status: ACTIVE
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text

from backend.app.config.settings import get_settings
from backend.app.infrastructure.database.lifecycle import (
    get_session_factory,
    shutdown,
    startup,
)

ADMIN_USER_ID = "00000000-0000-0000-0000-000000000001"
ADMIN_EMAIL = "admin@growflow.ai"
ADMIN_FULL_NAME = "GrowFlow Administrator"
ADMIN_PASSWORD = "GrowFlow2026!Demo"
ADMIN_ROLE = "ADMIN"


async def main() -> None:
    settings = get_settings()
    await startup(settings.database)

    meta = json.dumps({
        "sub": ADMIN_USER_ID,
        "email": ADMIN_EMAIL,
        "full_name": ADMIN_FULL_NAME,
        "role": ADMIN_ROLE,
    })

    async with get_session_factory()() as session:
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
                updated_at = NOW();
        """)
        await session.execute(
            user_sql,
            {
                "user_id": ADMIN_USER_ID,
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "meta": meta,
            },
        )

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
        await session.execute(ident_sql, {"user_id": ADMIN_USER_ID, "meta": meta})

        # 3. Upsert public.users
        growflow_user_sql = text("""
            INSERT INTO users (id, email, full_name, role, status, created_at, updated_at)
            VALUES (CAST(:user_id AS uuid), :email, :full_name, 'ADMIN', 'ACTIVE', NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                full_name = EXCLUDED.full_name,
                role = 'ADMIN',
                status = 'ACTIVE',
                updated_at = NOW();
        """)
        await session.execute(
            growflow_user_sql,
            {
                "user_id": ADMIN_USER_ID,
                "email": ADMIN_EMAIL,
                "full_name": ADMIN_FULL_NAME,
            },
        )

        await session.commit()
        print(f"SUCCESS: Admin account provisioned: {ADMIN_EMAIL} (password: {ADMIN_PASSWORD})")

    await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
