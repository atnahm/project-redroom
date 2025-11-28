from transformers import pipeline
from PIL import Image

class DeepfakeDetector:
    def __init__(self):
        print("⏳ Loading AI Models...")
        
        # Model 1: Vision Transformer (Good for GANs)
        print("   - Loading ViT Model (dima806)...")
        self.pipe_vit = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")
        
        # Model 2: ResNet/ConvNext (Good for Diffusion/General)
        print("   - Loading Deep-Fake-Detector-v2 (prithivMLmods)...")
        self.pipe_v2 = pipeline("image-classification", model="prithivMLmods/Deep-Fake-Detector-v2-Model")
        
        print("✅ AI Models Loaded Successfully!")

    def analyze(self, image: Image.Image):
        """
        Analyzes the image using an Ensemble approach (ViT + V2).
        """
        # 1. Run ViT
        res_vit = self.pipe_vit(image)
        score_vit = res_vit[0]['score'] if res_vit[0]['label'].lower() in ['fake', 'ai', 'generated'] else (1 - res_vit[0]['score'])
        
        # 2. Run V2
        res_v2 = self.pipe_v2(image)
        # Assuming V2 returns 'Fake'/'Real' labels similar to ViT
        score_v2 = res_v2[0]['score'] if res_v2[0]['label'].lower() in ['fake', 'ai', 'generated'] else (1 - res_v2[0]['score'])

        print(f"🔍 ViT Score (Fake Prob): {score_vit:.4f}")
        print(f"🔍 V2 Score (Fake Prob):  {score_v2:.4f}")

        # 3. Ensemble Logic (Average)
        avg_fake_prob = (score_vit + score_v2) / 2
        
        is_fake = avg_fake_prob > 0.5
        confidence = avg_fake_prob if is_fake else (1 - avg_fake_prob)
        
        return {
            "is_fake": is_fake,
            "confidence": confidence,
            "label": "Fake" if is_fake else "Real",
            "details": {
                "vit_score": score_vit,
                "v2_score": score_v2
            }
        }

# Singleton instance
_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = DeepfakeDetector()
    return _detector
