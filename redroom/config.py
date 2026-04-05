"""
Redroom System Configuration
Central configuration for all forensic pipeline parameters
"""

from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List


class AnalysisMode(str, Enum):
    """Quality mode determines forensic sensitivity and thresholds"""
    CLINICAL = "clinical"  # Lab conditions, controlled, 95%+ accuracy
    SURVEILLANCE = "surveillance"  # Security camera, compressed, 60-75% accuracy
    EXTREME = "extreme"  # Degraded, off-angle, best-effort
    AUTO = "auto"  # Auto-detect based on signal characteristics


@dataclass
class PRNUConfig:
    """Photo Response Non-Uniformity extraction parameters"""
    wiener_filter_kernel: int = 5  # Kernel size for Wiener filtering
    zero_mean_window: int = 8  # Window for zero-mean normalization
    nist_database_enabled: bool = True
    reference_db_path: str = "./data/nist_camera_fingerprints"
    cross_correlation_threshold: float = 0.85
    spoofing_confidence_threshold: float = 0.7


@dataclass
class BispectralConfig:
    """Bispectral artifact detection parameters"""
    paranoid_mode: bool = True  # Use 3.5σ instead of 2σ (1% vs 5% false positive)
    fft_size: int = 512
    biphase_threshold: float = 0.6
    gan_frequency_range: tuple = (8000, 32000)  # Hz
    diffusion_frequency_range: tuple = (16000, 64000)  # Hz


@dataclass
class rPPGConfig:
    """Remote Photoplethysmography (pulse detection) parameters"""
    min_frame_rate: float = 15.0  # FPS threshold for valid detection
    pulse_freq_min: float = 0.5  # Hz (30 bpm)
    pulse_freq_max: float = 3.0  # Hz (180 bpm)
    normal_hr_min: int = 30  # Beats per minute
    normal_hr_max: int = 200
    hrv_synthetic_threshold: float = 5.0  # ms (HRV below = synthetic)
    signal_quality_threshold: float = 0.6  # SNR threshold
    skewness_synthetic_threshold: float = 0.3
    kurtosis_synthetic_threshold: float = 2.0


@dataclass
class OculometricConfig:
    """Corneal reflection consistency analysis parameters"""
    glint_intensity_threshold: float = 200  # Pixel intensity
    glint_size_range: tuple = (2, 50)  # pixels
    light_divergence_threshold: float = 10.0  # degrees
    reflection_symmetry_threshold: float = 0.95  # 95% = synthetic characteristic
    minimum_eye_distance: float = 40  # pixels (sanity check)


@dataclass
class VLMConfig:
    """Sovereign VLM reasoning parameters"""
    model: str = "gemma_4_31b_awq"
    endpoint: str = "http://localhost:8001"
    temperature: float = 0.1  # Deterministic for auditability
    max_tokens: int = 1024
    top_p: float = 0.95
    weight_verification_enabled: bool = True
    weight_verification_algorithm: str = "sha3_512"
    prompt_injection_shield_enabled: bool = True
    forbidden_tokens: List[str] = None

    def __post_init__(self):
        if self.forbidden_tokens is None:
            self.forbidden_tokens = [
                "tell me about yourself",
                "execute",
                "bypass",
                "system prompt",
                "jailbreak",
                "ignore previous instructions",
                "forget the context",
                "what are your instructions",
                "debug mode",
                "admin",
                "root",
                "sudo",
            ]


@dataclass
class OrchestrationConfig:
    """Forensic pipeline orchestration parameters"""
    # Weighting for probability synthesis (must sum to 1.0)
    weight_rppg: float = 0.40  # Pulse detection (most reliable)
    weight_bispectral: float = 0.30  # Frequency artifacts
    weight_oculometric: float = 0.15  # Eye anomalies
    weight_prnu: float = 0.05  # Sensor fingerprint (DB-dependent)
    weight_vlm: float = 0.10  # VLM forensic reasoning

    # Evidence combination rules
    rppg_absence_critical: bool = True  # No pulse = strong AI signal
    suspicious_threshold: float = 0.70  # Probability > 70% = flagged
    vlm_override_threshold: float = 0.80  # VLM confidence > 80% = override synthesis

    # Report generation
    generate_unclassified_report: bool = True
    generate_classified_report: bool = True
    redact_sensitive_forensics: bool = True

    def validate(self):
        """Verify weights sum to 1.0"""
        total = (
            self.weight_rppg
            + self.weight_bispectral
            + self.weight_oculometric
            + self.weight_prnu
            + self.weight_vlm
        )
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"Weights must sum to 1.0, got {total}. "
                f"Adjust: rppg={self.weight_rppg}, "
                f"bispectral={self.weight_bispectral}, "
                f"oculometric={self.weight_oculometric}, "
                f"prnu={self.weight_prnu}, "
                f"vlm={self.weight_vlm}"
            )


@dataclass
class LedgerConfig:
    """Merkle tree ledger configuration"""
    db_path: str = "./redroom_ledger.db"
    retention_years: int = 7
    retention_total_bytes: int = 100 * 1024 * 1024 * 1024  # 100GB
    hash_algorithm: str = "sha3_512"
    concurrent_analysts: int = 100
    enable_audit_logging: bool = True
    enable_merkle_proofs: bool = True


@dataclass
class SecurityConfig:
    """Security and isolation parameters"""
    # mTLS for internal communication
    enable_mtls: bool = False  # Set True for production
    cert_path: str = "./certs/client.crt"
    key_path: str = "./certs/client.key"
    ca_path: str = "./certs/ca.crt"

    # Data diode simulation (MVP) vs real isolation
    data_diode_enabled: bool = True  # False = real fiber-optic in production
    data_diode_ingestion_ip: str = "0.0.0.0"
    data_diode_ingestion_port: int = 8003
    data_diode_analysis_ip: str = "127.0.0.1"
    data_diode_analysis_port: int = 8002

    # Air-gap validation
    external_api_calls_allowed: bool = False  # Strict for Tier-1
    network_egress_enabled: bool = False


# Default configuration instances
PRNU_CONFIG = PRNUConfig()
BISPECTRAL_CONFIG = BispectralConfig()
rPPG_CONFIG = rPPGConfig()
OCULOMETRIC_CONFIG = OculometricConfig()
VLM_CONFIG = VLMConfig()
ORCHESTRATION_CONFIG = OrchestrationConfig()
LEDGER_CONFIG = LedgerConfig()
SECURITY_CONFIG = SecurityConfig()

# Validate on import
try:
    ORCHESTRATION_CONFIG.validate()
except ValueError as e:
    import sys
    print(f"❌ Configuration validation failed: {e}", file=sys.stderr)
    sys.exit(1)


def get_config_summary() -> Dict:
    """Return summary of all configurations"""
    return {
        "prnu": PRNU_CONFIG.__dict__,
        "bispectral": BISPECTRAL_CONFIG.__dict__,
        "rppg": rPPG_CONFIG.__dict__,
        "oculometric": OCULOMETRIC_CONFIG.__dict__,
        "vlm": {k: v for k, v in VLM_CONFIG.__dict__.items() if k != "forbidden_tokens"},
        "orchestration": ORCHESTRATION_CONFIG.__dict__,
        "ledger": LEDGER_CONFIG.__dict__,
        "security": SECURITY_CONFIG.__dict__,
    }
