# Multi-stage Docker build for RapidOCR Service using UV
FROM python:3.13-slim

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container
COPY . /app

# Install the application dependencies
WORKDIR /app
RUN uv sync --frozen --no-cache

# Create non-root user
RUN useradd --create-home --shell /bin/bash rapidocr
USER rapidocr

# Create necessary directories
RUN mkdir -p /app/temp /app/logs

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
    CMD curl -f http://localhost:80/health || exit 1

# Run the application using uvicorn
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
