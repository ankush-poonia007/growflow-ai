"""Auth user provisioning trigger and reconciliation.

Revision ID: 0012_auth_user_provisioning
Revises: 0011_gate09_agent_executions
Create Date: 2026-10-25 UTC

Authorised by: GF-FIX-01 — Authentication, User Provisioning, and RBAC
Architecture ref:
  6B § 5.1 — Canonical users identity record
  6D § 3-4 — Supabase Auth User UUID -> GrowFlow users.id
  6D § 7   — Default STUDENT role, ACTIVE status
  6D § 33-34 — Safe defense-in-depth RLS and idempotent provisioning
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic (<= 32 chars for alembic_version column limit).
revision: str = "0012_auth_user_provisioning"
down_revision: str | None = "0011_gate09_agent_executions"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create auth user provisioning trigger, function, and safe reconciliation backfill."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # 1. Create or replace the trigger function
        op.execute("""
            CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
            RETURNS trigger AS $$
            BEGIN
                INSERT INTO public.users (id, email, full_name, role, status, created_at, updated_at)
                VALUES (
                    new.id::text,
                    coalesce(lower(new.email), ''),
                    coalesce(new.raw_user_meta_data->>'full_name', ''),
                    'STUDENT',
                    'ACTIVE',
                    now(),
                    now()
                )
                ON CONFLICT (id) DO NOTHING;
                RETURN new;
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;
        """)

        # 2. Grant permissions on the trigger function
        op.execute("""
            GRANT EXECUTE ON FUNCTION public.handle_new_auth_user() TO postgres, service_role;
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_auth_admin') THEN
                    GRANT EXECUTE ON FUNCTION public.handle_new_auth_user() TO supabase_auth_admin;
                END IF;
            END
            $$;
        """)

        # 3. Create triggers on auth.users if auth schema exists
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    -- Drop triggers if they exist to ensure idempotency
                    DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
                    DROP TRIGGER IF EXISTS on_auth_user_confirmed ON auth.users;

                    -- Trigger 1: Fire on new user signup
                    CREATE TRIGGER on_auth_user_created
                        AFTER INSERT ON auth.users
                        FOR EACH ROW
                        EXECUTE FUNCTION public.handle_new_auth_user();

                    -- Trigger 2: Fire when an existing user confirms email
                    CREATE TRIGGER on_auth_user_confirmed
                        AFTER UPDATE OF email_confirmed_at ON auth.users
                        FOR EACH ROW
                        WHEN (OLD.email_confirmed_at IS NULL AND NEW.email_confirmed_at IS NOT NULL)
                        EXECUTE FUNCTION public.handle_new_auth_user();
                END IF;
            END
            $$;
        """)

        # 4. Safe reconciliation backfill for existing email-confirmed users in auth.users
        # Only provisions users who have confirmed their email and do not already exist in public.users.
        # Strictly assigns STUDENT role and ACTIVE status, preserving any existing records.
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    INSERT INTO public.users (id, email, full_name, role, status, created_at, updated_at)
                    SELECT
                        u.id::text,
                        coalesce(lower(u.email), ''),
                        coalesce(u.raw_user_meta_data->>'full_name', ''),
                        'STUDENT',
                        'ACTIVE',
                        now(),
                        now()
                    FROM auth.users u
                    LEFT JOIN public.users p ON p.id = u.id::text
                    WHERE p.id IS NULL AND u.email_confirmed_at IS NOT NULL
                    ON CONFLICT (id) DO NOTHING;
                END IF;
            END
            $$;
        """)


def downgrade() -> None:
    """Drop provisioning triggers and function."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    DROP TRIGGER IF EXISTS on_auth_user_confirmed ON auth.users;
                    DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
                END IF;
            END
            $$;
        """)
        op.execute("DROP FUNCTION IF EXISTS public.handle_new_auth_user()")
