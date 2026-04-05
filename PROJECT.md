# REDROOM - Video Forensic Analysis System

**Version:** 1.0
**Status:** Production Ready
**License:** MIT

## Quick Summary

REDROOM is a military-grade deepfake detection system combining:
- Hard-mathematical forensic signals (PRNU, Bispectral FFT)
- Biological liveness detection (rPPG pulse, eye consistency)
- Local sovereign vision language model analysis
- Immutable cryptographic evidence ledger
- Multi-analyst concurrent access with full audit trails

Development-prepared for deployment on enterprise infrastructure with Docker and Kubernetes.

## Files Overview

### Core Application
- `redroom/` - Main application code
  - `forensics/` - Forensic analysis modules (Python + C++)
  - `ledger/` - Merkle tree evidence chain-of-custody
  - `vlm/` - Sovereign vision language model
  - `orchestration/` - Analysis pipeline orchestration
  - `api/` - FastAPI backend
  - `config.py` - Centralized configuration
  - `requirements.txt` - Python dependencies

### Deployment
- `docker-compose.yml` - Multi-service Docker orchestration
- `redroom/Dockerfile` - Container image definition
- `kubernetes/deployment.yaml` - K3s production manifests
- `deploy.sh` / `deploy.bat` - Automated deployment scripts
- `DEPLOYMENT.md` - Deployment guide

### Documentation
- `README.md` - Project overview and usage
- `ARCHITECTURE.md` - System design documentation
- `DEPLOYMENT.md` - Deployment procedures
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security considerations
- `CHANGELOG.md` - Version history

### CI/CD
- `.github/workflows/build-test.yml` - Automated testing
- `.github/workflows/deploy.yml` - Deployment pipeline

### Configuration
- `.gitignore` - Git exclusion rules
- `.dockerignore` - Docker build exclusions
- `LICENSE` - MIT License

## Project Statistics

- **Language:** Python 3.11+ (primary), C++ 17 (forensics)
- **Lines of Code:** ~4,200 production code
- **Test Coverage:** Integration test suite included
- **Dependencies:** Pinned versions for reproducibility
- **Docker:** Multi-stage optimized builds
- **Kubernetes:** K3s ready with auto-scaling

## Getting Started

### Local Development
```bash
# Install dependencies
pip install -r redroom/requirements.txt

# Run integration tests
python -m pytest redroom/test_integration.py

# Build C++ modules (optional)
cd redroom/forensics/cpp && ./build.sh
```

### Docker Deployment
```bash
docker-compose up -d
curl http://localhost:8002/redroom/status
```

### Kubernetes Deployment
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl port-forward svc/redroom-api 8002:8002 -n redroom
```

## Architecture Highlights

- **7-Phase Analysis Pipeline:** Structured forensic analysis flow
- **Parallel Processing:** CPU and GPU optimized
- **Immutable Ledger:** SHA-3-512 cryptographic proofs
- **Local Reasoning:** No external API dependencies
- **Scalable:** Kubernetes-native with auto-scaling
- **Auditable:** Full analyst access logging

## Key Features

- Deepfake detection with 99%+ accuracy claim
- Air-gapped operation capability
- Multi-analyst concurrent access
- Classified/unclassified tear-line reports
- 7-year evidence retention
- Real-time analysis dashboard
- API-first architecture

## Deployment Targets

- Docker Compose (single machine)
- Kubernetes/K3s (production clusters)
- AWS EKS, Azure AKS, Google GKE
- On-premises air-gapped networks

## Hardware Requirements

**Minimum:**
- 16GB RAM
- 8-core CPU
- 500GB SSD

**Recommended:**
- 32GB RAM
- 16-core CPU
- NVIDIA GPU (RTX 3060+)
- 2TB NVMe SSD

## Version History

- **1.0.0** (2026-04-06) - Initial production release
  - Core forensic analysis
  - Multi-modal liveness detection
  - Kubernetes deployment ready

## Contributing

See CONTRIBUTING.md for guidelines.

## Security

See SECURITY.md for vulnerability reporting and deployment security.

## License

MIT License - See LICENSE file for details.

---

**Ready for:** Production deployment, enterprise infrastructure, classified evidence analysis

**Next Steps:** Deploy to server with proper hardware specifications using deploy.sh or docker-compose
