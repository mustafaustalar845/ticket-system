
# models/user.py
# Tier 3 — Secure Database: Hashed Passwords


from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum
import bcrypt


class Role(str, Enum):
    admin    = "admin"
    employee = "employee"


class User(Document):
    username:      str
    password_hash: str           
    role:          Role = Role.employee
    full_name:     str
    is_active:     bool = True
    created_at:    datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"            
    @staticmethod
    def hash_password(plaintext: str) -> str:
        """
        Plaintext hashes the password using bcrypt.
        SALT_ROUNDS=12 → brute-force decrease thes attack.
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plaintext.encode("utf-8"), salt)
        return hashed.decode("utf-8")

   
    def verify_password(self, plaintext: str) -> bool:
        """
        Girilen şifreyi veritabanındaki hash ile karşılaştırır.
        Hash tek yönlüdür — hash'den orijinal şifreye ulaşılamaz.
        """
        return bcrypt.checkpw(
            plaintext.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    
    def to_safe_dict(self) -> dict:
        """Never return the password hash in API responses.."""
        return {
            "id":        str(self.id),
            "username":  self.username,
            "full_name": self.full_name,
            "role":      self.role,
            "is_active": self.is_active,
        }