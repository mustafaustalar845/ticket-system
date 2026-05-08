
# api/auth.py


from fastapi import APIRouter, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.user import User
from schemas.user_schema import LoginRequest, RegisterRequest, TokenResponse
from core.security import hash_password, verify_password, create_access_token

router  = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


# ── POST /api/auth/login ───────────────────────────────────
@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/15minutes")   
async def login(request: Request, body: LoginRequest):
    """
    Güvenli login akışı:
      1. Kullanıcıyı veritabanında bul
      2. bcrypt ile şifreyi doğrula
      3. JWT token üret ve döndür

    GÜVENLİK: Kullanıcı bulunamasa da şifre yanlış olsa da
    AYNI hata mesajı döndürülür — hangi bilginin yanlış
    olduğu ifşa edilmez.
    """
    user = await User.find_one(User.username == body.username.lower().strip())

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kullanıcı adı veya şifre."
        )

    
    if not verify_password(body.password, user.password_hash):
        print(f"[AUTH] Başarısız giriş: {body.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kullanıcı adı veya şifre."
        )

    
    token = create_access_token({
        "user_id":  str(user.id),
        "username": user.username,
        "role":     user.role,
        "full_name": user.full_name,
    })

    print(f"[AUTH] Başarılı giriş: {user.username} ({user.role})")

    return TokenResponse(
        access_token=token,
        user=user.to_safe_dict()
    )


# ── POST /api/auth/register ────────────────────────────────
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """Yeni kullanıcı oluşturur. Şifre otomatik hash'lenir."""

    existing = await User.find_one(User.username == body.username.lower())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu kullanıcı adı zaten kullanılıyor."
        )

    
    new_user = User(
        username=body.username.lower().strip(),
        password_hash=hash_password(body.password),
        full_name=body.full_name.strip(),
        role=body.role,
    )
    await new_user.insert()

    return {"message": "Kullanıcı başarıyla oluşturuldu.", "user": new_user.to_safe_dict()}