# ============================================================
# models/user.py
# Tier 3 — Secure Database: Hashed Passwords
# MongoDB için Beanie ODM (Motor async driver üzerinde çalışır)
# ============================================================

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
    password_hash: str            # Veritabanında SADECE hash saklanır, asla plaintext
    role:          Role = Role.employee
    full_name:     str
    is_active:     bool = True
    created_at:    datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"            # MongoDB koleksiyon adı

    # ── Şifre Hash'leme ─────────────────────────────────────
    # Kullanıcı oluşturulurken çağrılır.
    # bcrypt: önce rastgele salt üretir, sonra hash hesaplar.
    # Sonuç formatı: $2b$12$<22 char salt><31 char hash>
    @staticmethod
    def hash_password(plaintext: str) -> str:
        """
        Plaintext şifreyi bcrypt ile hash'ler.
        SALT_ROUNDS=12 → brute-force saldırılarını yavaşlatır.
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plaintext.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    # ── Şifre Doğrulama ─────────────────────────────────────
    # Login sırasında kullanılır.
    # bcrypt.checkpw() → sabit-zamanlı karşılaştırma yapar
    # (timing saldırılarına karşı güvenli)
    def verify_password(self, plaintext: str) -> bool:
        """
        Girilen şifreyi veritabanındaki hash ile karşılaştırır.
        Hash tek yönlüdür — hash'den orijinal şifreye ulaşılamaz.
        """
        return bcrypt.checkpw(
            plaintext.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    # ── JSON'a dönüştürürken password_hash'i gizle ──────────
    def to_safe_dict(self) -> dict:
        """API response'larında şifre hash'ini asla döndürme."""
        return {
            "id":        str(self.id),
            "username":  self.username,
            "full_name": self.full_name,
            "role":      self.role,
            "is_active": self.is_active,
        }