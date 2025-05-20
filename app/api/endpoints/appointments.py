from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from math import ceil
from app.db.base import get_db
from app.models.appointment import Appointment, AppointmentCreate, AppointmentResponse
from app.services.appointment_service import (
    create_appointment,
    get_appointment,
    get_appointments,
    update_appointment,
    delete_appointment,
    count_appointments,
    count_user_appointments,
    count_dietitian_appointments,
    get_user_appointments,
    get_dietitian_appointments
)
from app.core.security import get_current_active_user
from app.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.post("/", response_model=AppointmentResponse)
def create_new_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Yeni randevu oluşturur"""
    return create_appointment(db=db, appointment_data=appointment.dict())

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Belirli bir randevunun bilgilerini getirir"""
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    return db_appointment

@router.get("/", response_model=PaginatedResponse[AppointmentResponse])
def read_appointments(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    """Tüm randevuları sayfalı olarak listeler"""
    # Toplam randevu sayısını al
    total = count_appointments(db)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Randevuları getir
    appointments = get_appointments(db, skip=skip, limit=page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": appointments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/count")
def get_appointments_count(db: Session = Depends(get_db)):
    """Toplam randevu sayısını döndürür"""
    total = count_appointments(db)
    return {"total": total}

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment_info(
    appointment_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: Appointment = Depends(get_current_active_user)
):
    """Randevu bilgilerini günceller"""
    if current_user.appointment_id != appointment_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_appointment = update_appointment(db, appointment_id, appointment.dict())
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    return db_appointment

@router.delete("/{appointment_id}")
def delete_appointment_info(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: Appointment = Depends(get_current_active_user)
):
    """Randevuyu siler"""
    if current_user.appointment_id != appointment_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    result = delete_appointment(db, appointment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    return result

@router.get("/user", response_model=PaginatedResponse[AppointmentResponse])
def read_user_appointments(
    page: int = 1, 
    page_size: int = 10, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Kullanıcının randevularını sayfalı olarak listeler"""
    # Kullanıcı ID kontrolü
    if not hasattr(current_user, 'user_id'):
        raise HTTPException(status_code=400, detail="Bu endpoint sadece kullanıcılar için geçerlidir")
    
    # Toplam randevu sayısını al
    total = count_user_appointments(db, current_user.user_id)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Randevuları getir
    appointments = get_user_appointments(db, current_user.user_id, skip=skip, limit=page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": appointments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/dietitian", response_model=PaginatedResponse[AppointmentResponse])
def read_dietitian_appointments(
    page: int = 1, 
    page_size: int = 10, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Diyetisyenin randevularını sayfalı olarak listeler"""
    # Diyetisyen ID kontrolü
    if not hasattr(current_user, 'dietitian_id'):
        raise HTTPException(status_code=400, detail="Bu endpoint sadece diyetisyenler için geçerlidir")
    
    # Toplam randevu sayısını al
    total = count_dietitian_appointments(db, current_user.dietitian_id)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Randevuları getir
    appointments = get_dietitian_appointments(db, current_user.dietitian_id, skip=skip, limit=page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": appointments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }