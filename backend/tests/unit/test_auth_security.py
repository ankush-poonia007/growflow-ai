"""
GrowFlow Gate 04 — Unit Tests for Authentication & Security Foundation.

Tests:
1. SupabaseJWTVerifier — signature, claims, expiry, audience, issuer, algorithm confusion.
2. Domain authorization policies — account status, role RBAC, resource ownership.
3. Domain models — CurrentUser, UserRole, AccountStatus, UserModel conversion.
4. Secrets non-disclosure — confirms credentials are never leaked in errors or repr.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import uuid

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
import pytest

from backend.app.config.settings import Settings
from backend.app.domain.identity import (
    AccountStatus,
    CurrentUser,
    UserRole,
    verify_account_active,
    verify_resource_ownership,
    verify_role_access,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.shared.exceptions import AuthenticationException, AuthorizationException
from backend.app.shared.security.jwt import SupabaseJWTVerifier

_TEST_SECRET = "test-jwt-secret-at-least-32-chars-long-123456"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_test_settings(**kwargs: object) -> Settings:
    settings = Settings()
    settings.auth.JWT_SECRET = _TEST_SECRET
    settings.auth.JWT_AUDIENCE = _TEST_AUDIENCE
    settings.auth.JWT_ISSUER = _TEST_ISSUER
    for k, v in kwargs.items():
        setattr(settings.auth, k, v)
    return settings


def _create_test_jwt(
    *,
    user_id: uuid.UUID | None = None,
    email: str = "student@example.com",
    expires_in_seconds: int = 3600,
    secret: str = _TEST_SECRET,
    audience: str = _TEST_AUDIENCE,
    issuer: str = _TEST_ISSUER,
    algorithm: str = "HS256",
    custom_claims: dict[str, object] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, object] = {
        "sub": str(user_id or uuid.uuid4()),
        "email": email,
        "aud": audience,
        "iss": issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    if custom_claims:
        payload.update(custom_claims)
    return jwt.encode(payload, secret, algorithm=algorithm)


_TEST_EC_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
_TEST_EC_PUBLIC_KEY = _TEST_EC_PRIVATE_KEY.public_key()
_TEST_KID = "test-ec-kid-001"
_TEST_JWKS_URL = "https://test.supabase.co/auth/v1/.well-known/jwks.json"


class MockPyJWKClient:
    """Mock PyJWKClient for unit tests without network calls."""

    def __init__(self, key_id: str = _TEST_KID, public_key: object = _TEST_EC_PUBLIC_KEY) -> None:
        self._key_id = key_id
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token: str) -> object:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if kid != self._key_id:
            raise jwt.PyJWKError(f"Key with ID {kid} not found")
        return type("SigningKey", (), {"key": self._public_key, "key_id": self._key_id})()


def _create_test_es256_jwt(
    *,
    user_id: uuid.UUID | None = None,
    email: str = "student@example.com",
    expires_in_seconds: int = 3600,
    private_key: object = _TEST_EC_PRIVATE_KEY,
    kid: str = _TEST_KID,
    audience: str = _TEST_AUDIENCE,
    issuer: str = _TEST_ISSUER,
    custom_claims: dict[str, object] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, object] = {
        "sub": str(user_id or uuid.uuid4()),
        "email": email,
        "aud": audience,
        "iss": issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    if custom_claims:
        payload.update(custom_claims)
    return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": kid})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 1. SupabaseJWTVerifier Unit Tests
# ---------------------------------------------------------------------------


class TestSupabaseJWTVerifier:
    """Unit tests for SupabaseJWTVerifier."""

    @pytest.mark.unit
    def test_valid_token_verification(self) -> None:
        """Valid token with correct signature, audience, and issuer is successfully verified."""
        user_uuid = uuid.uuid4()
        token = _create_test_jwt(user_id=user_uuid, email="alice@example.com")
        settings = _make_test_settings()
        verifier = SupabaseJWTVerifier(settings=settings)

        result = verifier.verify(token)

        assert result.user_id == user_uuid
        assert result.email == "alice@example.com"
        assert result.claims["aud"] == _TEST_AUDIENCE

    @pytest.mark.unit
    def test_missing_token_raises_auth_exception(self) -> None:
        """Empty or whitespace token raises AUTH_MISSING_TOKEN."""
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify("")
        assert exc_info.value.code == "AUTH_MISSING_TOKEN"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_unconfigured_secret_fails_closed(self) -> None:
        """Missing JWT_SECRET raises AUTH_CONFIGURATION_ERROR without attempting decode."""
        settings = _make_test_settings(JWT_SECRET=None)
        verifier = SupabaseJWTVerifier(settings=settings)

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify("some.token.here")
        assert exc_info.value.code == "AUTH_CONFIGURATION_ERROR"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_expired_token_raises_token_expired(self) -> None:
        """Expired token raises AUTH_TOKEN_EXPIRED (401)."""
        expired_token = _create_test_jwt(expires_in_seconds=-60)
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(expired_token)
        assert exc_info.value.code == "AUTH_TOKEN_EXPIRED"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_invalid_signature_raises_signature_error(self) -> None:
        """Token signed with wrong secret raises AUTH_INVALID_SIGNATURE (401)."""
        bad_token = _create_test_jwt(secret="wrong-secret-key-that-does-not-match")
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(bad_token)
        assert exc_info.value.code == "AUTH_INVALID_SIGNATURE"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_invalid_audience_raises_audience_error(self) -> None:
        """Token with mismatched audience raises AUTH_INVALID_AUDIENCE (401)."""
        bad_aud_token = _create_test_jwt(audience="wrong-audience")
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(bad_aud_token)
        assert exc_info.value.code == "AUTH_INVALID_AUDIENCE"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_invalid_issuer_raises_issuer_error(self) -> None:
        """Token with mismatched issuer raises AUTH_INVALID_ISSUER (401)."""
        bad_iss_token = _create_test_jwt(issuer="https://evil.supabase.co/auth/v1")
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(bad_iss_token)
        assert exc_info.value.code == "AUTH_INVALID_ISSUER"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_malformed_token_raises_invalid_token(self) -> None:
        """Non-JWT string raises AUTH_INVALID_TOKEN (401)."""
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify("not-a-valid-jwt-structure")
        assert exc_info.value.code == "AUTH_INVALID_TOKEN"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_missing_sub_raises_invalid_subject(self) -> None:
        """Token without 'sub' claim raises AUTH_INVALID_SUBJECT (401)."""
        now = datetime.now(UTC)
        payload = {
            "email": "test@example.com",
            "aud": _TEST_AUDIENCE,
            "iss": _TEST_ISSUER,
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        token = jwt.encode(payload, _TEST_SECRET, algorithm="HS256")
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(token)
        assert exc_info.value.code == "AUTH_INVALID_SUBJECT"

    @pytest.mark.unit
    def test_non_uuid_sub_raises_invalid_subject(self) -> None:
        """Token with non-UUID 'sub' claim raises AUTH_INVALID_SUBJECT (401)."""
        token = _create_test_jwt(custom_claims={"sub": "not-a-uuid"})
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(token)
        assert exc_info.value.code == "AUTH_INVALID_SUBJECT"

    @pytest.mark.unit
    def test_algorithm_confusion_attack_rejected(self) -> None:
        """Tokens using algorithms other than HS256 (e.g. 'none') are strictly rejected."""
        now = datetime.now(UTC)
        payload = {
            "sub": str(uuid.uuid4()),
            "email": "attacker@example.com",
            "aud": _TEST_AUDIENCE,
            "iss": _TEST_ISSUER,
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        unsigned_token = jwt.encode(payload, key="", algorithm="none")
        verifier = SupabaseJWTVerifier(settings=_make_test_settings())

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(unsigned_token)
        assert exc_info.value.code == "AUTH_INVALID_TOKEN"

    @pytest.mark.unit
    def test_valid_es256_token_verification(self) -> None:
        """Valid ES256 token with correct EC signature, audience, and issuer is successfully verified."""
        user_uuid = uuid.uuid4()
        token = _create_test_es256_jwt(user_id=user_uuid, email="student.es256@example.com")
        settings = _make_test_settings(JWT_JWKS_URL=_TEST_JWKS_URL)
        mock_jwks = MockPyJWKClient()
        verifier = SupabaseJWTVerifier(settings=settings, jwks_client=mock_jwks)  # type: ignore[arg-type]

        result = verifier.verify(token)

        assert result.user_id == user_uuid
        assert result.email == "student.es256@example.com"
        assert result.claims["aud"] == _TEST_AUDIENCE
        assert result.claims["iss"] == _TEST_ISSUER

    @pytest.mark.unit
    def test_es256_expired_token_raises_token_expired(self) -> None:
        """Expired ES256 token raises AUTH_TOKEN_EXPIRED (401)."""
        expired_token = _create_test_es256_jwt(expires_in_seconds=-60)
        settings = _make_test_settings(JWT_JWKS_URL=_TEST_JWKS_URL)
        mock_jwks = MockPyJWKClient()
        verifier = SupabaseJWTVerifier(settings=settings, jwks_client=mock_jwks)  # type: ignore[arg-type]

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(expired_token)
        assert exc_info.value.code == "AUTH_TOKEN_EXPIRED"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_es256_invalid_signature_raises_signature_error(self) -> None:
        """ES256 token signed with different EC private key raises AUTH_INVALID_SIGNATURE (401)."""
        different_private_key = ec.generate_private_key(ec.SECP256R1())
        bad_token = _create_test_es256_jwt(private_key=different_private_key)
        settings = _make_test_settings(JWT_JWKS_URL=_TEST_JWKS_URL)
        mock_jwks = MockPyJWKClient()
        verifier = SupabaseJWTVerifier(settings=settings, jwks_client=mock_jwks)  # type: ignore[arg-type]

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(bad_token)
        assert exc_info.value.code == "AUTH_INVALID_SIGNATURE"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_es256_invalid_audience_raises_audience_error(self) -> None:
        """ES256 token with wrong audience raises AUTH_INVALID_AUDIENCE (401)."""
        token = _create_test_es256_jwt(audience="wrong-audience")
        settings = _make_test_settings(JWT_JWKS_URL=_TEST_JWKS_URL)
        mock_jwks = MockPyJWKClient()
        verifier = SupabaseJWTVerifier(settings=settings, jwks_client=mock_jwks)  # type: ignore[arg-type]

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(token)
        assert exc_info.value.code == "AUTH_INVALID_AUDIENCE"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_es256_invalid_issuer_raises_issuer_error(self) -> None:
        """ES256 token with wrong issuer raises AUTH_INVALID_ISSUER (401)."""
        token = _create_test_es256_jwt(issuer="https://malicious.issuer.co/auth/v1")
        settings = _make_test_settings(JWT_JWKS_URL=_TEST_JWKS_URL)
        mock_jwks = MockPyJWKClient()
        verifier = SupabaseJWTVerifier(settings=settings, jwks_client=mock_jwks)  # type: ignore[arg-type]

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(token)
        assert exc_info.value.code == "AUTH_INVALID_ISSUER"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_es256_unknown_kid_raises_signature_error(self) -> None:
        """ES256 token with unknown kid in header raises AUTH_INVALID_SIGNATURE (401)."""
        token = _create_test_es256_jwt(kid="unknown-kid-does-not-exist")
        settings = _make_test_settings(JWT_JWKS_URL=_TEST_JWKS_URL)
        mock_jwks = MockPyJWKClient()
        verifier = SupabaseJWTVerifier(settings=settings, jwks_client=mock_jwks)  # type: ignore[arg-type]

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(token)
        assert exc_info.value.code == "AUTH_INVALID_SIGNATURE"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_unsupported_rsa_algorithm_rejected(self) -> None:
        """Tokens using unsupported algorithms like RS256 are rejected with AUTH_INVALID_TOKEN."""
        from cryptography.hazmat.primitives.asymmetric import rsa

        rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        now = datetime.now(UTC)
        payload: dict[str, object] = {
            "sub": str(uuid.uuid4()),
            "email": "test@example.com",
            "aud": _TEST_AUDIENCE,
            "iss": _TEST_ISSUER,
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        token = jwt.encode(payload, rsa_key, algorithm="RS256")  # type: ignore[arg-type]
        settings = _make_test_settings(JWT_JWKS_URL=_TEST_JWKS_URL)
        verifier = SupabaseJWTVerifier(settings=settings)

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(token)
        assert exc_info.value.code == "AUTH_INVALID_TOKEN"
        assert exc_info.value.status_code == 401

    @pytest.mark.unit
    def test_es256_unconfigured_jwks_fails_closed(self) -> None:
        """ES256 token received when JWKS URL is unconfigured fails closed with AUTH_CONFIGURATION_ERROR."""
        token = _create_test_es256_jwt()
        settings = _make_test_settings(JWT_JWKS_URL=None)
        settings.database.SUPABASE_URL = None
        verifier = SupabaseJWTVerifier(settings=settings, jwks_client=None)

        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(token)
        assert exc_info.value.code == "AUTH_CONFIGURATION_ERROR"
        assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# 2. Authorization Rules Unit Tests
# ---------------------------------------------------------------------------


class TestAuthorizationRules:
    """Unit tests for domain authorization functions."""

    @pytest.fixture
    def active_student(self) -> CurrentUser:
        return CurrentUser(
            user_id=uuid.uuid4(),
            email="student@example.com",
            role=UserRole.STUDENT,
            status=AccountStatus.ACTIVE,
            full_name="Active Student",
        )

    @pytest.fixture
    def suspended_student(self) -> CurrentUser:
        return CurrentUser(
            user_id=uuid.uuid4(),
            email="suspended@example.com",
            role=UserRole.STUDENT,
            status=AccountStatus.SUSPENDED,
            full_name="Suspended Student",
        )

    @pytest.fixture
    def inactive_mentor(self) -> CurrentUser:
        return CurrentUser(
            user_id=uuid.uuid4(),
            email="inactive@example.com",
            role=UserRole.MENTOR,
            status=AccountStatus.INACTIVE,
            full_name="Inactive Mentor",
        )

    @pytest.fixture
    def admin_user(self) -> CurrentUser:
        return CurrentUser(
            user_id=uuid.uuid4(),
            email="admin@example.com",
            role=UserRole.ADMIN,
            status=AccountStatus.ACTIVE,
            full_name="Platform Admin",
        )

    @pytest.mark.unit
    def test_verify_account_active_passes_for_active(self, active_student: CurrentUser) -> None:
        """Active account passes without error."""
        verify_account_active(active_student)  # Must not raise

    @pytest.mark.unit
    def test_verify_account_active_fails_for_suspended(
        self, suspended_student: CurrentUser
    ) -> None:
        """Suspended account raises AUTH_ACCOUNT_SUSPENDED (403)."""
        with pytest.raises(AuthorizationException) as exc_info:
            verify_account_active(suspended_student)
        assert exc_info.value.code == "AUTH_ACCOUNT_SUSPENDED"
        assert exc_info.value.status_code == 403

    @pytest.mark.unit
    def test_verify_account_active_fails_for_inactive(self, inactive_mentor: CurrentUser) -> None:
        """Inactive account raises AUTH_ACCOUNT_INACTIVE (403)."""
        with pytest.raises(AuthorizationException) as exc_info:
            verify_account_active(inactive_mentor)
        assert exc_info.value.code == "AUTH_ACCOUNT_INACTIVE"
        assert exc_info.value.status_code == 403

    @pytest.mark.unit
    def test_verify_role_access_passes_for_allowed_role(self, active_student: CurrentUser) -> None:
        """Allowed role check succeeds."""
        verify_role_access(active_student, [UserRole.STUDENT, UserRole.MENTOR])  # Must not raise

    @pytest.mark.unit
    def test_verify_role_access_fails_for_disallowed_role(
        self, active_student: CurrentUser
    ) -> None:
        """Disallowed role raises AUTH_FORBIDDEN_ROLE (403)."""
        with pytest.raises(AuthorizationException) as exc_info:
            verify_role_access(active_student, [UserRole.ADMIN])
        assert exc_info.value.code == "AUTH_FORBIDDEN_ROLE"
        assert exc_info.value.status_code == 403

    @pytest.mark.unit
    def test_verify_resource_ownership_passes_for_owner(self, active_student: CurrentUser) -> None:
        """Owner can access their own resource."""
        verify_resource_ownership(active_student, active_student.user_id)  # Must not raise

    @pytest.mark.unit
    def test_verify_resource_ownership_fails_for_non_owner(
        self, active_student: CurrentUser
    ) -> None:
        """Non-owner accessing resource raises AUTH_FORBIDDEN_RESOURCE (403)."""
        other_user_id = uuid.uuid4()
        with pytest.raises(AuthorizationException) as exc_info:
            verify_resource_ownership(active_student, other_user_id)
        assert exc_info.value.code == "AUTH_FORBIDDEN_RESOURCE"
        assert exc_info.value.status_code == 403

    @pytest.mark.unit
    def test_verify_resource_ownership_admin_bypass_when_explicitly_allowed(
        self, admin_user: CurrentUser
    ) -> None:
        """Admin bypasses ownership only when allow_admin=True."""
        other_user_id = uuid.uuid4()
        verify_resource_ownership(admin_user, other_user_id, allow_admin=True)  # Must not raise

    @pytest.mark.unit
    def test_verify_resource_ownership_admin_denied_when_not_allowed(
        self, admin_user: CurrentUser
    ) -> None:
        """Admin is denied when allow_admin=False (default deny principle)."""
        other_user_id = uuid.uuid4()
        with pytest.raises(AuthorizationException) as exc_info:
            verify_resource_ownership(admin_user, other_user_id, allow_admin=False)
        assert exc_info.value.code == "AUTH_FORBIDDEN_RESOURCE"


# ---------------------------------------------------------------------------
# 3. Domain and ORM Model Conversion Tests
# ---------------------------------------------------------------------------


class TestIdentityModels:
    """Unit tests for UserModel and CurrentUser models."""

    @pytest.mark.unit
    def test_current_user_properties(self) -> None:
        """CurrentUser role helper properties behave accurately."""
        user_id = uuid.uuid4()
        student = CurrentUser(
            user_id=user_id,
            email="s@example.com",
            role=UserRole.STUDENT,
            status=AccountStatus.ACTIVE,
        )
        assert student.is_student is True
        assert student.is_mentor is False
        assert student.is_admin is False
        assert student.is_active is True

    @pytest.mark.unit
    def test_user_orm_model_to_current_user(self) -> None:
        """UserModel correctly converts to domain CurrentUser."""
        user_id = uuid.uuid4()
        orm_user = UserModel(
            id=str(user_id),
            email="mentor@example.com",
            role=UserRole.MENTOR.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Mentor Name",
        )
        current_user = orm_user.to_current_user()

        assert current_user.user_id == user_id
        assert current_user.email == "mentor@example.com"
        assert current_user.role == UserRole.MENTOR
        assert current_user.status == AccountStatus.ACTIVE
        assert current_user.full_name == "Mentor Name"


# ---------------------------------------------------------------------------
# 4. Secrets Non-Disclosure Tests
# ---------------------------------------------------------------------------


class TestSecretsNonDisclosure:
    """Verify that credentials and secrets never leak in exceptions, repr, or strings."""

    @pytest.mark.unit
    def test_current_user_repr_no_sensitive_disclosure(self) -> None:
        """CurrentUser repr does not reveal passwords or tokens."""
        user = CurrentUser(
            user_id=uuid.uuid4(),
            email="user@example.com",
            role=UserRole.STUDENT,
            status=AccountStatus.ACTIVE,
        )
        rep = repr(user)
        assert "user_id" in rep
        assert "password" not in rep
        assert "token" not in rep
        assert "secret" not in rep

    @pytest.mark.unit
    def test_jwt_verifier_exceptions_do_not_leak_secret(self) -> None:
        """Exception messages from JWTVerifier never contain the verification secret."""
        settings = _make_test_settings()
        verifier = SupabaseJWTVerifier(settings=settings)

        for bad_token in ["bad.token", "expired", ""]:
            try:
                verifier.verify(bad_token)
            except AuthenticationException as exc:
                assert _TEST_SECRET not in str(exc.message)
                assert _TEST_SECRET not in str(exc.details)


# ---------------------------------------------------------------------------
# 5. UserRepository Unit Tests
# ---------------------------------------------------------------------------


class TestUserRepository:
    """Unit tests for UserRepository operations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user(self) -> None:
        """create_user instantiates UserModel and adds it to session."""
        from unittest.mock import AsyncMock, MagicMock

        from backend.app.infrastructure.repositories.user_repository import UserRepository

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        repo = UserRepository(session=mock_session)

        user_id = uuid.uuid4()
        user = await repo.create_user(
            user_id=user_id,
            email="NEW@Example.com",
            role="STUDENT",
            status="ACTIVE",
            full_name="New Student",
        )

        assert user.id == str(user_id)
        assert user.email == "new@example.com"
        assert mock_session.add.called
        assert mock_session.flush.called

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_last_login(self) -> None:
        """update_last_login updates last_login_at timestamp and flushes."""
        from unittest.mock import AsyncMock

        from backend.app.infrastructure.repositories.user_repository import UserRepository

        mock_session = AsyncMock()
        repo = UserRepository(session=mock_session)

        user = UserModel(id=str(uuid.uuid4()), email="u@example.com")
        assert user.last_login_at is None

        await repo.update_last_login(user)

        assert user.last_login_at is not None
        assert mock_session.flush.called


# ---------------------------------------------------------------------------
# 6. Gate 04 Migration Integrity
# ---------------------------------------------------------------------------


class TestGate04MigrationIntegrity:
    """Verify Alembic migration 0002 structure and chain integrity."""

    @pytest.mark.unit
    def test_migration_0002_exists_and_chains_from_0001(self) -> None:
        """0002_gate04_users migration exists and has down_revision = 0001_gate03_baseline."""
        import importlib

        migration = importlib.import_module("backend.migrations.versions.0002_gate04_users")
        assert migration.revision == "0002_gate04_users"
        assert migration.down_revision == "0001_gate03_baseline"
