# ============================================================
# schemas/user_schema.py
# API istek/yanıt şemaları — şifre alanları dikkatli yönetilir
# ============================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from models.user import Role


class RegisterRequest(BaseModel):
    username:  str = Field(..., min_length=3, max_length=50)
    password:  str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    role:      Role = Role.employee

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Şifre en az 8 karakter olmalıdır.")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         dict


class UserResponse(BaseModel):
    id:        str
    username:  str
    full_name: str
    role:      Role
    is_active: bool