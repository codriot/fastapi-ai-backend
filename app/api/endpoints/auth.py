from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.config import settings
from app.core.security import create_access_token
from app.db.base import get_db
from app.services.user_service import authenticate_user
from app.services.dietitian_service import authenticate_dietitian
from app.schemas.token import Token

router = APIRouter(tags=["Kimlik Doğrulama"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Kullanıcı girişi ve token oluşturma"""
    # Önce kullanıcı olarak kontrol et
    user = authenticate_user(db, form_data.username, form_data.password)
    role = "user"
    
    # Kullanıcı bulunamadıysa diyetisyen olarak kontrol et
    if not user:
        user = authenticate_dietitian(db, form_data.username, form_data.password)
        role = "dietitian"
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yanlış kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kullanıcı ID'sini ve rolünü tokena ekle
    user_id = user.user_id if role == "user" else user.dietitian_id
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "role": role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 