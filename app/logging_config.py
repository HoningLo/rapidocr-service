"""Logging configuration and utilities."""

import logging
import sys
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

import structlog
from structlog.contextvars import clear_contextvars

from .config import settings

# Context variable for request tracking
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def configure_logging() -> None:
    """Configure structured logging for the application."""

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            (
                structlog.dev.ConsoleRenderer()
                if settings.log_format == "text"
                else structlog.processors.JSONRenderer()
            ),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid4())


def set_request_context(request_id: str, **kwargs: Any) -> None:
    """Set request context for logging."""
    clear_contextvars()
    request_id_ctx.set(request_id)
    structlog.contextvars.bind_contextvars(request_id=request_id, **kwargs)


def get_request_id() -> str | None:
    """Get the current request ID from context."""
    return request_id_ctx.get()


class LoggingMixin:
    """Mixin class to add logging capabilities to other classes."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log an info message with optional context."""
        self.logger.info(message, **kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message with optional context."""
        self.logger.warning(message, **kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """Log an error message with optional context."""
        self.logger.error(message, **kwargs)

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message with optional context."""
        self.logger.debug(message, **kwargs)
