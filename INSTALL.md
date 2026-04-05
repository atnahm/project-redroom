# Installation and Development Guide

Complete setup instructions for installing and developing REDROOM locally.

## Prerequisites

- Python 3.10+
- pip or conda
- Git
- Docker (for containerized development)
- Optional: Visual Studio Code, Docker Desktop, kubectl

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/atnahm/redroom.git
cd redroom
```

### 2. Create Virtual Environment

**Option A: venv (recommended)**
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

**Option B: conda**
```bash
conda create -n redroom python=3.11
conda activate redroom
```

### 3. Install Dependencies

```bash
cd redroom
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import cv2, fastapi, sqlalchemy, numpy; print('✓ All dependencies installed')"
```

## Running Tests

### Integration Tests

```bash
python -m pytest test_integration.py -v
```

### Test Coverage

```bash
pip install pytest-cov
python -m pytest test_integration.py --cov=redroom --cov-report=html
```

## Docker Development

### Build Development Image

```bash
docker build -t redroom:dev .
```

### Run Local Services

```bash
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f api
```

### Stop Services

```bash
docker-compose down
docker-compose down -v  # Also remove volumes
```

## C++ Module Development

### Build C++ Extensions

```bash
cd redroom/forensics/cpp

# Linux/macOS
./build.sh

# Windows
build.bat
```

### C++ Dependencies

- CMake 3.20+
- OpenCV 4.0+
- C++17 compatible compiler:
  - Linux: g++ 7+
  - macOS: clang 10+
  - Windows: MSVC 2019+

### Install C++ Dependencies (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    libfftw3-dev \
    python3-dev
```

### Install C++ Dependencies (macOS)

```bash
brew install cmake opencv fftw
```

### Install C++ Dependencies (Windows)

See COMPILER_SETUP.md or install Visual Studio Build Tools.

## Code Style

### Python Code Style

REDROOM follows PEP 8 style guide.

```bash
# Install linters
pip install flake8 black isort

# Check style
flake8 redroom/

# Auto-format code
black redroom/
isort redroom/
```

### C++ Code Style

Use clang-format with provided configuration.

```bash
# Install clang-format
sudo apt-get install clang-format  # Ubuntu
brew install clang-format  # macOS

# Format C++ files
clang-format -i redroom/forensics/cpp/*.cpp
```

## Type Checking

```bash
# Install mypy
pip install mypy

# Check types
mypy redroom/
```

## Documentation

Build and preview documentation locally.

```bash
# Install doc tools
pip install sphinx sphinx-rtd-theme

# Build HTML docs
cd docs
make html

# Open in browser
open build/html/index.html
```

## Debugging

### Python Debugger

```python
# Add to your code
import pdb; pdb.set_trace()

# Or use Python 3.7+
breakpoint()
```

### Remote Debugging with VS Code

See `.vscode/launch.json` for debugging configuration.

### Docker Container Debugging

```bash
docker exec -it redroom-api /bin/bash
```

## Performance Profiling

### CPU Profiling

```bash
pip install py-spy

py-spy record -o profile.svg -- python redroom/orchestration/main.py
```

### Memory Profiling

```bash
pip install memory-profiler

python -m memory_profiler redroom/orchestration/main.py
```

## Kubernetes Development

### Local K3s Setup

```bash
# Install K3s
curl -sfL https://get.k3s.io | sh -

# Export kubeconfig
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Verify
kubectl cluster-info
```

### Deploy Locally

```bash
kubectl apply -f kubernetes/deployment.yaml

# Monitor
kubectl get pods -n redroom
kubectl logs -n redroom deployment/redroom-api
```

## Troubleshooting

### Virtual Environment Issues

```bash
# Deactivate
deactivate

# Remove
rm -rf venv

# Recreate
python -m venv venv
source venv/bin/activate
pip install -r redroom/requirements.txt
```

### Dependency Conflicts

```bash
# Update pip
pip install --upgrade pip

# Clean and reinstall
pip cache purge
pip install -r redroom/requirements.txt --no-cache-dir
```

### Docker Issues

```bash
# Remove dangling images
docker image prune -a

# Remove dangling volumes
docker volume prune

# Restart daemon
docker restart
```

### C++ Compilation Errors

See `redroom/forensics/cpp/BUILD_README.md` for detailed C++ build troubleshooting.

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature
```

### 2. Make Changes and Test

```bash
# Edit code
# Run tests
python -m pytest redroom/test_integration.py -v

# Check style
flake8 redroom/
black --check redroom/
```

### 3. Commit Changes

```bash
git add .
git commit -m "Add your feature description"
```

### 4. Push and Create PR

```bash
git push origin feature/your-feature
```

Visit GitHub and create a pull request with description.

### 5. Code Review

Respond to feedback and update your PR.

### 6. Merge

Once approved, maintainers will merge to main branch.

## Contributing

See CONTRIBUTING.md for detailed contribution guidelines.

## Getting Help

- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and discuss ideas
- Documentation: Check README.md and ARCHITECTURE.md
- Security: See SECURITY.md for reporting vulnerabilities

---

**Happy developing! Welcome to REDROOM.**
