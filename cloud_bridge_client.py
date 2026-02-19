"""
JARVIS - Cloud Bridge Client
Mahalliy kompyuterda ishlaydi va Bulutdagi (Cloud Relay) serverdan buyruqlarni kutadi.
Bu "Reverse Shell" kabi ishlaydi, ya'ni firewall (NAT) muammosini hal qiladi.
"""
import requests
import time
import subprocess
import os
import json
from utils import setup_logger

from config import CLOUD_SERVER_URL

class CloudBridge:
    def __init__(self, server_url=None):
        self.logger = setup_logger("CloudBridge")
        self.server_url = server_url if server_url else CLOUD_SERVER_URL
        self.active = False

    def start_polling(self):
        """Serverdan buyruqlarni tekshirishni boshlash"""
        self.active = True
        self.logger.info(f"Connecting to Cloud Relay at {self.server_url}...")
        
        while self.active:
            try:
                # 1. Buyruqni olish
                response = requests.get(f"{self.server_url}/get", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    cmd = data.get("command")
                    
                    if cmd:
                        self.logger.info(f"Cloud Command Received: {cmd}")
                        result = self._execute_command(cmd)
                        # Natijani qaytarish (ixtiyoriy, agar server qo'llab-quvvatlasa)
                        # requests.post(f"{self.server_url}/result", json={"result": result})
                
            except Exception as e:
                # Serverga ulanishda xatolik bo'lsa, biroz kutamiz
                time.sleep(5)
            
            time.sleep(2) # 2 soniya interval

    def stop(self):
        self.active = False

    def _execute_command(self, cmd):
        """Buyruqni bajarish (Elite Local Executor)"""
        try:
            from executor import WindowsExecutor
            if not hasattr(self, 'executor'):
                self.executor = WindowsExecutor()

            self.logger.info(f"Executing cloud command: {cmd}")
            
            # 1. Research Result Handling
            if cmd.startswith("research_result:"):
                result_data = cmd.replace("research_result:", "")
                # Automate Word export locally
                from background_automation import BackgroundAutomation
                auto = BackgroundAutomation()
                auto.start_word_task(result_data, visible=True)
                return "✅ Research results exported to Word locally."

            # 2. Native JARVIS Commands (Parsing required)
            from parser import JARVISParser
            parser = JARVISParser()
            action_dict = parser.parse(cmd)
            
            if action_dict and action_dict.get("action") != "unknown":
                result = self.executor.execute(action_dict)
                return f"Success: {result}"
            
            # 3. Fallback to Shell
            if cmd.startswith("cmd:"):
                os_cmd = cmd.split("cmd:", 1)[1].strip()
                output = subprocess.check_output(os_cmd, shell=True).decode()
                return output
                
            return "Unknown command format"
                
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return f"Error: {e}"

if __name__ == "__main__":
    from config import CLOUD_SERVER_URL
    bridge = CloudBridge(CLOUD_SERVER_URL)
    bridge.start_polling()
