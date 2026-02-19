import time
import math
import ctypes
import threading
import os
import config

# Windows Mouse Control
mouse_event = ctypes.windll.user32.mouse_event
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

def move_mouse(x, y, sw, sh):
    nx = int(x * 65535 / sw)
    ny = int(y * 65535 / sh)
    mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0)

def left_click():
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def right_click():
    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

class HandGestureControl:
    """
    MODERN MEDIAPIPE TASKS IMPLEMENTATION
    Uses mediapipe.tasks.vision for better performance and Python 3.12 compatibility.
    """
    def __init__(self):
        try:
            import cv2
            import numpy as np
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            self.cv2 = cv2
            self.np = np
            self.mp = mp
            
            # Load Hand Landmarker
            model_path = os.path.join(os.getcwd(), 'hand_landmarker.task')
            if not os.path.exists(model_path):
                # Fallback path
                model_path = 'hand_landmarker.task'
            
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=0.7,
                min_hand_presence_confidence=0.7,
                min_tracking_confidence=0.7
            )
            self.landmarker = vision.HandLandmarker.create_from_options(options)
            
            self.available = True
            print("✅ JARVIS Logic: Gesture System Online (Modern Tasks Mode)")
        except Exception as e:
            print(f"⚠ Gesture Init Error: {e}")
            self.available = False
            
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Smoothing settings
        self.clocX, self.clocY = 0, 0
        self.plocX, self.plocY = 0, 0
        self.last_results = None
        self.skip_frames = 1 # Process every 2nd frame for better response
        self.smooth_factor = 5 # Faster response
        # Click state
        self.last_click_time = 0
        self.frame_count = 0 
        self.is_running = True
        self.skip_frames = 2 # Process every 3rd frame

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def process_frame(self, frame):
        if not self.available or not self.is_running:
            return frame
            
        h, w, c = frame.shape
        
        # Visual Status
        self.cv2.putText(frame, "GESTURE: ACTIVE (Optimized)", (10, 25), 
                    self.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, self.cv2.LINE_AA)
        
        self.frame_count += 1
        if self.frame_count % (self.skip_frames + 1) != 0:
            return frame

        # Resize for faster processing
        small_frame = self.cv2.resize(frame, (640, 480))
        rgb_frame = self.cv2.cvtColor(small_frame, self.cv2.COLOR_BGR2RGB)
        mp_image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb_frame)
        
        timestamp_ms = int(time.time() * 1000)
        try:
            results = self.landmarker.detect_for_video(mp_image, timestamp_ms)
            
            if results.hand_landmarks:
                config.SENTINEL_MODE["last_activity"] = time.time()
                
                for hand_landmarks in results.hand_landmarks:
                    # Draw simple landmarks
                    for landmark in hand_landmarks:
                        px, py = int(landmark.x * w), int(landmark.y * h)
                        self.cv2.circle(frame, (px, py), 2, (0, 255, 0), -1)
                    
                    # Landmarks: 8 is Index tip, 4 is Thumb tip, 12 is Middle tip
                    lm8 = hand_landmarks[8]
                    lm4 = hand_landmarks[4]
                    lm12 = hand_landmarks[12]
                    
                    x1, y1 = int(lm8.x * w), int(lm8.y * h)
                    x2, y2 = int(lm12.x * w), int(lm12.y * h)
                    x3, y3 = int(lm4.x * w), int(lm4.y * h)
                    
                    # Movement Box
                    margin = 120
                    self.cv2.rectangle(frame, (margin, margin), (w - margin, h - margin), (0, 255, 255), 2)
                    
                    move_x = self.np.interp(x1, (margin, w - margin), (0, self.screen_width))
                    move_y = self.np.interp(y1, (margin, h - margin), (0, self.screen_height))
                    
                    # Smoothing
                    self.clocX = self.plocX + (move_x - self.plocX) / self.smooth_factor
                    self.clocY = self.plocY + (move_y - self.plocY) / self.smooth_factor
                    
                    move_mouse(self.clocX, self.clocY, self.screen_width, self.screen_height)
                    self.plocX, self.plocY = self.clocX, self.clocY
                    
                    # --- CLICK LOGIC ---
                    # 1. Left Click: Index + Thumb pinch
                    dist_left = math.hypot(lm8.x - lm4.x, lm8.y - lm4.y) * 1000 # Normalized scale
                    if dist_left < 50:
                        if time.time() - self.last_click_time > 0.4:
                            self.cv2.circle(frame, (x1, y1), 20, (0, 255, 0), self.cv2.FILLED)
                            left_click()
                            self.last_click_time = time.time()
                            print("DEBUG: Left Click detected")

                    # 2. Right Click: Middle + Thumb pinch
                    dist_right = math.hypot(lm12.x - lm4.x, lm12.y - lm4.y) * 1000
                    if dist_right < 50:
                        if time.time() - self.last_click_time > 0.4:
                            self.cv2.circle(frame, (x2, y2), 20, (0, 0, 255), self.cv2.FILLED)
                            right_click()
                            self.last_click_time = time.time()
                            print("DEBUG: Right Click detected")
                            
        except Exception as e:
            print(f"JARVIS Gesture Error: {e}")
            pass
            
        return frame

if __name__ == "__main__":
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(0)
    gesture = HandGestureControl()
    while True:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        frame = gesture.process_frame(frame)
        cv2.imshow("JARVIS Gesture Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
