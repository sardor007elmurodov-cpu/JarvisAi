"""
JARVIS - Night Owl (Autonomous Researcher)
Tungi vaqtda mustaqil tadqiqot olib borish.
"""
import time
import threading
import json
import os
from datetime import datetime
from research_assistant import ResearchAssistant
from utils import setup_logger

class NightOwl:
    def __init__(self, research_module=None):
        self.logger = setup_logger("NightOwl")
        self.research = research_module or ResearchAssistant()
        self.running = False
        self.thread = None
        
        self.queue_file = os.path.join(os.getcwd(), "data", "research_queue.json")
        self.reports_dir = os.path.join(os.getcwd(), "research", "night_reports")
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
            
        self.queue = self._load_queue()

    def _load_queue(self):
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_queue(self):
        with open(self.queue_file, "w") as f:
            json.dump(self.queue, f)

    def add_topic(self, topic):
        """Tadqiqot mavzusini navbatga qo'shish"""
        if topic not in self.queue:
            self.queue.append(topic)
            self._save_queue()
            return f"'{topic}' mavzusi tungi tadqiqotlar ro'yxatiga qo'shildi."
        return "Bu mavzu allaqachon ro'yxatda bor."

    def start_autonomous_mode(self):
        """Avtonom rejimni ishga tushirish"""
        if self.running: return "Night Owl allaqachon ishlamoqda."
        self.running = True
        self.thread = threading.Thread(target=self._night_routine, daemon=True)
        self.thread.start()
        return "Night Owl rejimi yoqildi. Har tun soat 02:00 da tadqiqotlar boshlanadi."

    def stop_autonomous_mode(self):
        self.running = False
        return "Night Owl rejimi to'xtatildi."

    def _night_routine(self):
        self.logger.info("Night Owl loop started")
        while self.running:
            now = datetime.now()
            # Tungi soat 02:00 dan 05:00 gacha tekshirish
            if 2 <= now.hour < 5:
                if self.queue:
                    topic = self.queue.pop(0)
                    self._save_queue()
                    
                    self.logger.info(f"Night Owl: Researching '{topic}'...")
                    result = self.research.perform_research(topic)
                    
                    if isinstance(result, dict):
                        # Redirect report to night folder
                        old_path = result['file']
                        filename = os.path.basename(old_path)
                        new_path = os.path.join(self.reports_dir, f"NIGHT_{filename}")
                        os.rename(old_path, new_path)
                        self.logger.info(f"Night Owl: Report saved to {new_path}")
                
                # Wait 30 mins between topics to be gentle
                time.sleep(1800)
            else:
                # Check every 10 minutes if it's night time
                time.sleep(600)

if __name__ == "__main__":
    # Test
    owl = NightOwl()
    print(owl.add_topic("Quantum Computing trends 2025"))
    print("Test rejimida ishga tushirildi (real vaqtni kutmaydi)...")
    owl.start_autonomous_mode()
    time.sleep(2)
    owl.stop_autonomous_mode()
