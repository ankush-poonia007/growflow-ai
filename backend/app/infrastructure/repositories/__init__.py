"""
GrowFlow — Repository Infrastructure Package.

Exports:
  - BaseRepository: Abstract base for all GrowFlow repository implementations.

Domain repositories (UserRepository, ProjectRepository, etc.) are added in
Gate 05 and later gates, as authorized by the master plan.
"""

from backend.app.infrastructure.repositories.base import BaseRepository

__all__ = ["BaseRepository"]
