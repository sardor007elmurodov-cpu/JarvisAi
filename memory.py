"""
JARVIS - Advanced Memory Engine with AI Conversation Tracking
Handles long-term storage using SQLite.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from utils import setup_logger

class MemoryEngine:
    def __init__(self, db_path="jarvis_memory.db"):
        self.logger = setup_logger("MemoryEngine")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Ma'lumotlar bazasini va jadvallarni yaratish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # User Info
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_info (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Command History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    command TEXT,
                    response TEXT,
                    language TEXT
                )
            ''')
            
            # Habits (App usage)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                    app_name TEXT PRIMARY KEY,
                    use_count INTEGER,
                    last_used DATETIME
                )
            ''')
            
            # Projects
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    created_at DATETIME
                )
            ''')
            
            # Semantic Memory (Phase 4)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    topic TEXT PRIMARY KEY,
                    summary TEXT,
                    context TEXT,
                    created_at DATETIME
                )
            ''')
            
            # AI Conversation History (Phase 19.2)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    user_query TEXT,
                    assistant_response TEXT,
                    context TEXT
                )
            ''')
            
            # Long-Term Facts (New)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT,
                    category TEXT,
                    created_at DATETIME
                )
            ''')
            
            # Default user name if not exists
            cursor.execute("INSERT OR IGNORE INTO user_info (key, value) VALUES ('name', 'Janob')")
            
            conn.commit()
            conn.close()
            self.logger.info("SQLite Database initialized.")
        except Exception as e:
            self.logger.error(f"DB Init Error: {e}")

    def _query(self, sql, params=(), commit=False, fetch_one=False):
        """SQL so'rovlarini bajarish uchun yordamchi metod"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            
            if commit:
                conn.commit()
                result = cursor.rowcount
            else:
                result = cursor.fetchone() if fetch_one else cursor.fetchall()
            
            conn.close()
            return result
        except Exception as e:
            self.logger.error(f"Query Error: {e}")
            return None

    # ==================== USER INFO ====================
    def get_user_name(self):
        """Foydalanuvchi ismini olish"""
        result = self._query("SELECT value FROM user_info WHERE key='name'", fetch_one=True)
        return result[0] if result else "Janob"

    def set_user_name(self, name):
        """Foydalanuvchi ismini o'rnatish"""
        return self._query(
            "INSERT OR REPLACE INTO user_info (key, value) VALUES ('name', ?)",
            (name,),
            commit=True
        )
    
    def set_user_info(self, key, value):
        """Umumiy foydalanuvchi ma'lumotlarini o'rnatish"""
        return self._query(
            "INSERT OR REPLACE INTO user_info (key, value) VALUES (?, ?)",
            (key, value),
            commit=True
        )

    # ==================== COMMAND HISTORY ====================
    def add_to_history(self, command, response, language="uz"):
        """Buyruqni tarixga qo'shish"""
        return self._query(
            "INSERT INTO commands_history (timestamp, command, response, language) VALUES (?, ?, ?, ?)",
            (datetime.now(), command, response, language),
            commit=True
        )

    def add_command_history(self, action, parameters_str):
        """Alias for add_to_history to match executor calls"""
        return self.add_to_history(f"{action} {parameters_str}", "Executed via System")

    def get_history(self, limit=10):
        """So'nggi buyruqlarni olish (Tuples)"""
        return self._query(
            "SELECT timestamp, command, response FROM commands_history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )

    def get_command_history(self, limit=10):
        """So'nggi buyruqlarni olish (Dictionaries) - IntentEngine uchun"""
        rows = self.get_history(limit)
        history = []
        if rows:
            for row in rows:
                history.append({
                    "timestamp": row[0],
                    "command": row[1],
                    "response": row[2]
                })
        return history

    # ==================== HABITS ====================
    def record_app_usage(self, app_name):
        """Dastur ishlatilganini qayd qilish"""
        existing = self._query("SELECT use_count FROM habits WHERE app_name=?", (app_name,), fetch_one=True)
        
        if existing:
            return self._query(
                "UPDATE habits SET use_count=use_count+1, last_used=? WHERE app_name=?",
                (datetime.now(), app_name),
                commit=True
            )
        else:
            return self._query(
                "INSERT INTO habits (app_name, use_count, last_used) VALUES (?, 1, ?)",
                (app_name, datetime.now()),
                commit=True
            )

    def get_most_used_apps(self, limit=5):
        """Eng ko'p ishlatiladigan dasturlar"""
        return self._query(
            "SELECT app_name, use_count FROM habits ORDER BY use_count DESC LIMIT ?",
            (limit,)
        )
    
    def log_app_usage(self, app_name):
        """Alias for record_app_usage - dastur ishlatilganini qayd qilish"""
        return self.record_app_usage(app_name)

    # ==================== PROJECTS ====================
    def add_project(self, name, description=""):
        """Yangi loyiha qo'shish"""
        return self._query(
            "INSERT OR REPLACE INTO projects (name, description, created_at) VALUES (?, ?, ?)",
            (name, description, datetime.now()),
            commit=True
        )

    def get_all_projects(self):
        """Barcha loyihalarni olish"""
        return self._query("SELECT name, description, created_at FROM projects")

    def delete_project(self, name):
        """Loyihani o'chirish"""
        return self._query(
            "DELETE FROM projects WHERE name=?",
            (name,),
            commit=True
        )

    # ==================== SEMANTIC MEMORY ====================
    def add_semantic_memory(self, topic, summary, context=""):
        """Semantik xotirani qo'shish"""
        return self._query(
            "INSERT OR REPLACE INTO semantic_memory (topic, summary, context, created_at) VALUES (?, ?, ?, ?)",
            (topic, summary, context, datetime.now()),
            commit=True
        )

    def get_semantic_memory(self, topic):
        """Mavzu bo'yicha xotirani olish"""
        result = self._query(
            "SELECT summary, context FROM semantic_memory WHERE topic=?",
            (topic,),
            fetch_one=True
        )
        return result if result else (None, None)

    def summarize_recent_history(self):
        """So'nggi tarixni avtomatik xulosalash (AI Brain kerak)"""
        history = self.get_history(limit=20)
        if not history:
            return
        
        from llm_brain import GeminiBrain
        llm_brain = GeminiBrain()
        
        prompt = "Summarize these recent commands:\\n"
        for ts, cmd, resp in history:
            prompt += f"- {cmd}\\n"
        
        summary = llm_brain.generate_response(prompt)
        if summary:
            self.add_semantic_memory("recent_conversation", summary)

    # ==================== AI CONVERSATION MEMORY (Phase 2) ====================
    
    def store_conversation(self, user_query, assistant_response, context=""):
        """Store conversation for AI memory"""
        try:
            return self._query(
                "INSERT INTO conversation_history (timestamp, user_query, assistant_response, context) VALUES (?, ?, ?, ?)",
                (datetime.now(), user_query, assistant_response, context),
                commit=True
            )
        except Exception as e:
            self.logger.error(f"Store conversation error: {e}")
            return False
    
    def get_recent_conversations(self, limit=10):
        """Get recent conversation history"""
        try:
            results = self._query(
                "SELECT timestamp, user_query, assistant_response, context FROM conversation_history ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            
            conversations = []
            for row in results:
                conversations.append({
                    "timestamp": row[0],
                    "user_query": row[1],
                    "assistant_response": row[2],
                    "context": row[3]
                })
            
            return conversations
        except Exception as e:
            self.logger.error(f"Get conversations error: {e}")
            return []
    
    def search_conversations(self, query, days_ago=30):
        """Search past conversations"""
        try:
            cutoff = datetime.now() - timedelta(days=days_ago)
            
            results = self._query(
                "SELECT timestamp, user_query, assistant_response FROM conversation_history WHERE (user_query LIKE ? OR assistant_response LIKE ?) AND timestamp > ? ORDER BY timestamp DESC LIMIT 20",
                (f"%{query}%", f"%{query}%", cutoff)
            )
            
            conversations = []
            for row in results:
                conversations.append({
                    "timestamp": row[0],
                    "user_query": row[1],
                    "assistant_response": row[2]
                })
            
            return conversations
        except Exception as e:
            self.logger.error(f"Search conversations error: {e}")
            return []

    # ==================== LONG-TERM FACTS (Phase 2) ====================
    def add_fact(self, fact, category="general"):
        """Foydalanuvchi haqida yangi fakt qo'shish"""
        return self._query(
            "INSERT INTO user_facts (fact, category, created_at) VALUES (?, ?, ?)",
            (fact, category, datetime.now()),
            commit=True
        )

    def get_facts(self, category=None, limit=20):
        """Saqlangan faktlarni olish"""
        if category:
            return self._query(
                "SELECT fact, category, created_at FROM user_facts WHERE category=? ORDER BY created_at DESC LIMIT ?",
                (category, limit)
            )
        else:
            return self._query(
                "SELECT fact, category, created_at FROM user_facts ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )

    def search_facts(self, query):
        """Faktlarni qidirish (keyword bo'yicha)"""
        return self._query(
            "SELECT fact, category FROM user_facts WHERE fact LIKE ?",
            (f"%{query}%",)
        )

if __name__ == "__main__":
    mem = MemoryEngine()
    print(f"User: {mem.get_user_name()}")
    # mem.add_fact("User is a developer", "profession")
    # print(mem.get_facts())
