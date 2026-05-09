from fastapi import APIRouter, Depends, HTTPException, status
from backend.core.security import hash_password
from backend.core.dependencies import get_current_user, require_admin
from backend.models.user import User
from backend.schemas.user_schema import RegisterRequest as UserCreate 
from backend.schemas.user_schema import UserResponse as UserOut
from pydantic import BaseModel
from beanie import PydanticObjectId

class UserRoleUpdate(BaseModel):
    role: str

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@router.get("/users", response_model=list[UserOut])
async def list_users(current_user: User = Depends(require_admin)):
    """
    Tüm kullanıcıları listeler.
    Sadece 'admin' rolündeki kullanıcılar erişebilir.
    """
    users = await User.find_all().to_list()
    return [user.to_safe_dict() for user in users]

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
):
    """
    Yeni kullanıcı oluşturur.
    """
    existing = await User.find_one(User.username == user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten alınmış."
        )

    hashed_pw = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        password_hash=hashed_pw,
        role=user_data.role,
        full_name=user_data.full_name
    )
    await new_user.insert()
    return new_user.to_safe_dict()

@router.patch("/users/{user_id}/role", response_model=UserOut)
async def update_user_role(
    user_id: str,
    role_data: UserRoleUpdate,
    current_user: User = Depends(require_admin),   
):
    """
    Kullanıcının rolünü günceller (admin / employee).
    """
    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kendi rolünüzü değiştiremezsiniz."
        )

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    user.role = role_data.role
    await user.save()
    return user.to_safe_dict()

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),   
):
    """
    Kullanıcıyı siler.
    """
    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kendi hesabınızı silemezsiniz."
        )

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    await user.delete()