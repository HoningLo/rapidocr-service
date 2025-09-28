"""Data models for the RapidOCR service."""

from pydantic import BaseModel, Field


class OCRResult(BaseModel):
    """OCR processing result for a single file."""

    FileName: str = Field(..., description="Original filename of the processed image")
    UUID: str = Field(..., description="Unique identifier for the processing session")
    Context: str = Field(..., description="Extracted text content from the image")


class OCRResponse(BaseModel):
    """Response model for OCR API endpoints."""

    results: list[OCRResult] = Field(..., description="List of OCR results")
    processing_time: float = Field(..., description="Total processing time in seconds")
    gpu_used: bool = Field(..., description="Whether GPU acceleration was used")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    gpu_available: bool = Field(..., description="GPU availability status")
    uptime: float = Field(..., description="Service uptime in seconds")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: str | None = Field(None, description="Additional error details")
    request_id: str | None = Field(None, description="Request identifier for tracking")
