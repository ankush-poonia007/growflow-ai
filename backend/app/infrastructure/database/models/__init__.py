"""
GrowFlow — Database ORM Models Package.

Registers all SQLAlchemy ORM models with Base.metadata.
"""

from backend.app.infrastructure.database.models.user import UserModel

__all__ = [
    "UserModel",
]
