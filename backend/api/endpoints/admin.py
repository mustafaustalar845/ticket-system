

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import hash_password
from api.dependencies import get_current_user, require_admin
from models.user import User
from schemas.user_schema import UserCreate, UserOut, UserRoleUpdate

router = APIRouter(prefix="/admin", tags=["Admin Panel"])



@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),  
):
    """
    Tüm kullanıcıları listeler.
    Sadece 'admin' rolündeki kullanıcılar erişebilir.
    Şifre hash'leri response'a dahil edilmez (UserOut şeması).
    """
    return db.query(User).all()



@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),   # ← RBAC: sadece admin
):
    """
    Yeni kullanıcı oluşturur.
    - Şifre hash_password() ile hashlenir, düz metin kaydedilmez.
    - Kullanıcı adı tekrarı kontrolü yapılır.
    """
    
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten alınmış."
        )

   
    hashed_pw = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pw,
        role=user_data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),   
):
    """
    Kullanıcının rolünü günceller (admin / employee).
    Admin kendi rolünü değiştiremez (güvenlik önlemi).
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kendi rolünüzü değiştiremezsiniz."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return user



@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),   
):
    """
    Kullanıcıyı siler.
    Admin kendi hesabını silemez.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kendi hesabınızı silemezsiniz."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    db.delete(user)
    db.commit()