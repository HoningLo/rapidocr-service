# RapidOCR FastAPI Service

A high-performance FastAPI service that provides OCR capabilities using RapidOCR with GPU acceleration support, comprehensive logging, and UUID-based file tracking.

## Features

- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation
- 🔥 **GPU Acceleration**: Automatic GPU detection and utilization when available
- 📝 **Comprehensive Logging**: Structured logging for all operations with unique request tracking
- 🆔 **UUID Management**: Unique identifiers for all uploaded files and processing results
- 📁 **Smart File Management**: Temporary file storage with automatic cleanup
- 📷 **Multi-Image Support**: Process multiple images in a single request
- 🔄 **JSON Responses**: Standardized response format with filename, UUID, and extracted text
- 🐍 **Python 3.13+**: Modern Python with uv for fast dependency management

## Architecture

The service follows these core principles:
- **API-First Design**: Clean RESTful interface with type safety
- **Performance Optimization**: GPU acceleration with CPU fallback
- **Comprehensive Logging**: Full audit trail for all operations
- **Robust File Management**: UUID-based file tracking with cleanup
- **Data Integrity**: Complete traceability from input to output

## Quick Start

### Prerequisites

- Python 3.13+
- uv package manager
- Optional: CUDA-compatible GPU for acceleration

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rapidocr-service
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Run the service:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Usage

#### Single Image OCR
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image.jpg"
```

#### Multiple Images OCR
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image1.jpg" \
  -F "file=@image2.png"
```

#### Response Format
```json
[
  {
    "FileName": "image1.jpg",
    "UUID": "550e8400-e29b-41d4-a716-446655440000",
    "Context": "Extracted text from the image..."
  }
]
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black .
uv run isort .
```

### Type Checking
```bash
uv run mypy .
```

## Configuration

Environment variables:
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `TEMP_DIR`: Temporary file storage directory
- `MAX_FILE_SIZE`: Maximum upload file size in bytes
- `CLEANUP_INTERVAL`: File cleanup interval in seconds

## License

MIT License - see LICENSE file for details.
