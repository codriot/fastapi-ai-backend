from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base

app = FastAPI()

# Beğeniler ve kaydedilenler için ilişki tabloları
post_likes = Table(
    "post_likes",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
)

post_saves = Table(
    "post_saves",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
)

# Gönderi tablosu
class PostDB(Base):
    __tablename__ = "posts"
    
    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    image_url = Column(String(255), nullable=True)
    
    # İlişkiler
    liked_by = relationship("User", secondary=post_likes, backref="liked_posts")
    saved_by = relationship("User", secondary=post_saves, backref="saved_posts")
    comments = relationship("PostCommentDB", back_populates="post", cascade="all, delete-orphan")

# Yorum tablosu
class PostCommentDB(Base):
    __tablename__ = "post_comments"
    
    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    likes = Column(Integer, default=0)
    
    # İlişkiler
    post = relationship("PostDB", back_populates="comments")

# Pydantic modelleri
class PostBase(BaseModel):
    user_id: int
    content: str
    
class Post(PostBase):
    post_id: str
    timestamp: datetime
    likes: int = 0
    saved_by: List[str] = []
    comments: List[str] = []
    image_url: Optional[str] = None

class PostCreate(PostBase):
    image_url: Optional[str] = None

class PostResponse(PostBase):
    post_id: int
    timestamp: datetime
    image_url: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    
    class Config:
        from_attributes = True

class PostCommentBase(BaseModel):
    post_id: str
    user_id: str
    content: str
    
class PostComment(PostCommentBase):
    comment_id: str
    timestamp: datetime
    likes: int = 0

class PostCommentCreate(PostCommentBase):
    pass

class PostCommentResponse(PostCommentBase):
    comment_id: int
    timestamp: datetime
    likes: int = 0
    
    class Config:
        from_attributes = True