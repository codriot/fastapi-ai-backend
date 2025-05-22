#!/usr/bin/env python3
# Backblaze B2'ye dosya yükleyen test betiği

import sys
import os

# Proje kök dizinini Python path'ine ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from app.core.config import settings

# Test dosyası bilgileri
from datetime import datetime

FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_files", "resim.png"))
# Dosya adına tarih ekleyerek benzersiz yap
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
FILE_NAME = f"resim1_{timestamp}.png"

def get_b2_client():
    """Backblaze B2 istemcisi oluşturur"""
    try:
        # B2 ile uyumlu konfigürasyon
        config = Config(
            s3={
                'addressing_style': 'path',
                'payload_signing_enabled': False,
                'use_accelerate_endpoint': False
            },
            signature_version='s3v4'
        )
        
        return boto3.client(
            service_name='s3',
            endpoint_url=settings.BACKBLAZE_ENDPOINT,
            aws_access_key_id=settings.BACKBLAZE_KEY_ID,
            aws_secret_access_key=settings.BACKBLAZE_APPLICATION_KEY,
            config=config
        )
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None

def upload_specific_file(client, file_path, file_name):
    """Belirtilen dosyayı yükler"""
    try:
        print(f"\n{file_name} dosyası yükleniyor...")
        
        # Dosya var mı kontrol et
        if not os.path.exists(file_path):
            print(f"Hata: {file_path} bulunamadı")
            return False
            
        # Dosyayı binary modda aç ve içeriği oku
        with open(file_path, 'rb') as file_data:
            file_content = file_data.read()
          # Dosya uzantısına göre içerik tipini belirle
        content_type = 'application/octet-stream'  # Varsayılan
        if file_name.lower().endswith('.png'):
            content_type = 'image/png'
        elif file_name.lower().endswith('.jpg') or file_name.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif file_name.lower().endswith('.gif'):
            content_type = 'image/gif'
        elif file_name.lower().endswith('.pdf'):
            content_type = 'application/pdf'
          # Dosyayı yükle
        client.put_object(
            Bucket=settings.BACKBLAZE_BUCKET_NAME,
            Key=file_name,
            Body=file_content,
            ContentType=content_type
        )
        
        print(f"{file_name} dosyası başarıyla yüklendi")
        print(f"URL: {settings.BACKBLAZE_ENDPOINT}/{settings.BACKBLAZE_BUCKET_NAME}/{file_name}")
        return True
        
    except ClientError as e:
        print(f"Yükleme hatası: {str(e)}")
        return False

def list_bucket_contents(client, bucket_name):
    """Bucket içeriğini listeler"""
    try:
        response = client.list_objects_v2(Bucket=bucket_name)
        
        print(f"\n{bucket_name} bucket içeriği:")
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"- {obj['Key']} (Son değişiklik: {obj['LastModified']})")
        else:
            print("Bucket boş")
    except ClientError as e:
        print(f"Hata: {str(e)}")

def main():
    """Ana fonksiyon"""
    print("Backblaze B2 dosya yükleme testi başlıyor...")
    
    # B2 istemcisini oluştur
    b2_client = get_b2_client()
    
    if not b2_client:
        print("Backblaze B2 bağlantısı kurulamadı!")
        return
        
    # Yüklemeden önce bucket içeriğini listele
    list_bucket_contents(b2_client, settings.BACKBLAZE_BUCKET_NAME)
    
    # Özel dosyayı yükle
    upload_specific_file(b2_client, FILE_PATH, FILE_NAME)
    
    # Yükleme sonrası bucket içeriğini tekrar listele
    list_bucket_contents(b2_client, settings.BACKBLAZE_BUCKET_NAME)

if __name__ == '__main__':
    main()
