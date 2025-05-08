from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from .config import settings

# Şifre işlemleri için
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifre doğrulama"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Şifre hashleme"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT token oluşturma"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        if isinstance(encoded_jwt, bytes):
            return encoded_jwt.decode('utf-8')
        return encoded_jwt
    except Exception as e:
        raise Exception(f"Token oluşturma hatası: {str(e)}")

def verify_token(token: str) -> dict:
    """JWT token doğrulama"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token süresi dolmuş")
    except jwt.InvalidTokenError as e:
        raise Exception(f"Geçersiz token: {str(e)}")
    except Exception as e:
        raise Exception(f"Token doğrulama hatası: {str(e)}") 