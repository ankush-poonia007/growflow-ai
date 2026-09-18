"""
GrowFlow — Repository Base Class.

Provides the canonical abstract base class for all GrowFlow repository
implementations. Gate 03 authorises the data-access foundation only;
domain-specific repositories are introduced in Gate 05 and later gates.

Architecture ref:
  - 6A § 7 — Repository Architecture
  - 6A § 9 — Class-Based Architecture
  - 6B § 57 — Database Architecture Rules (no raw SQL in routes/agents)

Pattern:
  - Repositories own persistence access.
  - Repositories do not own business rules, notifications, AI calls, or HTTP formatting.
  - Application/domain code depends on repository contracts.
  - Infrastructure implements them.

The BaseRepository provides:
  - Session reference management.
  - Common CRUD primitives.
  - Typed return signatures using SQLAlchemy 2.0 patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar
from uuid import UUID  # noqa: TC003 — used at runtime in method signatures

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,  # noqa: TC002 — used at runtime in method signatures
)

from backend.app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from collections.abc import Sequence

# Generic type variable bound to the SQLAlchemy declarative Base.
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository[ModelT: Base]:
    """
    Abstract base repository providing common async CRUD operations.

    Subclasses must define the model class in their __init__ or class body.
    All database access goes through the injected AsyncSession.

    Transaction control is the responsibility of the calling application
    service / use-case layer. Repositories do not commit or rollback;
    they operate within the session provided to them.
    """

    def __init__(self, session: AsyncSession, model_class: type[ModelT]) -> None:
        """
        Initialise the repository with a session and model class.

        Args:
            session: The async database session for this unit of work.
            model_class: The SQLAlchemy model class managed by this repository.
        """
        self._session = session
        self._model_class = model_class

    async def get_by_id(self, entity_id: UUID | str) -> ModelT | None:
        """
        Retrieve an entity by its primary key UUID.

        Args:
            entity_id: The UUID primary key of the entity.

        Returns:
            The entity instance, or None if not found.
        """
        result = await self._session.execute(
            select(self._model_class).where(
                self._model_class.id == str(entity_id)  # type: ignore[attr-defined]
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[ModelT]:
        """
        Retrieve all entities of this type.

        Use with caution in production — add pagination in application services.

        Returns:
            Sequence of all entity instances.
        """
        result = await self._session.execute(select(self._model_class))
        return result.scalars().all()

    async def add(self, entity: ModelT) -> ModelT:
        """
        Add a new entity to the session (does not commit).

        The caller's unit-of-work controls the commit boundary.

        Args:
            entity: The entity instance to persist.

        Returns:
            The same entity instance (unchanged; commit handled by caller).
        """
        self._session.add(entity)
        await self._session.flush()  # Flush to assign DB-generated values (e.g. server_default).
        await self._session.refresh(entity)
        return entity

    async def save(self, entity: ModelT) -> ModelT:
        """
        Save/flush updates to an entity in the session.
        """
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    update = save

    async def delete(self, entity: ModelT) -> None:
        """
        Mark an entity for deletion in the current session.

        The caller's unit-of-work controls the commit boundary.

        Args:
            entity: The entity instance to delete.
        """
        await self._session.delete(entity)
        await self._session.flush()
