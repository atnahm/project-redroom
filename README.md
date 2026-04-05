# REDROOM - Open Source Deepfake Detection System

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Kubernetes Ready](https://img.shields.io/badge/Kubernetes-Ready-326CE5.svg)](https://kubernetes.io/)
[![GitHub Stars](https://img.shields.io/github/stars/atnahm/redroom?style=flat-square)](https://github.com/atnahm/redroom)
[![GitHub Issues](https://img.shields.io/github/issues/atnahm/redroom?style=flat-square)](https://github.com/atnahm/redroom/issues)
[![Version 1.0](https://img.shields.io/badge/Version-1.0-blue.svg)](https://github.com/atnahm/redroom/releases)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baadc.svg)](CODE_OF_CONDUCT.md)

Professional-grade video forensic analysis system for detecting AI-generated deepfakes through multi-modal forensic analysis, cryptographic chain-of-custody, and local sovereign reasoning.

**Open Source | Production Ready | Actively Maintained**

## System Overview

REDROOM implements a zero-trust forensic pipeline combining:

- Hard-mathematical forensic signals (PRNU sensor fingerprinting, bispectral frequency analysis)
- Biological liveness detection (cardiac pulse analysis, eye consistency validation)
- Local weight-verified vision language model analysis
- Immutable Merkle tree evidence ledger with cryptographic proofs
- Multi-analyst concurrent access with full audit trails

## Core Architecture

### Analysis Pipeline (7 Phases)

1. **Ingestion** - SHA-3-512 cryptographic hashing of evidence
2. **Frame Extraction** - Standardized preprocessing and quality validation
3. **Hard Forensics** (Parallel):
   - PRNU extraction via Wiener filtering (camera fingerprinting)
   - Bispectral FFT analysis (frequency artifact detection)
   - rPPG pulse detection (cardiac biological liveness)
   - Oculometric consistency (corneal reflection analysis)
4. **VLM Reasoning** - Local sovereign reasoning (Gemma 4, weight-attested)
5. **Synthesis** - Weighted probability combining all signals
6. **Ledger Commitment** - Immutable Merkle tree append
7. **Reporting** - Classified/unclassified tear-line reports

### Probability Model

Final AI-generation probability combines:
- rPPG Pulse (40% weight)
- Bispectral Analysis (30% weight)
- Oculometric Consistency (15% weight)
- PRNU Fingerprinting (5% weight)
- VLM Reasoning (10% weight)

## Project Structure

```
redroom/
├── forensics/
│   ├── python/                    # Python forensic modules
│   │   ├── rppg_detector.py
│   │   ├── oculometric_analyzer.py
│   │   └── forensic_orchestrator.py
│   └── cpp/                       # C++ optimization modules
│       ├── prnu_extractor.cpp
│       ├── bispectral_analyzer.cpp
│       └── CMakeLists.txt
├── ledger/
│   └── merkle_ledger.py           # Chain-of-custody ledger
├── vlm/
│   └── sovereign_vlm.py           # Local weight-attested VLM
├── api/
│   └── main.py                    # FastAPI backend
├── config.py                      # Centralized configuration
├── test_integration.py            # Integration test suite
└── docker-compose.yml             # Multi-service deployment

kubernetes/
├── deployment.yaml                # K3s deployment manifests
├── service.yaml
├── configmap.yaml
└── README.md
```

## Deployment

### Docker

```bash
cd redroom
docker-compose up -d
```

Services launched:
- API Server (Port 8002) - FastAPI evidence analysis
- vLLM Service (Port 8001) - Gemma 4 31B AWQ quantization
- Ledger Service - SQLite chain-of-custody

### Kubernetes (K3s)

```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/configmap.yaml

# Verify deployment
kubectl get pods -n redroom
kubectl get svc -n redroom
```

## API Reference

### Evidence Analysis

```http
POST /redroom/analyze
Content-Type: multipart/form-data

{
  "evidence": <video_file>,
  "quality_mode": "CLINICAL|SURVEILLANCE|EXTREME",
  "request_pdf": true
}
```

Response:
```json
{
  "request_id": "uuid",
  "status": "COMPLETE",
  "analysis": {
    "ai_probability": 0.95,
    "confidence": 0.98,
    "signals": {
      "rppg_score": 0.92,
      "bispectral_score": 0.98,
      "oculometric_score": 0.85,
      "prnu_score": 0.62,
      "vlm_score": 0.89
    }
  },
  "ledger_hash": "sha3_512_hash",
  "report_url": "/redroom/report/{request_id}.pdf"
}
```

### Ledger Query

```http
GET /redroom/ledger/query?start_date=2024-01-01&end_date=2024-12-31
```

Response:
```json
{
  "results": [
    {
      "timestamp": "2024-06-15T14:23:45Z",
      "evidence_hash": "sha3_512_hash",
      "ai_probability": 0.95,
      "analyst": "agent_123",
      "classification": "UNCLASSIFIED"
    }
  ],
  "total_records": 1524,
  "merkle_root": "hash"
}
```

### System Status

```http
GET /redroom/status
```

Response:
```json
{
  "version": "1.0",
  "modules": {
    "rppg": "operational",
    "bispectral": "operational",
    "oculometric": "operational",
    "prnu": "available",
    "vlm": "operational",
    "ledger": "operational"
  },
  "uptime_seconds": 86400,
  "processed_analyses": 1524
}
```

## Installation

### Requirements

- Python 3.10+
- OpenCV 4.0+
- Docker & Docker Compose (for containerized deployment)
- Kubernetes 1.24+ (for K3s deployment)
- Visual Studio Build Tools or GCC (for C++ compilation)
- 16GB RAM minimum (32GB recommended)
- SSD storage for ledger

### Local Setup

1. Install dependencies:
```bash
pip install -r redroom/requirements.txt
```

2. Build C++ modules (optional optimization):
```bash
cd redroom/forensics/cpp
./build.sh          # Linux/macOS
build.bat           # Windows
```

3. Run tests:
```bash
python -m pytest redroom/test_integration.py
```

## Configuration

See `redroom/config.py` for parameter tuning:

- `RPPG_QUALITY_MODES` - Pulse detection sensitivity
- `BISPECTRAL_PARANOID_MODE` - Frequency artifact threshold
- `LEDGER_RETENTION_DAYS` - Chain-of-custody archive duration
- `VLM_MODEL_PATH` - Local model loading path
- `ANALYSIS_TIMEOUT_SECONDS` - Per-evidence timeout limit

Default weights balance sensitivity vs false positive rate for government use.

## Security Model

### Air-Gapped Analysis

- No external API calls (local VLM only)
- One-way data diode option for sensitive environments
- SHA-3-512 cryptographic evidence tracking
- SQLite ledger stores only hashes (no raw evidence)

### Audit Trail

- Per-analyst request logging
- Merkle tree proofs of evidence integrity
- 7-year evidence retention (configurable)
- Multi-factor authentication ready (agent identifiers)

## Performance

Typical analysis times on standard hardware:

| Module | Single CPU | GPU (NVIDIA) |
|--------|-----------|--------------|
| rPPG Detection | 2-5 sec | 1-2 sec |
| Bispectral Analysis | 3-8 sec | 1-3 sec |
| Oculometric | 4-10 sec | 2-4 sec |
| PRNU Extraction | 5-15 sec | 3-6 sec |
| VLM Reasoning | 30-60 sec | 10-20 sec |
| **Total Pipeline** | 60-120 sec | 20-45 sec |

Parallel execution reduces wall-clock time to 60-120 seconds single CPU, 20-45 seconds with GPU.

## Hardware Requirements

### Minimum Configuration
- CPU: 8-core
- RAM: 16GB
- Storage: 500GB SSD
- GPU: Optional (NVIDIA RTX 3060 or equivalent)

### Recommended Configuration
- CPU: 16-core Intel Xeon or AMD EPYC
- RAM: 32GB DDR5
- Storage: 2TB NVMe SSD (RAID 1)
- GPU: 2x NVIDIA A100 or equivalent
- Network: 10Gbps connection to ledger servers

## Development

### Project Structure

All sources and build artifacts are Git-ready:

```
REDROOM/
├── .gitignore                     # Excludes credentials, build artifacts
├── Dockerfile                     # Container image
├── docker-compose.yml             # Multi-service orchestration
├── kubernetes/                    # K3s deployment templates
├── redroom/                       # Application code
│   ├── forensics/                 # Analysis modules
│   ├── ledger/                    # Evidence chain-of-custody
│   ├── vlm/                       # Sovereign reasoning
│   ├── api/                       # REST API
│   ├── requirements.txt
│   └── config.py
├── LICENSE
└── README.md
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/your-org/redroom.git
cd redroom

# Build Docker images
docker build -t redroom-api:latest -f Dockerfile .
docker build -t redroom-vllm:latest -f Dockerfile.vllm .

# Deploy
docker-compose up -d
```

### Container Registry

Push to your organization's registry:

```bash
docker tag redroom-api:latest your-registry.azurecr.io/redroom-api:v1.0
docker push your-registry.azurecr.io/redroom-api:v1.0
```

## Kubernetes Deployment

Deploy to production K3s cluster:

```bash
kubectl create namespace redroom
kubectl apply -f kubernetes/ -n redroom

# Scale analysis workers
kubectl scale deployment redroom-api --replicas=5 -n redroom

# Monitor
kubectl logs -n redroom deployment/redroom-api -f
kubectl top nodes
kubectl top pods -n redroom
```

## Troubleshooting

### Module Import Errors

If C++ modules fail to load, system automatically falls back to Python-only analysis:
```python
from redroom.ctypes_bridge import PRNUExtractorWrapper
# If .dll/.so not found, wrapper returns Python-compatible interface
```

### Performance Tuning

Adjust these for your hardware:
- `redroom/config.py` - ANALYSIS_TIMEOUT_SECONDS
- `docker-compose.yml` - CPU/memory limits
- `kubernetes/deployment.yaml` - Resource requests/limits

### Ledger Queries

Large ledger queries (>100k records) may require pagination:
```http
GET /redroom/ledger/query?limit=1000&offset=0
```

## Contributing

We welcome contributions of all kinds! Before getting started:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
2. Review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
3. Check [INSTALL.md](INSTALL.md) for development setup
4. Look for issues labeled "good first issue" or "help wanted"

### Ways to Contribute

- Report bugs and request features via [GitHub Issues](https://github.com/atnahm/redroom/issues)
- Submit code improvements via [Pull Requests](https://github.com/atnahm/redroom/pulls)
- Improve documentation
- Submit security vulnerabilities to [SECURITY.md](SECURITY.md)
- Share your deployment experiences
- Help others with questions in [Discussions](https://github.com/atnahm/redroom/discussions)

## Community

- **Issues**: Report bugs, suggest features - [GitHub Issues](https://github.com/atnahm/redroom/issues)
- **Discussions**: Ask questions, discuss ideas - [GitHub Discussions](https://github.com/atnahm/redroom/discussions)
- **Security**: Report vulnerabilities - [SECURITY.md](SECURITY.md)
- **Roadmap**: See what's planned - [ROADMAP.md](ROADMAP.md)
- **Contributors**: Thank you! - [CONTRIBUTORS.md](CONTRIBUTORS.md)

## Support

For issues, questions, or deployment help:
1. Check [INSTALL.md](INSTALL.md) for setup instructions
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment
3. Check configuration in `redroom/config.py`
4. Review logs: `docker logs redroom-api` or `kubectl logs`
5. Verify dependencies: `python -c "import cv2, fastapi, sqlalchemy"`
6. Open a GitHub Issue for help

## License

Refer to [LICENSE](LICENSE) file. REDROOM is released under the MIT License.

## Acknowledgments

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for recognition of everyone who makes REDROOM possible.

## Citation

If you use REDROOM in your research or production system, please cite:

```bibtex
@software{redroom2026,
  title={REDROOM: Open Source Deepfake Detection System},
  author={atnahm and contributors},
  url={https://github.com/atnahm/redroom},
  year={2026},
  version={1.0}
}
```

## Version

Current Release: 1.0
Build Date: April 2026
Status: Production Ready
License: MIT

---

**REDROOM: Collaborative deepfake detection for a more trustworthy world.**
