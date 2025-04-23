from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database import Base

# Yiyecekler tablosu için model
class Food(Base):
    __tablename__ = "foods"
    
    food_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    category = Column(String(50))

# Yapay zeka çıktıları için model
class AIModelOutput(Base):
    __tablename__ = "ai_model_outputs"
    
    output_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    diet_plan = Column(JSON, nullable=False)  # JSONB tipi, PostgreSQL'de JSON verileri saklar
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    
    # İlişkiler
    user = relationship("User", back_populates="ai_outputs")

# İlerleme takibi için model
class ProgressTracking(Base):
    __tablename__ = "progress_tracking"
    
    progress_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    current_weight = Column(Float)
    progress_notes = Column(Text)
    logged_at = Column(DateTime, default=datetime.now)
    
    # İlişkiler
    user = relationship("User", back_populates="progress_records")

# Randevular için model
class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    dietitian_id = Column(Integer, ForeignKey("dietitians.dietitian_id", ondelete="CASCADE"))
    date_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="planned")
    
    # İlişkiler
    user = relationship("User", back_populates="appointments")
    dietitian = relationship("Dietitian", back_populates="appointments")

# Pydantic modelleri
class FoodBase(BaseModel):
    name: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    category: Optional[str] = None

class FoodCreate(FoodBase):
    pass

class FoodResponse(FoodBase):
    food_id: int
    
    class Config:
        orm_mode = True

class AIModelOutputBase(BaseModel):
    user_id: int
    diet_plan: Dict[str, Any]
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

class AIModelOutputCreate(AIModelOutputBase):
    pass

class AIModelOutputResponse(AIModelOutputBase):
    output_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProgressTrackingBase(BaseModel):
    user_id: int
    current_weight: float
    progress_notes: Optional[str] = None

class ProgressTrackingCreate(ProgressTrackingBase):
    pass

class ProgressTrackingResponse(ProgressTrackingBase):
    progress_id: int
    logged_at: datetime
    
    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    user_id: int
    dietitian_id: int
    date_time: datetime
    status: Optional[str] = "planned"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    appointment_id: int
    
    class Config:
        orm_mode = True