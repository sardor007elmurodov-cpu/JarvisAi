import sys
import traceback
import threading
import time
import datetime
import os
import math
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPointF, QThread
from PyQt6.QtGui import QColor, QRadialGradient, QPainter, QPen, QFont, QPolygonF, QIcon
# import cv2  <-- Lazy loaded
# import numpy as np <-- Lazy loaded
import mss
import psutil
import config

from hud_core import HUDCoreMaster
from hud_panels import HUDMasterPanels, HUDStatusBar, HUDMediaControls
from agent import JARVIS, VoiceJARVIS
from gesture_control import HandGestureControl
from hud_lock import HUDLockScreen
from face_auth import FaceAuth
from security_scanner import SecurityScanner
from proactive_vision import ProactiveVision
from avatar_engine import AvatarWidget
from hud_effects import MatrixRain
import config

class JARVISBridge(QObject):
    state_update = pyqtSignal(str)
    log_update = pyqtSignal(str)
    color_update = pyqtSignal(str)
    
    def __init__(self, core, ui_core=None, avatar=None, hud_window=None):
        super().__init__()
        self.core = core
        self.ui_core = ui_core
        self.avatar = avatar
        self.hud_window = hud_window

    def run_command(self, text):
        self.state_update.emit("PROCESSING")
        def _exec():
            # 0. Set Avatar to THINKING
            if self.avatar: 
                self.avatar.set_expression("thinking")
            
            # 1. Log User Input
            self.log_update.emit(f"User: {text}")
            
            # 2. Process via Core
            try:
                response_data = self.core.process_command(text)
                success = True
            except Exception as e:
                response_data = f"Error processing command: {str(e)}"
                success = False
            
            # 3. Handle Dictionary Response
            emotion_color = "#00e0ff"
            ui_action = None
            if isinstance(response_data, dict):
                verbal = response_data.get("verbal_response", str(response_data))
                success = response_data.get("success", True)
                emotion_color = response_data.get("emotion_color", "#00e0ff")
                ui_action = response_data.get("ui_action")
            else:
                verbal = str(response_data)
                
            # Perform UI Action (Elite v16.0)
            if ui_action == "toggle_shield" and self.hud_window:
                if hasattr(self.hud_window, "privacy_shield"):
                    shield = self.hud_window.privacy_shield
                    # Use QTimer to update GUI from thread
                    from PyQt6.QtCore import QMetaObject, Q_ARG, Qt
                    if shield.isVisible():
                        QMetaObject.invokeMethod(shield, "hide", Qt.ConnectionType.QueuedConnection)
                    else:
                        QMetaObject.invokeMethod(shield, "show", Qt.ConnectionType.QueuedConnection)
                        QMetaObject.invokeMethod(shield, "raise_", Qt.ConnectionType.QueuedConnection)


                
            # Emit Color Update
            if emotion_color:
                self.color_update.emit(emotion_color)
                
            # 4. Log JARVIS Response
            self.log_update.emit(f"JARVIS: {verbal}")
            
            # 5. Speak & Animate
            if hasattr(self.core, 'speak'):
                if self.ui_core: self.ui_core.set_active(True)
                
                # AVATAR CONTROL
                if self.avatar:
                    self.avatar.show()
                    self.avatar.set_talking(True)
                
                self.core.speak(verbal)
                
                if self.ui_core: self.ui_core.set_active(False)
                if self.avatar:
                    self.avatar.set_talking(False)
                    # Set final expression based on outcome
                    final_expr = "success" if success else "alert"
                    if emotion_color == "#ff4444": final_expr = "alert" # Angry
                    self.avatar.set_expression(final_expr, duration=4000)
            
            self.state_update.emit("IDLE")
            # Revert color after a while (Optional, but good for mood reset)
            time.sleep(5)
            self.color_update.emit("#00e0ff") 
            
        threading.Thread(target=_exec, daemon=True).start()

class VoiceWorker(QThread):
    command_detected = pyqtSignal(str)
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        
    def run(self):
        if not hasattr(self.core, 'listen'):
            return
            
        print("🎤 VOICE WORKER STARTED. Listening for Wake Word...")
        
        while True:
            # 1. Listen for "Hey JARVIS" efficiently
            if self.core.voice and self.core.voice.listen_for_wake_word(config.WAKE_WORDS):
                print("⚡ WAKE WORD DETECTED!")
                self.command_detected.emit("WAKE_UP_TRIGGER") # Trigger UI effect
                
                # 2. Now listen for actual command
                cmd = self.core.listen()
                if cmd:
                    self.command_detected.emit(cmd)
            
            time.sleep(0.1)

class TelegramWorker(QThread):
    """Integrated Social Monitoring for HUD (Elite v18.5)"""
    def __init__(self, core):
        super().__init__()
        self.core = core

    def run(self):
        try:
            import asyncio
            from social_sentience import client, main as social_main
            
            # Use the loop to keep the client alive inside the thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            print("🛰 Starting Integrated Telegram Monitor...")
            loop.run_until_complete(social_main())
        except Exception as e:
            print(f"Telegram Monitor Error: {e}")

class CameraWorker(QThread):
    frame_update = pyqtSignal(object)
    raw_frame_update = pyqtSignal(object)
    analysis_update = pyqtSignal(dict)
    
    def __init__(self, camera=None, face_auth=None):
        super().__init__()
        self.camera_manager = camera
        self.face_auth = face_auth
        self.gesture = None # Initialized in run()
        self.vision_frame_skip = 10 # Check faces/posture every 10 frames
        self.frame_counter = 0

    def run(self):
        import cv2
        import numpy as np
        import time
        from gesture_control import HandGestureControl
        print("DEBUG: CameraWorker v16.0 Started (Sentinel Vision Active)")
        
        # Initialize heavy components in the thread, not __init__
        self.gesture = HandGestureControl()
        self.gesture.start()
        
        while True:
            import config
            if self.camera_manager:
                frame = self.camera_manager.get_latest_frame()
                if frame is not None:
                    # Work on a copy for processing
                    raw_frame = frame.copy()
                    self.raw_frame_update.emit(raw_frame) # For security analysis
                    
                    display_frame = cv2.flip(raw_frame, 1) # Mirror for HUD display
                    
                    # 1. Gesture Processing (High Priority)
                    if config.GESTURE_SETTINGS.get("enabled", True) and self.gesture:
                        display_frame = self.gesture.process_frame(display_frame)
                    
                    # 2. Vision Analysis (Throttled)
                    self.frame_counter += 1
                    if self.frame_counter % self.vision_frame_skip == 0:
                        self._process_vision(raw_frame)
                    
                    self.frame_update.emit(display_frame)
            
            time.sleep(0.03) # ~30 FPS internal limit


    def _process_vision(self, frame):
        """Fon rejimida yuz va qomatni tahlil qilish"""
        import cv2
        data = {
            "face_detected": False,
            "authorized": False,
            "confidence": 0,
            "user": "UNKNOWN",
            "posture_score": 100,
            "posture_status": "IDEAL"
        }
        
        if self.face_auth:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_auth.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                data["face_detected"] = True
                # Identify
                auth, conf = self.face_auth.identify_with_faces(frame, faces)
                if auth:
                    data["authorized"] = True
                    data["confidence"] = conf
                    data["user"] = "SARDORBEK"
                    
                    # Bio-Sync: Emotion Detection
                    (x, y, w, h) = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    data["emotion"] = self.face_auth.get_emotion(face_roi)
                    
                    # Posture Analysis (Only if authorized/present)
                    frame_h = frame.shape[0]
                    face_center_y = y + h/2
                    if face_center_y > frame_h * 0.7:
                        data["posture_score"], data["posture_status"] = 30, "SLOUCHED"
                    elif face_center_y > frame_h * 0.5:
                        data["posture_score"], data["posture_status"] = 70, "LEANING"
                else:
                    data["user"] = "UNKNOWN"
            
            self.analysis_update.emit(data)

