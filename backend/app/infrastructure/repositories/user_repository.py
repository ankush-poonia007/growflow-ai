"""
GrowFlow — User Repository Implementation.

Concrete repository providing async database operations for UserModel.
Integrates with the BaseRepository foundation established in Gate 03.

Architecture ref:
  6A § 7 — Repository Architecture: UserRepository
  6B § 5.1 — users table persistence
  6D § 4 — Identity mapping and retrieval by UUID
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[UserModel]):
    """
    Repository for UserModel entities.

    Provides domain query and persistence operations for application identity.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=UserModel)

    async def get_by_id(self, entity_id: UUID | str) -> UserModel | None:
        """
        Retrieve a user record by its primary key UUID.

        Args:
            entity_id: The UUID or stringified UUID of the user.

        Returns:
            The UserModel instance, or None if not found.
        """
        return await super().get_by_id(str(entity_id))

    async def get_by_email(self, email: str) -> UserModel | None:
        """
        Retrieve a user record by normalized email address.

        Args:
            email: Email address to look up.

        Returns:
            The UserModel instance, or None if not found.
        """
        result = await self._session.execute(
            select(self._model_class).where(self._model_class.email == email.strip().lower())
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        *,
        user_id: UUID | str,
        email: str,
        role: str = "STUDENT",
        status: str = "ACTIVE",
        full_name: str = "",
        avatar_url: str | None = None,
    ) -> UserModel:
        """
        Create and persist a new user identity record.

        Args:
            user_id: UUID corresponding to the Supabase Auth sub claim.
            email: User email address.
            role: Application role string.
            status: Account lifecycle status string.
            full_name: Optional display name.
            avatar_url: Optional avatar URL.

        Returns:
            The persisted UserModel instance.
        """
        user = UserModel(
            id=str(user_id),
            email=email.strip().lower(),
            role=role,
            status=status,
            full_name=full_name,
            avatar_url=avatar_url,
        )
        return await self.add(user)

    async def update_last_login(self, user: UserModel) -> None:
        """
        Update the user's last_login_at timestamp in UTC.

        Args:
            user: The UserModel instance to update.
        """
        user.last_login_at = datetime.now(UTC)
        await self._session.flush()
