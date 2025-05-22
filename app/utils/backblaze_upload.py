import boto3
from dotenv import load_dotenv
import os
from fastapi import UploadFile
import uuid
from app.core.config import settings
import aiofiles
import asyncio
from botocore.config import Config
import botocore.session
from boto3.session import Session

# .env dosyasını yükle
load_dotenv()

class BackblazeUploader:
    def __init__(self):
        """
        Backblaze B2 yükleyici sınıfını başlatır
        """
        # Özel bir botocore session oluştur ve yapılandır
        session = botocore.session.get_session()
        
        # Backblaze B2 bağlantı bilgileri ile boto3 session oluştur
        boto3_session = Session(
            aws_access_key_id=settings.BACKBLAZE_KEY_ID,
            aws_secret_access_key=settings.BACKBLAZE_APPLICATION_KEY,
            botocore_session=session
        )        # Backblaze B2 ile uyumlu istemciyi oluştur
        config = Config(
            s3={
                'addressing_style': 'path',
                'payload_signing_enabled': False,
                'use_accelerate_endpoint': False
            },
            signature_version='s3v4'
        )
        
        self.client = boto3_session.client(
            's3',
            endpoint_url=settings.BACKBLAZE_ENDPOINT,
            config=config
        )
          # Ekstra argümanlar - Backblaze B2 ACL'i desteklemediği için boş bırakıyoruz
        self.extra_args = {}
        
        self.bucket_name = settings.BACKBLAZE_BUCKET_NAME
    
    async def upload_file(self, file: UploadFile) -> str:
        """
        Dosyayı Backblaze B2'ye yükler ve URL'ini döndürür
        
        Args:
            file (UploadFile): Yüklenecek dosya
            
        Returns:
            str: Yüklenen dosyanın URL'i
        """
        temp_file = None
        try:
            # Benzersiz dosya adı oluştur
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Geçici dosya oluştur
            temp_file = f"temp_{unique_filename}"
            
            # Dosyayı geçici olarak kaydet
            async with aiofiles.open(temp_file, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Upload öncesi ekstra argümanları ayarla
            upload_args = dict(self.extra_args)
            
            # Content-Type ekle
            if file.content_type:
                upload_args['ContentType'] = file.content_type
            else:
                upload_args['ContentType'] = 'application/octet-stream'
              # Dosyayı doğrudan upload_file ile yükle (put_object yerine)            # Dosyayı yükle
            with open(temp_file, 'rb') as data:
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=unique_filename,
                    Body=data,
                    **upload_args
                )
            
            # Geçici dosyayı sil
            if os.path.exists(temp_file):
                os.remove(temp_file)
                temp_file = None
            
            # URL oluştur
            url = f"{settings.BACKBLAZE_ENDPOINT}/{self.bucket_name}/{unique_filename}"
            return url
            
        except Exception as e:
            # Hata durumunda geçici dosyayı temizle
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
            raise Exception(f"Dosya yükleme hatası: {str(e)}")

# Singleton instance
backblaze_uploader = BackblazeUploader() 