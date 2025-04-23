from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Body, Header
from fastapi.responses import FileResponse, JSONResponse
from firebase import verify_token, db
from models.post import Post, PostComment
from models.user import User, UserCreate, Role, user_to_dict, user_details_to_dict, dietitian_details_to_dict
from models.dietitian import DietitianCreate, dietitian_to_dict
from services.post_service import add_comment, delete_comment, delete_post, save_post, update_post
from services.user_service import add_user, get_user, delete_user
from services.recipe_service import get_recipe_names_by_keyword
import os
from firebase_admin import auth, initialize_app, firestore, credentials
import firebase_admin  # firebase_admin modülünü içe aktarın
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt  # JWT kütüphanesi
import pandas as pd
import joblib
import sys
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Ana proje dizinini sys.path'e ekleyelim
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Yapay zeka modülleri
try:
    from models.model_training import load_model
    # Script klasöründeki diet_list_make fonksiyonlarını kullanabilmek için
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'script'))
    from script.diet_list_make import (
        recommend_recipes, create_diet_list, recommend_recipes_turkish, create_diet_list_turkish,
        RecipeKeyword, filter_recipes_by_keyword
    )
except ImportError as e:
    print(f"Modül yüklenirken hata oluştu: {e}")

# Firebase Admin SDK'yı yalnızca bir kez başlat
if not firebase_admin._apps:
    initialize_app()

# Initialize Firestore client
db = firestore.client()

app = FastAPI(title="Diet App API", description="Diyet ve beslenme uygulaması için API")

# Token doğrulama için HTTPBearer kullanımı
security = HTTPBearer()

# JWT Ayarları
SECRET_KEY = "your_secret_key"  # Güçlü bir secret key belirleyin
ALGORITHM = "HS256"  # Kullanılacak algoritma
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 hafta (dakika cinsinden)

# Request modellerimizi tanımlayalım
class DietRequest(BaseModel):
    calorie_limit: int
    diet_type: str = "regular"  # regular veya turkish
    preferences: Optional[List[str]] = None
    keyword: Optional[RecipeKeyword] = None

class RecipeRequest(BaseModel):
    recipe_index: int
    n_recommendations: int = 5
    is_turkish: bool = False

def create_jwt_token(data: dict):
    """JWT token oluşturur."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str):
    """JWT token doğrular."""
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token süresi dolmuş.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Geçersiz token.")

def verify_token_header(authorization: str = Header(...)):
    """Header'dan gelen tokeni doğrular."""
    try:
        token = authorization  # Authorization başlığından token al
        decoded_token = verify_jwt_token(token)  # Token doğrulama işlemi
        return decoded_token.get("uid")  # Doğrulanan kullanıcı kimliği (UID)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

def format_response(success: bool, data=None, message=""):
    """Standart bir cevap formatı döndürür."""
    return JSONResponse(content={"success": success, "data": data, "message": message})

