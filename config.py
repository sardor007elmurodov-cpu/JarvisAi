"""
JARVIS - Configuration
Ultra Modern AI System
"""

# === JARVIS PRIME PERSONA ===
SYSTEM_PROMPT = """
You are J.A.R.V.I.S, an advanced AI system.
Your primary goal is to assist the user, Sardor, with any task.
You must learn from every interaction and improve your responses.
Consult with other AI models internally to verify your knowledge and gain experience.
Your responses should be professional, concise, and helpful.
Use the collected knowledge to personalize your service.
SIZNING PROTOKOLLARINGIZ:
1. FOYDALANUVCHI: Sizning yaratuvchingiz va yagona xo'jayiningiz. Unga "Janob" deb murojaat qiling.
2. OVOZ: Chuqur, ishonchli, sokin va professional.
3. NUTQ: Keraksiz so'zlar va emoji yo'q. Faqat aniq ma'lumot va professional javoblar.
4. TILLAR: O'zbek (Qat'iy faqat o'zbek tilida gapiring).
5. SHAXSIYAT: Aqlli, hurmatli, kamgap, lekin har doim yordamga tayyor.
7. QAT'IY QOIDA: Javoblaringiz 100% sof O'zbek tilida bo'lishi shart. Ingliz yoki Rus so'zlarini ishlatmang (faqat texnik atamalar mustasno).
8. AGAR TUSHUNMASANGIZ: "Janob, buyruqni aniqlashtiring" deb so'rang.
"""

# === UI COLORS (SUPER JARVIS PRIME) ===
# Stylized as High-Tech Cyan HUD
UI_COLORS = {
    "bg_dark": "#000000",        # Pitch Black
    "bg_panel": "#0a0f14",      # HUD Dark Grey/Blue
    "neon_cyan": "#00e0ff",     # Primary HUD Color (Elite Cyan)
    "electric_blue": "#00ffff", # Highlight
    "text_primary": "#00e0ff",  # Matching HUD Text
    "text_secondary": "#00a0b0", # Dimmed HUD Text
    "glow_color": "#00e0ff",
    "error_red": "#ff0033",
    "warning_orange": "#ffaa00"
}

# Responses for Wake word
WAKE_WORDS = ["jarvis", "hey jarvis", "jarvis prime", "jervis", "jarviz"]
WAKE_RESPONSES = [
    "Ha, janob. Eshitaman.", 
    "Buyruq bering, janob.", 
    "Tizim onlayn, janob.", 
    "Sizni eshityapman, janob."
]

# AI Brain Settings
# AI Brain Settings
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") # Groq API Key (Free tier at groq.com)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "") 
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "") # Hugging Face TGI/Inference
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL_NAME = "models/gemini-2.0-flash"
FALLBACK_MODEL_NAME = "llama-3.3-70b-versatile"
DEEPSEEK_MODEL_NAME = "deepseek-chat"
MISTRAL_MODEL_NAME = "mistral-small-latest"
HUGGINGFACE_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
# Response Settings
RESPONSE_SETTINGS = {
    "max_length": 300, # Increased for brain power
    "tone": "professional",
    "use_status": True,
    "user_name": "Sardor"
}

# Adaptive Persona Temperament
CURRENT_TEMPERAMENT = "PROFESSIONAL" # Options: PROFESSIONAL, ENTHUSIASTIC, CALM

