from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.nutrition import Nutrition, NutritionCreate, NutritionResponse
from app.services.nutrition_service import (
    create_nutrition,
    get_nutrition,
    get_nutritions,
    update_nutrition,
    delete_nutrition
)
from app.core.security import get_current_active_user

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

@router.get("/", response_model=List[NutritionResponse])
def read_nutritions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Tüm beslenme planlarını listeler"""
    nutritions = get_nutritions(db, skip=skip, limit=limit)
    return nutritions

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