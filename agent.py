"""
JARVIS - System Level AI Assistant
"""

import json
import sys
import threading
from executor import WindowsExecutor
from parser import CommandParser
from llm_brain import GeminiBrain
from utils import (
    setup_logger, validate_json_command, is_destructive_action,
    confirm_action, format_error_response
)

# CLI ranglar
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback - ranglar yo'q
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

from memory import MemoryEngine
from security import SecurityEngine
from translator import LanguageProcessor
from automation import AutomationEngine

class JARVIS:
    """
    JARVIS - Core AI Engine
    Markaziy muvofiqlashtiruvchi va mantiqiy markaz.
    """
    
    def __init__(self):
        self.logger = setup_logger("JARVIS")
        
        # Hybrid Mode Check
        try:
            from config import HYBRID_MODE
            self.hybrid_mode = HYBRID_MODE
        except:
            self.hybrid_mode = False

        # Core Modullar (Engines)
        self.executor = WindowsExecutor()
        self.parser = CommandParser()
        
        if self.hybrid_mode:
            self.logger.info("☁️  JARVIS Core starting in HYBRID EXECUTION mode.")
            self.brain = None # Brain is on the Cloud
            self.memory = MemoryEngine()
            self.security = SecurityEngine(memory=self.memory)
            self.translator = None 
            self.automation = None
        else:
            self.brain = GeminiBrain()
            self.memory = MemoryEngine()
            self.security = SecurityEngine(memory=self.memory)
            self.translator = LanguageProcessor()
            self.automation = AutomationEngine(core=self)
        self.voice = None # GUI yoki CLI tomonidan o'rnatiladi
        self.pending_command = None # Tasdiqlash kutilayotgan buyruq
        self.on_speak = None # CALLBACK (Phase 4 Refinement)
        self.on_research_log = None # NEW: For HUD Research Terminal
        self.lock = threading.Lock() # Thread safety lock
        
        # 2. Telegram User Bridge (Background Messaging & Auto-Reply)
        if not self.hybrid_mode:
            try:
                from telegram_user_bridge import TelegramUserBridge
                self.telegram_bridge = TelegramUserBridge()
                threading.Thread(target=self.telegram_bridge.run, daemon=True).start()
                self.executor.telegram_bridge = self.telegram_bridge
            except Exception as e:
                self.logger.warning(f"Telegram User Bridge initialization failed: {e}")
        else:
            self.telegram_bridge = None
            self.logger.info("☁️  Telegram Bridge offloaded to Cloud.")

        # 2.5 Telegram Bot (Command Center) - Now runs via start.py
        # try:
        #     from telegram_bot import TelegramBot
        #     self.telegram_bot = TelegramBot()
        #     # Disable signal handling in thread to avoid ValueError
        #     threading.Thread(target=lambda: self.telegram_bot.run(), daemon=True).start()
        #     self.logger.info("Telegram Bot Command Center started.")
        # except Exception as e:
        #     self.logger.warning(f"Telegram Bot initialization failed: {e}")
            
        # 3. Mood Engine (Emotional AI)
        from mood_engine import MoodEngine
        self.mood = MoodEngine()
        
        if not self.hybrid_mode:
            # 4. Vision Engine (On-Demand)
            from vision_engine import VisionEngine
            self.vision = VisionEngine(brain_module=self.brain)
    
            # 5. Research Assistant
            from research_assistant import ResearchAssistant
            self.research = ResearchAssistant()
    
            # 6. Neural Indexer (Second Brain / RAG)
            from neural_indexer import NeuralIndexer
            self.neural_indexer = NeuralIndexer(brain=self.brain)
            # Start background indexing
            # self.neural_indexer.index_hub()
            
            # 7. Proactive Vision (Elite v20.0)
            from proactive_vision import ProactiveVision
            self.proactive_vision = ProactiveVision(core=self, brain=self.brain)
            # self.proactive_vision.start()
            
            # 8. Self-Healing System (Healer)
            from healer import CodeHealer
            self.healer = CodeHealer(core=self)
        else:
            self.vision = None
            self.research = None
            self.neural_indexer = None
            self.proactive_vision = None
            self.healer = None
        self._start_healer_monitor()
        
        # 9. Elite Personal AI (Custom)
        from elite_ai import EliteAI
        self.elite_ai = EliteAI()
        
        # Avtomatizatsiyani boshlash
        self.automation.start()
        
        self.logger.info("Elite JARVIS Core initialized.")
        
        # Start Remote Command Listener
        self._start_remote_listener()

    def _start_healer_monitor(self):
        """Fondagi xatolarni avtomatik tuzatish moduli"""
        def monitor():
            while True:
                try:
                    fix_msg = self.healer.check_logs()
                    if fix_msg:
                        self.logger.info(f"🔧 {fix_msg}")
                        # Optionally notify user via speak or HUD
                        self.speak(fix_msg)
                except Exception as e:
                    self.logger.error(f"Healer monitor error: {e}")
                import time
                time.sleep(30) # Har 30 soniyada loglarni tekshirish
        
        threading.Thread(target=monitor, daemon=True).start()

    def _start_remote_listener(self):
        """Fondagi masofaviy buyruqlarni kuzatish (Web/Mobile/Telegram)"""
        import os
        import time
        def monitor():
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cmd_file = os.path.join(base_dir, "data", "remote_command.txt")
            self.logger.warning(f"[DEBUG MONITOR] Watching: {cmd_file}")
            
            while True:
                try:
                    if os.path.exists(cmd_file):
                        self.logger.warning(f"[DEBUG MONITOR] Found command file!")
                        try:
                            with open(cmd_file, "r", encoding="utf-8") as f:
                                text = f.read().strip()
                            
                            self.logger.warning(f"[DEBUG MONITOR] Content: '{text}'")
                            
                            if text:
                                self.logger.warning(f"[DEBUG MONITOR] Processing: {text}")
                                self.process_command(text)
                            
                            try:
                                os.remove(cmd_file)
                                self.logger.warning("[DEBUG MONITOR] File removed.")
                            except Exception as rm_err:
                                self.logger.error(f"[DEBUG MONITOR] Remove error: {rm_err}")
                        except Exception as read_err:
                            self.logger.error(f"[DEBUG MONITOR] Read error: {read_err}")
                        
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.error(f"Monitor Error: {e}")
                    time.sleep(1)
        
        threading.Thread(target=monitor, daemon=True).start()
        self.logger.info("Remote listener active.")

    def set_voice(self, voice_assistant):
        """Ovozli yordamchini integratsiya qilish"""
        self.voice = voice_assistant
        self.executor.set_voice(voice_assistant)  # Connect executor to voice
        self.logger.info("Voice Assistant integrated with Core and Executor.")

    def speak(self, text):
        """Matnni ovozga o'girish (Base implementation)"""
        if self.voice:
            if hasattr(self.voice, 'speak'):
                self.voice.speak(text)
        else:
            print(f"[JARVIS SPEAKS] {text}")
            # Direct pyttsx3 fallback
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                print("[TTS] Speak finished.")
            except Exception as e:
                self.logger.error(f"TTS Error: {e}")
            
        # Trigger Callback
        if self.on_speak:
            self.on_speak(text)
        
    def _detect_language(self, text):
        """Til aniqlash (Translator Engine orqali)"""
        return self.translator.detect_language(text)
    
    def _get_category(self, action):
        """Action bo'yicha kategoriyani aniqlash"""
        categories = {
            "shutdown": "SYSTEM_CONTROL",
            "restart": "SYSTEM_CONTROL",
            "sleep": "SYSTEM_CONTROL",
            "lock_screen": "SYSTEM_CONTROL",
            "quit_jarvis": "SYSTEM_CONTROL",
            
            "open_app": "APPLICATION_CONTROL",
            "close_app": "APPLICATION_CONTROL",
            "focus_app": "APPLICATION_CONTROL",
            "write_in_app": "APPLICATION_CONTROL",
            
            "open_website": "INTERNET_SEARCH",
            "search_google": "INTERNET_SEARCH",
            
            "create_folder": "FILE_MANAGEMENT",
            "delete_file": "FILE_MANAGEMENT",
            "open_file": "FILE_MANAGEMENT",
            "list_directory": "FILE_MANAGEMENT",
            
            "send_telegram_message": "COMMUNICATION",
            
            "get_time": "INFORMATIONAL_RESPONSE",
            "get_date": "INFORMATIONAL_RESPONSE",
            "get_weather": "INFORMATIONAL_RESPONSE",
            "get_system_info": "DEVICE_STATUS",
            
            # Media & Browser (Yangi)
            "youtube_search": "INTERNET_SEARCH",
            "youtube_comment": "INTERNET_SEARCH",
            "google_search_click": "INTERNET_SEARCH",
            "start_camera": "DEVICE_CONTROL",
            "stop_camera": "DEVICE_CONTROL",
            "start_screen_recording": "DEVICE_CONTROL",
            "stop_screen_recording": "DEVICE_CONTROL",
            "start_gesture_control": "DEVICE_CONTROL",
            "stop_gesture_control": "DEVICE_CONTROL",
            "start_typer_bot": "AUTOMATION",
            "stop_typer_bot": "AUTOMATION",
            "create_project": "AUTOMATION",
            "analyze_codebase": "AUTOMATION",
            "run_terminal_v2": "AUTOMATION",
            "reset_sentinel": "SYSTEM_CONTROL",
            "register_face": "DEVICE_CONTROL",
            "smart_search": "FILE_MANAGEMENT",
            "system_healer": "AUTOMATION",
            "get_financial_update": "INFORMATIONAL_RESPONSE",
            "universal_search": "FILE_MANAGEMENT",
            "workspace_orchestrator": "AUTOMATION",
            "toggle_gaming_mode": "SYSTEM_CONTROL",
            "perform_research": "INFORMATIONAL_RESPONSE",
            "scan_bluetooth": "DEVICE_CONTROL",
            "start_remote_bridge": "DEVICE_CONTROL",
            "connect_device": "DEVICE_CONTROL",
            "ai_conversation": "AI_BRAIN",
            "get_news_digest": "INFORMATIONAL_RESPONSE",
            "voice_clone_speak": "COMMUNICATION",
            "get_security_report": "DEVICE_STATUS",
            "desktop_automation": "AUTOMATION",
            "smart_media_control": "DEVICE_CONTROL",
            "advanced_schedule_manage": "AUTOMATION",
            "connect_account": "AI_BRAIN",
            "learn_from_feedback": "AI_BRAIN",
        }
        return categories.get(action, "lz_ACTION")
 
    def _generate_verbal_response(self, action, params, status, result):
        """Elite AI response via LanguageProcessor"""
        user_name = self.memory.get_user_name()
        # command_text = params.get('original_text', '')
        # lang = self._detect_language(command_text) if command_text else "uz"
        
        # User Request: Force Uzbek Language
        lang = "uz"
        
        return self.translator.get_action_response(
            action=action, 
            status=status, 
            lang=lang, 
            user_name=user_name,
            result=result,
            **params
        )




    def _handle_vision(self):
        verbal = self.vision.describe_screen()
        return {"status": "success", "action": "vision_analysis", "verbal_response": verbal}

    def _handle_optimization(self):
        import gc
        gc.collect()
        verbal = "Tizim optimallashtirildi. Kesh xotirasi tozalandi."
        return {"status": "success", "action": "optimization", "verbal_response": verbal}

    def _handle_focus(self, enable):
        # Placeholder for meaningful focus logic
        verbal = "Diqqat rejimi yoqildi." if enable else "Diqqat rejimi o'chirildi."
        return {"status": "success", "action": "focus_mode", "verbal_response": verbal}

    def process_command(self, text):
        """
        Buyruqni qayta ishlash - ELITE CORE LOGIC
        """
        try:
            with open("debug_commands.txt", "a", encoding="utf-8") as f:
                f.write(f"RECEIVED: {text}\n")
        except: pass

        # HUD DIRECT COMMANDS
        if text == "describe screen": return self._handle_vision()
        if text == "optimize system": return self._handle_optimization()
        if text == "enable focus mode": return self._handle_focus(True)
        if text == "disable focus mode": return self._handle_focus(False)

        with self.lock:
            self.logger.info(f"Elite Processing: {text}")
        
        try:
            # 0. Kontekstdan o'rganish
            self._learn_from_text(text)
            
            # 1. Til aniqlash va Xavfsizlik tekshiruvi
            lang = self._detect_language(text)
            parsed = self.parser.parse(text)
            action = parsed.get("action", "unknown")
            params = parsed.get("parameters", {})
            params['original_text'] = text
            user_name = self.memory.get_user_name()
            

            # 2. AI BRAIN ROUTING (agar action noma'lum bo'lsa)
            ai_verbal = None
            vision_keywords = ["rasm", "ekran", "bu nima", "ko'r", "see", "screen", "picture", "what is this"]
            
            if action == "unknown":
                if self.hybrid_mode:
                    return {"verbal_response": "Janob, hozirda GIBERID rejimdaman. Aqlli savollar va tadqiqotlarni Telegram bot orqali amalga oshirishingizni so'rayman.", "success": True}
                
                if self.brain and self.brain._initialized:
                    # Check if it's a vision request
                    if any(k in text.lower() for k in vision_keywords):
                        self.logger.info("Vision request detected. Capturing screen...")
                        # Take a quick screenshot for context
                        snap_path = "vision_context.png"
                        self.executor.execute({"action": "screenshot", "parameters": {"path": snap_path}})
                        # Analyze with context
                        prompt = f"User asked: '{text}'. Based on the screen image, provide a concise verbal response."
                        ai_verbal = self.brain.analyze_image(snap_path, prompt)
                        if ai_verbal == "ERROR_QUOTA_EXCEEDED":
                            ai_verbal = "Janob, hozirda tahlil quvvatim yetmayapti. Bir ozdan keyin urinib ko'ring."
                        action = "ai_conversation"
                    else:
                        # --- LONG-TERM MEMORY INTEGRATION ---
                        # 1. Retrieve Facts
                        facts = self.memory.search_facts(text)
                        context_prompt = text
                        if facts:
                            fact_list = "\n".join([f"- {f[0]}" for f in facts])
                            context_prompt = f"CONTEXT (User Facts):\n{fact_list}\n\nUSER QUERY:\n{text}"
                            self.logger.info(f"Memory Augmented Prompt with {len(facts)} facts.")

                        # 1.5. Retrieve Local Documents (RAG)
                        local_context = self.neural_indexer.query(text)
                        if local_context and "topilmadi" not in local_context:
                             context_prompt = f"LOCAL DOCUMENTS (RAG):\n{local_context}\n\n" + context_prompt
                             self.logger.info("RAG Context injected into Brain prompt.")

                        # 2. Generate Response (Elite AI Personalized)
                        ai_verbal = self.elite_ai.process(text)
                        
                        # 3. Extract New Facts (Background)
                        if len(text) > 10:
                            threading.Thread(
                                target=self.brain.extract_and_save_facts,
                                args=(text, self.memory),
                                daemon=True
                            ).start()
                        
                        if ai_verbal:
                            action = "ai_conversation"
            
            # 4. Execute qilish
            if action != "ai_conversation" and action != "unknown":
                command_dict = {"action": action, "parameters": params}
                
                # Odatlarni saqlash (Ilova ochilganda)
                if action == "open_app" and "app_name" in params:
                    self.memory.log_app_usage(params["app_name"])
                
                # --- SECURITY & CONFIRMATION ---
                if action == "confirm" and self.pending_command:
                    command_dict = self.pending_command
                    action = command_dict["action"]
                    params = command_dict["parameters"]
                    self.pending_command = None
                elif action == "emergency":
                    self.security.toggle_emergency(True)
                    self.executor.execute({"action": "lock_screen", "parameters": {}})
                    # Elite response using translator
                    verbal = self.translator.get_action_response("emergency", "success", lang, user_name=user_name)
                    return {"verbal_response": verbal, "action": "emergency"}
                else:
                    is_safe, msg, severity = self.security.validate_command(action, params)
                    if not is_safe:
                        if severity == "MEDIUM":
                            self.pending_command = command_dict
                            verbal = self.translator.get_action_response("request_confirmation", "success", lang, user_name=user_name)
                            return {"verbal_response": verbal, "action": "request_confirmation"}
                        else:
                            verbal = self.translator.get_action_response("security_denied", "success", lang, user_name=user_name)
                            return {"verbal_response": verbal, "action": "security_denied"}

                # --- AUTOMATION ROUTING ---
                if action == "protocol":
                    self.automation.execute_protocol(params.get("name"))
                    result = f"Protocol {params.get('name')} triggered"
                
                elif action == "schedule":
                    sub_cmd = params.get("sub_action", "")
                    sub_parsed = self.parser.parse(sub_cmd)
                    self.automation.add_scheduled_task(
                        params.get("time"), 
                        sub_parsed.get("action"), 
                        sub_parsed.get("parameters")
                    )
                    result = f"Scheduled {sub_parsed.get('action')} at {params.get('time')}"
                
                elif action == "timer":
                    sub_cmd = params.get("sub_action", "")
                    sub_parsed = self.parser.parse(sub_cmd)
                    self.automation.add_timer(
                        params.get("minutes"), 
                        sub_parsed.get("action"), 
                        sub_parsed.get("parameters")
                    )
                    result = f"Timer set for {params.get('minutes')} mins: {sub_parsed.get('action')}"
                
                else:
                    # Normal Execution
                    result_data = self.executor.execute(command_dict)
                    result = result_data.get("result", result_data) if isinstance(result_data, dict) else result_data
                
                category = self._get_category(action)
                verbal = self._generate_verbal_response(action, params, "success", result)
            elif action == "ai_conversation":
                result = "AI Conversation"
                category = "AI_BRAIN"
                verbal = ai_verbal
            else:
                result = "Unknown command"
                category = "UNKNOWN"
                verbal = self.translator.get_action_response("unknown", "success", lang, user_name=user_name)
            
            # 5. Xotiraga saqlash
            self.memory.add_to_history(text, verbal)
            
            # 6. Ovozli javob berish (SPEAK the verbal response)
            self.speak(verbal)
            
            # Emotional Analysis (Phase 2)
            emotion, emotion_color = self.mood.analyze_text_emotion(text)
            
            # Response assembly
            response = {
                "status": "success",
                "action": action,
                "category": category,
                "parameters": params,
                "result": result,
                "verbal_response": verbal,
                "lang": lang,
                "emotion": emotion,
                "emotion_color": emotion_color
            }
            
        except Exception as e:
            self.logger.error(f"Elite Core Error: {e}")
            user_name = self.memory.get_user_name()
            lang = "uz" # Default for critical core errors
            verbal = self.translator.get_action_response("error", "failure", lang, user_name=user_name, error_message=str(e))
            
            # Speak error message too
            self.speak(verbal)
            
            response = {
                "status": "error", "action": "error", "verbal_response": verbal, "result": str(e)
            }
        
        return response

    def _learn_from_text(self, text):
        """Matndan foydalanuvchi haqida ma'lumot olish"""
        text_lower = text.lower()
        
        # Ismni o'rganish
        name_patterns = ["mening ismim ", "ismim ", "meni ... deb chaqir"]
        for p in name_patterns:
            if p in text_lower:
                new_name = text[text_lower.find(p) + len(p):].strip().split()[0]
                # Tozalash
                new_name = new_name.replace(".", "").replace("!", "").replace(",", "")
                self.memory.set_user_info("name", new_name)
                self.logger.info(f"Yangi ism eslab qolindi: {new_name}")
        
        # Loyihalarni o'rganish
        if "loyiha" in text_lower or "project" in text_lower:
            # Sodda NER simulyatsiyasi
            words = text.split()
            for i, w in enumerate(words):
                if w.lower() in ["loyiha", "loyiham", "project"] and i < len(words) - 1:
                    proj_name = words[i+1].strip(" '\".,")
                    if len(proj_name) > 2:
                        self.memory.add_project(proj_name)
                        self.logger.info(f"Yangi loyiha aniqlandi: {proj_name}")


    def execute_automation(self, action, params):
        """Avtomatizatsiya (background) tomonidan chaqiriladigan metod"""
        self.logger.info(f"Background executing: {action}")
        
        # Ovozli xabar bo'lsa
        if action == "speak":
            text = params.get("text", "")
            self.speak(text)
            return

        # Boshqa amallar
        self.executor.execute({"action": action, "parameters": params})

    def get_elite_greeting(self, lang="uz"):
        """Vaqtga qarab salomlashish"""
        user_name = self.memory.get_user_name()
        return self.translator.get_greeting(lang, user_name)

    def interactive_mode(self):
        """
        Interaktiv CLI rejimi (Rangdor interfeys)
        """
        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}{Style.BRIGHT}🤖 JARVIS - System Level AI Assistant{Style.RESET_ALL}")
        print("=" * 60)
        print(f"\n{Fore.YELLOW}Buyruq turlari:{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}1. Tabiiy til (o'zbek/ingliz): {Fore.GREEN}'Chrome och', 'YouTube och'{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}2. Yozish: {Fore.GREEN}'Notepadda Salom deb yoz'{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Chiqish uchun:{Style.RESET_ALL} {Fore.RED}'exit', 'quit', 'chiq'{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Yordam uchun:{Style.RESET_ALL} {Fore.CYAN}'help', 'yordam'{Style.RESET_ALL}")
        print("=" * 60 + "\n")
        
        while True:
            try:
                # Input olish
                user_input = input(f"{Fore.MAGENTA}JARVIS >>> {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Chiqish buyruqlari
                if user_input.lower() in ["exit", "quit", "chiq", "q"]:
                    print(f"\n{Fore.CYAN}👋 Xayr! JARVIS to'xtatildi.{Style.RESET_ALL}")
                    break
                
                # Yordam
                if user_input.lower() in ["help", "yordam", "h"]:
                    self._print_help()
                    continue
                
                # Buyruqni bajarish
                response = self.process_command(user_input)
                
                # Natijani rangdor chiqarish
                verbal = response.get('verbal_response', 'Tayyor')
                if response.get("action") == "error" or "error" in verbal.lower():
                    print(f"{Fore.RED}❌ {verbal}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✓ {verbal}{Style.RESET_ALL}")
                
                # Speak (CLI Mode)
                if verbal:
                    self.speak(verbal)
                
                # JSON (debug)
                print(f"{Fore.WHITE}{json.dumps(response, indent=2, ensure_ascii=False)}{Style.RESET_ALL}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Xayr! JARVIS to'xtatildi.{Style.RESET_ALL}")
                break
            
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                print(f"\n{Fore.RED}❌ Xatolik: {e}{Style.RESET_ALL}")

    def _print_help(self):
        """Yordam ma'lumotini chop etish (kengaytirilgan)"""
        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}{Style.BRIGHT}📚 JARVIS YORDAM / HELP{Style.RESET_ALL}")
        print("=" * 60)
        
        print(f"\n{Fore.YELLOW}📱 ILOVALAR (Applications):{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• Chrome och{Style.RESET_ALL} / Open Chrome")
        print(f"  {Fore.GREEN}• Notepad yop{Style.RESET_ALL} / Close Notepad")
        print(f"  {Fore.GREEN}• Notepadda Salom deb yoz{Style.RESET_ALL} {Fore.CYAN}(NEW){Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}🌐 INTERNET:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• YouTube och{Style.RESET_ALL} / Open YouTube")
        print(f"  {Fore.GREEN}• Google'da Python qidir{Style.RESET_ALL} / Search Google Python")
        print(f"  {Fore.GREEN}• GitHub och{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}💬 ALOQA (Communication):{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• Telegramda Saved Messages'ga Salom deb yoz{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• telegram Shaboz Salom{Style.RESET_ALL} {Fore.CYAN}(Qisqa format){Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}📁 FAYL TIZIMI (File System):{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• test papka yarat{Style.RESET_ALL} / Create folder test")
        print(f"  {Fore.GREEN}• C:\\test papka ko'rsat{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}💻 TIZIM MA'LUMOTLARI (System Info):{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• Soat necha{Style.RESET_ALL} / Get time")
        print(f"  {Fore.GREEN}• Bugun qaysi sana{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• Tizim haqida{Style.RESET_ALL} / System info")
        
        print(f"\n{Fore.YELLOW}⌨️ KLAVIATURA (Keyboard):{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• Enter bos{Style.RESET_ALL} / Press Enter")
        print(f"  {Fore.GREEN}• Alt F4 bos{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}🎤 OVOZ (Voice Mode):{Style.RESET_ALL} {Fore.CYAN}(NEW){Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• py agent.py --voice{Style.RESET_ALL}")
        print(f"    Ovoz orqali buyruq berish")
        
        print(f"\n{Fore.RED}⚠️ XAVFLI BUYRUQLAR (Destructive):{Style.RESET_ALL}")
        print(f"  {Fore.RED}• Kompyuterni o'chir{Style.RESET_ALL} (Tasdiqlash so'raladi)")
        print(f"  {Fore.RED}• Qayta ishga tushir{Style.RESET_ALL}")
        
        print("=" * 60 + "\n")

