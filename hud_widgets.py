"""
JARVIS - Holographic Widgets
Ekranda suzib yuruvchi, shaffof va futuristik vidjetlar.
Asosiy HUD'dan alohida ishlaydi.
"""
import sys
import psutil
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush

class HologramWidget(QWidget):
    def __init__(self, title="WIDGET", x=1100, y=80):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(x, y, 220, 220)
        self.title = title
        self.opacity = 0
        
        # Fade in animation
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self._fade_in)
        self.fade_timer.start(30)
        
        # Dragging logic
        self.old_pos = None

    def _fade_in(self):
        self.opacity += 0.05
        if self.opacity >= 1.0:
            self.opacity = 1.0
            self.fade_timer.stop()
        self.update()

    def paint_glass_frame(self, painter):
        painter.setOpacity(self.opacity)
        # 1. Glass background
        grad = QRadialGradient(110, 110, 100)
        grad.setColorAt(0, QColor(0, 224, 255, 30))
        grad.setColorAt(1, QColor(0, 10, 20, 180))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(0, 224, 255, 60), 1))
        painter.drawRoundedRect(10, 10, 200, 200, 20, 20)
        
        # 2. Header
        painter.setFont(QFont("Outfit", 9, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(0, 224, 255, 200)))
        painter.drawText(25, 35, f"// {self.title}")
        
    # Draggable logic
    def mousePressEvent(self, event):
        self.old_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.position().toPoint() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.position().toPoint()

class SystemStatsWidget(HologramWidget):
    def __init__(self):
        super().__init__("SYSTEM_STATS", x=1100, y=80)
        self.cpu = 0
        self.ram = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def update_stats(self):
        self.cpu = int(psutil.cpu_percent())
        self.ram = int(psutil.virtual_memory().percent)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Hint.Antialiasing)
        self.paint_glass_frame(painter)
        
        # CPU Circle
        pen = QPen(QColor(0, 224, 255, 200), 2)
        painter.setPen(pen)
        painter.drawArc(40, 60, 100, 100, 90*16, int(-self.cpu * 3.6 * 16))
        
        painter.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        painter.drawText(75, 115, f"{self.cpu}%")
        painter.setFont(QFont("Outfit", 7))
        painter.drawText(80, 130, "CPU LOAD")

class FinancialDashboard(HologramWidget):
    def __init__(self):
        super().__init__("MARKET_SYNC", x=1100, y=320)
        from market_monitor import MarketMonitor
        self.monitor = MarketMonitor()
        self.data = {"BTC": 0, "ETH": 0, "SOL": 0}
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.fetch_data)
        self.update_timer.start(60000) # Every minute
        self.fetch_data()

    def fetch_data(self):
        def _task():
            self.data["BTC"] = self.monitor.get_raw_crypto_price("bitcoin")
            self.data["ETH"] = self.monitor.get_raw_crypto_price("ethereum")
            self.data["SOL"] = self.monitor.get_raw_crypto_price("solana")
            self.update()
        import threading
        threading.Thread(target=_task, daemon=True).start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Hint.Antialiasing)
        self.paint_glass_frame(painter)
        
        painter.setFont(QFont("JetBrains Mono", 9))
        y = 70
        for sym, price in self.data.items():
            painter.setPen(QPen(QColor(255, 255, 255, 150)))
            painter.drawText(30, y, sym)
            painter.setPen(QPen(QColor(0, 255, 170, 255)))
            painter.drawText(80, y, f"${price:,.2f}")
            y += 35

class WeatherHologram(HologramWidget):
    def __init__(self):
        super().__init__("ATMOSPHERE", x=1100, y=560)
        self.temp = "--"
        self.desc = "SYNCING..."
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_weather)
        self.timer.start(300000) # 5 mins
        self.fetch_weather()

    def fetch_weather(self):
        def _task():
            try:
                import requests
                # Open-Meteo for Tashkent (41.29, 69.24)
                res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=41.29&longitude=69.24&current_weather=true")
                data = res.json()
                self.temp = data['current_weather']['temperature']
                self.desc = "CLEAR" if data['current_weather']['weathercode'] == 0 else "CLOUDY"
                self.update()
            except: pass
        import threading
        threading.Thread(target=_task, daemon=True).start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Hint.Antialiasing)
        self.paint_glass_frame(painter)
        
        painter.setFont(QFont("Outfit", 26, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(255, 255, 255, 230)))
        painter.drawText(30, 110, f"{self.temp}°C")
        
        painter.setFont(QFont("Outfit", 10))
        painter.setPen(QPen(QColor(0, 224, 255, 200)))
        painter.drawText(30, 140, self.desc)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w1 = SystemStatsWidget()
    w2 = FinancialDashboard()
    w3 = WeatherHologram()
    w1.show(); w2.show(); w3.show()
    sys.exit(app.exec())

