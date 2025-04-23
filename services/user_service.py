from sqlalchemy.orm import Session
from models.user import User
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

def get_user_by_email(db: Session, email: str):
    """Kullanıcıyı email ile getirir"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Kullanıcıyı ID ile getirir"""
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, user_data: dict):
    """Yeni kullanıcı oluşturur"""
    # Şifreyi hash'le
    hashed_password = get_password_hash(user_data.get("password"))
    
    # Kullanıcı oluştur
    db_user = User(
        name=user_data.get("name"),
        email=user_data.get("email"),
        password=hashed_password,
        age=user_data.get("age"),
        gender=user_data.get("gender"),
        height=user_data.get("height"),
        weight=user_data.get("weight"),
        goal=user_data.get("goal"),
        activity_level=user_data.get("activity_level"),
        auth_provider=user_data.get("auth_provider", "email"),
        provider_id=user_data.get("provider_id")
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

def update_user(db: Session, user_id: int, user_data: dict):
    """Belirtilen kullanıcının bilgilerini günceller"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Şifre güncellemesi varsa hashleyelim
    if 'password' in user_data and user_data['password']:
        user_data['hashed_password'] = get_password_hash(user_data['password'])
        del user_data['password']  # Ham şifreyi sil
    
    # Sadece gönderilen alanları güncelle
    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        
        # SQLAlchemy nesnesini JSON'a çevrilebilir bir sözlüğe dönüştür
        user_dict = {}
        for key, value in db_user.__dict__.items():
            # SQLAlchemy'nin iç değişkenlerini atlama (_sa_ ile başlayanlar)
            if not key.startswith('_'):
                user_dict[key] = value
                
        return user_dict
    except Exception as e:
        db.rollback()
        raise Exception(f"Kullanıcı güncellenirken bir hata oluştu: {str(e)}")

def delete_user(db: Session, user_id: int):
    """Kullanıcıyı siler"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
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
    db_user = get_user_by_email(db, email)
    if not db_user:
        return False
    
    if not verify_password(password, db_user.password):
        return False
    
    return db_user
