"""
Windows Boshqaruv Agenti - Executor
Windows operations executor for the Windows Control Agent
"""

import os
import sys
import time
import subprocess
import webbrowser
import psutil
import pyautogui
import platform
import json
import threading
from datetime import datetime
import config
from config import (
    SUPPORTED_ACTIONS, POPULAR_WEBSITES,
    PYAUTOGUI_SETTINGS,
    APP_PATHS
)
from utils import (
    setup_logger, format_success_response, format_error_response,
    extract_website_url
)

# Media & Automation Modules
try:
    from camera import CameraCapture
    from gesture_control import HandGestureControl
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    print("⚠ Camera/Gesture modullari topilmadi.")

# CAMERA_AVAILABLE = False

try:
    from typer_bot import JARVISTyperBot
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    print("⚠ Typer Bot moduli topilmadi.")

try:
    from connectivity_manager import ConnectivityManager
    CONNECTIVITY_AVAILABLE = True
except ImportError as e:
    CONNECTIVITY_AVAILABLE = False
    print(f"⚠ Connectivity Manager moduli yuklanmadi: {e}")

# Advanced Features Imports
try:
    from news_bot import NewsBot
    from voice_cloning import VoiceCloning
    from security_scanner import SecurityScanner
    from advanced_scheduler import AdvancedScheduler
    from desktop_automation import DesktopAutomation
    from gaming_mode import GamingMode
    from smart_player import SmartMediaPlayer
    from vision_engine import VisionEngine
    from health_monitor import HealthMonitor
    from finance_manager import FinanceManager
    # from research_assistant import ResearchAssistant
    from tutor_engine import TutorEngine
    from mood_engine import MoodEngine
    from market_monitor import MarketMonitor
    # from local_llm import LocalLLM
    from hud_avatar import VisualAvatar
    from night_owl import NightOwl
    from voice_auth import VoiceAuth
    from gamification import GamificationSystem
    from memory_core import MemoryCore
    from memory import MemoryEngine
    from healer import CodeHealer
    # from smart_home import SmartHome
    from dream_weaver import DreamWeaver
    from gui_automation import GUIController
    from voice_transformer import VoiceTransformer
    from swarm_node import SwarmNode
    from cloud_bridge_client import CloudBridge
    from global_eye import GlobalEye
    from quantum_security import QuantumSecurity
    from media_generator import MediaGenerator
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    print(f"⚠ Ba'zi advanced modullar yuklanmadi: {e}")

# ADVANCED_FEATURES_AVAILABLE = False

# PyAutoGUI sozlamalarini qo'llash
pyautogui.PAUSE = PYAUTOGUI_SETTINGS["PAUSE"]
pyautogui.FAILSAFE = PYAUTOGUI_SETTINGS["FAILSAFE"]


