from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class PostDB(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    content = Column(String)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    user = relationship("UserDB", back_populates="posts")
    comments = relationship("PostCommentDB", back_populates="post", cascade="all, delete-orphan")

class PostCommentDB(Base):
    __tablename__ = "post_comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    post = relationship("PostDB", back_populates="comments")
    user = relationship("UserDB", back_populates="comments") 