@app.post("/login/")
async def login(credentials: dict = Body(...)):
    """
    Kullanıcı giriş endpoint'i.
    """
    try:
        email = credentials.get("email")
        password = credentials.get("password")
        
        # Firestore'da kullanıcıyı sorgula
        users_ref = db.collection("user")
        query = users_ref.where("email", "==", email).where("password", "==", password).limit(1)
        docs = query.stream()

        # Kullanıcıyı kontrol et
        user_data = None
        for doc in docs:
            user_data = doc.to_dict()
            user_data["uid"] = doc.id
            break

        if user_data:
            # Kullanıcı için JWT token oluştur
            token = create_jwt_token({"uid": user_data["uid"]})
            return format_response(True, {"token": token}, "Giriş başarılı.")
        else:
            return format_response(False, None, "Kullanıcı bulunamadı.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.post("/users/")
def create_user(user: User):
    """ Kullanıcı ekler ve token döndürür """
    try:
        result = add_user(user)
        token = create_jwt_token({"uid": result["uid"]})
        return format_response(True, {"token": token}, "Kullanıcı başarıyla oluşturuldu.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.get("/users/me")
def read_user(uid: str = Depends(verify_token_header)):
    """Token doğrulandıktan sonra kullanıcı bilgilerini döndür."""
    try:
        result = get_user(uid)
        
        # Tarih alanlarını dönüştür
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        
        return format_response(True, result, "Kullanıcı bilgileri başarıyla alındı.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.delete("/users/me")
def remove_user(uid: str = Depends(verify_token_header)):
    """ Token doğrulandıktan sonra kullanıcıyı siler """
    try:
        result = delete_user(uid)
        return format_response(True, result, "Kullanıcı başarıyla silindi.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

# Uploads klasörünü dışarıdan erişilebilir hale getiriyoruz
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/post/")
async def create_post(
    post_id: str = Form(...),
    user_id: str = Depends(verify_token_header),
    content: str = Form(...),
    timestamp: str = Form(...),
    image: UploadFile = File(None)  # Resim isteğe bağlıdır
):
    """Yeni bir post oluşturur ve resmini yükler"""
    try:
        post = Post(
            post_id=post_id,
            user_id=user_id,
            content=content,
            timestamp=timestamp,
        )
        result = save_post(post, image)
        return format_response(True, result, "Post başarıyla oluşturuldu.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

# Yüklenen resimleri sunucu üzerinden görüntüleyebilmek için
@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    return FileResponse(f"uploads/{filename}")

# ! şuan için bu endpoint istediğim şekilde çalışmamaktadır
# Tarif isimlerini dönen endpoint
@app.post("/get-recipe-names/")
async def get_recipe_names(
    keyword: str = Form(...)
):
    """
    Keyword'e göre tariflerin isimlerini dönen bir endpoint.
    """
    try:
        recipe_names = get_recipe_names_by_keyword(keyword)
        return format_response(True, {"keyword": keyword, "recipe_names": recipe_names}, "Tarif isimleri başarıyla alındı.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")


@app.post("/comments/")
async def create_comment(comment: PostComment, uid: str = Depends(verify_token_header)):
    """Belirtilen post'a yorum ekler"""
    return add_comment(comment)

@app.delete("/comments/{post_id}/{comment_id}")
async def remove_comment(post_id: str, comment_id: str, uid: str = Depends(verify_token_header)):
    """Bir posttaki yorumu siler"""
    return delete_comment(post_id, comment_id)

@app.put("/post/{post_id}")
async def modify_post(post_id: str, content: str, uid: str = Depends(verify_token_header)):
    """Bir post'un içeriğini günceller"""
    return update_post(post_id, content)

@app.delete("/post/{post_id}")
async def remove_post(post_id: str, uid: str = Depends(verify_token_header)):
    """Bir post'u tamamen siler"""
    return delete_post(post_id)

@app.post("/register/")
def register_user(user: UserCreate):
    """Yeni bir kullanıcı kaydı oluşturur ve rolüne göre ilgili koleksiyonlarda bilgilerini saklar."""
    try:
        # Firebase Authentication'da kullanıcı oluştur
        firebase_user = auth.create_user(email=user.email, password=user.password)
        user_id = firebase_user.uid
        
        # Ana users koleksiyonuna kaydet
        user_data = user_to_dict(user)
        db.collection("users").document(user_id).set(user_data)
        
        # Rolüne göre detayları kaydet
        if user.role == Role.USER:
            # Kullanıcı detaylarının zorunlu olduğunu kontrol et
            if user.age is None or user.weight is None or user.height is None or user.goal is None or user.activity_level is None:
                raise HTTPException(status_code=400, detail="Kullanıcı detayları eksik")
            
            user_details = user_details_to_dict(user_id, user)
            db.collection("user_details").document(user_id).set(user_details)
        
        elif user.role == Role.DIETITIAN:
            # Diyetisyen detaylarının zorunlu olduğunu kontrol et
            if user.experience is None or user.specialization is None:
                raise HTTPException(status_code=400, detail="Diyetisyen detayları eksik")
            
            dietitian_details = dietitian_details_to_dict(user_id, user)
            db.collection("dietitian_details").document(user_id).set(dietitian_details)
        
        # Admin rolü için ek bilgi gerekmez
        
        # Kullanıcı için token oluştur
        token = auth.create_custom_token(user_id)
        
        return format_response(
            True, 
            {"uid": user_id, "token": token.decode("utf-8")}, 
            "Kullanıcı başarıyla oluşturuldu."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kayıt sırasında bir hata oluştu: {str(e)}")

@app.post("/register-dietitian/")
def register_dietitian(dietitian: DietitianCreate):
    """Diyetisyen kaydı için özel endpoint. Diyetisyen bilgilerini ayrı bir koleksiyonda saklar."""
    try:
        # Firebase Authentication'da kullanıcı oluştur
        firebase_user = auth.create_user(email=dietitian.email, password=dietitian.password)
        dietitian_id = firebase_user.uid
        
        # Diyetisyen bilgilerini dietitians koleksiyonuna kaydet
        dietitian_data = dietitian_to_dict(dietitian)
        db.collection("dietitians").document(dietitian_id).set(dietitian_data)
        
        # Kullanıcı için token oluştur
        token = auth.create_custom_token(dietitian_id)
        
        return format_response(
            True, 
            {"uid": dietitian_id, "token": token.decode("utf-8")}, 
            "Diyetisyen başarıyla kaydedildi."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Diyetisyen kaydı sırasında bir hata oluştu: {str(e)}")

# Diet önerisi için endpoint
@app.post("/predict/diet-list/")
async def predict_diet_list(request: DietRequest):
    try:
        # İstek tipine göre diyet listesi oluştur
        if request.diet_type.lower() == "turkish":
            diet_list = create_diet_list_turkish(request.calorie_limit)
        else:
            diet_list = create_diet_list(request.calorie_limit)
            
        # Eğer tercihler belirtilmişse filtreleme yap
        if request.preferences:
            filtered_diet_list = []
            for _, recipe in diet_list.iterrows():
                # RecipeIngredientParts sütunu bir string olarak saklanıyorsa:
                ingredients = str(recipe.get('RecipeIngredientParts', ''))
                if any(pref.lower() in ingredients.lower() for pref in request.preferences):
                    filtered_diet_list.append(recipe.to_dict())
            return {"diet_list": filtered_diet_list, "total_recipes": len(filtered_diet_list)}
        
        # Eğer keyword belirtilmişse filtreleme yap
        if request.keyword:
            diet_list = filter_recipes_by_keyword(diet_list, request.keyword)
        
        # Tercihlere göre filtreleme yapılmadıysa tüm listeyi döndür
        return {"diet_list": diet_list.to_dict('records'), "total_recipes": len(diet_list)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diet listesi oluşturulurken bir hata oluştu: {str(e)}")

# Benzer tarifleri öneri için endpoint
@app.post("/predict/recipe-recommendations/")
async def predict_recipe_recommendations(request: RecipeRequest):
    try:
        if request.is_turkish:
            recommendations = recommend_recipes_turkish(request.recipe_index, request.n_recommendations)
        else:
            recommendations = recommend_recipes(request.recipe_index, request.n_recommendations)
            
        return {"recommendations": recommendations.to_dict('records'), "total_recipes": len(recommendations)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tarif önerileri alınırken bir hata oluştu: {str(e)}")

# Model tahminleri için endpoint (sabit parametrelere göre)
@app.post("/predict/nutrition/")
async def predict_nutrition(data: dict):
    try:
        # Model dosyasının yolu
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'trained_model.pkl')
        
        # Modeli yükle
        model = joblib.load(model_path)
        
        # Gerekli özellikleri al
        features = pd.DataFrame({
            'carbs': [data.get('carbs', 0)],
            'protein': [data.get('protein', 0)],
            'fats': [data.get('fats', 0)]
        })
        
        # Tahmin yap
        prediction = model.predict(features)[0]
        
        return {
            "predicted_calories": float(prediction),
            "input_features": data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin yapılırken bir hata oluştu: {str(e)}")

# Yapay zeka modeline doğrudan metin isteği göndermek için endpoint
@app.post("/predict/ai-query/")
async def ai_query(data: dict):
    try:
        query = data.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Sorgu metni boş olamaz")
            
        # Bu kısımda kendi yapay zeka modelinize istek gönderecek kod olmalı
        # Örnek olarak basit bir yanıt döndürüyoruz
        response = f"Sorgunuz için öneriler: '{query}' için yapay zeka modeli yanıtı"
        
        return {
            "query": query,
            "response": response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yapay zeka sorgusu sırasında bir hata oluştu: {str(e)}")

# Sağlık kontrolü için bir endpoint
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

# Uygulamayı başlatmak için (uvicorn ile çalıştırılabilir)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)