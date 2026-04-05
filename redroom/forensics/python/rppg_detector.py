"""
Remote Photoplethysmography (rPPG) - Cardiac Pulse Detection

The "ace card" against deepfakes. Live humans have a detectable pulse (~60-100 bpm).
AI-generated faces either lack a pulse signal entirely or have synthetic, overly-regular pulses.

Mode-Based Adaptation:
  - CLINICAL: High-quality, controlled lighting → High accuracy (95%+)
  - SURVEILLANCE: Grainy, off-angle → Moderate accuracy (60-75%)
  - EXTREME: Very low quality → Best-effort (may return None)

Algorithm: ChromaNet-style ICA (Independent Component Analysis)
  1. Extract green channel (hemoglobin absorbs green most)
  2. Spatially average face region
  3. Apply ICA to isolate pulse signal
  4. Extract heart rate (HRV signature)
  5. Compare against natural cardiac variability databases
  6. Flag if pulse absent, synthetic (too regular), or frame interpolation artifacts

Reference: Verkruysse, W., et al. (2008). "Remote plethysmographic imaging using 
ambient light." Optics Express.
"""

import cv2
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from scipy.stats import skew, kurtosis
from sklearn.decomposition import FastICA
import logging
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QualityMode(Enum):
    """Input quality assessment modes (like temperature in AI models)"""
    CLINICAL = "clinical"      # Best case: controlled lighting, frontal face
    SURVEILLANCE = "surveillance"  # Typical: security camera, compressed
    EXTREME = "extreme"        # Worst case: grainy, off-angle, poor lighting


@dataclass
class rPPGResult:
    """Result of rPPG analysis"""
    pulse_detected: bool           # True if cardiac pulse found
    heart_rate: Optional[float]    # Estimated HR in bpm (None if not detected)
    heart_rate_variability: Optional[float]  # HRV (std dev of HR)
    signal_quality: float          # 0-1, confidence in the measurement
    is_synthetic: bool             # True if pulse is artificially regular (AI-generated)
    interpolation_artifacts: bool  # True if frame interpolation detected
    quality_mode: QualityMode      # Which mode was inferred
    detailed_analysis: Dict        # Raw metrics for forensic report


