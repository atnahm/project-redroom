# REDROOM - Tier-1 Deepfake Detection System
# This Dockerfile builds the complete forensic analysis engine
# Build: docker build -t project-redroom:latest .
# Run: docker run -p 8002:8002 project-redroom:latest

FROM python:3.11-slim

LABEL maintainer="redroom-dev"
LABEL version="1.0"
LABEL description="Tier-1 forensic deepfake detection system with multi-phase pipeline"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    libopencv-dev python3-opencv \
    libfftw3-dev libfftw3-3 \
    sqlite3 libsqlite3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY redroom /app/redroom
COPY LICENSE /app/
COPY README.md /app/
COPY ARCHITECTURE.md /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/redroom/requirements.txt

# Create necessary directories
RUN mkdir -p /app/data \
    && mkdir -p /app/logs \
    && mkdir -p /var/redroom/ledger \
    && mkdir -p /var/redroom/cache

# Set permissions
RUN chmod -R 755 /app/redroom

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/redroom/status || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LEDGER_DB_PATH=/var/redroom/ledger/redroom_ledger.db
ENV VLLM_ENDPOINT=http://vllm:8000
ENV REDROOM_LOG_LEVEL=INFO
ENV REDROOM_MODE=production

WORKDIR /app

# Expose API port
EXPOSE 8002

# Create non-root user for security
RUN useradd -m -u 1000 redroom && \
    chown -R redroom:redroom /app /var/redroom

USER redroom

# Start the FastAPI application
CMD ["python", "-m", "redroom.orchestration.main"]
