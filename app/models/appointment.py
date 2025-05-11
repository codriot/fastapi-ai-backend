from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
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

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    dietitian_id = Column(Integer, ForeignKey("users.user_id"))
    appointment_date = Column(DateTime)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    user = relationship("User", back_populates="appointments", foreign_keys=[user_id])
    dietitian = relationship("User", foreign_keys=[dietitian_id])

class AppointmentBase(BaseModel):
    appointment_date: datetime
    status: AppointmentStatus
    notes: str | None = None

class AppointmentCreate(AppointmentBase):
    user_id: int
    dietitian_id: int

class AppointmentResponse(AppointmentBase):
    appointment_id: int
    user_id: int
    dietitian_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 