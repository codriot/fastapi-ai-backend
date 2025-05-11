from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, Optional
from database import Base

class Dietitian(Base):
    __tablename__ = "dietitians"

    dietitian_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    experience_years = Column(Integer)
    specialization = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

    # İlişkiler - Basit sınıf adları kullanarak
    appointments = relationship("Appointment", back_populates="dietitian")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")

# Pydantic modelleri
class DietitianBase(BaseModel):
    name: str
    email: str
    experience_years: Optional[int] = None
    specialization: Optional[str] = None

class DietitianCreate(DietitianBase):
    password: str

class DietitianResponse(DietitianBase):
    dietitian_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 için yeni syntax

def dietitian_to_dict(dietitian: DietitianCreate) -> Dict[str, Any]:
    """Diyetisyen kayıt verilerini dict'e dönüştürür"""
    dietitian_data = {
        "email": dietitian.email,
        "name": dietitian.name,
        "role": "dietitian",
        "experience": dietitian.experience_years,
        "specialization": dietitian.specialization,
        "created_at": datetime.now()
    }
    return dietitian_data