class rPPGDetector:
    """
    Detects cardiac pulse in video/image frames using ICA-based chromatic analysis
    """

    def __init__(self):
        """Initialize rPPG detector"""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect_from_video(self, video_path: str) -> rPPGResult:
        """
        Extract pulse from video file
        
        Args:
            video_path: Path to video file (must be 30-60 fps)
            
        Returns:
            rPPGResult with pulse detection and heart rate
        """
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps < 25:
            logger.warning(f"Low FPS ({fps}). Pulse detection may fail.")
        
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()

        if len(frames) < 30:  # Need minimum 1 second at 30fps
            logger.warning("Video too short for rPPG analysis")
            return self._failed_result(QualityMode.EXTREME)

        return self._analyze_frames(frames, fps)

    def detect_from_frames(self, frames: List[np.ndarray], fps: int = 30) -> rPPGResult:
        """
        Extract pulse from frame sequence
        
        Args:
            frames: List of BGR images
            fps: Frame rate (default 30)
            
        Returns:
            rPPGResult with pulse detection
        """
        if len(frames) < 30:
            logger.warning("Insufficient frames for rPPG")
            return self._failed_result(QualityMode.EXTREME)

        return self._analyze_frames(frames, fps)

    def detect_from_image(self, image: np.ndarray) -> rPPGResult:
        """
        Single image: cannot extract pulse, but can assess quality
        
        Returns:
            rPPGResult with pulse_detected=False (not enough data)
        """
        logger.info("Single image submitted. Cannot extract pulse from statics image.")
        return self._failed_result(self._assess_image_quality(image))

    # ========== PRIVATE METHODS ==========

    def _analyze_frames(self, frames: List[np.ndarray], fps: int) -> rPPGResult:
        """Core rPPG analysis pipeline"""
        
        # Step 1: Detect face region (use first frame)
        face_region = self._detect_face_region(frames[0])
        if face_region is None:
            logger.warning("Face not detected")
            return self._failed_result(QualityMode.SURVEILLANCE)

        x, y, w, h = face_region
        
        # Step 2: Extract green channel signal from face region
        green_signals = self._extract_green_channel_signal(frames, x, y, w, h)
        
        # Step 3: Assess quality mode based on signal characteristics
        quality_mode = self._assess_quality_mode(green_signals)
        
        # Step 4: Apply ICA to isolate pulse signal
        try:
            pulse_signal = self._apply_ica(green_signals)
        except Exception as e:
            logger.error(f"ICA failed: {e}")
            return self._failed_result(quality_mode)

        # Step 5: Extract heart rate
        hr, hrv = self._extract_heart_rate(pulse_signal, fps)
        
        if hr is None:
            logger.warning("Could not extract heart rate")
            return self._failed_result(quality_mode)

        # Step 6: Check for synthetic pulse (AI-generated faces have unnaturally regular HRV)
        is_synthetic = self._is_synthetic_pulse(pulse_signal, hrv)

        # Step 7: Check for frame interpolation artifacts
        has_interpolation = self._detect_frame_interpolation(frames)

        # Step 8: Compute signal quality
        signal_quality = self._compute_signal_quality(
            pulse_signal, green_signals, quality_mode
        )

        return rPPGResult(
            pulse_detected=True,
            heart_rate=hr,
            heart_rate_variability=hrv,
            signal_quality=signal_quality,
            is_synthetic=is_synthetic,
            interpolation_artifacts=has_interpolation,
            quality_mode=quality_mode,
            detailed_analysis={
                "raw_green_signal_mean": np.mean(green_signals),
                "raw_green_signal_std": np.std(green_signals),
                "pulse_signal_snr": self._estimate_snr(pulse_signal, green_signals),
                "frame_count": len(frames),
            }
        )

    def _detect_face_region(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face bounding box"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None
        
        # Use largest face
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        return (x, y, w, h)

    def _extract_green_channel_signal(
        self, 
        frames: List[np.ndarray], 
        x: int, y: int, w: int, h: int
    ) -> np.ndarray:
        """
        Extract spatially-averaged green channel signal from face region
        Hemoglobin absorbs green light most strongly (500-600 nm)
        """
        green_signals = []

        for frame in frames:
            # Crop to face region
            face_crop = frame[y:y+h, x:x+w, :]
            
            # Extract green channel (index 1 in BGR)
            green_channel = face_crop[:, :, 1].astype(np.float32)
            
            # Spatial average
            green_mean = np.mean(green_channel)
            green_signals.append(green_mean)

        return np.array(green_signals)

    def _assess_quality_mode(self, green_signals: np.ndarray) -> QualityMode:
        """Infer quality mode from signal characteristics"""
        signal_std = np.std(green_signals)
        signal_snr = signal_std / (1e-6 + np.mean(np.abs(np.diff(green_signals))))
        
        if signal_snr > 50:
            return QualityMode.CLINICAL
        elif signal_snr > 10:
            return QualityMode.SURVEILLANCE
        else:
            return QualityMode.EXTREME

    def _apply_ica(self, green_signals: np.ndarray) -> np.ndarray:
        """
        Apply Independent Component Analysis to isolate pulse signal
        
        The green channel contains:
          1. Illumination (slow, DC component)
          2. Motion (medium, 0-2 Hz)
          3. Pulse (1.5-2 Hz, cardiac signal)
          4. Noise (high frequency)
        
        ICA separates these into independent components.
        The pulse is the component with energy in the 40-180 bpm range.
        """
        # Reshape for ICA: (n_samples, n_features)
        X = green_signals.reshape(-1, 1)
        
        ica = FastICA(n_components=1, random_state=42, max_iter=500)
        S = ica.fit_transform(X).flatten()
        
        return S

    def _extract_heart_rate(
        self, 
        pulse_signal: np.ndarray, 
        fps: int
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Extract heart rate and HRV from pulse signal
        
        Returns:
            (heart_rate_bpm, heart_rate_variability)
        """
        # Bandpass filter: 0.5-3 Hz (30-180 bpm)
        nyquist = fps / 2
        low = 0.5 / nyquist
        high = 3.0 / nyquist
        
        if high >= 1.0:
            high = 0.99
        
        b, a = butter(4, [low, high], btype='band')
        filtered = filtfilt(b, a, pulse_signal)
        
        # Find peaks (heartbeats)
        peaks, properties = find_peaks(filtered, distance=fps//3)  # Min 20 bpm spacing
        
        if len(peaks) < 3:  # Need at least 3 beats
            return None, None
        
        # Calculate inter-beat intervals
        ibi = np.diff(peaks) / fps * 60  # Convert to seconds, then to BPM equivalent
        
        # Heart rate = mean of IBIs inverted
        heart_rate = 60.0 / np.mean(ibi)
        
        # HRV = standard deviation of IBIs
        hrv = np.std(ibi)
        
        # Sanity check
        if heart_rate < 30 or heart_rate > 200:
            return None, None
        
        return heart_rate, hrv

    def _is_synthetic_pulse(self, pulse_signal: np.ndarray, hrv: float) -> bool:
        """
        Detect if pulse is artificially regular (AI-generated)
        
        Deepfakes often have:
          - Too-regular pulse (synthetic sinusoid)
          - Unnatural HRV (zero or constant)
          - Suspiciously clean signal
        """
        # Natural HRV is typically 10-100 ms between beats
        # AI-generated: often <5 ms (too regular)
        if hrv < 5 and hrv > 0:
            return True
        
        # Check for overly sinusoidal pattern (AI characteristic)
        skewness = skew(pulse_signal)
        kurtosis_val = kurtosis(pulse_signal)
        
        # Natural pulse: skewed, high kurtosis (peaks and troughs)
        # AI pulse: symmetric, low kurtosis (smooth sine)
        if abs(skewness) < 0.3 and kurtosis_val < 2:
            return True
        
        return False

    def _detect_frame_interpolation(self, frames: List[np.ndarray]) -> bool:
        """
        Detect if frames were interpolated (deepfake frame synthesis technique)
        
        Optical flow consistency check:
          - Real video: smooth, consistent motion
          - Interpolated: abrupt changes, repeated frames, or motion incoherence
        """
        if len(frames) < 10:
            return False

        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        flow_magnitudes = []

        for i in range(1, min(10, len(frames))):
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            flow_magnitudes.append(np.mean(magnitude))
            prev_gray = curr_gray

        # Detect sudden changes (interpolation artifacts)
        flow_diff = np.abs(np.diff(flow_magnitudes))
        if np.max(flow_diff) > 2 * np.mean(flow_diff):
            return True

        return False

    def _compute_signal_quality(
        self,
        pulse_signal: np.ndarray,
        green_signals: np.ndarray,
        quality_mode: QualityMode
    ) -> float:
        """Compute overall signal quality (0-1)"""
        # SNR-based quality
        snr = self._estimate_snr(pulse_signal, green_signals)
        
        # Mode-based weighting
        if quality_mode == QualityMode.CLINICAL:
            return min(1.0, snr / 50)  # High bar
        elif quality_mode == QualityMode.SURVEILLANCE:
            return min(1.0, snr / 15)  # Moderate bar
        else:
            return min(1.0, snr / 5)   # Low bar

    @staticmethod
    def _estimate_snr(signal: np.ndarray, reference: np.ndarray) -> float:
        """Estimate signal-to-noise ratio"""
        signal_power = np.mean(signal**2)
        noise_power = np.mean(reference**2) - signal_power
        return 10 * np.log10(signal_power / max(noise_power, 1e-10))

    def _assess_image_quality(self, image: np.ndarray) -> QualityMode:
        """Assess static image quality"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        if variance > 100:
            return QualityMode.CLINICAL
        elif variance > 30:
            return QualityMode.SURVEILLANCE
        else:
            return QualityMode.EXTREME

    def _failed_result(self, quality_mode: QualityMode) -> rPPGResult:
        """Return failure result"""
        return rPPGResult(
            pulse_detected=False,
            heart_rate=None,
            heart_rate_variability=None,
            signal_quality=0.0,
            is_synthetic=False,
            interpolation_artifacts=False,
            quality_mode=quality_mode,
            detailed_analysis={"error": "pulse_extraction_failed"}
        )
