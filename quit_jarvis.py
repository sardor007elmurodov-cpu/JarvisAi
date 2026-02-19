"""
Quick shutdown script for JARVIS
"""
import os
import sys
import psutil

print("🛑 JARVIS-ni uchirish...")

# Find and kill all JARVIS processes
killed = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = proc.info['cmdline']
        if cmdline:
            cmd_str = str(cmdline)
            targets = ['start.py', 'hud_main.py', 'jarvis_web.py', 'telegram_bot.py', 'repair_system.py']
            if any(t in cmd_str for t in targets):
                print(f"   Stopping PID {proc.info['pid']}: {proc.info['name']}")
                proc.kill() # Terminate is too soft, use kill
                killed = True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if killed:
    print("✅ JARVIS to'xtatildi")
else:
    print("⚠ JARVIS jarayoni topilmadi")

sys.exit(0)
