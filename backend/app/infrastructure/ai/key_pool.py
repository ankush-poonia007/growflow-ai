"""
GrowFlow — Five-Key API Pool & Key Health State Machine.

Maintains health-aware round-robin rotation, automatic cooldown recovery,
and operational metrics across exactly five OpenRouter provider key slots.

Architecture ref:
  6E § 10 — Five-key API pool
  6E § 11 — Key ownership
  6E § 12 — Key health states
  6E § 13 — Key selection strategy
  6E § 14 — Key health metadata
  6E § 15 — Key recovery
  6E § 21 — Rate limits and cooldowns
  6E § 22 — Quota exhaustion
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from backend.app.infrastructure.ai.models import (
    AIErrorCategory,
    AIProviderUnavailableException,
    AIQuotaExhaustedException,
    KeyHealthState,
    KeyPoolEntry,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.config.settings import AISettings

logger = get_logger("growflow.infrastructure.ai.key_pool")


class APIKeyPoolManager:
    """Manages the in-memory health state machine and rotation for the five-key API pool."""

    def __init__(self, settings: AISettings) -> None:
        self._settings = settings
        self._rotation_index = 0
        self._pool: list[KeyPoolEntry] = []
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize the five slots with immutable aliases and initial health states."""
        raw_keys = [
            self._settings.OPENROUTER_API_KEY_1,
            self._settings.OPENROUTER_API_KEY_2,
            self._settings.OPENROUTER_API_KEY_3,
            self._settings.OPENROUTER_API_KEY_4,
            self._settings.OPENROUTER_API_KEY_5,
        ]

        self._pool = []
        for idx, key in enumerate(raw_keys, start=1):
            alias = f"key_{idx}"
            is_usable = bool(key and not key.startswith("your-") and len(key.strip()) > 0)
            status = KeyHealthState.ACTIVE if is_usable else KeyHealthState.DISABLED
            self._pool.append(
                KeyPoolEntry(
                    key_alias=alias,
                    raw_key=key.strip() if is_usable and key else None,
                    status=status,
                )
            )

        active_count = sum(1 for e in self._pool if e.status == KeyHealthState.ACTIVE)
        logger.info(
            "AI provider key pool initialized",
            total_slots=5,
            active_keys=active_count,
            disabled_keys=5 - active_count,
        )

    @property
    def has_live_keys(self) -> bool:
        """Check if any configured key slot is potentially viable (active, cooldown, or rate-limited)."""
        return any(
            e.status
            in (KeyHealthState.ACTIVE, KeyHealthState.COOLDOWN, KeyHealthState.RATE_LIMITED)
            and e.raw_key is not None
            for e in self._pool
        )

    def _recover_expired_cooldowns(self, now: datetime) -> None:
        """Automatically recover keys from COOLDOWN or RATE_LIMITED if their cooldown has elapsed."""
        for entry in self._pool:
            if (
                entry.status in (KeyHealthState.COOLDOWN, KeyHealthState.RATE_LIMITED)
                and entry.cooldown_until is not None
                and now >= entry.cooldown_until
            ):
                logger.info(
                    "Key recovered from cooldown to ACTIVE",
                    key_alias=entry.key_alias,
                    previous_status=entry.status.value,
                )
                entry.status = KeyHealthState.ACTIVE
                entry.cooldown_until = None
                entry.failure_count = 0

    def get_next_key(self) -> KeyPoolEntry:
        """
        Select the next eligible key using health-aware round-robin.

        Raises:
            AIQuotaExhaustedException: If all usable keys are rate-limited or in cooldown.
            AIProviderUnavailableException: If all keys are permanently failed or disabled.
        """
        now = datetime.now(UTC)
        self._recover_expired_cooldowns(now)

        active_keys = [
            entry
            for entry in self._pool
            if entry.status == KeyHealthState.ACTIVE and entry.raw_key is not None
        ]

        if not active_keys:
            has_cooling_keys = any(
                e.status in (KeyHealthState.RATE_LIMITED, KeyHealthState.COOLDOWN)
                and e.raw_key is not None
                for e in self._pool
            )
            if has_cooling_keys:
                logger.warning(
                    "All configured AI provider keys are currently in cooldown or rate-limited"
                )
                raise AIQuotaExhaustedException(
                    "All AI provider keys in pool are temporarily rate-limited or cooling down."
                )

            logger.error("No usable AI provider keys configured in pool")
            raise AIProviderUnavailableException(
                "No usable AI provider keys configured in pool (all failed or disabled)."
            )

        entry = active_keys[self._rotation_index % len(active_keys)]
        self._rotation_index += 1
        entry.last_used_at = now
        return entry

    def record_success(self, key_alias: str) -> None:
        """Record a successful execution on the specified key, resetting transient failure counts."""
        now = datetime.now(UTC)
        for entry in self._pool:
            if entry.key_alias == key_alias:
                entry.last_success_at = now
                entry.failure_count = 0
                return

    def record_rate_limit(self, key_alias: str, retry_after: float | None = None) -> None:
        """Mark a key as RATE_LIMITED and enforce cooldown."""
        now = datetime.now(UTC)
        cooldown_duration = (
            retry_after
            if retry_after is not None and retry_after > 0
            else float(self._settings.RATE_LIMIT_COOLDOWN_SECONDS)
        )
        for entry in self._pool:
            if entry.key_alias == key_alias:
                entry.rate_limit_count += 1
                entry.status = KeyHealthState.RATE_LIMITED
                entry.cooldown_until = now + timedelta(seconds=cooldown_duration)
                logger.warning(
                    "Key transitioned to RATE_LIMITED",
                    key_alias=key_alias,
                    cooldown_seconds=cooldown_duration,
                    cooldown_until=entry.cooldown_until.isoformat(),
                )
                return

    def record_failure(self, key_alias: str, category: AIErrorCategory) -> None:
        """Record an execution failure on the specified key and update health states."""
        now = datetime.now(UTC)
        for entry in self._pool:
            if entry.key_alias == key_alias:
                if category == AIErrorCategory.AUTH_ERROR:
                    entry.status = KeyHealthState.FAILED
                    logger.error(
                        "Key transitioned to FAILED due to authentication error",
                        key_alias=key_alias,
                    )
                    return

                if category in (AIErrorCategory.TRANSIENT_SERVER, AIErrorCategory.TIMEOUT):
                    entry.failure_count += 1
                    if entry.failure_count >= 3:
                        entry.status = KeyHealthState.COOLDOWN
                        entry.cooldown_until = now + timedelta(
                            seconds=self._settings.TRANSIENT_COOLDOWN_SECONDS
                        )
                        logger.warning(
                            "Key transitioned to COOLDOWN after consecutive failures",
                            key_alias=key_alias,
                            consecutive_failures=entry.failure_count,
                            cooldown_seconds=self._settings.TRANSIENT_COOLDOWN_SECONDS,
                        )
                    return

    def get_pool_status(self) -> list[dict[str, Any]]:
        """Return safe operational metadata for all slots (never leaks secrets)."""
        return [
            {
                "key_alias": e.key_alias,
                "status": e.status.value,
                "has_key": e.raw_key is not None,
                "last_used_at": e.last_used_at.isoformat() if e.last_used_at else None,
                "last_success_at": e.last_success_at.isoformat() if e.last_success_at else None,
                "failure_count": e.failure_count,
                "rate_limit_count": e.rate_limit_count,
                "cooldown_until": e.cooldown_until.isoformat() if e.cooldown_until else None,
            }
            for e in self._pool
        ]
