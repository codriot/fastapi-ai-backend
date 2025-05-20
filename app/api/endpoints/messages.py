from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from math import ceil
from app.db.base import get_db
from app.models.message import Message, MessageCreate, MessageResponse
from app.services.message_service import (
    get_message,
    get_user_messages,
    get_conversation,
    create_message,
    delete_message,
    count_user_messages,
    count_conversation
)
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.pagination import PaginatedResponse

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

@router.get("/", response_model=PaginatedResponse[MessageResponse])
def read_user_messages(
    page: int = 1, 
    page_size: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Kullanıcının tüm mesajlarını sayfalı olarak listeler (gelen ve giden)"""
    # Toplam mesaj sayısını al
    total = count_user_messages(db, current_user.user_id)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Mesajları getir
    messages = get_user_messages(db, current_user.user_id, skip, page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": messages,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/count")
def get_messages_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Kullanıcının toplam mesaj sayısını döndürür"""
    total = count_user_messages(db, current_user.user_id)
    return {"total": total}

@router.get("/conversation/{other_id}", response_model=PaginatedResponse[MessageResponse])
def read_conversation(
    other_id: int,
    page: int = 1, 
    page_size: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """İki kullanıcı arasındaki konuşmayı sayfalı olarak getirir"""
    # Toplam mesaj sayısını al
    total = count_conversation(db, current_user.user_id, other_id)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Mesajları getir
    messages = get_conversation(db, current_user.user_id, other_id, skip, page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": messages,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

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