from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.db.base import Base, engine

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# FastAPI uygulamasını oluştur
app = FastAPI(
    title=settings.APP_NAME,
    description="Diyet ve beslenme uygulaması için API",
    debug=settings.DEBUG
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# API router'ını ekle
app.include_router(api_router, prefix="/api")

# Sağlık kontrolü
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Ana sayfa
@app.get("/")
async def root():
    return {
        "message": "Diet App API'ye hoş geldiniz",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Uygulamayı başlatmak için
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)