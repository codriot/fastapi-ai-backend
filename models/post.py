from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()



class Post(BaseModel):
    post_id: str
    user_id: str
    content: str
    timestamp: datetime
    likes: int = 0
    saved_by: List[str] = []
    comments: List[str] = []
    image_url: Optional[str] = None  # Resim URL'si

class PostComment(BaseModel):
    comment_id: str
    post_id: str
    user_id: str
    content: str
    timestamp: datetime
    likes: int = 0