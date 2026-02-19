import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from hud_core import HUDCoreMaster
from hud_panels import HUDMasterPanels

class MinimalHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1366, 768)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.left_panel = HUDMasterPanels(side="left")
        self.right_panel = HUDMasterPanels(side="right")
        self.core = HUDCoreMaster()
        
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.core, 1)
        self.main_layout.addWidget(self.right_panel)
        
        print("[MINIMAL] HUD UI Initialized.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalHUD()
    window.show()
    print("[MINIMAL] Window shown.")
    sys.exit(app.exec())
