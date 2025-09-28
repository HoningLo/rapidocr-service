"""Main FastAPI application for RapidOCR service."""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .file_manager import file_manager
from .gpu_utils import gpu_detector
from .logging_config import (
    configure_logging,
    generate_request_id,
    get_logger,
    set_request_context,
)
from .models import ErrorResponse
from .routers import health, ocr

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan management."""
    # Startup
    logger.info("Starting RapidOCR service", version=settings.api_version)

    # Start file cleanup task
    await file_manager.start_cleanup_task()

    # Initialize GPU detection
    gpu_detector.detect_gpu()

    logger.info("RapidOCR service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down RapidOCR service")

    # Stop file cleanup task
    await file_manager.stop_cleanup_task()

    logger.info("RapidOCR service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Any) -> Response:
    """Add request logging and context."""
    request_id = generate_request_id()
    start_time = time.time()

    # Set request context for logging
    set_request_context(
        request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None,
    )

    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    # Log request completion
    processing_time = time.time() - start_time
    logger.info(
        "Request completed",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        processing_time=processing_time,
    )

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    request_id = generate_request_id()

    logger.error(
        "Unhandled exception",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        error=str(exc),
        error_type=type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            message="An internal server error occurred",
            details=None,
            request_id=request_id,
        ).model_dump(),
    )


# Root endpoint
@app.get("/", response_model=dict)
async def root() -> dict[str, Any]:
    """Root endpoint with basic service information."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(health.router)
app.include_router(ocr.router)

# Development server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
