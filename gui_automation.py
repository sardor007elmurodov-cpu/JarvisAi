"""
JARVIS - GUI Automation 2.0
Sichqoncha va klaviaturani professional darajada boshqarish.
PyAutoGUI kutubxonasini kuchaytiradi va barqarorlashtiradi.
"""
import pyautogui
import time
import os
import subprocess
from utils import setup_logger

# Fail-safe (sichqonchani burchakka olib borganda to'xtash)
pyautogui.FAILSAFE = True

class GUIController:
    def __init__(self):
        self.logger = setup_logger("GUIController")
        self.typing_speed = 0.05

    def type_text(self, text, interval=None):
        """Matn yozish (simulyatsiya)"""
        try:
            speed = interval if interval else self.typing_speed
            pyautogui.write(text, interval=speed)
            return f"'{text}' matni yozildi."
        except Exception as e:
            self.logger.error(f"Typing error: {e}")
            return "Yozishda xatolik yuz berdi."

    def press_hotkey(self, keys):
        """Klaviatura kombinatsiyasini bosish (masalan: ctrl, c)"""
        try:
            # keys: "ctrl+c" shaklida kelishi mumkin
            key_list = keys.split('+') if '+' in keys else [keys]
            pyautogui.hotkey(*key_list)
            return f"Klaviatura bosildi: {keys}"
        except Exception as e:
            self.logger.error(f"Hotkey error: {e}")
            return "Tugmalarni bosishda xatolik."

    def open_run_dialog(self, command):
        """Win+R orqali dastur ochish (Eng ishonchli usul)"""
        try:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            pyautogui.write(command)
            pyautogui.press('enter')
            return f"Run dialog orqali ochilmoqda: {command}"
        except Exception as e:
            self.logger.error(f"Run dialog error: {e}")
            return "Dasturni ochishda xatolik."

    def scroll(self, amount, direction="down"):
        """Sichqonchani aylantirish"""
        try:
            clicks = int(amount) if amount else 300
            if direction == "down":
                clicks = -clicks
            
            pyautogui.scroll(clicks)
            return f"{direction} tomonga {abs(clicks)} birlik aylantirildi."
        except Exception as e:
            return f"Scroll xatosi: {e}"

    def click_center(self):
        """Ekranning o'rtasiga bosish"""
        width, height = pyautogui.size()
        pyautogui.click(width/2, height/2)
        return "Ekran markaziga bosildi."

if __name__ == "__main__":
    gui = GUIController()
    # gui.open_run_dialog("notepad")
    # time.sleep(1)
    # gui.type_text("Salom, bu JARVIS!")
