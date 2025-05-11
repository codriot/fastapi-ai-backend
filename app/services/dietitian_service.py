from sqlalchemy.orm import Session
from app.models.dietitian import Dietitian
from passlib.context import CryptContext
from typing import List, Optional
from fastapi import HTTPException
from datetime import datetime
import logging

# Şifre işlemleri için
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Şifreyi hash'ler"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifrenin doğruluğunu kontrol eder"""
    return pwd_context.verify(plain_password, hashed_password)

def get_dietitian(db: Session, dietitian_id: int):
    """Diyetisyeni ID ile getirir"""
    return db.query(Dietitian).filter(Dietitian.dietitian_id == dietitian_id).first()

def get_dietitian_by_email(db: Session, email: str):
    """Diyetisyeni email ile getirir"""
    return db.query(Dietitian).filter(Dietitian.email == email).first()

def get_dietitians(db: Session, skip: int = 0, limit: int = 100):
    """Tüm diyetisyenleri listeler"""
    return db.query(Dietitian).offset(skip).limit(limit).all()

def create_dietitian(db: Session, dietitian_data: dict):
    """Yeni diyetisyen oluşturur"""
    # Email kontrolü
    db_dietitian = get_dietitian_by_email(db, email=dietitian_data.get("email"))
    if db_dietitian:
        raise HTTPException(status_code=400, detail="Email zaten kayıtlı")
    
    # Şifreyi hash'le
    hashed_password = get_password_hash(dietitian_data.get("password"))
    
    # Diyetisyen oluştur
    db_dietitian = Dietitian(
        name=dietitian_data.get("name"),
        email=dietitian_data.get("email"),
        password=hashed_password,
        experience_years=dietitian_data.get("experience_years"),
        specialization=dietitian_data.get("specialization")
    )
    
    try:
        db.add(db_dietitian)
        db.commit()
        db.refresh(db_dietitian)
        return db_dietitian
    except Exception as e:
        db.rollback()
        logging.error(f"Diyetisyen oluşturulurken hata: {str(e)}")
        raise

def update_dietitian(db: Session, dietitian_id: int, dietitian_data: dict):
    """Diyetisyen bilgilerini günceller"""
    db_dietitian = get_dietitian(db, dietitian_id)
    if not db_dietitian:
        return None
    
    # Şifre güncellemesi varsa hashleyelim
    if 'password' in dietitian_data and dietitian_data['password']:
        dietitian_data['password'] = get_password_hash(dietitian_data['password'])
    
    # Sadece gönderilen alanları güncelle
    for key, value in dietitian_data.items():
        if hasattr(db_dietitian, key):
            setattr(db_dietitian, key, value)
    
    try:
        db.commit()
        db.refresh(db_dietitian)
        return db_dietitian
    except Exception as e:
        db.rollback()
        logging.error(f"Diyetisyen güncellenirken hata: {str(e)}")
        raise

def delete_dietitian(db: Session, dietitian_id: int):
    """Diyetisyeni siler"""
    db_dietitian = get_dietitian(db, dietitian_id)
    if not db_dietitian:
        return None
    
    try:
        db.delete(db_dietitian)
        db.commit()
        return {"message": "Diyetisyen başarıyla silindi"}
    except Exception as e:
        db.rollback()
        logging.error(f"Diyetisyen silinirken hata: {str(e)}")
        raise

def authenticate_dietitian(db: Session, email: str, password: str):
    """Diyetisyen giriş doğrulaması yapar"""
    dietitian = get_dietitian_by_email(db, email)
    if not dietitian:
        return False
    if not verify_password(password, dietitian.password):
        return False
    return dietitian 