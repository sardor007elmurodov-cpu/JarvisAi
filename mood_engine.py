"""
JARVIS - Mood Detection Engine
Kamera orqali foydalanuvchi kayfiyatini aniqlash.
"""
import os
from utils import setup_logger

class MoodEngine:
    def __init__(self, vision_engine=None):
        self.logger = setup_logger("MoodEngine")
        self.vision = vision_engine

    def detect_mood(self):
        """Kamera orqali kayfiyatni aniqlash"""
        if not self.vision:
            return "Vision moduli ulanmagan."
            
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return "Kameradan rasm olib bo'lmadi."
            
        prompt = """
        Ushbu rasmda ko'ringan insonning yuz ifodasiga qarab uning kayfiyatini aniqlang.
        Javobni o'zbek tilida, qisqa va aniq bering (masalan: 'Xursand', 'Charchagan', 'Jiddiy').
        Shuningdek, ushbu kayfiyatga mos bitta kichik maslahat yoki gap ayting.
        """
        
        try:
            mood_analysis = self.vision.analyze_camera_frame(frame, prompt)
            return mood_analysis
        except Exception as e:
            self.logger.error(f"Mood detection error: {e}")
            return f"Kayfiyatni aniqlashda xatolik: {e}"

    def analyze_text_emotion(self, text):
        """Matn orqali hissiyotni aniqlash (Simple keyword + LLM)"""
        text = text.lower()
        
        # Simple keywords for speed
        if any(w in text for w in ["xursand", "baxtli", "happy", "joy", "zor", "ajoyib"]):
            return "HAPPY", "#00ff88"
        elif any(w in text for w in ["xafa", "sad", "yig'la", "depress", "yomon"]):
            return "SAD", "#0088ff"
        elif any(w in text for w in ["jahli", "angry", "asabi", "fu", "lanat"]):
            return "ANGRY", "#ff4444"
        elif any(w in text for w in ["charchadim", "tired", "uyqu", "sleep"]):
            return "TIRED", "#aa88ff"
        elif any(w in text for w in ["qo'rq", "scare", "fear"]):
            return "FEAR", "#ffaa00"
            
        return "NEUTRAL", "#00e0ff"

if __name__ == "__main__":
    mood = MoodEngine()
    print(mood.analyze_text_emotion("Men juda xursandman!"))