def main():
    """Main entry point"""
    import sys
    
    # GUI mode
    if "--gui" in sys.argv or len(sys.argv) == 1:
        # Agar hech qanday argument bo'lmasa yoki --gui bo'lsa
        try:
            from gui import JarvisGUI
            app = JarvisGUI()
            app.run()
            return
        except ImportError:
            print("⚠️ GUI kutubxonalari topilmadi. pip install customtkinter")
            print("Text rejimga o'tilmoqda...\n")
    
    # Voice mode
    if "--voice" in sys.argv:
        try:
            voice_jarvis = VoiceJARVIS()
            voice_jarvis.voice_interactive_mode()
        except ImportError as e:
            print(f"⚠️ Voice kutubxonalari topilmadi: {e}")
            print("Text rejimga o'tilmoqda...\n")
            jarvis = JARVIS()
            jarvis.interactive_mode()
        return
    
    # Bitta buyruq (command line argument)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        command = " ".join(sys.argv[1:])
        jarvis = JARVIS()
        response = jarvis.process_command(command)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return
    
    # Interactive mode (default)
    jarvis = JARVIS()
    jarvis.interactive_mode()


class VoiceJARVIS(JARVIS):
    """
    JARVIS - Ovozli interfeys
    """
    
    def __init__(self):
        super().__init__()
        # Voice modulini import qilish
        try:
            from voice import VoiceAssistant
            from config import VOICE_SETTINGS
            
            self.voice = VoiceAssistant(
                language=VOICE_SETTINGS.get("language", "uz-UZ"),
                fallback_language=VOICE_SETTINGS.get("fallback_language", "en-US"),
                speech_rate=VOICE_SETTINGS.get("speech_rate", 150),
                volume=VOICE_SETTINGS.get("volume", 1.0),
                enable_tts=VOICE_SETTINGS.get("enable_tts", True),
                enable_stt=VOICE_SETTINGS.get("enable_stt", True),
            )
            self.voice_enabled = True
            self.listen_timeout = VOICE_SETTINGS.get("listen_timeout", 5)
            self.phrase_time_limit = VOICE_SETTINGS.get("phrase_time_limit", 10)
        except ImportError as e:
            print(f"⚠ Voice moduli yuklanmadi: {e}")
            self.voice = None
            self.voice_enabled = False
    
    def speak(self, text):
        """Matnni ovozga o'girish (Edge TTS -> Silent Fallback to pyttsx3)"""
        super().speak(text)
    
    def listen(self):
        """Ovozni tinglash"""
        if self.voice_enabled and self.voice and self.voice.is_speech_available():
            return self.voice.listen(
                timeout=self.listen_timeout,
                phrase_time_limit=self.phrase_time_limit
            )
        return None
    
    def voice_interactive_mode(self):
        """
        Ovozli interaktiv rejim
        """
        print("\n" + "=" * 60)
        print("🎤 JARVIS - Voice Mode")
        print("=" * 60)
        
        if not self.voice_enabled:
            print("⚠ Voice moduli mavjud emas. Text rejimida davom etilmoqda.")
            self.interactive_mode()
            return
        
        self.speak("Salom! Men JARVIS. Sizga qanday yordam bera olaman?")
        
        print("\nBuyruq berish: ovoz bilan gapiring")
        print("Chiqish uchun: 'chiq', 'exit' yoki Ctrl+C")
        print("=" * 60 + "\n")
        
        from config import EXIT_COMMANDS
        
        while True:
            try:
                # Ovozni tinglash
                user_input = self.listen()
                
                if not user_input:
                    print("⚠ Ovoz tanib olinmadi. Qayta urinib ko'ring.")
                    continue
                
                print(f"📝 Siz: {user_input}")
                
                # Chiqish buyruqlari
                if user_input.lower() in EXIT_COMMANDS:
                    self.speak("Xayr! JARVIS to'xtatildi.")
                    break
                
                # Buyruqni bajarish
                response = self.process_command(user_input)
                
                # Javob
                verbal = response.get("verbal_response", "Buyruq bajarildi.")
                print(f"💬 JARVIS: {verbal}")
                self.speak(verbal)
                
                # JSON chiqarish (debug uchun)
                print(json.dumps(response, indent=2, ensure_ascii=False))
            
            except KeyboardInterrupt:
                print("\n")
                self.speak("Xayr! JARVIS to'xtatildi.")
                break
            
            except Exception as e:
                self.logger.error(f"Voice mode error: {e}")
                print(f"❌ Xatolik: {e}")


if __name__ == "__main__":
    main()

