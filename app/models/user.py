from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    DIETITIAN = "dietitian"
    ADMIN = "admin"

class UserBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: str
    name: str
    role: UserRole

class UserCreate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: str
    password: str
    name: str
    role: UserRole
    # User rolü için
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None
    # Dietitian rolü için
    experience: Optional[str] = None
    specialization: Optional[str] = None
    # Opsiyonel diğer alanlar
    gender: Optional[str] = None
    favorite_foods: Optional[List[str]] = []
    dietitian_id: Optional[str] = None

class UserResponse(UserBase):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    uid: str
    created_at: datetime

class UserDetails(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    uid: str
    age: int
    weight: float
    height: float
    goal: str
    activity_level: str

class DietitianDetails(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    uid: str
    experience: str
    specialization: str

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class Goal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    experience_years = Column(Integer, nullable=True)  # Diyetisyenler için
    specialization = Column(String(100), nullable=True)  # Diyetisyenler için
    created_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    user_appointments = relationship("Appointment", back_populates="user", foreign_keys="[Appointment.user_id]")
    dietitian_appointments = relationship("Appointment", back_populates="dietitian", foreign_keys="[Appointment.dietitian_id]")
    ai_outputs = relationship("AIModelOutput", back_populates="user")
    progress_records = relationship("ProgressTracking", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="[Message.sender_id]")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="[Message.receiver_id]")

# Özel kayıt modeli
class RegisterUser(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: str
    password: str
    name: str
    role: str
    # User rolü için
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None
    # Dietitian rolü için
    experience: Optional[str] = None
    specialization: Optional[str] = None
    # Opsiyonel diğer alanlar
    gender: Optional[str] = None
    favorite_foods: Optional[List[str]] = None
    dietitian_id: Optional[str] = None

# Firebase Firestore ile etkileşim için yardımcı fonksiyonlar
def user_to_dict(user: UserCreate) -> Dict[str, Any]:
    user_data = {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "created_at": datetime.now()
    }
    return user_data

def user_details_to_dict(user_id: str, user: UserCreate) -> Dict[str, Any]:
    details = {
        "uid": user_id,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "goal": user.goal,
        "activity_level": user.activity_level
    }
    return details

def dietitian_details_to_dict(user_id: str, user: UserCreate) -> Dict[str, Any]:
    details = {
        "uid": user_id,
        "experience": user.experience,
        "specialization": user.specialization
    }
    return details

def register_user_to_dict(user: RegisterUser) -> Dict[str, Any]:
    """Kayıt için kullanıcı verilerini dict'e dönüştürür"""
    user_data = {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "created_at": datetime.now()
    }
    return user_data

def register_user_details_to_dict(user_id: str, user: RegisterUser) -> Dict[str, Any]:
    """Kullanıcı detaylarını dict'e dönüştürür"""
    details = {
        "uid": user_id,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "goal": user.goal,
        "activity_level": user.activity_level
    }
    return details

def register_dietitian_details_to_dict(user_id: str, user: RegisterUser) -> Dict[str, Any]:
    """Diyetisyen detaylarını dict'e dönüştürür"""
    details = {
        "uid": user_id,
        "experience": user.experience,
        "specialization": user.specialization
    }
    return details