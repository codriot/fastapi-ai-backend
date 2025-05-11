from sqlalchemy.orm import Session
from app.models.nutrition import Nutrition
from typing import List, Optional
from fastapi import HTTPException
import logging

def get_nutrition(db: Session, nutrition_id: int):
    """Beslenme planını ID ile getirir"""
    return db.query(Nutrition).filter(Nutrition.nutrition_id == nutrition_id).first()

def get_nutritions(db: Session, skip: int = 0, limit: int = 100):
    """Tüm beslenme planlarını listeler"""
    return db.query(Nutrition).offset(skip).limit(limit).all()

def create_nutrition(db: Session, nutrition_data: dict):
    """Yeni beslenme planı oluşturur"""
    db_nutrition = Nutrition(**nutrition_data)
    try:
        db.add(db_nutrition)
        db.commit()
        db.refresh(db_nutrition)
        return db_nutrition
    except Exception as e:
        db.rollback()
        logging.error(f"Beslenme planı oluşturulurken hata: {str(e)}")
        raise

def update_nutrition(db: Session, nutrition_id: int, nutrition_data: dict):
    """Beslenme planını günceller"""
    db_nutrition = get_nutrition(db, nutrition_id)
    if not db_nutrition:
        return None
    
    for key, value in nutrition_data.items():
        if hasattr(db_nutrition, key):
            setattr(db_nutrition, key, value)
    
    try:
        db.commit()
        db.refresh(db_nutrition)
        return db_nutrition
    except Exception as e:
        db.rollback()
        logging.error(f"Beslenme planı güncellenirken hata: {str(e)}")
        raise

def delete_nutrition(db: Session, nutrition_id: int):
    """Beslenme planını siler"""
    db_nutrition = get_nutrition(db, nutrition_id)
    if not db_nutrition:
        return None
    
    try:
        db.delete(db_nutrition)
        db.commit()
        return {"message": "Beslenme planı başarıyla silindi"}
    except Exception as e:
        db.rollback()
        logging.error(f"Beslenme planı silinirken hata: {str(e)}")
        raise 