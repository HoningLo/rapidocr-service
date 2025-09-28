"""Health check and monitoring endpoints."""

import time
from typing import Any

from fastapi import APIRouter

from ..config import settings
from ..file_manager import file_manager
from ..gpu_utils import gpu_detector
from ..logging_config import get_logger
from ..models import HealthResponse
from ..ocr_service import ocr_service

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

# Application startup time for uptime calculation
startup_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Comprehensive health check endpoint."""
    # Calculate uptime
    uptime = time.time() - startup_time

    # Get various service information
    gpu_info = gpu_detector.get_gpu_info()
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


@router.get("/stats", response_model=dict)
async def get_stats() -> dict[str, Any]:
    """Get detailed service statistics and information."""
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
