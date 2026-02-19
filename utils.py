"""
Windows Boshqaruv Agenti - Yordamchi Funksiyalar
Utility functions and helpers for the Windows Control Agent
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from config import LOG_CONFIG, SECURITY_SETTINGS, DESTRUCTIVE_ACTIONS


def setup_logger(name="WindowsAgent"):
    """
    Logger sozlash
    """
    # Logs papkasini yaratish
    log_dir = LOG_CONFIG["log_dir"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, LOG_CONFIG["log_file"])
    
    # Logger yaratish
    logger = logging.getLogger(name)
    logger.setLevel(LOG_CONFIG["log_level"])
    
    # File handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_CONFIG["max_bytes"],
        backupCount=LOG_CONFIG["backup_count"]
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Handlerlarni qo'shish
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


def validate_json_command(command):
    """
    JSON buyruqni tekshirish
    
    Args:
        command (dict): JSON buyruq
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(command, dict):
        return False, "Command must be a dictionary"
    
    if "action" not in command:
        return False, "Missing 'action' field"
    
    if "parameters" not in command:
        return False, "Missing 'parameters' field"
    
    if not isinstance(command["parameters"], dict):
        return False, "'parameters' must be a dictionary"
    
    return True, None


def is_destructive_action(action):
    """
    Action destructive ekanligini tekshirish
    
    Args:
        action (str): Action nomi
        
    Returns:
        bool: Destructive bo'lsa True
    """
    return action in DESTRUCTIVE_ACTIONS


def confirm_action(action, parameters):
    """
    Destructive action uchun tasdiqlash so'rash
    
    Args:
        action (str): Action nomi
        parameters (dict): Action parametrlari
        
    Returns:
        bool: Tasdiqlangan bo'lsa True
    """
    if not SECURITY_SETTINGS["require_confirmation"]:
        return True
    
    if SECURITY_SETTINGS["test_mode"]:
        print(f"[TEST MODE] Would execute: {action} with {parameters}")
        return False
    
    print(f"\n⚠️  WARNING: You are about to execute a destructive action!")
    print(f"Action: {action}")
    print(f"Parameters: {parameters}")
    
    response = input("Are you sure? (yes/no): ").strip().lower()
    return response in ["yes", "y", "ha", "h"]


def get_current_time():
    """
    Hozirgi vaqtni qaytarish
    
    Returns:
        str: Vaqt (HH:MM:SS format)
    """
    return datetime.now().strftime("%H:%M:%S")


def get_current_date():
    """
    Hozirgi sanani qaytarish
    
    Returns:
        str: Sana (YYYY-MM-DD format)
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_full_datetime():
    """
    To'liq sana va vaqtni qaytarish
    
    Returns:
        str: Sana va vaqt
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_text(text):
    """
    Matnni normallash (kichik harflar, probellarsiz)
    
    Args:
        text (str): Asl matn
        
    Returns:
        str: Normallashtirilgan matn
    """
    if not text:
        return ""
    
    # Kichik harflarga o'tkazish
    text = text.lower().strip()
    
    # O'zbek harflarini normalize qilish
    replacements = {
        "o'": "o'",
        "g'": "g'",
        # Eski yozuv uchun
        "oʻ": "o'",
        "gʻ": "g'",
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def extract_app_name(text):
    """
    Matndan ilova nomini ajratib olish
    
    Args:
        text (str): Buyruq matni
        
    Returns:
        str: Ilova nomi yoki None
    """
    text = normalize_text(text)
    
    # Umumiy pattern'lar
    patterns = [
        # O'zbek: "chrome och", "notepad ni yop"
        ("och", ""),
        ("yop", ""),
        ("ishga tushir", ""),
        ("ni", ""),
        
        # Ingliz: "open chrome", "close notepad"
        ("open", ""),
        ("close", ""),
        ("launch", ""),
        ("start", ""),
    ]
    
    for pattern, _ in patterns:
        text = text.replace(pattern, "").strip()
    
    return text if text else None


def extract_website_url(text):
    """
    Matndan veb-sayt URL'ini ajratib olish
    
    Args:
        text (str): Buyruq matni
        
    Returns:
        str: URL yoki None
    """
    from config import POPULAR_WEBSITES
    
    text = normalize_text(text)
    
    # Agar to'g'ri URL bo'lsa
    if text.startswith("http://") or text.startswith("https://"):
        return text
    
    # Mashhur saytlar
    for site_name, url in POPULAR_WEBSITES.items():
        if site_name in text:
            return url
    
    # Agar faqat domen bo'lsa
    words = text.split()
    for word in words:
        if "." in word and len(word) > 3:
            if not word.startswith("http"):
                return f"https://{word}"
            return word
    
    return None


def format_success_response(action, result):
    """
    Muvaffaqiyatli javobni formatlash
    
    Args:
        action (str): Action nomi
        result: Natija
        
    Returns:
        dict: Formatlangan javob
    """
    return {
        "status": "success",
        "action": action,
        "result": result,
        "timestamp": get_full_datetime()
    }


def format_error_response(action, error):
    """
    Xatolik javobini formatlash
    
    Args:
        action (str): Action nomi
        error: Xatolik
        
    Returns:
        dict: Formatlangan javob
    """
    return {
        "status": "error",
        "action": action,
        "error": str(error),
        "timestamp": get_full_datetime()
    }
