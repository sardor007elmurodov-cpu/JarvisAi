from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QRectF, QTimer, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush, QLinearGradient, QRadialGradient, QImage, QPixmap, QPolygonF
import random
import cv2
import numpy as np
import psutil
import math
import time
import config

NEON = QColor(config.UI_COLORS["neon_cyan"])
DIM = QColor(config.UI_COLORS["text_secondary"])
ORANGE = QColor(config.UI_COLORS["warning_orange"])
RED = QColor(config.UI_COLORS["error_red"])

class TerminalNode(QWidget):
    """System Logs Display"""
    def __init__(self, title="TIZIM LOGLARI", parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 160) # Compacted from 180
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 35, 10, 10)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 5, 10, 150);
                border: 1px solid rgba(0, 224, 255, 30);
                color: {config.UI_COLORS['neon_cyan']};
                font-family: 'Consolas', 'Courier New';
                font-size: 10px;
            }}
        """)
        self.layout.addWidget(self.log_area)
        self.title = title
        
    def add_log(self, text):
        QTimer.singleShot(0, lambda: self._append(text))
        
    def _append(self, text):
        # Limit log size
        if self.log_area.toPlainText().count('\n') > 50:
            self.log_area.clear()
        self.log_area.append(f"> {text}")
        bar = self.log_area.verticalScrollBar()
        bar.setValue(bar.maximum())

    def set_privacy(self, active):
        """Toggle privacy obfuscation (Elite v14.0)"""
        if hasattr(self, 'is_privacy_active') and self.is_privacy_active == active:
            return
        self.is_privacy_active = active
        if active:
            self.log_area.setStyleSheet(self.log_area.styleSheet().replace(config.UI_COLORS['neon_cyan'], "#ff4444"))
            self.log_area.setText("⚠️ [MA'LUMOT YASHIRILDI] - MAXFIY QALQON FAOLLASHDI")
        else:
            self.log_area.setStyleSheet(self.log_area.styleSheet().replace("#ff4444", config.UI_COLORS['neon_cyan']))
            self.log_area.setText("Tizim loglari tiklandi...")
        self.update()

    def paintEvent(self, event):
        self._draw_tech_panel(self.title)

    def _draw_tech_panel(self, title, color=NEON):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cut = 15
        poly = QPolygonF([
            QPointF(cut, 0), QPointF(w-cut, 0),
            QPointF(w, cut), QPointF(w, h-cut),
            QPointF(w-cut, h), QPointF(cut, h),
            QPointF(0, h-cut), QPointF(0, cut)
        ])
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(0, 10, 20, 200))
        grad.setColorAt(1, QColor(0, 5, 10, 240))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 40), 1))
        painter.drawPolygon(poly)
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 200), 2))
        painter.drawLine(cut, 0, cut+20, 0); painter.drawLine(0, cut, 0, cut+20); painter.drawLine(0, cut, cut, 0)
        painter.drawLine(w-cut, h, w-cut-20, h); painter.drawLine(w, h-cut, w, h-cut-20); painter.drawLine(w, h-cut, w-cut, h)
        painter.setFont(QFont("Outfit", 9, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(cut+10, 25, title.upper())
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 100), 1))
        painter.drawLine(cut, 35, w-cut, 35)

class VisualNode(QWidget):
    """Base class for Camera and Screen nodes"""
    def __init__(self, title, width=320, height=200, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.title = title
        self.image_label = QLabel(self)
        self.image_label.setGeometry(10, 30, width-20, height-40) # Even tighter
        self.image_label.setStyleSheet("background-color: rgba(0,0,0,200); border: 1px solid #004455;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("SIGNAL YO'Q")

    def update_image(self, frame, is_private=False):
        try:
            target_w = self.image_label.width()
            target_h = self.image_label.height()
            
            if target_w > 0 and target_h > 0:
                frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            
            if is_private:
                # Apply heavy blur (Quantum Shield)
                frame = cv2.GaussianBlur(frame, (35, 35), 0)
                frame = cv2.GaussianBlur(frame, (35, 35), 0)
            
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qt_image))
            
            if is_private:
                self.image_label.setText("🛡️ HIMOYALANGAN")
                self.image_label.setStyleSheet("background-color: rgba(255,0,0,50); border: 2px solid #ff4444; color: #ff4444; font-weight: bold;")
            else:
                self.image_label.setText("")
                self.image_label.setStyleSheet("background-color: rgba(0,0,0,200); border: 1px solid #004455;")
        except Exception:
            pass

    def paintEvent(self, event):
        self._draw_tech_panel(self.title)

    def _draw_tech_panel(self, title):
        # Re-use logic or copy-paste (DRY principle would suggest a mixin, but simple copy is safer for hot-patching)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cut = 15
        
        # Frame
        painter.setPen(QPen(QColor(0, 224, 255, 60), 1))
        painter.setBrush(QBrush(QColor(0, 5, 10, 100))) # More transparent for visual feeds
        
        poly = QPolygonF([
            QPointF(cut, 0), QPointF(w-cut, 0),
            QPointF(w, cut), QPointF(w, h-cut),
            QPointF(w-cut, h), QPointF(cut, h),
            QPointF(0, h-cut), QPointF(0, cut)
        ])
        painter.drawPolygon(poly)
        
        # Brackets
        painter.setPen(QPen(QColor(0, 224, 255, 200), 2))
        painter.drawLine(0, cut, cut, 0)
        painter.drawLine(w, h-cut, w-cut, h)
        
        # Header
        painter.setFont(QFont("Outfit", 9, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(cut+5, 22, f"{title}")

class SecurityDashboard(QWidget):
    """Biometric & System Security Status"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 130) # Compacted from 140
        self.status = "RUXSAT BERILDI"
        self.authorized_user = "SARDORBEK"
        self.alert_level = "LOW"
        self.privacy_active = False
        self.color = NEON
        
    def update_security_status(self, status, user="UNKNOWN", alert="LOW", privacy=False):
        self.status = status.upper()
        self.authorized_user = user.upper()
        self.alert_level = alert.upper()
        self.privacy_active = privacy
        
        if self.status == "AUTHORIZED" or self.status == "RUXSAT BERILDI":
            self.color = NEON
        elif self.status == "WARNING" or self.status == "UNKNOWN":
            self.color = ORANGE
        else:
            self.color = RED
        self.update()

    def paintEvent(self, event):
        # Pulsing Glow Effect
        glow = math.sin(time.time() * 3) * 20 + 20
        self.border_alpha = 60 + glow
        self._draw_glass_panel()

    def _draw_glass_panel(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Glass Base
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(5, 15, 25, 220))
        grad.setColorAt(1, QColor(0, 5, 10, 240))
        painter.setBrush(QBrush(grad))
        
        border_color = QColor(self.color)
        border_color.setAlpha(int(self.border_alpha))
        painter.setPen(QPen(border_color, 1.2))
        painter.drawRoundedRect(QRectF(3, 3, self.width()-6, self.height()-6), 4, 4)
        
        # Corner Brackets
        painter.setPen(QPen(self.color, 1.5))
        s = 10
        painter.drawLine(3,3, 3+s, 3); painter.drawLine(3,3, 3, 3+s) # TL
        painter.drawLine(self.width()-3, self.height()-3, self.width()-3-s, self.height()-3) # BR
        
        # Title
        painter.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(18, 22, "XAVFSIZLIK & BIO-NAZORAT")
        
        # Status Label (Glow effect)
        painter.setFont(QFont("JetBrains Mono", 10, QFont.Weight.Bold))
        painter.setPen(QPen(self.color, 2))
        painter.drawText(18, 55, f"HOLAT: {self.status}")
        
        # Identity
        painter.setFont(QFont("JetBrains Mono", 8))
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        painter.drawText(18, 80, f"FOYDALANUVCHI: {self.authorized_user}")
        conf = 98 + (math.sin(time.time()*2) * 1.5) if self.status == "AUTHORIZED" or self.status == "RUXSAT BERILDI" else random.randint(30, 60)
        painter.drawText(18, 98, f"ISHONCH DARAJASI: {conf:.1f}%") # Dynamic detail
        
        if self.privacy_active:
            painter.setPen(QPen(QColor("#ff4444"), 1))
            painter.drawText(18, 125, "🛡️ MAXFIY HIMOYA: FAOLLASHDI")


