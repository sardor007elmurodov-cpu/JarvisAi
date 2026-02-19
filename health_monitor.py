"""
JARVIS - Health & Posture Monitor (OpenCV Edition)
Foydalanuvchining gavda holatini OpenCV Haar Cascades orqali kuzatish.
Mediapipe-siz ishlaydi.
"""
import cv2
import threading
import time
import os
from utils import setup_logger

class HealthMonitor:
    def __init__(self, voice_module=None):
        self.logger = setup_logger("HealthMonitor")
        self.voice = voice_module
        
        # Haar Cascade yuklash
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Monitoring holati
        self.is_running = False
        self.thread = None
        self.last_alert_time = 0
        self.alert_cooldown = 300 # 5 daqiqa
        
        # Kalibratsiya ma'lumotlari
        self.base_y = None
        self.base_h = None
        self.slouch_counter = 0

    def check_posture(self, frame):
        """Kadrda yuz holatini tahlil qilish"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return "NO_PERSON"

        # Eng katta yuzni olish
        (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        
        # Birinchi marta kalibratsiya qilish
        if self.base_y is None:
            self.base_y = y
            self.base_h = h
            return "CALIBRATING"

        # Sodda tahlil:
        # 1. Boshning pastga tushishi (y koordinatasi ortadi)
        # 2. Boshning oldinga egilishi (yuz kattalashadi, h ortadi)
        
        y_diff = y - self.base_y
        h_diff = h - self.base_h
        
        # Agar bosh sezilarli pastga tushsa yoki juda kattalashsa (oldinga egilsa)
        if y_diff > 40 or h_diff > 30:
            self.slouch_counter += 1
            if self.slouch_counter > 50: # ~2-3 soniya
                return "SLOUCHING"
        else:
            self.slouch_counter = 0
            # Sekin moslashish (kalibratsiyani yangilab turish)
            self.base_y = int(self.base_y * 0.95 + y * 0.05)
            self.base_h = int(self.base_h * 0.95 + h * 0.05)
            
        return "GOOD"

    def _monitor_loop(self):
        """Monitoring davri"""
        cap = cv2.VideoCapture(0)
        self.logger.info("Posture monitoring started (Haar Cascades)")
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret: break
                
            status = self.check_posture(frame)
            
            if status == "SLOUCHING":
                current_time = time.time()
                if current_time - self.last_alert_time > self.alert_cooldown:
                    self.logger.warning("USER SLOUCHING DETECTED")
                    if self.voice:
                        self.voice.speak("Janob, biroz bukchayib qoldingiz. Gavdangizni tik tuting, sog'lig'ingiz uchun foydali.")
                    self.last_alert_time = current_time
            
            time.sleep(0.05)
            
        cap.release()
        self.logger.info("Posture monitoring stopped")

    def start_monitoring(self):
        """Monitoringni boshlash"""
        if not self.is_running:
            self.base_y = None # Reset calibration
            self.is_running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            return "Sog'liq monitoringi yoqildi, janob. Iltimos, gavdangizni tik tutib 1-2 soniya turing."
        return "Monitoring allaqachon ishlamoqda."

    def stop_monitoring(self):
        """Monitoringni to'xtatish"""
        self.is_running = False
        return "Sog'liq monitoringi to'xtatildi."

if __name__ == "__main__":
    monitor = HealthMonitor()
    print("Monitoring boshlanmoqda...")
    monitor.start_monitoring()
    time.sleep(10)
    monitor.stop_monitoring()
    print("Tayyor.")
