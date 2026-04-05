# REDROOM Deepfake Detection System - Docker Image
# Build: docker build -t redroom:latest .
# Run: docker-compose up -d

FROM python:3.11-slim

LABEL maintainer="redroom-dev"
LABEL version="1.0"
LABEL description="Video forensic analysis system"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    libopencv-dev python3-opencv \
    libfftw3-dev libfftw3-3 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY redroom /app/redroom
COPY LICENSE /app/
COPY README.md /app/

RUN pip install --no-cache-dir -r /app/redroom/requirements.txt

RUN mkdir -p /app/data \
    && mkdir -p /app/logs \
    && mkdir -p /var/redroom/ledger

RUN chmod -R 755 /app/redroom

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/redroom/status || exit 1

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LEDGER_DB_PATH=/var/redroom/ledger/redroom_ledger.db
ENV VLLM_ENDPOINT=http://vllm:8000

WORKDIR /app

EXPOSE 8002

RUN useradd -m -u 1000 redroom && \
    chown -R redroom:redroom /app /var/redroom

USER redroom

CMD ["python", "-m", "redroom.orchestration.main"]
