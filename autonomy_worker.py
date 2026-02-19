import os
import shutil
import time
import threading
from utils import setup_logger

class SystemAutonomy:
    """
    JARVIS - System Autonomy Worker
    Handles file organization, cache cleaning, and system optimization.
    """
    def __init__(self, hud_callback=None):
        self.logger = setup_logger("SystemAutonomy")
        self.hud_callback = hud_callback # To update HUD UI
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
    def get_disk_info(self):
        """Disk holatini aniqlash (GB)"""
        total, used, free = shutil.disk_usage("/")
        return free // (2**30)

    def organize_desktop(self):
        """Desktopdagi fayllarni papkalarga saralash"""
        self.logger.info("Organizing Desktop...")
        if self.hud_callback:
            self.hud_callback("ORGANIZING", 20)
            
        folders = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
            "Apps": [".exe", ".msi"],
            "Archives": [".zip", ".rar", ".7z"],
            "Media": [".mp4", ".mp3", ".wav", ".avi"]
        }
        
        files = [f for f in os.listdir(self.desktop_path) if os.path.isfile(os.path.join(self.desktop_path, f))]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            moved = False
            for folder, exts in folders.items():
                if ext in exts:
                    dest_dir = os.path.join(self.desktop_path, folder)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    shutil.move(os.path.join(self.desktop_path, file), os.path.join(dest_dir, file))
                    moved = True
                    break
                    
        if self.hud_callback:
            self.hud_callback("FINISHED", 100)
        self.logger.info("Desktop organized successfully.")

    def clean_system(self):
        """Vaqtincha fayllarni tozalash (Silently)"""
        self.logger.info("Cleaning System Cache...")
        temp_dirs = [
            os.environ.get('TEMP'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
        ]
        
        if self.hud_callback:
            self.hud_callback("CLEANING", 10)
            
        total_deleted = 0
        for d in temp_dirs:
            if not d or not os.path.exists(d): continue
            for item in os.listdir(d):
                item_path = os.path.join(d, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        total_deleted += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        total_deleted += 1
                except: continue
                
        if self.hud_callback:
            self.hud_callback(f"CLEANED {total_deleted} ITEMS", 100)
        
        self.logger.info(f"System cleaned. Deleted {total_deleted} items.")

if __name__ == "__main__":
    sa = SystemAutonomy()
    print(f"Free space: {sa.get_disk_info()} GB")
    # sa.clean_system()
