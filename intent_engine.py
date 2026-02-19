"""
JARVIS - Predictive Intent Engine (Elite v16.0)
Analyzes user behavior patterns to anticipate future commands and workspace needs.
"""
import time
from collections import Counter
from pathlib import Path

class IntentEngine:
    def __init__(self, memory_engine=None):
        self.memory = memory_engine
        self.history_limit = 50
        self.transition_matrix = {}
        
    def analyze_patterns(self):
        """Build a simple Markov-style transition matrix from command history"""
        if not self.memory: return
        
        # Get last 100 commands from memory
        history = self.memory.get_command_history(limit=self.history_limit)
        if len(history) < 5: return

        # Command extraction (simplified)
        commands = [h['command'].lower().split()[0] for h in history if 'command' in h]
        
        # Build transitions: Current -> Next
        self.transition_matrix = {}
        for i in range(len(commands) - 1):
            current = commands[i]
            next_cmd = commands[i+1]
            if current not in self.transition_matrix:
                self.transition_matrix[current] = []
            self.transition_matrix[current].append(next_cmd)

    def predict_next(self, current_command):
        """Predict the next likely command based on the current one"""
        if not current_command: return None
        
        cmd_key = current_command.lower().split()[0]
        if cmd_key not in self.transition_matrix:
            return None
            
        # Get most common next command
        next_probs = Counter(self.transition_matrix[cmd_key])
        prediction, count = next_probs.most_common(1)[0]
        
        # Confidence threshold
        confidence = count / len(self.transition_matrix[cmd_key])
        if confidence > 0.4:
            return {
                "action": prediction,
                "confidence": confidence,
                "hint": self._generate_hint(prediction)
            }
        return None

    def _generate_hint(self, action):
        hints = {
            "open": "Janob, odatda bu loyihani ochganingizdan so'ng terminalni ishga tushirasiz. Shuni bajaraymi?",
            "google": "Qidiruv natijalari asosida yangi hujjat yaratishni taklif qilaman.",
            "youtube": "Musiqa tinglash vaqtida 'Focus Mode'ni yoqishni unutmang.",
            "telegram": "Xabar yuborilgandan so'ng hisobotni yangilab qo'yishingizni maslahat beraman."
        }
        return hints.get(action, f"Janob, {action} bo'yicha keyingi qadamni rejalashtiryapman.")

if __name__ == "__main__":
    # Test simulation
    engine = IntentEngine()
    engine.transition_matrix = {"open": ["terminal", "terminal", "browser"]}
    print(engine.predict_next("open repository"))
