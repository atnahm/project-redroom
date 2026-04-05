# Contributing to REDROOM

Guidelines for contributing to the REDROOM deepfake detection system.

## Code of Conduct

Be respectful and professional in all interactions. Discriminatory behavior will not be tolerated.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/redroom.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Commit with clear messages: `git commit -m "Add feature description"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

## Development Setup

```bash
# Install dependencies
pip install -r redroom/requirements.txt

# Run tests
python -m pytest redroom/test_integration.py

# Build C++ modules (optional)
cd redroom/forensics/cpp
./build.sh  # Linux/macOS
build.bat   # Windows
```

## Code Style

- Python: PEP 8 (max 100 characters per line)
- Commits: Conventional Commits format
- Docstrings: Google format for all public functions

Example:
```python
def analyze_evidence(video_path: str, quality_mode: str = "CLINICAL") -> AnalysisResult:
    """
    Analyze video evidence for deepfake indicators.

    Args:
        video_path: Path to video file
        quality_mode: Analysis sensitivity (CLINICAL, SURVEILLANCE, EXTREME)

    Returns:
        AnalysisResult with probability and detailed scores

    Raises:
        FileNotFoundError: If video file not found
        ValueError: If quality_mode is invalid
    """
```

## Testing

All changes require tests:

```bash
# Run specific test
python -m pytest redroom/test_integration.py::test_rppg_detector -v

# Run with coverage
python -m pytest redroom/test_integration.py --cov=redroom
```

## Pull Request Process

1. Update README.md if needed
2. Add tests for new features
3. Ensure all tests pass: `python -m pytest redroom/`
4. Fill out the PR template completely
5. Request review from maintainers
6. Address feedback from reviewers

## Reporting Issues

Use GitHub Issues with these labels:
- `bug`: Something is broken
- `enhancement`: New feature or improvement
- `documentation`: Docs need updating
- `question`: Usage question
- `performance`: Speed/efficiency issue

Include:
- Clear description of the issue
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- System info (Python version, OS, hardware)
- Logs or error messages

## Documentation

Update docs when:
- Adding new functions or modules
- Changing API behavior
- Adding configuration options
- Updating deployment procedures

Documentation should be:
- Clear and concise
- Include examples where appropriate
- Updated in README.md, DEPLOYMENT.md, or docstrings

## Release Process

Maintainers handle releases using semantic versioning:

1. Update version in code
2. Update CHANGELOG.md
3. Create annotated Git tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub Release with notes

## License

All contributions are licensed under the MIT License per the LICENSE file.

## Questions?

Open a GitHub Discussion or Issue. We're here to help.

Thank you for contributing to REDROOM!
