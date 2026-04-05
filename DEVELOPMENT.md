# Development Standards and Guidelines

Quality assurance standards for REDROOM codebase and contributions.

## Code Quality Requirements

All contributions must meet these standards to be accepted.

### Python Code

#### Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Maximum line length: 100 characters
- Use meaningful variable names
- Avoid magic numbers (use constants instead)
- Comment complex logic clearly

#### Tools
```bash
# Format code
black redroom/ --line-length=100

# Check style
flake8 redroom/ --max-line-length=100

# Sort imports
isort redroom/

# Type checking
mypy redroom/
```

#### Example
```python
"""Module docstring explaining purpose."""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

def analyze_evidence(
    video_path: str,
    quality_mode: str = "CLINICAL",
    timeout_seconds: int = 120
) -> Optional[AnalysisResult]:
    """
    Analyze video evidence for deepfake indicators.

    Args:
        video_path: Path to video file
        quality_mode: Analysis sensitivity level
        timeout_seconds: Maximum analysis duration

    Returns:
        AnalysisResult with probability and scores, or None if failed

    Raises:
        FileNotFoundError: If video file not found
        ValueError: If quality_mode is invalid
    """
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    logger.info(f"Starting analysis of {video_path}")
    # Implementation here
```

### C++ Code

#### Style Guide
- Follow [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- Use clang-format for automatic formatting
- Meaningful variable names
- Comments for non-obvious logic
- RAII principles

#### Tools
```bash
# Format code
clang-format -i redroom/forensics/cpp/*.cpp

# Check with clang-tidy
clang-tidy redroom/forensics/cpp/*.cpp
```

#### Example
```cpp
#include <opencv2/opencv.hpp>
#include <vector>

namespace redroom {
namespace forensics {

class PRNUExtractor {
 public:
  /**
   * Extract PRNU fingerprint from image.
   *
   * @param image Input grayscale image
   * @return PRNU noise residual
   */
  cv::Mat ExtractFromImage(const cv::Mat& image);

 private:
  static constexpr int kWienerKernelSize = 5;

  cv::Mat ApplyWienerFilter(const cv::Mat& image);
};

}  // namespace forensics
}  // namespace redroom
```

## Testing Requirements

### Python Tests
- All new features must have tests
- Minimum 80% code coverage
- Tests should be in `test_` prefixed files
- Use pytest framework

```bash
# Run tests
python -m pytest redroom/ -v

# Check coverage
python -m pytest redroom/ --cov=redroom --cov-report=html
```

### Test Example
```python
import pytest
from redroom.forensics.python.rppg_detector import rPPGDetector

def test_rppg_detector_initialization():
    """Test rPPG detector initializes correctly."""
    detector = rPPGDetector()
    assert detector is not None

def test_rppg_detector_quality_modes():
    """Test all quality modes are valid."""
    detector = rPPGDetector()
    for mode in ["CLINICAL", "SURVEILLANCE", "EXTREME"]:
        assert mode.name in ["CLINICAL", "SURVEILLANCE", "EXTREME"]

def test_rppg_detector_invalid_input():
    """Test detector handles invalid input."""
    detector = rPPGDetector()
    with pytest.raises(ValueError):
        detector.detect(None)
```

## Documentation Requirements

### Docstrings
All public functions and classes must have docstrings.

**Python:**
```python
def function_name(arg1: str, arg2: int = 10) -> bool:
    """
    Brief description of what function does.

    Longer explanation if needed. Can span multiple lines.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2, defaults to 10

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If arg1 is empty
        TypeError: If arg2 is not an integer

    Example:
        >>> result = function_name("input", 20)
        >>> print(result)
        True
    """
```

**C++:**
```cpp
/**
 * Brief description of function.
 *
 * Longer description if needed. Multiple lines okay.
 *
 * @param arg1 Description of arg1
 * @param arg2 Description of arg2
 * @return Description of return value
 * @throws std::invalid_argument if arg1 is empty
 */
void FunctionName(const std::string& arg1, int arg2);
```

### Comments
- Explain *why*, not *what*
- Avoid obvious comments
- Keep comments updated with code

```python
# Bad comment
x = y + 1  # Add 1 to y

# Good comment
frame_index = current_frame + 1  # Advance to next frame for analysis
```

## Version Control Practices

### Commit Messages
```
[TYPE] Brief description (50 chars max)

Longer explanation of changes (72 chars per line).
Include why the change was made, not just what.

Fixes #123
Related to #456
```

**Types:** `[FEATURE]`, `[BUG]`, `[DOCS]`, `[REFACTOR]`, `[PERF]`, `[TEST]`,`[CI]`

### Branch Naming
```
feature/short-description          # New features
bugfix/short-description           # Bug fixes
docs/short-description             # Documentation
refactor/short-description         # Refactoring
```

### Pull Requests
- One feature per PR
- Reference related issues
- Link to documentation
-Provide test results
- Include screenshots if UI changes

## Security Standards

### Code Security
- No hardcoded credentials (use environment variables)
- Input validation on all external data
- Escape output for XSS prevention
- SQL injection prevention (use parameterized queries)
- No secrets in commit messages

### Dependencies
- Pin dependency versions
- Regular security updates
- Dependabot enabled
- Review dependency licenses

### Secrets Management
```python
# Bad - DO NOT DO THIS
api_key = "sk-12345abcdef"

# Good
import os
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
```

## Performance Standards

### Python Performance
- Profile before optimizing: `py-spy`, `memory-profiler`
- Use list comprehensions over loops
- Cache expensive operations
- Avoid deep nesting
- Use generators for large datasets

### C++ Performance
- Minimize memory allocations
- Avoid unnecessary copies
- Use const references where appropriate
- Profile with `perf`, `valgrind`
- Consider SIMD operations for signal processing

### Benchmarking
```python
import timeit

# Measure execution time
time_taken = timeit.timeit(my_function, number=1000)
print(f"Average: {time_taken/1000:.6f} seconds")
```

## Review Checklist

Before submitting a pull request, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] Test coverage is >80%
- [ ] Docstrings are complete
- [ ] No hardcoded secrets
- [ ] Commit messages are clear
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact assessed
- [ ] Code reviews comments addressed