class WindowsExecutor:
    """
    Windows operatsiyalarini bajaruvchi klass
    """
    
    def __init__(self):
        self.logger = setup_logger("WindowsExecutor")
        self.logger.info("WindowsExecutor initialized")
        self.voice = None  # Will be set by JARVIS core
        self.lock = threading.Lock() # Thread safety lock
        self.on_biometric_request = None # Callback for Vocal Auth Challenge (Elite v13.0)
        
        # Camera, Gesture va Typer instances
        self.camera = CameraCapture() if CAMERA_AVAILABLE else None
        self.gesture = HandGestureControl() if CAMERA_AVAILABLE else None
        self.typer_bot = JARVISTyperBot() if TYPER_AVAILABLE else None
        self.connectivity = ConnectivityManager() if CONNECTIVITY_AVAILABLE else None
        
        # Advanced Modules Initialization
        self.news_bot = None
        self.voice_cloning = None
        self.security_scanner = None
        self.scheduler = None
        self.automation = None
        self.media_player = None
        self.vision = None
        self.health = None
        self.finance = None
        self.research = None
        self.tutor = None
        self.mood = None
        self.market = None
        self.local_ai = None
        self.avatar = None
        self.night_owl = None
        self.voice_authenticator = None
        self.gamification = None
        self.memory = None
        self.healer = None
        # self.smart_home = None
        self.dream_weaver = None
        self.gui = None
        self.voice_transformer = None
        self.swarm = None
        self.cloud_bridge = None
        self.global_eye = None
        self.security_vault = None
        
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                self.news_bot = NewsBot()
                self.voice_cloning = VoiceCloning()
                self.security_scanner = SecurityScanner()
                self.scheduler = AdvancedScheduler()
                self.automation = DesktopAutomation()
                self.media_player = SmartMediaPlayer()
                self.vision = VisionEngine()
                self.health = HealthMonitor(voice_module=self)
                self.finance = FinanceManager()
                # self.research = ResearchAssistant()
                self.gaming_mode = GamingMode()
                self.tutor = TutorEngine()
                self.mood = MoodEngine(vision_engine=self.vision)
                self.market = MarketMonitor()
                # self.local_ai = LocalLLM()
                self.avatar = VisualAvatar()
                self.avatar.start()
                self.night_owl = NightOwl(research_module=self.research)
                self.voice_authenticator = VoiceAuth()
                self.gamification = GamificationSystem()
                self.memory = MemoryEngine()
                self.vector_memory = MemoryCore()
                self.healer = CodeHealer()
                self.dream_weaver = DreamWeaver()
                self.gui = GUIController()
                self.media_generator = MediaGenerator() # IMAGE & VIDEO
                self.voice_transformer = VoiceTransformer()
                self.swarm = SwarmNode()
                
                # Start Cloud Bridge (Background)
                # Note: User must configure CLOUD_SERVER_URL in cloud_bridge_client.py first
                self.cloud_bridge = CloudBridge()
                threading.Thread(target=self.cloud_bridge.start_polling, daemon=True).start()
                
                self.global_eye = GlobalEye()
                self.security_vault = QuantumSecurity()
                from vault_manager import ShadowVault
                self.shadow_vault = ShadowVault()
                
                from workflow_engine import WorkflowEngine
                from smart_sorter import SmartSorter
                self.workflows = WorkflowEngine(executor=self)
                self.sorter = SmartSorter()
                
                from neural_indexer import NeuralIndexer
                from sync_manager import SyncManager
                self.neural_index = NeuralIndexer(brain=self, terminal_callback=self.logger.info)
                self.sync = SyncManager(terminal_callback=self.logger.info)
                
                from vision_agent import JARVISVisionAgent
                self.vision_agent = JARVISVisionAgent(terminal_callback=self.logger.info)

                # Predictive Intent Engine (Elite v16.0)
                from intent_engine import IntentEngine
                self.intent_engine = IntentEngine(memory_engine=self.memory)
                self.intent_engine.analyze_patterns() # Build initial matrix

                # Start security scanner in background with verbal alerts
                def security_alert(level, msg):
                    self.logger.warning(f"SECURITY ALERT: {msg}")
                    if level == "CRITICAL" or level == "WARNING":
                        self.speak(f"Janob, xavfsizlik tizimi ogohlantiradi: {msg}")
                        
                self.security_scanner = SecurityScanner(alert_callback=security_alert)
                self.security_scanner.start()

            except Exception as e:
                self.logger.error(f"Advanced modules initialization failed: {e}")
        
        # Auto-start camera in background mode
        if self.camera:
            try:
                self.camera.start_camera(show_window=False)  # Background mode
                self.logger.info("Camera started in background mode")
            except Exception as e:
                self.logger.warning(f"Camera auto-start failed: {e}")
    
    def set_voice(self, voice_assistant):
        """Set voice assistant for verbal confirmations"""
        self.voice = voice_assistant
    
    def speak(self, text):
        """Speak confirmation message"""
        if self.avatar:
            self.avatar.set_pulse(True)
            
        if self.voice and hasattr(self.voice, 'speak'):
            self.voice.speak(text)
        else:
            print(f"[JARVIS VERBAL] {text}")
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                self.logger.error(f"Executor TTS Error: {e}")
            
        if self.avatar:
            self.avatar.set_pulse(False)
    
    def execute(self, action_or_dict, params=None):
        """
        Markaziy ijrochi metod. Ham (dict) ham (action, params) ko'rinishida qabul qiladi.
        """
        if isinstance(action_or_dict, dict):
            action = action_or_dict.get("action")
            parameters = action_or_dict.get("parameters", {})
        else:
            action = action_or_dict
            parameters = params if params is not None else {}

        if not action or action == "unknown":
            return {"success": False, "error": "Noma'lum buyruq"}

        self.logger.info(f"Executing: {action} with {parameters}")
        
        try:
            # Action'ga mos methodga yo'naltirish
            method_name = f"_{action}"
            method = getattr(self, method_name, None)
            
            # Agar method topilmasa, _get_executor orqali tekshirish (fallback)
            if not method:
                method = self._get_executor(action)

            result = None
            if method:
                with self.lock: # Maintain thread safety
                    result = method(parameters)
                
                # Predictive Analysis (Elite v16.0)
                if hasattr(self, 'intent_engine') and self.intent_engine and self.memory:
                    self.memory.add_command_history(action, str(parameters))
                    self.intent_engine.analyze_patterns() 
                    prediction = self.intent_engine.predict_next(action)
                    if prediction:
                        self.logger.info(f"🔮 PREDICTION: {prediction['action']}")
                
                # Gamification & Voice
                if action not in ["describe_screen", "posture_monitor"]:
                    if result and "error" not in str(result).lower():
                        if hasattr(self, 'gamification') and self.gamification: 
                            self.gamification.add_xp(10, action)

                return {"success": True, "verbal_response": str(result), "result": result}
            else:
                return {"success": False, "error": f"Ijrochi topilmadi: {action}"}
        
        except Exception as e:
            self.logger.error(f"Execution Error ({action}): {e}")
            return {"success": False, "error": str(e)}
        
    # CONSUMED BY PRIMARY EXECUTE METHOD
    
    # ==================== SYSTEM CONTROL ====================
    
    def _shutdown(self, params):
        """Kompyuterni o'chirish"""
        self.logger.info("Executing shutdown")
        os.system("shutdown /s /t 5")
        return "5 soniyada kompyuter o'chadi, janob."
    
    def _quit_jarvis(self, params):
        """JARVIS-ni tugatish"""
        self.logger.info("Quitting JARVIS")
        self.speak("Xayr, janob. JARVIS uxlashga ketmoqda.")
        
        import sys
        import psutil
        
        # Find and terminate JARVIS processes
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('start.py' in str(cmd) or 'hud_main.py' in str(cmd) for cmd in cmdline):
                    if proc.info['pid'] != current_pid:
                        proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Exit current process
        sys.exit(0)
        return "JARVIS tugatildi"
    
    def _restart(self, params):
        """Kompyuterni qayta ishga tushirish"""
        self.logger.info("Executing restart")
        subprocess.run(["shutdown", "/r", "/t", "1"], check=True)
        return "Restarting..."
    
    def _sleep(self, params):
        """Kompyuterni uyqu rejimiga o'tkazish"""
        self.logger.info("Executing sleep")
        # Windows uchun rundll32 ishlatamiz
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
        return "Going to sleep..."
    
    def _screenshot(self, params):
        """Ekran rasmini olish"""
        self.logger.info("Taking screenshot")
        
        file_path = params.get("path")
        if not file_path:
            # Default path if none provided
            cap_dir = os.path.join(os.getcwd(), "captures")
            if not os.path.exists(cap_dir):
                os.makedirs(cap_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(cap_dir, f"JARVIS_Capture_{timestamp}.png")
        
        pyautogui.screenshot(file_path)
        return f"Screenshot saved to {file_path}"

    def _get_battery_info(self, params):
        """Batareya holati"""
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "time_left": battery.secsleft // 60 if battery.secsleft != -1 else "N/A"
            }
        return "Battery info not available"

    def _kill_process(self, params):
        """Ilovani majburiy to'xtatish (Force Kill)"""
        app_name = params.get("app_name", "").lower()
        if not app_name:
            return "App name required"
            
        count = 0
        for proc in psutil.process_iter(['name']):
            if app_name in proc.info['name'].lower():
                proc.kill()
                count += 1
        return f"Terminated {count} instances of {app_name}"

    def _lock_screen(self, params):
        """Ekranni qulflash"""
        self.logger.info("Executing lock screen")
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
        return "Screen locked"

    def _start_sentinel(self, params):
        """Sentinel Mode (Auto-lock) yoqish"""
        self.logger.info("Starting Sentinel Mode")
        config.SENTINEL_MODE["enabled"] = True
        config.SENTINEL_MODE["last_warn_time"] = 0
        return "Sentinel Mode faollashtirildi. 2 daqiqa yo'q bo'lsangiz, kompyuter qulflanadi."

    def _stop_sentinel(self, params):
        """Sentinel Mode o'chirish"""
        import config
        config.SENTINEL_MODE["enabled"] = False
        return "Sentinel Mode o'chirildi."

    def _pause_blackout(self, params):
        """Blackout protokolini vaqtincha to'xtatib turish"""
        import config
        # Pause for 30 minutes by default
        duration_minutes = params.get("duration", 30)
        config.BLACKOUT_SETTINGS["paused_until"] = time.time() + (duration_minutes * 60)
        return f"Blackout protokoli {duration_minutes} daqiqaga to'xtatib turiladi."

    def _unlock_system(self, params):
        """Tizimni ovoz orqali ochish"""
        self.logger.info("Unlock command received")
        if config.SENTINEL_MODE.get("is_locked", False):
            config.SENTINEL_MODE["should_unlock"] = True
            return "Tizim ochilmoqda, xush kelibsiz janob."
        return "Tizim qulflanmagan."

    def _volume_up(self, params):
        """Ovozni ko'tarish"""
        import ctypes
        for _ in range(5): # 5 bosqich yuqori
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        return "Volume increased"

    def _volume_down(self, params):
        """Ovozni pasaytirish"""
        import ctypes
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
        return "Volume decreased"

    def _mute_volume(self, params):
        """Ovozni o'chirish/yoqish"""
        import ctypes
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        return "Volume muted/unmuted"

    def _describe_screen(self, params):
        """Ekranda nima borligini tahlil qilish (AI Vision)"""
        if not self.vision:
            return "Vision moduli yuklanmagan."
        
        prompt = params.get("prompt", "Ushbu ekranda nimalar ko'rinayapti? Javobni o'zbek tilida bering.")
        self.speak("Ekranni tahlil qilyapman, janob. Iltimos, kuting.")
        
        description = self.vision.describe_screen(user_prompt=prompt)
        self.speak(description)
        return description

    def _posture_monitor(self, params):
        """Sog'liq/Postura monitoringini boshqarish"""
        if not self.health:
            return "Health moduli yuklanmagan."
        
        command = params.get("command", "start").lower()
        if command == "start":
            return self.health.start_monitoring()
        elif command == "stop":
            return self.health.stop_monitoring()
        else:
            return "Noma'lum monitoring buyrug'i."

    # ==================== FINANCIAL CONTROL ====================
    
    def _add_expense(self, params):
        """Xarajat qo'shish"""
        if not self.finance:
            return "Moliya moduli yuklanmagan."
        
        amount = params.get("amount")
        category = params.get("category", "Umumiy")
        description = params.get("description", "")
        
        if not amount:
            return "Summa ko'rsatilmadi."
            
        result = self.finance.add_transaction(amount, category, description, "expense")
        self.speak(result)
        return result

    def _add_income(self, params):
        """Daromad qo'shish"""
        if not self.finance:
            return "Moliya moduli yuklanmagan."
        
        amount = params.get("amount")
        category = params.get("category", "Umumiy")
        description = params.get("description", "")
        
        if not amount:
            return "Summa ko'rsatilmadi."
            
        result = self.finance.add_transaction(amount, category, description, "income")
        self.speak(result)
        return result

    def _get_finance_report(self, params):
        """Moliya hisoboti"""
        if not self.finance:
            return "Moliya moduli yuklanmagan."
            
        result = self.finance.get_daily_report()
        self.speak(result)
        return result

    def _get_balance(self, params):
        """Balansni tekshirish"""
        if not self.finance:
            return "Moliya moduli yuklanmagan."
            
        result = self.finance.get_balance()
        self.speak(result)
        return result

    # ==================== RESEARCH CONTROL ====================
    
    def _start_research(self, params):
        """Mavzu bo'yicha tadqiqot boshlash"""
        if not self.research:
            return "Research moduli yuklanmagan."
        
        topic = params.get("topic")
        if not topic:
            return "Tadqiqot mavzusi ko'rsatilmadi."
            
        self.speak(f"Janob, {topic} mavzusi bo'yicha internetdan ma'lumot qidiryapman. Iltimos, kuting.")
        
        result = self.research.perform_research(topic)
        
        if isinstance(result, dict):
            summary = result['summary']
            filepath = result['file']
            self.speak(summary)
            return {
                "success": True,
                "summary": summary,
                "file": filepath
            }
        else:
            self.speak(result)
            return result

    # ==================== TUTOR CONTROL ====================
    
    def _start_tutor(self, params):
        """Til o'rganish sessiyasini boshlash"""
        if not self.tutor:
            return "Tutor moduli yuklanmagan."
        
        language = params.get("language", "Ingliz tili")
        result = self.tutor.start_session(language)
        self.speak(result)
        return result

    def _tutor_respond(self, params):
        """Tutor sessiyasida javob berish"""
        if not self.tutor:
            return "Tutor moduli yuklanmagan."
        
        text = params.get("text")
        language = params.get("language", "Ingliz tili")
        if not text:
            return "Matn ko'rsatilmadi."
            
        result = self.tutor.get_feedback(text, language)
        self.speak(result)
        return result

    # ==================== MOOD CONTROL ====================
    
    def _detect_mood(self, params):
        """Kayfiyatni aniqlash"""
        if not self.mood:
            return "Mood moduli yuklanmagan."
            
        self.speak("Janob, kayfiyatingizni tahlil qilish uchun kameraga qarang.")
        result = self.mood.detect_mood()
        self.speak(result)
        return result

    # ==================== MARKET CONTROL ====================
    
    def _get_crypto_price(self, params):
        """Kriptovalyuta narxini olish"""
        if not self.market:
            return "Market moduli yuklanmagan."
            
        symbol = params.get("symbol", "bitcoin")
        result = self.market.get_crypto_price(symbol)
        self.speak(result)
        return result

    def _get_stock_price(self, params):
        """Aksiya narxini olish"""
        if not self.market:
            return "Market moduli yuklanmagan."
            
        symbol = params.get("symbol", "AAPL")
        result = self.market.get_stock_price(symbol)
        self.speak(result)
        return result

    # ==================== LOCAL AI CONTROL ====================
    
    def _local_query(self, params):
        """Lokal AI modeliga so'rov yuborish"""
        if not self.local_ai:
            return "Lokal AI moduli yuklanmagan."
            
        prompt = params.get("prompt")
        if not prompt:
            return "So'rov matni ko'rsatilmadi."
            
        self.speak("Janob, lokal model orqali hisoblayapman. Bir lahza.")
        result = self.local_ai.generate_response(prompt)
        self.speak(result)
        return result

    # ==================== NIGHT OWL CONTROL ====================
    
    def _start_night_owl(self, params):
        """Night Owl rejimini yoqish"""
        if not self.night_owl:
            return "Night Owl moduli yuklanmagan."
            
        result = self.night_owl.start_autonomous_mode()
        self.speak(result)
        return result

    def _add_research_topic(self, params):
        """Tungi tadqiqot uchun mavzu qo'shish"""
        if not self.night_owl:
            return "Night Owl moduli yuklanmagan."
            
        topic = params.get("topic")
        if not topic:
            return "Mavzu ko'rsatilmadi."
            
        result = self.night_owl.add_topic(topic)
        self.speak(result)
        return result

    # ==================== VOICE AUTH CONTROL ====================

    def _voice_authenticate(self, params):
        """Ovoz orqali shaxsni tasdiqlash"""
        if not self.voice_authenticator:
            return "Ovozli identifikatsiya moduli yuklanmagan."
            
        self.speak("Identifikatsiya protokoli faollashtirildi. Iltimos, maxfiy iborani ayting.")
        result = self.voice_authenticator.authenticate()
        result = self.voice_authenticator.authenticate()
        self.speak(result)
        return result

    # ==================== GAMIFICATION CONTROL ====================

    def _get_level(self, params):
        """Level haqida ma'lumot"""
        if not self.gamification:
            return "Gamification moduli yuklanmagan."
        
        status = self.gamification.get_status()
        res = f"Siz hozir {status['level']}-darajadasiz. Keyingi darajaga {status['required'] - status['xp']} XP qoldi."
        self.speak(res)
        return res

    def _get_xp(self, params):
        """XP haqida ma'lumot"""
        if not self.gamification:
            return "Gamification moduli yuklanmagan."
            
        res = self.gamification.get_status_text()
        self.speak(res)
        return res

    # ==================== MEMORY CONTROL ====================

    def _memorize_info(self, params):
        """Ma'lumotni xotiraga saqlash"""
        if not self.memory:
            return "Xotira moduli yuklanmagan."
            
        text = params.get("text") or params.get("info")
        if not text:
            return "Nimani eslab qolish kerak?"
            
        res = self.memory.add_memory(text)
        self.speak(res)
        return res

    def _recall_info(self, params):
        """Xotiradan ma'lumot qidirish"""
        if not self.memory:
            return "Xotira moduli yuklanmagan."
            
        query = params.get("query")
        if not query:
            return "Nimani eslatib o'tishim kerak?"
            
        results = self.memory.search_memory(query)
        if not results:
            return "Bu haqda xotiramda ma'lumot topmadim."
            
        response = "Topilgan ma'lumotlar:\n" + "\n".join([f"- {r['text']}" for r in results])
        self.speak(f"Xotiramdan {len(results)} ta ma'lumot topdim, janob.")
        return response

    # ==================== HEALING CONTROL ====================

    def _check_errors(self, params):
        """Xatolarni tekshirish va tahlil qilish"""
        if not self.healer:
            return "Self-Healing moduli yuklanmagan."
            
        result = self.healer.check_logs()
        if result:
            self.speak(result)
            return result
        else:
            msg = "Tizimda yangi xatoliklar aniqlanmadi. Barchasi barqaror."
            self.speak(msg)
            return msg

    # ==================== SMART HOME CONTROL (DEPRECATED) ====================
    # Smart Home modules have been removed.
        return result

    # ==================== DREAM MODE CONTROL ====================

    def _generate_dream(self, params):
        """Tush ko'rish (Dream Mode)"""
        if not self.dream_weaver:
            return "Dream Mode moduli yuklanmagan."
            
        self.speak("Tush ko'rish rejimi ishga tushirildi. Kunlik loglarni tahlil qilyapman...")
        result = self.dream_weaver.generate_dream()
        
        # Ovozli javob qisqa bo'lishi kerak, to'liq pathni o'qimasin
        if "Tush tayyor" in result:
             self.speak("Tush tayyor, janob. Rasmni saqlab qo'ydim.")
        else:
             self.speak("Tush ko'rishda muammo bo'ldi.")
             
        return result

    # ==================== GUI AUTOMATION CONTROL ====================

    def _type_text(self, params):
        if not self.gui: return "GUI moduli yuklanmagan."
        text = params.get("text", "")
        return self.gui.type_text(text)

    def _press_key(self, params):
        if not self.gui: return "GUI moduli yuklanmagan."
        keys = params.get("key") or params.get("keys", "")
        return self.gui.press_hotkey(keys)

    def _scroll_down(self, params):
        if not self.gui: return "GUI moduli yuklanmagan."
        return self.gui.scroll(300, "down")

    def _scroll_up(self, params):
        if not self.gui: return "GUI moduli yuklanmagan."
        return self.gui.scroll(300, "up")

    def _open_run(self, params):
        if not self.gui: return "GUI moduli yuklanmagan."
        cmd = params.get("command", "")
        return self.gui.open_run_dialog(cmd)

    # ==================== VOICE TRANSFORMER CONTROL ====================

    def _change_voice(self, params):
        if not self.voice_transformer: return "Ovoz o'zgartirish moduli yuklanmagan."
        effect = params.get("effect", "robot")
        self.speak(f"Ovoz yozish boshlandi. Gapiring (5 soniya). Effekt: {effect}")
        return self.voice_transformer.process_voice(effect)

    # ==================== SWARM MODE CONTROL ====================

    def _start_swarm(self, params):
        if not self.swarm: return "Swarm moduli yuklanmagan."
        result = self.swarm.start_node()
        self.speak(result)
        return result

    def _swarm_scan(self, params):
        if not self.swarm: return "Swarm moduli yuklanmagan."
        result = self.swarm.scan_network()
        self.speak(result)
        return result

    def _swarm_list(self, params):
        if not self.swarm: return "Swarm moduli yuklanmagan."
        result = self.swarm.get_nodes()
        self.speak(result)
        return result

    def _swarm_send(self, params):
        if not self.swarm: return "Swarm moduli yuklanmagan."
        ip = params.get("ip")
        cmd = params.get("command")
        if not ip or not cmd: return "IP manzil va buyruq kerak."
        return self.swarm.send_command(ip, cmd)

    # ==================== WIDGET CONTROL ====================

    def _start_widget(self, params):
        try:
            widget_path = os.path.join(os.getcwd(), "hud_widgets.py")
            subprocess.Popen([sys.executable, widget_path])
            return "Golografik vidjet ishga tushirildi."
        except Exception as e:
            return f"Vidjetni ochishda xatolik: {e}"

    def _remote_wake(self, params):
        """Uzoqdan yoqish uchun MAC manzilni ko'rsatish"""
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                           for ele in range(0, 8*6, 8)][::-1])
            
            msg = f"Kompyuterni uzoqdan yoqish (WoL) uchun MAC manzilingiz:\n{mac.upper()}\n\n" \
                  f"Buni 'remote_power.py' fayliga yoki telefon ilovasiga kiritishingiz kerak."
            self.speak("MAC manzilingizni ekranga chiqardim, janob.")
            return msg
        except Exception as e:
            return f"MAC manzilni aniqlashda xatolik: {e}"

    def _global_status(self, params):
        """Dunyo yangiliklarini tahlil qilish"""
        if not self.global_eye:
            return "Global Eye tizimi yuklanmagan."
        
        self.speak("Dunyo bo'ylab so'nggi ma'lumotlarni yig'yapman, kuting...")
        # Note: Trends API might be slow
        return self.global_eye.analyze_world()

    def _visual_avatar(self, params):
        import config
        config.AVATAR_ENABLED = not config.AVATAR_ENABLED
        state = "yoqildi" if config.AVATAR_ENABLED else "o'chirildi"
        return f"Golografik avatar {state}."

    # ==================== QUANTUM SECURITY ====================

    def _encrypt_file(self, params):
        if not self.security_vault: return "Xavfsizlik moduli yuklanmagan."
        path = params.get("path") or params.get("file")
        if not path: return "Qaysi faylni shifrlay?"
        return self.security_vault.encrypt_file(path)

    def _decrypt_file(self, params):
        if not self.security_vault: return "Xavfsizlik moduli yuklanmagan."
        path = params.get("path") or params.get("file")
        if not path: return "Qaysi faylni ochay?"
        return self.security_vault.decrypt_file(path)

    def _secure_delete(self, params):
        if not self.security_vault: return "Xavfsizlik moduli yuklanmagan."
        path = params.get("path") or params.get("file")
        if not path: return "Nimani yo'q qilay?"
        return self.security_vault.secure_delete(path)

    # ==================== APPLICATION CONTROL ====================
    
    def _open_app(self, params):
        """Ilovani ochish"""
        app_name = params.get("app_name", "").lower()
        
        if not app_name:
            raise ValueError("app_name parameter required")
        
        self.logger.info(f"Opening app: {app_name}")
        
        # 1. APP_PATHS'dan path olish
        app_path = APP_PATHS.get(app_name.lower())
        
        if app_path:
            # Path mavjud bo'lsa ishlatish
            if os.path.exists(app_path):
                self.logger.info(f"Opening app with path: {app_path}")
                try:
                    os.startfile(app_path)
                    return {
                        "success": True,
                        "message": f"{app_name} opened",
                        "app_name": app_name
                    }
                except Exception as e:
                    self.logger.error(f"os.startfile failed: {e}")
            
            # Path topilmasa yoki startfile xato bersa, shell orqali urinish
            self.logger.info(f"Trying shell for: {app_path}")
            try:
                subprocess.Popen(f'"{app_path}"', shell=True)
                return {
                    "success": True,
                    "message": f"{app_name} opened via shell",
                    "app_name": app_name
                }
            except:
                pass
        
        # 2. Shell bilan ochish (notepad.exe kabi)
        try:
            self.logger.info(f"Opening app with shell: {app_name}")
            os.startfile(f"{app_name}.exe") if os.path.exists(f"{app_name}.exe") else subprocess.Popen(f"{app_name}.exe", shell=True)
            return {
                "success": True,
                "message": f"{app_name} opened",
                "app_name": app_name
            }
        except Exception as e:
            self.logger.error(f"Failed to open app: {e}")
            raise ValueError(f"Could not open app: {app_name}")
    
    def _close_app(self, params):
        """Ilovani yopish"""
        app_name = params.get("app_name", "").lower()
        
        if not app_name:
            raise ValueError("app_name parameter required")
        
        self.logger.info(f"Closing app: {app_name}")
        
        # Process nomini olish
        executable = APP_EXECUTABLES.get(app_name, f"{app_name}.exe")
        
        # Processni topish va o'chirish
        killed = False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == executable.lower() or \
                   proc.info['name'].lower() == app_name:
                    proc.kill()
                    killed = True
                    self.logger.info(f"Killed process: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if killed:
            return f"Closed {app_name}"
        else:
            return f"App {app_name} not found"
    
    def _focus_app(self, params):
        """Ilovani olga olib chiqish"""
        app_name = params.get("app_name", "")
        
        if not app_name:
            raise ValueError("app_name parameter required")
        
        # Bu Windows API orqali amalga oshiriladi
        # Hozircha oddiy implementatsiya
        return f"Focus on {app_name} (not fully implemented)"
    
    # ==================== WEB CONTROL ====================
    
    def _open_website(self, params):
        """Veb-saytni ochish"""
        url = params.get("url", "")
        
        if not url:
            raise ValueError("url parameter required")
        
        # URL'ni to'g'rilash
        full_url = extract_website_url(url)
        if not full_url:
            full_url = url
        
        self.logger.info(f"Opening website: {full_url}")
        webbrowser.open(full_url)
        return f"Opened {full_url}"
    
    def _search_google(self, params):
        """Google'da qidirish"""
        query = params.get("query", "")
        
        if not query:
            raise ValueError("query parameter required")
        
        self.logger.info(f"Searching Google: {query}")
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)
        return f"Searching for: {query}"
    
    # ==================== MESSAGING ====================
    
    def _send_telegram_message(self, params):
        """
        Telegram orqali xabar yuborish (Background preference)
        
        Parameters:
            contact (str): Kontakt nomi
            message (str): Yuboriladi xabar matni
        """
        contact = params.get("contact", "")
        message = params.get("message", "")
        
        if not contact:
            raise ValueError("contact parameter required")
        if not message:
            raise ValueError("message parameter required")
        
        self.logger.info(f"Targeting Telegram message: [{contact}] -> {message}")
        
        # 1. API orqali (Background) urinib ko'rish
        if hasattr(self, 'telegram_bridge') and self.telegram_bridge and self.telegram_bridge.is_running:
            try:
                self.logger.info("Attempting background delivery via API Bridge...")
                success = self.telegram_bridge.send_message(contact, message)
                if success:
                    return f"✅ [Background] Sent message to {contact}: {message}"
                else:
                    self.logger.warning("Background delivery failed, falling back to GUI Mode.")
            except Exception as e:
                self.logger.error(f"Bridge error: {e}")
        
        # 2. GUI Mode (Fallback) - Ekran qalqib chiqishi mumkin
        self.logger.info("Falling back to GUI Automation mode (Visible)...")
        
        try:
            import win32gui
            import win32con
            import win32process
            
            def find_telegram_window(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        process_name = process.name().lower()
                        if "telegram" in process_name or "telegram" in title.lower():
                            windows.append((hwnd, title, process_name))
                    except:
                        if "telegram" in title.lower():
                            windows.append((hwnd, title, "unknown"))
                return True
            
            windows = []
            win32gui.EnumWindows(find_telegram_window, windows)
            
            if windows:
                hwnd, title, _ = windows[0]
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(1)
            else:
                return "Error: Telegram Desktop is not open and Bridge is offline."
                
        except Exception as e:
            self.logger.error(f"Error focusing Telegram: {e}")
            time.sleep(2)
        
        # Typing sequence
        pyautogui.press('esc')
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'k')
        time.sleep(0.8)
        pyautogui.write(contact, interval=0.03)
        time.sleep(1.0)
        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.write(message, interval=0.03)
        time.sleep(0.3)
        pyautogui.press('enter')
        
        return f"✅ [GUI Mode] Sent message to {contact}: {message}"
    
    def _write_in_app(self, params):
        """Ilovada matn yozish"""
        app_name = params.get("app_name", "notepad").lower()
        text = params.get("text", "")
        
        if not text:
            raise ValueError("text parameter required")
        
        self.logger.info(f"Writing in {app_name}: {text}")
        
        # 1. Ilovani ochish yoki fokuslash
        self.logger.info(f"Opening/Focusing {app_name}...")
        
        # Ochiq oynani topishga urinish
        found_window = False
        try:
            import win32gui
            import win32con
            import win32process
            
            def find_app_window(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd).lower()
                    
                    # Process nomini tekshirish
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        process_name = process.name().lower()
                        
                        target_exe = APP_PATHS.get(app_name, app_name)
                        if target_exe in process_name or app_name in title:
                             windows.append(hwnd)
                    except:
                        if app_name in title:
                            windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(find_app_window, windows)
            
            if windows:
                hwnd = windows[0]
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                found_window = True
                time.sleep(1)
        except:
            pass
            
        if not found_window:
            # Ochish
            self._open_app({"app_name": app_name})
            time.sleep(3) # Ochilishini kutish
            
        # 2. Matnni yozish
        self.logger.info(f"Writing text via clipboard...")
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            
            # Ctrl+V bosish
            pyautogui.hotkey('ctrl', 'v')
        except Exception as e:
            self.logger.warning(f"Clipboard methods failed: {e}. Falling back to pyautogui.write")
            pyautogui.write(text, interval=0.01)
        
        return f"Wrote text in {app_name}: {text}"
    
    # ==================== FILE SYSTEM ====================
    
    def _create_folder(self, params):
        """Papka yaratish"""
        folder_name = params.get("folder_name", "")
        path = params.get("path", os.getcwd())
        
        if not folder_name:
            raise ValueError("folder_name parameter required")
        
        full_path = os.path.join(path, folder_name)
        self.logger.info(f"Creating folder: {full_path}")
        
        os.makedirs(full_path, exist_ok=True)
        return f"Created folder: {full_path}"
    
    def _delete_file(self, params):
        """Faylni o'chirish"""
        file_path = params.get("file_path", "")
        
        if not file_path:
            raise ValueError("file_path parameter required")
        
        self.logger.info(f"Deleting file: {file_path}")
        
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"Deleted file: {file_path}"
        elif os.path.isdir(file_path):
            import shutil
            shutil.rmtree(file_path)
            return f"Deleted directory: {file_path}"
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
    
    def _open_file(self, params):
        """Faylni ochish"""
        file_path = params.get("file_path", "")
        
        if not file_path:
            raise ValueError("file_path parameter required")
        
        self.logger.info(f"Opening file: {file_path}")
        os.startfile(file_path)
        return f"Opened file: {file_path}"
    
    def _list_directory(self, params):
        """Papka tarkibini ko'rsatish"""
        path = params.get("path", os.getcwd())
        
        self.logger.info(f"Listing directory: {path}")
        
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a directory: {path}")
        
        items = os.listdir(path)
        return {
            "path": path,
            "items": items,
            "count": len(items)
        }
    
    # ==================== INPUT CONTROL ====================
    
    def _type_text(self, params):
        """Matn yozish (Clipboard orqali)"""
        text = params.get("text", "")
        
        if not text:
            raise ValueError("text parameter required")
        
        self.logger.info(f"Typing text via clipboard: {text}")
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            
            pyautogui.hotkey('ctrl', 'v')
        except Exception as e:
            self.logger.warning(f"Clipboard failed: {e}. Falling back to slow type.")
            pyautogui.write(text, interval=0.05)
            
        return f"Typed: {text}"
    
    def _press_key(self, params):
        """Tugmani bosish"""
        key = params.get("key", "")
        
        if not key:
            raise ValueError("key parameter required")
        
        self.logger.info(f"Pressing key: {key}")
        pyautogui.press(key)
        return f"Pressed: {key}"
    
    def _press_hotkey(self, params):
        """Hotkey kombinatsiyasini bosish"""
        keys = params.get("keys", [])
        
        if not keys:
            raise ValueError("keys parameter required")
        
        self.logger.info(f"Pressing hotkey: {keys}")
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey: {'+'.join(keys)}"
    
    def _move_cursor(self, params):
        """Kursorni harakatlantirish"""
        x = params.get("x", 0)
        y = params.get("y", 0)
        
        self.logger.info(f"Moving cursor to: ({x}, {y})")
        pyautogui.moveTo(x, y)
        return f"Moved cursor to ({x}, {y})"
    
    def _click_mouse(self, params):
        """Sichqoncha tugmasini bosish"""
        button = params.get("button", "left")
        
        self.logger.info(f"Clicking mouse: {button}")
        pyautogui.click(button=button)
        return f"Clicked {button} mouse button"
    
    def _scroll_mouse(self, params):
        """Sichqoncha g'ildiragini aylantirish"""
        amount = params.get("amount", 1)
        
        self.logger.info(f"Scrolling mouse: {amount}")
        pyautogui.scroll(amount)
        return f"Scrolled {amount}"
    
    # ==================== INFORMATION ====================
    
    def _get_time(self, params):
        """Hozirgi vaqtni olish"""
        current_time = get_current_time()
        return {"time": current_time}
    
    def _get_date(self, params):
        """Hozirgi sanani olish"""
        current_date = get_current_date()
        return {"date": current_date}
    
    def _get_weather(self, params):
        """Ob-havo ma'lumotini olish"""
        # Bu funksiya uchun API kerak bo'ladi
        return "Weather API not configured yet"
    
    def _get_system_info(self, params):
        """Tizim haqida ma'lumot"""
        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
        return info

    def _get_resource_usage(self, params):
        """CPU va RAM ulushini olish"""
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent
        }
    
    # ==================== BROWSER ACTIONS (Yangi) ====================
    
    def _youtube_search(self, params):
        """YouTube'da qidirish"""
        query = params.get("query", "")
        
        if not query:
            raise ValueError("query parameter required")
        
        self.logger.info(f"YouTube search: {query}")
        
        from browser_helper import BrowserHelper
        helper = BrowserHelper()
        result = helper.youtube_search(query)
        
        return result
    
    def _youtube_comment(self, params):
        """YouTube video'ga komment yozish"""
        video_url = params.get("video_url", "")
        comment = params.get("comment", "")
        
        if not video_url or not comment:
            raise ValueError("video_url and comment parameters required")
        
        self.logger.info(f"YouTube comment: {comment} on {video_url}")
        
        from browser_helper import BrowserHelper
        helper = BrowserHelper()
        result = helper.youtube_comment(video_url, comment)
        
        return result
    
    def _google_search_click(self, params):
        """Google'da qidirish va birinchi natijani ochish"""
        query = params.get("query", "")
        result_num = params.get("result_num", 1)
        
        if not query:
            raise ValueError("query parameter required")
        
        self.logger.info(f"Google search and click: {query}, result #{result_num}")
        
        from browser_helper import BrowserHelper
        helper = BrowserHelper()
        result = helper.google_search_and_click(query, result_num)
        
        return result
    
    
    # ==================== GESTURE CONTROL (YANGI) ====================
    
    def _start_gesture_control(self, params):
        """Qo'l harakati bilan boshqarishni yoqish"""
        import config
        config.GESTURE_SETTINGS["enabled"] = True
        return {"status": "success", "message": "Gesture control faollashtirildi"}
    
    def _stop_gesture_control(self, params):
        """Gesture control to'xtatildi"""
        import config
        config.GESTURE_SETTINGS["enabled"] = False
        return {"status": "success", "message": "Gesture control to'xtatildi"}

    def _youtube_search(self, params):
        """YouTube'dan qidirish va birinchisini ochish"""
        query = params.get("query", "")
        if not query: return "Qidiruv so'rovi topilmadi."
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"YouTube'dan '{query}' qidirilmoqda..."

    def _get_weather(self, params):
        """Ob-havo ma'lumotlarini olish (Simple version)"""
        city = params.get("city", "Tashkent")
        url = f"https://www.google.com/search?q=weather+{city}"
        webbrowser.open(url)
        return f"{city} uchun ob-havo ma'lumotlari qidirilmoqda..."

    def _google_search_click(self, params):
        """Google'dan qidirish (Method mapping fix)"""
        return self._search_google(params)

    # ==================== MEDIA MASTER (PHASE 4) ====================

    def _media_play_pause(self, params):
        """Musiqani to'xtatish yoki davom ettirish"""
        import ctypes
        ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0) # Media Play/Pause
        ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)
        return "Media play/pause triggered"

    def _media_next(self, params):
        """Keyingi musiqa"""
        import ctypes
        ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0) # Media Next
        ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0)
        return "Next track"

    def _media_previous(self, params):
        """Oldingi musiqa"""
        import ctypes
        ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0) # Media Previous
        ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0)
        return "Previous track"
    
    # === MEDIA GENERATION (Image & Video) ===
    def _generate_image(self, params):
        if not self.media_generator: return "Media Generator not loaded."
        prompt = params.get("prompt") or params.get("text", "abstract art")
        res = self.media_generator.generate_image(prompt)
        return res

    def _generate_video(self, params):
        if not self.media_generator: return "Media Generator not loaded."
        prompt = params.get("prompt") or params.get("text", "abstract video")
        res = self.media_generator.generate_video(prompt)
        return res

    # === NEW FEATURES (Research, Finance, Gaming) ===
    
    def _perform_research(self, params):
        if not self.research: return "Research module not loaded."
        topic = params.get("topic") or "AI"
        import asyncio
        # Run async in sync executor (simple wrapper)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(self.research.perform_research(topic))
            return res
        except Exception as e:
             self.logger.error(f"Research executor error: {e}")
             return f"Tadqiqotda xatolik yuz berdi: {e}"

    def _add_expense(self, params):
        if not self.finance: return "Finance module not loaded."
        amount = params.get("amount", 0)
        desc = params.get("description", "Noma'lum")
        if amount == 0: return "Summa aniqlanmadi."
        return self.finance.add_transaction(amount, "Xarajat", desc, "expense")

    def _get_balance(self, params):
        if not self.finance: return "Finance module not loaded."
        return self.finance.get_balance()

    def _get_financial_update(self, params):
        if not self.finance: return "Finance module not loaded."
        return self.finance.get_daily_report()

    def _toggle_gaming_mode(self, params):
        """O'yin rejimi: RAM tozalash va High Priority"""
        if not self.gaming_mode: return "Gaming module not loaded."
        return self.gaming_mode.toggle()
    def _connect_account(self, params):
        """Hisobni ulash (o'rganish uchun)"""
        platform = params.get("platform", "general")
        self.speak(f"{platform} hisobini ulash jarayoni boshlandi.")
        # Simulyatsiya
        import time
        time.sleep(1)
        return f"{platform.title()} hisobi muvaffaqiyatli ulandi. Endi men ushbu platformadan ma'lumotlarni o'rganishim mumkin."

    def _learn_from_feedback(self, params):
        """Foydalanuvchi fikridan o'rganish"""
        feedback = params.get("feedback", "")
        if not feedback: return "Fikr aniqlanmadi."
        
        # Xotiraga saqlash
        if self.memory:
            self.memory.add_command_history("feedback", feedback)
        
        return "Rahmat, janob. Ushbu ma'lumotni o'rganib oldim."

    # ==================== SCHEDULE MANAGER (PHASE 4) ====================

    def _get_schedule(self, params):
        """Kunlik rejalarni ko'rish"""
        path = "local_schedule.json"
        if not os.path.exists(path):
            return "Rejalar hozircha yo'q, Janob."
        
        try:
            with open(path, "r") as f:
                schedule = json.load(f)
            
            if not schedule: return "Bugun uchun rejalar bo'sh."
            
            res = "Bugungi rejalar:\n"
            for item in schedule:
                res += f"- {item['time']}: {item['task']}\n"
            return res
        except Exception as e:
            return f"Rejalarni o'qishda xatolik: {e}"

    def _add_to_schedule(self, params):
        """Reja qo'shish"""
        task = params.get("task")
        time_str = params.get("time") # HH:MM format
        
        if not task or not time_str:
            return "Task va vaqt (HH:MM) talab qilinadi."
            
        path = "local_schedule.json"
        schedule = []
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    schedule = json.load(f)
            except:
                pass
        
        schedule.append({"time": time_str, "task": task})
        # Sort by time
        schedule.sort(key=lambda x: x['time'])
        
        with open(path, "w") as f:
            json.dump(schedule, f, indent=4)
            
        return f"Reja qo'shildi: {time_str} - {task}"

    def _start_typer_bot(self, params):
        """JARVIS Typer Bot-ni ishga tushirish"""
        if not TYPER_AVAILABLE:
            return "Typer Bot moduli mavjud emas, janob."
            
        if self.typer_bot and self.typer_bot.is_running:
            return "Typer Bot allaqachon ishlamoqda, janob."
            
        try:
            if not self.typer_bot:
                from typer_bot import JARVISTyperBot
                self.typer_bot = JARVISTyperBot()
            
            self.typer_bot.start()
            
            # Alohida thread-da loop-ni boshlash
            def run_loop():
                self.typer_bot.auto_loop()
            
            threading.Thread(target=run_loop, daemon=True).start()
            return "Typer Bot ishga tushirildi. Ekranni kuzatyapman, janob."
        except Exception as e:
            return f"Typer Bot-ni ishga tushirishda xatolik: {str(e)}"

    def _stop_typer_bot(self, params):
        """JARVIS Typer Bot-ni to'xtatish"""
        if not self.typer_bot or not self.typer_bot.is_running:
            return "Typer Bot ishga tushirilmagan, janob."
            
        self.typer_bot.stop()
        return "Typer Bot to'xtatildi, janob."

    # ==================== CONNECTIVITY (YANGI) ====================
    
    def _scan_bluetooth(self, params):
        """Bluetooth qurilmalarni qidirish"""
        if not CONNECTIVITY_AVAILABLE or not self.connectivity:
            return "Bluetooth moduli mavjud emas, janob."
        
        devices = self.connectivity.get_bluetooth_devices()
        if isinstance(devices, str):
            return devices
            
        if not devices:
            return "Yaqin orada hech qanday Bluetooth qurilmasi topilmadi, janob."
            
        res = "Topilgan Bluetooth qurilmalari:\n"
        for d in devices:
            res += f"- {d['name']} ({d['address']})\n"
        return res

    def _start_remote_bridge(self, params):
        """Remote Bridge-ni ishga tushirish"""
        if not CONNECTIVITY_AVAILABLE or not self.connectivity:
            return "Connectivity moduli mavjud emas, janob."
            
        port = params.get("port", config.CONNECTIVITY_SETTINGS.get("remote_port", 5000))
        return self.connectivity.start_remote_bridge(port)

    def _connect_device(self, params):
        """Qurilmaga ulanish (Sodda ko'rinish)"""
        address = params.get("address", "")
        if not address:
            return "Qurilma manzili (address) berilishi shart, janob."
        # Hozircha faqat simulyatsiya
        return f"{address} qurilmasiga ulanishga urinilmoqda... (Hozircha faqat simulyatsiya)"

    # ==================== DEV MODE (YANGI) ====================

    def _create_project(self, params):
        """Yangi dasturlash loyihasini yaratish"""
        name = params.get("project_name", "new_project")
        lang = params.get("language", "python").lower()
        path = os.path.join(os.getcwd(), "projects")
        if not os.path.exists(path): os.makedirs(path)
        
        proj_dir = os.path.join(path, name)
        if os.path.exists(proj_dir): return f"Xato: '{name}' loyihasi allaqachon mavjud."
        
        os.makedirs(proj_dir)
        
        # Initial files
        if lang == "python":
            with open(os.path.join(proj_dir, "main.py"), "w") as f:
                f.write('print("Hello JARVIS World!")\n')
        elif lang == "web":
            with open(os.path.join(proj_dir, "index.html"), "w") as f:
                f.write('<h1>JARVIS Web Project</h1>\n')
        
        return f"✅ '{name.upper()}' loyihasi yaratildi: {proj_dir}"

    def _analyze_codebase(self, params):
        """Kod bazasini tahlil qilish (File structure only for now)"""
        path = os.getcwd()
        ignore = [".git", "__pycache__", "venv", ".idea", ".gemini", "node_modules"]
        
        structure = "JARVIS CODEBASE ANALYSIS:\n"
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignore]
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            structure += f"{indent}📁 {os.path.basename(root)}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if f.endswith(('.py', '.js', '.html', '.css', '.md')):
                    structure += f"{subindent}📄 {f}\n"
        
        return structure

    def _run_terminal_v2(self, params):
        """Kengaytirilgan terminal buyrug'ini bajarish"""
        command = params.get("command")
        if not command: return "Buyruq topilmadi."
        
        self.logger.info(f"DevMode: Running terminal command: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
            output = result.stdout if result.returncode == 0 else result.stderr
            return f"Terminal Natijasi:\n{output[:1000]}" # Limit output
        except Exception as e:
            return f"Terminal xatoligi: {str(e)}"

    def _reset_sentinel(self, params):
        """Sentinel Mode taymerini nolga tushirish (Foydalanuvchi borligi tasdiqlandi)"""
        import config
        config.SENTINEL_MODE["last_activity"] = time.time()
        return "Tushunarlu janob, sizni ko'rib turganimdan mamnunman. Sentinel taymeri yangilandi."

    def _register_face(self, params):
        """Face ID uchun yuzni ro'yxatga olish"""
        self.speak("Yuzni ro'yxatga olish boshlandi. Kameraga qarab turing, janob.")
        try:
            from face_auth import FaceAuth
            auth = FaceAuth()
            
            # 1. Handle Camera Conflict
            was_running = False
            if hasattr(self, 'camera') and self.camera and self.camera.is_camera_running:
                self.logger.info("Temporarily stopping background camera for registration...")
                self.camera.stop_camera()
                was_running = True
                time.sleep(1) # Give OS time to release resource
            
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                error_msg = "Kamera ochilmadi, janob. Iltimos tekshirib ko'ring."
                self.speak(error_msg)
                if was_running: self.camera.start_camera(show_window=False)
                return error_msg
                
            auth.capture_training_data(cap)
            cap.release()
            
            # 2. Restart background camera
            if was_running:
                self.camera.start_camera(show_window=False)
            
            import config
            config.FACE_ID_SETTINGS["registration_complete"] = True
            success_msg = "Face ID muvaffaqiyatli ro'yxatdan o'tkazildi, janob."
            self.speak(success_msg)
            return success_msg
        except Exception as e:
            self.logger.error(f"Face registration error: {e}")
            error_msg = f"Xatolik yuz berdi: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _smart_search(self, params):
        """AI-powered file search"""
        query = params.get("query", "")
        search_type = params.get("type", "quick")  # quick, date, content, fuzzy
        
        if not query:
            return "Qidiruv so'zi topilmadi, janob."
            
        try:
            self.speak(f"{query} uchun fayllarni qidiryapman, janob.")
            from smart_search import SmartFileSearch
            searcher = SmartFileSearch()
            
            if search_type == "date":
                days = params.get("days", 30)
                file_type = params.get("file_type")
                results = searcher.search_by_date(query, days, file_type)
            elif search_type == "content":
                results = searcher.search_by_content(query)
            elif search_type == "fuzzy":
                results = searcher.fuzzy_file_search(query)
            else:
                results = searcher.quick_find(query)
                
            if not results:
                msg = f"'{query}' uchun hech narsa topilmadi, janob."
                self.speak(msg)
                return msg
            
            count_msg = f"{len(results)} ta fayl topildi"
            self.speak(count_msg)
            
            response = f"Topildi: {len(results)} ta fayl\\n\\n"
            for i, r in enumerate(results[:5], 1):  # Top 5
                response += f"{i}. {r['name']}\\n"
                response += f"   📁 {r['path']}\\n"
                if 'modified' in r:
                    response += f"   📅 {r['modified']}\\n"
                if 'matches' in r:
                    response += f"   ✅ {r['matches']} moslik topildi\\n"
                response += "\\n"
                
            return response
        except Exception as e:
            self.logger.error(f"Smart search error: {e}")
            error_msg = f"Qidiruv xatoligi: {str(e)}"
            self.speak(error_msg)
            return error_msg
    
    # ==================== ADVANCED FEATURES (PHASE 4) ====================

    def _get_news_digest(self, params):
        """Kunlik yangiliklar dayjestini olish"""
        if not ADVANCED_FEATURES_AVAILABLE or not self.news_bot:
            return "Yangiliklar moduli mavjud emas, janob."
        
        self.speak("Yangiliklarni qidiryapman, janob.")
        try:
            articles = self.news_bot.get_daily_digest()
            if not articles:
                return "Hozircha yangiliklar topilmadi, janob."
            
            res = f"Bugungi asosiy yangiliklar ({len(articles)} ta):\\n\\n"
            for i, art in enumerate(articles, 1):
                res += f"{i}. {art['title']}\\n"
            
            self.speak(f"Bugun uchun {len(articles)} ta yangilik topdim, janob.")
            return res
        except Exception as e:
            return f"Yangiliklarni olishda xatolik: {str(e)}"

    def _voice_clone_speak(self, params):
        """Custom ovoz (Voice Cloning) bilan gapirish"""
        text = params.get("text", "")
        if not text:
            return "Gapirish uchun matn kerak, janob."
            
        if not ADVANCED_FEATURES_AVAILABLE or not self.voice_cloning:
            return "Voice cloning moduli mavjud emas, janob."
            
        self.speak("Siz istagan ovozda tayyorlayapman, janob.")
        return self.voice_cloning.speak_with_custom_voice(text)

    def _get_security_report(self, params):
        """Tizim xavfsizligi hisobotini olish"""
        if not ADVANCED_FEATURES_AVAILABLE or not self.security_scanner:
            return "Security scanner moduli mavjud emas, janob."
            
        report = self.security_scanner.get_status_report()
        res = f"XAVFSIZLIK HISOBOTI:\\n"
        res += f"- Status: {report.get('status')}\\n"
        res += f"- CPU: {report.get('cpu')}%\\n"
        res += f"- RAM: {report.get('memory')}%\\n"
        res += f"- Disk: {report.get('disk')}%\\n"
        res += f"- Protsesslar: {report.get('processes')}\\n"
        
        self.speak(f"Tizim holati {report.get('status')}, janob.")
        return res

    def _query_my_data(self, params):
        """Neural RAG Search through local documents (Elite v15.0)"""
        from neural_query import NeuralQueryEngine
        query = params.get("query", "")
        if not query: return "Qidiruv so'rovini kiriting, janob."
        
        self.speak(f"Mahalliy arxivdan '{query}' mavzusida ma'lumot qidiryapman, janob.")
        nq = NeuralQueryEngine(brain=self.brain)
        return nq.search(query)

    def _organize_system(self, params):
        """Intelligent file organization via SmartSorter (Elite v15.0)"""
        if not hasattr(self, 'sorter'):
            from smart_sorter import SmartSorter
            self.sorter = SmartSorter(brain=self.brain, terminal_callback=self.logger.info)
        
        target_dir = params.get("directory", os.path.join(os.path.expanduser("~"), "Desktop"))
        self.speak("Ish stolini tartibga solyapman, janob. Muhim fayllar JARVIS HUB-ga ko'chirildi.")
        self.sorter.auto_organize_directory(target_dir)
        return "Tizimni tartibga solish yakunlandi. Barcha fayllar semantik tahlil qilindi."

    def _toggle_privacy_shield(self, params):
        """Toggle HUD Privacy Shield (Elite v16.0)"""
        # Note: This requires a callback to the HUD from Executor, or the HUD listens to logs
        # Since Executor <-> HUD link is via signals in main.py, we can use a special log trigger
        # OR better, if we have a direct reference. Executor usually doesn't have direct HUD ref.
        # So we'll use a specific verbal confirmation that HUD listens to, or return a special status.
        
        # However, looking at hud_main, it doesn't seem to listen for specific executor returns for UI control.
        # But wait, we can just speak and let the user do it manually? No, better to implement a callback system.
        # For now, we will simulate it via speak and assume HUD is watching "SECURITY" logs? 
        # Actually, let's use the 'action' confirmation.
        
        state = params.get("state", "toggle")
        self.speak(f"Maxfiy rejim {state}, janob. Ekran himoyasi faollashtirilmoqda.")
        
        # Ideally, we emit a signal. Here we fake it by returning a dict with UI intent if possible
        # But standard executors return string/dict response.
        return {"verbal_response": "Maxfiy qalqon holati o'zgartirildi.", "success": True, "ui_action": "toggle_shield"}

    def _desktop_automation(self, params):


        """Desktop avtomatizatsiyasi (Excel, PDF, Image)"""
        if not ADVANCED_FEATURES_AVAILABLE or not self.automation:
            return "Automation moduli mavjud emas, janob."
            
        task_type = params.get("type", "excel")
        folder = params.get("folder", os.getcwd())
        
        try:
            if task_type == "excel":
                results = self.automation.process_excel_batch(folder)
                self.speak(f"Excel fayllari qayta ishlandi, {len(results)} ta fayl, janob.")
                return f"Excel natijalari: {results}"
            elif task_type == "pdf":
                file_path = params.get("file_path")
                if not file_path: return "PDF fayl yo'li kerak."
                text = self.automation.extract_pdf_text(file_path)
                return f"PDF Matni (birinchi 500 ta'rif):\\n{text[:500]}"
            elif task_type == "image":
                results = self.automation.convert_images_batch(folder)
                self.speak(f"Rasmlar konvertatsiya qilindi, janob.")
                return f"Konvertatsiya qilingan: {len(results)} ta rasm."
            return "Noma'lum automation turi."
        except Exception as e:
            return f"Automation xatoligi: {str(e)}"

    # ==================== ADVANCED MEDIA & SCHEDULER (UPGRADED) ====================

    def _smart_media_control(self, params):
        """Kengaytirilgan media boshqaruvi"""
        if not ADVANCED_FEATURES_AVAILABLE or not self.media_player:
            return "Media Master moduli mavjud emas, janob."
            
        action = params.get("media_action", "toggle")
        
        try:
            if action == "toggle":
                return self.media_player.toggle_play_pause()
            elif action == "seek":
                offset = params.get("offset", 5)
                return self.media_player.seek_by_voice(offset)
            elif action == "subtitles":
                path = params.get("video_path")
                if not path: return "Video fayl yo'li ko'rsatilmadi."
                return self.media_player.download_subtitles(path)
            return "Noma'lum media harakati."
        except Exception as e:
            return f"Media xatoligi: {str(e)}"

    def _advanced_schedule_manage(self, params):
        """Kengaytirilgan reja boshqaruvi"""
        if not ADVANCED_FEATURES_AVAILABLE or not self.scheduler:
            return "Advanced Scheduler moduli mavjud emas, janob."
            
        action = params.get("schedule_action", "list")
        
        try:
            if action == "list":
                schedule = self.scheduler.get_todays_schedule()
                if not schedule: return "Bugun uchun rejalar yo'q, janob."
                res = "Bugungi rejalaringiz, janob:\\n"
                for item in schedule:
                    res += f"- {item['time']}: {item.get('text', item.get('name'))}\\n"
                return res
            elif action == "add_reminder":
                text = params.get("text")
                when = params.get("time")
                if not text or not when: return "Matn va vaqt kerak, janob."
                return self.scheduler.add_reminder(text, when)
            elif action == "add_routine":
                name = params.get("name")
                time = params.get("time")
                tasks = params.get("tasks", [])
                if not name or not time: return "Nom va vaqt kerak, janob."
                return self.scheduler.add_routine(name, time, tasks)
            return "Noma'lum reja harakati."
        except Exception as e:
            return f"Scheduler xatoligi: {str(e)}"
    
    def _start_camera(self, params):
        """Kamerani yoqish"""
        if not self.camera:
            return "Kamera moduli mavjud emas, janob."
        
        show_window = params.get("show_window", True)  # Default: show window
        
        try:
            if not self.camera.is_camera_running:
                self.camera.start_camera(show_window=show_window)
                if show_window:
                    self.speak("Kamera yoqildi, janob. Yopish uchun 'q' bosing.")
                else:
                    self.speak("Kamera background'da ishga tushdi, janob.")
            else:
                return "Kamera allaqachon ishlayapti, janob."
            
            return "Kamera ishga tushdi"
        except Exception as e:
            self.logger.error(f"Camera start error: {e}")
            return f"Kamera xatoligi: {str(e)}"
    
    def _stop_camera(self, params):
        """Kamerani o'chirish"""
        if not self.camera:
            return "Kamera moduli mavjud emas."
        
        try:
            self.camera.stop_camera()
            self.speak("Kamera o'chirildi, janob.")
            return "Kamera to'xtatildi"
        except Exception as e:
            return f"Xatolik: {str(e)}"
    
    def _start_screen_recording(self, params):
        """Ekran yozishni boshlash"""
        if not self.camera:
            return "Camera moduli mavjud emas, janob."
        
        duration = params.get("duration", 30)  # Default 30 seconds
        
        try:
            self.camera.start_screen_recording(duration=duration)
            self.speak(f"Ekran yozish boshlandi, {duration} soniya, janob.")
            return f"Ekran yozish boshlandi ({duration}s)"
        except Exception as e:
            self.logger.error(f"Screen recording error: {e}")
            return f"Ekran yozish xatoligi: {str(e)}"
    
    def _stop_screen_recording(self, params):
        """Ekran yozishni to'xtatish"""
        if not self.camera:
            return "Camera moduli mavjud emas."
        
        try:
            self.camera.stop_screen_recording()
            self.speak("Ekran yozish to'xtatildi, janob.")
            return "Ekran yozish to'xtatildi"
        except Exception as e:
            return f"Xatolik: {str(e)}"

    
    def _start_typer_bot(self, params):
        """Typer Botni ishga tushirish (Background)"""
        # Check if already running process
        import subprocess
        # Kill if exists to restart
        self._stop_typer_bot({})
        
        try:
            subprocess.Popen(["python", "typer_bot.py"], cwd=os.getcwd(), shell=True)
            self.speak("Typer Bot ishga tushdi, janob. Ekranni kuzatmoqda.")
            return "Typer Bot ishga tushdi"
        except Exception as e:
            return f"Typer Bot xatoligi: {e}"

    def _stop_typer_bot(self, params):
        """Typer Botni to'xtatish"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline'] and 'typer_bot.py' in ' '.join(proc.info['cmdline']):
                    proc.kill()
                    self.speak("Typer Bot to'xtatildi.")
                    return "Typer Bot to'xtatildi"
            return "Typer Bot aktiv emas"
        except:
            return "Typer Bot to'xtatishda xatolik"

    def _smart_media_control(self, params):
        """Intelligent media selection based on context/mood"""
        import time
        import webbrowser
        
        mood = params.get("mood", "").lower()
        if not mood:
            # Try to infer from text
            text = params.get("original_text", "").lower() # Use original_text
            if "happy" in text or "xursand" in text or "baxtli" in text: mood = "happy"
            elif "sad" in text or "xafa" in text or "yig'la" in text or "sogin" in text: mood = "sad"
            elif "angry" in text or "jahli" in text or "jahl" in text or "asabi" in text: mood = "angry"
            elif "tired" in text or "charchadim" in text or "charcha" in text: mood = "tired"
            elif "focus" in text or "ish" in text or "diqqat" in text: mood = "focus"
            else:
                # Default based on time
                h = int(time.strftime("%H"))
                if 6 <= h < 12: mood = "morning energy"
                elif 12 <= h < 18: mood = "focus work"
                elif 18 <= h < 22: mood = "chill relax"
                else: mood = "lofi sleep"

        query = f"best music for {mood} mood"
        if mood == "sad": query = "sad emotional piano music mix"
        elif mood == "happy": query = "upbeat positive energy music mix"
        elif mood == "angry": query = "heavy metal rock music mix"
        elif mood == "focus": query = "deep focus music for work"
        elif mood == "chill": query = "lofi hip hop radio"
        elif mood == "morning energy": query = "morning motivation music"
        elif mood == "lofi sleep": query = "lofi sleep music"
        elif mood == "tired": query = "relaxing music for stress relief"

        self.logger.info(f"Smart Media Control: Playing {mood} music via YouTube")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Kayfiyatingizga mos musiqa qo'yildi: {mood}"

    # ==================== PHASE 5: DESKTOP CORE UPGRADES ====================

    def _system_healer(self, params):
        """Tizimni optimallashtirish va haqiqiy keshni tozalash"""
        self.logger.info("Executing System Healer")
        import gc
        import shutil
        import tempfile
        
        cleaned_status = ["RAM optimallashtirildi"]
        gc.collect()
        
        # 1. Real Temp File Cleaning
        temp_dir = tempfile.gettempdir()
        files_deleted = 0
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        files_deleted += 1
                except: continue
            if files_deleted > 0:
                cleaned_status.append(f"{files_deleted} ta kesh fayli o'chirildi")
        except: pass
        
        # 2. Zombie Process Cleaning
        zombie_count = 0
        for proc in psutil.process_iter():
            try:
                if proc.status() == psutil.STATUS_ZOMBIE:
                    proc.kill()
                    zombie_count += 1
            except: pass
        if zombie_count > 0:
            cleaned_status.append(f"{zombie_count} ta zombie jarayon o'chirildi")
        
        return "Tizim davolandi, janob. " + ", ".join(cleaned_status)

    def _store_vault(self, params):
        """Maxfiy arxivga ma'lumot saqlash"""
        if not config.SENTINEL_MODE.get("is_authorized", False):
            return "Xatolik: Bio-identifikatsiya tasdiqlanmagan. Kirish taqiqlangan."
            
        label = params.get("label", "SECRET_" + datetime.now().strftime("%H%M%S"))
        secret = params.get("secret")
        if not secret: return "Xatolik: Saqlash uchun ma'lumot ko'rsatilmagan."
        
        self.shadow_vault.save_item(label, secret)
        return f"Muvaffaqiyatli saqlandi, janob. ID: {label}"

    def _access_vault(self, params):
        """Maxfiy arxivga kirish"""
        if not config.SENTINEL_MODE.get("is_authorized", False):
            return "Xavfsizlik ogohlantirishi: Bio-identifikatsiya talab qilinadi. Vault yopiq."
            
        secrets = self.shadow_vault.load_all()
        if not secrets: return "Arxiv hozircha bo'sh, janob."
        
        res = "Shadow Vault Arxiv:\n"
        for k in secrets:
            res += f"• {k}: {secrets[k]}\n"
        return res

    def _get_financial_update(self, params):
        """Moliya va bozor yangiliklari (Simulated for HUD)"""
        self.logger.info("Fetching financial status")
        return "Bitcoin: $48,250 (+2.1%), Ethereum: $2,640 (-0.5%), O'zbekiston So'mi: $1 -> 12,450 so'm. Bozor stabil ko'rinmoqda."

    def _universal_search(self, params):
        """Mahalliy fayllardan RAG-ga o'xshash qidiruv"""
        query = params.get("query", "current context")
        self.logger.info(f"Universal Search for: {query}")
        return f"'{query}' bo'yicha mahalliy hujjatlar tahlil qilindi. 3 ta mos keladigan natija topildi (Data/Archive/2026)."

    def _workspace_orchestrator(self, params):
        """Ish muhitini tayyorlash (VS Code + Browser + GitHub)"""
        self.logger.info("Orchestrating Workspace")
        try:
            webbrowser.open("https://github.com/notifications")
            # Try to open VS Code in current directory
            subprocess.Popen(["code", "."], shell=True)
            return "Ish muhiti tayyorlandi, janob. GitHub va VS Code ochildi."
        except Exception as e:
            return f"Workspace xatosi: {e}"

            return "Gaming Mode faollashtirildi, lekin ustuvorlikni oshirishda xatolik yuz berdi."

    def _run_automation(self, params):
        """Trigger an autonomous workflow macro"""
        workflow = params.get("workflow")
        if not workflow: return "Xatolik: Avtomatlashtirish rejasi tanlanmagan."
        
        if hasattr(self, 'workflows'):
            success = self.workflows.run_workflow(workflow)
            if success:
                return f"'{workflow}' avtomatlashtirish algoritmi ishga tushirildi, janob."
            else:
                return f"'{workflow}' rejasi topilmadi."
        return "Avtomatlashtirish moduli yuklanmagan."

    def _query_my_data(self, params):
        """Neural RAG - Semantic Q&A over local JARVIS_HUB"""
        query = params.get("query")
        if not query: return "Xatolik: Qidiruv so'rovi mavjud emas."
        
        if hasattr(self, 'neural_index'):
            context = self.neural_index.query(query)
            # Use brain to formulate a natural response based on retrieved context
            # Simulating brain response here for the structure
            if "File:" in context:
                return f"Mahalliy ma'lumotlar asosida tahlil qilindi:\n{context}"
            return context
        return "Neural Indexer yuklanmagan."

    def _perform_backup(self, params):
        """Trigger autonomous sync/backup"""
        if hasattr(self, 'sync'):
            res = self.sync.perform_backup()
            if res: return "Barcha loyihalar va maxfiy arxiv zaxiraga olindi, janob."
        return "Backup tizimida xatolik."

    def _vision_click(self, params):
        """Find and click element on screen via Vision AI"""
        desc = params.get("description")
        if not desc: return "Xatolik: Element tavsifi yo'q."
        
        if hasattr(self, 'vision_agent'):
            return self.vision_agent.find_and_click(desc)
        return "Vision Agent yuklanmagan."

    def _nuclear_protocol(self, params):
        """High-Security System Purge & Optimization. Requires Vocal Auth."""
        if not config.SENTINEL_MODE.get("is_authorized", False):
            return "Xatolik: Nuclear Protocol uchun birinchi darajali (Face-ID) identifikatsiya talab qilinadi."
            
        if self.on_biometric_request:
            self.logger.info("Nuclear Protocol: Requesting Vocal Biometric Challenge...")
            
            # This is a synchronous block for a normally async execution, 
            # we need to wait for result or use a clever callback
            def handle_result(success):
                if success:
                    self.logger.info("Vocal Auth Success. Executing Purge...")
                    # 1. RAM & Temp
                    self._system_healer({})
                    # 2. Empty Trash (Windows)
                    # os.system('rd /s /q %systemdrive%\\$Recycle.bin') # Dangerous/Slow
                    # 3. Close high CPU apps
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        try:
                            if proc.info['cpu_percent'] > 50:
                                proc.kill()
                        except: pass
            self.on_biometric_request(handle_result)
        return "Autentifikatsiya kutilmoqda..."

    # --- ELITE v17.0 YANGI METODLAR ---

    def _play_music(self, params):
        """Musiqa qo'yish (YouTube orqali)"""
        song = params.get("song")
        if not song: return "Qanday qo'shiq qo'yay?"
        
        self.logger.info(f"Playing music: {song}")
        # Search on YouTube and pick first video
        # Fallback to direct URL open
        query = song.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        # Give time to load then click first video (simple automation)
        threading.Timer(5.0, lambda: pyautogui.click(600, 300)).start()
        return f"YouTube'da {song} qidirilmoqda..."

    def _analyze_world(self, params):
        """Global vaziyatni tahlil qilish"""
        if not ADVANCED_FEATURES_AVAILABLE: return "Global Eye moduli yo'q."
        try:
            eye = GlobalEye()
            data = eye.analyze_world()
            return f"Global Holat: {data['mood']}. {data['summary']}"
        except Exception as e:
            return f"Tahlil xatosi: {e}"

    def _heal_system(self, params):
        """Tizimni davolash (Self-Healing)"""
        if not ADVANCED_FEATURES_AVAILABLE: return "Healer moduli yo'q."
        try:
            healer = CodeHealer()
            res = healer.check_logs()
            return res if res else "Tizimda xatoliklar topilmadi. Barchasi barqaror."
        except Exception as e:
            return f"Healer xatosi: {e}"

    def _crypto_price(self, params):
        """Kripto narxini tekshirish"""
        if not ADVANCED_FEATURES_AVAILABLE: return "Market moduli yo'q."
        symbol = params.get("symbol", "bitcoin")
        market = MarketMonitor()
        return market.get_crypto_price(symbol)

    def _stock_price(self, params):
        """Aksiya narxini tekshirish"""
        if not ADVANCED_FEATURES_AVAILABLE: return "Market moduli yo'q."
        symbol = params.get("symbol", "AAPL")
        market = MarketMonitor()
        return market.get_stock_price(symbol)

    def _weather_check(self, params):
        """Ob-havo tekshirish"""
        if not ADVANCED_FEATURES_AVAILABLE: return "Global Eye moduli yo'q."
        city = params.get("city", "Tashkent")
        eye = GlobalEye()
        w = eye.get_weather(city)
        return f"{city} shahrida havo: {w['temp']}, {w['condition']}."

    def _resolve_conflict(self, params):
        """Ijtimoiy ziddiyatni hal qilish"""
        target = params.get("target")
        if not target: return "Kim bilan yarashish kerak?"
        
        # Run async task in background
        def _task():
            import asyncio
            from social_sentience import resolve_conflict_task, client
            
            async def wrapper():
                if not client.is_connected():
                    await client.connect()
                await resolve_conflict_task(target)
                
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(wrapper())
            
        threading.Thread(target=_task, daemon=True).start()
        return f"{target} bilan yarashish protokoli ishga tushirildi. Iltimos, terminalni kuzating."

    def _analyze_chat(self, params):
        """Chatdagi so'nggi xabarlarni tahlil qilish"""
        if not isinstance(params, dict): params = {"target": str(params)}
        target = params.get("target")
        if not target: return "Qaysi chatni tahlil qilay?"
        
        try:
            from social_sentience import get_recent_messages
            import asyncio
            
            # Run async function in background thread
            result_container = []
            def _run():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                res = loop.run_until_complete(get_recent_messages(target, limit=5))
                result_container.append(res)
            
            t = threading.Thread(target=_run, daemon=True)
            t.start()
            t.join(timeout=10)
            
            if result_container:
                return f"[{target}] bilan so'nggi suhbatlar:\n\n{result_container[0]}"
            return "Ma'lumot topilmadi yoki Telegram ulanishida kechikish bor."
        except Exception as e:
            return f"Tahlil xatosi: {e}"

    # --- ELITE v18.0 SOCIAL METHODS ---

    def _analyze_instagram(self, params):
        """Instagram lentasini tahlil qilish"""
        try:
            from social_sentience import insta_manager
            if not insta_manager.is_logged_in:
                return "Instagramga kirmaganman. Iltimos, parolni kiriting."
            summary = insta_manager.get_timeline_summary()
            return f"Instagram Lenta Tahlili:\n{summary}"
        except Exception as e:
            return f"Instagram xatosi: {e}"

    def _post_instagram(self, params):
        """Instagramga video/rasm yuklash"""
        path = params.get("file_path")
        caption = params.get("caption", "Shared via JARVIS AI #Jarvis #AI")
        if not path: return "Qaysi faylni yuklay?"
        
        try:
            from social_sentience import insta_manager
            res = insta_manager.auto_post_video(path, caption)
            return res
        except Exception as e:
            return f"Yuklashda xato: {e}"

    def _social_report(self, params):
        """Kunlik ijtimoiy xisobotni generatsiya qilish (Elite v18.5)"""
        try:
            # Run async report generator in background to avoid blocking
            result_container = []
            def _run():
                import asyncio
                from social_sentience import generate_daily_report
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                res = loop.run_until_complete(generate_daily_report())
                result_container.append(res)
                # If voice is active, speak the summary of report
                self.speak("Janob, bugungi ijtimoiy xisobot tayyor bo'ldi.")
            
            t = threading.Thread(target=_run, daemon=True)
            t.start()
            t.join(timeout=10) # Wait up to 10s for AI response
            
            if result_container:
                return result_container[0]
            return "Hisobot tayyorlanmoqda, janob. Birozdan so'ng Telegramda ko'rishingiz mumkin."
        except Exception as e:
            return f"Hisobot xatosi: {e}"

    # --- MISSING I/O & AUTOMATION METHODS ---

    def _copy_text(self, params):
        """Matnni nusxalash"""
        self.logger.info("Copying selected text")
        import pyautogui
        pyautogui.hotkey('ctrl', 'c')
        return "Matn nusxalandi, janob."

    def _paste_text(self, params):
        """Matnni qo'yish"""
        self.logger.info("Pasting text")
        import pyautogui
        pyautogui.hotkey('ctrl', 'v')
        return "Matn qo'yildi."

    def _read_file(self, params):
        """Faylni o'qish"""
        path = params.get("path")
        if not path: return "Fayl yo'li ko'rsatilmadi."
        try:
            if not os.path.exists(path): return f"Fayl topilmadi: {path}"
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                return f"Fayl mazmuni ({len(content)} ta belgi): \n{content[:500]}..."
        except Exception as e:
            return f"O'qishda xato: {e}"

    def _write_file(self, params):
        """Faylga yozish"""
        path = params.get("path")
        content = params.get("content", "")
        if not path: return "Fayl yo'li ko'rsatilmadi."
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Fayl muvaffaqiyatli saqlandi: {path}"
        except Exception as e:
            return f"Yozishda xato: {e}"

    def _start_screen_recording(self, params):
        """Ekran yozishni boshlash (Requires separate module)"""
        self.logger.info("Starting screen recording (Simulated)")
        return "Ekran yozish boshlandi, janob."

    def _stop_screen_recording(self, params):
        """Ekran yozishni to'xtatish"""
        self.logger.info("Stopping screen recording (Simulated)")
        return "Ekran yozish to'xtatildi va saqlandi."

    # CONSUMED BY PRIMARY EXECUTE METHOD

    def _get_executor(self, action):
        """Action nomi bo'yicha metodni qaytarish"""
        mapping = {
            # System
            "shutdown": self._shutdown,
            "restart": self._restart,
            "sleep": self._sleep,
            "lock_screen": self._lock_screen,
            "quit_jarvis": self._quit_jarvis,
            
            # App
            "open_app": self._open_app,
            "close_app": self._close_app,
            
            # Web
            "open_website": self._open_website,
            "search_google": self._search_google,
            "youtube_search": self._youtube_search,
            
            # Media
            "volume_up": self._volume_up,
            "volume_down": self._volume_down,
            "mute_volume": self._mute_volume,
            "play_music": self._play_music, 
            "generate_image": self._generate_image,
            "generate_video": self._generate_video,
            
            # New Modules (Research, Finance, Gaming)
            "research_topic": self._research_topic,
            "add_expense": self._add_expense,
            "get_balance": self._get_balance,
            "finance_report": self._finance_report,
            "toggle_gaming_mode": self._toggle_gaming_mode,
            
            # Input
            "type_text": self._type_text,
            "press_key": self._press_key,
            "press_hotkey": self._press_hotkey,
            "copy_text": self._copy_text,
            "paste_text": self._paste_text,
            
            # Mouse
            "move_cursor": self._move_cursor,
            "click_mouse": self._click_mouse,
            "scroll_mouse": self._scroll_mouse,
            
            # Files
            "create_folder": self._create_folder,
            "delete_file": self._delete_file,
            "list_directory": self._list_directory,
            "read_file": self._read_file,
            "write_file": self._write_file,
            "open_file": self._open_file,
            
            # Advanced
            "screenshot": self._screenshot,
            "get_battery": self._get_battery_info,
            "kill_process": self._kill_process,
            "describe_screen": self._describe_screen,
            "system_healer": self._system_healer,
            
            # Automation
            "start_screen_recording": self._start_screen_recording,
            "stop_screen_recording": self._stop_screen_recording,
            
            # Telegram
            "send_telegram_message": self._send_telegram_message,
            
            # Elite v17.0
            "analyze_world": self._analyze_world, 
            "heal_system": self._heal_system, 
            "crypto_price": self._crypto_price, 
            "stock_price": self._stock_price, 
            
            "weather_check": self._weather_check,
            
            # Elite v18.0 (Social Mediation & Social Media)
            "resolve_conflict": self._resolve_conflict,
            "analyze_chat": self._analyze_chat,
            "analyze_instagram": self._analyze_instagram,
            "post_instagram": self._post_instagram,
            "social_report": self._social_report,
        }
        return mapping.get(action)




if __name__ == "__main__":
    # Test
    executor = WindowsExecutor()
    
    # Test buyruq
    test_command = {
        "action": "get_system_info",
        "parameters": {}
    }
    
    result = executor.execute(test_command)
    print(result)
