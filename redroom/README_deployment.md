# Deployment Guide

This repository contains the Redroom backend, which acts as the deepfake forensic orchestration layer.

## AWS / GCP Deployment
We provide a comprehensive Dockerized environment to run this software on an AWS EC2 instance or GCP Compute instance.

1. Provision an instance (e.g., Ubuntu 22.04) with at least 8GB of RAM. If you intend to use the local `vLLM` features, you must use a GPU instance (e.g. AWS `g4dn.xlarge` or `p3.2xlarge`) and install Nvidia Container Toolkit.
2. Clone this repository.
3. Install Docker and Docker Compose.
4. Run `docker-compose up -d --build`.
5. The API will be available on `http://<your-instance-ip>:8002`.

If you only want to spin up the API (bypassing the local vLLM dependency for testing), you can run:
`docker build -t redroom-api -f Dockerfile .`
`docker run -p 8002:8002 redroom-api`