class ScreenWorker(QThread):
    screen_update = pyqtSignal(object)  # Changed from np.ndarray to object for lazy loading

    def run(self):
        import cv2
        import numpy as np
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while True:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                self.screen_update.emit(frame)
                time.sleep(0.12) # ~8 FPS (Preview only, saving CPU)

class NetworkWorker(QThread):
    network_update = pyqtSignal(list)

    def run(self):
        while True:
            try:
                conns = psutil.net_connections(kind='inet')
                active = []
                for c in conns:
                    if c.status == 'ESTABLISHED' and c.remote_address:
                        host = c.remote_address.ip
                        port = c.remote_address.port
                        active.append((host, port, "ESTABLISHED"))
                
                if active:
                    self.network_update.emit(active)
            except: pass
            time.sleep(5) # Refresh connections every 5s

class WindowControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Style
        style = """
            QPushButton {
                background: rgba(0, 224, 255, 0.1);
                border: 1px solid rgba(0, 224, 255, 0.3);
                color: #00e0ff;
                font-family: Consolas;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: rgba(0, 224, 255, 0.3);
                border: 1px solid #00e0ff;
            }
            QPushButton#closeBtn:hover {
                background: rgba(255, 68, 68, 0.3);
                border: 1px solid #ff4444;
                color: #ff4444;
            }
        """
        self.setStyleSheet(style)
        
        self.btn_min = QPushButton("_")
        self.btn_min.setFixedSize(30, 20)
        self.btn_min.setToolTip("Minimize")
        
        self.btn_max = QPushButton("[]")
        self.btn_max.setFixedSize(30, 20)
        self.btn_max.setToolTip("Maximize/Restore")

        self.btn_close = QPushButton("X")
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFixedSize(30, 20)
        self.btn_close.setToolTip("Close (Minimize to Tray)")
        
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

