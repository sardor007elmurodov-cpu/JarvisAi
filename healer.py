"""
JARVIS - Self-Healing Code System
Xatolarni avtomatik aniqlash va tuzatish tizimi.
Log fayllarini kuzatadi va Gemini yordamida yechim topadi.
"""
import os
import time
import re
import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import setup_logger

class CodeHealer:
    def __init__(self):
        from llm_brain import GeminiBrain
        from config import LOG_CONFIG
        self.logger = setup_logger("CodeHealer")
        self.brain = GeminiBrain()
        self.log_file = os.path.join(os.getcwd(), LOG_CONFIG["log_dir"], LOG_CONFIG["log_file"])
        self.last_pos = 0

    def analyze_error(self, error_text):
        """Xatolikni sun'iy intellekt (DeepSeek/Gemini) yordamida tahlil qilish"""
        prompt = f"""
        JARVIS tizim logida xatolik aniqlandi. Uni tahlil qiling va TUZATISH uchun JSON formatida javob bering.
        
        LOG:
        {error_text}
        
        JSON formati faqat shu ko'rinishda bo'lsin:
        {{
            "reason": "Xatolik sababi",
            "file": "fayl_yo'li",
            "search_snippet": "tuzatilishi kerak bo'lgan eski kod qismi (aniq match bo'lishi shart)",
            "replace_snippet": "yangi tuzatilgan kod",
            "is_dependency_error": true/false,
            "module_to_install": "pip_uchun_modul_nomi"
        }}
        """
        try:
            # Use unified brain (uses DeepSeek if available)
            response_text = self.brain.generate_response(prompt)
            
            if not response_text:
                return {"error": "AI javob bermadi"}

            # JSON extraction
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {"error": "JSON topilmadi", "raw": response_text}
        except Exception as e:
            return {"error": str(e)}

    def apply_fix(self, fix_data):
        """Faylga o'zgartirish kiritish (Self-Patching)"""
        file_path = fix_data.get("file")
        search_snippet = fix_data.get("search_snippet")
        replace_snippet = fix_data.get("replace_snippet")
        
        if not file_path or not os.path.exists(file_path) or not search_snippet:
            return False
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if search_snippet in content:
                new_content = content.replace(search_snippet, replace_snippet)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                self.logger.info(f"✅ AUTO-REPAIR: Applied patch to {file_path}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Patch failed: {e}")
            
        return False

    def handle_dependencies(self, module_name):
        """Missing modulni pip orqali o'rnatish"""
        if not module_name: return False
        self.logger.info(f"📦 AUTO-REPAIR: Missing module '{module_name}' detected. Installing...")
        import subprocess
        try:
            subprocess.run(["pip", "install", module_name], check=True)
            return True
        except: return False

    def check_logs(self):
        """Log faylini tekshirish va avtomatik tuzatish"""
        if not os.path.exists(self.log_file):
            return None
            
        with open(self.log_file, "r", encoding="utf-8") as f:
            f.seek(self.last_pos)
            lines = f.readlines()
            self.last_pos = f.tell()
            
        error_chunk = "".join([l for l in lines if "ERROR" in l or "Exception" in l or "Traceback" in l])
        
        if error_chunk:
            self.logger.info("Self-healing sequence initiated...")
            fix_data = self.analyze_error(error_chunk)
            
            if "error" in fix_data: return None
            
            # 1. Dependency check
            if fix_data.get("is_dependency_error"):
                success = self.handle_dependencies(fix_data.get("module_to_install"))
                if success: return f"🔧 [HEALER] Missing module '{fix_data['module_to_install']}' installed automatically."
                
            # 2. Code Fix check
            if fix_data.get("file") and fix_data.get("search_snippet"):
                success = self.apply_fix(fix_data)
                if success:
                    return f"🔥 [HEALER] BUG FIXED: {fix_data['reason']} in {os.path.basename(fix_data['file'])}"
                    
        return None

if __name__ == "__main__":
    healer = CodeHealer()
    # Mock error for testing
    print(healer.analyze_error("ZeroDivisionError: division by zero at executor.py line 50"))
