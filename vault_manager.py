import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

class ShadowVault:
    """
    JARVIS - Shadow Vault (Quantum Security v16.0)
    Secure storage using AES-256 (Fernet) encryption.
    """
    def __init__(self, master_password="J.A.R.V.I.S.E.L.I.T.E"):
        self.vault_path = os.path.join(os.getcwd(), "data", "shadow.vault")
        self.salt_path = os.path.join(os.getcwd(), "data", "vault.salt")
        self.master_password = master_password.encode()
        
        if not os.path.exists(os.path.dirname(self.vault_path)):
            os.makedirs(os.path.dirname(self.vault_path))
            
        self._initialize_key()

    def _initialize_key(self):
        """Derive an AES key from the master password using PBKDF2"""
        if os.path.exists(self.salt_path):
            with open(self.salt_path, "rb") as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_path, "wb") as f:
                f.write(salt)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
        self.fernet = Fernet(key)

    def save_item(self, label, secret):
        """Encrypt and save a secret to the vault"""
        data = self.load_all()
        data[label] = secret
        
        raw_json = json.dumps(data).encode()
        encrypted = self.fernet.encrypt(raw_json)
        
        with open(self.vault_path, "wb") as f:
            f.write(encrypted)
        return True

    def load_all(self):
        """Decrypt and load all secrets"""
        if not os.path.exists(self.vault_path):
            return {}
            
        try:
            with open(self.vault_path, "rb") as f:
                encrypted = f.read()
            
            decrypted_json = self.fernet.decrypt(encrypted).decode()
            return json.loads(decrypted_json)
        except Exception as e:
            print(f"Vault decryption error: {e}")
            return {}

    def get_item(self, label):
        """Retrieve a specific secret"""
        data = self.load_all()
        return data.get(label)
