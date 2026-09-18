"""GrowFlow — Email Infrastructure Package."""

from backend.app.infrastructure.email.client import (
    EmailClient,
    GmailOAuthEmailClient,
)
from backend.app.infrastructure.email.exceptions import (
    DuplicateSubmissionError,
    EmailAuthenticationError,
    EmailConfigurationError,
    EmailDeliveryError,
    EmailServiceError,
)

__all__ = [
    "DuplicateSubmissionError",
    "EmailAuthenticationError",
    "EmailClient",
    "EmailConfigurationError",
    "EmailDeliveryError",
    "EmailServiceError",
    "GmailOAuthEmailClient",
]
