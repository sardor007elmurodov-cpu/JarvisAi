"""
JARVIS - Visual Avatar HUD
Futuristik pulsing animatsiya.
"""
import tkinter as tk
import threading
import time
import math

class VisualAvatar:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.running = False
        self.thread = None
        self.pulse_active = False

    def _create_window(self):
        self.root = tk.Tk()
        self.root.title("JARVIS CORE")
        self.root.geometry("300x300+100+100")
        self.root.overrideredirect(True) # Title bar-ni olib tashlash
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")
        
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        self._animate()
        self.root.mainloop()

    def _animate(self):
        if not self.running:
            return
            
        self.canvas.delete("all")
        
        # Markaziy nuqta
        cx, cy = 150, 150
        
        # Pulsatsiya mantiqi
        t = time.time()
        pulse_scale = 1.0 + (0.1 * math.sin(t * 5))
        if self.pulse_active:
            pulse_scale = 1.2 + (0.3 * math.sin(t * 15))
            
        # Tashqi halqa
        r1 = 80 * pulse_scale
        self.canvas.create_oval(cx-r1, cy-r1, cx+r1, cy+r1, outline="#00d2ff", width=2)
        
        # Ichki halqa
        r2 = 50 * pulse_scale
        self.canvas.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, outline="#00d2ff", width=4)
        
        # Markaziy yadro
        r3 = 20 * (1.1 if self.pulse_active else 1.0)
        self.canvas.create_oval(cx-r3, cy-r3, cx+r3, cy+r3, fill="#00d2ff")
        
        # Neon effekt uchun yorug'lik
        self.canvas.create_oval(cx-r3-5, cy-r3-5, cx+r3+5, cy+r3+5, outline="#00d2ff", width=1)

        self.root.after(30, self._animate)

    def start(self):
        """Avatarni ishga tushirish"""
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._create_window, daemon=True)
        self.thread.start()

    def set_pulse(self, active):
        """Pulsatsiyani yoqish/o'chirish (gapirganda)"""
        self.pulse_active = active

    def stop(self):
        """To'xtatish"""
        self.running = False
        if self.root:
            self.root.quit()

if __name__ == "__main__":
    # Test
    avatar = VisualAvatar()
    avatar.start()
    time.sleep(2)
    print("Gapirish boshlandi...")
    avatar.set_pulse(True)
    time.sleep(3)
    print("Gapirish tugadi...")
    avatar.set_pulse(False)
    time.sleep(5)
    avatar.stop()
