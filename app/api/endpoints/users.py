from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.user import User, UserCreate, UserResponse
from app.services.user_service import (
    create_user,
    get_user,
    get_users,
    update_user,
    delete_user
)
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Yeni kullanıcı oluşturur"""
    return create_user(db=db, user=user)

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Mevcut kullanıcının bilgilerini getirir"""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Belirli bir kullanıcının bilgilerini getirir"""
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return db_user

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Tüm kullanıcıları listeler"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=UserResponse)
def update_user_info(
    user_id: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Kullanıcı bilgilerini günceller"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_user = update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return db_user

@router.delete("/{user_id}")
def delete_user_info(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Kullanıcıyı siler"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_user = delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return {"message": "Kullanıcı başarıyla silindi"} 