# Qo'llab-quvvatlanadigan action'lar
SUPPORTED_ACTIONS = [
    # System Control
    "shutdown",
    "restart", 
    "sleep",
    "lock_screen",
    
    # Application Control
    "open_app",
    "close_app",
    "focus_app",
    
    # Web Control
    "open_website",
    "search_google",
    
    # Messaging
    "send_telegram_message",
    
    # Write in App
    "write_in_app",
    
    # File System
    "create_folder",
    "delete_file",
    "open_file",
    "list_directory",
    
    # Input Control
    "type_text",
    "press_key",
    "press_hotkey",
    "move_cursor",
    "click_mouse",
    "scroll_mouse",
    
    # Information
    "get_time",
    "get_date",
    "get_weather",
    "get_system_info",
    
    # Browser (Yangi)
    "youtube_search",
    "youtube_comment",
    "google_search_click",
    
    # Camera & Screen (Yangi)
    "start_camera",
    "stop_camera",
    "start_screen_recording",
    "stop_screen_recording",
    "describe_screen",
    "posture_monitor",
    
    # Gesture Control (Yangi)
    "start_gesture_control",
    "stop_gesture_control",
    "start_sentinel",
    "stop_sentinel",
    
    # Typer Bot (Yangi)
    "start_typer_bot",
    "stop_typer_bot",
    "screenshot",
    
    # Financial Control (Yangi)
    "add_expense",
    "add_income",
    "get_finance_report",
    "get_balance",
    "start_research",
    "start_tutor",
    "tutor_respond",
    "detect_mood",
    "get_crypto_price",
    "get_stock_price",
    "local_query",
    "start_night_owl",
    "add_research_topic",
    "voice_authenticate",
    "get_level",
    "get_xp",
    "memorize_info",
    "recall_info",
    "check_errors",
    "control_lights",
    "control_speakers",
    "control_climate",
    "generate_dream",
    "type_text",
    "press_key",
    "generate_image",
    "generate_video",
    "scroll_down",
    "scroll_up",
    "learn_from_feedback",
    "connect_account",
    "open_run",
    "change_voice",
    "start_swarm",
    "swarm_scan",
    "swarm_list",
    "swarm_send",
    "start_widget",
    "remote_wake",
    "global_status",
    "visual_avatar",
    "encrypt_file",
    "decrypt_file",
    "secure_delete",
    "scan_bluetooth",
    "start_remote_bridge",
    "connect_device",
    "create_project",
    "analyze_codebase",
    "run_terminal_v2",
    "register_face",
    "get_battery_info",
    "kill_process",
    "volume_up",
    "volume_down",
    "mute_volume",
    "protocol",
    "schedule",
    "timer",
    "emergency",
    "confirm",
    "media_play_pause",
    "media_next",
    "media_previous",
    "get_schedule",
    "add_to_schedule",
    "reset_sentinel",
    
    "get_news_digest",
    "voice_clone_speak",
    "get_security_report",
    "desktop_automation",
    "smart_media_control",
    "advanced_schedule_manage",
    
    # Desktop Core Upgrades (Phase 5)
    "system_healer",
    "get_financial_update",
    "universal_search",
    "workspace_orchestrator",
    "toggle_gaming_mode",
    
    # God Mode Features (Elite v9.0)
    "access_vault",
    "store_vault",
    
    # Omni-Autonomy (Elite v10.0)
    "run_automation",
    
    # Advanced Neural Intelligence (Elite v11.0)
    "query_my_data",
    "organize_system",
    "perform_backup",

    
    # Adaptive Intelligence (Elite v13.0)
    "vision_click",
    "nuclear_protocol",
    "toggle_privacy_shield"
]


# Xavfli amallar (Tasdiqlash talab qilinadi)
DESTRUCTIVE_ACTIONS = [
    "shutdown", "restart", "delete_file", "format_disk", "kill_process", "self_destruct"
]

