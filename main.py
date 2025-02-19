from fastapi import FastAPI, File, UploadFile, Form, HTTPException,Depends
from fastapi.responses import FileResponse
from firebase import verify_token
from models.post import Post, PostComment
from models.user import User
from services.post_service import add_comment, delete_comment, delete_post, save_post, update_post
from services.user_service import add_user, get_user, delete_user
from services.recipe_service import get_recipe_names_by_keyword
import os



app = FastAPI()

@app.post("/users/")
def create_user(user: User):
    """ Kullanıcı ekler ve token döndürür """
    return add_user(user)

@app.get("/users/me")
def read_user(uid: str = Depends(verify_token)):
    """ Token doğrulandıktan sonra kullanıcı bilgilerini döndür ve yeni token ver """
    return get_user(uid)

@app.delete("/users/me")
def remove_user(uid: str = Depends(verify_token)):
    """ Token doğrulandıktan sonra kullanıcıyı siler """
    return delete_user(uid)

@app.post("/comments/")
async def create_comment(comment: PostComment):
    result = add_comment(comment)
    return result

# Uploads klasörünü dışarıdan erişilebilir hale getiriyoruz
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/posts/")
async def create_post(
    post_id: str = Form(...),
    user_id: str = Form(...),
    content: str = Form(...),
    timestamp: str = Form(...),
    image: UploadFile = File(None)  # Resim isteğe bağlıdır
):
    """Yeni bir post oluşturur ve resmini yükler"""
    post = Post(
        post_id=post_id,
        user_id=user_id,
        content=content,
        timestamp=timestamp,
    )
    
    return save_post(post, image)

# Yüklenen resimleri sunucu üzerinden görüntüleyebilmek için
@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    return FileResponse(f"uploads/{filename}")

# ! şuan için bu endpoint istediğim şekilde çalışmamaktadır
# Tarif isimlerini dönen endpoint
@app.post("/get-recipe-names/")
async def get_recipe_names(
    keyword: str = Form(...)
):
    """
    Keyword'e göre tariflerin isimlerini dönen bir endpoint.
    """
    try:
        recipe_names = get_recipe_names_by_keyword(keyword)
        return {"keyword": keyword, "recipe_names": recipe_names}
    except Exception as e:
        return {"error": f"Bir hata oluştu: {str(e)}"}

@app.post("/comments/")
async def create_comment(comment: PostComment):
    """Belirtilen post'a yorum ekler"""
    return add_comment(comment)

@app.delete("/comments/{post_id}/{comment_id}")
async def remove_comment(post_id: str, comment_id: str):
    """Bir posttaki yorumu siler"""
    return delete_comment(post_id, comment_id)

@app.put("/posts/{post_id}")
async def modify_post(post_id: str, content: str):
    """Bir post'un içeriğini günceller"""
    return update_post(post_id, content)

@app.delete("/posts/{post_id}")
async def remove_post(post_id: str):
    """Bir post'u tamamen siler"""
    return delete_post(post_id)