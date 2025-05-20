from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
from math import ceil
from app.db.session import get_db
from app.models.dietitian import Dietitian, DietitianCreate, DietitianResponse
from app.services.dietitian_service import (
    create_dietitian,
    get_dietitian,
    get_dietitians,
    update_dietitian,
    delete_dietitian,
    count_dietitians
)
from app.core.security import get_current_active_user, create_access_token
from app.schemas.token import TokenResponse
from app.core.config import settings
from app.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.post("/", response_model=TokenResponse)
def create_new_dietitian(dietitian: DietitianCreate, db: Session = Depends(get_db)):
    """Yeni diyetisyen oluşturur ve token döner"""
    db_dietitian = create_dietitian(db=db, dietitian_data=dietitian.model_dump())
    
    # Token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_dietitian.email, "type": "dietitian"}
    )
    
    # Dietitian dict oluştur (password hariç)
    dietitian_dict = {
        "dietitian_id": db_dietitian.dietitian_id,
        "email": db_dietitian.email,
        "name": db_dietitian.name,
        "created_at": db_dietitian.created_at,
        "experience_years": db_dietitian.experience_years,
        "specialization": db_dietitian.specialization
    }
    
    # TokenResponse objesi döndür
    return {
        "user": dietitian_dict,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/{dietitian_id}", response_model=DietitianResponse)
def read_dietitian(dietitian_id: int, db: Session = Depends(get_db)):
    """Belirli bir diyetisyenin bilgilerini getirir"""
    db_dietitian = get_dietitian(db, dietitian_id=dietitian_id)
    if db_dietitian is None:
        raise HTTPException(status_code=404, detail="Diyetisyen bulunamadı")
    return db_dietitian

@router.get("/", response_model=PaginatedResponse[DietitianResponse])
def read_dietitians(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    """Tüm diyetisyenleri sayfalı olarak listeler"""
    # Toplam diyetisyen sayısını al
    total = count_dietitians(db)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Diyetisyenleri getir
    dietitians = get_dietitians(db, skip=skip, limit=page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": dietitians,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/count")
def get_dietitians_count(db: Session = Depends(get_db)):
    """Toplam diyetisyen sayısını döndürür"""
    total = count_dietitians(db)
    return {"total": total}

@router.put("/{dietitian_id}", response_model=DietitianResponse)
def update_dietitian_info(dietitian_id: int, dietitian: DietitianCreate, db: Session = Depends(get_db)):
    """Diyetisyen bilgilerini günceller"""
    db_dietitian = update_dietitian(db, dietitian_id=dietitian_id, dietitian_data=dietitian.model_dump())
    if db_dietitian is None:
        raise HTTPException(status_code=404, detail="Diyetisyen bulunamadı")
    return db_dietitian

@router.delete("/{dietitian_id}")
def delete_dietitian_info(dietitian_id: int, db: Session = Depends(get_db)):
    """Diyetisyeni siler"""
    result = delete_dietitian(db, dietitian_id=dietitian_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Diyetisyen bulunamadı")
    return result 