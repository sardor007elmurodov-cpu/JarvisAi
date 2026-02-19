"""
JARVIS - Social Sentience Engine (Phase 15 - Elite v18.0)
Telegram va Instagram orqali avtonom ijtimoiy aloqalarni boshqarish.
Vazifalari:
- Ijtimoiy mojaro va nizolarni avtomatik aniqlash va hal qilish (Mediator).
- Telegram Userbot (shaxsiy profil nomidan yozish).
- Spam va keraksiz chatlarni tahlil qilish.
"""

import os
import json
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
from telethon.errors import SessionPasswordNeededError
from config import GEMINI_API_KEY, AI_MODEL_NAME
import google.generativeai as genai

# --- CONFIG ---
# Foydalanuvchi o'z API ID va Hash'larini kiritishi kerak (my.telegram.org)
API_ID = 36952810  # User Provided
API_HASH = "a80a7d6473da8d0be8b026981d6d9f2a" # User Provided
PHONE_NUMBER = "+998880451129" # Corrected phone number

# Social Mediation Settings
MEDIATION_ENABLED = True
TARGET_CONTACTS = ["Shahboz", "Unknownshahboz", "Boss"] # Kim bilan yarashish kerak
AUTO_REPLY_MODE = False # Avto-javob
MOOD_TRACKER = {}
HUD_CALLBACKS = [] # Elite v18.5 - Callbacks for HUD UI

# Setup Logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger("SocialSentience")

# Setup Gemini/GenAI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(AI_MODEL_NAME)

client = TelegramClient('jarvis_user_session', API_ID, API_HASH)
GLOBAL_LOOP = None # Elite v18.5 - Shared loop for thread-safe calls

async def analyze_sentiment(text):
    """Xabar mazmunini AI orqali tahlil qilish"""
    try:
        prompt = f"""
        Analyze this Telegram message for sentiment and intent.
        Message: "{text}"
        
        Is it Aggressive, Sad, Neutral, or Happy?
        Is it a conflict that needs resolution? (Yes/No)
        
        Return JSON: {{ "sentiment": "...", "conflict": true/false, "summary": "..." }}
        """
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return {"sentiment": "Neutral", "conflict": False, "summary": "Nomalum"}

async def generate_reply(history, style="Apologetic"):
    """Mojaroni hal qilish uchun javob generatsiya qilish"""
    prompt = f"""
    You are a professional mediator acting as the user.
    The user wants to resolve a conflict with this person.
    
    Chat Context:
    {history}
    
    Task: Write a calm, polite, and constructive reply (in Uzbek) to de-escalate the situation and make peace.
    Style: {style}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Uzr, biroz band edim. Gaplashib olsak bo'ladimi?"

# --- ELITE DATA STORAGE ---
DAILY_LOG_FILE = os.path.join(os.getcwd(), "data", "daily_social_log.json")

def save_to_log(sender_name, message, analysis):
    """Save analysis to local log for end-of-day reporting"""
    try:
        if not os.path.exists("data"): os.makedirs("data")
        data = []
        if os.path.exists(DAILY_LOG_FILE):
            with open(DAILY_LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        entry = {
            "timestamp": str(asyncio.get_event_loop().time()), # Simplification
            "sender": sender_name,
            "message": message[:200],
            "sentiment": analysis.get("sentiment"),
            "summary": analysis.get("summary")
        }
        data.append(entry)
        
        with open(DAILY_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Log save error: {e}")

@client.on(events.NewMessage(incoming=True))
async def incoming_handler(event):
    """Monitor ALL messages (Private, Groups, Channels) v18.5"""
    try:
        sender = await event.get_sender()
        sender_name = "Noma'lum"
        
        if isinstance(sender, User):
            sender_name = f"{sender.first_name} {sender.last_name or ''}".strip()
        elif isinstance(sender, (Chat, Channel)):
            sender_name = sender.title
        
        message_text = event.message.message
        if not message_text or len(message_text) < 5: return

        # 1. Global Analysis for ALL messages
        logger.info(f"🛰 Monitoring: [{sender_name}]")
        analysis = await analyze_sentiment(message_text)
        
        # 2. Save for Daily Report
        save_to_log(sender_name, message_text, analysis)
        
        # 3. HUD Real-time Update (Elite v18.5)
        for cb in HUD_CALLBACKS:
            try:
                cb(f"[{sender_name}]: {message_text[:40]}...")
            except: pass

        # 4. Urgent Conflict Detection
        if analysis.get("conflict"):
            logger.warning(f"⚔ Urgent Conflict in {sender_name}")
            # Potential voice alert or separate notification
            
    except Exception as e:
        logger.error(f"Handler error: {e}")

async def generate_daily_report():
    """Analyze the day's logs and provide a structured summary report"""
    try:
        if GLOBAL_LOOP and GLOBAL_LOOP.is_running():
            fut = asyncio.run_coroutine_threadsafe(_generate_report_logic(), GLOBAL_LOOP)
            return fut.result(timeout=15)
        return await _generate_report_logic()
    except Exception as e:
        return f"Hisobot yaratishda xato: {e}"