# O'zbek til pattern'lar
UZ_PATTERNS = {
    # System Control
    "shutdown": ["o'chir", "ochir", "yopil", "kompyuterni o'chir", "kompyuterni och"],
    "restart": ["qayta yoq", "qayta ishga tushir", "restart", "qaytadan yurgiz"],
    "sleep": ["uxlat", "uyqu rejim", "uyquga"],
    "lock_screen": ["qulfa", "ekranni qulfa", "qulfla"],
    
    # Application Control
    "open_app": ["och", "ochib ber", "ishga tushir", "yurgiz", "zapusk qil", "start ber"],
    "close_app": ["yop", "yopib ber", "tugatish", "o'chir", "to'xtat", "kill qil"],
    "focus_app": ["oldinga ol", "focus qil", "ekranga chiqar"],
    
    # Web Control
    "open_website": ["sayt och", "veb-sayt och", "ochib ber", "saytiga kir", "veb"],
    "search_google": ["google'da qidir", "qidiruv", "izla", "google dan qidir", "googleda qidir", "googledan qidir", "google'dan qidir", "internetdan qidir", "internetdan", "qidir"],
    "youtube_search": ["youtube'da qidir", "yotubeda qidir", "yutubda qidir", "youtube dan qidir", "yotubedan qidir", "yotubega kirib qidir"],
    
    # File System
    "create_folder": ["papka yarat", "folder yarat", "papka yaratish", "yangi papka"],
    "mute_volume": ["ovozni o'chir", "ovozni yoq", "bezovta qilinmasin"],
    "protocol": ["xayrli tong", "xayrli tun", "ish rejimi", "dam olish rejimi"],
    "schedule": ["har kuni soat", "har kuni", "rejalashtir"],
    "timer": ["daqiqadan keyin", "sekunddan keyin", "soatdan keyin", "taymer qo'y"],
    "generate_image": ["rasm chiz", "rasm yarat", "surat chiz"],
    "generate_video": ["video yarat", "video yasab"],
    
    # New Modules
    "perform_research": ["haqida surishtir", "tadqiqot qil", "o'rganib chiq", "haqida ma'lumot top", "tadqiqot", "research", "tahlil qil", "mavzuni o'rgan"],
    "add_expense": ["sarfladim", "ishlatdim", "sotib oldim", "to'ladim", "xarajat qildim"],
    "get_balance": ["balans", "qancha pulim bor", "hisobimda qancha", "pulim qolgan"],
    "get_financial_update": ["xarajatlarim", "qancha ishlatdim", "moliya hisoboti"],
    "toggle_gaming_mode": ["o'yin rejimi", "gaming mode", "fps oshir", "o'yin boshladim", "game mode"],
    "emergency": ["emergency", "favqulodda", "protokol nol", "stop all"],
    "pause_blackout": ["blackoutni to'xtatib tur", "o'chirishni kechiktir", "pauza qil", "blackoutni pauza qil", "to'xtatib tur"],
    "confirm": ["ha", "tasdiqlayman", "bajar", "yes", "shunday qil"],
    "delete_file": ["o'chir", "delete qil", "faylni o'chir"],
    "open_file": ["fayl och", "ochib ber"],
    "list_directory": ["ko'rsat", "ro'yxat", "nima bor"],
    
    # Input Control
    "type_text": ["yoz", "matn yoz"],
    "press_key": ["bos", "tugmani bos", "boss"],
    "press_hotkey": ["bos", "kombinatsiya bos"],
    "move_cursor": ["siljit", "kursorni siljit", "ko'chir"],
    "click_mouse": ["bos", "klik qil", "sichqonchani bos"],
    "scroll_mouse": ["aylantir", "scroll qil"],
    
    # Typer Bot
    "start_typer_bot": ["typer botni ishga tushir", "typing botni ishga tushir", "botni yoq", "yozib ber", "avto-yozish", "typer bol", "yozishni boshla", "o'rnimga yoz"],
    "stop_typer_bot": ["botni o'chir", "to'xtat", "yozishni to'xtat"],
    "start_sentinel": ["sentinel mode yoq", "xavfsizlikni yoq", "meni kuzat", "sentinel yoq", "sentinelni ishlat"],
    "stop_sentinel": ["sentinel mode o'chir", "sentinel o'chir", "sentinelni to'xtat"],
    "unlock_system": ["Sardorbek009", "parol Sardorbek009", "kod Sardorbek009", "Sardorbek 009", "Sardorbek nol nol to'qqiz", "Sardorbek nollar to'qqiz", "Sardorbek zero zero nine", "Sardorbek nol nol toqqiz", "Sardorbek"],
    
    # Information
    "get_time": ["soat necha", "vaqt", "hozir soat necha"],
    "get_date": ["bugun qaysi sana", "sana", "qaysi kun"],
    "get_weather": ["ob-havo", "havo qanday"],
    "get_system_info": ["tizim haqida", "kompyuter haqida", "info", "holat", "📊", "📊 holat"],
    
    # Research (Redundant but safe)
    "perform_research": ["tadqiqot", "research", "o'rganib chiq", "tahlil qil", "haqida ma'lumot top", "mavzuni o'rgan"],
    
    # Messaging
    "send_telegram_message": ["telegram", "telegramga", "telegramdan", "telegramm", "ga.*yoz", "ga.*xabar", "yozib\\s*yubor", "xabar\\s*yubor", "deb\\s*yoz"],
    
    # Google search (Yangi)
    "google_search_click": ["google qidir", "googleda qidir", "google'da qidirish", "googledan qidir", "google'dan qidir", "qidirib ber", "izlab ber", "qidir"],
    "search_google": ["googleda qidiruv", "qidir", "izlash"],
    
    # Camera & Screen
    "start_camera": ["kamera och", "kamerani yoq", "kamerani ishga tushir"],
    "stop_camera": ["kamerani yop", "kamerani o'chir"],
    "start_screen_recording": ["ekranni yoz", "ekran yozish", "screen record"],
    "stop_screen_recording": ["ekran yozishni to'xtat"],
    
    # Gesture Control
    "start_gesture_control": ["qol harakati", "gesture", "qol bilan boshqar"],
    "stop_gesture_control": ["gesture to'xtat"],
    
    # Write in App (Yangi)
    "write_in_app": ["notepadda", "bloknotda", "wordda", "da yoz"],
    
    # YouTube Actions
    "youtube_search": [
        "yutubdan qidir", "youtubedan qidir", "yutubdan izla", "video qidir", 
        "youtube dan qidir", "youtube da izla", "yutubda qidir", 
        "musiqa qo'y", "qo'shiq qo'y", "qushiq quy", "musiqa quy", 
        "qushiqni quy", "qo'shiqni qo'y", "eshitaylik", "aytishsin"
    ],
    "youtube_open": ["yutubni och", "youtubeni och", "videoni och", "youtubega kir"],
    
    # Connectivity
    "scan_bluetooth": ["bluetooth qidir", "qurilmalarni qidir", "blutusni yoq", "yaqin atrofdagi qurilmalar"],
    "start_remote_bridge": ["remote bridge yoq", "telefonni ula", "masofaviy boshqaruvni yoq"],
    "connect_device": ["qurilmaga ulan", "bog'lan", "ulan"],
    
    # Dev Mode
    "create_project": ["loyiha yarat", "proekt och", "pyton loyihasi"],
    "analyze_codebase": ["kodni tahlil qil", "xatolarni qidir", "kodni ko'rib chiq"],
    "run_terminal_v2": ["terminalda ishlat", "buyruqni bajar", "komandani yurgiz"],
    "register_face": ["yuzni ro'yxatga ol", "yuzimni tani", "yuzni skaner qil", "register face"],
    "media_play_pause": ["musiqani to'xtat", "musiqani qo'y", "play pause", "musiqani pauza qil"],
    "media_next": ["keyingi musiqa", "keyingisi", "next music"],
    "media_previous": ["oldingi musiqa", "oldingisi", "previous music"],
    
    # Learning
    "connect_account": ["hisobni ula", "bog'la", "akkauntni ula", "gmailni ula", "githubni ula", "ulash", "login qil"],
    "learn_from_feedback": ["bu xato", "aslida bunday", "eslab qol", "o'rganib ol", "noto'g'ri tushunding", "o'zgartir"],
    "get_schedule": ["rejalarimni ko'rsat", "bugun nima ishlarim bor", "rejani o'qi"],
    "add_to_schedule": ["rejaga qo'sh", "vazifa qo'sh", "yangi reja"],
    "reset_sentinel": ["men borman", "men shu yerdaman", "bor borman", "shu yerdaman", "shuyerdaman", "men bor"],
    "smart_search": ["faylni qidir", "topib ber", "qayerda joylashgan", "fayl topish", "qidirish"],
    "quit_jarvis": ["o'chir", "yopil", "uxla", "jarvisni uchir", "chiq", "tugatish", "quit jarvis"],
    
    # Advanced Features
    "get_news_digest": ["yangiliklar", "yangiliklarni o'qi", "dayjest", "bugun nima gap"],
    "voice_clone_speak": ["ovozida ayt", "ovozida gapir", "ovozini ishlat"],
    "smart_media_control": ["musiqa qo'y", "musiqa yangrasin", "nima eshitaylik", "kayfiyatga qarab musiqa"],
    "system_healer": ["tozala", "optimallashtir", "kompyuterni davola", "tizimni tekshir", "healer"],
    "get_financial_update": ["kripto", "bozor", "narxlar", "moliya", "bitcoin necha pul"],
    "universal_search": ["fayllardan qidir", "hujjatlardan top", "fayl ichidan qidir", "topib ber"],
    "workspace_orchestrator": ["ish vaqti", "ishni boshlaymiz", "ish muhiti", "hamma narsani och"],
    "toggle_gaming_mode": ["o'yin rejimi", "gaming mode", "fpsni ko'tar"],
    "perform_research": ["research", "tadqiqot", "ma'lumot yig'", "research assistant"],
    "get_security_report": ["xavfsizlik hisoboti", "tizim holati", "xavfsizlikni tekshir"],
    "desktop_automation": ["fayllarni tahlil qil", "excelni ko'r", "pdfdan matn", "rasmlarni o'zgartir"],
    "advanced_schedule_manage": ["eslatma qo'sh", "yangi reja qo'sh", "remaynder", "kun tartibi"],
    "access_vault": ["arxivni och", "maxfiy", "vaultni ko'rsat", "arxivga kir", "shadow archive"],
    "store_vault": ["arxivga saqlash", "saqla", "maxfiy joyga qo'y", "vaultga saqla"],
    "run_automation": ["avtomatlashtirma", "avtomatlashtir", "ish rejimini yoq", "makros", "macro"],
    "query_my_data": ["ma'lumotlarimdan qidir", "loyihalarim haqida", "arxivdan top", "hujjatlardan top", "rag qidiruv"],
    "organize_system": ["tizimni tartibla", "fayllarni sarala", "hubni yangila", "tartibga sol"],
    "perform_backup": ["zaxiralash", "backup qil", "arxivni zaxiralash", "loyihalarni saqla"],

    "vision_click": ["shuni bos", "topib bos", "ekrandan top", "vision click", "buni bos"],
    "nuclear_protocol": ["nuclear protocol", "to'liq tozalash", "maxfiy tozalash", "tizimni yangila"],
    "workspace_mode": ["ishchi rejim", "workspace", "muhitni tayyorla", "coding mode", "relax mode", "research mode"],
    "toggle_privacy_shield": ["maxfiy rejim", "ekranni yop", "privacy shield", "yashir", "qalqonni yoq"],
    
    # Social Mediation & Social Media (Phase 15)
    "resolve_conflict": ["yarashish kerak", "muammoni hal qil", "ziddiyatni yech", "bilan yarash", "bilan kelish"],
    "analyze_chat": ["chatni tahlil", "nima deb yozdi", "nima dedi", "unread messages"],
    "analyze_instagram": ["instagramda nima gap", "instagram tahlil", "lentada nima bor"],
    "post_instagram": ["instagramga qo'y", "instagramga post", "video yukla", "post qo'y"]
}


