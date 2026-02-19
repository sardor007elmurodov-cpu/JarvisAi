"""
JARVIS - Elite Automation Engine
Handles complex scheduling, protocols, and conditional triggers.
"""

import time
import threading
import json
import os
from datetime import datetime, timedelta
from utils import setup_logger

class AutomationEngine:
    def __init__(self, core=None):
        self.logger = setup_logger("AutomationEngine")
        self.core = core
        self.tasks = []
        self.protocols = {
            "good_morning": [
                {"action": "speak", "params": {"text": "Xayrli tong, janob. Yangi kun muborak bo'lsin."}},
                {"action": "get_time", "params": {}},
                {"action": "open_website", "params": {"website_name": "kun.uz"}}
            ],
            "work_mode": [
                {"action": "open_app", "params": {"app_name": "chrome"}},
                {"action": "speak", "params": {"text": "Ish rejimi faollashtirildi. Muvaffaqiyatlar tilayman."}}
            ],
            "good_night": [
                {"action": "speak", "params": {"text": "Xayrli tun, janob. Tizim kutish rejimiga o'tmoqda."}},
                {"action": "close_app", "params": {"app_name": "chrome"}},
                {"action": "mute_volume", "params": {}}
            ]
        }
        self.is_running = False
        self._load_tasks()

    def _load_tasks(self):
        """Vazifalarni xotiradan yuklash (Hozircha oddiy ro'yxat)"""
        if os.path.exists("automation_tasks.json"):
            try:
                with open("automation_tasks.json", "r") as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []

    def _save_tasks(self):
        """Vazifalarni saqlash"""
        with open("automation_tasks.json", "w") as f:
            json.dump(self.tasks, f)

    def add_scheduled_task(self, time_str, action, params, repeat=True):
        """Jadval asosida vazifa (HH:MM)"""
        task = {
            "id": int(time.time()),
            "type": "scheduled",
            "time": time_str,
            "action": action,
            "params": params,
            "repeat": repeat,
            "done_today": False
        }
        self.tasks.append(task)
        self._save_tasks()
        self.logger.info(f"Task scheduled: {action} at {time_str}")

    def add_timer(self, minutes, action, params):
        """Taymer bo'yicha vazifa"""
        target_time = datetime.now() + timedelta(minutes=minutes)
        task = {
            "id": int(time.time()),
            "type": "timer",
            "trigger_at": target_time.isoformat(),
            "action": action,
            "params": params
        }
        self.tasks.append(task)
        self.logger.info(f"Timer set for {minutes} minutes: {action}")

    def execute_protocol(self, protocol_name, threaded=True):
        """Oldindan belgilangan protokollarni bajarish"""
        if threaded:
            threading.Thread(target=self._execute_protocol_logic, args=(protocol_name,), daemon=True).start()
        else:
            self._execute_protocol_logic(protocol_name)

    def _execute_protocol_logic(self, protocol_name):
        if protocol_name in self.protocols:
            self.logger.info(f"Executing protocol: {protocol_name}")
            for step in self.protocols[protocol_name]:
                if self.core:
                    self.core.execute_automation(step["action"], step["params"])
                time.sleep(1.5)
        else:
            self.logger.warning(f"Unknown protocol: {protocol_name}")

    def run_worker(self):
        """Backround worker loop"""
        self.is_running = True
        self.logger.info("Automation Worker started.")
        
        while self.is_running:
            now_dt = datetime.now()
            now_str = now_dt.strftime("%H:%M")
            
            to_remove = []
            
            for task in self.tasks:
                triggered = False
                
                if task["type"] == "scheduled":
                    if task["time"] == now_str and not task["done_today"]:
                        triggered = True
                        if not task["repeat"]:
                            to_remove.append(task)
                        else:
                            task["done_today"] = True
                
                elif task["type"] == "timer":
                    trigger_at = datetime.fromisoformat(task["trigger_at"])
                    if now_dt >= trigger_at:
                        triggered = True
                        to_remove.append(task)
                
                if triggered:
                    self.logger.info(f"Triggering {task['type']} task: {task['action']}")
                    if self.core:
                        if task["action"] == "protocol":
                            self.execute_protocol(task["params"].get("name"))
                        else:
                            self.core.execute_automation(task["action"], task["params"])
            
            # Tozalash
            for t in to_remove:
                if t in self.tasks:
                    self.tasks.remove(t)
            
            # Reset daily tasks
            if now_str == "00:00":
                for t in self.tasks:
                    if t.get("type") == "scheduled":
                        t["done_today"] = False
            
            time.sleep(15) # Checking frequency

    def start(self):
        t = threading.Thread(target=self.run_worker, daemon=True)
        t.start()

if __name__ == "__main__":
    # Test
    auto = AutomationEngine()
    print("Automation initialized.")
