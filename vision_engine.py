"""
JARVIS - AI Vision Engine (Modern SDK v13.0)
Uses the new google-genai SDK for vision tasks.
"""
import os
import mss
import time
from datetime import datetime
from PIL import Image
import google.genai as genai
from google.genai import types

class VisionEngine:
    def __init__(self, brain_module=None):
        from config import GEMINI_API_KEY, AI_MODEL_NAME
        self.api_key = GEMINI_API_KEY
        self.model_id = AI_MODEL_NAME
        self.client = genai.Client(api_key=self.api_key)
        self.brain = brain_module
        
        # Captures directory
        self.cap_dir = os.path.join(os.getcwd(), "captures")
        if not os.path.exists(self.cap_dir):
            os.makedirs(self.cap_dir)

    def capture_screen(self):
        """Ekranni rasmga olish"""
        with mss.mss() as sct:
            filename = f"vision_capture_{datetime.now().strftime('%H%M%S')}.png"
            filepath = os.path.join(self.cap_dir, filename)
            sct.shot(output=filepath)
            return filepath

    def describe_screen(self, user_prompt="Ushbu ekranda nimalar ko'rinayapti? Javobni o'zbek tilida bering."):
        """Ekranni tahlil qilish va javob berish"""
        filepath = self.capture_screen()
        
        try:
            img = Image.open(filepath)
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[user_prompt, img]
            )
            
            # Clean up
            try:
                img.close()
                os.remove(filepath)
            except: pass
            
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "Quota exceeded" in error_msg or "429" in error_msg:
                return "Janob, ko'rish tizimi biroz charchadi (API Quota Limit). Iltimos, 1 daqiqa kuting."
            return f"Ko'rish tizimida xatolik: {e}"

    def analyze_camera_frame(self, frame, prompt="Ushbu rasmda nimalar bor?"):
        """Kamera kadrini tahlil qilish"""
        try:
            import cv2
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img_rgb)
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, img]
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                return "API cheklovi (Quota) oshib ketdi. Biroz kuting."
            return f"Kamera tahlilidaxatolik: {e}"

if __name__ == "__main__":
    vision = VisionEngine()
    print(f"Ekran tahlil qilinmoqda ({vision.model_id})...")
    print(vision.describe_screen())