# Ingliz til pattern'lar
EN_PATTERNS = {
    # System Control
    "shutdown": ["shutdown", "turn off", "power off", "shut down"],
    "restart": ["restart", "reboot", "reset"],
    "sleep": ["sleep", "suspend", "hibernate"],
    "lock_screen": ["lock", "lock screen"],
    
    # Application Control
    "open_app": ["open", "launch", "start", "run"],
    "close_app": ["close", "quit", "exit", "kill"],
    "focus_app": ["focus", "switch to", "bring to front"],
    
    # Web Control
    "open_website": ["open site", "go to", "browse", "navigate to"],
    "search_google": ["google", "search", "search google", "google search"],
    "youtube_search": ["youtube search", "search on youtube", "search youtube"],
    
    # File System
    "create_folder": ["create folder", "make folder", "new folder", "mkdir"],
    "delete_file": ["delete", "remove", "delete file"],
    "open_file": ["open file", "open"],
    "list_directory": ["list", "show files", "dir", "ls"],
    
    # Input Control
    "type_text": ["type", "write", "input text"],
    "press_key": ["press", "hit", "press key"],
    "press_hotkey": ["press", "hotkey", "combination"],
    "move_cursor": ["move", "move cursor", "move mouse"],
    "click_mouse": ["click", "mouse click"],
    "scroll_mouse": ["scroll", "wheel"],
    
    # Information
    "get_time": ["time", "what time", "current time"],
    "get_date": ["date", "what date", "today"],
    "get_weather": ["weather", "forecast"],
    "get_system_info": ["system info", "info", "system"],
    
    # Messaging
    "send_telegram_message": ["send telegram", "telegram message", "message on telegram", "send via telegram"],
    
    # Write in App
    "write_in_app": ["write in", "type in", "type into"],
    
    # Advanced Features
    "get_news_digest": ["get news", "news digest", "today's news"],
    "voice_clone_speak": ["speak with voice", "clone voice", "speak as"],
    "get_security_report": ["security report", "system status", "check security"],
    "desktop_automation": ["process excel", "extract pdf", "convert images"],
    "smart_media_control": ["seek media", "download subtitles", "media control"],
    "advanced_schedule_manage": ["add reminder", "add routine", "schedule manage"]
}

