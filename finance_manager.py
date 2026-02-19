"""
JARVIS - Finance Manager
SQLite orqali xarajatlar va daromadlarni hisobga olish.
"""
import sqlite3
import os
from datetime import datetime
from utils import setup_logger

class FinanceManager:
    def __init__(self):
        self.logger = setup_logger("FinanceManager")
        self.db_path = os.path.join(os.getcwd(), "data", "finance.db")
        
        # Data papkasini yaratish
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
            
        self._init_db()

    def _init_db(self):
        """Ma'lumotlar bazasini yaratish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                amount REAL,
                category TEXT,
                description TEXT,
                type TEXT -- 'expense' yoki 'income'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_limit REAL
            )
        ''')
        conn.commit()
        conn.close()

    def set_budget(self, category, limit):
        """Kategoriya uchun oylik limit o'rnatish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO budgets (category, monthly_limit) VALUES (?, ?)", (category, limit))
            conn.commit()
            conn.close()
            return f"{category} uchun oylik limit {limit} so'm qilib belgilandi."
        except Exception as e:
            return f"Xatolik: {e}"

    def check_budget(self, category):
        """Budjet holatini tekshirish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Limitni olish
            cursor.execute("SELECT monthly_limit FROM budgets WHERE category=?", (category,))
            row = cursor.fetchone()
            if not row: return None
            limit = row[0]
            
            # Shu oydagi xarajatni olish
            this_month = datetime.now().strftime("%Y-%m")
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE category=? AND type='expense' AND timestamp LIKE ?", (category, f"{this_month}%"))
            spent = cursor.fetchone()[0] or 0
            
            conn.close()
            return {"limit": limit, "spent": spent}
        except:
            return None

    def add_transaction(self, amount, category="Umumiy", description="", item_type="expense"):
        """Tranzaksiya qo'shish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO transactions (timestamp, amount, category, description, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, amount, category, description, item_type))
            
            conn.commit()
            
            # Budjetni tekshirish (Elite v21.0)
            budget_info = self.check_budget(category)
            warning = ""
            if budget_info and item_type == "expense":
                if budget_info["spent"] > budget_info["limit"]:
                    warning = f"\n⚠️ OGOHLANTIRISH: {category} uchun oylik budjetdan o'tib ketdingiz! (Limit: {budget_info['limit']}, Sarflandi: {budget_info['spent']})"
                elif budget_info["spent"] > budget_info["limit"] * 0.9:
                    warning = f"\n⚠️ DIQQAT: {category} budjeti tugab bormoqda (90%+ ishlatildi)."
            
            conn.close()
            
            type_uz = "xarajat" if item_type == "expense" else "daromad"
            self.logger.info(f"Added {type_uz}: {amount} - {category}")
            return f"{amount} so'm miqdoridagi {type_uz} {category} kategoriyasiga qo'shildi, janob.{warning}"
        except Exception as e:
            self.logger.error(f"Error adding transaction: {e}")
            return f"Moliya bazasiga yozishda xatolik yuz berdi: {e}"

    def get_daily_report(self):
        """Bugungi xarajatlar hisoboti"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute('''
                SELECT SUM(amount) FROM transactions 
                WHERE type='expense' AND timestamp LIKE ?
            ''', (f"{today}%",))
            
            total = cursor.fetchone()[0] or 0
            conn.close()
            
            return f"Bugungi jami xarajatlaringiz {total} so'mni tashkil etadi, janob."
        except Exception as e:
            return f"Hisobot tayyorlashda xatolik: {e}"

    def get_balance(self):
        """Umumiy balans"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
            income = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
            expense = cursor.fetchone()[0] or 0
            
            balance = income - expense
            conn.close()
            
            return f"Hozirgi balansingiz {balance} so'm. Jami daromad: {income}, jami xarajat: {expense}."
        except Exception as e:
            return f"Balansni hisoblashda xatolik: {e}"

if __name__ == "__main__":
    # Test
    fm = FinanceManager()
    print(fm.add_transaction(50000, "Tushlik", "Osh markazi"))
    print(fm.get_daily_report())
    print(fm.get_balance())
