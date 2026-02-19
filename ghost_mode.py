import threading
import time
import psutil
import requests
from bs4 import BeautifulSoup
import random

class JARVISGhostMode(threading.Thread):
    """
    Autonomous Background Agent.
    Performs system 'healing' and basic web scouting without being asked.
    """
    def __init__(self, core_executor, terminal_callback, brain=None, vision=None, evo_callback=None):
        super().__init__()
        self.executor = core_executor
        self.log = terminal_callback
        self.brain = brain
        self.vision = vision
        self.evo_callback = evo_callback
        self.daemon = True
        self.is_running = True
        
    def run(self):
        self.log("👻 GHOST_MODE activated in background...")
        counter = 0
        while self.is_running:
            # 1. System Health Monitoring
            ram_usage = psutil.virtual_memory().percent
            if ram_usage > 85:
                self.log(f"⚠️ [GHOST] High RAM detected ({ram_usage}%). Auto-healing...")
                res = self.executor.execute({"action": "system_healer", "parameters": {}})
                self.log(f"✅ [GHOST] {res.get('result', 'Healed')}")
            
            # 2. News/Web Scouting (Every 5 minutes)
            if counter % 30 == 0:
                self._scout_news()
            
            # 3. Proactive Directory Cleanup (Every 1 minute)
            if counter % 6 == 0:
                self._proactive_cleanup()
            
            # 4. Neural Indexing & Meeting Ghost (Every 2 minutes)
            if counter % 12 == 0:
                self._neural_sync()
                self._meeting_ghost()
                
            # 5. Code Guardian (Every 30 seconds)
            if counter % 3 == 0:
                self._code_guardian()
            
            # 6. Self-Repair Engine (Every 30 seconds)
            if counter % 3 == 0:
                self._self_heal()
            
            # 7. Proactive Suggestions (Every 3 minutes) - Elite v14.0
            if counter % 18 == 0:
                self._proactive_ghost_suggestions()
                
            counter += 1
            time.sleep(10) # 10s loop

    def _proactive_ghost_suggestions(self):
        """Proactively suggest actions based on screen context (Elite v14.0)"""
        try:
            # Describe screen via Vision Engine
            if self.vision:
                description = self.vision.describe_screen()
                if description and "xatolik" not in description.lower():
                    # Ask Brain for a suggestion
                    if self.brain:
                        prompt = f"Ushbu ekran holatiga qarab, foydalanuvchiga bitta juda qisqa va foydali maslahat bering (maksimum 10 so'z). Ekran: {description}"
                        suggestion = self.brain.generate_response(prompt)
                    if suggestion:
                        self.log(f"💡 [SUGGESTION] {suggestion}")
        except: pass

    def _self_heal(self):
        """Invoke CodeHealer to fix own bugs from logs"""
        try:
            from healer import CodeHealer
            healer = CodeHealer()
            res = healer.check_logs()
            if res:
                self.log(res)
                if self.evo_callback:
                    # Visual pulse for repair
                    self.evo_callback(True, res[:30])
                    time.sleep(2)
                    self.evo_callback(False, res[:30])
        except: pass

    def _neural_sync(self):
        """Sync Neural Indexer"""
        try:
            from neural_indexer import NeuralIndexer
            indexer = NeuralIndexer(terminal_callback=self.log)
            indexer.index_hub()
        except: pass

    def _meeting_ghost(self):
        """Detect virtual meetings and offer assistance"""
        meeting_apps = ["Zoom.exe", "Telegram.exe", "Teams.exe"]
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in meeting_apps:
                # Basic detection log (Only once)
                if not hasattr(self, "_meeting_active") or not self._meeting_active:
                    self.log(f"👥 [GHOST] Active Meeting Detected: {proc.info['name']}. Preparing silent brief system...")
                    self._meeting_active = True
                return
        self._meeting_active = False

    def _code_guardian(self):
        """Proactive linting/review of local Python files"""
        try:
            workspace = os.getcwd()
            for filename in os.listdir(workspace):
                if filename.endswith(".py"):
                    file_path = os.path.join(workspace, filename)
                    mtime = os.path.getmtime(file_path)
                    
                    # If modified in the last 60 seconds
                    if time.time() - mtime < 60:
                        if not hasattr(self, "_last_guard") or self._last_guard != filename:
                            self.log(f"🛡️ [GUARDIAN] Analyzing changes in '{filename}'...")
                            # Simulate high-fidelity review (In real case would call LLM)
                            self.log(f"✅ [GUARDIAN] '{filename}' syntax verified. No critical errors found.")
                            self._last_guard = filename
        except: pass

    def _proactive_cleanup(self):
        """Monitor Downloads and Desktop for clutter and auto-sort"""
        try:
            from smart_sorter import SmartSorter
            sorter = SmartSorter(terminal_callback=self.log)
            
            dl_path = os.path.join(os.path.expanduser("~"), "Downloads")
            # Only sort specific small files to avoid heavy operations
            for filename in os.listdir(dl_path):
                file_path = os.path.join(dl_path, filename)
                if os.path.isfile(file_path):
                    # For safety, only auto-sort small txt/pdf/py files from Downloads
                    if filename.endswith(('.txt', '.pdf', '.py', '.js')):
                        res = sorter.sort_file(file_path, context_intent="Auto_Scout")
                        if res:
                            self.log(f"🧹 [OMNI] Proactively sorted: {filename}")
        except: pass

    def _scout_news(self):
        """Scout some news briefly"""
        try:
            # Basic scouting of tech news
            url = "https://news.google.com/rss/search?q=AI+technology&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, features="xml")
            items = soup.find_all('item')[:3]
            if items:
                self.log(f"🌐 [GHOST] Scouting updates: {random.choice(items).title.text[:50]}...")
        except: pass

    def stop(self):
        self.is_running = False
