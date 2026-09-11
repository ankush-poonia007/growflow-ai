"""
GrowFlow — Database Exception Integration.

Maps SQLAlchemy database exceptions to GrowFlow's canonical exception hierarchy
(established in Gate 02) so that database errors produce safe, machine-readable
API error responses without leaking internal state.

Architecture ref:
  - 6A § 22 — Exception Architecture
  - 6A § 23 — Error Codes
  - 6B — Database Architecture

Integration points:
  - Database integrity violations (unique constraints, FK violations) → ConflictException
  - Database operational errors (connection timeout, pool exhausted) → InfrastructureException
  - No-result-found from strict queries → NotFoundException

These handlers are used at the repository/data-access layer boundary.
Application services catch GrowFlowException subclasses and let the
global handler (established in Gate 02) translate them to safe API responses.

SAFETY: No database credentials, query text, or raw SQL is ever included in
exceptions raised here. Error details are sanitised before propagation.
"""

from __future__ import annotations

from sqlalchemy.exc import (  # noqa: TC002
    IntegrityError,
    NoResultFound,
    OperationalError,
    SQLAlchemyError,
)

from backend.app.shared.exceptions import (
    ConflictException,
    InfrastructureException,
    NotFoundException,
)
from backend.app.shared.logging import get_logger

logger = get_logger("growflow.infrastructure.database.exceptions")


def handle_integrity_error(exc: IntegrityError, context: str = "") -> None:
    """
    Translate a SQLAlchemy IntegrityError to a GrowFlow ConflictException.

    IntegrityError covers:
    - Unique constraint violations (duplicate records)
    - Foreign-key constraint violations (orphaned records)
    - Not-null constraint violations (required field missing)

    Args:
        exc: The SQLAlchemy IntegrityError instance.
        context: Optional human-readable context (e.g. "creating user").

    Raises:
        ConflictException: Always raised; never propagates raw SQLAlchemy exception.
    """
    logger.warning(
        "Database integrity constraint violated",
        context=context,
        # Raw exception message may contain table/column names but not credentials.
        # Still sanitised below to avoid leaking schema details in the API response.
        error_type=type(exc).__name__,
    )

    message = f"A conflict occurred{' while ' + context if context else ''}."
    raise ConflictException(message=message) from exc


def handle_no_result_found(exc: NoResultFound, resource: str = "Resource") -> None:
    """
    Translate a SQLAlchemy NoResultFound to a GrowFlow NotFoundException.

    Args:
        exc: The SQLAlchemy NoResultFound instance.
        resource: Human-readable resource name (e.g. "Project", "User").

    Raises:
        NotFoundException: Always raised.
    """
    raise NotFoundException(message=f"{resource} not found.") from exc


def handle_operational_error(exc: OperationalError, context: str = "") -> None:
    """
    Translate a SQLAlchemy OperationalError to a GrowFlow InfrastructureException.

    OperationalError covers:
    - Connection failures
    - Pool exhaustion
    - Timeout errors
    - SSL errors

    Args:
        exc: The SQLAlchemy OperationalError instance.
        context: Optional context string.

    Raises:
        InfrastructureException: Always raised; credential-safe message only.
    """
    logger.error(
        "Database operational error",
        context=context,
        error_type=type(exc).__name__,
        # Never log exc.params or connection string.
    )

    raise InfrastructureException(
        message="A database error occurred. Please try again."
    ) from exc


def handle_sqlalchemy_error(exc: SQLAlchemyError, context: str = "") -> None:
    """
    Generic handler for unexpected SQLAlchemy errors.

    Falls back to InfrastructureException for any SQLAlchemy error not
    handled by a more specific handler above.

    Args:
        exc: Any SQLAlchemy exception.
        context: Optional context string.

    Raises:
        InfrastructureException: Always raised.
    """
    logger.error(
        "Unexpected database error",
        context=context,
        error_type=type(exc).__name__,
    )

    raise InfrastructureException(
        message="An unexpected database error occurred."
    ) from exc
