# STEP 1: Use a pinned, stable base image
# Using 'bookworm' ensures you don't get 'trixie' (testing) which broke your last build.
FROM python:3.11-slim-bookworm AS builder

LABEL maintainer="redroom-dev"
LABEL version="1.1"

# Environment variables for Python performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# STEP 2: Optimized System Dependencies
# 1. Removed libfftw3-3 (libfftw3-dev handles it)
# 2. Combined updates and installs
# 3. Use opencv-python-headless in requirements.txt later to avoid UI bloat
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    build-essential \
    libopencv-dev \
    libfftw3-dev \
    sqlite3 \
    libsqlite3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# STEP 3: Layer Caching (The "Secret" to fast builds)
# Copy requirements first. If your code changes but requirements don't, 
# Docker skips the 'pip install' step entirely in the next build.
COPY redroom/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /app/requirements.txt

# STEP 4: Copy Application Code
# We copy this AFTER pip install so code changes don't trigger a full reinstall
COPY redroom /app/redroom
COPY LICENSE README.md ARCHITECTURE.md /app/

# STEP 5: Infrastructure Setup
RUN mkdir -p /app/data /app/logs /var/redroom/ledger /var/redroom/cache

# STEP 6: Security & User Management
# Create a system user without a home directory for maximum security
RUN groupadd -r redroom && useradd -r -g redroom -u 1000 redroom && \
    chown -R redroom:redroom /app /var/redroom

# Default Environment Configuration
ENV LEDGER_DB_PATH=/var/redroom/ledger/redroom_ledger.db \
    VLLM_ENDPOINT=http://vllm:8000 \
    REDROOM_LOG_LEVEL=INFO \
    REDROOM_MODE=production

# Health check (checks the actual orchestration endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/redroom/status || exit 1

EXPOSE 8002
USER redroom

# Entrypoint
CMD ["python", "-m", "redroom.orchestration.main"]
