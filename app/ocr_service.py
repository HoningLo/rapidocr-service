"""OCR processing service using RapidOCR."""

import time
from pathlib import Path
from typing import Any

from rapidocr_onnxruntime import RapidOCR

from .config import settings
from .gpu_utils import gpu_detector
from .logging_config import LoggingMixin
from .models import OCRResult


class OCRService(LoggingMixin):
    """Service for performing OCR on images using RapidOCR."""

    def __init__(self) -> None:
        super().__init__()
        self._ocr_engine: RapidOCR | None = None
        self._gpu_config: dict[str, Any] = {}
        self._initialize_engine()

    def _initialize_engine(self) -> None:
        """Initialize the RapidOCR engine with GPU configuration."""
        try:
            # Get GPU configuration
            self._gpu_config = gpu_detector.configure_for_gpu()

            # Configure RapidOCR parameters
            ocr_config: dict[str, Any] = {}

            # Force GPU usage if specified in settings
            if settings.ocr_use_gpu is not None:
                if settings.ocr_use_gpu and not gpu_detector.detect_gpu():
                    self.log_warning(
                        "GPU usage requested but no GPU available, falling back to CPU"
                    )
                elif settings.ocr_use_gpu:
                    self.log_info("Forcing GPU usage as per configuration")
                else:
                    self.log_info("Forcing CPU usage as per configuration")
                    # Override GPU detection
                    self._gpu_config = {"use_cpu": True}

            # Initialize RapidOCR engine
            self._ocr_engine = RapidOCR(**ocr_config)

            self.log_info(
                "OCR engine initialized",
                gpu_config=self._gpu_config,
                providers=settings.ocr_providers,
            )

        except Exception as e:
            self.log_error("Failed to initialize OCR engine", error=str(e))
            raise

    def is_gpu_enabled(self) -> bool:
        """Check if GPU acceleration is enabled."""
        return self._gpu_config.get("use_cuda", False) or self._gpu_config.get(
            "use_opencl", False
        )

    async def process_image(
        self, file_path: Path, file_uuid: str, original_filename: str
    ) -> OCRResult:
        """
        Process a single image file and extract text.

        Args:
            file_path: Path to the image file
            file_uuid: UUID assigned to this file
            original_filename: Original filename of the uploaded file

        Returns:
            OCRResult: Contains extracted text and metadata
        """
        start_time = time.time()

        try:
            self.log_info(
                "Starting OCR processing",
                file_uuid=file_uuid,
                filename=original_filename,
                file_path=str(file_path),
            )

            # Perform OCR
            if self._ocr_engine is None:
                raise RuntimeError("OCR engine not initialized")
            result = self._ocr_engine(str(file_path))

            # Extract text from result
            # RapidOCR returns format: (detection_results, timing_info) or None
            # detection_results is a list of [[[bbox], text, confidence], ...]
            extracted_text = ""

            if result and len(result) >= 1 and result[0]:
                # result[0] contains the detection results
                detection_results = result[0]
                text_lines = []

                for item in detection_results:
                    if len(item) >= 2 and item[1]:  # item[1] is the text
                        text_lines.append(str(item[1]).strip())

                extracted_text = "\n".join(text_lines)

            processing_time = time.time() - start_time

            self.log_info(
                "OCR processing completed",
                file_uuid=file_uuid,
                filename=original_filename,
                processing_time=processing_time,
                text_length=len(extracted_text),
                gpu_used=self.is_gpu_enabled(),
            )

            return OCRResult(
                FileName=original_filename,
                UUID=file_uuid,
                Context=extracted_text or "No text detected",
            )

        except Exception as e:
            processing_time = time.time() - start_time

            self.log_error(
                "OCR processing failed",
                file_uuid=file_uuid,
                filename=original_filename,
                processing_time=processing_time,
                error=str(e),
            )

            # Return error result instead of raising
            return OCRResult(
                FileName=original_filename,
                UUID=file_uuid,
                Context=f"OCR processing failed: {str(e)}",
            )

    async def process_multiple_images(
        self, file_info_list: list[tuple[str, Path, str]]
    ) -> list[OCRResult]:
        """
        Process multiple image files.

        Args:
            file_info_list: List of (uuid, file_path, original_filename) tuples

        Returns:
            List[OCRResult]: Results for all processed images
        """
        start_time = time.time()
        results = []

        self.log_info(
            "Starting batch OCR processing",
            file_count=len(file_info_list),
            gpu_enabled=self.is_gpu_enabled(),
        )

        for file_uuid, file_path, original_filename in file_info_list:
            result = await self.process_image(file_path, file_uuid, original_filename)
            results.append(result)

        total_time = time.time() - start_time

        self.log_info(
            "Batch OCR processing completed",
            file_count=len(file_info_list),
            total_time=total_time,
            avg_time_per_file=total_time / len(file_info_list) if file_info_list else 0,
        )

        return results

    def get_engine_info(self) -> dict[str, Any]:
        """Get information about the OCR engine for health checks."""
        return {
            "engine_initialized": self._ocr_engine is not None,
            "gpu_config": self._gpu_config,
            "gpu_enabled": self.is_gpu_enabled(),
            "providers": settings.ocr_providers,
        }


# Global OCR service instance
ocr_service = OCRService()
