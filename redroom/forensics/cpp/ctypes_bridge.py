"""
Ctypes bindings for C++ forensics modules

Bridges Python code with compiled C++ PRNU and Bispectral analyzers.
Handles library loading, type conversions, and error handling.
"""

import ctypes
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple
import logging
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


# ============================================================================
# Type Definitions (matching C++ enums)
# ============================================================================

class ArtifactType(IntEnum):
    """Artifact classification (must match C++ enum)"""
    UNKNOWN = 0
    GAN_RINGING = 1
    DIFFUSION_INCOHERENCE = 2
    COMPRESSION_ARTIFACT = 3


# ============================================================================
# C Structure Mappings
# ============================================================================

class FrequencySpike(ctypes.Structure):
    """Maps C++ FrequencySpike struct"""
    _fields_ = [
        ("frequency_bin_x", ctypes.c_int),
        ("frequency_bin_y", ctypes.c_int),
        ("magnitude", ctypes.c_float),
        ("frequency_hz", ctypes.c_float),
        ("artifact_type", ctypes.c_int),
    ]


class PRNUFingerprint(ctypes.Structure):
    """Maps C++ PRNUFingerprint struct"""
    _fields_ = [
        ("frame_count", ctypes.c_int),
        ("confidence", ctypes.c_float),
        ("estimated_model", ctypes.c_char_p),
        ("error_message", ctypes.c_char_p),
    ]


class PRNUMatch(ctypes.Structure):
    """Maps C++ PRNUMatch struct"""
    _fields_ = [
        ("is_match", ctypes.c_bool),
        ("match_score", ctypes.c_float),
        ("detected_camera", ctypes.c_char_p),
        ("spoofing_probability", ctypes.c_float),
    ]


class BispectralAnalysis(ctypes.Structure):
    """Maps C++ BispectralAnalysis struct"""
    _fields_ = [
        ("global_bicoherence_score", ctypes.c_float),
        ("ai_generation_probability", ctypes.c_float),
        ("primary_artifact", ctypes.c_int),
        ("confidence", ctypes.c_float),
        ("error_message", ctypes.c_char_p),
        ("temporal_consistency", ctypes.c_float),
    ]


# ============================================================================
# Library Loader
# ============================================================================

class CppForcensicsLoader:
    """Manages loading and caching of C++ forensics libraries"""

    _instance = None
    _prnu_lib = None
    _bispectral_lib = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_library_path(cls, library_name: str) -> Optional[Path]:
        """Find compiled library in expected locations"""
        # Expected build directories
        search_paths = [
            Path(__file__).parent / "cpp" / "build" / library_name,
            Path(__file__).parent / "cpp" / library_name,
            Path(__file__).parent / "cpp" / "build" / "lib" / library_name,
        ]

        # Windows DLL extensions
        import platform
        if platform.system() == "Windows":
            dll_names = [
                f"{library_name}.dll",
                f"lib{library_name}.dll",
                f"{library_name}_d.dll",
            ]
        else:
            # Linux/macOS shared object
            dll_names = [
                f"lib{library_name}.so",
                f"lib{library_name}.so.1",
                f"lib{library_name}.dylib",
            ]

        for base_path in search_paths:
            for dll_name in dll_names:
                full_path = base_path.parent / dll_name if base_path.is_dir() else base_path.parent / dll_name
                if full_path.exists():
                    logger.info(f"Found {library_name} at {full_path}")
                    return full_path

        logger.warning(f"Could not find {library_name} library. Searched: {search_paths}")
        return None

    @classmethod
    def load_prnu_library(cls) -> Optional[ctypes.CDLL]:
        """Load PRNU extractor library"""
        if cls._prnu_lib is not None:
            return cls._prnu_lib

        lib_path = cls.get_library_path("prnu_extractor")
        if lib_path is None:
            logger.error("PRNU library not found. Build with: cmake --build build")
            return None

        try:
            cls._prnu_lib = ctypes.CDLL(str(lib_path))
            logger.info("✅ PRNU extractor library loaded")
            return cls._prnu_lib
        except OSError as e:
            logger.error(f"Failed to load PRNU library: {e}")
            return None

    @classmethod
    def load_bispectral_library(cls) -> Optional[ctypes.CDLL]:
        """Load Bispectral analyzer library"""
        if cls._bispectral_lib is not None:
            return cls._bispectral_lib

        lib_path = cls.get_library_path("bispectral_analyzer")
        if lib_path is None:
            logger.error("Bispectral library not found. Build with: cmake --build build")
            return None

        try:
            cls._bispectral_lib = ctypes.CDLL(str(lib_path))
            logger.info("✅ Bispectral analyzer library loaded")
            return cls._bispectral_lib
        except OSError as e:
            logger.error(f"Failed to load Bispectral library: {e}")
            return None


