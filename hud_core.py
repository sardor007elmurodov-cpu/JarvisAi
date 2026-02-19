import sys
import math
import random
import time
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush, QFont

class HUDCoreMaster(QWidget):
    """
    JARVIS REFINED CORE - J.A.R.V.I.S. Wave Edition
    Professional minimalist design with audio-reactive center.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Animations
        self.angles = [0, 90, 180, 270]
        self.speeds = [0.5, -0.8, 1.2, -0.3]
        
        # Audio Spectrum (64-band for more detail)
        self.spectrum = [random.randint(10, 30) for _ in range(64)]
        self.offset_y = 0
        self.is_active = False # Audio faollik holati
        
        # Palette - Elite JARVIS Cyan
        self.cyan = QColor("#00e0ff")
        self.orange = QColor("#ffffff8800")
        self.white = QColor("#ffffffffff")
        
        # Particle System (Elite v13.0)
        self.particles = [] # List of {'pos': QPointF, 'vel': QPointF, 'life': 1.0, 'color': QColor}
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)
        
    def emit_particles(self, count=5):
        """Create new intelligence particles"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.randint(250, 400)
            x = math.cos(angle) * dist
            y = math.sin(angle) * dist
            
            # Velocity towards center (Target: 0,0)
            speed = random.uniform(1.8, 3.5)
            vx = -math.cos(angle) * speed
            vy = -math.sin(angle) * speed
            
            self.particles.append({
                'pos': QPointF(x, y),
                'vel': QPointF(vx, vy),
                'life': 1.0,
                'color': self.cyan if random.random() > 0.3 else self.white
            })

    def tick(self):
        for i in range(len(self.angles)):
            self.angles[i] += self.speeds[i]
            
        # Update Spectrum with smoothing (Only if ACTIVE)
        for i in range(len(self.spectrum)):
            if self.is_active:
                target = random.randint(5, 50 if i % 8 == 0 else 25)
                if random.random() > 0.95: self.emit_particles(1) # Emit on audio activity
            else:
                target = 2 # Silent mode
            self.spectrum[i] = int(self.spectrum[i] * 0.8 + target * 0.2)
            
        # Update Particles
        alive_particles = []
        for p in self.particles:
            p['pos'] += p['vel']
            p['life'] -= 0.008
            # Friction/Gravity towards center? No, linear is fine for high-tech
            if p['life'] > 0 and (abs(p['pos'].x()) > 5 or abs(p['pos'].y()) > 5):
                alive_particles.append(p)
        self.particles = alive_particles

        self.update()

    def set_active(self, active):
        self.is_active = active

    def set_theme_color(self, hex_code):
        """Update the core color theme"""
        self.cyan = QColor(hex_code)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        cx, cy = float(center.x()), float(center.y())
        
        # 0. PARTICLES (Elite v13.0)
        painter.save()
        painter.translate(center)
        for p in self.particles:
            alpha = int(p['life'] * 200)
            color = QColor(p['color'])
            color.setAlpha(alpha)
            painter.setPen(QPen(color, 1.5))
            # Draw as small dots or tiny lines
            painter.drawPoint(p['pos'])
            if p['life'] > 0.5:
                # Add trail
                painter.setOpacity(0.3)
                painter.drawLine(p['pos'], p['pos'] - p['vel'] * 3)
        painter.restore()
        painter.setOpacity(1.0)
        
        # 0. OUTER NEON BLOOM (Global Glow)
        bloom_radius = 200 + (math.sin(time.time() * 2) * 20) if self.is_active else 180
        grad_bloom = QRadialGradient(cx, cy, bloom_radius)
        c = self.cyan
        grad_bloom.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 15))
        grad_bloom.setColorAt(1, Qt.GlobalColor.transparent)
        painter.setBrush(QBrush(grad_bloom))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, int(bloom_radius), int(bloom_radius))

        # 1. CENTRAL TEXT (J.A.R.V.I.S.)
        grad_glow = QRadialGradient(cx, cy, 70)
        grad_glow.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 50))
        grad_glow.setColorAt(0.5, QColor(c.red(), c.green(), c.blue(), 10))
        grad_glow.setColorAt(1, Qt.GlobalColor.transparent)
        painter.setBrush(QBrush(grad_glow))
        painter.drawEllipse(center, 90, 90)

        # Neon line around text
        painter.setPen(QPen(QColor(c.red(), c.green(), c.blue(), 150), 1))
        painter.drawEllipse(center, 80, 80)

        # The Identity
        painter.setPen(QPen(self.white, 2))
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        painter.setFont(font)
        painter.drawText(center.x()-58, center.y()+5, "J.A.R.V.I.S.")

        # 2. THE AUDIO WAVE RING
        self.draw_circular_waves(painter, center, 85)

        # 3. OUTER TECH ARCS
        self.draw_minimal_rings(painter, center)
    
    def draw_circular_waves(self, painter, center, radius):
        painter.save()
        painter.translate(center)
        num_bars = len(self.spectrum)
        angle_step = 360 / num_bars
        
        for i, val in enumerate(self.spectrum):
            painter.rotate(angle_step)
            
            # Neon Glow bars
            color = self.cyan if i % 2 == 0 else QColor(self.cyan.red(), self.cyan.green(), self.cyan.blue(), 200)
            painter.setPen(QPen(color, 2))
            painter.setOpacity(0.6)
            painter.drawLine(int(radius), 0, int(radius + val), 0)
            
            # Bright Tips
            painter.setPen(QPen(self.white, 2))
            painter.setOpacity(1.0)
            painter.drawLine(int(radius + val), 0, int(radius + val + 2), 0)
            
        painter.restore()

    def draw_minimal_rings(self, painter, center):
        painter.setOpacity(1.0)
        # Main Neon Circle
        r1 = 160
        rect1 = QRectF(center.x() - r1, center.y() - r1, r1 * 2, r1 * 2)
        c = self.cyan
        painter.setPen(QPen(QColor(c.red(), c.green(), c.blue(), 120), 1, Qt.PenStyle.DashLine))
        painter.drawEllipse(rect1)
        
        # Rotating Neon Brackets (Primary)
        painter.save()
        painter.translate(center)
        painter.rotate(self.angles[0])
        
        # Neon Glow for brackets
        pen_glow = QPen(self.cyan, 6)
        pen_glow.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_glow)
        painter.setOpacity(0.3)
        for a in range(0, 360, 120):
            painter.drawArc(QRectF(-170, -170, 340, 340), a * 16, 25 * 16)
            
        # Sharpe Arc
        painter.setPen(QPen(self.white, 2))
        painter.setOpacity(0.8)
        for a in range(0, 360, 120):
            painter.drawArc(QRectF(-172, -172, 344, 344), a * 16, 10 * 16)
        painter.restore()
        
        # Outer Tech Ticks
        painter.save()
        painter.translate(center)
        painter.rotate(self.angles[1] * 0.5)
        painter.setPen(QPen(self.cyan, 2))
        for a in range(0, 360, 10):
            opacity = 0.8 if a % 30 == 0 else 0.2
            painter.setOpacity(opacity)
            painter.drawLine(195, 0, 205, 0)
            painter.rotate(10)
        painter.restore()

if __name__ == "__main__":
    pass
