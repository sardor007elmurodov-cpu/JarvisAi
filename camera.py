"""
JARVIS Camera and Screen Capture Module
Kamera va ekran yozish
"""

import cv2
import numpy as np
import threading
import time
from datetime import datetime
import mss
import os


class CameraCapture:
    """Kamera va ekran capture"""
    
    def __init__(self):
        self.is_camera_running = False
        self.is_screen_recording = False
        self.camera_thread = None
        self.screen_thread = None
        self.current_frame = None  # Shared frame for HUD and other modules
        self.lock = threading.Lock()
        
        # Output directory
        self.output_dir = "recordings"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def start_camera(self, show_window=False):
        """
        Kamerani boshlash
        Args:
            show_window: True = oyna ko'rsatish, False = background'da ishlash
        """
        if self.is_camera_running:
            print("Kamera allaqachon ishlamoqda")
            return
        
        self.is_camera_running = True
        self.show_camera_window = show_window
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()
        print("✅ Kamera boshlandi (background mode)" if not show_window else "✅ Kamera boshlandi")
    
    def _camera_loop(self):
        """Kamera loop"""
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("⚠ Kamera topilmadi")
            self.is_camera_running = False
            return
        
        while self.is_camera_running:
            ret, frame = self.camera.read()
            if not ret:
                break
            
            # Store frame for external access
            with self.lock:
                self.current_frame = frame.copy()
            
            # Only show window if requested
            if self.show_camera_window:
                # Mirror effect
                frame = cv2.flip(frame, 1)
                
                # Status text
                cv2.putText(frame, "JARVIS Camera", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Display
                cv2.imshow("JARVIS Camera", frame)
                
                # Quit on 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop_camera()
                    break
            else:
                # Background mode - just keep capture alive for other uses
                cv2.waitKey(1)  # Small delay
        
        self.camera.release()
        with self.lock:
            self.current_frame = None
        if self.show_camera_window:
            cv2.destroyWindow("JARVIS Camera")
    
    def get_latest_frame(self):
        """Latest captured frame'ni olish"""
        with self.lock:
            return self.current_frame if self.current_frame is not None else None
    
    def stop_camera(self):
        """Kamerani to'xtatish"""
        self.is_camera_running = False
        if self.camera_thread:
            self.camera_thread.join(timeout=2)
        print("✅ Kamera to'xtatildi")
    
    def start_screen_recording(self, duration=30):
        """
        Ekran yozishni boshlash
        
        Args:
            duration: Yozish davomiyligi (sekundlarda), default 30s
        """
        if self.is_screen_recording:
            print("Ekran yozish allaqachon boshqarilyapti")
            return
        
        self.is_screen_recording = True
        self.screen_thread = threading.Thread(
            target=self._screen_recording_loop, 
            args=(duration,),
            daemon=True
        )
        self.screen_thread.start()
        print(f"✅ Ekran yozish boshlandi ({duration}s)")
    
    def _screen_recording_loop(self, duration):
        """Screen recording loop"""
        # Output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"screen_{timestamp}.avi")
        
        # Screen capture
        with mss.mss() as sct:
            # Monitor info
            monitor = sct.monitors[1]  # Primary monitor
            width = monitor["width"]
            height = monitor["height"]
            
            # Video writer
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_file, fourcc, 20.0, (width, height))
            
            start_time = time.time()
            frame_count = 0
            
            print(f"📹 Yozilmoqda: {output_file}")
            
            while self.is_screen_recording:
                # Time check
                if time.time() - start_time > duration:
                    break
                
                # Capture screen
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                
                # Convert BGRA to BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Write frame
                out.write(frame)
                frame_count += 1
                
                # Small delay
                time.sleep(0.05)  # ~20 FPS
            
            out.release()
            self.is_screen_recording = False
            
            print(f"✅ Ekran yozish tugadi: {output_file}")
            print(f"   Frames: {frame_count}, Duration: {frame_count/20:.1f}s")
    
    def stop_screen_recording(self):
        """Ekran yozishni to'xtatish"""
        self.is_screen_recording = False
        if self.screen_thread:
            self.screen_thread.join(timeout=3)
        print("✅ Ekran yozish to'xtatildi")
    
    def stop_all(self):
        """Hammani to'xtatish"""
        self.stop_camera()
        self.stop_screen_recording()
        print("✅ Barcha capture'lar to'xtatildi")


# Test
if __name__ == "__main__":
    cam = CameraCapture()
    
    print("1. Kamerani boshlash")
    cam.start_camera()
    
    print("\n2. 10 soniya kutish...")
    time.sleep(10)
    
    print("\n3. Ekran yozish (5s)")
    cam.start_screen_recording(duration=5)
    
    print("\n4. Screen recording'ni kutish...")
    time.sleep(6)
    
    print("\n5. Hammani to'xtatish")
    cam.stop_all()
    
    print("\n✅ Test tugadi")
