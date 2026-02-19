import os
import shutil
import zipfile
import time
from pathlib import Path

class SyncManager:
    """
    JARVIS - Autonomous Sync & Backup (Elite v11.0)
    Proactively backs up critical project data and vault.
    """
    def __init__(self, terminal_callback=None):
        self.log = terminal_callback
        self.hub_path = Path("C:/JARVIS_HUB")
        self.vault_path = Path(os.getcwd()) / "data" / "shadow.vault"
        self.backup_root = Path(os.getcwd()) / "data" / "backups"
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def perform_backup(self):
        """Create a compressed backup of hub and vault"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_root / f"JARVIS_BACKUP_{timestamp}.zip"
        
        if self.log: self.log(f"💾 [SYNC] Initiating autonomous system backup...")
        
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                # Backup HUB
                if self.hub_path.exists():
                    for root, dirs, files in os.walk(self.hub_path):
                        for file in files:
                            zipf.write(os.path.join(root, file), 
                                      arcname=os.path.relpath(os.path.join(root, file), self.hub_path.parent))
                
                # Backup Vault
                if self.vault_path.exists():
                    zipf.write(self.vault_path, arcname="shadow.vault")
            
            if self.log: self.log(f"✅ [SYNC] Backup successful: JARVIS_BACKUP_{timestamp}.zip")
            return str(backup_file)
        except Exception as e:
            if self.log: self.log(f"❌ [SYNC] Backup failed: {str(e)}")
            return False
