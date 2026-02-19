
import os
import asyncio
from telethon import TelegramClient, events
import config
from utils import setup_logger

class TelegramUserBridge:
    """
    JARVIS Personal Telegram Assistant.
    Connects as the USER to handle auto-replies and background messaging.
    """
    def __init__(self):
        self.logger = setup_logger("TelegramUserBridge")
        self.api_id = config.TELEGRAM_USER_SETTINGS["api_id"]
        self.api_hash = config.TELEGRAM_USER_SETTINGS["api_hash"]
        self.session = config.TELEGRAM_USER_SETTINGS["session_name"]
        
        self.client = TelegramClient(self.session, self.api_id, self.api_hash)
        self.is_running = False
        self.loop = None

    async def start(self):
        self.logger.info("Starting Telegram User bridge...")
        try:
            await self.client.start()
            self.logger.info("Telegram User bridge connected.")
            self.is_running = True
            
            # Registration of events
            @self.client.on(events.NewMessage(incoming=True))
            async def handle_incoming(event):
                if not config.TELEGRAM_USER_SETTINGS["auto_reply"]:
                    return
                
                if event.is_private:
                    sender = await event.get_sender()
                    msg_text = event.text.lower()
                    
                    # Don't auto-reply to everything, just a simple gesture
                    self.logger.info(f"Incoming message from {sender.first_name}: {event.text}")
                    
                    # If message is "salom" or similar, we can have a smart reply
                    reply_text = f"🤖 [JARVIS]: Salom, {sender.first_name}. Sardor hozirda band bo'lishi mumkin. Men xabaringizni unga yetkazdim."
                    await event.reply(reply_text)

            self.logger.info("Auto-reply listener active.")
            await self.client.run_until_disconnected()
        except Exception as e:
            self.logger.error(f"Bridge Error: {e}")
            self.is_running = False

    async def send_message_async(self, contact, message):
        """Asenkron xabar yuborish"""
        try:
            if not self.client.is_connected():
                await self.client.connect()
            
            # Kontaktni qidirish
            entity = await self.client.get_entity(contact)
            await self.client.send_message(entity, message)
            self.logger.info(f"Background message sent to {contact}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send background message: {e}")
            return False

    def send_message(self, contact, message):
        """Sinxron wrapper (Executor uchun)"""
        if not self.is_running:
            return False
            
        future = asyncio.run_coroutine_threadsafe(
            self.send_message_async(contact, message), 
            self.client.loop
        )
        return future.result()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop
        loop.run_until_complete(self.start())

if __name__ == "__main__":
    bridge = TelegramUserBridge()
    bridge.run()
