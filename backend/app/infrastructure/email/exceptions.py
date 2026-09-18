"""
GrowFlow — Email Infrastructure Exceptions.

Defines domain-specific errors for email dispatch, OAuth token refresh,
and configuration failures. Prevents leakage of internal credentials or tokens.
"""

from __future__ import annotations


class EmailServiceError(Exception):
    """Base exception for all email-related failures."""

    def __init__(self, message: str = "Email service operation failed.") -> None:
        super().__init__(message)
        self.message = message


class EmailConfigurationError(EmailServiceError):
    """Raised when email provider or OAuth credentials are unconfigured or incomplete."""

    def __init__(self, message: str = "Email service is not configured.") -> None:
        super().__init__(message)


class EmailAuthenticationError(EmailServiceError):
    """Raised when OAuth token refresh or authentication fails."""

    def __init__(self, message: str = "Email service authentication failed.") -> None:
        super().__init__(message)


class EmailDeliveryError(EmailServiceError):
    """Raised when message dispatch via Gmail API fails."""

    def __init__(self, message: str = "Failed to deliver email message.") -> None:
        super().__init__(message)


class DuplicateSubmissionError(EmailServiceError):
    """Raised when an identical contact submission is detected within the idempotency window."""

    def __init__(
        self,
        message: str = "A message with this content was recently received. Please wait before resending.",
    ) -> None:
        super().__init__(message)
