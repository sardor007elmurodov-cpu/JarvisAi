
import os
import asyncio
import subprocess
import pyautogui
import psutil
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import config
from utils import setup_logger

# Suppress loggers
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

class TelegramBot:
    """
    JARVIS Remote Command Center (Bot API).
    Uses 'python-telegram-bot' to avoid api_id/hash requirements.
    """
    def __init__(self):
        self.logger = setup_logger("TelegramBot")
        self.bot_token = config.TELEGRAM_SETTINGS["bot_token"]
        self.allowed_user_id = int(config.TELEGRAM_SETTINGS["chat_id"])
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != self.allowed_user_id:
            await update.message.reply_text("⛔ Access Denied")
            return

        keyboard = [
            [InlineKeyboardButton("🔒 Lock Screen", callback_data="lock"), InlineKeyboardButton("📸 Screenshot", callback_data="screen")],
            [InlineKeyboardButton("🌙 Sleep", callback_data="sleep"), InlineKeyboardButton("ℹ️ Info", callback_data="info")],
            [InlineKeyboardButton("🔊 Mute", callback_data="mute"), InlineKeyboardButton("🔊 Unmute", callback_data="unmute")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🤖 **JARVIS Command Center**\nTanlang janob:", reply_markup=reply_markup, parse_mode="Markdown")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        
        if user_id != self.allowed_user_id:
            await query.answer("Access Denied", show_alert=True)
            return

        await query.answer()
        data = query.data
        self.logger.info(f"Bot received command: {data}")

        if data == "lock":
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            await query.edit_message_text(text="🔒 System Locked")
            
        elif data == "sleep":
            await query.edit_message_text(text="🌙 Sleep Mode Initiated")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            
        elif data == "screen":
            path = "remote_screenshot.png"
            pyautogui.screenshot(path)
            await query.message.reply_photo(photo=open(path, 'rb'), caption="📸 Screenshot")
            os.remove(path)
            
        elif data == "info":
            battery = psutil.sensors_battery()
            percent = battery.percent if battery else "N/A"
            mem = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent()
            await query.edit_message_text(text=f"📊 **System Status**\n🔋 Battery: {percent}%\n🧠 RAM: {mem}%\n⚡ CPU: {cpu}%", parse_mode="Markdown")
            
        elif data == "mute":
            pyautogui.press("volumemute")
            await query.edit_message_text(text="🔊 Ovoz o'chirildi")
            
        elif data == "unmute":
            pyautogui.press("volumemute")
            await query.edit_message_text(text="🔊 Ovoz yoqildi")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text commands"""
        user_id = update.effective_user.id
        if user_id != self.allowed_user_id:
             return

        text = update.message.text
        self.logger.info(f"Bot received text command: {text}")

        # 1. JARVIS Start/Stop Special Commands
        if any(cmd in text.lower() for cmd in ["jarvis_start", "start_jarvis", "jarvis ishga tushir"]):
             subprocess.Popen(["python", "start.py"], cwd=os.getcwd())
             await update.message.reply_text("🚀 JARVIS ishga tushirilmoqda...")
             return

        if any(cmd in text.lower() for cmd in ["jarvis_stop", "stop_jarvis", "jarvis o'chir"]):
             subprocess.Popen(["python", "quit_jarvis.py"], cwd=os.getcwd())
             await update.message.reply_text("🛑 JARVIS to'xtatilmoqda...")
             return

        # 2. Forward other commands to JARVIS via file bridge (Elite v21.0)
        # This allows the bot to act as a remote input for the core agent
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cmd_file = os.path.join(base_dir, "data", "remote_command.txt")
            with open(cmd_file, "w", encoding="utf-8") as f:
                f.write(text)
            await update.message.reply_text(f"📥 Buyruq qabul qilindi: '{text}'")
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {e}")

    async def send_notification(self, message):
        """Send proactive message to the user"""
        try:
            from telegram import Bot
            bot = Bot(token=self.bot_token)
            await bot.send_message(chat_id=self.allowed_user_id, text=message, parse_mode="Markdown")
            return True
        except Exception as e:
            self.logger.error(f"Notification error: {e}")
            return False

    async def send_file(self, file_path, caption=""):
        """Send file to the user"""
        try:
            from telegram import Bot
            bot = Bot(token=self.bot_token)
            with open(file_path, 'rb') as f:
                await bot.send_document(chat_id=self.allowed_user_id, document=f, caption=caption)
            return True
        except Exception as e:
            self.logger.error(f"File send error: {e}")
            return False

    def run(self):
        """Starts the bot polling loop"""
        self.logger.info("Starting Telegram Bot (Polling)...")
        application = Application.builder().token(self.bot_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        from telegram.ext import MessageHandler, filters
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

        # Run polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
