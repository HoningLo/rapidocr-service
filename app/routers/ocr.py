"""OCR processing endpoints."""

import time

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ..config import settings
from ..file_manager import file_manager
from ..logging_config import get_logger
from ..models import OCRResponse
from ..ocr_service import ocr_service

logger = get_logger(__name__)
router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/", response_model=OCRResponse)
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
            detail=f"Too many files. Maximum allowed: {settings.max_files}",
        )

    # Validate file sizes
    for file in files:
        if file.size and file.size > settings.max_file_size:
            logger.warning(
                "File too large",
                filename=file.filename,
                size=file.size,
                max_size=settings.max_file_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File {file.filename} is too large. Maximum size: {settings.max_file_size} bytes",
            )

    try:
        # Save uploaded files
        file_info_list = await file_manager.save_multiple_files(files)

        logger.info(
            "Processing OCR batch",
            file_count=len(file_info_list),
            files=[info[2] for info in file_info_list],  # original filenames
        )

        # Process OCR
        results = await ocr_service.process_multiple_images(file_info_list)

        # Clean up temporary files
        for _file_uuid, file_path, _ in file_info_list:
            file_manager.cleanup_file(file_path)

        processing_time = time.time() - start_time

        logger.info(
            "OCR batch completed",
            file_count=len(results),
            processing_time=processing_time,
            gpu_used=ocr_service.is_gpu_enabled(),
        )

        return OCRResponse(
            results=results,
            processing_time=processing_time,
            gpu_used=ocr_service.is_gpu_enabled(),
        )

    except Exception as e:
        processing_time = time.time() - start_time

        logger.error(
            "OCR processing failed",
            file_count=len(files),
            processing_time=processing_time,
            error=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        ) from e
