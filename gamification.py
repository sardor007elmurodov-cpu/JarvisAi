"""
JARVIS - Gamification System
Foydalanuvchi faolligini o'yinga aylantirish (XP, Level).
"""
import json
import os
from utils import setup_logger

class GamificationSystem:
    def __init__(self):
        self.logger = setup_logger("Gamification")
        self.data_file = os.path.join(os.getcwd(), "data", "user_stats.json")
        self.stats = self._load_data()
        
        # Level formulasi: XP = Level * 100
        self.xp_per_level = 100

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"level": 1, "xp": 0, "total_commands": 0}

    def _save_data(self):
        # Ensure data dir exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w") as f:
            json.dump(self.stats, f)

    def add_xp(self, amount, source="Command"):
        """XP qo'shish va levelni tekshirish"""
        self.stats["xp"] += amount
        self.stats["total_commands"] += 1
        
        # Level Up Logic
        current_level = self.stats["level"]
        required_xp = current_level * self.xp_per_level
        
        response = ""
        if self.stats["xp"] >= required_xp:
            self.stats["xp"] -= required_xp
            self.stats["level"] += 1
            response = f"\n🎉 TABRIKLAYMAN! Siz yangi darajaga ko'tarildingiz: Level {self.stats['level']}!"
            self.logger.info(f"Level Up: {self.stats['level']}")
            
        self._save_data()
        return response

    def get_status(self):
        """Status ma'lumotlarini olish"""
        lvl = self.stats["level"]
        xp = self.stats["xp"]
        req = lvl * self.xp_per_level
        progress = int((xp / req) * 100)
        
        return {
            "level": lvl,
            "xp": xp,
            "required": req,
            "progress": progress,
            "total": self.stats["total_commands"]
        }

    def get_status_text(self):
        s = self.get_status()
        return f"Level: {s['level']} | XP: {s['xp']}/{s['required']} ({s['progress']}%) | Jami buyruqlar: {s['total']}"

if __name__ == "__main__":
    game = GamificationSystem()
    print(game.add_xp(50, "Test"))
    print(game.get_status_text())
