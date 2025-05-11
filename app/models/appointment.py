from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.database import Base
import enum

class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    dietitian_id = Column(Integer, ForeignKey("dietitians.dietitian_id", ondelete="CASCADE"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    user = relationship("User", back_populates="appointments")
    dietitian = relationship("Dietitian", back_populates="appointments")

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