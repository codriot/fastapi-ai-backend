from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env dosyasından çevresel değişkenleri yükle
load_dotenv()

# Veritabanı bağlantı URL'si
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy engine oluştur
engine = create_engine(DATABASE_URL)

# Oturum oluşturucuyu yapılandır
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Temel model sınıfı
Base = declarative_base()

# Meta nesne
metadata = MetaData()

# Veritabanı oturumu elde etmek için bağımlılık
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()