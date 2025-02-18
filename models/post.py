from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import List
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
    image_url: str = None

@app.post("/posts/")
async def create_post(post: Post, image: UploadFile = File(...)):
    post_data = post.dict()  # Post verisini al
    
    # Resmi kaydet
    image_filename = image.filename
    image_content = await image.read()

    # Resmi diske kaydedebiliriz
    with open(f"uploads/{image_filename}", "wb") as f:
        f.write(image_content)

    return {"message": "Post başarıyla oluşturuldu", "post": post_data, "image_filename": image_filename}

class PostComment(BaseModel):
    comment_id: str
    post_id: str
    user_id: str
    content: str
    timestamp: datetime
    likes: int = 0
