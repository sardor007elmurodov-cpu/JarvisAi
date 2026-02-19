import os
import time
import mss
import pyautogui
from llm_brain import GeminiBrain
import mss.tools
from utils import setup_logger

class JARVISTyperBot:
    """
    Universal Typer Bot for JARVIS (Master Edition).
    Captures screen, extracts text via Gemini Vision, and types it.
    """
    def __init__(self):
        self.logger = setup_logger("JARVISTyperBot")
        self.brain = None # Lazy load
        self.is_running = False
        self.typing_speed = 0.005 # Ultra-fast typing
        self.cooldown_until = 0 # Cooldown timer for 429
        self.last_hash = None # To prevent redundant API calls
        self._initialized = False

    def _setup(self):
        """Lazy load heavy dependencies"""
        if not self._initialized:
            from llm_brain import GeminiBrain
            self.brain = GeminiBrain()
            self._initialized = True
        
    def start(self):
        """Botni ishga tushirish"""
        self.is_running = True
        self.last_hash = None # Reset hash to force detection on start
        print("⌨️ Typer Bot activated. JARVIS is watching the screen...")
        
    def stop(self):
        """Botni to'xtatish"""
        self.is_running = False
        self.last_hash = None
        print("⌨️ Typer Bot deactivated.")

    def run_once(self):
        """Bitta sikl: Screenshot -> AI Brain -> Auto-Type"""
        import config
        if not self.is_running or config.SENTINEL_MODE.get("is_locked", False): 
            return
            
        self._setup() # Ensure brain is ready
        
        # 0. Cooldown check FIRST (stay within 10-15 RPM for Free Tier)
        if time.time() < self.cooldown_until:
            return

        try:
            # 1. Screenshot olish (Full Screen to be sure)
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot_path = "typer_snap.png"
                
                # Full screen capture
                sct_img = sct.grab(monitor)
                
                # OPTIMIZATION: Ultra-Sensitive Hashing
                from PIL import Image
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                # 16x16 is extremely sensitive to any visual change
                img_small = img.resize((16, 16), Image.Resampling.NEAREST).convert("L")
                current_hash = hash(img_small.tobytes())
                
                if self.last_hash == current_hash:
                    return # Screen didn't change at all
                
                self.last_hash = current_hash
                img.save(screenshot_path)
            
            self.logger.info(f"Visual change detected. Analyzing...")
            # Optionally speak asynchronous feedback if integrated with core
            # self._speak("Ekranni tahlil qilyapman...") 
            
            # 2. Gemini Vision orqali matnni o'qish (Solver & Typer Mode)
            prompt = """
                Return ONLY the text to be typed OR the solution to the task on screen.
                RULES:
                1. Identify the task: Typing test, Coding challenge, Math problem, or general Question.
                2. If it's a challenge/problem: SOLVE it and return ONLY the answer/code.
                3. If it's a typing test: Return the RAW text exactly as it appears.
                4. If it's a picture with text: Extract and return the text.
                5. IGNORE HUD overlays, stats, or menus.
                6. RETURN ONLY PLAIN TEXT. NO MARKDOWN. NO EXPLANATIONS.
                7. If no task or text is found, return NOTHING.
                """
            
            if not self.brain._initialized:
                self.logger.error("Gemini Brain not initialized.")
                return

            text = self.brain.analyze_image(screenshot_path, prompt)
            
            if text == "ERROR_QUOTA_EXCEEDED":
                self.logger.warning("🛑 Quota Exceeded. 60s cooldown.")
                self.cooldown_until = time.time() + 60
                return
            
            if text:
                # Clean markdown and artifacts
                text = text.replace("```", "").strip()
                if not text: 
                    self.logger.warning("AI returned empty/whitespace string.")
                    return

                self.logger.info(f"📖 Sending detected text to system (Len: {len(text)})")
                
                # 3. Smart Typing (Elite v30.0)
                # If text is long, use clipboard for stability and speed
                if len(text) > 100:
                    self.logger.info("Using Clipboard for high-capacity transfer...")
                    import pyperclip
                    pyperclip.copy(text)
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'v')
                else:
                    # Realistic human-like typing for short texts
                    self.logger.info("Simulating realistic keystrokes...")
                    for char in text:
                        if not self.is_running: break
                        pyautogui.write(char)
                        # Speed optimization: 0.005 - 0.02 range
                        time.sleep(random.uniform(0.005, 0.015)) 
                
                self.logger.info("✅ Cycle complete.")
            else:
                self.logger.info("ℹ️ AI found no text to type on this screen.")
            
            # Cleanup
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                
        except Exception as e:
            self.logger.error(f"Typer Bot Cycle Error: {e}")

    def auto_loop(self):
        """Doimiy ravishda o'qish va yozish"""
        while self.is_running:
            self.run_once()
            # 3s is much more responsive while still respecting basic quota
            time.sleep(3) 

if __name__ == "__main__":
    bot = JARVISTyperBot()
    bot.start()
    bot.run_once()
