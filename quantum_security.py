"""
JARVIS - Quantum Security (Kvant Himoya)
Fayllarni shifrlash va xavfsiz o'chirish moduli.
Algoritm: Fernet (Symmetric AES-128 via Cryptography).
Ismi: Kyber-Simulated Encryption.
"""
import os
import shutil
from cryptography.fernet import Fernet
from utils import setup_logger

class QuantumSecurity:
    def __init__(self):
        self.logger = setup_logger("QuantumSecurity")
        self.key_file = os.path.join(os.getcwd(), "data", "quantum_key.key")
        self.key = self._load_key()

    def _load_key(self):
        """Kalitni yuklash yoki yangisini yaratish"""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
            self.logger.info("New Quantum Key generated.")
            return key

    def encrypt_file(self, file_path):
        """Faylni shifrlash"""
        try:
            if not os.path.exists(file_path):
                return "Fayl topilmadi."

            with open(file_path, "rb") as f:
                data = f.read()

            fernet = Fernet(self.key)
            encrypted = fernet.encrypt(data)

            with open(file_path + ".enc", "wb") as f:
                f.write(encrypted)
            
            # Asl faylni o'chirish (ixtiyoriy, xavfsizlik uchun)
            os.remove(file_path)
            return f"Fayl muvaffaqiyatli shifrlandi: {file_path}.enc"
        except Exception as e:
            return f"Shifrlash xatosi: {e}"

    def decrypt_file(self, file_path):
        """Faylni deshifrlash"""
        try:
            if not os.path.exists(file_path):
                return "Fayl topilmadi."
            
            if not file_path.endswith(".enc"):
                return "Bu fayl shifrlanmagan (yoki .enc emas)."

            with open(file_path, "rb") as f:
                data = f.read()

            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(data)

            original_path = file_path.replace(".enc", "")
            with open(original_path, "wb") as f:
                f.write(decrypted)
            
            os.remove(file_path)
            return f"Fayl tiklandi: {original_path}"
        except Exception as e:
            return f"Deshifrlash xatosi: {e} (Noto'g'ri kalit yoki fayl buzilgan)"

    def secure_delete(self, file_path, passes=3):
        """Faylni qaytarib bo'lmas qilib o'chirish (Shredding)"""
        try:
            if not os.path.exists(file_path): return "Fayl topilmadi."
            
            length = os.path.getsize(file_path)
            
            with open(file_path, "wb") as f:
                for _ in range(passes):
                    f.write(os.urandom(length))
                    f.seek(0)
            
            os.remove(file_path)
            return f"Fayl butunlay yo'q qilindi: {file_path}"
        except Exception as e:
            return f"O'chirish xatosi: {e}"

if __name__ == "__main__":
    qs = QuantumSecurity()
    # Test
    # with open("test_secret.txt", "w") as f: f.write("Top Secret Data")
    # print(qs.encrypt_file("test_secret.txt"))
    # print(qs.decrypt_file("test_secret.txt.enc"))
