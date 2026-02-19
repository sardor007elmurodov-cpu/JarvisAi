import random
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtCore import QRectF

class MatrixRain:
    def __init__(self, width, height, font_size=14):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.columns = int(width / font_size)
        self.drops = [random.randint(-50, height) for _ in range(self.columns)]
        self.speeds = [random.randint(2, 5) for _ in range(self.columns)]
        self.chars = "01" # Binary rain for system aesthetic
        self.active = False

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.columns = int(width / self.font_size)
        # Re-init drops if dimensions change significantly
        if len(self.drops) != self.columns:
            self.drops = [random.randint(-50, height) for _ in range(self.columns)]
            self.speeds = [random.randint(2, 5) for _ in range(self.columns)]

    def update(self):
        if not self.active: return
        
        for i in range(len(self.drops)):
            self.drops[i] += self.speeds[i]
            if self.drops[i] > self.height:
                self.drops[i] = random.randint(-50, 0)
                self.speeds[i] = random.randint(2, 10)

    def draw(self, painter):
        if not self.active: return
        
        painter.setFont(QFont("Consolas", self.font_size - 2))
        
        for i in range(len(self.drops)):
            x = i * self.font_size
            y = self.drops[i]
            
            # Draw the trail
            for j in range(5):
                alpha = 150 - (j * 30)
                if alpha < 0: alpha = 0
                
                painter.setPen(QPen(QColor(0, 224, 255, alpha), 1))
                char = random.choice(self.chars)
                painter.drawText(x, int(y - (j * self.font_size)), char)
            
            # Draw the lead character (Bright)
            painter.setPen(QPen(QColor(200, 255, 255, 255), 1))
            painter.drawText(x, int(y), random.choice(self.chars))