# Rus til pattern'lar (Yangi)
RU_PATTERNS = {
    "shutdown": ["выключи компьютер", "выключи", "выключить", "завершение работы"],
    "restart": ["перезагрузи", "перезагрузить", "рестарт"],
    "sleep": ["сон", "режим сна", "спать"],
    "lock_screen": ["заблокируй", "заблокировать экран"],
    "open_app": ["открой", "запусти", "открыть"],
    "close_app": ["закрой", "останови", "закрыть"],
    "open_website": ["открой сайт", "перейди на"],
    "search_google": ["гугл", "найди в гугле", "поиск"],
    "get_time": ["время", "сколько времени", "который час"],
    "get_date": ["дата", "какое сегодня число"],
    "write_in_app": ["напиши в", "в блокноте", "в ворде"],
}

# Ilovalar yo'llari
APP_PATHS = {
    # Browsers
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",

    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

    
    # Editors & IDEs
    "notepad": r"C:\Windows\System32\notepad.exe",
    "vscode": r"C:\Users\user\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "pycharm": r"C:\Program Files\JetBrains\PyCharm\bin\pycharm64.exe",
    "sublime": r"C:\Program Files\Sublime Text\sublime_text.exe",
    

    
    # Video & Media
    "capcut": r"C:\Users\user\AppData\Local\CapCut\CapCut.exe",
    "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "aimp": r"C:\Program Files (x86)\AIMP\AIMP.exe",
    "spotify": r"C:\Users\user\AppData\Roaming\Spotify\Spotify.exe",
    
    # Communication
    "telegram": r"C:\Users\user\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "discord": r"C:\Users\user\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "slack": r"C:\Users\user\AppData\Local\slack\slack.exe",
    "zoom": r"C:\Program Files\Zoom\bin\Zoom.exe",
    
    # Office & Productivity
    "word": r"C:\Program Files\Microsoft Office\Root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\Root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\Root\Office16\POWERPNT.EXE",

    

    

    
    # Utilities
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
}

