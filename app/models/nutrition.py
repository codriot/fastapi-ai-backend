from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from app.db.base import Base

class Nutrition(Base):
    __tablename__ = "nutritions"

    nutrition_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    dietitian_id = Column(Integer, ForeignKey("dietitians.dietitian_id"))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    meal_plan = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    user = relationship("User", back_populates="nutrition_plans", foreign_keys=[user_id])
    dietitian = relationship("Dietitian", back_populates="nutrition_plans", foreign_keys=[dietitian_id])

class NutritionBase(BaseModel):
    title: str
    description: str
    meal_plan: str

class NutritionCreate(NutritionBase):
    user_id: int
    dietitian_id: int

class NutritionResponse(NutritionBase):
    nutrition_id: int
    user_id: int
    dietitian_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 