import os
# Fix Qt DPI Awareness Access Denied
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTOSCREENSCALEFACTOR"] = "1"

import sys
import subprocess
import time
import psutil

def kill_existing(script_name):
    """Find and kill processes running a specific python script"""
    print(f"🧹 Checking for existing instances of {script_name}...")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and script_name in ' '.join(cmdline):
                # Don't kill ourself
                if proc.info['pid'] == os.getpid(): continue
                print(f"   ⚠️ Killing old instance (PID: {proc.info['pid']})")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def main():
    print("========================================")
    print("   J.A.R.V.I.S SYSTEM INITIALIZATION   ")
    print("========================================")
    
    # Pre-clean known conflicts
    kill_existing("telegram_bot.py")
    kill_existing("jarvis_web.py") # Usually harmless but good to clean
    # Do NOT kill HUD or Agent if running independently, but Bot is the main conflict source.
    
    # Environment Detection
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(current_dir, ".venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    
    print(f"🚀 Python interpreter: {python_exe}")
    
    # Load Config for Hybrid Mode check
    try:
        from config import HYBRID_MODE
    except ImportError:
        HYBRID_MODE = False

    # 1. Launch Web Gateway (Background)
    print("🌐 Starting Web Gateway...")
    web_proc = subprocess.Popen([python_exe, os.path.join(current_dir, "jarvis_web.py")], 
                                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
    
    if HYBRID_MODE:
        print("☁️  HYBRID MODE: Offloading brain to Cloud...")
        # Start Cloud Bridge Client (Executor)
        bridge_proc = subprocess.Popen([python_exe, os.path.join(current_dir, "cloud_bridge_client.py")],
                                      creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
    else:
        # 2. Launch Telegram Bot (Background)
        print("🤖 Starting Telegram Bot...")
        bot_proc = subprocess.Popen([python_exe, os.path.join(current_dir, "telegram_bot.py")], 
                                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
        
        # 3. Launch Sentience Engine (Background - Proactive Mind)
        print("🧠 Starting Sentience Engine...")
        sentience_proc = subprocess.Popen([python_exe, os.path.join(current_dir, "sentience_engine.py")],
                                          creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)

    time.sleep(2) # Give services a moment to warm up
    
    # 4. Launch Main HUD (Foreground - blocks until closed)
    print("🖥️  Launching JARVIS HUD...")
    try:
        subprocess.run([python_exe, os.path.join(current_dir, "hud_main.py")])
    except Exception as e:
        print(f"⚠ HUD Launch Error: {e}")
    finally:
        print("\n🖥️  HUD yopildi. Fon xizmatlari (Web/Telegram/Cloud) ishlashda davom etmoqda.")
        print("✅ Tizim fon rejimiga o'tdi.")
        time.sleep(1)

if __name__ == "__main__":
    main()
