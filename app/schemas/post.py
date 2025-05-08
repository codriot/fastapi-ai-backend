from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PostBase(BaseModel):
    content: str
    image_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostCommentBase(BaseModel):
    content: str

class PostCommentCreate(PostCommentBase):
    pass

class PostComment(PostCommentBase):
    comment_id: int
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Post(PostBase):
    post_id: int
    user_id: int
    created_at: datetime
    comments: List[PostComment] = []

    class Config:
        from_attributes = True

class PostResponse(Post):
    pass 