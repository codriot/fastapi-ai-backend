from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env dosyasından çevresel değişkenleri yükle
load_dotenv()

# Veritabanı bağlantı URL'si
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dietai:e9rP3eyC3cbPD6jUWNj9CfWR8PSDzzgS@dpg-d04jlgi4d50c73a8lgf0-a.frankfurt-postgres.render.com/dietapp_rt6g")

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