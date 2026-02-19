"""
JARVIS - Elite Security Engine
Handles advanced command validation and authentication.
"""

import config
from utils import setup_logger, is_destructive_action

class SecurityEngine:
    def __init__(self, memory=None):
        self.logger = setup_logger("SecurityEngine")
        self.memory = memory
        self.authorized_users = ["Sardor", "Janob", "Admin"] # Authorized pool
        self.emergency_mode = False

    def validate_command(self, action, params, current_user="Janob"):
        """
        Buyruq xavfsizligini kompleks tekshirish
        
        Returns:
            tuple: (is_safe, message, severity)
        """
        # 1. Emergency mode check
        if self.emergency_mode:
            return False, "Emergency mode faol. Amallar vaqtincha taqiqlangan.", "CRITICAL"

        # 2. Destructive actions check
        if is_destructive_action(action):
            # Ismi bazadan tekshirish
            stored_name = self.memory.get_user_name() if self.memory else "Janob"
            
            if stored_name not in self.authorized_users:
                self.logger.warning(f"Unauthorized destructive action attempt by: {stored_name}")
                return False, f"Kechirasiz {stored_name}, bu amalni bajarish uchun vakolatingiz yetarli emas.", "HIGH"
            
            return False, f"Ushbu amal ({action}) tizim uchun xavfli bo'lishi mumkin. Tasdiqlaysizmi?", "MEDIUM"

        return True, "Safe", "LOW"

    def authenticate_user(self, input_source="voice"):
        """
        Foydalanuvchini tanish simulyatsiyasi
        """
        self.logger.info(f"Authenticating via {input_source}...")
        # Elite simulation: User name in memory must be authorized
        if self.memory:
            name = self.memory.get_user_name()
            if name in self.authorized_users:
                return True
        return False

    def toggle_emergency(self, state=True):
        self.emergency_mode = state
        self.logger.info(f"Emergency mode set to: {state}")

if __name__ == "__main__":
    sec = SecurityEngine()
    print(sec.validate_command("shutdown", {}))
