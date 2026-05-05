from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
from backend.core.config import settings

# Password Hashing Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Setup
ALGORITHM = settings.ALGORITHM

# AES Encryption Setup
# The key must be a valid Fernet key (url-safe base64-encoded 32-byte key)
fernet = Fernet(settings.ENCRYPTION_KEY.encode('utf-8'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data like TCKN using AES-256 (Fernet)"""
    return fernet.encrypt(data.encode('utf-8')).decode('utf-8')


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt AES-256 encrypted data"""
    return fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
