from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.security import verify_password, get_password_hash, create_access_token
from backend.core.config import settings
from backend.models.user import User
from backend.schemas.user_schema import UserCreate, UserResponse, Token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    user = await User.find_one(User.username == user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        hashed_password=hashed_password,
        role=user_in.role
    )
    await user.insert()
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one(User.username == form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
