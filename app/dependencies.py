"""FastAPI dependencies for dependency injection."""

from typing import Any

from fastapi import Request

from .logging_config import get_logger, get_request_id

logger = get_logger(__name__)


async def get_request_info(request: Request) -> dict[str, Any]:
    """Get request information for logging and tracking."""
    request_id = get_request_id()
    return {
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


def get_current_logger() -> Any:
    """Get the current logger instance."""
    return logger
