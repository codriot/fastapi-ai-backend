from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.database import Base

class Nutrition(Base):
    __tablename__ = "nutritions"

    nutrition_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    dietitian_id = Column(Integer, ForeignKey("dietitians.dietitian_id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    user = relationship("User", back_populates="nutrition_plans")
    dietitian = relationship("Dietitian", back_populates="nutrition_plans")

class NutritionBase(BaseModel):
    title: str
    description: str
    calories: float
    protein: float
    carbs: float
    fat: float

class NutritionCreate(NutritionBase):
    user_id: int
    dietitian_id: int

class NutritionResponse(NutritionBase):
    nutrition_id: int
    user_id: int
    dietitian_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 