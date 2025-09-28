# Multi-stage Docker build for RapidOCR Service
FROM python:3.13-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY app/ ./app/

# Install dependencies and build wheel
RUN uv build


FROM python:3.13-slim as runtime

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv in runtime
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash rapidocr
USER rapidocr
WORKDIR /home/rapidocr

# Copy built wheel and install
COPY --from=builder /app/dist/*.whl ./
RUN uv pip install --system *.whl && rm *.whl

# Create necessary directories
RUN mkdir -p temp logs

# Set environment variables
ENV PYTHONPATH=/home/rapidocr
ENV TEMP_DIR=/home/rapidocr/temp
ENV LOG_LEVEL=INFO
ENV HOST=0.0.0.0
ENV PORT=80

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
