from typing import Optional
from beanie import Document
from pydantic import Field

class User(Document):
    username: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = Field(default="employee") # "admin" or "employee"

    class Settings:
        name = "users"