class ActiveThreatRadar(QWidget):
    """Real-time Network/Process Threat Radar"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 120) # Compacted from 140
        self.angle = 0
        self.blips = [] # (x, y, life, type)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scan)
        self.timer.start(50) # 20 FPS scan

    def _scan(self):
        """Update blips animation life"""
        self.angle = (self.angle + 4) % 360
        # Fade out blips
        new_blips = []
        for x, y, life, b_type in self.blips:
            if life > 0:
                new_blips.append((x, y, life - 2, b_type))
        self.blips = new_blips
        self.update()

    def update_radar(self, connections):
        """
        Feed real network connection data (IPs/Ports) to radar.
        connections: List of (host, port, status)
        """
        import random
        import math
        
        # Limit blips to avoid overcrowding
        if len(self.blips) > 20: return
        
        for host, port, remote in connections:
            # Map remote host string to a deterministic angle/radius or random for visual flair
            # For now, let's use a bit of randomness with a hint of consistency
            angle = (hash(host) % 360)
            radius = 30 + (hash(str(port)) % 60)
            
            rad = math.radians(angle)
            bx = 160 + math.cos(rad) * radius
            by = 100 + math.sin(rad) * radius
            
            # Types: 0=Safe, 1=External/Possible Threat
            is_external = not host.startswith(('127.', '192.', '10.', '172.'))
            b_type = 1 if is_external else 0
            
            self.blips.append((bx, by, 100, b_type))
        # Decay blips
        for b in self.blips:
            b[2] -= 2
        self.blips = [b for b in self.blips if b[2] > 0]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w/2, h/2
        
        # 1. PANEL BASE
        painter.setPen(QPen(QColor(0, 224, 255, 40), 0.8))
        painter.setBrush(QBrush(QColor(0, 4, 8, 160)))
        painter.drawRoundedRect(QRectF(5, 5, w-10, h-10), 4, 4)
        
        # 2. RADAR GRID
        painter.setPen(QPen(QColor(0, 224, 255, 30), 1))
        painter.drawEllipse(QPointF(cx, cy), 80, 80)
        painter.drawEllipse(QPointF(cx, cy), 40, 40)
        painter.drawLine(int(cx-80), int(cy), int(cx+80), int(cy))
        painter.drawLine(int(cx), int(cy-80), int(cx), int(cy+80))
        
        # 3. SWEEP LINE
        painter.setPen(QPen(QColor(0, 255, 0, 200), 2))
        rad = math.radians(self.angle)
        ex = cx + math.cos(rad) * 80
        ey = cy + math.sin(rad) * 80
        
        grad = QLinearGradient(cx, cy, ex, ey)
        grad.setColorAt(0, Qt.GlobalColor.transparent)
        grad.setColorAt(1, QColor(0, 255, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(int(cx-80), int(cy-80), 160, 160, int(self.angle*16), int(-30*16))
        
        # 4. BLIPS
        detected_count = 0
        for b in self.blips:
            alpha = int(b[2] * 2.55)
            color = QColor("#ff4444") if b[3] == "NET" else QColor("#ffaa00")
            color.setAlpha(alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(b[0], b[1]), 3, 3)
            detected_count += 1
            
        # 5. HEADER & STATS
        painter.setFont(QFont("JetBrains Mono", 8))
        painter.setPen(QPen(QColor("#ff4444"), 1))
        painter.drawText(w-100, 22, f"NISHONLAR: {detected_count}")

class HUDTelemetryPanel(QWidget):
    """Elite Holographic Telemetry: CPU, RAM, Disk, GPU as Circle Charts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 180) # Expanded to fit all
        self.stats = {"CPU": 0, "RAM": 0, "DISK": 0, "DARAJA": 1}
        self.xp_percent = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000) # Faster refresh
        
    def update_stats(self, gamification=None):
        try:
            self.stats["CPU"] = int(psutil.cpu_percent())
            self.stats["RAM"] = int(psutil.virtual_memory().percent)
            self.stats["DISK"] = int(psutil.disk_usage('/').percent)
            
            if gamification:
                status = gamification.get_status()
                self.stats["DARAJA"] = status["level"]
                self.xp_percent = status["progress"]
            
            self.update()
        except: pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. GLASS SLAB
        painter.setPen(QPen(QColor(0, 224, 255, 40), 0.7))
        painter.setBrush(QBrush(QColor(0, 4, 8, 160)))
        painter.drawRoundedRect(QRectF(5, 5, self.width()-10, self.height()-10), 4, 4)
        
        # 2. SEPARATOR
        painter.setPen(QPen(QColor(0, 224, 255, 30), 0.5))
        painter.drawLine(self.width()//2, 35, self.width()//2, self.height()-15)
        
        # 3. CIRCULAR METRICS
        positions = [(80, 75), (240, 75), (80, 135), (240, 135)]
        keys = ["CPU", "RAM", "DISK", "DARAJA"]
        
        for i, key in enumerate(keys):
            cx, cy = positions[i]
            val = self.stats[key]
            
            # Label
            painter.setFont(QFont("Outfit", 7, QFont.Weight.Bold))
            painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
            painter.drawText(cx-25, cy-5, 50, 12, Qt.AlignmentFlag.AlignCenter, key)
            
            # Value
            painter.setFont(QFont("JetBrains Mono", 6))
            painter.setPen(QPen(QColor(0, 224, 255, 230)))
            painter.drawText(cx-25, cy+8, 50, 12, Qt.AlignmentFlag.AlignCenter, f"{val}%")
            
            # Ultra-Thin Arc (Smaller)
            painter.setOpacity(0.9)
            rect = QRectF(cx-22, cy-22, 44, 44)
            if key == "DARAJA":
                span = int(-self.xp_percent * 3.6 * 16)
                painter.setPen(QPen(QColor("#ff8800"), 1.5))
            else:
                span = int(-val * 3.6 * 16)
                color = QColor(0, 224, 255) if val < 85 else QColor("#ff4444")
                painter.setPen(QPen(color, 1.5))
            
            painter.drawArc(rect, 90*16, span)
            
            # Subtle outer ghost arc
            painter.setOpacity(0.1)
            painter.drawEllipse(rect)
            painter.setOpacity(1.0)

        # Header
        painter.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
        painter.drawText(18, 22, "TIZIM DIAGNOSTIKASI")

class WorldMoodNode(QWidget):
    """Visualizes the 'Mood of the World' based on Global Trends"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 110)
        
        # Data State
        self.mood_text = "YUKLANMOQDA..."
        self.summary = "Global ma'lumotlar tahlil qilinmoqda..."
        self.mood_color = QColor("#00e0ff") # Cyan
        
        # Integration
        try:
            from global_eye import GlobalEye
            self.eye = GlobalEye()
        except:
            self.eye = None
            self.summary = "Global Eye moduli topilmadi."

        # Animation Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)
        
        # Data Refresh Timer (Every 5 mins)
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.refresh_data)
        self.data_timer.start(300000) # 5 minutes
        
        # Initial fetch
        QTimer.singleShot(1000, self.refresh_data)

    def refresh_data(self):
        """Fetch data in background thread"""
        if not self.eye: return
        import threading
        def _task():
            try:
                data = self.eye.analyze_world()
                self.mood_text = data.get("mood", "UNKNOWN")
                self.summary = data.get("summary", "Ma'lumot yo'q")
                self.mood_color = QColor(data.get("color", "#00e0ff"))
            except Exception as e:
                print(f"Global Eye Update Error: {e}")
        
        threading.Thread(target=_task, daemon=True).start()

    def update_mood(self, mood, summary, color_hex="#00e0ff"):
        # External override if needed
        self.mood_text = mood.upper()
        self.summary = summary
        self.mood_color = QColor(color_hex)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. PANEL
        painter.setPen(QPen(QColor(0, 224, 255, 30), 0.8))
        painter.setBrush(QBrush(QColor(0, 4, 8, 140)))
        painter.drawRoundedRect(QRectF(5, 5, self.width()-10, self.height()-10), 4, 4)
        
        # 2. HEADER
        painter.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(18, 22, "GLOBAL RAZVEDKA & HOLAT")
        
        # 3. MOOD ORB
        pulse = abs(math.sin(time.time() * 1.5))
        painter.setOpacity(0.3 + 0.7 * pulse)
        # Using a QRadialGradient for a soft orb effect
        grad_orb = QRadialGradient(285, 45, 10)
        grad_orb.setColorAt(0, self.mood_color)
        grad_orb.setColorAt(1, Qt.GlobalColor.transparent)
        painter.setBrush(QBrush(grad_orb))
        painter.setPen(QPen(self.mood_color, 1))
        painter.drawEllipse(275, 35, 20, 20)
        painter.setOpacity(1.0)
        
        # 4. TEXT
        painter.setFont(QFont("JetBrains Mono", 10, QFont.Weight.Bold))
        painter.setPen(QPen(self.mood_color, 1))
        painter.drawText(18, 50, f"HOZIRGI: {self.mood_text}")
        
        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QPen(QColor(255, 255, 255, 180)))
        rect = QRectF(18, 65, self.width()-36, 40) # Slightly taller
        painter.drawText(rect, Qt.TextFlag.TextWordWrap, self.summary)


class SelfEvolutionNode(QWidget):
    """Visualizes JARVIS Self-Healing & Evolution (Elite v19.0)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 110)
        self.kernel_health = 100
        self.sentience_level = 1
        self.xp = 0
        self.repair_active = False
        self.last_fix = "INITIALIZING..."
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def set_evolution_data(self, level, xp):
        self.sentience_level = level
        self.xp = xp
        self.update()

    def set_repair_status(self, is_active, fix_name="YO'Q"):
        self.repair_active = is_active
        if fix_name != "YO'Q": self.last_fix = fix_name
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Glass Panel
        painter.setPen(QPen(QColor(0, 224, 255, 30), 0.8))
        painter.setBrush(QBrush(QColor(0, 4, 8, 140)))
        painter.drawRoundedRect(QRectF(5, 5, self.width()-10, self.height()-10), 4, 4)
        
        # Header
        painter.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(18, 22, "AI MUSTAQIL TARAQQIYOTI")
        
        # Sentience level
        painter.setFont(QFont("JetBrains Mono", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(0, 224, 255, 255)))
        painter.drawText(230, 22, f"SAVIYA: {self.sentience_level}")
        
        # Health Bar
        painter.setFont(QFont("JetBrains Mono", 7))
        painter.setPen(QPen(QColor(0, 224, 255, 180)))
        painter.drawText(18, 45, f"YADRO_SALOMATLIGI: {self.kernel_health}%")
        
        # Evolution Progress (XP Bar)
        painter.setPen(QPen(QColor(0, 224, 255, 40), 1))
        painter.drawRect(18, 55, 280, 5)
        
        required_xp = self.sentience_level * 100
        progress_width = min(280, int((self.xp / required_xp) * 280)) if required_xp > 0 else 0
        
        painter.setBrush(QBrush(QColor(0, 224, 255, 150)))
        painter.drawRect(18, 55, progress_width, 5)
        
        # Status Pulse
        if self.repair_active:
            pulse = abs(math.sin(time.time() * 5))
            painter.setPen(QPen(QColor(255, 215, 0, int(255 * pulse)), 1.5))
            painter.drawText(18, 75, "TA'MIRLANISH FAOL...")
        else:
            painter.setPen(QPen(QColor(0, 255, 127, 100), 1))
            painter.drawText(18, 75, "TIZIM BARQAROR")

        painter.setFont(QFont("JetBrains Mono", 6))
        painter.setPen(QPen(QColor(255, 255, 255, 100)))
        painter.drawText(18, 95, f"SO'NGGI_FIKR: {self.last_fix[:45]}...")
        
