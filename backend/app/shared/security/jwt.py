"""
GrowFlow — Supabase JWT Verifier.

Implements centralized server-side JWT verification using PyJWT.
Supports:
1. Symmetric HS256 verification via SUPABASE_JWT_SECRET (legacy/test suites).
2. Asymmetric ES256 verification via Supabase JWKS (modern Supabase Auth tokens).

Enforces algorithm whitelist integrity, audience/issuer validation, expiration,
and subject UUID claims extraction per Part 6D and Gate 04 specifications.

Architecture ref:
  6D § 3  — Supabase Auth as identity authority
  6D § 13 — Token validation rules (signature, expiry, audience, issuer)
  6D § 35 — Centralized typed settings for verification secret / JWKS endpoint
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

import jwt
from jwt import PyJWKClient, PyJWKError

from backend.app.config.settings import Settings, get_settings
from backend.app.shared.exceptions import AuthenticationException
from backend.app.shared.logging import get_logger

logger = get_logger("growflow.security.jwt")

_ALLOWED_ALGORITHMS = ["HS256", "ES256"]


@dataclass(frozen=True)
class VerifiedToken:
    """
    Immutable representation of a cryptographically verified JWT.

    Attributes:
        user_id: Parsed UUID from the 'sub' claim.
        email: User's email address from the token claims.
        claims: Raw verified claims dictionary.
    """

    user_id: UUID
    email: str
    claims: dict[str, Any]


class SupabaseJWTVerifier:
    """
    Server-side JWT verifier for Supabase Auth tokens.

    Supports:
    - Symmetric HS256 verification against SUPABASE_JWT_SECRET.
    - Asymmetric ES256 verification against Supabase JWKS (SUPABASE_JWT_JWKS_URL).

    Enforces strict audience and issuer checks, expiration verification,
    and claim extraction. Fails closed on any cryptographic or claims anomaly.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        jwks_client: PyJWKClient | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._jwks_client = jwks_client
        if self._jwks_client is None:
            jwks_url = self._resolve_jwks_url()
            if jwks_url:
                try:
                    self._jwks_client = PyJWKClient(
                        jwks_url,
                        cache_jwk_set=True,
                        lifespan=3600,
                    )
                except Exception as exc:
                    logger.warning("Failed to initialize PyJWKClient", error=str(exc))
                    self._jwks_client = None

    def _resolve_jwks_url(self) -> str | None:
        """Resolve trusted JWKS URL strictly from settings."""
        if getattr(self._settings.auth, "JWT_JWKS_URL", None):
            return self._settings.auth.JWT_JWKS_URL
        supabase_url = getattr(self._settings.database, "SUPABASE_URL", None)
        if supabase_url:
            return f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        return None

    def verify(self, token: str) -> VerifiedToken:
        """
        Verify a raw bearer JWT string and extract its validated identity.

        Args:
            token: Raw compact JWT string.

        Returns:
            VerifiedToken with validated user_id and email.

        Raises:
            AuthenticationException: If the token is expired, invalid, unsigned,
                or has mismatched claims (HTTP 401).
        """
        if not token or not token.strip():
            raise AuthenticationException(
                message="Authentication token is missing.",
                code="AUTH_MISSING_TOKEN",
            )

        token_str = token.strip()

        # 1. Determine if this token is an ES256 token
        is_es256 = False
        try:
            unverified_header = jwt.get_unverified_header(token_str)
            if unverified_header.get("alg") == "ES256":
                is_es256 = True
        except Exception:
            unverified_header = None

        # 2. If not ES256, verify that symmetric JWT_SECRET is configured
        if not is_es256 and not self._settings.auth.JWT_SECRET:
            logger.error("HS256 JWT verification attempted without configured SUPABASE_JWT_SECRET")
            raise AuthenticationException(
                message="Authentication service is temporarily unavailable.",
                code="AUTH_CONFIGURATION_ERROR",
            )

        # 3. Parse unverified header if not already parsed
        if unverified_header is None:
            try:
                unverified_header = jwt.get_unverified_header(token_str)
            except Exception as exc:
                logger.warning("Authentication failed: malformed token header", error=str(exc))
                raise AuthenticationException(
                    message="Authentication token is malformed or invalid.",
                    code="AUTH_INVALID_TOKEN",
                ) from exc

        alg = unverified_header.get("alg")
        if not alg or alg not in _ALLOWED_ALGORITHMS:
            logger.warning("Authentication failed: disallowed algorithm", alg=alg)
            raise AuthenticationException(
                message="Authentication token is malformed or invalid.",
                code="AUTH_INVALID_TOKEN",
            )

        # 3. Resolve verification key based on algorithm
        if alg == "HS256":
            secret = self._settings.auth.JWT_SECRET
            if not secret:
                logger.error("HS256 JWT verification attempted without configured SUPABASE_JWT_SECRET")
                raise AuthenticationException(
                    message="Authentication service is temporarily unavailable.",
                    code="AUTH_CONFIGURATION_ERROR",
                )
            verification_key: Any = secret
            allowed_algs = ["HS256"]
        elif alg == "ES256":
            if not self._jwks_client:
                jwks_url = self._resolve_jwks_url()
                if jwks_url:
                    self._jwks_client = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)

            if not self._jwks_client:
                logger.error("ES256 JWT verification attempted without configured SUPABASE_JWT_JWKS_URL")
                raise AuthenticationException(
                    message="Authentication service is temporarily unavailable.",
                    code="AUTH_CONFIGURATION_ERROR",
                )

            try:
                signing_key = self._jwks_client.get_signing_key_from_jwt(token_str)
                verification_key = signing_key.key
            except PyJWKError as exc:
                logger.warning("Authentication failed: JWKS key retrieval failed", error=str(exc))
                raise AuthenticationException(
                    message="Authentication token signature is invalid.",
                    code="AUTH_INVALID_SIGNATURE",
                ) from exc
            except Exception as exc:
                logger.warning("Authentication failed: unexpected JWKS retrieval error", error=str(exc))
                raise AuthenticationException(
                    message="Authentication token could not be verified.",
                    code="AUTH_INVALID_TOKEN",
                ) from exc
            allowed_algs = ["ES256"]
        else:
            raise AuthenticationException(
                message="Authentication token is malformed or invalid.",
                code="AUTH_INVALID_TOKEN",
            )

        # 4. Decode & cryptographically verify claims
        expected_audience = self._settings.auth.JWT_AUDIENCE
        expected_issuer = self._settings.auth.JWT_ISSUER

        decode_options = {
            "require": ["exp", "sub"],
            "verify_exp": True,
            "verify_aud": bool(expected_audience),
            "verify_iss": bool(expected_issuer),
            "verify_iat": False,
        }

        try:
            claims = jwt.decode(
                token_str,
                key=verification_key,
                algorithms=allowed_algs,
                audience=expected_audience if expected_audience else None,
                issuer=expected_issuer if expected_issuer else None,
                options=decode_options,
            )
        except jwt.ExpiredSignatureError as exc:
            logger.info("Authentication failed: token expired")
            raise AuthenticationException(
                message="Authentication token has expired.",
                code="AUTH_TOKEN_EXPIRED",
            ) from exc
        except jwt.InvalidAudienceError as exc:
            logger.warning("Authentication failed: audience mismatch")
            raise AuthenticationException(
                message="Authentication token audience is invalid.",
                code="AUTH_INVALID_AUDIENCE",
            ) from exc
        except jwt.InvalidIssuerError as exc:
            logger.warning("Authentication failed: issuer mismatch")
            raise AuthenticationException(
                message="Authentication token issuer is invalid.",
                code="AUTH_INVALID_ISSUER",
            ) from exc
        except jwt.InvalidSignatureError as exc:
            logger.warning("Authentication failed: invalid signature")
            raise AuthenticationException(
                message="Authentication token signature is invalid.",
                code="AUTH_INVALID_SIGNATURE",
            ) from exc
        except jwt.MissingRequiredClaimError as exc:
            logger.warning("Authentication failed: missing required claim")
            raise AuthenticationException(
                message="Authentication token is missing required claims.",
                code="AUTH_INVALID_SUBJECT",
            ) from exc
        except (jwt.DecodeError, jwt.InvalidAlgorithmError) as exc:
            logger.warning("Authentication failed: malformed token or algorithm confusion attempt")
            raise AuthenticationException(
                message="Authentication token is malformed or invalid.",
                code="AUTH_INVALID_TOKEN",
            ) from exc
        except Exception as exc:
            logger.warning(
                "Authentication failed: unexpected token verification error",
                error_type=type(exc).__name__,
            )
            raise AuthenticationException(
                message="Authentication token could not be verified.",
                code="AUTH_INVALID_TOKEN",
            ) from exc

        # 5. Extract and validate subject
        sub = claims.get("sub")
        if not sub:
            raise AuthenticationException(
                message="Authentication token subject is missing.",
                code="AUTH_INVALID_SUBJECT",
            )

        try:
            user_id = UUID(str(sub))
        except (ValueError, TypeError) as exc:
            logger.warning("Authentication failed: subject claim is not a valid UUID")
            raise AuthenticationException(
                message="Authentication token subject is invalid.",
                code="AUTH_INVALID_SUBJECT",
            ) from exc

        email = claims.get("email", "")

        return VerifiedToken(
            user_id=user_id,
            email=str(email),
            claims=claims,
        )
