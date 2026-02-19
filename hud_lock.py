from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QImage, QPixmap
from datetime import datetime
import cv2
import numpy as np

class HUDLockScreen(QWidget):
    """
    JARVIS Virtual Lock Screen
    Full-screen overlay with Face ID authentication and password fallback.
    """
    unlocked = pyqtSignal()

    def __init__(self, camera=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.camera_manager = camera
        self.init_ui()
        # Removed showFullScreen from init (now handled by showEvent or manual call)
        
        self.typed_pass = "" # Manual password buffer
        self.face_verified = False
        self.use_face_id = False  # Default to False
        self.camera_active = False  # Default to False
        self.face_auth = None
        
        # Face ID (Try to enable if available)
        try:
            from face_auth import FaceAuth
            import config
            if config.FACE_ID_SETTINGS.get("enabled", False):
                self.face_auth = FaceAuth()
                self.use_face_id = True
                self.start_face_verification()
        except Exception as e:
            print(f"⚠ Face ID not available: {e}")
            self.use_face_id = False
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update)
        self.anim_timer.start(50)

    def start_face_verification(self):
        """Monitor shared camera for face verification"""
        if self.camera_manager:
            self.camera_active = True
            self.face_timer = QTimer(self)
            self.face_timer.timeout.connect(self.check_face)
            self.face_timer.start(100)
        else:
            print("⚠ Lock Screen: No camera manager provided")
            self.camera_active = False

    def check_face(self):
        """Continuously check for authorized face using shared frame"""
        if not self.camera_active or not self.camera_manager:
            return
            
        frame = self.camera_manager.get_latest_frame()
        if frame is not None:
            # Check if face matches
            is_authorized = self.face_auth.verify_face(frame)
            
            if is_authorized:
                self.face_verified = True
                self.status.setText("FACE VERIFIED - ACCESS GRANTED")
                self.status.setStyleSheet("color: #00ff00; font-size: 24px; font-family: 'Consolas'; margin-top: 20px;")
                QTimer.singleShot(500, self.unlock)
            
            # Update camera preview
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera_preview.setPixmap(QPixmap.fromImage(q_img).scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio))

    def showEvent(self, event):
        self.typed_pass = "" # Reset buffer when showing
        if hasattr(self, 'face_verified'):
            self.face_verified = False
        if hasattr(self, 'use_face_id') and self.use_face_id and not self.camera_active:
            self.start_face_verification()
        super().showEvent(event)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("SYSTEM LOCKED\nBY JARVIS")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #00e0ff; font-size: 80px; font-weight: bold; font-family: 'Consolas';")
        
        self.status = QLabel("SENTINEL PROTOCOL ACTIVE")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: #ff3300; font-size: 24px; font-family: 'Consolas'; margin-top: 20px;")
        
        # Camera preview for Face ID
        self.camera_preview = QLabel("")
        self.camera_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_preview.setStyleSheet("border: 2px solid #00e0ff; margin-top: 20px;")
        self.camera_preview.setFixedSize(320, 240)
        
        # Password input display
        self.password_display = QLabel("")
        self.password_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_display.setStyleSheet("color: #00ff00; font-size: 32px; font-family: 'Consolas'; margin-top: 30px; letter-spacing: 5px;")
        
        self.hint_label = QLabel("Look at camera for Face ID or type password")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("color: #888888; font-size: 16px; font-family: 'Consolas'; margin-top: 10px;")
        
        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.camera_preview)
        layout.addWidget(self.password_display)
        layout.addWidget(self.hint_label)

    def keyPressEvent(self, event):
        # 1. Block Alt+F4, Esc, etc.
        if event.key() == Qt.Key.Key_F4 and (event.modifiers() & Qt.KeyboardModifier.AltModifier):
            event.ignore()
            return
        elif event.key() == Qt.Key.Key_Escape:
            event.ignore()
            return
        
        # 2. Handle Enter key - submit password
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.typed_pass == "Sardorbek009":
                self.unlock()
            else:
                # Wrong password - shake effect or clear
                self.typed_pass = ""
                self.password_display.setText("")
                self.status.setText("ACCESS DENIED")
                QTimer.singleShot(1000, lambda: self.status.setText("SENTINEL PROTOCOL ACTIVE"))
            return
        
        # 3. Handle Backspace
        if event.key() == Qt.Key.Key_Backspace:
            if self.typed_pass:
                self.typed_pass = self.typed_pass[:-1]
                self.password_display.setText("*" * len(self.typed_pass))
            return
            
        # 4. Capture manual password
        key_text = event.text()
        if key_text and key_text.isprintable():
            self.typed_pass += key_text
            # Keep only last 20 chars to avoid memory issues
            if len(self.typed_pass) > 20:
                self.typed_pass = self.typed_pass[-20:]
            
            # Update display
            self.password_display.setText("*" * len(self.typed_pass))
        
        super().keyPressEvent(event)

    def closeEvent(self, event):
        # Only allow closing if we are specifically calling unlock()
        if not hasattr(self, '_can_close') or not self._can_close:
            event.ignore()
        else:
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dark tech background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 5, 10, 240))
        gradient.setColorAt(1, QColor(0, 15, 30, 250))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        
        # Scanning line effect
        scan_y = (datetime.now().microsecond // 1000) % self.height()
        painter.setPen(QPen(QColor(0, 224, 255, 40), 2))
        painter.drawLine(0, scan_y, self.width(), scan_y)
        
        # Border glow
        painter.setPen(QPen(QColor(0, 224, 255, 100), 2))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def unlock(self):
        # Clean up camera resources
        if hasattr(self, 'face_timer'):
            self.face_timer.stop()
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
            self.camera_active = False
        
        self._can_close = True
        self.close()
        self.unlocked.emit()
