"""
JARVIS - Local AI Engine
Ollama orqali oflayn rejimda ishlash.
"""
import requests
import json
from utils import setup_logger

class LocalLLM:
    def __init__(self, model="llama3"):
        self.logger = setup_logger("LocalLLM")
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def is_available(self):
        """Ollama serveri ishlayotganini tekshirish"""
        try:
            response = requests.get("http://localhost:11434/", timeout=2)
            return response.status_code == 200
        except:
            return False

    def generate_response(self, prompt):
        """Lokal modeldan javob olish"""
        if not self.is_available():
            return "Ollama serveri topilmadi. Iltimos, Ollama dasturini ishga tushiring."

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.url, json=payload)
            data = response.json()
            return data.get("response", "Hech qanday javob olinmadi.")
        except Exception as e:
            self.logger.error(f"Local LLM error: {e}")
            return f"Lokal AI bilan bog'lanishda xatolik: {e}"

if __name__ == "__main__":
    # Test
    llm = LocalLLM()
    if llm.is_available():
        print("Modeldan javob kutilmoqda...")
        print(llm.generate_response("Salom, JARVIS!"))
    else:
        print("Ollama ishlamayapti.")
