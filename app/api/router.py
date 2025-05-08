from fastapi import APIRouter
from .endpoints import auth, posts, users, dietitians, nutrition, appointments

# Ana router
api_router = APIRouter()

# Alt router'ları ekle
api_router.include_router(auth.router, prefix="/auth", tags=["Kimlik Doğrulama"])
api_router.include_router(users.router, prefix="/users", tags=["Kullanıcılar"])
api_router.include_router(dietitians.router, prefix="/dietitians", tags=["Diyetisyenler"])
api_router.include_router(posts.router, prefix="/posts", tags=["Gönderiler"])
api_router.include_router(nutrition.router, prefix="/nutrition", tags=["Beslenme"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Randevular"]) 