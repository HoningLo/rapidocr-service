# Multi-stage Docker build for RapidOCR Service using UV
FROM python:3.13-slim

# Install system dependencies for runtime and GPU support
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    curl \
    wget \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container
COPY . /app

# Install the application dependencies
WORKDIR /app
RUN uv sync --frozen --no-cache

# Create necessary directories and non-root user
RUN mkdir -p /app/temp /app/logs && \
    useradd --create-home --shell /bin/bash rapidocr && \
    chown -R rapidocr:rapidocr /app

USER rapidocr

# Set environment variables
ENV PYTHONPATH=/app
ENV TEMP_DIR=/app/temp
ENV LOG_LEVEL=INFO
ENV HOST=0.0.0.0
ENV PORT=80

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health/ || exit 1

# Run the application using uvicorn
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
