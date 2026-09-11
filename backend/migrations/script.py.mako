"""
Alembic script.py.mako — migration template.

This template is used by Alembic's 'alembic revision' and
'alembic revision --autogenerate' commands to generate new migration files.

GrowFlow conventions:
- Each migration is forward-only (upgrade) with a reversible downgrade where practical.
- Never rewrite an applied migration.
- Migration file names use the timestamp slug format from alembic.ini.
"""
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
