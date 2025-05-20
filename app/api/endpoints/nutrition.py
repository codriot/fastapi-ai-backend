from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from math import ceil
from app.db.base import get_db
from app.models.nutrition import Nutrition, NutritionCreate, NutritionResponse
from app.services.nutrition_service import (
    create_nutrition,
    get_nutrition,
    get_nutritions,
    update_nutrition,
    delete_nutrition,
    count_nutritions,
    get_user_nutritions,
    count_user_nutritions
)
from app.core.security import get_current_active_user
from app.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.post("/", response_model=NutritionResponse)
def create_new_nutrition(nutrition: NutritionCreate, db: Session = Depends(get_db)):
    """Yeni beslenme planı oluşturur"""
    return create_nutrition(db=db, nutrition_data=nutrition.dict())

@router.get("/{nutrition_id}", response_model=NutritionResponse)
def read_nutrition(nutrition_id: int, db: Session = Depends(get_db)):
    """Belirli bir beslenme planının bilgilerini getirir"""
    db_nutrition = get_nutrition(db, nutrition_id)
    if db_nutrition is None:
        raise HTTPException(status_code=404, detail="Beslenme planı bulunamadı")
    return db_nutrition

@router.get("/", response_model=PaginatedResponse[NutritionResponse])
def read_nutritions(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    """Tüm beslenme planlarını sayfalı olarak listeler"""
    # Toplam beslenme planı sayısını al
    total = count_nutritions(db)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Beslenme planlarını getir
    nutritions = get_nutritions(db, skip=skip, limit=page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": nutritions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/count")
def get_nutritions_count(db: Session = Depends(get_db)):
    """Toplam beslenme planı sayısını döndürür"""
    total = count_nutritions(db)
    return {"total": total}

@router.put("/{nutrition_id}", response_model=NutritionResponse)
def update_nutrition_info(
    nutrition_id: int,
    nutrition: NutritionCreate,
    db: Session = Depends(get_db),
    current_user: Nutrition = Depends(get_current_active_user)
):
    """Beslenme planı bilgilerini günceller"""
    if current_user.nutrition_id != nutrition_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_nutrition = update_nutrition(db, nutrition_id, nutrition.dict())
    if db_nutrition is None:
        raise HTTPException(status_code=404, detail="Beslenme planı bulunamadı")
    return db_nutrition

@router.delete("/{nutrition_id}")
def delete_nutrition_info(
    nutrition_id: int,
    db: Session = Depends(get_db),
    current_user: Nutrition = Depends(get_current_active_user)
):
    """Beslenme planını siler"""
    if current_user.nutrition_id != nutrition_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    result = delete_nutrition(db, nutrition_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Beslenme planı bulunamadı")
    return result

@router.get("/user", response_model=PaginatedResponse[NutritionResponse])
def read_user_nutritions(
    page: int = 1, 
    page_size: int = 10, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Kullanıcının beslenme planlarını sayfalı olarak listeler"""
    # Kullanıcı ID kontrolü
    if not hasattr(current_user, 'user_id'):
        raise HTTPException(status_code=400, detail="Bu endpoint sadece kullanıcılar için geçerlidir")
    
    # Toplam beslenme planı sayısını al
    total = count_user_nutritions(db, current_user.user_id)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Beslenme planlarını getir
    nutritions = get_user_nutritions(db, current_user.user_id, skip=skip, limit=page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": nutritions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }