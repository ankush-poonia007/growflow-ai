"""
GrowFlow — Gmail OAuth Email Client.

Implements outbound email delivery via Google OAuth 2.0 and the Gmail REST API v1.
OAuth credentials, tokens, and authorization processes remain strictly server-side.
"""

from __future__ import annotations

import base64
from email.message import EmailMessage
import time
from typing import Any, Protocol

import httpx

from backend.app.config.settings import Settings  # noqa: TC001
from backend.app.infrastructure.email.exceptions import (
    EmailAuthenticationError,
    EmailConfigurationError,
    EmailDeliveryError,
)
from backend.app.shared.logging import get_logger

logger = get_logger("growflow.infrastructure.email")

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


class EmailClient(Protocol):
    """Protocol defining the outbound email client contract."""

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        *,
        reply_to: str | None = None,
    ) -> str:
        """Send an email message and return a provider message ID."""
        ...


class GmailOAuthEmailClient:
    """
    Outbound email client using server-side Google OAuth 2.0 and Gmail API.

    Authenticates via Google refresh token, caches access tokens until expiry,
    and dispatches RFC 2822 messages via the official Gmail v1 REST API.
    """

    def __init__(
        self,
        settings: Settings,
        *,
        token_url: str = GOOGLE_TOKEN_URL,
        send_url: str = GMAIL_SEND_URL,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._token_url = token_url
        self._send_url = send_url
        self._http_client = http_client

        self._client_id = settings.email.GMAIL_CLIENT_ID
        self._client_secret = settings.email.GMAIL_CLIENT_SECRET
        self._refresh_token = settings.email.GMAIL_REFRESH_TOKEN
        self._from_address = settings.email.FROM_ADDRESS or "neurachat.support@gmail.com"

        # In-memory access token cache
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    @property
    def is_configured(self) -> bool:
        """Return True if all required Google OAuth credentials are present."""
        return bool(
            self._client_id
            and self._client_secret
            and self._refresh_token
            and not self._client_id.startswith("your-")
        )

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        """
        Obtain a valid Gmail access token using the OAuth refresh token flow.
        Caches the token with a 60-second safety buffer before expiration.
        """
        if not self.is_configured:
            logger.error("Gmail OAuth credentials are missing or unconfigured.")
            raise EmailConfigurationError("Gmail OAuth credentials are not configured.")

        # Return cached token if still valid
        now = time.time()
        if self._access_token and now < (self._token_expires_at - 60):
            return self._access_token

        logger.info(
            "Refreshing Gmail OAuth access token",
            token_url=self._token_url,
            from_address=self._from_address,
        )

        try:
            response = await client.post(
                self._token_url,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "refresh_token": self._refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=15.0,
            )
        except httpx.RequestError as exc:
            logger.error("Network error during Gmail OAuth token refresh", error=str(exc))
            raise EmailAuthenticationError(
                "Failed to communicate with authentication provider."
            ) from exc

        if response.status_code != 200:
            logger.error(
                "Gmail OAuth token refresh failed",
                status_code=response.status_code,
            )
            raise EmailAuthenticationError("Gmail OAuth token refresh was rejected.")

        data: dict[str, Any] = response.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)

        if not access_token:
            logger.error("OAuth token response did not contain access_token")
            raise EmailAuthenticationError("Invalid token response from authentication provider.")

        self._access_token = access_token
        self._token_expires_at = now + float(expires_in)
        return access_token

    def _build_raw_message(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        reply_to: str | None = None,
    ) -> str:
        """
        Build an RFC 2822 EmailMessage and encode as URL-safe base64.
        Guarantees that From is the authoritative mailbox and visitor email is Reply-To only.
        """
        # Protect against CRLF header injection
        clean_to = to_email.replace("\r", "").replace("\n", "").strip()
        clean_subject = subject.replace("\r", "").replace("\n", "").strip()

        msg = EmailMessage()
        msg["From"] = self._from_address
        msg["To"] = clean_to
        msg["Subject"] = clean_subject

        if reply_to:
            clean_reply_to = reply_to.replace("\r", "").replace("\n", "").strip()
            msg["Reply-To"] = clean_reply_to

        msg.set_content(body_text)

        raw_bytes = msg.as_bytes()
        return base64.urlsafe_b64encode(raw_bytes).decode("utf-8")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        *,
        reply_to: str | None = None,
    ) -> str:
        """
        Deliver an email message using the Gmail v1 messages.send API.
        Includes automatic retries for transient failures (status 500, 502, 503, 504).
        """
        raw_message = self._build_raw_message(
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            reply_to=reply_to,
        )

        max_attempts = 3
        backoff_seconds = 1.0

        async def _execute_send(client: httpx.AsyncClient) -> str:
            token = await self._get_access_token(client)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            body = {"raw": raw_message}

            last_error: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    response = await client.post(
                        self._send_url,
                        headers=headers,
                        json=body,
                        timeout=20.0,
                    )

                    if response.status_code in (200, 201):
                        resp_data = response.json()
                        message_id = str(resp_data.get("id", "delivered"))
                        logger.info(
                            "Gmail message sent successfully",
                            message_id=message_id,
                            to=to_email,
                        )
                        return message_id

                    # If token expired mid-flight (401), invalidate and refresh once
                    if response.status_code == 401 and attempt < max_attempts:
                        logger.warning("Access token expired; refreshing token for retry")
                        self._access_token = None
                        token = await self._get_access_token(client)
                        headers["Authorization"] = f"Bearer {token}"
                        continue

                    # Retry on transient 5xx server errors
                    if response.status_code in (500, 502, 503, 504) and attempt < max_attempts:
                        logger.warning(
                            "Transient error from Gmail API; retrying",
                            status_code=response.status_code,
                            attempt=attempt,
                        )
                        time.sleep(backoff_seconds * attempt)
                        continue

                    # Non-retryable error
                    logger.error(
                        "Gmail API rejected message send",
                        status_code=response.status_code,
                    )
                    raise EmailDeliveryError(
                        f"Gmail API rejected message delivery with status {response.status_code}."
                    )

                except httpx.RequestError as exc:
                    last_error = exc
                    logger.warning(
                        "Network exception during Gmail API send",
                        attempt=attempt,
                        error=str(exc),
                    )
                    if attempt < max_attempts:
                        time.sleep(backoff_seconds * attempt)
                        continue
                    break

            raise EmailDeliveryError("Failed to deliver email after retry attempts.") from last_error

        if self._http_client:
            return await _execute_send(self._http_client)

        async with httpx.AsyncClient() as client:
            return await _execute_send(client)
