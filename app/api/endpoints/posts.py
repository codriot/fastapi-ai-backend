from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session
from typing import List

from app.core.exceptions import PermissionDeniedException, NotFoundException
from app.db.base import get_db
from app.services.post_service import (
    create_post, get_post, get_posts, get_user_posts,
    update_post, delete_post, add_comment, get_comments,
    delete_comment
)
from app.schemas.post import Post, PostCreate, PostResponse
from app.utils.backblaze_upload import backblaze_uploader
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
        raise Exception(f"Post oluşturulurken bir hata oluştu: {str(e)}")

@router.get("/{post_id}", response_model=Post)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Belirli bir post'u getirir"""
    post = get_post(db, post_id)
    if not post:
        raise NotFoundException("Post bulunamadı")
    return post

@router.get("/", response_model=List[Post])
async def read_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Tüm post'ları getirir"""
    return get_posts(db, skip, limit)

@router.get("/user/{user_id}", response_model=List[Post])
async def read_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Belirli bir kullanıcının post'larını getirir"""
    return get_user_posts(db, user_id, skip, limit)

@router.put("/{post_id}", response_model=Post)
async def update_post_content(
    post_id: int,
    content: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Post içeriğini günceller"""
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
    content: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Post'a yorum ekler"""
    if not hasattr(current_user, 'user_id'):
        raise PermissionDeniedException()
    
    return add_comment(db, post_id, current_user.user_id, content)

@router.get("/{post_id}/comments")
async def read_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Post'un yorumlarını getirir"""
    return get_comments(db, post_id, skip, limit)

@router.delete("/comments/{comment_id}")
async def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Yorumu siler"""
    return delete_comment(db, comment_id) 