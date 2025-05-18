from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Settings(BaseSettings):
    # Uygulama ayarları
    APP_NAME: str = "Diet App API"
    DEBUG: bool = True
    
    # Veritabanı ayarları
    DATABASE_URL: str 
    
    # JWT ayarları
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dietapp-JWT-secretkey-2025-04-23-v1")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 hafta
    
    # Backblaze B2 ayarları
    BACKBLAZE_KEY_ID: str = os.getenv("BACKBLAZE_KEY_ID")
    BACKBLAZE_APPLICATION_KEY: str = os.getenv("BACKBLAZE_APPLICATION_KEY")
    BACKBLAZE_BUCKET_NAME: str = os.getenv("BACKBLAZE_BUCKET_NAME")
    BACKBLAZE_ENDPOINT: str = os.getenv("BACKBLAZE_ENDPOINT")
    
    # CORS ayarları
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings() 