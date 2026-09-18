"""
GrowFlow — Contact Application Service.

Encapsulates business logic for public contact inquiries, server-side validation,
idempotency / duplicate delivery prevention, and reliable Gmail dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import time
from typing import TYPE_CHECKING
import uuid

from backend.app.infrastructure.email.exceptions import DuplicateSubmissionError
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.config.settings import Settings
    from backend.app.infrastructure.email.client import EmailClient

logger = get_logger("growflow.application.contact")

# In-memory sliding window cache for duplicate prevention: {hash: timestamp}
_RECENT_SUBMISSIONS: dict[str, float] = {}
_IDEMPOTENCY_WINDOW_SECONDS = 60.0


@dataclass(frozen=True)
class ContactSubmissionResult:
    """Canonical domain result for a processed contact inquiry."""

    submission_id: str
    status: str
    timestamp: str
    message: str


class ContactService:
    """Application service coordinating public contact submissions and email delivery."""

    def __init__(
        self,
        email_client: EmailClient,
        settings: Settings,
        outbox_service: OutboxService | None = None,
    ) -> None:
        self._email_client = email_client
        self._settings = settings
        self._outbox_service = outbox_service

    def _compute_submission_hash(self, email: str, topic: str, message: str) -> str:
        """Compute an SHA-256 fingerprint for idempotency checking."""
        normalized = f"{email.lower().strip()}:{topic.lower().strip()}:{message.strip()}"
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _check_and_record_idempotency(self, signature: str) -> None:
        """Prune expired entries and reject duplicate submissions within the idempotency window."""
        now = time.time()
        # Clean up entries older than 2x the window
        expired_keys = [
            k for k, t in _RECENT_SUBMISSIONS.items() if now - t > (_IDEMPOTENCY_WINDOW_SECONDS * 2)
        ]
        for k in expired_keys:
            _RECENT_SUBMISSIONS.pop(k, None)

        # Check if identical message was sent within the active window
        last_sent = _RECENT_SUBMISSIONS.get(signature)
        if last_sent and (now - last_sent) < _IDEMPOTENCY_WINDOW_SECONDS:
            logger.warning("Duplicate contact submission prevented", signature=signature[:12])
            raise DuplicateSubmissionError(
                "A message with this content was recently received. Please wait before resending."
            )

        _RECENT_SUBMISSIONS[signature] = now

    def _format_topic_label(self, topic: str) -> str:
        """Return a capitalized human-readable label for the discussion topic."""
        labels = {
            "general": "General Question",
            "product": "Product",
            "project": "Project",
            "mentorship": "Mentorship",
            "engineering": "Engineering",
            "feedback": "Feedback",
            "other": "Other",
        }
        return labels.get(topic.lower().strip(), topic.capitalize())

    async def submit_inquiry(
        self,
        name: str,
        email: str,
        discussion_topic: str,
        message: str,
    ) -> ContactSubmissionResult:
        """
        Validate, protect against duplicate delivery, and dispatch contact inquiry.
        Delivers email to the authoritative mailbox with visitor email set as Reply-To.
        """
        clean_name = name.strip()
        clean_email = email.strip()
        clean_topic = discussion_topic.strip()
        clean_message = message.strip()

        # Idempotency / duplicate check
        signature = self._compute_submission_hash(clean_email, clean_topic, clean_message)
        self._check_and_record_idempotency(signature)

        submission_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        now_iso = now.isoformat()
        topic_label = self._format_topic_label(clean_topic)

        # Structured subject and body
        subject = f"[GrowFlow Contact] {topic_label} — {clean_name}"
        body = (
            f"GrowFlow Contact Submission\n"
            f"--------------------------------------------------\n"
            f"Name:             {clean_name}\n"
            f"Email:            {clean_email}\n"
            f"Discussion Topic: {topic_label}\n"
            f"Submitted At:     {now_iso}\n"
            f"Submission ID:    {submission_id}\n"
            f"--------------------------------------------------\n\n"
            f"Message:\n{clean_message}\n"
        )

        target_mailbox = self._settings.email.CONTACT_MAILBOX or "neurachat.support@gmail.com"

        logger.info(
            "Dispatching contact inquiry email",
            submission_id=submission_id,
            topic=clean_topic,
            target_mailbox=target_mailbox,
        )

        # Deliver outbound email via Gmail OAuth client
        message_id = await self._email_client.send_email(
            to_email=target_mailbox,
            subject=subject,
            body_text=body,
            reply_to=clean_email,
        )

        logger.info(
            "Contact inquiry delivered successfully",
            submission_id=submission_id,
            provider_message_id=message_id,
        )

        # Optional outbox emission if available
        if self._outbox_service:
            try:
                await self._outbox_service.emit(
                    event_type="contact.inquiry_received",
                    actor_role="visitor",
                    resource_type="contact_submission",
                    resource_id=submission_id,
                    metadata={
                        "topic": clean_topic,
                        "email": clean_email,
                        "provider_message_id": message_id,
                    },
                )
            except Exception as exc:
                logger.warning("Could not persist contact event to outbox", error=str(exc))

        return ContactSubmissionResult(
            submission_id=submission_id,
            status="delivered",
            timestamp=now_iso,
            message="Message received. Thanks for reaching out. Your message has been submitted to the GrowFlow team.",
        )