class VoiceSettingsNode(QWidget):
    """Voice Synthesis & Profile Status"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 60) # Compacted from 70
        self.voice_type = "NEURAL (ElevenLabs)"
        self.is_syncing = False
        
    def set_voice_info(self, v_type, syncing=False):
        self.voice_type = v_type
        self.is_syncing = syncing
        self.update()

    def _draw_uhd_frame(self, title):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # UHD Box
        painter.setPen(QPen(QColor(0, 224, 255, 80), 0.8))
        painter.setBrush(QBrush(QColor(0, 5, 10, 150)))
        painter.drawRect(0, 0, self.width(), self.height())
        
        # Tech Corners
        painter.setPen(QPen(QColor(0, 224, 255, 255), 1))
        s = 10
        painter.drawLine(0, 0, s, 0); painter.drawLine(0, 0, 0, s) # TL
        painter.drawLine(self.width(), 0, self.width()-s, 0); painter.drawLine(self.width(), 0, self.width(), s) # TR
        
        # Title
        painter.setFont(QFont("Outfit", 7, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(10, 15, f"[ {title} ]")
        
        # Metadata
        painter.setFont(QFont("JetBrains Mono", 5))
        painter.setPen(QPen(QColor(0, 224, 255, 120), 1))
        painter.drawText(self.width()-45, 15, "LIVE_FEED_4K")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cut = 10
        
        # 1. TECH FRAME (Chamfered)
        painter.setPen(QPen(QColor(0, 224, 255, 60), 1))
        painter.setBrush(QBrush(QColor(0, 5, 10, 180)))
        
        poly = QPolygonF([
            QPointF(cut, 0), QPointF(w-cut, 0),
            QPointF(w, cut), QPointF(w, h-cut),
            QPointF(w-cut, h), QPointF(cut, h),
            QPointF(0, h-cut), QPointF(0, cut)
        ])
        painter.drawPolygon(poly)
        
        # 2. BRACKETS
        painter.setPen(QPen(QColor(0, 224, 255, 200), 2))
        painter.drawLine(0, cut, cut, 0)
        painter.drawLine(w, h-cut, w-cut, h)

        # 3. CONTENT
        painter.setFont(QFont("Outfit", 9, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
        painter.drawText(20, 25, "OVOZ SINTEZI")
        
        painter.setFont(QFont("JetBrains Mono", 8))
        painter.setPen(QPen(QColor(0, 224, 255, 200)))
        painter.drawText(20, 48, f"REJIM: {self.voice_type}")
        
        if self.is_syncing:
            painter.setPen(QPen(QColor("#ffaa00"), 1))
            painter.drawText(20, 68, "⚡ OPTIMALLASHTIRILMOQDA...")
        else:
            painter.setPen(QPen(QColor("#00ffaa"), 1))
            painter.drawText(20, 68, "● HOLAT: ISHLAMOQDA")
             
class PostureNode(QWidget):
    """Monitors User Posture (Health)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 60) # Compacted from 70
        self.posture_score = 100
        self.status = "A'LO"
        self.color = QColor("#00ff00")
        
    def set_posture(self, score, status):
        self.posture_score = score
        self.status = status.upper()
        if self.posture_score > 80: self.color = QColor("#00ff00")
        elif self.posture_score > 50: self.color = QColor("#ffaa00")
        else: self.color = QColor("#ff4444")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. GLASS SLAB
        painter.setPen(QPen(self.color, 0.7))
        painter.setBrush(QBrush(QColor(2, 6, 4, 190)))
        painter.drawRoundedRect(QRectF(5, 5, self.width()-10, self.height()-10), 4, 4)
        
        # 2. CONTENT
        painter.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
        painter.drawText(18, 22, "BIOMETRIK QOMAT TAHLILI")
        
        # Minimal Bar
        painter.setPen(QPen(QColor(255, 255, 255, 25), 1))
        bar_rect = QRectF(18, 42, self.width()-36, 4)
        painter.drawRect(bar_rect)
        
        painter.setBrush(QBrush(self.color))
        pw = (self.width()-36) * (self.posture_score / 100)
        painter.drawRect(QRectF(18, 42, pw, 4))
        
        # Status Label
        painter.setFont(QFont("JetBrains Mono", 8, QFont.Weight.Bold))
        painter.setPen(self.color)
        painter.drawText(18, 68, f"NATIJA: {self.posture_score}% | {self.status}")