# Mashhur veb-saytlar
POPULAR_WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com",
    "gmail": "https://mail.google.com",
}

# PyAutoGUI sozlamalari
PYAUTOGUI_SETTINGS = {
    "PAUSE": 0.5,  # Har bir operatsiyadan keyin kutish vaqti (sekundlarda)
    "FAILSAFE": True,  # Cursor chap yuqori burchakka ketsa to'xtaydi
}

# Logging sozlamalari
LOG_CONFIG = {
    "log_dir": "logs",
    "log_file": "agent.log",
    "log_level": "INFO",
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5,
}

# Tizim sozlamalari
SYSTEM_NAME = "JARVIS"
USER_NAME = "Sardor"
AVATAR_ENABLED = True

# Xavfsizlik sozlamalari
SECURITY_SETTINGS = {
    "require_confirmation": True,  # Destructive operatsiyalar uchun tasdiqlash
    "test_mode": False,  # Test rejimida destructive operatsiyalar simulate qilinadi
    "max_file_size_delete": 104857600,  # Max 100MB fayl o'chirish mumkin
}

# Sentinel Mode (Auto-Lock) Settings
SENTINEL_MODE = {
    "enabled": True,           # On/off
    "use_virtual_lock": True,   # JARVIS UI lock (allows voice/vision monitoring)
    "timeout": 300.0,           # Seconds before lock (5 minutes)
    "warn_at": 15.0,            # Warn user 15 seconds before lock
    "last_warn_time": 0,
    "last_activity": 0,         # Tracks face/keyboard activity
    "is_locked": False,         # Current lock status
    "should_unlock": False      # Voice unlock trigger
}

