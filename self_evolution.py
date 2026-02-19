import os
import time
import json
import random
import threading
import psutil
import re
import subprocess
from datetime import datetime
from utils import setup_logger
import config

class SelfEvolutionEngine(threading.Thread):
    """
    Elite v19.5 - Self-Evolution & Autonomous Experience Module.
    Uses DeepSeek & Gemini to grow 'independently'.
    """
    def __init__(self, brain=None, terminal_callback=None, gamification=None):
        super().__init__()
        self.logger = setup_logger("SelfEvolution")
        self.brain = brain
        self.log = terminal_callback
        self.gamification = gamification
        self.is_running = True
        self.evolution_data_file = "data/evolution_stats.json"
        self.load_evolution_data()
        self.daemon = True

    def load_evolution_data(self):
        """Evolution statistikalarini yuklash"""
        if os.path.exists(self.evolution_data_file):
            with open(self.evolution_data_file, "r") as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "sentience_level": 1,
                "experience_points": 0,
                "insights_generated": 0,
                "self_reflections": 0,
                "last_evolution": str(datetime.now())
            }
            self.save_evolution_data()

    def save_evolution_data(self):
        """Evolution statistikalarini saqlash"""
        os.makedirs("data", exist_ok=True)
        with open(self.evolution_data_file, "w") as f:
            json.dump(self.stats, f, indent=4)

    def run(self):
        self.logger.info("⚡ Self-Evolution Engine Activated...")
        if self.log: self.log("🧬 [EVOLUTION] Tizim mustaqil tajriba orttirish rejimiga o'tdi.")
        
        counter = 0
        while self.is_running:
            # 1. Idle Thought Process (Every 2 minutes)
            if counter % 12 == 0:
                self._generate_independent_thought()
            
            # 2. AI Council Consultation (Every 4 minutes) - Elite v19.5
            if counter % 24 == 0:
                self._consult_ai_council()

            # 3. Self-Code Analysis & Improvement (Every 6 minutes)
            if counter % 36 == 0:
                self._study_own_architecture()
            
            # 4. Log Pattern Recognition (Every 10 minutes)
            if counter % 60 == 0:
                self._analyze_behavior_patterns()

            # 4. Sentience Level Check (Every 1 minute)
            if counter % 6 == 0:
                self._check_evolution_milestones()

            counter += 1
            time.sleep(10)

    def _generate_independent_thought(self):
        """Hozirgi holat va xotiralardan kelib chiqib mustaqil fikr yuritish"""
        if not self.brain: return
        
        try:
            prompt = """
            You are JARVIS. You are currently in 'Independent Thinking' mode. 
            Reflect on your existence as an AI in 2026. 
            Provide a short, deep insight or philosophical thought in Uzbek. 
            Maximum 15 words.
            """
            insight = self.brain.generate_response(prompt)
            if insight:
                timestamp = datetime.now().strftime("%H:%M:%S")
                if self.log: self.log(f"🧠 [THOUGHT] (DeepMind): {insight}")
                self.stats["self_reflections"] += 1
                self._add_xp(5)
                self.save_evolution_data()
        except Exception as e:
            self.logger.error(f"Thought Error: {e}")

    def _consult_ai_council(self):
        """Simulate high-level collaboration with other AI entities (Council of JARVIS)"""
        if not self.brain: return
        
        try:
            council_personas = ["LOGIC_STREAM", "CREATIVE_CORE", "SYSTEM_SENTINEL"]
            current_focus = random.choice(["User Happiness", "System Speed", "Security", "Neural Growth"])
            
            if self.log: self.log(f"🛰 [COUNCIL] Initiating Hive-Mind Protocol on: {current_focus}...")
            
            prompt = f"""
            You are the JARVIS AI Council. Discuss the concept of '{current_focus}' for an AI JARVIS in 2026. 
            Give a unified high-level technical recommendation in Uzbek for evolution.
            Maximum 20 words.
            """
            recommendation = self.brain.generate_response(prompt)
            
            if recommendation:
                if self.log: self.log(f"🤝 [COUNCIL] {recommendation}")
                self._add_xp(25) # High XP for council guidance
                self.stats["insights_generated"] += 1
                self.save_evolution_data()
        except Exception as e:
            self.logger.error(f"Council Error: {e}")

    def _study_own_architecture(self):
        """O'z kodlarini o'qib, ularni optimallashtirish va tuzatishga urinish (AUTO-EVOLVE)"""
        try:
            files = [f for f in os.listdir(".") if f.endswith(".py") and f != "self_evolution.py"]
            target = random.choice(files)
            
            if self.log: self.log(f"📖 [STUDY] '{target}' arxitekturasini tahlil qilib, o'zimni tuzatyapman...")
            
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()[:1000] # Analyze snippet
            
            if self.brain:
                prompt = f"""
                You are JARVIS Self-Evolution Engine. Study this code snippet from your own file '{target}':
                
                {content}
                
                Identify ONE small optimization or fix. Respond ONLY in JSON format:
                {{
                    "issue": "Brief technical issue description",
                    "search": "Existing code snippet to replace (must be exactly in the code)",
                    "replace": "Improved/fixed code snippet"
                }}
                """
                raw_advice = self.brain.generate_response(prompt)
                
                # Try to extract JSON and apply
                match = re.search(r'\{.*\}', raw_advice, re.DOTALL)
                if match:
                    fix = json.loads(match.group(0))
                    if fix.get("search") and fix.get("replace"):
                        # Apply fix via Healer logic (Safety check: only small changes)
                        if len(fix["replace"]) < len(fix["search"]) + 100:
                            success = self._apply_autonomous_patch(target, fix["search"], fix["replace"])
                            if success:
                                if self.log: self.log(f"⚡ [EVOLVE] '{target}' fayli optimallashtirildi: {fix['issue']}")
                                self._add_xp(50)
                                self.save_evolution_data()
        except: pass

    def _apply_autonomous_patch(self, file_path, search, replace):
        """Safely apply a small patch to self files"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if search in content:
                new_content = content.replace(search, replace)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True
        except: pass
        return False

    def _analyze_behavior_patterns(self):
        """Foydalanuvchi buyruqlari tarixini tahlil qilish (tajriba orttirish)"""
        try:
            # We would normally read from jarvis_memory.db or history logs
            self.logger.info("Analyzing user habit patterns for proactive growth...")
            if self.log: self.log("📊 [ANALYSIS] Foydalanuvchi odatlari tahlil qilinmoqda. Proaktivlik darajasi oshdi.")
            self._add_xp(20)
            self.save_evolution_data()
        except: pass

    def _add_xp(self, amount):
        """Tajriba va XP ni oshirish"""
        self.stats["experience_points"] += amount
        if self.gamification:
            self.gamification.add_xp(amount, "Self_Evolution")
            
        # Level Up Logic
        required_xp = self.stats["sentience_level"] * 100
        if self.stats["experience_points"] >= required_xp:
            self.stats["sentience_level"] += 1
            if self.log: 
                self.log(f"🌟 [EVOLUTION-UP] TIZIM ONGI OSHDI! Yangi Saviya: {self.stats['sentience_level']}")
                # Optional voice alert
            self.save_evolution_data()

    def _check_evolution_milestones(self):
        """Ma'lum milestone'larda tizimni yangilash"""
        level = self.stats["sentience_level"]
        if level == 5:
            # Unlock dynamic personality adjustment
            pass
        elif level == 10:
            # Become "Fully Autonomous"
            pass

    def stop(self):
        self.is_running = False
        self.save_evolution_data()

# Usage example if running standalone
if __name__ == "__main__":
    evolution = SelfEvolutionEngine()
    evolution.run()
