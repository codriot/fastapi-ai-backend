from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship

class Dietitian(Base):
    __tablename__ = "dietitians"

    dietitian_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True)
    password = Column(String(255), nullable=False)
    experience_years = Column(Integer, nullable=True)
    specialization = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    dietitian_appointments = relationship("Appointment", back_populates="dietitian")
    nutrition_plans = relationship("Nutrition", back_populates="dietitian")

# Pydantic şemaları
class DietitianBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: str
    name: str

class DietitianCreate(DietitianBase):
    password: str
    experience_years: Optional[int] = None
    specialization: Optional[str] = None

class DietitianResponse(DietitianBase):
    dietitian_id: int
    created_at: datetime
    experience_years: Optional[int] = None
    specialization: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Yardımcı fonksiyonlar
def dietitian_to_dict(dietitian: DietitianCreate) -> Dict[str, Any]:
    dietitian_data = {
        "email": dietitian.email,
        "name": dietitian.name,
        "password": dietitian.password,
        "created_at": datetime.now()
    }
    return dietitian_data

def dietitian_details_to_dict(dietitian_id: int, dietitian: DietitianCreate) -> Dict[str, Any]:
    details = {
        "dietitian_id": dietitian_id,
        "email": dietitian.email,
        "password": dietitian.password
    }
    return details 