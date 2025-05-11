from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from database import Base

class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("dietitians.dietitian_id", ondelete="CASCADE"), nullable=False)
    message_content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.now)
    
    # İlişkiler - Sadece sınıf adlarını kullanarak
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("Dietitian", foreign_keys=[receiver_id], back_populates="received_messages")

# Pydantic modelleri
class MessageBase(BaseModel):
    message_content: str
    
class MessageCreate(MessageBase):
    sender_id: int
    receiver_id: int

class MessageResponse(MessageBase):
    message_id: int
    sender_id: int
    receiver_id: int
    sent_at: datetime
    
    class Config:
        from_attributes = True