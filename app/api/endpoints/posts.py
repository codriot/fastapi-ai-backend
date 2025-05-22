from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
from math import ceil
import os

from app.core.exceptions import PermissionDeniedException, NotFoundException
from app.db.base import get_db
from app.services.post_service import (
    create_post, get_post, get_posts, get_user_posts,
    update_post, delete_post, add_comment, get_comments,
    delete_comment, count_posts, count_user_posts, count_comments
)
from app.schemas.post import Post, PostCreate, PostResponse, PostComment
from app.schemas.pagination import PaginatedResponse
from app.utils.backblaze_upload import backblaze_uploader
from app.utils.get_signed_url import get_signed_url
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=PostResponse)
async def create_new_post(
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Yeni bir post oluşturur ve resmini Backblaze B2'ye yükler"""
    # Sadece normal kullanıcılar post oluşturabilir
    if not hasattr(current_user, 'user_id'):
        raise PermissionDeniedException()
    
    try:
        image_url = None
        if image:
            # Resmi Backblaze B2'ye yükle
            image_url = await backblaze_uploader.upload_file(image)
        
        # Post'u oluştur
        post = create_post(db, current_user.user_id, content, image_url)
        return post
        
    except Exception as e:
        import logging
        logging.error(f"Post oluşturma hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Post oluşturulurken bir hata oluştu: {str(e)}"
        )

@router.get("/{post_id}", response_model=Post)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Belirli bir post'u getirir"""
    # Yorumları içeren gönderiyi getir
    post = get_post(db, post_id, include_comments=True)
    if not post:
        raise NotFoundException("Post bulunamadı")
    
    # SQLAlchemy nesnesini sözlüğe dönüştür
    if isinstance(post, dict):
        post_dict = post
    else:
        post_dict = post.__dict__.copy() if hasattr(post, "__dict__") else dict(post)
    
    # _sa_instance_state anahtarını kaldır (SQLAlchemy iç kullanım)
    if "_sa_instance_state" in post_dict:
        post_dict.pop("_sa_instance_state")
    
    # Eğer resim URL'si B2'de ise geçici erişim URL'si oluştur
    if post_dict.get("image_url") and "backblazeb2.com" in post_dict["image_url"]:
        try:
            # URL'den dosya adını çıkart
            file_name = os.path.basename(post_dict["image_url"])
            signed_url = get_signed_url(file_name)
            # Orijinal URL'yi geçici URL ile değiştir
            post_dict["image_url"] = signed_url
        except Exception as e:
            # Hata durumunda orijinal URL'yi koru
            print(f"Geçici URL oluşturma hatası: {str(e)}")
    
    # Yorumları işle
    if "comments" in post_dict:
        processed_comments = []
        for comment in post_dict["comments"]:
            # Yorum SQLAlchemy nesnesini sözlüğe dönüştür
            comment_dict = comment.__dict__.copy() if hasattr(comment, "__dict__") else dict(comment)
            if "_sa_instance_state" in comment_dict:
                comment_dict.pop("_sa_instance_state")
            processed_comments.append(comment_dict)
        post_dict["comments"] = processed_comments
    else:
        post_dict["comments"] = []
    
    # Model oluşturucusu varsa kullan
    try:
        return Post.model_validate(post_dict)
    except Exception as e:
        print(f"Model doğrulama hatası: {str(e)}")
        return post_dict

@router.get("/", response_model=PaginatedResponse[Post])
async def read_posts(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Tüm post'ları sayfalı olarak getirir"""
    # Toplam kayıt sayısını al
    total = count_posts(db)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Yorumları içeren gönderileri getir
    posts = get_posts(db, skip, page_size, include_comments=True)
    
    # Resim URL'lerini işle ve yorumları içeren tam postları hazırla
    processed_posts = []
    for post in posts:
        # SQLAlchemy nesnesini sözlüğe dönüştür
        post_dict = post.__dict__.copy() if hasattr(post, "__dict__") else dict(post)
        
        # _sa_instance_state anahtarını kaldır (SQLAlchemy iç kullanım)
        if "_sa_instance_state" in post_dict:
            post_dict.pop("_sa_instance_state")
        
        # Resim URL'sini geçici URL ile değiştir
        if post_dict.get("image_url") and "backblazeb2.com" in post_dict["image_url"]:
            try:
                file_name = os.path.basename(post_dict["image_url"])
                signed_url = get_signed_url(file_name)
                post_dict["image_url"] = signed_url
            except Exception as e:
                print(f"Geçici URL oluşturma hatası: {str(e)}")
        
        # Yorumları işle ve ekle
        if "comments" in post_dict:
            processed_comments = []
            for comment in post_dict["comments"]:
                # Yorum SQLAlchemy nesnesini sözlüğe dönüştür
                comment_dict = comment.__dict__.copy() if hasattr(comment, "__dict__") else dict(comment)
                if "_sa_instance_state" in comment_dict:
                    comment_dict.pop("_sa_instance_state")
                processed_comments.append(comment_dict)
            post_dict["comments"] = processed_comments
        else:
            post_dict["comments"] = []
        
        # Model doğrulaması varsa kullan
        try:
            processed_posts.append(Post.model_validate(post_dict))
        except Exception as e:
            print(f"Model doğrulama hatası: {str(e)}")
            processed_posts.append(post_dict)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": processed_posts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/count")
async def get_posts_count(db: Session = Depends(get_db)):
    """Toplam post sayısını döndürür"""
    total = count_posts(db)
    return {"total": total}

@router.get("/user/{user_id}", response_model=PaginatedResponse[Post])
async def read_user_posts(
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Belirli bir kullanıcının post'larını sayfalı olarak getirir"""
    # Toplam kayıt sayısını al
    total = count_user_posts(db, user_id)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Yorumları içeren gönderileri getir
    posts = get_user_posts(db, user_id, skip, page_size, include_comments=True)
    
    # Resim URL'lerini işle ve yorumları içeren tam postları hazırla
    processed_posts = []
    for post in posts:
        # SQLAlchemy nesnesini sözlüğe dönüştür
        post_dict = post.__dict__.copy() if hasattr(post, "__dict__") else dict(post)
        
        # _sa_instance_state anahtarını kaldır (SQLAlchemy iç kullanım)
        if "_sa_instance_state" in post_dict:
            post_dict.pop("_sa_instance_state")
        
        # Resim URL'sini geçici URL ile değiştir
        if post_dict.get("image_url") and "backblazeb2.com" in post_dict["image_url"]:
            try:
                file_name = os.path.basename(post_dict["image_url"])
                signed_url = get_signed_url(file_name)
                post_dict["image_url"] = signed_url
            except Exception as e:
                print(f"Geçici URL oluşturma hatası: {str(e)}")
        
        # Yorumları işle ve ekle
        if "comments" in post_dict:
            processed_comments = []
            for comment in post_dict["comments"]:
                # Yorum SQLAlchemy nesnesini sözlüğe dönüştür
                comment_dict = comment.__dict__.copy() if hasattr(comment, "__dict__") else dict(comment)
                if "_sa_instance_state" in comment_dict:
                    comment_dict.pop("_sa_instance_state")
                processed_comments.append(comment_dict)
            post_dict["comments"] = processed_comments
        else:
            post_dict["comments"] = []
        
        # Model doğrulaması varsa kullan
        try:
            processed_posts.append(Post.model_validate(post_dict))
        except Exception as e:
            print(f"Model doğrulama hatası: {str(e)}")
            processed_posts.append(post_dict)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": processed_posts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.put("/{post_id}", response_model=Post)
async def update_post_content(
    post_id: int,
    post_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Post içeriğini günceller"""
    # JSON body'den content değerini al
    content = post_data.get("content")
    post = get_post(db, post_id)
    if not post:
        raise NotFoundException("Post bulunamadı")
    
    if post.user_id != current_user.user_id:
        raise PermissionDeniedException()
    
    return update_post(db, post_id, content)

@router.delete("/{post_id}")
async def remove_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Post'u siler"""
    post = get_post(db, post_id)
    if not post:
        raise NotFoundException("Post bulunamadı")
    
    if post.user_id != current_user.user_id:
        raise PermissionDeniedException()
    
    return delete_post(db, post_id)

@router.post("/{post_id}/comments")
async def create_comment(
    post_id: int,
    comment_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Post'a yorum ekler"""
    if not hasattr(current_user, 'user_id'):
        raise PermissionDeniedException()
    
    # JSON body'den content değerini al
    content = comment_data.get("content")
    return add_comment(db, post_id, current_user.user_id, content)

@router.get("/{post_id}/comments", response_model=PaginatedResponse[PostComment])
async def read_comments(
    post_id: int,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Post'un yorumlarını sayfalı olarak getirir"""
    # Toplam kayıt sayısını al
    total = count_comments(db, post_id)
    
    # Sayfa sayısını hesapla
    pages = ceil(total / page_size) if total > 0 else 0
    
    # skip değerini hesapla
    skip = (page - 1) * page_size
    
    # Kayıtları getir
    comments = get_comments(db, post_id, skip, page_size)
    
    # Sayfalanmış yanıt oluştur
    return {
        "items": comments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.delete("/comments/{comment_id}")
async def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Yorumu siler"""
    return delete_comment(db, comment_id) 