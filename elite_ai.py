"""
JARVIS - Elite AI Engine (Personalized)
Sardor uchun maxsus yaratilgan shaxsiy AI yordamchi.
"""
import config
from llm_brain import GeminiBrain
from memory import MemoryEngine
from utils import setup_logger

class EliteAI:
    def __init__(self):
        self.logger = setup_logger("EliteAI")
        self.brain = GeminiBrain()
        self.memory = MemoryEngine()
        self.identity = "Elite Personal Intelligence (E.P.I)"
        self.version = "1.0.0"
        
    def get_personalized_prompt(self, user_query):
        """Foydalanuvchi ma'lumotlari asosida promptni shaxsiylashtirish"""
        user_name = self.memory.get_user_name()
        facts = self.memory.search_facts(user_query)
        
        context = f"Siz Sardorbekning shaxsiy AI yordamchisisiz (E.P.I). "
        context += f"Foydalanuvchi ismi: {user_name}. "
        
        if facts:
            context += "\nSiz u haqida quyidagilarni bilasiz:\n"
            for f in facts:
                context += f"- {f[0]}\n"
        
        full_prompt = f"{context}\n\nFOYDALANUVCHI BUYRUG'I: {user_query}\n\nJavobni professional, lekin yaqin yordamchi sifatida o'zbek tilida bering."
        return full_prompt

    def process(self, text):
        """Buyruqni qayta ishlash"""
        self.logger.info(f"Elite AI processing: {text}")
        
        # Maxsus 'Elite' buyruqlar
        if "o'zing haqingda" in text.lower() or "kimligingni" in text.lower():
            return f"Men {self.identity}, {user_name} uchun maxsus yaratilgan intellektual yordamchiman. Versiyam: {self.version}."
            
        # Shaxsiylashtirilgan LLM javobi
        prompt = self.get_personalized_prompt(text)
        response = self.brain.generate_response(prompt)
        
        return response

if __name__ == "__main__":
    # Test
    epi = EliteAI()
    print(epi.process("Menga bugungi ishlarimni eslat"))
