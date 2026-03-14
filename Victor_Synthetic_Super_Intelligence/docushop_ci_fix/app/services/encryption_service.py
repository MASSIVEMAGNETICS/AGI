import base64
from typing import Optional

from cryptography.fernet import Fernet


class EncryptionService:
    """
    Service for encrypting/decrypting PHI data

    Uses AES-256 encryption via Fernet (symmetric encryption)
    In production, use cloud KMS or HSM for key management
    """

    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            # Generate a new key - in production, load from secure key storage
            key = Fernet.generate_key()
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string"""
        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return base64.b64encode(encrypted_bytes).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string"""
        encrypted_bytes = base64.b64decode(ciphertext.encode())
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key()


# Global encryption service instance
# In production, initialize with key from environment/KMS
encryption_service = EncryptionService()
