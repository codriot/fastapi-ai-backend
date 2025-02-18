from firebase import db
from models.post import Post, PostComment
from datetime import datetime
from firebase_admin import credentials, initialize_app, storage

# Fotoğrafı Firebase Storage'a yükleme fonksiyonu
def upload_image_to_firestore(image, post_id: str) -> str:
    image_filename = f"images/{post_id}.jpg"
    
    # Fotoğrafı geçici olarak yerel dosyaya kaydedelim
    with open(image_filename, "wb") as f:
        f.write(image.file.read())
    
    # Firebase Storage'a yükleyelim
    bucket = storage.bucket()
    blob = bucket.blob(f"post_images/{post_id}.jpg")
    blob.upload_from_filename(image_filename)

    # Dosyanın URL'sini döndürelim
    return blob.public_url

# Post eklemek için servis fonksiyonu
def add_post(post: Post, image) -> dict:
    # Fotoğrafı Firebase Storage'a yükle
    image_url = upload_image_to_firestore(image, post.post_id)
    
    # Firestore'a postu kaydedelim
    from firebase_admin import firestore
    db = firestore.client()
    doc_ref = db.collection("posts").document(post.post_id)
    post_dict = post.dict()
    post_dict['image_url'] = image_url  # Fotoğraf URL'sini ekleyelim
    doc_ref.set(post_dict)

    return {"message": "Post başarıyla oluşturuldu", "image_url": image_url}

# Yorum eklemek için servis fonksiyonu
def add_comment(comment: PostComment) -> dict:
    from firebase_admin import firestore
    db = firestore.client()
    doc_ref = db.collection("posts").document(comment.post_id)
    post = doc_ref.get()

    if post.exists:
        post_data = post.to_dict()
        post_data["comments"].append(comment.dict())
        doc_ref.set(post_data)
        return {"message": "Yorum başarıyla eklendi"}
    
    return {"error": "Post bulunamadı"}