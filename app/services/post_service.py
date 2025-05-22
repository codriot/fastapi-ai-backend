from sqlalchemy.orm import Session
from app.models.post import PostDB, PostCommentDB
from app.schemas.post import Post, PostComment
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

def create_post(db: Session, user_id: int, content: str, image_url: str = None) -> Post:
    """
    Yeni bir post oluşturur
    
    Args:
        db (Session): Veritabanı oturumu
        user_id (int): Kullanıcı ID'si
        content (str): Post içeriği
        image_url (str, optional): Backblaze B2'deki resim URL'i
        
    Returns:
        Post: Oluşturulan post
    """
    db_post = PostDB(
        user_id=user_id,
        content=content,
        image_url=image_url,
        timestamp=datetime.utcnow()
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Pydantic modelini oluştur
    try:
        return Post.model_validate(db_post)
    except Exception as e:
        logging.error(f"Model dönüştürme hatası: {str(e)}")
        # Hatayı göster ve doğrudan veritabanı nesnesini dön
        return db_post

def get_post(db: Session, post_id: int, include_comments: bool = True):
    """
    Gönderiyi ID ile getirir
    
    Args:
        db (Session): Veritabanı oturumu
        post_id (int): Gönderi ID'si
        include_comments (bool): Yorumları da getirip getirmeyeceği
        
    Returns:
        PostDB: Gönderi nesnesi
    """
    # Yorumları da getirmek için SQLAlchemy options kullanıyoruz
    query = db.query(PostDB).filter(PostDB.post_id == post_id)
    
    # Sonucu al
    post = query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gönderi bulunamadı"
        )
      # Yorumları ekle
    if include_comments:
        comments = get_comments(db, post_id)
        
        # ORM nesnesini sözlüğe çevir ve yorumları ekle
        if isinstance(post, dict):
            post['comments'] = comments
            return post
        else:
            # SQLAlchemy nesnesini sözlük olarak kopyala
            post_dict = {column.name: getattr(post, column.name)
                       for column in post.__table__.columns}
            post_dict['comments'] = comments
            return post_dict
        
    return post

def get_posts(db: Session, skip: int = 0, limit: int = 100, include_comments: bool = True):
    """
    Tüm gönderileri getirir
    
    Args:
        db (Session): Veritabanı oturumu
        skip (int): Atlanacak kayıt sayısı
        limit (int): Getirilecek kayıt sayısı
        include_comments (bool): Yorumları da getirip getirmeyeceği
        
    Returns:
        List[Dict]: Gönderi listesi (sözlük olarak)
    """
    posts = db.query(PostDB).order_by(PostDB.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Yorumları ekle
    if include_comments:
        result_posts = []
        for post in posts:
            comments = get_comments(db, post.post_id)
            # SQLAlchemy nesnesini sözlük olarak kopyala
            post_dict = {column.name: getattr(post, column.name) 
                        for column in post.__table__.columns}
            post_dict['comments'] = comments
            result_posts.append(post_dict)
        return result_posts
    
    return posts

def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 100, include_comments: bool = True):
    """
    Belirli bir kullanıcının gönderilerini getirir
    
    Args:
        db (Session): Veritabanı oturumu
        user_id (int): Kullanıcı ID'si
        skip (int): Atlanacak kayıt sayısı
        limit (int): Getirilecek kayıt sayısı
        include_comments (bool): Yorumları da getirip getirmeyeceği
        
    Returns:
        List[Dict]: Gönderi listesi (sözlük olarak)
    """
    posts = db.query(PostDB).filter(PostDB.user_id == user_id).order_by(PostDB.timestamp.desc()).offset(skip).limit(limit).all()
    if not posts:
        return []  # Boş liste dönüyoruz, hata fırlatmak yerine
    
    # Yorumları ekle
    if include_comments:
        result_posts = []
        for post in posts:
            comments = get_comments(db, post.post_id)
            # SQLAlchemy nesnesini sözlük olarak kopyala
            post_dict = {column.name: getattr(post, column.name) 
                        for column in post.__table__.columns}
            post_dict['comments'] = comments
            result_posts.append(post_dict)
        return result_posts
    
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
    # Önce gönderi var mı doğrudan kontrol et (get_post çağırmadan)
    post = db.query(PostDB).filter(PostDB.post_id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gönderi bulunamadı"
        )
    
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

# Sayma fonksiyonları

def count_posts(db: Session):
    """Toplam gönderi sayısını döner"""
    return db.query(PostDB).count()

def count_user_posts(db: Session, user_id: int):
    """Belirli bir kullanıcının gönderi sayısını döner"""
    return db.query(PostDB).filter(PostDB.user_id == user_id).count()

def count_comments(db: Session, post_id: int):
    """Belirli bir gönderinin yorum sayısını döner"""
    return db.query(PostCommentDB).filter(PostCommentDB.post_id == post_id).count()