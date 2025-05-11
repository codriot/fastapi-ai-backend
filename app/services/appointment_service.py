from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from typing import List, Optional
from fastapi import HTTPException
import logging

def get_appointment(db: Session, appointment_id: int):
    """Randevuyu ID ile getirir"""
    return db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()

def get_appointments(db: Session, skip: int = 0, limit: int = 100):
    """Tüm randevuları listeler"""
    return db.query(Appointment).offset(skip).limit(limit).all()

def create_appointment(db: Session, appointment_data: dict):
    """Yeni randevu oluşturur"""
    db_appointment = Appointment(**appointment_data)
    try:
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        db.rollback()
        logging.error(f"Randevu oluşturulurken hata: {str(e)}")
        raise

def update_appointment(db: Session, appointment_id: int, appointment_data: dict):
    """Randevuyu günceller"""
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    
    for key, value in appointment_data.items():
        if hasattr(db_appointment, key):
            setattr(db_appointment, key, value)
    
    try:
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        db.rollback()
        logging.error(f"Randevu güncellenirken hata: {str(e)}")
        raise

def delete_appointment(db: Session, appointment_id: int):
    """Randevuyu siler"""
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    
    try:
        db.delete(db_appointment)
        db.commit()
        return {"message": "Randevu başarıyla silindi"}
    except Exception as e:
        db.rollback()
        logging.error(f"Randevu silinirken hata: {str(e)}")
        raise 