# ...existing code...
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal
from app.db import get_db





from app.models.users import User

from app.core.security import hash_password, verify_password

from app.schemas.users import UserUpdate, UserOut


router = APIRouter(prefix="/users", tags=["Users"])


# Kullanıcıları Listele
@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# Tek Kullanıcı Detayı
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Kullanıcı Güncelleme
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.username:
        user.username = data.username

    if data.email:
        user.email = data.email

    if data.name is not None:
        user.name = data.name

    if data.password:
        user.hashed_password = hash_password(data.password)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DB constraint error")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return user


# Kullanıcı Silme
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.delete(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DB constraint error")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return
