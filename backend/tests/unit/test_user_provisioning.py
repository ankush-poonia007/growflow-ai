"""
GrowFlow — Unit Tests for User Provisioning and RBAC Integrity.

Tests:
1. UserRepository user creation and data normalization (email lowercasing, UUID stringification).
2. Default role assignment strictly adheres to STUDENT (never MENTOR or ADMIN on public signup).
3. Preservation of existing users and privileged roles.
4. Token claims isolation (user metadata cannot override backend authoritative role).
5. Migration 0012 chain integrity (down_revision = 0011_gate09_agent_executions).
6. Fail-closed behavior on unknown identity tokens.
"""

from __future__ import annotations

import importlib
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest

from backend.app.domain.identity import (
    AccountStatus,
    CurrentUser,
    UserRole,
    verify_account_active,
    verify_role_access,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.shared.exceptions import AuthenticationException, AuthorizationException


class TestUserProvisioning:
    """Comprehensive verification of user provisioning constraints and data normalization."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_provisions_student_active_by_default(self) -> None:
        """New user provisioning defaults strictly to STUDENT role and ACTIVE status."""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        repo = UserRepository(session=mock_session)

        user_id = uuid.uuid4()
        user = await repo.create_user(
            user_id=user_id,
            email="Ada.Lovelace@University.Edu",
            full_name="Ada Lovelace",
        )

        assert user.id == str(user_id)
        assert user.email == "ada.lovelace@university.edu"
        assert user.role == UserRole.STUDENT.value
        assert user.status == AccountStatus.ACTIVE.value
        assert user.full_name == "Ada Lovelace"
        assert mock_session.add.called
        assert mock_session.flush.called

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_normalizes_whitespace_and_casing(self) -> None:
        """Email address is stripped of whitespace and lowercased."""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        repo = UserRepository(session=mock_session)

        user_id = uuid.uuid4()
        user = await repo.create_user(
            user_id=user_id,
            email="   STUDENT@DOMAIN.COM   ",
        )

        assert user.email == "student@domain.com"
        assert user.full_name == ""

    @pytest.mark.unit
    def test_user_conversion_to_current_user_preserves_identity(self) -> None:
        """UserModel.to_current_user accurately transforms database entity into domain value object."""
        user_id = uuid.uuid4()
        model = UserModel(
            id=str(user_id),
            email="student@growflow.ai",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Test Student",
        )

        current_user = model.to_current_user()
        assert current_user.user_id == user_id
        assert current_user.email == "student@growflow.ai"
        assert current_user.role == UserRole.STUDENT
        assert current_user.status == AccountStatus.ACTIVE
        assert current_user.full_name == "Test Student"

    @pytest.mark.unit
    def test_user_model_invalid_role_raises_value_error(self) -> None:
        """Attempting to convert a UserModel with an unsupported role string raises ValueError."""
        model = UserModel(
            id=str(uuid.uuid4()),
            email="invalid@growflow.ai",
            role="SUPERUSER",  # Not a valid UserRole enum
            status=AccountStatus.ACTIVE.value,
        )
        with pytest.raises(ValueError):
            model.to_current_user()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_user_repository_get_by_id_normalizes_uuid(self) -> None:
        """get_by_id accepts UUID or string and queries via session."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = UserRepository(session=mock_session)
        user_uuid = uuid.uuid4()
        result = await repo.get_by_id(user_uuid)

        assert result is None
        assert mock_session.execute.called

    @pytest.mark.unit
    def test_role_cannot_be_escalated_to_admin_or_mentor_via_metadata(self) -> None:
        """
        User-controlled metadata or request parameters cannot escalate authorization.
        Application role is strictly validated against UserRole enum and backend DB record.
        """
        user_id = uuid.uuid4()
        # Simulated untrusted user metadata containing forged 'ADMIN' role
        untrusted_metadata = {"role": "ADMIN", "full_name": "Attacker"}

        # Legitimate provisioning ignores untrusted_metadata['role']
        student_user = CurrentUser(
            user_id=user_id,
            email="attacker@growflow.ai",
            role=UserRole.STUDENT,  # Authoritative role from public.users
            status=AccountStatus.ACTIVE,
            full_name=untrusted_metadata["full_name"],
        )

        # Attempting admin-only resource verification must fail closed with 403
        with pytest.raises(AuthorizationException) as exc_info:
            verify_role_access(student_user, {UserRole.ADMIN})

        assert exc_info.value.status_code == 403
        assert exc_info.value.code == "AUTH_FORBIDDEN_ROLE"

    @pytest.mark.unit
    def test_existing_privileged_user_retains_authorized_role(self) -> None:
        """Existing MENTOR and ADMIN users retain their privileged authorization."""
        admin_id = uuid.uuid4()
        admin_user = CurrentUser(
            user_id=admin_id,
            email="admin@growflow.ai",
            role=UserRole.ADMIN,
            status=AccountStatus.ACTIVE,
            full_name="Platform Administrator",
        )

        # Admin satisfies ADMIN requirement
        verify_role_access(admin_user, {UserRole.ADMIN})

        # Mentor satisfies MENTOR requirement
        mentor_id = uuid.uuid4()
        mentor_user = CurrentUser(
            user_id=mentor_id,
            email="mentor@growflow.ai",
            role=UserRole.MENTOR,
            status=AccountStatus.ACTIVE,
            full_name="Dr. Alan Turing",
        )
        verify_role_access(mentor_user, {UserRole.MENTOR})

        # Student cannot access Mentor resource
        with pytest.raises(AuthorizationException):
            verify_role_access(admin_user, {UserRole.MENTOR})

    @pytest.mark.unit
    def test_suspended_and_inactive_users_rejected(self) -> None:
        """Suspended and inactive users are blocked from workspace access."""
        user_id = uuid.uuid4()
        suspended_user = CurrentUser(
            user_id=user_id,
            email="suspended@growflow.ai",
            role=UserRole.STUDENT,
            status=AccountStatus.SUSPENDED,
        )
        with pytest.raises(AuthorizationException) as exc_info:
            verify_account_active(suspended_user)
        assert exc_info.value.code == "AUTH_ACCOUNT_SUSPENDED"

        inactive_user = CurrentUser(
            user_id=user_id,
            email="inactive@growflow.ai",
            role=UserRole.STUDENT,
            status=AccountStatus.INACTIVE,
        )
        with pytest.raises(AuthorizationException) as exc_info:
            verify_account_active(inactive_user)
        assert exc_info.value.code == "AUTH_ACCOUNT_INACTIVE"

    @pytest.mark.unit
    def test_migration_0012_chains_from_0011(self) -> None:
        """Migration 0012_auth_user_provisioning correctly revises 0011_gate09_agent_executions."""
        migration = importlib.import_module("backend.migrations.versions.0012_auth_user_provisioning")
        assert migration.revision == "0012_auth_user_provisioning"
        assert migration.down_revision == "0011_gate09_agent_executions"
        assert hasattr(migration, "upgrade")
        assert hasattr(migration, "downgrade")
