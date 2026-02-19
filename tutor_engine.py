"""
JARVIS - AI Tutor Engine
Til o'rganishda yordam beruvchi aqlli modul.
"""
import google.generativeai as genai
from utils import setup_logger

class TutorEngine:
    def __init__(self):
        from config import GEMINI_API_KEY, AI_MODEL_NAME
        self.logger = setup_logger("TutorEngine")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(AI_MODEL_NAME)
        self.session_history = []

    def start_session(self, language="Ingliz tili"):
        """Yangi o'quv sessiyasini boshlash"""
        self.session_history = []
        prompt = f"Siz professional {language} o'qituvchi JARVIS-siz. Foydalanuvchi bilan salomlashing va bugungi darsni boshlang."
        try:
            response = self.model.generate_content(prompt)
            self.session_history.append({"role": "user", "parts": [prompt]})
            self.session_history.append({"role": "model", "parts": [response.text]})
            return response.text
        except Exception as e:
            self.logger.error(f"Tutor start error: {e}")
            return f"O'qituvchi modulini ishga tushirishda xatolik: {e}"

    def get_feedback(self, user_text, language="Ingliz tili"):
        """Foydalanuvchi matniga feedback berish va suhbatni davom ettirish"""
        prompt = f"""
        Foydalanuvchi quyidagi matnni yozdi/aytdi: '{user_text}'
        
        Sizning vazifangiz:
        1. Agar xato bo'lsa, uni tuzatib tushuntiring (o'zbek tilida).
        2. Suhbatni {language}da davom ettiring.
        3. Foydalanuvchidan savol so'rang.
        
        Javobingizni avval o'zbek tilidagi feedback, so'ngra {language}dagi javob bilan bering.
        """
        try:
            # We don't always use chat session for memory here to keep it simple and focused on feedback
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Tutor feedback error: {e}")
            return f"Feedback olishda xatolik: {e}"

if __name__ == "__main__":
    # Test
    tutor = TutorEngine()
    print(tutor.start_session())
    print("-" * 20)
    print(tutor.get_feedback("I is a student"))
