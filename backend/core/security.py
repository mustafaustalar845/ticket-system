
# core/security.py
# Tier 2 — Security Modules: Hash Algorithm (bcrypt) + JWT


from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi import HTTPException, status



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