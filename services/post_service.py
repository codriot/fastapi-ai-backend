from sqlalchemy.orm import Session
from models.post import PostDB, PostCommentDB, Post, PostComment
from fastapi import HTTPException, UploadFile, status
import logging
import os
import shutil
from datetime import datetime
from typing import List, Optional

UPLOAD_FOLDER = "uploads"  # Resimlerin kaydedileceği klasör

# Klasör yoksa oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_uploaded_file(upload_file: UploadFile, user_id: int, post_id: int) -> str:
    """Yüklenen dosyayı kaydeder ve dosya yolunu döndürür"""
    if not upload_file:
        return None
    
    # Uploads klasörünü oluştur
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Dosya adını oluştur: user_id_post_id_filename
    filename = f"{user_id}_{post_id}_{upload_file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    # Dosyayı kaydet
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        logging.error(f"Dosya kaydedilirken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dosya kaydedilemedi"
        )
    
    return file_path

def create_post(db: Session, user_id: int, content: str, image: Optional[UploadFile] = None):
    """Yeni bir gönderi oluşturur"""
    # İçerik kontrolü
    if not content or content.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Gönderi içeriği boş olamaz"
        )
    
    # Gönderi oluştur
    db_post = PostDB(
        user_id=user_id,
        content=content,
        timestamp=datetime.now()
    )
    
    try:
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        # Eğer resim varsa kaydet ve bağlantıyı güncelle
        if image:
            file_path = save_uploaded_file(image, user_id, db_post.post_id)
            db_post.image_url = file_path
            db.commit()
            db.refresh(db_post)
        
        return db_post
    except Exception as e:
        db.rollback()
        logging.error(f"Gönderi oluşturulurken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gönderi oluşturulurken bir hata oluştu: {str(e)}"
        )

def get_post(db: Session, post_id: int):
    """Gönderiyi ID ile getirir"""
    post = db.query(PostDB).filter(PostDB.post_id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gönderi bulunamadı"
        )
    return post

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    """Tüm gönderileri getirir"""
    return db.query(PostDB).order_by(PostDB.timestamp.desc()).offset(skip).limit(limit).all()

def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Belirli bir kullanıcının gönderilerini getirir"""
    posts = db.query(PostDB).filter(PostDB.user_id == user_id).order_by(PostDB.timestamp.desc()).offset(skip).limit(limit).all()
    if not posts:
        return []  # Boş liste dönüyoruz, hata fırlatmak yerine
    return posts

def update_post(db: Session, post_id: int, content: str):
    """Gönderi içeriğini günceller"""
    if not content or content.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gönderi içeriği boş olamaz"
        )
        
    db_post = get_post(db, post_id)  # Burada get_post içinde 404 kontrolü yapılıyor
    
    db_post.content = content
    
    try:
        db.commit()
        db.refresh(db_post)
        return db_post
    except Exception as e:
        db.rollback()
        logging.error(f"Gönderi güncellenirken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gönderi güncellenirken bir hata oluştu: {str(e)}"
        )

def delete_post(db: Session, post_id: int):
    """Gönderiyi siler"""
    db_post = get_post(db, post_id)  # Burada get_post içinde 404 kontrolü yapılıyor
    
    try:
        # Önce, gönderi ile ilişkili resim varsa silinmeli
        if db_post.image_url and os.path.exists(db_post.image_url):
            os.remove(db_post.image_url)
        
        db.delete(db_post)
        db.commit()
        return {"message": "Gönderi başarıyla silindi"}
    except Exception as e:
        db.rollback()
        logging.error(f"Gönderi silinirken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gönderi silinirken bir hata oluştu: {str(e)}"
        )

def add_comment(db: Session, post_id: int, user_id: int, content: str):
    """Gönderiye yorum ekler"""
    # İçerik kontrolü
    if not content or content.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yorum içeriği boş olamaz"
        )
        
    # Gönderi kontrolü
    db_post = get_post(db, post_id)  # Burada get_post içinde 404 kontrolü yapılıyor
    
    # Yorum oluştur
    db_comment = PostCommentDB(
        post_id=post_id,
        user_id=user_id,
        content=content,
        timestamp=datetime.now()
    )
    
    try:
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except Exception as e:
        db.rollback()
        logging.error(f"Yorum eklenirken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Yorum eklenirken bir hata oluştu: {str(e)}"
        )

def get_comments(db: Session, post_id: int, skip: int = 0, limit: int = 100):
    """Gönderinin yorumlarını getirir"""
    # Önce gönderi var mı kontrol et
    get_post(db, post_id)  # Burada get_post içinde 404 kontrolü yapılıyor
    
    comments = db.query(PostCommentDB).filter(PostCommentDB.post_id == post_id).order_by(PostCommentDB.timestamp.desc()).offset(skip).limit(limit).all()
    return comments

def delete_comment(db: Session, comment_id: int):
    """Yorumu siler"""
    db_comment = db.query(PostCommentDB).filter(PostCommentDB.comment_id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yorum bulunamadı"
        )
    
    try:
        db.delete(db_comment)
        db.commit()
        return {"message": "Yorum başarıyla silindi"}
    except Exception as e:
        db.rollback()
        logging.error(f"Yorum silinirken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Yorum silinirken bir hata oluştu: {str(e)}"
        )