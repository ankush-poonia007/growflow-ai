"""
GrowFlow — Profile Service Implementation.

Manages user, student, mentor profiles, and user preferences.

Architecture ref:
  6A § 9  — Class-Based Architecture
  6B § 5  — Identity & Access
  6C § 10 — User and Profile APIs
"""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING, Any

from backend.app.shared.exceptions import NotFoundException

if TYPE_CHECKING:
    from collections.abc import Sequence
    import uuid

    from backend.app.infrastructure.database.models.profile import (
        MentorProfileModel,
        StudentProfileModel,
        StudentTechnologyModel,
        UserPreferenceModel,
    )
    from backend.app.infrastructure.database.models.user import UserModel
    from backend.app.infrastructure.repositories.profile_repository import ProfileRepository
    from backend.app.infrastructure.repositories.technology_repository import TechnologyRepository
    from backend.app.infrastructure.repositories.user_repository import UserRepository


class ProfileService:
    """Application service for identity, profile, preferences, and technology skills."""

    def __init__(
        self,
        profile_repo: ProfileRepository,
        user_repo: UserRepository,
        technology_repo: TechnologyRepository,
    ) -> None:
        self._profile_repo = profile_repo
        self._user_repo = user_repo
        self._technology_repo = technology_repo

    async def get_user_self(self, user_id: uuid.UUID) -> UserModel:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User record not found.", code="USER_NOT_FOUND")
        return user

    async def update_user_self(
        self,
        user_id: uuid.UUID,
        *,
        full_name: str | None = None,
        avatar_url: str | None = None,
    ) -> UserModel:
        user = await self.get_user_self(user_id)
        if full_name is not None:
            user.full_name = full_name.strip()
        if avatar_url is not None:
            user.avatar_url = avatar_url.strip() if avatar_url else None
        return user

    async def get_or_create_student_profile(
        self, user_id: uuid.UUID
    ) -> tuple[StudentProfileModel, Sequence[StudentTechnologyModel]]:
        # Ensure user exists
        await self.get_user_self(user_id)
        profile = await self._profile_repo.get_student_profile(user_id)
        if profile is None:
            # Generate default student_id
            rand_suffix = secrets.token_hex(4).upper()
            student_id = f"STU-{rand_suffix}"
            profile = await self._profile_repo.create_or_update_student_profile(
                user_id=user_id, student_id=student_id
            )

        technologies = await self._technology_repo.get_student_technologies(user_id)
        return profile, technologies

    async def update_student_profile(
        self,
        user_id: uuid.UUID,
        *,
        bio: str | None = None,
        goals: str | None = None,
        interests: str | None = None,
        technologies: list[dict[str, Any]] | None = None,
    ) -> tuple[StudentProfileModel, Sequence[StudentTechnologyModel]]:
        profile, _ = await self.get_or_create_student_profile(user_id)
        updated_profile = await self._profile_repo.create_or_update_student_profile(
            user_id=user_id,
            student_id=profile.student_id,
            bio=bio,
            goals=goals,
            interests=interests,
        )

        if technologies is not None:
            for tech_entry in technologies:
                tech_id = tech_entry.get("technology_id")
                proficiency = tech_entry.get("proficiency", "INTERMEDIATE")
                rel_type = tech_entry.get("relationship_type", "KNOWN")
                if tech_id:
                    await self._technology_repo.add_student_technology(
                        student_id=user_id,
                        technology_id=tech_id,
                        proficiency=proficiency,
                        relationship_type=rel_type,
                    )

        tech_list = await self._technology_repo.get_student_technologies(user_id)
        return updated_profile, tech_list

    async def get_or_create_mentor_profile(self, user_id: uuid.UUID) -> MentorProfileModel:
        await self.get_user_self(user_id)
        profile = await self._profile_repo.get_mentor_profile(user_id)
        if profile is None:
            rand_suffix = secrets.token_hex(4).upper()
            mentor_id = f"MEN-{rand_suffix}"
            profile = await self._profile_repo.create_or_update_mentor_profile(
                user_id=user_id, mentor_id=mentor_id
            )
        return profile

    async def update_mentor_profile(
        self,
        user_id: uuid.UUID,
        *,
        bio: str | None = None,
        specialization: str | None = None,
    ) -> MentorProfileModel:
        profile = await self.get_or_create_mentor_profile(user_id)
        return await self._profile_repo.create_or_update_mentor_profile(
            user_id=user_id,
            mentor_id=profile.mentor_id,
            bio=bio,
            specialization=specialization,
        )

    async def get_or_create_preferences(self, user_id: uuid.UUID) -> UserPreferenceModel:
        await self.get_user_self(user_id)
        prefs = await self._profile_repo.get_user_preferences(user_id)
        if prefs is None:
            prefs = await self._profile_repo.create_or_update_user_preferences(user_id)
        return prefs

    async def update_preferences(
        self,
        user_id: uuid.UUID,
        *,
        email_notifications: bool | None = None,
        timezone: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> UserPreferenceModel:
        await self.get_user_self(user_id)
        return await self._profile_repo.create_or_update_user_preferences(
            user_id=user_id,
            email_notifications=email_notifications,
            timezone=timezone,
            preferences=preferences,
        )
