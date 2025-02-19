from firebase import db
from models.post import Post, PostComment
from firebase_admin import  firestore
import os
from fastapi import UploadFile

UPLOAD_FOLDER = "uploads"  # Resimlerin kaydedileceği klasör
POSTS_COLLECTION = "post"  # Firestore koleksiyon adı

# Klasör yoksa oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_post(post: Post, image: UploadFile = None):
    """Post'u kaydeder ve resmi sunucuda saklar"""
    image_url = None  # Başlangıçta boş

    if image:
        file_extension = image.filename.split(".")[-1]
        image_filename = f"{post.post_id}.{file_extension}"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)

        # Resmi sunucuda kaydet
        with open(image_path, "wb") as img_file:
            img_file.write(image.file.read())

        # Sunucuda saklanan resmin URL’sini oluştur
        image_url = f"http://127.0.0.1:8000/{UPLOAD_FOLDER}/{image_filename}"
    
    # Postu kaydederken resim URL'sini ekleyelim
    post.image_url = image_url
    
    # Firestore'a postu kaydedelim
    db = firestore.client()
    doc_ref = db.collection(POSTS_COLLECTION).document(post.post_id)
    doc_ref.set(post.dict())

    return {"message": "Post başarıyla eklendi", "post": post.dict()}

# Yorum eklemek için servis fonksiyonu
def add_comment(comment: PostComment):
    """Bir posta yorum ekler"""
    doc_ref = db.collection("post").document(comment.post_id)
    post = doc_ref.get()
    
    if post.exists:
        post_data = post.to_dict()
        if "comments" not in post_data:
            post_data["comments"] = []
        
        # Yeni yorumu ekleyelim
        post_data["comments"].append(comment.dict())
        
        # Güncellenmiş veriyi Firestore'a kaydedelim
        doc_ref.set(post_data)
        return {"message": "Yorum başarıyla eklendi"}
    
    return {"error": "Post bulunamadı"}

def delete_comment(post_id: str, comment_id: str):
    """Belirtilen post'tan bir yorumu siler"""
    doc_ref = db.collection(POSTS_COLLECTION).document(post_id)
    post = doc_ref.get()

    if post.exists:
        post_data = post.to_dict()
        post_data["comments"] = [c for c in post_data.get("comments", []) if c["comment_id"] != comment_id]
        
        doc_ref.set(post_data)
        return {"message": "Yorum başarıyla silindi"}

    return {"error": "Post bulunamadı"}

def update_post(post_id: str, content: str):
    """Bir post'un içeriğini günceller"""
    doc_ref = db.collection(POSTS_COLLECTION).document(post_id)
    post = doc_ref.get()

    if post.exists:
        doc_ref.update({"content": content})
        return {"message": "Post başarıyla güncellendi"}

    return {"error": "Post bulunamadı"}

def delete_post(post_id: str):
    """Bir post'u siler"""
    doc_ref = db.collection(POSTS_COLLECTION).document(post_id)
    post = doc_ref.get()

    if post.exists:
        doc_ref.delete()
        return {"message": "Post başarıyla silindi"}

    return {"error": "Post bulunamadı"}