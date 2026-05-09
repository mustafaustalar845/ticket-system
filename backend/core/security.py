
# core/security.py
# Tier 2 — Security Modules: Hash Algorithm (bcrypt) + JWT


from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()
AES_SECRET_KEY = os.getenv("AES_SECRET_KEY")
if AES_SECRET_KEY:
    cipher_suite = Fernet(AES_SECRET_KEY.encode())
else:
    cipher_suite = None




SECRET_KEY      = "your_very_strong_secret_key_here"  
ALGORITHM       = "HS256"
TOKEN_EXPIRE_H  = 8     
BCRYPT_ROUNDS   = 12    


# bcrypt — Password Hashing
def hash_password(plaintext: str) -> str:
    """
    Şifreyi bcrypt ile hash'ler.

    Akış:
      1. bcrypt.gensalt(12) → rastgele 22 karakterlik salt üretir
      2. bcrypt.hashpw(şifre + salt) → 60 karakterlik hash döner
      3. Sonuç: $2b$12$<salt><hash>

    Neden plaintext saklamıyoruz?
      - Veritabanı sızıntısında şifreler ele geçirilemez
      - Her kullanıcı farklı salt → aynı şifreler farklı hash üretir
      - Rainbow table saldırıları işe yaramaz
    """
    salt   = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(plaintext.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    """
    Girilen şifreyi hash ile karşılaştırır.

    bcrypt.checkpw() — sabit-zamanlı karşılaştırma:
      - Her zaman aynı sürede çalışır
      - Timing saldırılarını engeller
      - True döndürürse şifre doğrudur
    """
    return bcrypt.checkpw(
        plaintext.encode("utf-8"),
        hashed.encode("utf-8")
    )



def create_access_token(data: dict) -> str:
    """
    JWT token üretir.
    Payload: user_id, username, role + exp (son kullanma)
    """
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_H)
    payload.update({"exp": expire, "iss": "ticket-system"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Token'ı doğrular ve payload'ı döner."""
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer="ticket-system"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturum süresi doldu. Tekrar giriş yapın."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz token."
        )

# AES-256 (Fernet) Encryption for TCKN
def encrypt_data(plain_text: str) -> str:
    if not cipher_suite:
        raise ValueError("AES_SECRET_KEY not set")
    if not isinstance(plain_text, str):
        raise ValueError("Data to encrypt must be a string")
    
    encoded_text = plain_text.encode('utf-8')
    encrypted_text = cipher_suite.encrypt(encoded_text)
    return encrypted_text.decode('utf-8')

def decrypt_data(cipher_text: str) -> str:
    if not cipher_suite:
        raise ValueError("AES_SECRET_KEY not set")
    try:
        if not isinstance(cipher_text, str):
            raise ValueError("Cipher text must be a string")
            
        decoded_cipher = cipher_text.encode('utf-8')
        decrypted_text = cipher_suite.decrypt(decoded_cipher)
        return decrypted_text.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed. Ensure the key and cipher text are valid. Error: {str(e)}")