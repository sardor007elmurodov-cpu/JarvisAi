"""
JARVIS - Dream Weaver (Tushlar Rejimi)
Kunlik faoliyat asosida AI san'at asarini yaratish.
1. Loglarni o'qiydi.
2. Gemini orqali "Tush Promtini" tuzadi.
3. Pollinations.ai orqali rasmni generatsiya qiladi.
"""
import os
import time
import requests
import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import setup_logger

class DreamWeaver:
    def __init__(self):
        from config import AI_MODEL_NAME
        self.logger = setup_logger("DreamWeaver")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(AI_MODEL_NAME)
        self.dreams_dir = os.path.join(os.getcwd(), "dreams")
        if not os.path.exists(self.dreams_dir):
            os.makedirs(self.dreams_dir)

    def generate_dream(self):
        """Tush ko'rish jarayoni"""
        self.logger.info("Dream sequence initiated...")
        
        # 1. Loglarni tahlil qilish
        log_summary = self._get_log_summary()
        
        # 2. Promt yaratish
        dream_prompt = self._create_visual_prompt(log_summary)
        self.logger.info(f"Dream Prompt: {dream_prompt}")
        
        # 3. Rasmni generatsiya qilish
        image_path = self._fetch_image(dream_prompt)
        
        if image_path:
            return f"Tush tayyor, janob. Rasmni bu yerda ko'rishingiz mumkin: {image_path}\nTush ta'rifi: {dream_prompt}"
        else:
            return "Tushni tasvirlashda xatolik yuz berdi."

    def _get_log_summary(self):
        """Log faylidan so'nggi voqealarni olish"""
        from config import LOG_CONFIG
        log_file = os.path.join(os.getcwd(), LOG_CONFIG["log_dir"], LOG_CONFIG["log_file"])
        if not os.path.exists(log_file):
            return "A peaceful day with no records."
            
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                # Last 2000 chars roughly
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - 2000))
                lines = f.readlines()
                return "".join(lines)
        except:
            return "Abstract system data."

    def _create_visual_prompt(self, context):
        """Gemini yordamida rasm uchun prompt tuzish"""
        prompt = f"""
        Based on the following system logs, create a short, artistic, and abstract visual description for an AI art generator.
        The description should represent the "mood" of the day (e.g., busy, calm, error-prone, productive).
        Keep it under 20 words. Focus on colors and cybernetic elements.
        
        Logs:
        {context}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "Cybernetic dreamscape with neon blue lights and digital rain"

    def _fetch_image(self, prompt):
        """Pollinations.ai orqali rasm yuklab olish"""
        try:
            # URL encode prompt
            safe_prompt = requests.utils.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{safe_prompt}"
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                filename = f"dream_{int(time.time())}.jpg"
                filepath = os.path.join(self.dreams_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return filepath
        except Exception as e:
            self.logger.error(f"Image generation error: {e}")
            
        return None

if __name__ == "__main__":
    dw = DreamWeaver()
    print(dw.generate_dream())
