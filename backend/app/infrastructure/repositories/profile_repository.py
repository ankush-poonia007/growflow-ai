"""
GrowFlow — Profile Repository Implementation.

Provides persistence operations for student profiles, mentor profiles,
and user preferences.

Architecture ref:
  6A § 7 — Repository Architecture
  6B § 5.2 — student_profiles
  6B § 5.3 — mentor_profiles
  6B § 5.4 — user_preferences
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from backend.app.infrastructure.database.models.profile import (
    MentorProfileModel,
    StudentProfileModel,
    UserPreferenceModel,
)
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class ProfileRepository(BaseRepository[StudentProfileModel]):
    """
    Repository managing profile-related entities for students, mentors, and user preferences.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=StudentProfileModel)

    async def get_student_profile(self, user_id: UUID | str) -> StudentProfileModel | None:
        result = await self._session.execute(
            select(StudentProfileModel).where(StudentProfileModel.user_id == str(user_id))
        )
        return result.scalar_one_or_none()

    async def get_student_profile_by_student_id(
        self, student_id: str
    ) -> StudentProfileModel | None:
        result = await self._session.execute(
            select(StudentProfileModel).where(StudentProfileModel.student_id == student_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update_student_profile(
        self,
        user_id: UUID | str,
        student_id: str,
        *,
        bio: str | None = None,
        goals: str | None = None,
        interests: str | None = None,
    ) -> StudentProfileModel:
        profile = await self.get_student_profile(user_id)
        if profile is None:
            profile = StudentProfileModel(
                user_id=str(user_id),
                student_id=student_id,
                bio=bio,
                goals=goals,
                interests=interests,
            )
            self._session.add(profile)
        else:
            if bio is not None:
                profile.bio = bio
            if goals is not None:
                profile.goals = goals
            if interests is not None:
                profile.interests = interests
        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def get_mentor_profile(self, user_id: UUID | str) -> MentorProfileModel | None:
        result = await self._session.execute(
            select(MentorProfileModel).where(MentorProfileModel.user_id == str(user_id))
        )
        return result.scalar_one_or_none()

    async def get_mentor_profile_by_mentor_id(self, mentor_id: str) -> MentorProfileModel | None:
        result = await self._session.execute(
            select(MentorProfileModel).where(MentorProfileModel.mentor_id == mentor_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update_mentor_profile(
        self,
        user_id: UUID | str,
        mentor_id: str,
        *,
        bio: str | None = None,
        specialization: str | None = None,
    ) -> MentorProfileModel:
        profile = await self.get_mentor_profile(user_id)
        if profile is None:
            profile = MentorProfileModel(
                user_id=str(user_id),
                mentor_id=mentor_id,
                bio=bio,
                specialization=specialization,
            )
            self._session.add(profile)
        else:
            if bio is not None:
                profile.bio = bio
            if specialization is not None:
                profile.specialization = specialization
        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def get_user_preferences(self, user_id: UUID | str) -> UserPreferenceModel | None:
        result = await self._session.execute(
            select(UserPreferenceModel).where(UserPreferenceModel.user_id == str(user_id))
        )
        return result.scalar_one_or_none()

    async def create_or_update_user_preferences(
        self,
        user_id: UUID | str,
        *,
        email_notifications: bool | None = None,
        timezone: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> UserPreferenceModel:
        prefs = await self.get_user_preferences(user_id)
        if prefs is None:
            prefs = UserPreferenceModel(
                user_id=str(user_id),
                email_notifications=True if email_notifications is None else email_notifications,
                timezone=timezone or "UTC",
                preferences=preferences or {},
            )
            self._session.add(prefs)
        else:
            if email_notifications is not None:
                prefs.email_notifications = email_notifications
            if timezone is not None:
                prefs.timezone = timezone
            if preferences is not None:
                prefs.preferences = preferences
        await self._session.flush()
        await self._session.refresh(prefs)
        return prefs
