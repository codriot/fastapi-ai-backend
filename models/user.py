from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class Role(str, Enum):
    USER = "user"
    DIETITIAN = "dietitian" 
    ADMIN = "admin"

class UserBase(BaseModel):
    email: str
    name: str
    role: Role

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: Role
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
    uid: str
    created_at: datetime

class UserDetails(BaseModel):
    uid: str
    age: int
    weight: float
    height: float
    goal: str
    activity_level: str

class DietitianDetails(BaseModel):
    uid: str
    experience: str
    specialization: str

class User(BaseModel):
    uid: str
    email: str
    password: str  # Güvenlik için hashlenmeli
    apple_login: Optional[str] = None
    google_login: Optional[str] = None
    gender: str
    age: int
    weight: float
    height: float
    favorite_foods: List[str]
    goal: str
    dietitian_id: Optional[str] = None
    created_at: datetime

# Özel kayıt modeli (firebase ile uyumlu)
class RegisterUser(BaseModel):
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