class PrivacyShield(QWidget):
    """Semi-transparent overlay to hide HUD contents when unauthorized persons are near."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background-color: rgba(0, 10, 20, 245);") # High opacity
        self.hide()
        
        self.layout = QVBoxLayout(self)
        self.label = QFrame(self)
        self.label.setFixedSize(600, 200)
        self.label.setStyleSheet("""
            QFrame {
                border: 2px solid #ff4444;
                background: rgba(255, 0, 0, 0.1);
                border-radius: 15px;
            }
        """)
        
        inner_layout = QVBoxLayout(self.label)
        self.title = QLabel("🛡️ SENTINEL PRIVACY SHIELD :: ACTIVE", self.label)
        self.title.setStyleSheet("color: #ff4444; font-size: 24px; font-weight: bold; border: none;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.msg = QLabel("Unauthorized biological presence detected. \nSystem data has been obfuscated for security.", self.label)
        self.msg.setStyleSheet("color: #ffffff; font-size: 14px; border: none;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        inner_layout.addWidget(self.title)
        inner_layout.addWidget(self.msg)
        
        self.layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)

class MasterHUD(QMainWindow):
    """
    JARVIS ELITE HUD - v8.0
    The clean, branded legacy interface.
    """
    def __init__(self):
        super().__init__()
        self.resize(1366, 768)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Enable dragging for frameless window
        self._drag_pos = None
        
        # 1. JARVIS CORE
        try:
            self.jarvis_core = VoiceJARVIS()
        except Exception as e:
            print(f"Error loading VoiceJARVIS: {e}")
            from agent import JARVIS
            self.jarvis_core = JARVIS()
            
        # 2. UI Setup
        print("[HUD DEBUG] Initializing UI...")
        self.init_ui()
        
        print("[HUD DEBUG] Initializing FaceAuth...")
        try:
            self.face_auth = FaceAuth()
        except Exception as fa_err:
            print(f"[HUD DEBUG] FaceAuth CRASH: {fa_err}")
            traceback.print_exc()
            self.face_auth = None
            
        # Dragging logic
        self._drag_pos = None
        
        # 2.1 Autonomy Worker
        print("[HUD DEBUG] Initializing Autonomy Worker...")
        try:
            from autonomy_worker import SystemAutonomy
            self.autonomy = SystemAutonomy(hud_callback=self._handle_autonomy_update)
        except Exception as au_err:
            print(f"[HUD DEBUG] Autonomy Worker CRASH: {au_err}")
            traceback.print_exc()
            self.autonomy = None
        
        # Security Scanner (Phase 4)
        print("[HUD DEBUG] Initializing Security Scanner...")
        try:
            self.security = SecurityScanner(alert_callback=self._handle_security_alert, face_auth=self.face_auth)
            self.security.start()
        except Exception as sc_err:
            print(f"[HUD DEBUG] Security Scanner CRASH: {sc_err}")
            self.security = None
        
        # Proactive Vision (Phase 4)
        # print("[HUD DEBUG] Initializing Proactive Vision...")
        # self.vision_pro = ProactiveVision(core=self, brain=self.jarvis_core.brain)
        # self.vision_pro.start()
        
        # 2.2 Global Eye (Phase 66)
        print("[HUD DEBUG] Initializing Global Eye...")
        try:
            from global_eye import GlobalEye
            self.global_eye = GlobalEye()
        except Exception as ge_err:
            print(f"[HUD DEBUG] Global Eye Error: {ge_err}")
            self.global_eye = None

        self.mood_timer = QTimer()
        self.mood_timer.timeout.connect(self._update_world_mood)
        # Check mood every 10 minutes to save API quota
        self.mood_timer.start(600000) 
        QTimer.singleShot(5000, self._update_world_mood) # Initial check
        
        # 2.3 Voice Cloning (Phase 67)
        print("[HUD DEBUG] Initializing Voice Cloning...")
        try:
            from voice_cloning import VoiceCloning
            self.voice_cloning = VoiceCloning()
        except Exception as vc_err:
            print(f"[HUD DEBUG] Voice Cloning Error: {vc_err}")
            self.voice_cloning = None

        # 2.4 Voice Biometrics (Elite v13.0)
        print("[HUD DEBUG] Initializing Voice Biometrics...")
        try:
            from voice_auth import VoiceAuth
            self.voice_auth = VoiceAuth(terminal_callback=self.left_panel.terminal.add_log)
            v_type = "NEURAL (ElevenLabs)" if (self.voice_cloning and self.voice_cloning.elevenlabs_available) else "LOCAL (XTTS)"
            self.left_panel.voice_node.set_voice_info(v_type)
        except Exception as vb_err:
            print(f"[HUD DEBUG] Voice Biometrics Error: {vb_err}")
            self.voice_auth = None

        # Inject Custom Voice into JARVIS Core
        self.jarvis_core.speak = self._neural_speak
        
        # Initialize Sentinel Presence
        import config
        config.SENTINEL_MODE["last_activity"] = time.time()
        
        # Connect Social Sentience to HUD (Elite v18.5)
        print("[HUD DEBUG] Initializing Social Sentience...")
        try:
            from social_sentience import HUD_CALLBACKS
            HUD_CALLBACKS.append(self.left_panel.telegram_node.add_log)
            
            # Start Background Telegram Monitor (No more 'database is locked')
            print("[HUD DEBUG] Starting Telegram Worker Thread...")
            self.tg_worker = TelegramWorker(self.jarvis_core)
            self.tg_worker.start()
            print("[HUD DEBUG] Telegram Worker Started.")
        except Exception as e:
            print(f"Social HUD Link Error: {e}")

        # 3.2 Initialize Bridge
        self.avatar = AvatarWidget() 
        self.avatar.setParent(self)
        self.avatar.move(590, 100) # Centered above the orb
        self.avatar.show()
        
        self.bridge = JARVISBridge(self.jarvis_core, self.core, self.avatar, hud_window=self)
        self.bridge.log_update.connect(self._handle_log)
        self.bridge.color_update.connect(self._update_theme_color)

        
        # Connect Speak Callback (Phase 4 Refinement)
        self.jarvis_core.on_speak = self.left_panel.add_log
        self.jarvis_core.on_research_log = self.left_panel.research.add_log # New link
        
        # 3. State & Animation Timer (Optimized FPS ~25)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_hud_state)
        self.timer.start(40) 
        
        # 4. Camera System
        if not config.GUI_SETTINGS.get("lite_mode"):
            self.cam_worker = CameraWorker(self.jarvis_core.executor.camera, face_auth=self.face_auth)
            self.cam_worker.frame_update.connect(self._update_camera_feed)
            self.cam_worker.raw_frame_update.connect(self.security.process_vision_frame)
            self.cam_worker.analysis_update.connect(self._update_vision_analysis)
            self.cam_worker.start()
        else:
            self.cam_worker = None
            print("[HUD DEBUG] Lite Mode: Camera System DISABLED.")


        # 4.1 Virtual Lock Screen (Hidden initially)
        self.lock_screen = HUDLockScreen(self.jarvis_core.executor.camera)
        self.lock_screen.unlocked.connect(self._deactivate_virtual_lock)
        self.lock_screen.hide()

        # Sentinel Mode Monitor (1 second interval)
        self.sentinel_timer = QTimer()
        self.sentinel_timer.timeout.connect(self._check_sentinel)
        self.sentinel_timer.start(1000)
        
        # Kernel Watchdog (Elite v12.0 - Self-Repair)
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self._kernel_watchdog)
        self.watchdog_timer.start(5000) # Check every 5s
        
        # 5. Screen System
        if not config.GUI_SETTINGS.get("lite_mode"):
            self.screen_worker = ScreenWorker()
            self.screen_worker.screen_update.connect(self._update_screen_feed)
            self.screen_worker.start()
        else:
            self.screen_worker = None
            print("[HUD DEBUG] Lite Mode: Screen Sync DISABLED.")

        # 5.1 Network Guardian (Serious Engineering v8.5)
        self.net_worker = NetworkWorker()
        self.net_worker.network_update.connect(self._update_radar_feed)
        self.net_worker.start()

        # Connect Bridge UI core
        self.bridge.ui_core = self.core
        
        # 5.2 Autonomous Ghost Mode (Elite v9.0)
        if not self.jarvis_core.hybrid_mode:
            from ghost_mode import JARVISGhostMode
            self.ghost = JARVISGhostMode(
                self.jarvis_core.executor, 
                terminal_callback=self.left_panel.terminal.add_log,
                brain=self.jarvis_core.brain,
                vision=self.jarvis_core.vision,
                evo_callback=self.left_panel.evo_node.set_repair_status
            )
            self.ghost.start()
        else:
            self.ghost = None

        # 5.3 Self-Evolution Engine (Elite v19.0)
        if not self.jarvis_core.hybrid_mode:
            from self_evolution import SelfEvolutionEngine
            self.evolution = SelfEvolutionEngine(
                brain=self.jarvis_core.brain,
                terminal_callback=self.left_panel.terminal.add_log,
                gamification=self.jarvis_core.executor.gamification
            )
            self.evolution.start()
        else:
            self.evolution = None

        # Evolution UI Update Timer
        self.evo_update_timer = QTimer(self)
        self.evo_update_timer.timeout.connect(self._update_evolution_ui)
        self.evo_update_timer.start(5000) # Every 5s
        
        # Connect Biometric Request (Elite v13.0)
        self.jarvis_core.executor.on_biometric_request = self._vocal_auth_challenge
        
        # Matrix Rain Effect (Background)
        if not config.GUI_SETTINGS.get("lite_mode"):
            self.matrix_rain = MatrixRain(self.width(), self.height())
            self.matrix_timer = QTimer(self)
            self.matrix_timer.timeout.connect(self._update_matrix)
            self.matrix_timer.start(50) # 20 FPS
        else:
            self.matrix_rain = None
            self.matrix_timer = None
            print("[HUD DEBUG] Lite Mode: Matrix Rain DISABLED.")

        # 6. Voice System (Background Listener)
        if not config.GUI_SETTINGS.get("lite_mode") and not "--silent" in sys.argv:
            self.voice_worker = VoiceWorker(self.jarvis_core)
            self.voice_worker.command_detected.connect(self._handle_voice_command)
            self.voice_worker.start()
        else:
            self.voice_worker = None
            print("[HUD DEBUG] Lite Mode: Local Voice Recognition DISABLED.")
            
        # 7. Privacy Shield Overlay
        print("[HUD DEBUG] Initializing Privacy Shield...")
        self.privacy_shield = PrivacyShield(self)
        self.privacy_shield.setGeometry(0, 0, self.width(), self.height())
        print("[HUD DEBUG] Privacy Shield initialized.")

        # 8. Real-Time Market Monitor (Phase 5 Link)
        if not config.GUI_SETTINGS.get("lite_mode") and not self.jarvis_core.hybrid_mode:
            from market_monitor import MarketMonitor
            self.market_monitor = MarketMonitor()
            self.market_timer = QTimer(self)
            self.market_timer.timeout.connect(self._update_market_metrics)
            self.market_timer.start(30000) # Every 30 seconds
            self._update_market_metrics() # Initial fetch
        else:
            self.market_monitor = None
            print("[HUD DEBUG] Market Monitor DISABLED.")
        print("[HUD DEBUG] MasterHUD Constructor COMPLETE.")

    def _update_market_metrics(self):
        """Fetch real data for FinancialDashboard"""
        def fetch():
            try:
                # We use simple prices for HUD panel
                # Convert symbolic responses to dict
                data = {
                    "BTC": self.market_monitor.get_raw_crypto_price("bitcoin"),
                    "ETH": self.market_monitor.get_raw_crypto_price("ethereum"),
                    "SOL": self.market_monitor.get_raw_crypto_price("solana")
                }

                QTimer.singleShot(0, lambda: self.right_panel.finance_node.update_market_data(data))
            except: pass
        threading.Thread(target=fetch, daemon=True).start()

    def update_hud_state(self):
        try:
            # Update Core Animation
            # self.core.update() # Core handles its own timer
            
            # Update Gamification Stats
            if hasattr(self.jarvis_core, 'executor') and hasattr(self.jarvis_core.executor, 'gamification'):
                self.right_panel.stats_node.update_stats(self.jarvis_core.executor.gamification)
            else:
                self.right_panel.stats_node.update_stats()

            # Update Sentience Level based on system load (Dynamic HUD)
            cpu = psutil.cpu_percent()
            if cpu > 80:
                self.status_bar.set_sentience("STRESS", "#ff4444")
            elif cpu > 50:
                self.status_bar.set_sentience("ACTIVE", "#ffaa00")
            else:
                self.status_bar.set_sentience("STABLE", "#00e0ff")
        except Exception as e:
            print(f"[HUD DEBUG] update_hud_state error: {e}")
            
        # 🔄 Update Storage Info in HUD
        # free_gb = self.autonomy.get_disk_info()
        # self.right_panel.storage_node.update_storage(free_gb)

    def _handle_autonomy_update(self, status, progress):
        """Autonomy ishchilari holatini HUD-da aks ettirish"""
        # self.right_panel.storage_node.update_storage(self.autonomy.get_disk_info(), status, progress)
        pass

    def _handle_voice_command(self, text):
        if not self.mute_btn.isChecked(): # Only process if MIC ON
            if text == "WAKE_UP_TRIGGER":
                # Visual Feedback for "Hey JARVIS"
                self.core.set_active(True) # Pulse visualizer
                self.bridge.log_update.emit("🎤 I am listening, Sir...")
                QTimer.singleShot(2000, lambda: self.core.set_active(False))
                return

            print(f"🎤 JARVIS HEARD -> '{text}'") # Console Debug
            
            # Direct Autonomy Command Check
            cmd = text.lower()
            if "clean system" in cmd or "tozalash" in cmd or "davola" in cmd:
                self.left_panel.terminal.add_log("🧹 INITIATING SYSTEM HEALER...")
                self.left_panel.healer_node.set_status("HEALING...", 40)
                
                def run_heal():
                    res = self.jarvis_core.executor.execute({"action": "system_healer", "parameters": {}})
                    self.left_panel.healer_node.set_status("OPTIMAL", 100)
                    self.left_panel.terminal.add_log(f"✅ {res.get('result', 'Heal complete')}")
                    
                threading.Thread(target=run_heal, daemon=True).start()
                return

            
            if "organize desktop" in cmd or "tartiblash" in cmd:
                self.left_panel.terminal.add_log("📂 INITIATING DESKTOP ORGANIZER...")
                threading.Thread(target=self.autonomy.organize_desktop, daemon=True).start()
                return

            self.bridge.run_command(text)

    def _update_evolution_ui(self):
        """Mustaqil rivojlanish ma'lumotlarini HUD-da aks ettirish"""
        if hasattr(self, 'evolution') and hasattr(self.left_panel, 'evo_node'):
            level = self.evolution.stats.get("sentience_level", 1)
            xp = self.evolution.stats.get("experience_points", 0)
            self.left_panel.evo_node.set_evolution_data(level, xp)

    def _trigger_research(self, topic):
        """HUD-dan to'g'ridan-to'g'ri tadqiqotni boshlash"""
        self.left_panel.terminal.add_log(f"🔎 INITIATING RESEARCH: {topic}")
        self.status_bar.set_sentience("RESEARCHING", "#ffaa00")
        
        def _res_worker():
            from research_assistant import ResearchAssistant
            import asyncio
            ra = ResearchAssistant()
            # Feed logs to HUD research terminal
            ra.logger.info = lambda msg: self.left_panel.research.add_log(msg)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(ra.perform_research(topic, format="word"))
            
            self.left_panel.terminal.add_log(f"✅ RESEARCH COMPLETE")
            self.jarvis_core.speak(f"Janob, {topic} bo'yicha tadqiqot yakunlandi. Word hujjati tayyor.")
            self.status_bar.set_sentience("STABLE", "#00e0ff")
            
        threading.Thread(target=_res_worker, daemon=True).start()

    def _update_world_mood(self):
        """Dunyodagi trendlarni tahlil qilish va HUD-ni yangilash"""
        def _task():
            data = self.global_eye.analyze_world()
            # Update UI safely
            QTimer.singleShot(0, lambda: self.right_panel.mood_node.update_mood(
                data.get("mood", "STABLE"),
                data.get("summary", "Status normal."),
                data.get("color", "#00e0ff")
            ))
            
            # If mood is CRITICAL, notify via log
            if data.get("mood") == "CRITICAL":
                QTimer.singleShot(0, lambda: self.left_panel.terminal.add_log(f"🌍 GLOBAL ALERT: {data.get('summary')}"))
                
        threading.Thread(target=_task, daemon=True).start()

    def _vocal_auth_challenge(self, callback=None):
        """Perform a spectral voice verification sequence (Elite v13.0)"""
        def run_auth():
            self.core.set_active(True) # Visual pulse during scan
            self.left_panel.terminal.add_log("🎙️ BIOMETRIC_SCAN: Initiated. Please speak for identification...")
            
            success = self.voice_auth.authenticate()
            
            self.core.set_active(False)
            if success:
                self.status_bar.set_sentience("ACCESS GRANTED", "#00ff88")
                if callback: callback(True)
            else:
                self.status_bar.set_sentience("ACCESS DENIED", "#ff0033")
                if callback: callback(False)
                
        threading.Thread(target=run_auth, daemon=True).start()

    def _update_vision_analysis(self, data):
        """Fon tahlili natijalarini HUD-da aks ettirish (Smooth UI)"""
        import config
        
        # 1. Update Security Dashboard
        user = data.get("user", "UNKNOWN")
        confidence = data.get("confidence", 0)
        authorized = data.get("authorized", False)
        face_detected = data.get("face_detected", False)
        
        if authorized:
            config.SENTINEL_MODE["is_authorized"] = True # Sync for Vault access
            self.left_panel.security_node.update_security_status("AUTHORIZED", user=user)
            self.is_privacy_active = False
            self.left_panel.terminal.set_privacy(False)
            self.left_panel.research.set_privacy(False)
            
            if hasattr(self, 'privacy_shield'): self.privacy_shield.hide()
            if config.SENTINEL_MODE.get("is_locked"):
                self.left_panel.add_log(f"👤 FACE ID: Identified (Conf: {int(confidence)})")
                self._deactivate_virtual_lock()
            
            # Bio-Sync: React to user emotion
            emotion = data.get("emotion", "NEUTRAL")
            self._sync_bio_state(emotion)
            
            # Posture Update
            self.right_panel.posture_node.set_posture(data["posture_score"], data["posture_status"])
        else:
            config.SENTINEL_MODE["is_authorized"] = False # Reset
            if face_detected:
                self.is_privacy_active = True
                self.left_panel.terminal.set_privacy(True)
                self.left_panel.research.set_privacy(True)
                
                self.left_panel.security_node.update_security_status("UNKNOWN", user="???", alert="HIGH", privacy=True)
                self._set_hud_alert_mode(True)
                if hasattr(self, 'privacy_shield'): 
                    self.privacy_shield.show()
                    self.privacy_shield.raise_()
                
                # Privacy Shield log
                if not hasattr(self, "_last_privacy_trigger") or time.time() - self._last_privacy_trigger > 60:
                    # self._engage_privacy_shield()
                    self._last_privacy_trigger = time.time()
            else:
                self.is_privacy_active = False
                self.left_panel.terminal.set_privacy(False)
                self.left_panel.research.set_privacy(False)
                
                self.left_panel.security_node.update_security_status("SECURE", alert="LOW", privacy=False)
                self._set_hud_alert_mode(False)
                self.right_panel.posture_node.set_posture(100, "NO DATA")
                if hasattr(self, 'privacy_shield'): self.privacy_shield.hide()

    def _sync_bio_state(self, emotion):
        """Sync HUD state with User Biometrics (Emotion) - Elite v15.0"""
        if not hasattr(self, "_last_mood_log"): self._last_mood_log = "NEUTRAL"
        if not hasattr(self, "_last_mood_time"): self._last_mood_time = 0
        
        # Debounce: Only update if emotion changed AND > 10 seconds passed (unless critical)
        if self._last_mood_log == emotion: return
        if time.time() - self._last_mood_time < 10 and emotion not in ["ANGRY", "STRESSED"]: return

        if emotion == "HAPPY":
            config.CURRENT_TEMPERAMENT = "ENTHUSIASTIC"
            self._update_theme_color("#ffd700") # Gold for joy
            self.status_bar.set_sentience("BIO-SYNC: QUVNOQ", "#ffd700")
            self.left_panel.terminal.add_log("🧠 BIO-SYNC: Ijobiy holat aniqlandi. G'ayratli rejim faollashdi.")
            
        elif emotion in ["TIRED", "SAD"]:
            config.CURRENT_TEMPERAMENT = "CALM"
            self._update_theme_color("#aa88ff") # Electric Purple for Focus
            self.status_bar.set_sentience("BIO-SYNC: KAM QUVVAT", "#aa88ff")
            self.left_panel.terminal.add_log("🧠 BIO-SYNC: Charchoq aniqlandi. Tinch rejimga o'tilmoqda.")

        elif emotion in ["ANGRY", "STRESSED"]:
            config.CURRENT_TEMPERAMENT = "CALM"
            self._update_theme_color("#ff8800") # Amber for Stress
            self.status_bar.set_sentience("BIO-SYNC: STRESS", "#ff8800")
            self.left_panel.terminal.add_log("⚠️ BIO-SYNC: Yuqori stress aniqlandi. Tizim yuki kamaytirildi.")

        else: # NEUTRAL
            config.CURRENT_TEMPERAMENT = "PROFESSIONAL"
            self._update_theme_color("#00e0ff") # Cyan (Default)
            self.status_bar.set_sentience("BIO-SYNC: BARQAROR", "#00e0ff")
            self.left_panel.terminal.add_log("🧠 BIO-SYNC: Holat normallashdi. Professional rejim faol.")

        self._last_mood_log = emotion
        self._last_mood_time = time.time()



    def speak(self, text):
        """Redirect speak calls to neural engine (Elite v16.0)"""
        self._neural_speak(text)

    def _neural_speak(self, text):
        """Standard speak o'rniga Neural ovozdan foydalanish"""
        def _speak_task():
            self.core.set_active(True) # Pulse on speak
            self.left_panel.voice_node.set_voice_info(self.left_panel.voice_node.voice_type, syncing=True)
            self.left_panel.terminal.add_log(text)
            
            # Try Voice Cloning first
            res = self.voice_cloning.speak_with_custom_voice(text)
            
            # Fallback if cloning failed or not configured
            if not res or "failed" in str(res).lower() or "not configured" in str(res).lower():
                if hasattr(self.jarvis_core, 'voice') and self.jarvis_core.voice:
                    # Use standard TTS (Edge or pyttsx3)
                    self.jarvis_core.voice.speak(text)

            self.left_panel.voice_node.set_voice_info(self.left_panel.voice_node.voice_type, syncing=False)
            self.core.set_active(False)
            
        threading.Thread(target=_speak_task, daemon=True).start()

    def _update_camera_feed(self, frame):
        """Kamera kadrini HUD-da ko'rsatish (Processing endi worker'da)"""
        priv = getattr(self, 'is_privacy_active', False)
        self.right_panel.update_camera(frame, is_private=priv)

    def _engage_privacy_shield(self):
        """Notanish shaxs aniqlanganda ogohlantirish (Minimize o'chirildi - USER request)"""
        self.left_panel.terminal.add_log("🛡️ PRIVACY ALERT: Unauthorized person detected near the system.")
        # self.jarvis_core.speak("Janob, begona shaxs aniqlandi.") 

    def _set_hud_alert_mode(self, active):
        if active:
            self.status_bar.set_sentience("RED ALERT", "#ff0000")
            self.core.cyan = QColor("#ff0000")
        else:
            self.core.cyan = QColor("#00e0ff")

    def _update_screen_feed(self, frame):
        priv = getattr(self, 'is_privacy_active', False)
        self.right_panel.update_screen(frame, is_private=priv)

    def _update_radar_feed(self, connections):
        """Update the radar node with real connections"""
        if hasattr(self.right_panel, 'radar_node'):
            self.right_panel.radar_node.update_radar(connections)

    def _kernel_watchdog(self):
        """Monitor and restart crashed workers (Self-Repair)"""
        # 1. Camera Worker
        if self.cam_worker and not self.cam_worker.isRunning():
            self.left_panel.terminal.add_log("🔧 [KERNEL] Camera worker died. Restarting...")
            self.cam_worker.start()
            
        # 2. Screen Worker
        if self.screen_worker and not self.screen_worker.isRunning():
            self.left_panel.terminal.add_log("🔧 [YADRO] Ekran jarayoni to'xtadi. Qayta yuklanmoqda...")
            self.screen_worker.start()
            
        # 3. Network Worker
        if not self.net_worker.isRunning():
            self.left_panel.terminal.add_log("🔧 [YADRO] Tarmoq jarayoni to'xtadi. Qayta yuklanmoqda...")
            self.net_worker.start()
            
        # 4. Ghost Mode
        if not hasattr(self, 'ghost') or not self.ghost.is_alive():
            self.left_panel.terminal.add_log("🔧 [YADRO] Ghost jarayoni to'xtadi. Qayta tiklanmoqda...")

            from ghost_mode import JARVISGhostMode
            self.ghost = JARVISGhostMode(
                self.jarvis_core.executor, 
                terminal_callback=self.left_panel.terminal.add_log,
                evo_callback=self.left_panel.evo_node.set_repair_status
            )
            self.ghost.start()

    def _handle_log(self, text):
        # Pipe logs to the left terminal panel
        self.left_panel.add_log(text)
        
        # Emit intelligence particles (Elite v13.0)
        if hasattr(self.core, 'emit_particles'):
            self.core.emit_particles(3) # Small burst for each log
            
        # Activate visualizer briefly on log (Only if MIC is ON)
        if hasattr(self, 'mute_btn') and not self.mute_btn.isChecked():
            self.core.set_active(True)
            QTimer.singleShot(500, lambda: self.core.set_active(False))
            
    def _update_theme_color(self, hex_code):
        """Dynamic Theme Update (Emotional AI)"""
        try:
            # Update Core (Center Orb)
            self.core.set_theme_color(hex_code)
            
            # Update Status Bar
            self.status_bar.set_sentience(self.status_bar.sentience_status, hex_code)
            
            # Optional: Update Panels if supported (HUDMasterPanels would need update method)
            # self.left_panel.update_color(hex_code) 
            
        except Exception as e:
            print(f"Theme update error: {e}")

    def _handle_security_alert(self, level, message):
        """Security scanner xabarlarini HUD logiga yo'naltirish"""
        icon = "🚨" if level == "CRITICAL" else "⚠️"
        
        if level == "CRITICAL" or (level == "WARNING" and "Notanish" in message):
            self.jarvis_core.speak(f"{icon} Janob, xavfsizlik ogohlantirishi. {message}")
            if hasattr(self, 'privacy_shield'):
                self.privacy_shield.show()
                self.privacy_shield.raise_()
        else:
            # SHUNCHAKI LOG (ovozsiz)
            self.left_panel.add_log(f"{icon} SECURITY [{level}]: {message}")


    def _update_matrix(self):
        if hasattr(self, 'matrix_rain') and self.matrix_rain.active:
            self.matrix_rain.update()
            self.update() # Trigger paintEvent

    def _check_sentinel(self):
        """Sentinel Mode monitor logic"""
        import config

        # 0. Always check Blackout (17:00-19:00)
        self._check_blackout()

        if not config.SENTINEL_MODE.get("enabled", False):
            return

        # 1. Check if we should unlock via voice signal
        if config.SENTINEL_MODE.get("is_locked"):
            if config.SENTINEL_MODE.get("should_unlock"):
                self._deactivate_virtual_lock()
                config.SENTINEL_MODE["should_unlock"] = False
            return

        # Use centralized last_activity from config
        absence_duration = time.time() - config.SENTINEL_MODE.get("last_activity", time.time())

        # Warning before lock
        warn_threshold = config.SENTINEL_MODE["timeout"] - config.SENTINEL_MODE["warn_at"]
        if absence_duration > warn_threshold:
            if time.time() - config.SENTINEL_MODE["last_warn_time"] > 10:
                remaining = int(config.SENTINEL_MODE["timeout"] - absence_duration)
                if remaining > 0:
                    # Speak warning (which also logs it via on_speak)
                    self.jarvis_core.speak(f"Janob, sentinel tizimi ishga tushmoqda. {remaining} soniyadan keyin tizim qulflanadi.")
                    config.SENTINEL_MODE["last_warn_time"] = time.time()

        # Lock screen
        if absence_duration >= config.SENTINEL_MODE["timeout"]:
            self.left_panel.add_log("🛑 SENTINEL: LOCKING SYSTEM NOW.")
            # Trigger lock via bridge/core
            if config.SENTINEL_MODE.get("use_virtual_lock", False):
                self._activate_virtual_lock()
            else:
                self.bridge.run_command("lock screen")

    def _check_blackout(self):
        """17:00 - 19:00 Blackout enforcement"""
        import config
        if not config.BLACKOUT_SETTINGS.get("enabled", False):
            return
            
        now = datetime.datetime.now().strftime("%H:%M")
        start = config.BLACKOUT_SETTINGS["start_time"]
        end = config.BLACKOUT_SETTINGS["end_time"]
        
        # Simple string comparison for time range
        if start <= now < end:
            # Check for active pause
            if time.time() < config.BLACKOUT_SETTINGS.get("paused_until", 0):
                remaining_pause = int((config.BLACKOUT_SETTINGS["paused_until"] - time.time()) / 60)
                if remaining_pause > 0:
                    # Log pause status only once per minute to avoid spam
                    if not hasattr(self, "_last_pause_log") or time.time() - self._last_pause_log > 60:
                        self.left_panel.add_log(f"⏳ BLACKOUT: Paused. Remaining: {remaining_pause}m")
                        self._last_pause_log = time.time()
                return

            self.left_panel.add_log("🌑 BLACKOUT PROTOCOL ENFORCED. Shutting down...")
            # Give 5 seconds to read
            QTimer.singleShot(5000, lambda: os.system("shutdown /s /t 1"))

    def _activate_virtual_lock(self):
        import config
        if not config.SENTINEL_MODE["is_locked"]:
            config.SENTINEL_MODE["is_locked"] = True
            self.lock_screen.showFullScreen()
            self.lock_screen._can_close = False # Block closing
            # Auto-enable MIC (important for voice unlock)
            self.mute_btn.setChecked(False)
            self._toggle_mute() # Refresh UI & state
            
            self.left_panel.add_log("🔐 SYSTEM VIRTUAL LOCK ACTIVATED.")
            self.jarvis_core.speak("Tizim qulflandi, janob.")

    def _deactivate_virtual_lock(self):
        import config
        if config.SENTINEL_MODE["is_locked"]:
            config.SENTINEL_MODE["is_locked"] = False
            config.SENTINEL_MODE["last_activity"] = time.time() # FIX: Reset timer
            self.lock_screen._can_close = True # Allow closing
            self.lock_screen.unlock()
            self.left_panel.add_log("🔓 SYSTEM UNLOCKED.")
            self.jarvis_core.speak("Xush kelibsiz, janob.")

    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # A. TOP STATUS BAR (Sleek)
        self.status_bar = HUDStatusBar()
        self.main_layout.addWidget(self.status_bar)
        
        # Window Controls (Floating)
        self.win_controls = WindowControls(self)
        self.win_controls.move(self.width() - 140, 15)
        self.win_controls.btn_min.clicked.connect(self.showMinimized)
        self.win_controls.btn_max.clicked.connect(self.toggle_maximize)
        self.win_controls.btn_close.clicked.connect(self.close)
        self.win_controls.show()

        # B. MIDDLE CONTENT (Balanced 3-Col Layout)
        self.mid_container = QWidget()
        self.mid_layout = QHBoxLayout(self.mid_container)
        # optimize margins for 1366px width (30px side margins)
        self.mid_layout.setContentsMargins(30, 10, 30, 10) 
        self.mid_layout.setSpacing(50) # Reduced spacing for tighter look
        
        self.left_panel = HUDMasterPanels("left")
        self.right_panel = HUDMasterPanels("right")
        self.core = HUDCoreMaster()
        
        # 30% - 40% - 30% ratio
        self.mid_layout.addWidget(self.left_panel, 3) 
        self.mid_layout.addWidget(self.core, 4)       
        self.mid_layout.addWidget(self.right_panel, 3)
        
        self.main_layout.addWidget(self.mid_container, 1)
 
        # C. FOOTER (Integrated Input)
        self.footer_container = QWidget()
        self.footer_container.setFixedHeight(90)
        self.footer_layout = QHBoxLayout(self.footer_container)
        self.footer_layout.setContentsMargins(50, 0, 50, 25)
        self.footer_layout.setSpacing(20)
 
        # Mute Button (Hex Style)
        self.mute_btn = QPushButton("🔊 MIC: ON")
        self.mute_btn.setFixedSize(110, 45)
        self.mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mute_btn.setStyleSheet(self._get_btn_style())
        self.mute_btn.setCheckable(True)
        self.mute_btn.clicked.connect(self._toggle_mute)
        self.footer_layout.addWidget(self.mute_btn)
        
        # Tools (Vision, Boost)
        self.vision_btn = QPushButton("👁️")
        self.vision_btn.setFixedSize(50, 45)
        self.vision_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vision_btn.setStatusTip("Analyze Screen Content")
        self.vision_btn.setStyleSheet(self._get_btn_style())
        self.vision_btn.clicked.connect(self._analyze_vision)
        self.footer_layout.addWidget(self.vision_btn)

        self.boost_btn = QPushButton("⚡")
        self.boost_btn.setFixedSize(50, 45)
        self.boost_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boost_btn.setStatusTip("Optimize System")
        self.boost_btn.setStyleSheet(self._get_btn_style())
        self.boost_btn.clicked.connect(self._boost_system)
        self.footer_layout.addWidget(self.boost_btn)
        
        # Matrix and Focus buttons removed as 'keraksiz'

        # Input Field (Futuristic)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("AWAITING INSTRUCTION...")
        self.input_field.setFixedHeight(45)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(5, 10, 15, 220);
                border: 1px solid rgba(0, 224, 255, 50);
                border-left: 3px solid #00e0ff;
                border-radius: 0px;
                color: #ffffff;
                font-family: 'Consolas';
                font-size: 14px;
                padding-left: 15px;
                letter-spacing: 1px;
            }
            QLineEdit:focus {
                border: 1px solid #00e0ff;
                border-left: 3px solid #ffffff;
                background-color: rgba(10, 20, 30, 240);
            }
        """)
        self.input_field.returnPressed.connect(self._send_command)
        self.footer_layout.addWidget(self.input_field)
        
        self.main_layout.addWidget(self.footer_container)
        self.setStyleSheet("background-color: transparent;")

    def _get_btn_style(self):
        return """
            QPushButton {
                background-color: rgba(0, 20, 30, 200);
                border: 1px solid #00e0ff;
                border-bottom: 3px solid #00e0ff;
                color: #00e0ff;
                font-weight: bold;
                font-family: 'Outfit';
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(0, 224, 255, 30);
            }
            QPushButton:checked {
                background-color: rgba(255, 20, 20, 50);
                border: 1px solid #ff4444;
                border-bottom: 3px solid #ff4444;
                color: #ff4444;
                text-align: center;
            }
        """

    def _prepare_youtube_search(self):
        """Pre-fill command for YT search"""
        self.input_field.setFocus()
        self.input_field.setText("play on youtube ")

    def _cycle_theme(self):
        """Cycle through predefined visual themes"""
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        
        self.theme_index = (self.theme_index + 1) % len(self.themes)
        theme_name, color_hex = self.themes[self.theme_index]
        
        self.current_theme_color = QColor(color_hex)
        self.left_panel.add_log(f"🎨 PROTOCOL: Switched to {theme_name} MODE")
        
        # Update Core & Status
        self.core.set_theme_color(color_hex)
        self.status_bar.set_sentience(f"{theme_name} PROTOCOL", color_hex)
        
        # Update Footer Buttons Style
        new_style = self._get_btn_style().replace("#00e0ff", color_hex).replace("rgba(0, 224, 255, 30)", f"rgba({self.current_theme_color.red()}, {self.current_theme_color.green()}, {self.current_theme_color.blue()}, 30)")
        for btn in [self.mute_btn, self.vision_btn, self.boost_btn]:
            if hasattr(self, 'theme_btn') and btn == self.theme_btn: continue # Skip if missing
            try:
                btn.setStyleSheet(new_style)
            except: pass
            
        self.update() # Repaint main window grid

    def _analyze_vision(self):
        # Debounce to prevent API spam
        if hasattr(self, "_last_vision_time") and time.time() - self._last_vision_time < 20:
             self.left_panel.add_log("⏳ VISION: Tizim sovishi kutilyapti...")
             return
             
        self._last_vision_time = time.time()
        self.left_panel.add_log("👁️ VISION: Capturing screen for analysis...")
        self.bridge.run_command("describe screen")

    def _toggle_focus(self):
        if self.focus_btn.isChecked():
            self.left_panel.add_log("🧘 FOCUS MODE: ENGAGED.")
            self.bridge.run_command("enable focus mode")
            self.focus_btn.setStyleSheet(self._get_btn_style().replace("border-bottom: 3px solid #ff4444", "border-bottom: 3px solid #00ff00").replace("color: #ff4444", "color: #00ff00"))
        else:
            self.left_panel.add_log("🧘 FOCUS MODE: DISENGAGED.")
            self.bridge.run_command("disable focus mode")
            self.focus_btn.setStyleSheet(self._get_btn_style())

    def _toggle_matrix(self):
        if self.matrix_rain and self.matrix_btn.isChecked():
            self.matrix_rain.active = True
            self.matrix_rain.resize(self.width(), self.height())
        elif self.matrix_rain:
            self.matrix_rain.active = False
            self.update()

    def _boost_system(self):
        self.left_panel.add_log("⚡ BOOST: Dumping memory & cache...")
        self.bridge.run_command("optimize system")

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _toggle_mute(self):
        if self.mute_btn.isChecked():
            self.mute_btn.setText("🔇 MIC: OFF")
            self.core.set_active(False)
        else:
            self.mute_btn.setText("🔊 MIC: ON")

    def _send_command(self):
        text = self.input_field.text().strip()
        if text:
            self.bridge.run_command(text)
            self.input_field.clear()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        
        # 1. DEEP VOID BACKGROUND (Slight Blue Tint)
        painter.fillRect(self.rect(), QColor(2, 4, 8, 250))
        
        # 1.B MATRIX RAIN LAYER
        if self.matrix_rain and self.matrix_rain.active:
            self.matrix_rain.draw(painter)
        
        # 2. HEX GRID PATTERN (Subtle)
        self.draw_hex_grid(painter, w, h)
        
        # 3. DATE/TIME (Top Right Corner)
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        painter.setPen(QPen(QColor(0, 224, 255, 200), 1))
        painter.setFont(QFont("Outfit", 28, QFont.Weight.Bold))
        painter.drawText(w-130, 80, time_str)
        
        painter.setFont(QFont("Outfit", 10))
        painter.setPen(QPen(QColor(0, 224, 255, 100), 1))
        painter.drawText(w-130, 95, now.strftime("%A, %b %d").upper())

        # 4. VIGNETTE
        grad = QRadialGradient(float(w/2), float(h/2), float(w/1.2))
        grad.setColorAt(0, Qt.GlobalColor.transparent)
        grad.setColorAt(1, QColor(0, 0, 0, 200))
        painter.fillRect(self.rect(), grad)

    def draw_hex_grid(self, painter, w, h):
        """Draws a faint hexagonal mesh background"""
        painter.setPen(QPen(QColor(0, 224, 255, 8), 1))
        size = 40
        for y in range(0, h + size, size):
            offset = (size // 2) if (y // size) % 2 == 1 else 0
            for x in range(0 - size, w + size, size):
                # Simple dots for vertices instead of full hex to save CPU
                painter.drawPoint(x + offset, y)
                # Optional: draw small crosses
                if x % (size*4) == 0 and y % (size*4) == 0:
                     painter.drawLine(x+offset-2, y, x+offset+2, y)
                     painter.drawLine(x+offset, y-2, x+offset, y+2)
        painter.setPen(QPen(QColor(0, 224, 255, 12), 0.5))
        spacing = 200 # Wide and clean
        s = 3 # Small precision cross
        for x in range(0, w, spacing):
            for y in range(0, h, spacing):
                painter.drawLine(x-s, y, x+s, y)
                painter.drawLine(x, y-s, x, y+s)
        
        # Ultra-subtle corner guides
        painter.setPen(QPen(QColor(0, 224, 255, 30), 0.5))
        L = 40
        painter.drawLine(10, 10, 10+L, 10); painter.drawLine(10, 10, 10, 10+L) # TL
        painter.drawLine(w-10, h-10, w-10-L, h-10); painter.drawLine(w-10, h-10, w-10, h-10-L) # BR

    def resizeEvent(self, event):
        """Reposition floating elements on resize"""
        if hasattr(self, 'win_controls'):
            self.win_controls.move(self.width() - 140, 10)
            self.win_controls.raise_()
            
        if hasattr(self, 'avatar') and self.avatar:
            # Position avatar top-center, slightly below status bar
            aw, ah = self.avatar.width(), self.avatar.height()
            self.avatar.move(int((self.width() - aw) / 2), 60)
            self.avatar.raise_()
            
        if hasattr(self, 'privacy_shield'):
            self.privacy_shield.setGeometry(0, 0, self.width(), self.height())
            self.privacy_shield.raise_()
            
    def closeEvent(self, event):
        """No-Exit Policy: JARVIS ni yopib bo'lmaydi, faqat minimize bo'ladi"""
        event.ignore()
        self.showMinimized()
        self.left_panel.add_log("🔐 PERSISTENCE: JARVIS cannot be closed, only minimized.")

    def keyPressEvent(self, event):
        # Activity detected!
        import config
        config.SENTINEL_MODE["last_activity"] = time.time()
        
        # Block Alt+F4 manually if needed (though closeEvent handles it)
        if event.key() == Qt.Key.Key_F4 and event.modifiers() & Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return

        if event.key() == Qt.Key.Key_Escape:
            # Instead of closing, minimize to keep JARVIS active in background
            self.showMinimized()
            self.left_panel.add_log("📉 HUD minimized. JARVIS still active.")

    # --- Frameless Window Dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

if __name__ == "__main__":
    print("[HUD DEBUG] Loading QApplication...")
    app = QApplication(sys.argv)
    print("[HUD DEBUG] Creating MasterHUD Window...")
    try:
        window = MasterHUD()
        print("[HUD DEBUG] Showing Window...")
        window.show()
        window.raise_()
        window.activateWindow()
        print("[HUD DEBUG] Executing App Loop...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"[HUD CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()
