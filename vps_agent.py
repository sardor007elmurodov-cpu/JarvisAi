"""
JARVIS - VPS Agent (Cortex) Elite v1.0
Bulutda ishlovchi miyya qismi. Telegram va AI tahlilini boshqaradi.
"""
import os
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import config
from elite_ai import EliteAI
from research_assistant import ResearchAssistant
from utils import setup_logger

# --- GLOBAL STATE ---
COMMAND_QUEUE = []
app = Flask(__name__)
logger = setup_logger("VPS_Agent")
ai = EliteAI()
research = ResearchAssistant()

# --- TELEGRAM BOT LOGIC (VPS MODE) ---
class VPSTelegramBot:
    def __init__(self):
        self.token = config.TELEGRAM_SETTINGS["bot_token"]
        self.chat_id = int(config.TELEGRAM_SETTINGS["chat_id"])

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.chat_id: return
        await update.message.reply_text("🤖 **JARVIS VPS Active**\nMen bulutdaman, janob. Nima buyurasiz?")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.chat_id: return
        text = update.message.text
        logger.info(f"VPS Bot Received: {text}")

        # 1. Research (VPS-da bajariladi)
        if "tadqiqot" in text.lower() or "research" in text.lower():
            topic = text.lower().replace("tadqiqot", "").replace("research", "").strip()
            await update.message.reply_text(f"🔍 VPS-da tadqiqot boshlandi: {topic}...")
            
            # Async research
            res = await research.perform_research(topic, depth="deep")
            
            # Export buyrug'ini PC-ga yuboramiz
            COMMAND_QUEUE.append(f"research_result:{res}")
            await update.message.reply_text("✅ Tadqiqot tugadi. Hisobot PC-da Word formatida ochiladi.")
            return

        # 2. PC Commands (PC-ga yuboriladi)
        pc_keywords = ["och", "open", "yoz", "type", "screenshot", "screen", "lock", "sleep", "app", "cmd"]
        if any(kw in text.lower() for kw in pc_keywords):
            COMMAND_QUEUE.append(text)
            await update.message.reply_text("📥 Buyruq PC-ga yuborildi.")
            return

        # 3. AI Chat (VPS-da bajariladi)
        response = ai.process(text)
        await update.message.reply_text(response)

    def run(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        logger.info("VPS Telegram Bot Polling...")
        application.run_polling()

# --- FLASK SERVER LOGIC ---
@app.route('/get', methods=['GET'])
def get_commands():
    if COMMAND_QUEUE:
        cmd = COMMAND_QUEUE.pop(0)
        return jsonify({"command": cmd})
    return jsonify({"command": None})

@app.route('/')
def home():
    return "JARVIS VPS Cortex is Online."

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == "__main__":
    # Flaskni alohida thread-da ishga tushirish
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Botni asosiy thread-da ishga tushirish
    bot = VPSTelegramBot()
    bot.run()
