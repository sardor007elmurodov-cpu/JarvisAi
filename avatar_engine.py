"""
JARVIS - Visual Avatar Engine
Procedural generation of a futuristic AI face.
No external images required.
"""
import sys
import random
import math
import time
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class AvatarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(180, 180) 
        
        self.is_talking = False
        self.expression = "idle" # idle, thinking, success, alert
        self.blink_timer = 0
        self.mouth_height = 0
        self.scanline_y = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
        
        # Colors
        self.color_primary = QColor(0, 224, 255) # Elite Cyan
        self.color_success = QColor(0, 255, 136) # Neon Green
        self.color_alert = QColor(255, 68, 68)   # Bright Red
        self.current_color = self.color_primary

    def set_talking(self, talking):
        self.is_talking = talking
        if talking:
            self.expression = "talking"
        else:
            self.expression = "idle"

    def set_expression(self, expr, duration=3000):
        """Trigger a specific expression for a duration"""
        self.expression = expr
        if expr == "success":
            self.current_color = self.color_success
            QTimer.singleShot(duration, self._reset_expression)
        elif expr == "alert":
            self.current_color = self.color_alert
            QTimer.singleShot(duration, self._reset_expression)
        elif expr == "thinking":
            self.current_color = self.color_primary
        else:
            self.current_color = self.color_primary

    def _reset_expression(self):
        self.expression = "idle"
        self.current_color = self.color_primary

    def animate(self):
        # Blinking logic
        if self.expression != "alert":
            self.blink_timer += 1
            if self.blink_timer > 120:
                self.blink_timer = 0
            
        # Mouth animation
        if self.is_talking:
            self.mouth_height = random.randint(5, 45)
        elif self.expression == "thinking":
            self.mouth_height = 5 + math.sin(time.time()*10) * 3
        else:
            self.mouth_height = 2
            
        # Scanline
        self.scanline_y = (self.scanline_y + 2) % 180
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        
        color = self.current_color
        
        # --- SCANLINE EFFECT ---
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 30), 0.5))
        painter.drawLine(0, self.scanline_y, w, self.scanline_y)
        
        # --- EYES ---
        eye_y = cy - 25
        eye_w = 40
        eye_h = 12
        
        # Expressions
        if self.expression == "thinking":
            eye_h = 8
        elif self.expression == "success":
            eye_h = 15
        elif self.expression == "alert":
            eye_h = 18
            
        # Blink effect
        if 115 < self.blink_timer < 118:
            eye_h = 1 # Closed
            
        painter.setPen(QPen(color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Left Eye
        painter.drawRect(int(cx - 50), int(eye_y), eye_w, eye_h)
        # Right Eye
        painter.drawRect(int(cx + 10), int(eye_y), eye_w, eye_h)
        
        # Eye Glow
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        if eye_h > 3:
            painter.drawEllipse(int(cx - 30), int(eye_y + eye_h//2 - 3), 6, 6)
            painter.drawEllipse(int(cx + 30), int(eye_y + eye_h//2 - 3), 6, 6)
            
        # --- NOSE ---
        painter.setPen(QPen(color, 1.5))
        painter.drawLine(int(cx), int(cy - 5), int(cx), int(cy + 15))
        painter.drawLine(int(cx - 5), int(cy + 15), int(cx + 5), int(cy + 15))
        
        # --- MOUTH (Visualizer) ---
        mouth_y = cy + 45
        painter.setPen(QPen(color, 2))
        
        segments = 10
        msg_width = 70
        step = msg_width / segments
        start_x = cx - (msg_width / 2)
        
        for i in range(segments):
            x = start_x + (i * step)
            val = self.mouth_height + random.randint(-2, 2)
            if self.expression == "alert":
                val += 5
            painter.drawLine(int(x), int(mouth_y - val/2), int(x), int(mouth_y + val/2))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    avatar = AvatarWidget()
    avatar.show()
    avatar.set_expression("success")
    sys.exit(app.exec())
