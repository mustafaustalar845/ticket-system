
# core/dependencies.py
# Tier 2 — RBAC: Role-Based Access Control


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User, Role
from core.security import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    JWT token'ı doğrular ve aktif kullanıcıyı döner.
    Tüm korumalı endpoint'lerde kullanılır.
    """
    payload = decode_token(credentials.credentials)

    user = await User.find_one(User.username == payload.get("username"))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı veya hesap devre dışı."
        )
    return user


def require_role(*roles: Role):
    """
    Belirtilen rollere sahip olmayan kullanıcıları engeller.

    Kullanım:
        @router.get("/admin", dependencies=[Depends(require_role(Role.admin))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu işlemi yapmaya yetkiniz yok."
            )
        return current_user
    return role_checker


# Kısayollar
require_admin    = require_role(Role.admin)
require_employee = require_role(Role.admin, Role.employee)