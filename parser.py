"""
Windows Boshqaruv Agenti - Parser
Natural language parser for Uzbek and English commands
"""

import re
import os
from config import UZ_PATTERNS, EN_PATTERNS, POPULAR_WEBSITES, APP_PATHS
from utils import setup_logger, normalize_text, extract_app_name, extract_website_url


class CommandParser:
    """
    Tabiiy tilni JSON buyruqqa o'giradigan klass
    """
    
    def __init__(self):
        self.logger = setup_logger("CommandParser")
        self.logger.info("CommandParser initialized")
    
    def parse(self, text):
        """
        Tabiiy til buyrug'ini JSON formatga o'girish
        """
        if not text:
            return {"action": "unknown", "parameters": {}}
        
        self.logger.info(f"Parsing command: {text}")
        normalized_text = text.lower().strip()
        
        # Intent'ni aniqlash
        action, confidence = self._detect_action(normalized_text)
        
        if action == "unknown":
            return {"action": "unknown", "parameters": {}}
        
        # Parametrlarni extract qilish
        parameters = self._extract_parameters(action, normalized_text, text)
        
        return {"action": action, "parameters": parameters}

    def _detect_action(self, text):
        """Buyruqdan action'ni aniqlash"""
        best_action = "unknown"
        best_score = 0
        
        # O'zbek pattern'larni tekshirish - Regex support
        for action, patterns in UZ_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    score = len(pattern)
                    if score > best_score:
                        best_score = score
                        best_action = action
        
        # Ingliz pattern'lar
        for action, patterns in EN_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    score = len(pattern)
                    if score > best_score:
                        best_score = score
                        best_action = action
                        
        if best_action == "unknown":
            print(f"🔍 [DEBUG] RAW: '{text}' action not detected.")
        else:
            print(f"🔍 [DEBUG] DETECTED: {best_action} (Score: {best_score})")
                        
        return best_action, best_score

    def _extract_parameters(self, action, text, original_text=""):
        """Parametrlarni ajratib olish"""
        params = {}
        text_lower = (original_text if original_text else text).lower()

        # Phase 15: Social Mediation & Instagram
        if action in ["resolve_conflict", "analyze_chat"]:
            params["target"] = self._extract_target_name(text)
            return params
        
        elif action == "post_instagram":
            params["file_path"] = self._extract_file_path(text)
            params["caption"] = self._extract_typed_text(text) or "Shared via JARVIS AI"
            return params

        # v17: Music, Crypto, Stock, Weather
        elif action == "play_music":
            params["song"] = self._extract_song_name(text)
            return params
        elif action == "crypto_price":
            params["symbol"] = self._extract_crypto_symbol(text)
            return params
        elif action == "stock_price":
            params["symbol"] = self._extract_stock_symbol(text)
            return params
        elif action == "weather_check":
            params["city"] = self._extract_city_name(text)
            return params

        # Original Extraction Logic
        if action in ["open_app", "close_app"]:
            params["app_name"] = self._extract_app_name(text)
        
        elif action == "focus_app":
            params["app_name"] = self._extract_app_name(text)
        
        elif action == "open_website":
            url = extract_website_url(text)
            params["url"] = url if url else self._extract_url_from_text(text)
        
        elif action in ["search_google", "google_search_click", "youtube_search"]:
            params["query"] = self._extract_search_query(text)
        
        elif action == "send_telegram_message":
            contact, message = self._extract_telegram_params(text)
            params["contact"] = contact
            params["message"] = message
            
        elif action == "type_text":
            params["text"] = self._extract_typed_text(text)
            
        elif action == "press_key":
            params["key"] = self._extract_key(text)
            
        elif action == "create_folder":
            params["folder_name"] = self._extract_folder_name(text)
            
        elif action in ["delete_file", "open_file"]:
            params["file_path"] = self._extract_file_path(text)
            
        elif action == "start_screen_recording":
            params["duration"] = self._extract_duration(text)

        elif action == "protocol":
            if any(w in text for w in ["tong", "morning"]): params["name"] = "good_morning"
            elif any(w in text for w in ["tun", "night"]): params["name"] = "good_night"
            elif any(w in text for w in ["ish", "work"]): params["name"] = "work_mode"
            
        elif action == "schedule":
            params["time"] = self._extract_time(text)
            params["sub_action"] = self._extract_automation_action(text, ["soat", "da"])
            
        elif action == "timer":
            params["minutes"] = self._extract_duration(text)
            params["sub_action"] = self._extract_automation_action(text, ["daqiqadan keyin", "sekunddan keyin", "soatdan keyin"])

        elif action in ["generate_image", "generate_video"]:
            params["prompt"] = self._extract_media_prompt(text)

        elif action == "perform_research":
            params["topic"] = self._extract_research_topic(text)
            
        elif action == "add_expense":
            amt, desc = self._extract_amount_desc(text)
            params["amount"] = amt
            params["description"] = desc

        elif action == "connect_account":
             params["platform"] = self._extract_platform_name(text)

        elif action == "learn_from_feedback":
             params["feedback"] = text

        return params

    # --- HELPER METHODS ---

    def _extract_target_name(self, text):
        """Target contact nomini aniqlash"""
        keywords = ["bilan", "with", "haqida", "nima dedi", "nima yozdi", "yarash", "hal qil"]
        clean = text
        for k in keywords:
            clean = clean.replace(k, "")
        actions = ["yarashish kerak", "muammoni", "ziddiyatni", "chatni tahlil", "ko'rchi", "tekshir"]
        for a in actions:
            clean = clean.replace(a, "")
        return clean.strip().title()

    def _extract_app_name(self, text):
        """Ilova nomini extract qilish"""
        text_lower = text.lower()
        text_normalized = text_lower.replace(" ", "_")
        for app in APP_PATHS.keys():
            if app in text_normalized or app.replace("_", " ") in text_lower:
                return app
        return "notepad"

    def _extract_url_from_text(self, text):
        """URL extract qilish"""
        patterns = ["och", "sayt och", "open", "open site", "veb-sayt"]
        for pattern in patterns:
            text = text.replace(pattern, "").strip()
        return text if text else "https://www.google.com"

    def _extract_search_query(self, text):
        """Qidiruv so'rovini extract qilish"""
        query = text.lower().strip()
        patterns = [
            "google'dan", "google dan", "googledan", "google'da", "google da", "googleda",
            "youtube'dan", "youtube dan", "youtubedan", "youtube'da", "youtube da", "youtubeda",
            "musiqa qo'y", "qo'shiq qo'y", "top", "qidiruv", "qidir", "search", "google", "youtube"
        ]
        for pattern in patterns:
            query = query.replace(pattern, "").strip()
        return query if query else "python"

    def _extract_folder_name(self, text):
        patterns = ["papka yarat", "folder yarat", "create folder", "mkdir"]
        for pattern in patterns:
            text = text.replace(pattern, "").strip()
        return text if text else "new_folder"

    def _extract_file_path(self, text):
        path_pattern = r'[a-zA-Z]:\\[^\\s]+'
        match = re.search(path_pattern, text)
        return match.group() if match else None

    def _extract_typed_text(self, text):
        patterns = [r"yoz[ib\s]*[ber\s]*(.+)", r"type\s+(.+)", r"write\s+(.+)", r"aytsin\s+(.+)"]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return text

    def _extract_key(self, text):
        key_map = {"enter": "enter", "probel": "space", "space": "space", "backspace": "backspace"}
        for k, v in key_map.items():
            if k in text: return v
        return "enter"

    def _extract_telegram_params(self, text):
        # Support both "shahboz ga yoz" and "shahbozga yoz"
        if "ga " in text:
            parts = text.split("ga ", 1)
        elif "ga" in text:
            parts = text.split("ga", 1)
        else:
            return "Unknown", text
            
        contact = parts[0].replace("telegram", "").strip().title()
        raw_msg = parts[1].strip()
        
        # If user just said "ga yoz", provide default
        if raw_msg.lower() == "yoz" or not raw_msg:
             message = "Salom, janob siz bilan bog'lanmoqchi."
        else:
             message = raw_msg.replace("deb yoz", "").replace("yoz", "").strip()
             if not message: message = raw_msg # Fallback
             
        return contact, message

    def _extract_time(self, text):
        match = re.search(r'(\d{1,2})[:\s-](\d{2})', text)
        return f"{int(match.group(1)):02d}:{int(match.group(2)):02d}" if match else "09:00"

    def _extract_duration(self, text):
        nums = re.findall(r'\d+', text)
        if nums:
            val = int(nums[0])
            if "soat" in text or "hour" in text: return val * 60
            return val
        return 1

    def _extract_automation_action(self, text, keywords):
        clean = text
        for k in keywords:
            if k in clean: clean = clean.split(k)[-1].strip()
        return clean

    def _extract_song_name(self, text):
        keywords = ["musiqa quyib ber", "qo'shiq qo'y", "play music", "musiqa", "qo'shiq"]
        clean = text.lower()
        for k in keywords: clean = clean.replace(k, "")
        return clean.replace("iltimos", "").replace("jarvis", "").strip() or "Best songs 2026"

    def _extract_crypto_symbol(self, text):
        mapping = {"bitcoin": "bitcoin", "bitkoin": "bitcoin", "btc": "bitcoin", "ethereum": "ethereum", "eth": "ethereum"}
        for k, v in mapping.items():
            if k in text.lower(): return v
        return "bitcoin"

    def _extract_stock_symbol(self, text):
        mapping = {"apple": "AAPL", "tesla": "TSLA", "google": "GOOGL"}
        for k, v in mapping.items():
            if k in text.lower(): return v
        return "AAPL"

    def _extract_city_name(self, text):
        text = text.lower().replace("ob-havo", "").replace("weather", "").strip()
        return text if text else "Tashkent"

    def _extract_number(self, text):
        """Matndan raqamni ajratib olish (default: 50)"""
        import re
        nums = re.findall(r'\d+', text)
        if nums:
            return int(nums[0])
        
        # Word mapping fallback
        mapping = {"yarim": 50, "to'liq": 100, "o'chir": 0, "yoq": 100, "o'rtacha": 50, "sal": 30}
        for k, v in mapping.items():
            if k in text.lower(): return v
        return 50

    def _extract_media_prompt(self, text):
        keywords = ["rasm chiz", "rasm yarat", "video yarat", "video yasab", "imagine", "generate", "create image", "haqida video", "chizib"]
        clean = text.lower()
        for k in keywords: clean = clean.replace(k, "")
        return clean.strip() or "future city cyberpunk"

    def _extract_platform_name(self, text):
        platforms = ["google", "telegram", "github", "twitter", "facebook", "instagram", "linkedin"]
        for p in platforms:
            if p in text.lower(): return p
        return "general"

    def _extract_research_topic(self, text):
        keywords = ["haqida surishtir", "tadqiqot qil", "o'rganib chiq", "haqida ma'lumot top", "research", "study"]
        clean = text
        for k in keywords: clean = clean.replace(k, "")
        return clean.strip() or "AI trends 2026"

    def _extract_amount_desc(self, text):
        # "tushlikka 50000 so'm sarfladim" -> (50000, "tushlikka")
        import re
        nums = re.findall(r'\d+', text.replace(" ", ""))
        amount = int(nums[0]) if nums else 0
        desc = text.replace(str(amount), "").replace("so'm", "").replace("sarfladim", "").replace("sarf", "").replace("qildim", "").strip()
        return amount, desc
