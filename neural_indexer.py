import os
import json
import threading
import time
from pathlib import Path

class NeuralIndexer:
    """
    JARVIS - Neural RAG Core (Elite v11.0)
    Indexes local files for semantic search and Q&A.
    """
    def __init__(self, brain=None, terminal_callback=None):
        self.brain = brain
        self.log = terminal_callback
        self.hub_path = Path("C:/JARVIS_HUB")
        self.index_path = os.path.join(os.getcwd(), "data", "neural_index.json")
        self.index = {}
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except: self.index = {}

    def _save_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=4)

    def index_hub(self):
        """Background indexing of the JARVIS_HUB"""
        if self.log: self.log("🧠 [NEURAL] Starting background indexing of JARVIS_HUB...")
        
        def _task():
            for root, dirs, files in os.walk(self.hub_path):
                for file in files:
                    if file.endswith(('.txt', '.md', '.py', '.js')):
                        file_path = os.path.join(root, file)
                        mtime = os.path.getmtime(file_path)
                        
                        # Only index if new or changed
                        if file_path not in self.index or self.index[file_path]['mtime'] < mtime:
                            content = self._read_file(file_path)
                            if content:
                                # Simple "Vector" simulation: key phrases + summary via Brain
                                info = {"mtime": mtime, "preview": content[:500]}
                                self.index[file_path] = info
                                if self.log: self.log(f"📑 [NEURAL] Indexed: {file}")
            
            self._save_index()
            if self.log: self.log("✅ [NEURAL] Hub synchronization complete.")
            
        threading.Thread(target=_task, daemon=True).start()

    def _read_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except: return None

    def query(self, query_text):
        """Simple keyword-based semantic retrieval for now, upgradeable to full embedding"""
        results = []
        keywords = query_text.lower().split()
        
        for path, info in self.index.items():
            content = info['preview'].lower()
            score = sum(1 for kw in keywords if kw in content or kw in path.lower())
            if score > 0:
                results.append((path, info['preview'][:200]))
        
        if not results:
            return "Kechirasiz janob, bu mavzuda mahalliy ma'lumot topilmadi."
            
        # Format for Brain analysis
        context = "\n".join([f"File: {r[0]}\nContent: {r[1]}" for r in results[:3]])
        return context
