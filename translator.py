"""
JARVIS - Multi-language Processor Engine (Elite Edition)
Handles translation, normalization and professional response mapping.
"""

from utils import setup_logger
from datetime import datetime
import random

class LanguageProcessor:
    def __init__(self):
        self.logger = setup_logger("LanguageProcessor")
        self.supported_languages = ["uz"] # STRICT UZBEK MODE
        
        # Elite Response Database
        self.responses = {
            "uz": {
                "greetings": {
                    "morning": ["Xayrli tong, {user}. Kuningiz unumli o'tsin.", "Xayrli tong. Barcha tizimlar tayyor holatda.", "Salom, {user}. Ishni boshlaymizmi?"],
                    "afternoon": ["Xayrli kun, {user}. Qanday yordam bera olaman?", "Salom, {user}. Tizimlar ideal holatda.", "Xayrli kun. Buyruqlaringizni kutaman."],
                    "evening": ["Xayrli kech, {user}. Dam olish vaqti kelmadimi?", "Xayrli kech. Bugun ancha samarali mehnat qildingiz.", "Salom, {user}. Kechki xizmatga tayyorman."],
                    "night": ["Xayrli tun, {user}. Tizim kutish rejimiga o'tkazilmoqda.", "Xayrli tun. Yaxshi dam oling.", "Salom, {user}. Tungi navbatchilik boshlandi."]
                },
                "actions": {
                    "open_app": ["Janob, bajarildi.", "Janob, ilova ochildi.", "Bajarildi, Janob."],
                    "close_app": ["Janob, bajarildi.", "Yopildi, Janob."],
                    "open_website": ["Janob, bajarildi.", "Sayt ochildi, Janob."],
                    "search_google": ["Janob, qidiruv bajarildi."],
                    "get_time": ["Hozir soat {res}, Janob."],
                    "get_date": ["Bugun {res}, Janob."],
                    "create_folder": ["Janob, bajarildi.", "Papka yaratildi, Janob."],
                    "delete_file": ["Janob, bajarildi.", "Fayl o'chirildi, Janob."],
                    "send_telegram_message": ["Janob, xabar yuborildi."],
                    "write_in_app": ["Janob, bajarildi.", "Yozildi, Janob."],
                    "schedule": ["Janob, rejalashtirildi."],
                    "timer": ["Janob, taymer o'rnatildi."],
                    "protocol": ["Janob, protokol ishga tushdi."],
                    "youtube_search": ["Janob, bajarildi."],
                    "youtube_comment": ["Janob, izoh qoldirildi."],
                    "google_search_click": ["Janob, bajarildi."],
                    "start_camera": ["Janob, kamera yoqildi."],
                    "analyze_chat": ["{res}"],
                    "social_report": ["{res}"],
                    "stop_camera": ["Janob, kamera o'chirildi."],
                    "start_screen_recording": ["Janob, yozish boshlandi."],
                    "stop_screen_recording": ["Janob, yozish to'xtatildi."],
                    "start_gesture_control": ["Janob, Gesture Control yoqildi."],
                    "stop_gesture_control": ["Janob, Gesture Control o'chirildi."],
                    "start_typer_bot": ["Janob, Typer Bot ishga tushdi. Ekranda matn tanlang."],
                    "stop_typer_bot": ["Janob, Typer Bot to'xtatildi."],
                    "security_denied": ["Kechirasiz {user}, xavfsizlik protokoli tufayli bu amal taqiqlandi.", "Vakolatingiz yetarli emas, {user}.", "Kirish rad etildi."],
                    "request_confirmation": ["Ushbu amalni bajarishni tasdiqlaysizmi, {user}?", "Bu xavfli bo'lishi mumkin. Tasdiqlaysizmi?", "Ruxsat berasizmi, {user}?"],
                    "emergency": ["Emergency protokol faollashtirildi. Xavfsizligingiz ta'minlandi.", "Tizim bloklandi. Protokol nol ishga tushdi.", "Favqulodda to'xtatish bajarildi."],
                    "error": ["Xatolik yuz berdi: {error_message}.", "Kechirasiz {user}, texnik xatolik: {error_message}."],
                    "unknown": ["Kechirasiz {user}, buyrug'ingizni tushuna olmadim. Iltimos, aniqroq buyruq bering.", "Buyruq tushunarsiz, {user}. Qayta urinib ko'ring."]
                }
            },
            "en": {
                "greetings": {
                    "morning": ["Good morning, {user}. Wish you a productive day.", "Good morning. All systems are go.", "Hello, {user}. Ready to start?"],
                    "afternoon": ["Good afternoon, {user}. How can I assist?", "Hello, {user}. Systems are nominal.", "Good afternoon. Waiting for your orders."],
                    "evening": ["Good evening, {user}. Isn't it time to rest?", "Good evening. You've done a lot today.", "Hello, {user}. Ready for evening duty."],
                    "night": ["Good night, {user}. Systems on standby.", "Good night. Have a good rest.", "Hello, {user}. Night watch initiated."]
                },
                "actions": {
                    "open_app": ["{app} opened successfully, {user}.", "{app} is running. Ready to serve.", "{app} is ready, {user}."],
                    "close_app": ["{app} closed, {user}.", "{app} process terminated.", "App closed, {user}."],
                    "open_website": ["Navigated to {site}, {user}.", "{site} loaded. Here you go.", "Website is ready, {user}."],
                    "search_google": ["Searching Google for {query}, {user}."],
                    "get_time": ["It's {res}, {user}.", "Local time is {res}.", "The time is {res}, {user}."],
                    "get_date": ["Today is {res}, {user}."],
                    "security_denied": ["I'm sorry {user}, but security protocols deny this action.", "Insufficient permissions, {user}.", "Access denied."],
                    "request_confirmation": ["Do you confirm this action, {user}?", "This might be dangerous. Confirm?", "Authorize this action, {user}?"],
                    "emergency": ["Emergency protocol activated. Security ensured.", "Systems locked. Protocol zero engaged.", "Emergency stop executed."],
                    "error": ["An error occurred: {error_message}.", "Sorry {user}, technical error: {error_message}."],
                    "unknown": ["I'm sorry {user}, I didn't get that. Could you please rephrase?", "Command not recognized, {user}."]
                }
            },
            "ru": {
                "greetings": {
                    "morning": ["Доброе утро, {user}. Удачного дня.", "Доброе утро. Все системы в норме.", "Здравствуйте, {user}. Приступим?"],
                    "afternoon": ["Добрый день, {user}. Чем могу помочь?", "Здравствуйте. Системы работают штатно.", "Добрый день. Жду ваших указаний."],
                    "evening": ["Добрый вечер, {user}. Не пора ли отдохнуть?", "Добрый вечер. Вы сегодня много поработали.", "Здравствуйте. К вечерней смене готов."],
                    "night": ["Доброй ночи, {user}. Системы в режиме ожидания.", "Доброй ночи. Приятного отдыха.", "Здравствуйте. Ночной дозор начат."]
                },
                "actions": {
                    "open_app": ["{app} успешно открыто, {user}.", "{app} запущено. К службе готов.", "{app} готово, {user}."],
                    "close_app": ["{app} закрыто, {user}.", "Процесс {app} завершен.", "Приложение закрыто, {user}."],
                    "open_website": ["Перешел на {site}, {user}.", "{site} загружен. Пожалуйста.", "Сайт готов, {user}."],
                    "get_time": ["Сейчас {res}, {user}.", "Местное время: {res}.", "Время {res}, {user}."],
                    "security_denied": ["Простите, {user}, протоколы безопасности запрещают это действие.", "Недостаточно прав, {user}.", "Доступ запрещен."],
                    "request_confirmation": ["Вы подтверждаете это действие, {user}?", "Это может быть опасно. Подтверждаете?", "Разрешаете выполнение, {user}?"],
                    "emergency": ["Аварийный протокол активирован. Безопасность обеспечена.", "Системы заблокированы. Протокол ноль.", "Экстренная остановка выполнена."],
                    "error": ["Произошла ошибка: {error_message}.", "Извините {user}, техническая ошибка: {error_message}."],
                    "unknown": ["Извините {user}, я вас не понял. Повторите команду точнее.", "Команда не распознана, {user}."]
                }
            }
        }

    def detect_language(self, text):
        uz_words = ["och", "yop", "qidir", "yarat", "yoz", "soat", "necha", "bugun", "boshla", "to'xtat"]
        ru_words = ["открой", "закрой", "поиск", "создай", "время", "дата", "начни", "стоп"]
        en_words = ["open", "close", "search", "create", "time", "date", "start", "stop"]
        text_lower = text.lower()
        uz_count = sum(1 for w in uz_words if w in text_lower)
        ru_count = sum(1 for w in ru_words if w in text_lower)
        en_count = sum(1 for w in en_words if w in text_lower)
        if uz_count >= max(ru_count, en_count) and uz_count > 0: return "uz"
        elif ru_count > en_count and ru_count > 0: return "ru"
        elif en_count > 0: return "en"
        return "uz"

    def get_greeting(self, lang="uz", user_name="Janob"):
        hour = datetime.now().hour
        if 5 <= hour < 12: key = "morning"
        elif 12 <= hour < 18: key = "afternoon"
        elif 18 <= hour < 22: key = "evening"
        else: key = "night"
        
        greeting = random.choice(self.responses.get(lang, self.responses["uz"])["greetings"][key])
        return greeting.format(user=user_name)

    def get_action_response(self, action, status, lang="uz", user_name="Janob", **kwargs):
        if status != "success" and action not in ["security_denied", "request_confirmation", "error", "unknown"]:
            return f"Error encountered, {user_name}." if lang=="en" else f"Xatolik, {user_name}."
            
        lang_data = self.responses.get(lang, self.responses["uz"])
        templates = lang_data["actions"].get(action, ["Command executed, {user}."])
        template = random.choice(templates)
        
        # Default keys for formatting if not provided
        format_args = {
            "app": kwargs.get("app_name", "App"),
            "site": kwargs.get("url", "Website"),
            "res": str(kwargs.get("result", "")),
            "user": user_name,
            "query": kwargs.get("query", ""),
            "error_message": kwargs.get("error_message", "")
        }
        # Update with any other passed kwargs
        format_args.update(kwargs)
        
        try:
            response = template.format(**format_args)
        except KeyError:
            # Fallback if some placeholder is missing
            response = template
        
        # Manual replace for legacy templates or cases where .format didn't catch {user}
        if "{user}" in response:
            response = response.replace("{user}", user_name)
        
        return response

if __name__ == "__main__":
    lp = LanguageProcessor()
    print(lp.get_greeting("uz", "Sardor"))
    print(lp.get_action_response("open_app", "success", "uz", user_name="Sardor", app_name="Chrome"))
