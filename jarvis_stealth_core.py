
import os
import sys
import subprocess
import time
import threading
from utils import setup_logger

class JARVISStealthCore:
    """
    The Invisible Heart of JARVIS.
    Runs on the laptop background, managing all essential services.
    """
    def __init__(self):
        self.logger = setup_logger("StealthCore")
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Detect Python
        venv_python = os.path.join(self.current_dir, ".venv", "Scripts", "python.exe")
        self.python_exe = venv_python if os.path.exists(venv_python) else sys.executable
        
        self.services = {}
        self.is_running = True

    def start_service(self, name, script_name):
        """Fondagi xizmatni ishga tushirish (yashirin)"""
        if name in self.services and self.services[name].poll() is None:
            self.logger.info(f"{name} allaqachon ishlayapti.")
            return

        script_path = os.path.join(self.current_dir, script_name)
        if not os.path.exists(script_path):
            self.logger.error(f"Fayl topilmadi: {script_name}")
            return

        self.logger.info(f"Yashirin xizmat ishga tushmoqda: {name} ({script_name})")
        
        # Use subprocess.CREATE_NO_WINDOW on Windows for true stealth
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = 0x08000000 # CREATE_NO_WINDOW

        proc = subprocess.Popen(
            [self.python_exe, script_path],
            creationflags=creation_flags,
            cwd=self.current_dir
        )
        self.services[name] = proc

    def monitor_services(self):
        """Xizmatlar holatini kuzatish va kerak bo'lsa qayta yoqish"""
        while self.is_running:
            for name, proc in list(self.services.items()):
                if proc.poll() is not None:
                    self.logger.warning(f"⚠️ {name} to'xtab qoldi! Qayta ishga tushirilmoqda...")
                    # Re-launch the corresponding script
                    if name == "WebGateway": self.start_service(name, "jarvis_web.py")
                    elif name == "TelegramBot": self.start_service(name, "telegram_bot.py")
                    elif name == "Automation": self.start_service(name, "background_automation.py")
                    elif name == "UserBot": self.start_service(name, "telegram_user_bridge.py")
                    elif name == "Sentience": self.start_service(name, "sentience_engine.py")
            
            time.sleep(10)

    def run(self):
        self.logger.info("JARVIS Stealth Core faollashdi.")
        
        # 1. Start Web Gateway
        self.start_service("WebGateway", "jarvis_web.py")
        
        # 2. Start Telegram Bot (Official Bot)
        self.start_service("TelegramBot", "telegram_bot.py")
        
        # 3. Start Automation Worker
        self.start_service("Automation", "background_automation.py")
        
        # 4. Start Telegram User Assistant (Personal Account)
        self.start_service("UserBot", "telegram_user_bridge.py")
        
        # 5. Start Sentience Engine (Proactive AI)
        self.start_service("Sentience", "sentience_engine.py")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.is_running = False
        self.logger.info("Stealth Core to'xtatilmoqda...")
        for name, proc in self.services.items():
            proc.terminate()
        self.logger.info("Barcha fon xizmatlari o'chirildi.")

if __name__ == "__main__":
    core = JARVISStealthCore()
    core.run()
