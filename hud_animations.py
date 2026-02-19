from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

class HUDStateManager(QObject):
    state_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_state = "IDLE"
        
    def set_state(self, state):
        if state in ["IDLE", "LISTENING", "PROCESSING", "SPEAKING", "ERROR"]:
            self.current_state = state
            self.state_changed.emit(state)

class HUDAnimationEngine:
    @staticmethod
    def get_rotation_speeds(state):
        # Master HUD has 6 rings
        if state == "IDLE":
            return [1.0, -0.6, 1.5, -0.8, 0.4, 2.5]
        elif state == "LISTENING":
            return [5.0, -4.0, 6.0, -3.0, 2.0, 8.0]
        elif state == "PROCESSING":
            return [12.0, -10.0, 18.0, -12.0, 8.0, 25.0]
        elif state == "SPEAKING":
            return [2.0, -1.5, 3.0, -2.0, 1.0, 4.0]
        elif state == "ERROR":
            return [0.1, -0.1, 0.1, -0.1, 0.1, -0.1]
        return [1.0] * 6

    @staticmethod
    def get_colors(state):
        if state == "ERROR":
            return QColor("#ff3b3b")
        elif state == "LISTENING":
            return QColor("#00e0ff") # Cyan
        elif state == "PROCESSING":
            return QColor("#ffffff") # White
        return QColor("#ff8800") # Solar Orange (Primary for Master Core)
