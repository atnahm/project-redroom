"""
Oculometric Consistency Analyzer

Detects facial anomalies by analyzing eye properties and corneal reflections.
Live human eyes have specific optical properties; deepfakes often fail to replicate them correctly.

Two-Pronged Approach:
  1. Geometric: Detect both eyes' specular highlights (corneal glints)
     Calculate implied 3D light source position for each eye
     If light sources diverge by >10°, flag as synthetic
     
  2. VLM-Augmented: Have the vision model analyze the eye region
     directly and flag physically implausible reflections
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EyeAnomalyType(Enum):
    """Types of eye anomalies detected"""
    NONE = "none"
    MISMATCHED_REFLECTIONS = "mismatched_reflections"  # Different light sources
    MISSING_REFLECTION = "missing_reflection"          # One eye has no glint
    UNNATURAL_SYMMETRY = "unnatural_symmetry"          # Too perfectly mirrored
    IMPOSSIBLE_GEOMETRY = "impossible_geometry"        # Reflections violate 3D space
    BLUR_ASYMMETRY = "blur_asymmetry"                  # Unnatural focus differences


@dataclass
class CornealReflectionAnalysis:
    """Result of corneal reflection analysis"""
    left_eye_found: bool
    right_eye_found: bool
    left_glint_position: Optional[Tuple[int, int]]     # (x, y) pixel coords
    right_glint_position: Optional[Tuple[int, int]]
    inferred_light_source_left: Optional[np.ndarray]   # 3D position (normalized)
    inferred_light_source_right: Optional[np.ndarray]
    light_source_divergence_angle: Optional[float]     # Degrees, >10° = suspicious
    anomaly_type: EyeAnomalyType
    anomaly_confidence: float                           # 0-1
    is_suspicious: bool
    detailed_metrics: Dict                              # Raw measurements


class OculometricAnalyzer:
    """
    Analyzes eye properties for deepfake detection
    """

    def __init__(self, vlm_model=None):
        """
        Initialize oculometric analyzer
        
        Args:
            vlm_model: Optional VLM for secondary validation
        """
        # Load Haar Cascade for eye detection
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.vlm_model = vlm_model

    def analyze(self, image: np.ndarray) -> CornealReflectionAnalysis:
        """
        Analyze eye properties in image
        
        Returns:
            CornealReflectionAnalysis with detailed metrics
        """
        # Detect face first
        face_region = self._detect_face(image)
        if face_region is None:
            logger.warning("Face not detected")
            return self._failed_analysis(EyeAnomalyType.NONE, 0.0)

        x, y, w, h = face_region
        face_crop = image[y:y+h, x:x+w, :]

        # Detect eyes within face region
        left_eye, right_eye = self._detect_eyes(face_crop)

        if left_eye is None or right_eye is None:
            logger.warning("Could not detect both eyes")
            return self._failed_analysis(EyeAnomalyType.NONE, 0.0)

        # Extract corneal glints (specular highlights)
        left_glint_pos = self._extract_corneal_glint(
            face_crop, left_eye, is_left=True
        )
        right_glint_pos = self._extract_corneal_glint(
            face_crop, right_eye, is_left=False
        )

        # If either glint is missing, can't analyze further
        if left_glint_pos is None or right_glint_pos is None:
            anomaly_type = EyeAnomalyType.MISSING_REFLECTION
            return self._failed_analysis(anomaly_type, 0.8)

        # Calculate implied light source positions (3D)
        left_light_3d = self._estimate_light_source_3d(
            left_eye, left_glint_pos, face_crop
        )
        right_light_3d = self._estimate_light_source_3d(
            right_eye, right_glint_pos, face_crop
        )

        # Calculate divergence angle
        divergence_angle = self._calculate_divergence(left_light_3d, right_light_3d)

        # Determine if suspicious
        is_suspicious = False
        anomaly_type = EyeAnomalyType.NONE
        anomaly_confidence = 0.0

        if divergence_angle > 10:
            # Light sources point in opposite directions = synthetic
            is_suspicious = True
            anomaly_type = EyeAnomalyType.MISMATCHED_REFLECTIONS
            anomaly_confidence = min(1.0, (divergence_angle - 10) / 20)

        # Check for unnatural symmetry (AI often makes eyes too perfectly mirrored)
        symmetry_score = self._check_reflection_symmetry(left_glint_pos, right_glint_pos)
        if symmetry_score > 0.95:
            is_suspicious = True
            anomaly_type = EyeAnomalyType.UNNATURAL_SYMMETRY
            anomaly_confidence = 0.7

        # VLM secondary check if available
        if self.vlm_model and is_suspicious:
            vlm_verdict = self._vlm_eye_check(face_crop, left_eye, right_eye)
            if vlm_verdict:
                anomaly_confidence = min(1.0, anomaly_confidence + 0.2)

        return CornealReflectionAnalysis(
            left_eye_found=True,
            right_eye_found=True,
            left_glint_position=left_glint_pos,
            right_glint_position=right_glint_pos,
            inferred_light_source_left=left_light_3d,
            inferred_light_source_right=right_light_3d,
            light_source_divergence_angle=divergence_angle,
            anomaly_type=anomaly_type,
            anomaly_confidence=anomaly_confidence,
            is_suspicious=is_suspicious,
            detailed_metrics={
                "reflection_symmetry_score": symmetry_score,
                "left_glint_brightness": self._measure_glint_brightness(face_crop, left_glint_pos),
                "right_glint_brightness": self._measure_glint_brightness(face_crop, right_glint_pos),
            }
        )

    # ========== PRIVATE METHODS ==========

    def _detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None
        
        # Return largest face
        return tuple(max(faces, key=lambda f: f[2] * f[3]))

    def _detect_eyes(self, face_crop: np.ndarray) -> Tuple[Optional[Tuple], Optional[Tuple]]:
        """
        Detect left and right eyes in face crop
        
        Returns:
            (left_eye, right_eye) or (None, None)
        """
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 5)

        if len(eyes) < 2:
            return None, None

        # Sort by x-coordinate: leftmost is left eye
        eyes_sorted = sorted(eyes, key=lambda e: e[0])
        return tuple(eyes_sorted[0]), tuple(eyes_sorted[1])

    def _extract_corneal_glint(
        self,
        face_crop: np.ndarray,
        eye_rect: Tuple[int, int, int, int],
        is_left: bool
    ) -> Optional[Tuple[int, int]]:
        """
        Extract the corneal glint (specular highlight) position
        
        Strategy:
          1. Crop to eye region
          2. Convert to HSV
          3. Find bright regions (V > threshold)
          4. Corneal glint usually topmost-left in eye
        """
        ex, ey, ew, eh = eye_rect
        eye_crop = face_crop[ey:ey+eh, ex:ex+ew, :]

        # Convert to HSV
        hsv = cv2.cvtColor(eye_crop, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2].astype(np.float32)

        # Find bright pixels (glint region)
        threshold = 200
        glint_mask = v_channel > threshold

        if not np.any(glint_mask):
            return None

        # Find contours of glint region
        glint_coords = np.argwhere(glint_mask)
        if len(glint_coords) == 0:
            return None

        # Corneal glint is usually the brightest spot
        brightest_idx = np.argmax(v_channel[glint_mask])
        glint_y, glint_x = glint_coords[brightest_idx]

        # Convert back to full face_crop coordinates
        glint_x_full = ex + glint_x
        glint_y_full = ey + glint_y

        return (glint_x_full, glint_y_full)

    def _estimate_light_source_3d(
        self,
        eye_rect: Tuple[int, int, int, int],
        glint_position: Tuple[int, int],
        face_crop: np.ndarray
    ) -> np.ndarray:
        """
        Estimate 3D light source position from corneal glint
        
        Basic ray-tracing from eye center through glint position
        Assumes cornea is roughly spherical at (eye_center, ~7mm radius)
        """
        ex, ey, ew, eh = eye_rect
        eye_center_x = ex + ew // 2
        eye_center_y = ey + eh // 2
        
        glint_x, glint_y = glint_position

        # Ray direction (from eye center to glint)
        ray_x = glint_x - eye_center_x
        ray_y = glint_y - eye_center_y

        # Normalize
        ray_length = np.sqrt(ray_x**2 + ray_y**2 + 1e-6)
        ray_x /= ray_length
        ray_y /= ray_length

        # Estimated light source in 3D (assuming depth ~300mm from face)
        # This is a simplified geometric model
        light_3d = np.array([ray_x, ray_y, 1.0])
        light_3d /= np.linalg.norm(light_3d)

        return light_3d

    def _calculate_divergence(
        self,
        left_light: np.ndarray,
        right_light: np.ndarray
    ) -> float:
        """
        Calculate angle between two light source directions (in degrees)
        
        If both eyes report opposite light sources, it's synthetic.
        Natural lighting should be similar for both eyes.
        """
        # Cosine similarity
        cos_angle = np.dot(left_light, right_light) / (
            np.linalg.norm(left_light) * np.linalg.norm(right_light) + 1e-6
        )
        cos_angle = np.clip(cos_angle, -1.0, 1.0)

        # Convert to degrees
        angle_rad = np.arccos(cos_angle)
        angle_deg = np.degrees(angle_rad)

        return angle_deg

    def _check_reflection_symmetry(
        self,
        left_pos: Tuple[int, int],
        right_pos: Tuple[int, int]
    ) -> float:
        """
        Check if reflections are suspiciously symmetric
        AI often produces perfectly mirrored eyes
        """
        left_x, left_y = left_pos
        right_x, right_y = right_pos

        # Horizontal symmetry: reflections at same relative position in each eye
        symmetry = 1.0 - (abs(left_x - right_x) / 256)  # Normalized to image width
        return np.clip(symmetry, 0.0, 1.0)

    def _measure_glint_brightness(
        self,
        face_crop: np.ndarray,
        glint_pos: Optional[Tuple[int, int]]
    ) -> float:
        """Measure brightness of corneal glint (0-255)"""
        if glint_pos is None:
            return 0.0

        x, y = glint_pos
        x = int(np.clip(x, 0, face_crop.shape[1]-1))
        y = int(np.clip(y, 0, face_crop.shape[0]-1))

        brightness = np.mean(face_crop[y, x, :])
        return brightness

    def _vlm_eye_check(
        self,
        face_crop: np.ndarray,
        left_eye: Tuple,
        right_eye: Tuple
    ) -> bool:
        """
        Secondary VLM check: ask if eye reflections are physically plausible
        
        Prompt: "Are the corneal reflections in these eyes physically consistent?"
        Expected: True for real, False for synthetic
        """
        if self.vlm_model is None:
            return False

        prompt = """
        Examine the corneal reflections (specular highlights) in these eyes.
        Are they physically plausible given a natural light source?
        Answer only: TRUE or FALSE
        """

        try:
            response = self.vlm_model.analyze(face_crop, prompt)
            return "true" in response.lower()
        except Exception as e:
            logger.error(f"VLM eye check failed: {e}")
            return False

    def _failed_analysis(
        self,
        anomaly_type: EyeAnomalyType,
        confidence: float
    ) -> CornealReflectionAnalysis:
        """Return failed analysis result"""
        return CornealReflectionAnalysis(
            left_eye_found=False,
            right_eye_found=False,
            left_glint_position=None,
            right_glint_position=None,
            inferred_light_source_left=None,
            inferred_light_source_right=None,
            light_source_divergence_angle=None,
            anomaly_type=anomaly_type,
            anomaly_confidence=confidence,
            is_suspicious=(confidence > 0.5),
            detailed_metrics={"error": "eye_detection_failed"}
        )
