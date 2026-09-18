"""
GrowFlow — Contact API Endpoint Integration Tests.

Validates POST /api/v1/contact input validation, error handling,
canonical response structure, duplicate prevention, and failure boundaries.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import pytest

from backend.app.api.dependencies.services import get_contact_service
from backend.app.application.services.contact_service import (
    ContactService,
    ContactSubmissionResult,
)
from backend.app.config.settings import Settings
from backend.app.infrastructure.email.exceptions import (
    DuplicateSubmissionError,
    EmailConfigurationError,
    EmailDeliveryError,
)


@pytest.fixture
def mock_contact_service() -> AsyncMock:
    """Mock ContactService returning deterministic submission results."""
    service = AsyncMock(spec=ContactService)
    service.submit_inquiry.return_value = ContactSubmissionResult(
        submission_id="sub_test_12345",
        status="delivered",
        timestamp="2026-09-12T15:00:00Z",
        message="Message received. Thanks for reaching out. Your message has been submitted to the GrowFlow team.",
    )
    return service


def test_submit_contact_success(client: TestClient, app, mock_contact_service: AsyncMock):
    """Verify 201 Created response and canonical envelope on valid contact submission."""
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service

    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "discussion_topic": "engineering",
            "message": "Inquiring about multi-agent task execution.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "Message received" in data["message"]
    assert data["data"]["submission_id"] == "sub_test_12345"
    assert data["data"]["status"] == "delivered"

    mock_contact_service.submit_inquiry.assert_called_once_with(
        name="Jane Doe",
        email="jane@example.com",
        discussion_topic="engineering",
        message="Inquiring about multi-agent task execution.",
    )

    app.dependency_overrides.clear()


def test_submit_contact_missing_fields(client: TestClient):
    """Verify 422 Unprocessable Entity when required fields are missing."""
    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            # Missing email, discussion_topic, message
        },
    )
    assert response.status_code == 422


def test_submit_contact_invalid_email(client: TestClient):
    """Verify 422 when email format is invalid."""
    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            "email": "not-an-email",
            "discussion_topic": "general",
            "message": "Valid length message for testing purposes.",
        },
    )
    assert response.status_code == 422


def test_submit_contact_unsupported_topic(client: TestClient):
    """Verify 422 when discussion_topic is not a supported enum value."""
    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "discussion_topic": "invalid_topic_name",
            "message": "Valid length message for testing purposes.",
        },
    )
    assert response.status_code == 422


def test_submit_contact_message_too_short(client: TestClient):
    """Verify 422 when message is under 10 characters."""
    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "discussion_topic": "general",
            "message": "Short",  # < 10 chars
        },
    )
    assert response.status_code == 422


def test_submit_contact_header_injection_attempt(client: TestClient):
    """Verify that CRLF characters in the name field are rejected to prevent header injection."""
    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe\r\nBcc: victim@example.com",
            "email": "jane@example.com",
            "discussion_topic": "general",
            "message": "Trying to inject headers into the outgoing email.",
        },
    )
    assert response.status_code == 422


def test_submit_contact_duplicate_rejected(client: TestClient, app, mock_contact_service: AsyncMock):
    """Verify 409 Conflict when DuplicateSubmissionError is raised."""
    mock_contact_service.submit_inquiry.side_effect = DuplicateSubmissionError(
        "A message with this content was recently received."
    )
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service

    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "discussion_topic": "feedback",
            "message": "Submitting identical feedback twice in a row.",
        },
    )

    assert response.status_code == 409
    app.dependency_overrides.clear()


def test_submit_contact_unconfigured_error(client: TestClient, app, mock_contact_service: AsyncMock):
    """Verify 503 Service Unavailable when email provider credentials are not configured."""
    mock_contact_service.submit_inquiry.side_effect = EmailConfigurationError("Provider unconfigured.")
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service

    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "discussion_topic": "mentorship",
            "message": "Inquiring about the mentor application process.",
        },
    )

    assert response.status_code == 503
    app.dependency_overrides.clear()


def test_submit_contact_delivery_failure(client: TestClient, app, mock_contact_service: AsyncMock):
    """Verify 502 Bad Gateway when Gmail API delivery fails."""
    mock_contact_service.submit_inquiry.side_effect = EmailDeliveryError("Delivery failed.")
    app.dependency_overrides[get_contact_service] = lambda: mock_contact_service

    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "discussion_topic": "mentorship",
            "message": "Inquiring about the mentor application process.",
        },
    )

    assert response.status_code == 502
    app.dependency_overrides.clear()
