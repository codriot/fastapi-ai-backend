from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    email = Column(String(150), unique=True, index=True)
    password = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    goal = Column(String(100), nullable=True)
    activity_level = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    user_appointments = relationship("Appointment", back_populates="user", foreign_keys="[Appointment.user_id]")
    ai_outputs = relationship("AIModelOutput", back_populates="user")
    progress_records = relationship("ProgressTracking", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="[Message.sender_id]")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="[Message.receiver_id]")
    nutrition_plans = relationship("Nutrition", back_populates="user", foreign_keys="[Nutrition.user_id]")

# Pydantic şemaları
class UserBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: str
    name: Optional[str] = None

class UserCreate(UserBase):
    email: str
    password: str
    name: Optional[str] = None  # <-- ZORUNLU DEĞİL
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RegisterUser(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: str
    password: str
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None

# Yardımcı fonksiyonlar
def user_to_dict(user: UserCreate) -> Dict[str, Any]:
    user_data = {
        "email": user.email,
        "name": user.name,
        "password": user.password,
        "created_at": datetime.now()
    }
    return user_data

def user_details_to_dict(user_id: str, user: UserCreate) -> Dict[str, Any]:
    details = {
        "user_id": user_id,
        "email": user.email,
        "password": user.password
    }
    return details

def register_user_to_dict(user: RegisterUser) -> Dict[str, Any]:
    user_data = {
        "email": user.email,
        "name": user.name,  # name artık None olabilir, veritabanında NULL olarak kaydolacak
        "password": user.password,
        "created_at": datetime.now()
    }
    return user_data

def register_user_details_to_dict(user_id: str, user: RegisterUser) -> Dict[str, Any]:
    details = {
        "uid": user_id,
        "email": user.email,
        "password": user.password
    }
    return details