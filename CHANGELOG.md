# Changelog

All notable changes to REDROOM are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-04-06

### Added
- Core forensic analysis pipeline (7-phase processing)
- rPPG pulse detection module with quality mode adaptation
- Oculometric eye consistency analyzer
- PRNU camera fingerprint extraction (C++)
- Bispectral frequency analysis for GAN/Diffusion detection
- Sovereign VLM reasoning with weight attestation
- Merkle tree immutable ledger with chain-of-custody
- FastAPI REST backend with evidence analysis endpoints
- Docker Compose deployment with vLLM service
- Kubernetes manifests for K3s production deployment
- Comprehensive integration test suite
- Multi-analyst concurrent access with audit trails
- Cryptographic evidence hashing (SHA-3-512)
- Full API documentation
- GitHub Actions CI/CD workflows

### Features
- Parallel forensic analysis (60-120 second per-evidence analysis time)
- Air-gapped operation (no external API calls required)
- Configuration-driven analysis parameters
- Multiple quality modes (CLINICAL, SURVEILLANCE, EXTREME)
- Tear-line classified/unclassified reporting
- 7-year evidence retention capability
- GPU acceleration support (NVIDIA CUDA)

### Architecture
- microservices-ready with Docker and Kubernetes
- Scalable to 100+ concurrent analysts
- Persistent ledger storage with SQLite
- Local vision language model (Qwen/Qwen2-VL-7B)
- Modular C++ optimization for performance-critical modules

## [Unreleased]

### Planned
- Dashboard intelligence visualization
- Advanced PDF report generation with classification handling
- Enhanced GPU multi-card support
- Machine learning model optimization
- Additional frequency domain analysis
- Extended forensic signal types

---

## Version Numbering

MAJOR.MINOR.PATCH format:
- MAJOR: Significant architectural changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes and optimizations

---

## Upgrade Notes

### 1.0.0 Release
First stable release. Production-ready for deployment.

**Hardware Requirements:**
- Minimum: 16GB RAM, 8-core CPU
- Recommended: 32GB RAM, 16-core CPU, NVIDIA GPU

**Dependencies:**
- Python 3.10+
- OpenCV 4.0+
- Docker 20.10+ (for containerized deployment)
- Kubernetes 1.24+ (for K3s deployment)

**Breaking Changes:**
None - initial release.

## Contributing

See CONTRIBUTING.md for guidelines on reporting issues and submitting improvements.

## License

REDROOM is licensed under the MIT License. See LICENSE for details.
