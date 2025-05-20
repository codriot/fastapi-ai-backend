from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import timedelta
from math import ceil
from app.db.base import get_db
from app.models.user import User, UserCreate, UserResponse
from app.services.user_service import (
    create_user,
    get_user,
    get_users,
    update_user,
    delete_user,
    count_users
)
from app.core.security import get_current_active_user, create_access_token
from app.schemas.token import TokenResponse
from app.core.config import settings
from app.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.post("/", response_model=TokenResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Yeni kullanıcı oluşturur ve token döner"""
    db_user = create_user(db=db, user=user)
    
    # Token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "type": "user"}
    )
    
    # User dict oluştur (password hariç)
    user_dict = {
        "user_id": db_user.user_id,
        "email": db_user.email,
        "name": db_user.name,
        "created_at": db_user.created_at,
        "age": db_user.age,
        "gender": db_user.gender,
        "height": db_user.height,
        "weight": db_user.weight,
        "goal": db_user.goal,
        "activity_level": db_user.activity_level
    }
    
    # TokenResponse objesi döndür
    return {
        "user": user_dict,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Mevcut kullanıcının bilgilerini getirir"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mevcut kullanıcının bilgilerini günceller"""
    db_user = update_user(db, current_user.user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Belirli bir kullanıcının bilgilerini getirir"""
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return db_user

@router.get("/", response_model=PaginatedResponse[UserResponse])
def read_users(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    """Tüm kullanıcıları sayfalı olarak listeler"""
    # Toplam kullanıcı sayısını al
    total = count_users(db)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Kullanıcıları getir
    users = get_users(db, skip=skip, limit=page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/count")
def get_users_count(db: Session = Depends(get_db)):
    """Toplam kullanıcı sayısını döndürür"""
    total = count_users(db)
    return {"total": total}

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