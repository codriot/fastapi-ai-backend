from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id"))
    receiver_id = Column(Integer, ForeignKey("users.user_id"))
    message_content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.now)

    # İlişkiler
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="received_messages", foreign_keys=[receiver_id])

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

    model_config = ConfigDict(from_attributes=True)