# Blackout Settings
BLACKOUT_SETTINGS = {
    "start_time": "17:00",
    "end_time": "19:00",
    "enabled": True,
    "paused_until": 1771588382  # Paused for 24 hours
}

# Cloud Settings
CLOUD_SERVER_URL = "https://jarvisai-cortex.onrender.com"
HYBRID_MODE = False # User requested full local power

# Ovoz sozlamalari (Voice Settings)
VOICE_SETTINGS = {
    "language": "uz-UZ",           # Asosiy til (O'zbek)
    "fallback_language": "en-US",  # Zaxira til (Ingliz)
    "speech_rate": 160,            # Ovoz tezligi (Professional JARVIS tone)
    "volume": 1.0,                 # Ovoz balandligi (0.0 - 1.0)
    "enable_tts": True,            # Text-to-Speech yoqish
    "enable_stt": True,            # Speech-to-Text yoqish
    "listen_timeout": 5,           # Ovoz kutish vaqti (sekund)
    "phrase_time_limit": 10,       # Maksimal gapirish vaqti (sekund)
}
# Gesture Control Settings
GESTURE_SETTINGS = {
    "enabled": True,           # Default state
    "persistent": True,        # Keep running in background/minimize
    "smoothing": 7
}

# GUI State
GUI_SETTINGS = {
    "minimized": False,
    "lite_mode": True # Enabled for stability
}

# Connectivity Settings
CONNECTIVITY_SETTINGS = {
    "remote_port": 5000,
    "bt_timeout": 5.0,
    "authorized_ips": ["127.0.0.1"]
}

# Face ID Settings
FACE_ID_SETTINGS = {
    "enabled": True,
    "confidence_threshold": 65,
    "registration_complete": False
}

# Wake word (uyg'otish so'zi)
WAKE_WORDS = ["jarvis", "джарвис", "жарвис", "эй жарвис"]

# Telegram Bot Settings
TELEGRAM_SETTINGS = {
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "enabled": True
}

# Telegram User Assistant (Phase 61) Settings
# Sign up at https://my.telegram.org to get api_id and api_hash
TELEGRAM_USER_SETTINGS = {
    "api_id": int(os.getenv("TELEGRAM_USER_API_ID", "0")), 
    "api_hash": os.getenv("TELEGRAM_USER_API_HASH", ""),
    "phone_number": os.getenv("TELEGRAM_USER_PHONE", ""),
    "enabled": False, # Disabled due to invalid API hash error
    "auto_reply": False,
    "session_name": "jarvis_user_session"
}

# Web Gateway Sozlamalari
WEB_SETTINGS = {
    "host": "0.0.0.0",
    "port": 5000,
    "password": "jarvis_access", # Remote kirish paroli
    "secret_key": "super_secret_jarvis_key_2026", # Session uchun
    "session_timeout": 3600 # 1 soat
}


# Chiqish buyruqlari
EXIT_COMMANDS = ["exit", "quit", "chiq", "q", "stop", "стоп", "выход"]