# ============================================================================
# PRNU Extractor Python Wrapper
# ============================================================================

class PRNUExtractorWrapper:
    """Python wrapper for C++ PRNU extractor"""

    def __init__(self):
        self.lib = CppForcensicsLoader.load_prnu_library()
        if self.lib is None:
            logger.warning("PRNU C++ module not available - fallback to Python-only mode")
            self.enabled = False
        else:
            self.enabled = True
            self._setup_ctypes()

    def _setup_ctypes(self):
        """Configure ctypes function signatures"""
        if not self.enabled:
            return

        # PRNUExtractor constructor
        self.lib.PRNUExtractor_new.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.PRNUExtractor_new.restype = ctypes.c_void_p

        # extract_from_image
        self.lib.PRNUExtractor_extract_from_image.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
        ]
        self.lib.PRNUExtractor_extract_from_image.restype = PRNUFingerprint

        # extract_from_video
        self.lib.PRNUExtractor_extract_from_video.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        self.lib.PRNUExtractor_extract_from_video.restype = PRNUFingerprint

        # compare_to_reference (simplified - requires full ctypes mapping)
        # Skipped for MVP - stub in Python

    def extract_from_image(self, image_path: str) -> Dict:
        """Extract PRNU from single image"""
        if not self.enabled:
            return {
                "frame_count": 0,
                "confidence": 0.0,
                "estimated_model": "unknown",
                "error": "C++ PRNU module not available",
            }

        try:
            # Call C++ function
            extractor = self.lib.PRNUExtractor_new(5, 8)
            result = self.lib.PRNUExtractor_extract_from_image(
                extractor,
                image_path.encode("utf-8"),
            )

            return {
                "frame_count": result.frame_count,
                "confidence": result.confidence,
                "estimated_model": result.estimated_model.decode("utf-8") if result.estimated_model else "unknown",
                "error": result.error_message.decode("utf-8") if result.error_message else "",
            }
        except Exception as e:
            logger.error(f"PRNU extraction failed: {e}")
            return {
                "frame_count": 0,
                "confidence": 0.0,
                "estimated_model": "unknown",
                "error": str(e),
            }

    def extract_from_video(self, video_path: str, sample_frames: int = 30) -> Dict:
        """Extract PRNU from video"""
        if not self.enabled:
            return {
                "frame_count": 0,
                "confidence": 0.0,
                "estimated_model": "unknown",
                "error": "C++ PRNU module not available",
            }

        try:
            extractor = self.lib.PRNUExtractor_new(5, 8)
            result = self.lib.PRNUExtractor_extract_from_video(
                extractor,
                video_path.encode("utf-8"),
                sample_frames,
            )

            logger.info(f"✅ PRNU extracted from {result.frame_count} frames")

            return {
                "frame_count": result.frame_count,
                "confidence": result.confidence,
                "estimated_model": result.estimated_model.decode("utf-8") if result.estimated_model else "unknown",
                "error": result.error_message.decode("utf-8") if result.error_message else "",
            }
        except Exception as e:
            logger.error(f"PRNU video extraction failed: {e}")
            return {
                "frame_count": 0,
                "confidence": 0.0,
                "estimated_model": "unknown",
                "error": str(e),
            }