## Naming Conventions

### Python
```python
# Classes: PascalCase
class DeepfakeDetector:
    pass

# Functions/methods: snake_case
def analyze_evidence():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
ANALYSIS_TIMEOUT = 120

# Private: leading underscore
_internal_helper()
```

### C++
```cpp
// Classes: PascalCase
class PRNUExtractor {};

// Functions: PascalCase
void ExtractFingerprint();

// Constants: kPascalCase
const int kMaxFrames = 1000;

// Private: trailing underscore
int private_member_;
```

## Documentation Standards

### README
- Clear project description
- Quick start instructions
- Links to full documentation
- License information
- Contribution guidelines

### CHANGELOG
- Detailed release notes
- Breaking changes highlighted
- Contributors acknowledged
- Version and date specified

### API Documentation
- All endpoints documented
- Request/response examples
- Error codes explained
- Rate limits specified

## Maintenance

### Regular Tasks
- [ ] Monthly dependency updates
- [ ] Quarterly security audits
- [ ] Annual architecture review
- [ ] Semi-annual documentation audit
- [ ] Continuous CI/CD monitoring

### Release Process
1. Update CHANGELOG.md
2. Bump version in code
3. Create release tag
4. Build Docker images
5. Push to registries
6. Create GitHub release
7. Announce to community

## Getting Help

- **Style Questions**: Open a GitHub Discussion
- **Design Questions**: Open an Issue, tag as question
- **Security Issues**: See SECURITY.md
- **Code Review**: Comment on PR or request review
- **API Changes**: Discuss in Issue before implementation

---

**Remember: Quality code today prevents problems tomorrow.**
