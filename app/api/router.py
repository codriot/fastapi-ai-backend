from fastapi import APIRouter
from .endpoints import auth, posts, users, dietitians, nutrition, appointments, nutrition_ai, messages, file_access, recipes

# Ana router
api_router = APIRouter()

# Alt router'ları ekle
api_router.include_router(auth.router, prefix="/auth", tags=["Kimlik Doğrulama"])
api_router.include_router(users.router, prefix="/users", tags=["Kullanıcılar"])
api_router.include_router(dietitians.router, prefix="/dietitians", tags=["Diyetisyenler"])
api_router.include_router(posts.router, prefix="/posts", tags=["Gönderiler"])
api_router.include_router(nutrition.router, prefix="/nutrition", tags=["Beslenme"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Randevular"])
api_router.include_router(nutrition_ai.router, prefix="/nutrition/ai", tags=["Beslenme AI"])
api_router.include_router(messages.router, prefix="/messages", tags=["Mesajlaşma"])
api_router.include_router(file_access.router, prefix="/files", tags=["Dosya Erişimi"])
api_router.include_router(recipes.router, prefix="/recipes", tags=["Tarifler"])