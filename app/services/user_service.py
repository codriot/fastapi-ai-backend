from sqlalchemy.orm import Session
from app.models.user import User, UserCreate
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

def get_user(db: Session, user_id: int):
    """Kullanıcıyı ID ile getirir"""
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Kullanıcıyı email ile getirir"""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Tüm kullanıcıları listeler"""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    """Yeni kullanıcı oluşturur"""
    # Email kontrolü
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email zaten kayıtlı")
    
    # Kullanıcı oluştur (şifre hashlenmeden)
    db_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
        age=user.age,
        gender=user.gender,
        height=user.height,
        weight=user.weight,
        goal=user.goal,
        activity_level=user.activity_level
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        logging.error(f"Kullanıcı oluşturulurken hata: {str(e)}")
        raise

def update_user(db: Session, user_id: int, user: UserCreate):
    """Kullanıcı bilgilerini günceller"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Sadece gönderilen alanları güncelle
    update_data = user.model_dump(exclude_unset=True)
    
    # Güncelleme zamanını ayarla
    update_data["updated_at"] = datetime.now()
    
    # Sadece gönderilen alanları güncelle
    for key, value in update_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        logging.error(f"Kullanıcı güncellenirken hata: {str(e)}")
        raise

def delete_user(db: Session, user_id: int):
    """Kullanıcıyı siler"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    try:
        db.delete(db_user)
        db.commit()
        return {"message": "Kullanıcı başarıyla silindi"}
    except Exception as e:
        db.rollback()
        logging.error(f"Kullanıcı silinirken hata: {str(e)}")
        raise

def authenticate_user(db: Session, email: str, password: str):
    """Kullanıcı giriş doğrulaması yapar"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    # Şifreyi doğrudan karşılaştır
    if user.password != password:
        return False
    return user

# Kullanıcı sayma fonksiyonu
def count_users(db: Session):
    """Toplam kullanıcı sayısını döner"""
    return db.query(User).count()