class TelegramIntelligenceNode(TerminalNode):
    """Real-time Telegram Monitoring & Daily AI Reports for HUD"""
    def __init__(self, parent=None):
        super().__init__("TELEGRAM IJTIMOIY NAZORAT", parent)
        self.setFixedSize(320, 130)
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 5, 10, 200);
                border: 1px solid rgba(0, 224, 255, 15);
                color: {config.UI_COLORS['neon_cyan']};
                font-family: 'Consolas';
                font-size: 8px;
            }}
        """)
        self.add_log("🛰 Monitoring: Global (Guruhlar/Kanallar/Chatlar)")
        self.add_log("🤖 Rejim: Avtonom Tahlil v18.5")

class ResearchNode(TerminalNode):
    """Dedicated terminal for AI Research logs"""
    def __init__(self, parent=None):
        super().__init__("TADQIQOT TERMINALI", parent)
        self.setFixedSize(320, 110) # Compacted from 130
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 5, 10, 200);
                border: 1px solid rgba(0, 224, 255, 20);
                color: #ffaa00;
                font-family: 'Consolas';
                font-size: 9px;
            }
        """)

class HUDMasterPanels(QWidget):
    def __init__(self, side="left", parent=None):
        super().__init__(parent)
        self.side = side
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8) # Compacted from 12
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        if side == "left":
            self.security_node = SecurityDashboard()
            self.terminal = TerminalNode("TIZIM TERMINALI")
            self.telegram_node = TelegramIntelligenceNode()
            self.research = ResearchNode()
            self.evo_node = SelfEvolutionNode()
            self.voice_node = VoiceSettingsNode()
            
            self.layout.setSpacing(10) # Breathable vertical flow
            self.layout.addWidget(self.security_node)
            self.layout.addWidget(self.terminal)
            self.layout.addWidget(self.telegram_node)
            self.layout.addWidget(self.research)
            self.layout.addWidget(self.evo_node)
            self.layout.addWidget(self.voice_node)
            self.layout.addStretch()
        else:
            # RIGHT PANEL: CLEAN & FUNCTIONAL (Elite v14.0)
            # Increased height to 200 to fix 'squashed' look and match 16:9/4:3 better
            self.camera_node = VisualNode("KESTIRISH KAMERASI", height=200) 
            self.screen_node = VisualNode("EKRAN LINK", height=200) 
            self.stats_node = HUDTelemetryPanel() 
            self.posture_node = PostureNode() 
            
            # Removed radar_node as per user request to clean up clutter
            
            self.layout.setSpacing(15) # Increased spacing for premium feel
            self.layout.addWidget(self.camera_node)
            self.layout.addWidget(self.screen_node)
            self.layout.addWidget(self.stats_node)
            self.layout.addWidget(self.posture_node)
            self.layout.addStretch()

    def update_camera(self, frame, is_private=False):
        if hasattr(self, 'camera_node'):
            self.camera_node.update_image(frame, is_private=is_private)
            
    def update_screen(self, frame, is_private=False):
        if hasattr(self, 'screen_node'):
            self.screen_node.update_image(frame, is_private=is_private)

    def add_log(self, text):
        if hasattr(self, 'terminal'):
            self.terminal.add_log(text)

