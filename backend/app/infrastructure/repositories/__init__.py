"""
GrowFlow — Repository Infrastructure Package.

Exports:
  - BaseRepository: Abstract base for all GrowFlow repository implementations.
  - UserRepository: Concrete repository for UserModel and identity persistence.
"""

from backend.app.infrastructure.repositories.base import BaseRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
]
