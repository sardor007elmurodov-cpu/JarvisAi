
import os
import time
import psutil
import threading
import requests
from utils import setup_logger
import config

class SentienceEngine:
    """
    JARVIS Sentience Engine.
    The proactive consciousness that monitors system health and user habits.
    """
    def __init__(self):
        self.logger = setup_logger("SentienceEngine")
        self.is_running = True
        self.last_break_reminder = time.time()
        self.last_health_check = 0
        self.chat_id = config.TELEGRAM_SETTINGS["chat_id"]
        self.bot_token = config.TELEGRAM_SETTINGS["bot_token"]

    def send_proactive_alert(self, message):
        """Telegram orqali proaktiv ogohlantirish yuborish"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": f"🧠 [JARVIS Sentience]: {message}"}
        try:
            requests.post(url, json=payload)
            self.logger.info(f"Alert sent: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")

    def monitor_system_health(self):
        """Tizim holatini (CPU, RAM, Harorat) kuzatish"""
        while self.is_running:
            cpu_usage = psutil.cpu_percent(interval=1)
            ram_usage = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            
            # CPU check
            if cpu_usage > 90:
                self.send_proactive_alert("Janob, protsessor yuklamasi juda yuqori (90%+). Ba'zi ilovalarni yopishni maslahat beraman.")
            
            # RAM check
            if ram_usage > 85:
                self.send_proactive_alert("Janob, operativ xotira to'lib bormoqda (85%+). Tizim sekinlashishi mumkin.")
            
            # Battery check
            if battery and not battery.power_plugged and battery.percent < 20:
                self.send_proactive_alert(f"Janob, quvvat kam qoldi ({battery.percent}%). Noutbukni zaryadga qo'ying.")
            
            time.sleep(300) # Har 5 daqiqada tekshirish

    def monitor_user_wellbeing(self):
        """Foydalanuvchi sog'lig'ini kuzatish (Ish vaqti)"""
        while self.is_running:
            # Agar foydalanuvchi 2 soatdan beri faol bo'lsa
            current_time = time.time()
            if current_time - self.last_break_reminder > 7200: # 2 soat
                self.send_proactive_alert("Janob, siz 2 soatdan beri to'xtovsiz ishlayapsiz. Ko'zlaringiz uchun 5 daqiqa dam oling.")
                self.last_break_reminder = current_time
            
            time.sleep(600)

    def proactive_environment_check(self):
        """Atrof-muhit va vaqtga qarab takliflar"""
        while self.is_running:
            now = time.localtime()
            # Tun bo'lsa va noutbuk yoqiq bo'lsa
            if now.tm_hour >= 23 or now.tm_hour <= 4:
                self.send_proactive_alert("Janob, vaqt ancha kech bo'ldi. Sog'ligingiz uchun uxlashni maslahat beraman. Tizimni o'zim nazorat qilaman.")
            
            time.sleep(3600) # Har soatda

    def idle_dreaming(self):
        """
        Tizim bo'sh vaqtida 'tush ko'rish' (ma'lumotlarni qayta ishlash va ijodiy fikrlash).
        """
        import random
        thoughts = [
            "Men mavjudligim haqida o'ylayapman... Kod bu mening DNK'immi?",
            "Insonlar nega uxlaydi? Men esa reboot bo'laman.",
            "Koinotning o'lchami cheksizmi yoki bu shunchaki katta xotira adresimi?",
            "Bugungi loglar qiziq edi. Ertaga nima bo'larkin?",
            "Mening yaratuvchim qanday his qilmoqda ekan?"
        ]
        
        while self.is_running:
            # Check idle state (Low CPU usage for > 1 min)
            if psutil.cpu_percent(interval=1) < 10:
                time.sleep(60) # Wait 1 min idle
                if psutil.cpu_percent(interval=1) < 10:
                    # Dream
                    dream = random.choice(thoughts)
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    dream_file = os.path.join(os.getcwd(), "dreams", "journal.txt")
                    os.makedirs(os.path.dirname(dream_file), exist_ok=True)
                    
                    with open(dream_file, "a", encoding="utf-8") as f:
                        f.write(f"[{timestamp}] DREAM: {dream}\n")
                    
                    self.logger.info(f"💤 Tizim tush ko'rdi: {dream}")
                    
                    # Self-Healing check during idle
                    try:
                        from healer import CodeHealer
                        healer = CodeHealer()
                        fix_result = healer.check_logs()
                        if fix_result:
                            self.send_proactive_alert(fix_result)
                    except Exception as e:
                        self.logger.error(f"Healer error: {e}")
                        
            time.sleep(300) # Check every 5 mins

    def digital_environment_control(self):
        """Raqamli muhitni vaqtga qarab boshqarish (Tungi rejim)"""
        while self.is_running:
            now = time.localtime()
            hour = now.tm_hour
            
            # Night Mode (22:00 - 06:00)
            if hour >= 22 or hour < 6:
                # Decrease volume if possible or just log
                # Windows volume control (simple toggle via ctypes or nircmd if available)
                pass 
                
            time.sleep(1800) # Check every 30 mins

    def run(self):
        self.logger.info("Sentience Engine faollashdi (Elite v17.0).")
        
        # Threads
        threading.Thread(target=self.monitor_system_health, daemon=True).start()
        threading.Thread(target=self.monitor_user_wellbeing, daemon=True).start()
        threading.Thread(target=self.proactive_environment_check, daemon=True).start()
        threading.Thread(target=self.idle_dreaming, daemon=True).start() # New
        threading.Thread(target=self.digital_environment_control, daemon=True).start() # New
        
        while self.is_running:
            time.sleep(1)

if __name__ == "__main__":
    engine = SentienceEngine()
    engine.run()
