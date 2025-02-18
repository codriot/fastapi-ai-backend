from fastapi import FastAPI, File, UploadFile
from models.post import Post, PostComment
from models.user import User
from services.post_service import add_comment, add_post
from services.user_service import add_user, get_user, delete_user

app = FastAPI()

@app.post("/users/")
def create_user(user: User):
    return add_user(user)

@app.get("/users/{uid}")
def read_user(uid: str):
    return get_user(uid)

@app.delete("/users/{uid}")
def remove_user(uid: str):
    return delete_user(uid)

@app.post("/posts/")
async def create_post(post: Post, image: UploadFile = File(...)):
    result = add_post(post, image)
    return result

@app.post("/comments/")
async def create_comment(comment: PostComment):
    result = add_comment(comment)
    return result
