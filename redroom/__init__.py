"""
Redroom package initialization
Tier-1 Deepfake Detection System
"""

__version__ = "1.0.0"
__author__ = "Redroom Security Team"
__description__ = "Air-gapped forensic deepfake detection for intelligence agencies"

import logging

# Configure package logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Package metadata
SYSTEM_NAME = "Redroom"
TIER = "Tier-1"
CLASSIFICATION = "RESTRICTED"

# Export key modules
from redroom.config import (
    AnalysisMode,
    PRNU_CONFIG,
    BISPECTRAL_CONFIG,
    rPPG_CONFIG,
    OCULOMETRIC_CONFIG,
    VLM_CONFIG,
    ORCHESTRATION_CONFIG,
    LEDGER_CONFIG,
    SECURITY_CONFIG,
)

__all__ = [
    "SYSTEM_NAME",
    "TIER",
    "CLASSIFICATION",
    "__version__",
    "AnalysisMode",
    "PRNU_CONFIG",
    "BISPECTRAL_CONFIG",
    "rPPG_CONFIG",
    "OCULOMETRIC_CONFIG",
    "VLM_CONFIG",
    "ORCHESTRATION_CONFIG",
    "LEDGER_CONFIG",
    "SECURITY_CONFIG",
]
