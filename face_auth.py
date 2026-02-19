import cv2
import os
import numpy as np

class FaceAuth:
    """
    JARVIS - Face ID Authentication Module
    Uses OpenCV LBPH for secure identity verification.
    """
    def __init__(self):
        self.cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.data_path = os.path.join(os.getcwd(), "data", "faces")
        self.model_path = os.path.join(self.data_path, "face_model.yml")
        
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            
        self._load_model()

    def get_emotion(self, face_roi):
        """Analyze face ROI for simple emotions (HAPPY/NEUTRAL)"""
        if face_roi is None or face_roi.size == 0:
            return "NEUTRAL"
        
        # Smile detection
        smiles = self.smile_cascade.detectMultiScale(face_roi, 1.7, 22)
        if len(smiles) > 0:
            return "HAPPY"
        return "NEUTRAL"

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.recognizer.read(self.model_path)
            self.model_loaded = True
        else:
            self.model_loaded = False

    def capture_training_data(self, video_capture):
        """Yuzni ro'yxatdan o'tkazish (Training)"""
        print("👤 Face ID: Ro'yxatdan o'tkazish boshlandi. Kameraga qarab turing...")
        count = 0
        samples = []
        ids = []
        
        while count < 30: # 30 ta rasm yetarli
            ret, frame = video_capture.read()
            if not ret: break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                count += 1
                face_roi = gray[y:y+h, x:x+w]
                samples.append(face_roi)
                ids.append(1) # JARVIS User ID = 1
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.imshow("Face ID Registration", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            
        if count >= 20:
            self.recognizer.train(samples, np.array(ids))
            self.recognizer.write(self.model_path)
            self.model_loaded = True
            print("✅ Face ID: Muvaffaqiyatli ro'yxatdan o'tdingiz, Janob.")
        
        cv2.destroyAllWindows()

    def identify(self, frame):
        """Yuzni tanish va identifikatsiya qilish"""
        if not self.model_loaded:
            return False, 0
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
        return self.identify_with_faces(frame, faces)

    def identify_with_faces(self, frame, faces):
        """Oldindan aniqlangan yuzlar bilan identifikatsiya qilish (Tezroq)"""
        if not self.model_loaded or len(faces) == 0:
            return False, 0
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            label, confidence = self.recognizer.predict(face_roi)
            
            # LBPH confidence: lower is better. < 60 is usually a solid match
            if label == 1 and confidence < 65:
                return True, confidence
                
        return False, 100

    def verify_face(self, frame):
        """Quick verification for lock screen - returns True/False"""
        is_match, confidence = self.identify(frame)
        return is_match

    def detect_faces(self, frame):
        """Kadrda har qanday yuz borligini aniqlash"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return len(faces) > 0

if __name__ == "__main__":
    # Test
    auth = FaceAuth()
    print("FaceAuth initialized.")
