"""
GrowFlow — Database Infrastructure Package.

Public surface:
- Base: SQLAlchemy declarative base (all models inherit from this)
- TimestampMixin: UTC created_at / updated_at columns
- UUIDPrimaryKeyMixin: UUID primary key column
- lifecycle: engine startup / shutdown
- engine: engine / session factory builders
- exceptions: database exception → GrowFlow exception mapping
"""

from backend.app.infrastructure.database import lifecycle
from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.infrastructure.database.engine import (
    build_async_engine,
    build_async_session_factory,
    get_session_context,
)
from backend.app.infrastructure.database.exceptions import (
    handle_integrity_error,
    handle_no_result_found,
    handle_operational_error,
    handle_sqlalchemy_error,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "build_async_engine",
    "build_async_session_factory",
    "get_session_context",
    "handle_integrity_error",
    "handle_no_result_found",
    "handle_operational_error",
    "handle_sqlalchemy_error",
    "lifecycle",
]
