from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class AIModelOutput(Base):
    __tablename__ = "ai_model_outputs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    output_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    user = relationship("User", back_populates="ai_outputs") 