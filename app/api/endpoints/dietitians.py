from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.dietitian import Dietitian, DietitianCreate, DietitianResponse
from app.services.dietitian_service import (
    create_dietitian,
    get_dietitian,
    get_dietitians,
    update_dietitian,
    delete_dietitian
)
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=DietitianResponse)
def create_new_dietitian(dietitian: DietitianCreate, db: Session = Depends(get_db)):
    """Yeni diyetisyen oluşturur"""
    return create_dietitian(db=db, dietitian_data=dietitian.dict())

@router.get("/{dietitian_id}", response_model=DietitianResponse)
def read_dietitian(dietitian_id: int, db: Session = Depends(get_db)):
    """Belirli bir diyetisyenin bilgilerini getirir"""
    db_dietitian = get_dietitian(db, dietitian_id)
    if db_dietitian is None:
        raise HTTPException(status_code=404, detail="Diyetisyen bulunamadı")
    return db_dietitian

@router.get("/", response_model=List[DietitianResponse])
def read_dietitians(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Tüm diyetisyenleri listeler"""
    dietitians = get_dietitians(db, skip=skip, limit=limit)
    return dietitians

@router.put("/{dietitian_id}", response_model=DietitianResponse)
def update_dietitian_info(
    dietitian_id: int,
    dietitian: DietitianCreate,
    db: Session = Depends(get_db),
    current_user: Dietitian = Depends(get_current_active_user)
):
    """Diyetisyen bilgilerini günceller"""
    if current_user.dietitian_id != dietitian_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_dietitian = update_dietitian(db, dietitian_id, dietitian.dict())
    if db_dietitian is None:
        raise HTTPException(status_code=404, detail="Diyetisyen bulunamadı")
    return db_dietitian

@router.delete("/{dietitian_id}")
def delete_dietitian_info(
    dietitian_id: int,
    db: Session = Depends(get_db),
    current_user: Dietitian = Depends(get_current_active_user)
):
    """Diyetisyeni siler"""
    if current_user.dietitian_id != dietitian_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    result = delete_dietitian(db, dietitian_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Diyetisyen bulunamadı")
    return result 