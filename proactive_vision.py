"""
JARVIS - Proactive Vision Worker (Phase 4)
Periodically captures screen and analyzes it to provide proactive suggestions.
"""

import time
import threading
import mss
import os
from PIL import Image

class ProactiveVision:
    def __init__(self, core=None, brain=None):
        self.core = core
        self.brain = brain
        self.running = False
        self.interval = 15 # Check every 15 seconds (Real-time Feel)
        self.thread = None
        self.last_analysis = ""

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            print("👁️ Proactive Vision: Online")

    def stop(self):
        self.running = False
        print("👁️ Proactive Vision: Offline")

    def _run_loop(self):
        while self.running:
            try:
                self._analyze_screen()
            except Exception as e:
                print(f"Vision Worker Error: {e}")
            time.sleep(self.interval)

    def _analyze_screen(self):
        if not self.brain or not self.brain._initialized:
            return

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot_path = "vision_temp.png"
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img.save(screenshot_path)

        prompt = """
        Siz JARVIS Vision (Ko'z) tizimisiz. Ekrandagi holatni tezkor tahlil qiling.
        FAQAT quyidagi holatlarda javob qaytaring (O'zbek tilida):
        1. Qizil xatoliklar (Error/Exception) kodda yoki terminalda.
        2. Muhim ogohlantirishlar (Low Battery, Virus threat).
        3. Foydalanuvchi qandaydir murakkab muammo ustida ishlayotgan bo'lsa (masalan, StackOverflow ochiq bo'lsa).
        4. Muhim bildirishnomalar (Notifications) o'tkazib yuborilgan bo'lsa.
        
        Agar hammasi joyida bo'lsa yoki oddiy ish jarayoni bo'lsa, HECH NIMA YOZMANG (bo'sh qoldiring).
        Javobni 'Janob, ...' deb boshlang va juda qisqa (max 12 so'z) bo'lsin.
        """

        analysis = self.brain.analyze_image(screenshot_path, prompt)
        
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        if analysis and analysis.strip() and analysis != self.last_analysis:
            self.last_analysis = analysis
            print(f"👁️ PROACTIVE VISION DETECTED: {analysis}")
            if self.core:
                # Use JARVIS's central speak method
                self.core.speak(f"[VISION] {analysis}")

if __name__ == "__main__":
    from llm_brain import GeminiBrain
    brain = GeminiBrain()
    vision = ProactiveVision(brain=brain)
    vision.start()
    while True:
        time.sleep(1)
