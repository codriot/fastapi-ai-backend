from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.get_signed_url import get_signed_url
from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.db.base import get_db

router = APIRouter()

@router.get("/signed-url/{file_name}")
async def generate_signed_url(
    file_name: str,
    duration_seconds: int = 3600,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Backblaze B2'de saklanan bir dosya için geçici URL oluşturur
    
    Args:
        file_name: Dosya adı (örn: "example.jpg")
        duration_seconds: URL'nin geçerli olacağı süre (saniye)
        
    Returns:
        dict: Geçici erişim URL'si
    """
    try:
        url = get_signed_url(file_name, duration_seconds)
        return {"url": url, "expires_in_seconds": duration_seconds}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL oluşturma hatası: {str(e)}"
        )
