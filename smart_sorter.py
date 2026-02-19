import os
import shutil
import time
import threading
from pathlib import Path

class SmartSorter:
    """
    JARVIS - Smart Sorter Core (Elite v10.0)
    Automatically categorizes and moves files into organized project folders.
    """
    def __init__(self, brain=None, terminal_callback=None):
        self.brain = brain
        self.log = terminal_callback
        self.base_hub = Path("C:/JARVIS_HUB")
        self.base_hub.mkdir(parents=True, exist_ok=True)
        
        # Extensions mapping for basic sorting
        self.ext_map = {
            'docs': ['.pdf', '.docx', '.txt', '.md', '.pptx', '.xlsx'],
            'media': ['.jpg', '.png', '.mp4', '.mp3', '.wav', '.gif'],
            'code': ['.py', '.js', '.html', '.css', '.json', '.cpp', '.java', '.ts', '.sh'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        }
        
        # Initialize brain if not provided
        if not self.brain:
            try:
                from llm_brain import GeminiBrain
                self.brain = GeminiBrain()
            except ImportError:
                self.brain = None

    def _get_semantic_info(self, file_path):
        """Analyze file content to determine project and category (Elite v15.0)"""
        if not self.brain or not self.brain._initialized:
            return None, None

        file_path = Path(file_path)
        # Only analyze text-like files for now (size limit 4KB)
        text_exts = ['.txt', '.py', '.js', '.md', '.html', '.css', '.json', '.sh', '.bat']
        if file_path.suffix.lower() not in text_exts or file_path.stat().st_size > 1024 * 50: # 50KB limit
            return None, None

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4000) # Read first 4000 chars

            prompt = f"""
            Analyze the following file content and name:
            Filename: {file_path.name}
            Content Preview: {content}

            Based on this, determine:
            1. PROJECT_NAME: A short (1-2 word) name of the project this file belongs to (e.g., 'JARVIS', 'Website', 'ML_Research').
            2. CATEGORY: One of [docs, media, code, archives, misc].

            Format: PROJECT: <name> | CATEGORY: <category>
            If unsure, return 'NONE'.
            """
            response = self.brain.generate_response(prompt)
            if response and "PROJECT:" in response:
                import re
                proj_match = re.search(r"PROJECT:\s*([^|]+)", response)
                cat_match = re.search(r"CATEGORY:\s*(\w+)", response)
                
                project = proj_match.group(1).strip() if proj_match else "General"
                category = cat_match.group(1).strip().lower() if cat_match else None
                return project, category
        except Exception as e:
            if self.log: self.log(f"⚠️ [SORTER] Semantic error: {e}")
        
        return None, None

    def sort_file(self, file_path, context_intent=None):
        """
        Move a file to its logical home using semantic intelligence.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return False

        # 1. Try Semantic Analysis first (Elite v15.0)
        project_name, category = self._get_semantic_info(file_path)
        
        # 2. Fallback to basic mapping if semantic failed
        if not category:
            category = "misc"
            for cat, exts in self.ext_map.items():
                if file_path.suffix.lower() in exts:
                    category = cat
                    break
        
        # 3. Use intent or semantic project name
        if context_intent:
            project_name = context_intent
        elif not project_name:
            project_name = "General"

        # Clean project name
        project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).strip()
        
        target_dir = self.base_hub / project_name / category
        target_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            target_path = target_dir / file_path.name
            # If exists, append timestamp
            if target_path.exists():
                target_path = target_dir / f"{file_path.stem}_{int(time.time())}{file_path.suffix}"
            
            shutil.move(str(file_path), str(target_path))
            if self.log:
                self.log(f"📦 [SORTER] { '🧠 SEMANTIC:' if project_name != 'General' else '' } Moved '{file_path.name}' to {project_name}/{category}")
            return str(target_path)
        except Exception as e:
            if self.log:
                self.log(f"❌ [SORTER] Failed to move {file_path.name}: {str(e)}")
            return False

    def auto_organize_directory(self, directory_path):
        """Scan and organize an entire directory"""
        dir_path = Path(directory_path)
        if not dir_path.exists(): return
        
        files = [f for f in dir_path.iterdir() if f.is_file()]
        for f in files:
            # Skip if it's already in the HUB (avoid loops if hub is in path)
            if "JARVIS_HUB" in str(f): continue
            
            # Start in thread to not block
            threading.Thread(target=self.sort_file, args=(f,), daemon=True).start()

