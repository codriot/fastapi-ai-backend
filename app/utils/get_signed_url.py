from fastapi import FastAPI, HTTPException
import requests
import os
from dotenv import load_dotenv
import time
import urllib.parse

# .env dosyasını yükle
load_dotenv()

# B2 kimlik bilgileri
KEY_ID = os.getenv("BACKBLAZE_KEY_ID")
APP_KEY = os.getenv("BACKBLAZE_APPLICATION_KEY")
BUCKET_NAME = os.getenv("BACKBLAZE_BUCKET_NAME")

def get_signed_url(file_name: str, duration_seconds: int = 3600):
    """
    Backblaze B2'deki özel bir dosya için geçici bir URL oluşturur
    
    Args:
        file_name: Dosya adı (örn: "example.jpg")
        duration_seconds: URL'nin geçerli olacağı süre (saniye)
        
    Returns:
        str: Geçici erişim URL'si
    """
    try:
        # B2 hesabını yetkilendir
        auth_response = requests.get(
            "https://api.backblazeb2.com/b2api/v2/b2_authorize_account",
            auth=(KEY_ID, APP_KEY)
        )
        
        if auth_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Backblaze B2 yetkilendirme hatası")
            
        auth_data = auth_response.json()
        
        # Bucket ID'sini bul
        bucket_response = requests.post(
            f"{auth_data['apiUrl']}/b2api/v2/b2_list_buckets",
            headers={"Authorization": auth_data["authorizationToken"]},
            json={"accountId": auth_data["accountId"]}
        )
        
        if bucket_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Bucket listesi alınamadı")
            
        buckets = bucket_response.json().get("buckets", [])
        bucket_id = next((b["bucketId"] for b in buckets if b["bucketName"] == BUCKET_NAME), None)
        
        if not bucket_id:
            raise HTTPException(status_code=404, detail=f"'{BUCKET_NAME}' bucket'ı bulunamadı")
        
        # Dosya bilgilerini alalım
        file_info_response = requests.post(
            f"{auth_data['apiUrl']}/b2api/v2/b2_list_file_names",
            headers={"Authorization": auth_data["authorizationToken"]},
            json={
                "bucketId": bucket_id,
                "prefix": file_name,
                "maxFileCount": 1
            }
        )
        
        if file_info_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Dosya bilgisi alınamadı")
            
        files = file_info_response.json().get("files", [])
        if not files:
            raise HTTPException(status_code=404, detail=f"'{file_name}' dosyası bulunamadı")
            
        # İndirme yetkilendirmesi al
        download_auth_response = requests.post(
            f"{auth_data['apiUrl']}/b2api/v2/b2_get_download_authorization",
            headers={"Authorization": auth_data["authorizationToken"]},
            json={
                "bucketId": bucket_id,
                "fileNamePrefix": file_name,
                "validDurationInSeconds": duration_seconds
            }
        )
        
        if download_auth_response.status_code != 200:
            raise HTTPException(status_code=500, detail="İndirme yetkilendirmesi alınamadı")
            
        auth_token = download_auth_response.json().get("authorizationToken")
        
        # URL kodlaması yaparak doğru bir URL oluştur
        encoded_file_name = urllib.parse.quote(file_name)
        download_url = f"{auth_data['downloadUrl']}/file/{BUCKET_NAME}/{encoded_file_name}?Authorization={auth_token}"
        
        return download_url
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL oluşturma hatası: {str(e)}")
