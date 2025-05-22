#!/usr/bin/env python3

import sys
import os

# Proje kök dizinini Python path'ine ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from app.core.config import settings

# Test için gerekli dizin ve dosya ayarları
LOCAL_DIR = os.path.join(os.path.dirname(__file__), 'test_files')
if not os.path.exists(LOCAL_DIR):
    os.makedirs(LOCAL_DIR)

def get_b2_client():
    """Backblaze B2 istemcisi oluşturur"""
    try:
        return boto3.client(
            service_name='s3',
            endpoint_url=settings.BACKBLAZE_ENDPOINT,
            aws_access_key_id=settings.BACKBLAZE_KEY_ID,
            aws_secret_access_key=settings.BACKBLAZE_APPLICATION_KEY
        )
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None

def get_b2_resource():
    """Backblaze B2 resource nesnesi oluşturur"""
    try:
        config = Config(
            s3={
                'addressing_style': 'path',
                'payload_signing_enabled': False,
                'use_accelerate_endpoint': False
            },
            signature_version='s3v4'
        )
        
        return boto3.resource(
            service_name='s3',
            endpoint_url=settings.BACKBLAZE_ENDPOINT,
            aws_access_key_id=settings.BACKBLAZE_KEY_ID,
            aws_secret_access_key=settings.BACKBLAZE_APPLICATION_KEY,
            config=config
        )
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None

def list_bucket_contents(bucket_name, b2):
    """Bucket içeriğini listeler"""
    try:
        bucket = b2.Bucket(bucket_name)
        print(f"\n{bucket_name} bucket içeriği:")
        for obj in bucket.objects.all():
            print(f"- {obj.key}")
    except ClientError as e:
        print(f"Hata: {str(e)}")

def upload_test_file(bucket_name, b2, file_name="test.txt"):
    """Test dosyası yükler"""
    try:
        # Test dosyası oluştur
        file_path = os.path.join(LOCAL_DIR, file_name)
        with open(file_path, 'w') as f:
            f.write("Bu bir test dosyasıdır")        # Dosyayı yükle
        print(f"\n{file_name} dosyası yükleniyor...")
        # Doğrudan client üzerinden put_object kullan
        client = b2.meta.client
        with open(file_path, 'rb') as data:
            # Dosya içeriğini oku
            file_content = data.read()
            
        client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content,
            ContentType='text/plain'
        )
        print(f"{file_name} başarıyla yüklendi")

        # Yerel dosyayı sil
        os.remove(file_path)
        
    except ClientError as e:
        print(f"Hata: {str(e)}")

def main():
    """Ana test fonksiyonu"""
    print("Backblaze B2 bağlantı testi başlıyor...")
    
    # B2 istemcilerini oluştur
    b2_client = get_b2_client()
    b2 = get_b2_resource()
    
    if not b2_client or not b2:
        print("Backblaze B2 bağlantısı kurulamadı!")
        return
    
    # Mevcut bucket'ları listele
    try:
        buckets = b2_client.list_buckets()
        print("\nMevcut bucket'lar:")
        for bucket in buckets['Buckets']:
            print(f"- {bucket['Name']}")
    except ClientError as e:
        print(f"Bucket'lar listelenirken hata: {str(e)}")
        return
    
    # Ana bucket içeriğini listele
    list_bucket_contents(settings.BACKBLAZE_BUCKET_NAME, b2)
    
    # Test dosyası yükle
    upload_test_file(settings.BACKBLAZE_BUCKET_NAME, b2)
    
    # Upload sonrası bucket içeriğini tekrar listele
    list_bucket_contents(settings.BACKBLAZE_BUCKET_NAME, b2)

if __name__ == '__main__':
    main()