class HolographicScanner(QWidget):
    """Futuristic 3D-like scanning visualizer for HUD 2.0"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 60) # Compacted from 80
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(40)
        
    def update_anim(self):
        self.angle = (self.angle + 3) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w/2, h/2
        
        # Draw scanning circles
        painter.setPen(QPen(QColor(0, 224, 255, 60), 1))
        for i in range(3):
            r = 30 + i*20 + math.sin(math.radians(self.angle + i*45)) * 10
            painter.drawEllipse(QPointF(cx, cy), r, r/2)
            
        # Rotating line
        painter.setPen(QPen(QColor(0, 255, 200, 180), 2))
        rad = math.radians(self.angle)
        lx = math.cos(rad) * 100
        ly = math.sin(rad) * 30
        painter.drawLine(int(cx-lx), int(cy-ly), int(cx+lx), int(cy+ly))
        
        painter.setFont(QFont("JetBrains Mono", 7))
        painter.setPen(QColor(0, 255, 200, 150))
        painter.drawText(10, 20, "SCANNER: DEEP_OS_LINK")
        painter.drawText(w-80, 20, f"BURCHAK: {self.angle}°")

class FinancialDashboard(QWidget):
    """Simulated Crypto/Stock monitor for JARVIS Core"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 70) # Compacted from 80
        self.prices = {"BTC": 48200, "ETH": 2600, "SOL": 105}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.jitter)
        self.timer.start(2000)

    def update_market_data(self, data):
        """Update with real market values if provided"""
        if isinstance(data, dict):
            for k, v in data.items():
                if k in self.prices:
                    self.prices[k] = v
        self.update()

    def jitter(self):

        for k in self.prices:
            self.prices[k] += random.uniform(-10, 10)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        
        painter.setPen(QPen(QColor(0, 224, 255, 40), 1))
        painter.drawRect(0, 0, w-1, h-1)
        
        painter.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(10, 20, "MOLIYA TERMINALI")
        
        y = 45
        painter.setFont(QFont("JetBrains Mono", 9))
        for coin, price in self.prices.items():
            painter.setPen(QColor(0, 224, 255))
            painter.drawText(15, y, f"{coin}:")
            painter.setPen(QColor("#00ff88"))
            painter.drawText(80, y, f"${price:,.2f}")
            y += 20

