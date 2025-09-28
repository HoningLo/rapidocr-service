"""Configuration settings for the RapidOCR service."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=80, description="Server port")

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    # File management
    temp_dir: Path = Field(
        default=Path("temp"), description="Temporary files directory"
    )
    max_file_size: int = Field(
        default=10 * 1024 * 1024, description="Max file size in bytes (10MB)"
    )
    max_files: int = Field(
        default=10, description="Maximum number of files per request"
    )
    cleanup_interval: int = Field(
        default=3600, description="File cleanup interval in seconds"
    )
    file_retention: int = Field(
        default=3600, description="File retention time in seconds"
    )

    # OCR configuration
    ocr_use_gpu: bool | None = Field(
        default=None, description="Force GPU usage (None=auto-detect)"
    )
    ocr_providers: list[str] = Field(
        default=["CPUExecutionProvider"], description="ONNX runtime providers"
    )

    # Security
    allowed_extensions: list[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"],
        description="Allowed file extensions",
    )

    # API configuration
    api_title: str = Field(default="RapidOCR Service", description="API title")
    api_description: str = Field(
        default="FastAPI service for OCR processing with GPU support",
        description="API description",
    )
    api_version: str = Field(default="1.0.0", description="API version")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
