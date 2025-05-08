from sqlalchemy.orm import Session
from models.dietitian import Dietitian
from passlib.context import CryptContext
from typing import Optional
from fastapi import HTTPException
from datetime import datetime
import logging

# Şifre işlemleri için
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """Şifreyi hash'ler"""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Şifrenin doğruluğunu kontrol eder"""
    return pwd_context.verify(plain_password, hashed_password)

def get_dietitian_by_email(db: Session, email: str):
    """Diyetisyeni email ile getirir"""
    return db.query(Dietitian).filter(Dietitian.email == email).first()

def get_dietitian_by_id(db: Session, dietitian_id: int):
    """Diyetisyeni ID ile getirir"""
    return db.query(Dietitian).filter(Dietitian.dietitian_id == dietitian_id).first()

def create_dietitian(db: Session, dietitian_data: dict):
    """Yeni diyetisyen oluşturur"""
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
    """Belirtilen diyetisyenin bilgilerini günceller"""
    db_dietitian = get_dietitian_by_id(db, dietitian_id)
    if not db_dietitian:
        return None
    
    # Şifre güncellemesi varsa hashleyelim
    if 'password' in dietitian_data and dietitian_data['password']:
        dietitian_data['hashed_password'] = get_password_hash(dietitian_data['password'])
        del dietitian_data['password']  # Ham şifreyi sil
    
    # Sadece gönderilen alanları güncelle
    for key, value in dietitian_data.items():
        if hasattr(db_dietitian, key):
            setattr(db_dietitian, key, value)
    
    try:
        db.commit()
        db.refresh(db_dietitian)
        
        # SQLAlchemy nesnesini JSON'a çevrilebilir bir sözlüğe dönüştür
        dietitian_dict = {}
        for key, value in db_dietitian.__dict__.items():
            if not key.startswith('_'):  # SQLAlchemy iç değişkenlerini atlama
                dietitian_dict[key] = value
                
        return dietitian_dict
    except Exception as e:
        db.rollback()
        raise Exception(f"Diyetisyen güncellenirken bir hata oluştu: {str(e)}")

def delete_dietitian(db: Session, dietitian_id: int):
    """Diyetisyen siler"""
    db_dietitian = get_dietitian_by_id(db, dietitian_id)
    if not db_dietitian:
        raise HTTPException(status_code=404, detail="Diyetisyen bulunamadı")
    
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
    db_dietitian = get_dietitian_by_email(db, email)
    if not db_dietitian:
        return False
    
    if not verify_password(password, db_dietitian.password):
        return False
    
    return db_dietitian