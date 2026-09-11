"""
GrowFlow — Structured Logging Setup.

Configures standard library logging and structlog with correlation support,
secret redaction, ISO timestamps, and environment-aware formatting.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import structlog

from backend.app.config.settings import Environment, Settings
from backend.app.shared.logging.context import get_correlation_id, get_request_id
from backend.app.shared.logging.filters import redact_secrets_processor

if TYPE_CHECKING:
    from structlog.types import EventDict, WrappedLogger


def inject_correlation_context(
    _logger: WrappedLogger,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Inject current correlation_id and request_id into the log event."""
    correlation_id = get_correlation_id()
    if correlation_id and "correlation_id" not in event_dict:
        event_dict["correlation_id"] = correlation_id

    request_id = get_request_id()
    if request_id and "request_id" not in event_dict:
        event_dict["request_id"] = request_id

    return event_dict


def setup_logging(settings: Settings | None = None) -> None:
    """
    Initialize structured logging.

    Applies secret redaction, correlation tracking, and JSON or console formatting.
    """
    log_level_str = settings.app.LOG_LEVEL.upper() if settings else "INFO"
    log_level = getattr(logging, log_level_str, logging.INFO)
    is_dev = (settings is None) or (settings.app.ENV == Environment.DEVELOPMENT)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        inject_correlation_context,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_secrets_processor,
    ]

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    renderer: structlog.types.Processor
    if is_dev and not (settings and settings.app.TESTING):
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Quiet overly chatty loggers
    for noisy in ("uvicorn.access", "httpcore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str = "growflow") -> structlog.stdlib.BoundLogger:
    """Return a configured structlog logger instance."""
    return structlog.get_logger(name)  # type: ignore[return-value]
