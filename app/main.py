"""Main FastAPI application for RapidOCR service."""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile, status
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
from .models import ErrorResponse, HealthResponse, OCRResponse
from .ocr_service import ocr_service

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Application startup time
startup_time = time.time()


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
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Any) -> Response:
    """Add request logging and context."""
    request_id = generate_request_id()
    start_time = time.time()

    # Set logging context
    set_request_context(
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else "unknown",
    )

    logger.info("Request started")

    try:
        response = await call_next(request)

        # Log successful response
        processing_time = time.time() - start_time
        logger.info(
            "Request completed",
            status_code=response.status_code,
            processing_time=processing_time,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error("Request failed", error=str(e), processing_time=processing_time)

        # Return structured error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred",
                details=str(e),
                request_id=request_id,
            ).dict(),
            headers={"X-Request-ID": request_id},
        )


@app.get("/", response_model=dict)
async def root() -> dict[str, Any]:
    """Root endpoint with basic service information."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs_url": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint with detailed system information."""
    current_time = time.time()
    uptime = current_time - startup_time

    # Get GPU information
    gpu_info = gpu_detector.get_gpu_info()

    # Get OCR engine information
    ocr_info = ocr_service.get_engine_info()

    logger.info(
        "Health check requested",
        uptime=uptime,
        gpu_available=gpu_info["gpu_available"],
        ocr_engine_ready=ocr_info["engine_initialized"],
    )

    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        gpu_available=gpu_info["gpu_available"],
        uptime=uptime,
    )


@app.post("/ocr", response_model=OCRResponse)
async def process_ocr(files: list[UploadFile] = File(...)) -> OCRResponse:
    """
    Process one or more images for OCR text extraction.

    Accepts multiple image files and returns extracted text for each.
    Each file is assigned a UUID for tracking purposes.
    """
    start_time = time.time()

    # Validate number of files
    if len(files) > settings.max_files:
        logger.warning(
            "Too many files uploaded",
            file_count=len(files),
            max_allowed=settings.max_files,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum {settings.max_files} files allowed per request.",
        )

    # Validate file sizes and types
    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have a filename",
            )

        # Read a small chunk to check size (FastAPI doesn't provide size directly)
        content = await file.read(settings.max_file_size + 1)
        await file.seek(0)  # Reset file pointer

        if len(content) > settings.max_file_size:
            logger.warning(
                "File too large",
                filename=file.filename,
                size=len(content),
                max_size=settings.max_file_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File {file.filename} is too large. Maximum size: {settings.max_file_size} bytes",
            )

    logger.info(
        "OCR request received",
        file_count=len(files),
        filenames=[f.filename for f in files],
    )

    try:
        # Save uploaded files
        file_info_list = await file_manager.save_multiple_files(files)

        # Process OCR for all files
        ocr_results = await ocr_service.process_multiple_images(file_info_list)

        # Clean up temporary files
        for _file_uuid, file_path, _ in file_info_list:
            file_manager.cleanup_file(file_path)

        processing_time = time.time() - start_time

        logger.info(
            "OCR request completed successfully",
            file_count=len(files),
            processing_time=processing_time,
            gpu_used=ocr_service.is_gpu_enabled(),
        )

        return OCRResponse(
            results=ocr_results,
            processing_time=processing_time,
            gpu_used=ocr_service.is_gpu_enabled(),
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        processing_time = time.time() - start_time

        logger.error(
            "OCR request failed",
            file_count=len(files),
            processing_time=processing_time,
            error=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        ) from e


@app.get("/stats", response_model=dict)
async def get_stats() -> dict[str, Any]:
    """Get service statistics and information."""
    # Get various service information
    gpu_info = gpu_detector.get_gpu_info()
    ocr_info = ocr_service.get_engine_info()
    temp_dir_info = file_manager.get_temp_dir_info()

    uptime = time.time() - startup_time

    return {
        "service": {
            "name": settings.api_title,
            "version": settings.api_version,
            "uptime_seconds": uptime,
        },
        "gpu": gpu_info,
        "ocr_engine": ocr_info,
        "file_management": temp_dir_info,
        "configuration": {
            "max_file_size": settings.max_file_size,
            "max_files": settings.max_files,
            "cleanup_interval": settings.cleanup_interval,
            "file_retention": settings.file_retention,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
