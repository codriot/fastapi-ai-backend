import boto3
from dotenv import load_dotenv
import os
from fastapi import UploadFile
import uuid
from app.core.config import settings

# .env dosyasını yükle
load_dotenv()

class BackblazeUploader:
    def __init__(self):
        """
        Backblaze B2 yükleyici sınıfını başlatır
        """
        # Backblaze B2 bağlantı bilgileri
        self.client = boto3.client(
            's3',
            endpoint_url=settings.BACKBLAZE_ENDPOINT,
            aws_access_key_id=settings.BACKBLAZE_KEY_ID,
            aws_secret_access_key=settings.BACKBLAZE_APPLICATION_KEY
        )
        self.bucket_name = settings.BACKBLAZE_BUCKET_NAME
    
    async def upload_file(self, file: UploadFile) -> str:
        """
        Dosyayı Backblaze B2'ye yükler ve URL'ini döndürür
        
        Args:
            file (UploadFile): Yüklenecek dosya
            
        Returns:
            str: Yüklenen dosyanın URL'i
        """
        try:
            # Benzersiz dosya adı oluştur
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Dosyayı yükle
            await self.client.upload_fileobj(
                file.file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            # URL oluştur
            url = f"{settings.BACKBLAZE_ENDPOINT}/{self.bucket_name}/{unique_filename}"
            return url
            
        except Exception as e:
            raise Exception(f"Dosya yükleme hatası: {str(e)}")

# Singleton instance
backblaze_uploader = BackblazeUploader() 