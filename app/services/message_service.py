from sqlalchemy.orm import Session
from app.models.message import Message
from typing import List, Optional
from fastapi import HTTPException
import logging
from datetime import datetime

def get_message(db: Session, message_id: int):
    """Mesaj ID'sine göre mesajı getirir"""
    return db.query(Message).filter(Message.message_id == message_id).first()

def get_user_messages(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Kullanıcının tüm mesajlarını getirir (gelen ve giden)"""
    return db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(Message.sent_at.desc()).offset(skip).limit(limit).all()

def get_conversation(db: Session, user_id: int, other_id: int, skip: int = 0, limit: int = 100):
    """İki kullanıcı arasındaki konuşmayı getirir"""
    return db.query(Message).filter(
        (
            (Message.sender_id == user_id) & (Message.receiver_id == other_id)
        ) | (
            (Message.sender_id == other_id) & (Message.receiver_id == user_id)
        )
    ).order_by(Message.sent_at.desc()).offset(skip).limit(limit).all()

def create_message(db: Session, message_data: dict):
    """Yeni mesaj oluşturur"""
    db_message = Message(**message_data)
    try:
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception as e:
        db.rollback()
        logging.error(f"Mesaj oluşturulurken hata: {str(e)}")
        raise

def delete_message(db: Session, message_id: int):
    """Mesajı siler"""
    db_message = get_message(db, message_id)
    if not db_message:
        return None
    
    try:
        db.delete(db_message)
        db.commit()
        return {"message": "Mesaj başarıyla silindi"}
    except Exception as e:
        db.rollback()
        logging.error(f"Mesaj silinirken hata: {str(e)}")
        raise 