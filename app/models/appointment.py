from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from app.db.base import Base
import enum

class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    dietitian_id = Column(Integer, ForeignKey("dietitians.dietitian_id"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="pending")

    # İlişkiler
    user = relationship("User", back_populates="user_appointments", foreign_keys=[user_id])
    dietitian = relationship("Dietitian", back_populates="dietitian_appointments", foreign_keys=[dietitian_id])

class AppointmentBase(BaseModel):
    appointment_date: datetime
    status: str = "pending"

class AppointmentCreate(AppointmentBase):
    user_id: int
    dietitian_id: int

class AppointmentResponse(AppointmentBase):
    appointment_id: int
    user_id: int
    dietitian_id: int

    model_config = ConfigDict(from_attributes=True) 