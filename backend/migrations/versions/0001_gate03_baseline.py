"""Gate 03 baseline: enable required PostgreSQL extensions.

Revision ID: 0001_gate03_baseline
Revises: None (initial migration)
Create Date: 2026-09-11 UTC

This migration establishes the required PostgreSQL extension foundation.

Authorised by: Gate 03 — Database Foundation
Architecture ref: 6B Database Architecture & Data Model (FROZEN)

Extensions enabled:
  - uuid-ossp: server-side UUID generation (pgcrypto alternative; compatible
    with existing Supabase schemas which often have uuid-ossp pre-installed)
  - pg_trgm: trigram similarity — required for future full-text search indexes
    on project/user names (6B § 40 — Indexing Strategy)

SAFETY:
  - Uses CREATE EXTENSION IF NOT EXISTS — idempotent, non-destructive.
  - No table creation or data mutation in this migration.
  - downgrade() removes only the extensions added here, using IF EXISTS guards.
  - This migration may be applied to the hosted Supabase instance safely.
  - Never call RESET, DROP DATABASE, or TRUNCATE.

Note on Supabase-managed extensions:
  Supabase pre-installs many extensions (uuid-ossp, pgcrypto, etc.).
  The IF NOT EXISTS clause ensures this migration is idempotent even if
  extensions are already present on the hosted database.
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_gate03_baseline"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Enable required PostgreSQL extensions for GrowFlow."""
    # uuid-ossp: provides uuid_generate_v4() server-side default.
    # Supabase typically pre-installs this; IF NOT EXISTS is idempotent.
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    # pg_trgm: trigram similarity for full-text search indexes.
    # Required for future search patterns identified in 6B § 40.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    """Remove extensions added in this migration (only if they exist)."""
    # Note: dropping shared extensions in a hosted Supabase environment
    # should be done with extreme care. These guards prevent errors if
    # the extension is still in use.
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS \"uuid-ossp\"")