class SystemHealerNode(QWidget):
    """Visual feedback for System Repair/Health logic"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 50) # Compacted from 60
        self.status = "OPTIMAL"
        self.health = 98

    def set_status(self, status, health=98):
        self.status = status.upper()
        self.health = health
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        w, h = self.width(), self.height()
        
        painter.setPen(QPen(QColor(0, 224, 255, 100), 1))
        painter.drawRoundedRect(5, 5, w-10, h-10, 4, 4)
        
        painter.setFont(QFont("Outfit", 9))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(15, 25, f"TABIB_YADRO: {self.status}")
        
        # Health bar
        painter.setBrush(QColor(0, 224, 255, 40))
        painter.drawRect(15, 40, w-30, 10)
        painter.setBrush(QColor(0, 255, 150, 180))
        painter.drawRect(15, 40, int((w-30) * self.health/100), 10)

class HUDStatusBar(QWidget):
    """Top Status Bar with Sentience Indicator"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.sentience_status = "BARQAROR"
        self.sentience_color = QColor("#00e0ff")
        
    def set_sentience(self, status, color_hex="#00e0ff"):
        self.sentience_status = status.upper()
        self.sentience_color = QColor(color_hex)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        m = 40 
        
        # 1. UHD STATUS LINE
        line_pen = QPen(QColor(0, 224, 255, 80), 0.8)
        painter.setPen(line_pen)
        painter.drawLine(m, h-10, w-m, h-10)
        
        # 2. SECTIONS (Ticks)
        painter.setPen(QPen(QColor(0, 224, 255, 150), 1))
        for x in [m, w-m, w/2]:
            painter.drawLine(int(x), h-15, int(x), h-5)

        # 3. INDICATORS
        painter.setFont(QFont("Outfit", 10, QFont.Weight.Bold))
        painter.setPen(QPen(self.sentience_color, 1))
        status_text = f"ASOSIY_TIZIM_V.16.0_ELITE :: {self.sentience_status}"
        painter.drawText(0, 10, w, 30, Qt.AlignmentFlag.AlignCenter, status_text)

        
class HUDMediaControls(QWidget):
    """Dummy class for compatibility"""
    pass
