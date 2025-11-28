import os
import json
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from PIL import Image
from datetime import datetime

class ForensicAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠ GEMINI_API_KEY not found. Forensic analysis will be disabled.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Forensic Engine (Gemini 1.5 Flash) Loaded!")

    def analyze(self, image: Image.Image):
        if not self.model:
            return None

        prompt = """
        ### ROLE
        You are the "Antigravity" Visual Forensics Engine. Your sole purpose is to analyze input images for subtle, high-level artifacts indicative of Generative Adversarial Networks (GANs) or Diffusion Models.

        ### THE ALGORITHM (Step-by-Step Analysis)
        Execute the following 5-point inspection:
        1. Dermatological Consistency: Check for "Subsurface Scattering" errors, waxy skin, undefined pores.
        2. Ocular Geometry: Check for asymmetrical "catchlights", jagged irises.
        3. Physics & Lighting: Check for inconsistent shadows, non-directional motion blur.
        4. Textile and Follicle Integrity: Check for "melting" hair, warping clothing patterns.
        5. Background Semantic Coherence: Check for morphing shapes, gibberish text.

        ### FINAL OUTPUT FORMAT
        Return ONLY valid JSON:
        {
          "visual_anomalies_detected": ["List specific flaw 1", "List specific flaw 2"],
          "human_likelihood_score": 0-100,
          "ai_generation_probability": 0-100,
          "verdict": "REAL" | "SYNTHETIC" | "UNCERTAIN",
          "reasoning_summary": "One sentence summary."
        }
        """

        try:
            # Add timeout to prevent hanging
            response = self.model.generate_content(
                [prompt, image],
                request_options={"timeout": 15}
            )
            # Clean up code blocks if present
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Forensic Analysis Failed: {e}")
            return None

# Singleton
_analyzer = None

def get_forensic_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = ForensicAnalyzer()
    return _analyzer
