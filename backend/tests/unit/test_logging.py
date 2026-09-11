"""
Unit tests for structured logging and correlation context.
"""

from __future__ import annotations

import pytest

from backend.app.shared.logging.context import (
    clear_context,
    generate_correlation_id,
    get_correlation_id,
    get_request_id,
    set_correlation_id,
    set_request_id,
)
from backend.app.shared.logging.filters import (
    REDACTED_PLACEHOLDER,
    redact_sensitive_data,
)


@pytest.mark.unit
def test_correlation_context_lifecycle() -> None:
    """Verify get/set/clear of correlation and request IDs."""
    clear_context()
    assert get_correlation_id() is None
    assert get_request_id() is None

    test_corr_id = generate_correlation_id()
    test_req_id = generate_correlation_id()

    set_correlation_id(test_corr_id)
    set_request_id(test_req_id)

    assert get_correlation_id() == test_corr_id
    assert get_request_id() == test_req_id

    clear_context()
    assert get_correlation_id() is None
    assert get_request_id() is None


@pytest.mark.unit
def test_secret_redaction_filters() -> None:
    """Verify that credentials and tokens are redacted from dictionaries."""
    data = {
        "username": "student_1",
        "password": "super-secret-password",
        "api_key": "sk-1234567890",
        "nested": {
            "token": "jwt.token.here",
            "safe_field": "visible",
            "supabase_secret_key": "sb_secret",
        },
        "list_data": [
            {"auth_token": "secret_in_list", "name": "item"},
        ],
    }

    sanitized = redact_sensitive_data(data)

    assert sanitized["username"] == "student_1"
    assert sanitized["password"] == REDACTED_PLACEHOLDER
    assert sanitized["api_key"] == REDACTED_PLACEHOLDER
    assert sanitized["nested"]["token"] == REDACTED_PLACEHOLDER
    assert sanitized["nested"]["safe_field"] == "visible"
    assert sanitized["nested"]["supabase_secret_key"] == REDACTED_PLACEHOLDER
    assert sanitized["list_data"][0]["auth_token"] == REDACTED_PLACEHOLDER
    assert sanitized["list_data"][0]["name"] == "item"
