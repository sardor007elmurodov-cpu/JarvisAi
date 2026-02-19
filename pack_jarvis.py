import os
import zipfile
from datetime import datetime

def pack_project():
    # Faqat "Miyya" (VPS) uchun kerakli fayllar
    include_files = [
        "vps_agent.py", "elite_ai.py", "research_assistant.py", 
        "llm_brain.py", "utils.py", "config.py", "requirements.txt",
        "telegram_bot.py", "memory.py", "social_sentience.py",
        "agent.py" # Core logic
    ]
    
    include_dirs = ["data"] # Xotira va sozlamalar uchun
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = f"JARVIS_VPS_ELITE_{timestamp}.zip"
    
    print(f"📦 Arxiv yaratilmoqda: {zip_name}...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Fayllarni qo'shish
        for file in include_files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  + {file}")
        
        # Papkalarni qo'shish
        for folder in include_dirs:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
                        print(f"  + {file_path}")

    print(f"\n✅ Tayyor! '{zip_name}' faylini VPS-ga yuklang.")

if __name__ == "__main__":
    pack_project()
