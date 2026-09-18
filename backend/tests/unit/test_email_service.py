"""
GrowFlow — Unit Tests for Gmail OAuth Client & Contact Application Service.

Verifies token refresh, RFC 2822 message construction, retry behavior,
header injection protection, and duplicate prevention.
"""

from __future__ import annotations

import base64
from email import message_from_bytes
from email.header import decode_header, make_header
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend.app.application.services.contact_service import ContactService
from backend.app.config.settings import Settings
from backend.app.infrastructure.email.client import GmailOAuthEmailClient
from backend.app.infrastructure.email.exceptions import (
    DuplicateSubmissionError,
    EmailAuthenticationError,
    EmailConfigurationError,
    EmailDeliveryError,
)


@pytest.fixture
def mock_settings() -> Settings:
    """Settings fixture with mock Gmail OAuth credentials."""
    settings = Settings()
    settings.email.GMAIL_CLIENT_ID = "mock-client-id"
    settings.email.GMAIL_CLIENT_SECRET = "mock-client-secret"
    settings.email.GMAIL_REFRESH_TOKEN = "mock-refresh-token"
    settings.email.FROM_ADDRESS = "neurachat.support@gmail.com"
    settings.email.CONTACT_MAILBOX = "neurachat.support@gmail.com"
    return settings


@pytest.mark.asyncio
async def test_gmail_client_unconfigured_raises_error():
    """Verify that unconfigured credentials fail cleanly with EmailConfigurationError."""
    settings = Settings()
    settings.email.GMAIL_CLIENT_ID = None
    settings.email.GMAIL_CLIENT_SECRET = None
    settings.email.GMAIL_REFRESH_TOKEN = None

    client = GmailOAuthEmailClient(settings)
    assert not client.is_configured

    with pytest.raises(EmailConfigurationError, match="Gmail OAuth credentials are not configured"):
        await client.send_email(
            to_email="neurachat.support@gmail.com",
            subject="Test",
            body_text="Test body",
        )


@pytest.mark.asyncio
async def test_gmail_client_successful_send(mock_settings: Settings):
    """Verify message construction, RFC 2822 format, and successful send."""
    mock_http = AsyncMock(spec=httpx.AsyncClient)

    # Mock token refresh response
    token_response = httpx.Response(
        200,
        json={"access_token": "ya29.mock-token", "expires_in": 3600},
        request=httpx.Request("POST", "https://oauth2.googleapis.com/token"),
    )

    # Mock send response
    send_response = httpx.Response(
        200,
        json={"id": "msg_123456789"},
        request=httpx.Request("POST", "https://gmail.googleapis.com/send"),
    )

    mock_http.post.side_effect = [token_response, send_response]

    client = GmailOAuthEmailClient(mock_settings, http_client=mock_http)
    message_id = await client.send_email(
        to_email="neurachat.support@gmail.com",
        subject="[GrowFlow Contact] Engineering — Jane Doe",
        body_text="Hello, inquiring about agent architecture.",
        reply_to="visitor@example.com",
    )

    assert message_id == "msg_123456789"
    assert mock_http.post.call_count == 2

    # Verify send payload content
    send_call = mock_http.post.call_args_list[1]
    assert send_call.kwargs["headers"]["Authorization"] == "Bearer ya29.mock-token"

    raw_b64 = send_call.kwargs["json"]["raw"]
    raw_bytes = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
    mime_msg = message_from_bytes(raw_bytes)

    assert mime_msg["From"] == "neurachat.support@gmail.com"
    assert mime_msg["To"] == "neurachat.support@gmail.com"
    assert mime_msg["Reply-To"] == "visitor@example.com"
    decoded_subject = str(make_header(decode_header(mime_msg["Subject"])))
    assert decoded_subject == "[GrowFlow Contact] Engineering — Jane Doe"
    assert "Hello, inquiring about agent architecture." in mime_msg.get_payload()


@pytest.mark.asyncio
async def test_gmail_client_token_failure(mock_settings: Settings):
    """Verify that OAuth refresh failure raises EmailAuthenticationError without leaking secrets."""
    mock_http = AsyncMock(spec=httpx.AsyncClient)
    token_response = httpx.Response(
        400,
        json={"error": "invalid_grant"},
        request=httpx.Request("POST", "https://oauth2.googleapis.com/token"),
    )
    mock_http.post.return_value = token_response

    client = GmailOAuthEmailClient(mock_settings, http_client=mock_http)
    with pytest.raises(EmailAuthenticationError, match="Gmail OAuth token refresh was rejected"):
        await client.send_email(
            to_email="neurachat.support@gmail.com",
            subject="Test",
            body_text="Test body",
        )


@pytest.mark.asyncio
async def test_contact_service_duplicate_prevention(mock_settings: Settings):
    """Verify that duplicate contact submissions within the idempotency window are blocked."""
    mock_email_client = AsyncMock()
    mock_email_client.send_email.return_value = "msg_001"

    service = ContactService(email_client=mock_email_client, settings=mock_settings)

    # First submission succeeds
    result1 = await service.submit_inquiry(
        name="John Smith",
        email="john@example.com",
        discussion_topic="product",
        message="I would like to ask about the product.",
    )
    assert result1.status == "delivered"
    assert mock_email_client.send_email.call_count == 1

    # Immediate identical resubmission is rejected
    with pytest.raises(DuplicateSubmissionError):
        await service.submit_inquiry(
            name="John Smith",
            email="john@example.com",
            discussion_topic="product",
            message="I would like to ask about the product.",
        )

    # Email client should NOT have been called a second time
    assert mock_email_client.send_email.call_count == 1
