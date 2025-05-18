# import boto3
# from dotenv import load_dotenv
# import os

# # .env dosyasındaki değişkenleri yükle
# load_dotenv()

# # Endpoint URL (Backblaze B2 için)
# ENDPOINT_URL = os.getenv("ENDPOINT_URL")
# BUCKET_NAME = os.getenv("BUCKET_NAME")

# # Ortam değişkenlerinden anahtarları al
# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# # Boto3 istemcisi oluştur
# client = boto3.client(
#     's3',
#     endpoint_url=ENDPOINT_URL,
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY
# )

# # Tüm bucket'ları listele
# response = client.list_buckets()

# for bucket in response['Buckets']:
#     print(bucket['Name'])
