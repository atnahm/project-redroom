# REDROOM Deepfake Detection System - Docker Image
# Build: docker build -t redroom:latest .
# Run: docker-compose up -d

FROM python:3.11-slim

LABEL maintainer="redroom-dev"
LABEL version="1.0"
LABEL description="Video forensic analysis system"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl wget git build-essential cmake \
    libopencv-dev python3-opencv \
    libfftw3-dev libfftw3-3 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY redroom/requirements.txt /app/redroom/requirements.txt

RUN pip install --no-cache-dir -r /app/redroom/requirements.txt

# Copy source code
COPY redroom /app/redroom
COPY LICENSE /app/
COPY README.md /app/

# Build C++ Extensions
RUN cd /app/redroom/forensics/cpp && \
    rm -rf build && mkdir build && cd build && \
    cmake .. && make && \
    cp lib*.so ..

RUN mkdir -p /app/data \
    && mkdir -p /app/logs \
    && mkdir -p /var/redroom/ledger

RUN chmod -R 755 /app/redroom

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LEDGER_DB_PATH=/var/redroom/ledger/redroom_ledger.db
ENV VLLM_ENDPOINT=http://vllm:8000
ENV PYTHONPATH=/app

WORKDIR /app

EXPOSE 8002


RUN useradd -m -u 1000 redroom &&     chown -R redroom:redroom /app /var/redroom

USER redroom


CMD ["python", "-m", "redroom.orchestration.main"]
