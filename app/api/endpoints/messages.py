from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.message import Message, MessageCreate, MessageResponse
from app.services.message_service import (
    get_message,
    get_user_messages,
    get_conversation,
    create_message,
    delete_message
)
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=MessageResponse)
def send_message(
    message: MessageCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Yeni mesaj gönderir"""
    # Gönderenin mevcut kullanıcı olduğunu doğrula
    if current_user.user_id != message.sender_id:
        raise HTTPException(
            status_code=403, 
            detail="Sadece kendi adınıza mesaj gönderebilirsiniz"
        )
    
    return create_message(db=db, message_data=message.dict())

@router.get("/", response_model=List[MessageResponse])
def read_user_messages(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Kullanıcının tüm mesajlarını listeler (gelen ve giden)"""
    messages = get_user_messages(db, current_user.user_id, skip, limit)
    return messages

@router.get("/conversation/{other_id}", response_model=List[MessageResponse])
def read_conversation(
    other_id: int,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """İki kullanıcı arasındaki konuşmayı getirir"""
    messages = get_conversation(db, current_user.user_id, other_id, skip, limit)
    return messages

@router.get("/{message_id}", response_model=MessageResponse)
def read_message(
    message_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Belirli bir mesajın detaylarını getirir"""
    db_message = get_message(db, message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Mesaj bulunamadı")
    
    # Sadece ilgili kullanıcılar mesajı görebilir
    if db_message.sender_id != current_user.user_id and db_message.receiver_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Bu mesaja erişim izniniz yok")
    
    return db_message

@router.delete("/{message_id}")
def delete_user_message(
    message_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mesajı siler"""
    db_message = get_message(db, message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Mesaj bulunamadı")
    
    # Sadece gönderen silme yetkisine sahip
    if db_message.sender_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Sadece gönderen mesajı silebilir")
    
    result = delete_message(db, message_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Mesaj bulunamadı")
    
    return result 