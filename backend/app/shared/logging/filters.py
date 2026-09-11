"""
GrowFlow — Logging Filters and Secret Redaction.

Redacts credentials, tokens, API keys, and sensitive data from all log records.
"""

from __future__ import annotations

import re
from typing import Any

SENSITIVE_KEY_PATTERNS = re.compile(
    r"(password|secret|token|api_?key|authorization|bearer|cookie|jwt|private_?key|credential)",
    re.IGNORECASE,
)

REDACTED_PLACEHOLDER = "[REDACTED]"


def redact_sensitive_data(val: Any) -> Any:
    """Recursively redact sensitive key-value pairs from data structures."""
    if isinstance(val, dict):
        sanitized: dict[str, Any] = {}
        for k, v in val.items():
            if isinstance(k, str) and SENSITIVE_KEY_PATTERNS.search(k):
                sanitized[k] = REDACTED_PLACEHOLDER
            else:
                sanitized[k] = redact_sensitive_data(v)
        return sanitized
    if isinstance(val, list):
        return [redact_sensitive_data(item) for item in val]
    if isinstance(val, tuple):
        return tuple(redact_sensitive_data(item) for item in val)
    return val


def redact_secrets_processor(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Structlog processor to ensure no secrets leak into logged event dictionaries."""
    sanitized: dict[str, Any] = {}
    for key, value in event_dict.items():
        if isinstance(key, str) and SENSITIVE_KEY_PATTERNS.search(key):
            sanitized[key] = REDACTED_PLACEHOLDER
        else:
            sanitized[key] = redact_sensitive_data(value)
    return sanitized
