from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.core.config import settings
from app.db.session import get_db
from app.services.user_service import authenticate_user
from app.services.dietitian_service import authenticate_dietitian

router = APIRouter()

@router.post("/")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    # Önce kullanıcı olarak dene
    user = authenticate_user(db, form_data.username, form_data.password)
    if user:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "type": "user"}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    # Kullanıcı değilse diyetisyen olarak dene
    dietitian = authenticate_dietitian(db, form_data.username, form_data.password)
    if dietitian:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": dietitian.email, "type": "dietitian"}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    ) 