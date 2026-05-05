from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(default="employee")

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