async def _generate_report_logic():
    """Core logic for report generation"""
    if not os.path.exists(DAILY_LOG_FILE):
        return "Bugun uchun ma'lumotlar mavjud emas, janob."
    
    try:
        with open(DAILY_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            
        if not logs: return "Bugungi xotira bo'sh, janob."
        
        prompt = f"""
        You are JARVIS. Analyze these Telegram message summaries from today and provide a "Daily Intelligence Report" in Uzbek.
        Focus on:
        1. Key topics discussed across all groups and channels.
        2. Any important requests or tasks mentioned.
        3. General social mood/sentience.
        4. Urgent matters that were noticed.
        
        Data: {json.dumps(logs[-30:])} # Analyze last 30 significant events
        """
        response = model.generate_content(prompt)
        report = response.text
        
        # Clear log for next day optionally or archive it
        return f"📅 BUGUNGI IJTIMOIY HISOBOT (Elite v18.5):\n\n{report}"
    except Exception as e:
        return f"Hisobot yaratishda xato: {e}"

async def get_recent_messages(target_name, limit=10):
    """Fetch last X messages from a specific chat for analysis"""
    try:
        # 1. If we have a global loop running (Integrated HUD mode), use it
        if GLOBAL_LOOP and GLOBAL_LOOP.is_running():
            fut = asyncio.run_coroutine_threadsafe(_get_msgs_logic(target_name, limit), GLOBAL_LOOP)
            return fut.result(timeout=10)
        
        # 2. Standalone mode (Legacy)
        return await _get_msgs_logic(target_name, limit)
    except Exception as e:
        return f"Xabar olishda xato: {e}"

async def _get_msgs_logic(target_name, limit):
    """Core logic for message fetching"""
    if not client.is_connected():
        await client.connect()
        
    target_chat = None
    async for dialog in client.iter_dialogs():
        if target_name.lower() in dialog.name.lower():
            target_chat = dialog
            break
            
    if not target_chat:
        return f"❌ {target_name} nomli chat topilmadi."

    history = []
    async for msg in client.iter_messages(target_chat, limit=limit):
        sender = "Siz" if msg.out else "U kishi"
        history.append(f"{sender}: {msg.text}")
    
    history.reverse() # Oldest to newest
    return "\n".join(history)

async def resolve_conflict_task(target_name):
    """Foydalanuvchi buyrug'i bilan yarashish jarayonini boshlash"""
    logger.info(f"🕊 Starting Mediation Protocol for: {target_name}")
    
    # Find chat
    target_chat = None
    async for dialog in client.iter_dialogs():
        if target_name.lower() in dialog.name.lower():
            target_chat = dialog
            break
            
    if not target_chat:
        print(f"❌ Chat with {target_name} not found.")
        return

    # Fetch history
    history = ""
    async for msg in client.iter_messages(target_chat, limit=10):
        sender = "Them" if msg.sender_id == target_chat.id else "Me"
        history = f"{sender}: {msg.text}\n" + history
        
    print(f"🔍 Analyzing Chat History with {target_chat.name}...")
    reply_draft = await generate_reply(history)
    
    print(f"\n💡 JARVIS taklif qilgan javob:\n'{reply_draft}'\n")
    print("Yuboraymi? (Ha/Yo'q)")
    # Real senariyda user ovoz bilan tasdiqlaydi, bu yerda simulation

from instagrapi import Client as InstaClient
from instagrapi.types import Media

# --- INSTAGRAM CONFIG ---
INSTA_USERNAME = "sardor007elmurodov@gmail.com" # Updated to email based on user request
INSTA_PASSWORD = "Sar009" # User Provided Password

class InstagramManager:
    def __init__(self):
        self.cl = InstaClient()
        self.is_logged_in = False

    def login(self, username, password):
        try:
            self.cl.login(username, password)
            self.is_logged_in = True
            logger.info(f"✅ Instagram logged in as: {username}")
            return True
        except Exception as e:
            logger.error(f"❌ Instagram Login Failed: {e}")
            return False

    def get_timeline_summary(self):
        """Asosiy lentadagi yangiliklarni tahlil qilish"""
        if not self.is_logged_in: return "Instagram tizimiga kirmagan."
        try:
            feed = self.cl.get_timeline_feed()
            # Analyze top 5 posts
            summary = []
            for item in list(feed.values())[:5]:
                user = item.user.username
                text = item.caption_text
                summary.append(f"@{user}: {text[:50]}...")
            return "\n".join(summary)
        except Exception as e:
            return f"Feed xatosi: {e}"

    def auto_post_video(self, video_path, caption):
        """Avtomatik video/reel yuklash"""
        if not self.is_logged_in: return "Kirmaganman."
        try:
            logger.info(f"📹 Posting video: {video_path}")
            media = self.cl.video_upload(video_path, caption)
            return f"Video muvaffaqiyatli yuklandi: {media.pk}"
        except Exception as e:
            return f"Video yuklashda xato: {e}"

insta_manager = InstagramManager()

# ... (Previous Telegram code remains) ...

async def main():
    global GLOBAL_LOOP
    GLOBAL_LOOP = asyncio.get_event_loop()
    print("Social Sentience Engine ishga tushmoqda...")
    
    # 1. Telegram Start
    try:
        await client.start(phone=PHONE_NUMBER)
        print("✅ Telegram ulangan!")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
    
    # 2. Instagram Start (Optional/On request)
    if INSTA_PASSWORD:
        insta_manager.login(INSTA_USERNAME, INSTA_PASSWORD)
    
    # Run forever
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Running inside existing loop check
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("Asyncio loop already running. Use task creation.")
            loop.create_task(main())
        else:
            asyncio.run(main())
    except:
        asyncio.run(main())
