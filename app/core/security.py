from datetime import datetime, timedelta
from typing import Optional, Any, Union
import jwt
from passlib.context import CryptContext
from .config import settings
from jose import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User

# Şifre işlemleri için
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 şeması
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifre doğrulama"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Şifre hashleme"""
    return pwd_context.hash(password)

def create_access_token(
    data: dict,
    expires_delta: Union[timedelta, None] = None
) -> str:
    """JWT token oluşturma"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """JWT token doğrulama"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token süresi dolmuş",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Geçersiz token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Mevcut kullanıcıyı getirir"""
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        user_type: str = payload.get("type")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz kimlik bilgileri",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user_type == "user":
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Kullanıcı bulunamadı",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user
        elif user_type == "dietitian":
            from app.models.dietitian import Dietitian
            dietitian = db.query(Dietitian).filter(Dietitian.email == email).first()
            if dietitian is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Diyetisyen bulunamadı",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return dietitian
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz kullanıcı tipi",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Kimlik doğrulama hatası: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Aktif kullanıcıyı getirir"""
    if not current_user:
        raise HTTPException(status_code=400, detail="Kullanıcı aktif değil")
    return current_user 