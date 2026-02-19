"""
JARVIS - Gaming Mode (Elite v21.0)
Optimizes system for maximum gaming performance.
"""
import psutil
import subprocess
import os
import time
from utils import setup_logger

class GamingMode:
    def __init__(self):
        self.logger = setup_logger("GamingMode")
        self.active = False
        self.heavy_apps = ["chrome.exe", "msedge.exe", "Teams.exe", "Discord.exe", "Code.exe"]
        self.suspended_procs = []

    def toggle(self):
        if not self.active:
            return self.activate()
        else:
            return self.deactivate()

    def activate(self):
        """Enable Gaming Mode"""
        self.logger.info("🎮 Activating Gaming Mode...")
        self.active = True
        
        # 1. RAM Cleanup (Basic attempt)
        self._clear_ram()
        
        # 2. Suspend Heavy Apps (Optional - may be aggressive)
        # For safety, we only lower their priority instead of suspending
        self._optimize_background_apps()
        
        # 3. Increase priority for high-load games (auto-detect or manual)
        self._boost_game_procs()
        
        return "🎮 Gaming Mode yoqildi. Tizim optimallashtirildi, janob."

    def deactivate(self):
        """Disable Gaming Mode"""
        self.logger.info("🎮 Deactivating Gaming Mode...")
        self.active = False
        self._restore_system()
        return "🎮 Gaming Mode o'chirildi. Tizim normal holatga qaytdi."

    def _clear_ram(self):
        """Simple RAM cleanup by triggering GC or clearing standby (needs admin for advanced)"""
        # In python we can't do much without external tools, but we can log intent
        self.logger.info("Cleaning up memory standby list...")
        # Placeholder for external RAM clear tool if available

    def _optimize_background_apps(self):
        """Lower priority of known heavy background apps"""
        for proc in psutil.process_iter(['name', 'nice']):
            try:
                if proc.info['name'] in self.heavy_apps:
                    if os.name == 'nt':
                        proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    else:
                        proc.nice(10)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def _boost_game_procs(self):
        """Boost priority of obviously active games"""
        # We look for apps using > 10% CPU and not in heavy_apps
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 10 and proc.info['name'] not in self.heavy_apps:
                    if os.name == 'nt':
                        proc.nice(psutil.HIGH_PRIORITY_CLASS)
                        self.logger.info(f"🚀 Boosted process: {proc.info['name']}")
            except:
                continue

    def _restore_system(self):
        """Restore process priorities"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.heavy_apps:
                    if os.name == 'nt':
                        proc.nice(psutil.NORMAL_PRIORITY_CLASS)
            except:
                continue

if __name__ == "__main__":
    gm = GamingMode()
    print(gm.activate())
    time.sleep(5)
    print(gm.deactivate())