# ============================================================================
# Bispectral Analyzer Python Wrapper
# ============================================================================

class BispectralAnalyzerWrapper:
    """Python wrapper for C++ Bispectral analyzer"""

    def __init__(self, paranoid_mode: bool = True):
        self.lib = CppForcensicsLoader.load_bispectral_library()
        self.paranoid_mode = paranoid_mode

        if self.lib is None:
            logger.warning("Bispectral C++ module not available - fallback to Python-only mode")
            self.enabled = False
        else:
            self.enabled = True
            self._setup_ctypes()

    def _setup_ctypes(self):
        """Configure ctypes function signatures"""
        if not self.enabled:
            return

        # Constructor
        self.lib.BispectralAnalyzer_new.argtypes = [ctypes.c_bool]
        self.lib.BispectralAnalyzer_new.restype = ctypes.c_void_p

        # analyze
        self.lib.BispectralAnalyzer_analyze.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
        ]
        self.lib.BispectralAnalyzer_analyze.restype = BispectralAnalysis

        # set_paranoid_mode
        self.lib.BispectralAnalyzer_set_paranoid_mode.argtypes = [
            ctypes.c_void_p,
            ctypes.c_bool,
        ]
        self.lib.BispectralAnalyzer_set_paranoid_mode.restype = None

    def analyze(self, image_path: str) -> Dict:
        """Analyze single image for bispectral artifacts"""
        if not self.enabled:
            return {
                "bicoherence": 0.0,
                "ai_probability": 0.0,
                "artifact_type": "unknown",
                "confidence": 0.0,
                "error": "C++ Bispectral module not available",
            }

        try:
            analyzer = self.lib.BispectralAnalyzer_new(self.paranoid_mode)
            result = self.lib.BispectralAnalyzer_analyze(
                analyzer,
                image_path.encode("utf-8"),
            )

            artifact_name = ArtifactType(result.primary_artifact).name

            return {
                "bicoherence": result.global_bicoherence_score,
                "ai_probability": result.ai_generation_probability,
                "artifact_type": artifact_name,
                "confidence": result.confidence,
                "paranoid_mode": self.paranoid_mode,
                "error": result.error_message.decode("utf-8") if result.error_message else "",
            }
        except Exception as e:
            logger.error(f"Bispectral analysis failed: {e}")
            return {
                "bicoherence": 0.0,
                "ai_probability": 0.0,
                "artifact_type": "unknown",
                "confidence": 0.0,
                "error": str(e),
            }

    def set_paranoid_mode(self, enabled: bool):
        """Toggle paranoid mode (3.5σ vs 2σ threshold)"""
        self.paranoid_mode = enabled
        if self.enabled:
            analyzer = self.lib.BispectralAnalyzer_new(enabled)
            logger.info(f"Bispectral paranoid mode: {'ENABLED (3.5σ)' if enabled else 'DISABLED (2σ)'}")


# ============================================================================
# Module Initialization
# ============================================================================

def get_cpp_modules() -> Tuple[Optional[PRNUExtractorWrapper], Optional[BispectralAnalyzerWrapper]]:
    """Get initialized C++ module wrappers"""
    prnu = PRNUExtractorWrapper()
    bispectral = BispectralAnalyzerWrapper(paranoid_mode=True)

    return prnu, bispectral


if __name__ == "__main__":
    # Test module availability
    logging.basicConfig(level=logging.INFO)
    prnu, bispectral = get_cpp_modules()

    print(f"PRNU Module: {'✅ ENABLED' if prnu.enabled else '❌ DISABLED'}")
    print(f"Bispectral Module: {'✅ ENABLED' if bispectral.enabled else '❌ DISABLED'}")

    if not prnu.enabled or not bispectral.enabled:
        print("\n⚠️  C++ modules not available. Build with:")
        print("  cd redroom/forensics/cpp")
        print("  mkdir build && cd build")
        print("  cmake .. && cmake --build . --config Release")
