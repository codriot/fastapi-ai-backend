from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Body, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, Base, engine
from sqlalchemy.orm import Session
import traceback
import logging
import os
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from passlib.context import CryptContext
import pandas as pd
import joblib
import sys
from enum import Enum

# Ana proje dizinini sys.path'e ekleyelim
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Modelleri import edelim - Önce bağımsız modeller
from models.food_tracking import (
    Food, AIModelOutput, ProgressTracking, Appointment,
    FoodCreate, AIModelOutputCreate, ProgressTrackingCreate, AppointmentCreate
)
from models.user import User, UserCreate, UserResponse as UserResponseModel
from models.dietitian import Dietitian, DietitianCreate, DietitianResponse
from models.message import Message, MessageCreate, MessageResponse
from models.post import PostDB, PostCommentDB, Post, PostComment, PostCreate, PostResponse
# Diyet öneri modülünü import ediyoruz
from models.nutrition_model import (
    NutritionRequest, NutritionProfile, ProfileRequest, 
    model_yukle, veri_yukle, diyet_oner, hazir_profil_degerlerini_al
)

# Servisleri import edelim
from services.user_service import (
    create_user, get_user_by_id, get_user_by_email, update_user, 
    delete_user, authenticate_user, get_password_hash
)
from services.dietitian_service import (
    create_dietitian, get_dietitian_by_id, get_dietitian_by_email, 
    update_dietitian, delete_dietitian, authenticate_dietitian
)
from services.post_service import (
    create_post, get_post, get_posts, get_user_posts, update_post, 
    delete_post, add_comment, get_comments, delete_comment
)
from services.recipe_service import get_recipe_names_by_keyword

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

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Diet App API", description="Diyet ve beslenme uygulaması için API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm domainlere izin ver (geliştirme için)
    allow_credentials=True,
    allow_methods=["*"],  # Tüm HTTP metodlarına izin ver
    allow_headers=["*"],  # Tüm HTTP başlıklarına izin ver
)

# Uploads klasörünü dışarıdan erişilebilir hale getiriyoruz
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# JWT için ayarlar
# Rastgele ve güçlü bir secret key oluşturalım
import secrets
# Sabit SECRET_KEY yerine rastgele ama uygulamanın her başlatılışında aynı kalacak bir key oluşturalım
SECRET_KEY = "dietapp-JWT-secretkey-2025-04-23-v1"  # Üretim ortamında daha güçlü bir key kullanılmalı
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 hafta

# OAuth2 için token şeması
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Şifre işlemleri için
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserAuth(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str = "user"
    
    class Config:
        orm_mode = True

# Token yardımcı fonksiyonları
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    # user_id'yi string'e dönüştür
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])
        
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # PyJWT 2.0+ ile uyumluluk için değişiklik
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        # PyJWT 2.0+ sürümlerinde encode işlemi bytes değil string döndürür
        # Eğer encoded_jwt bir bytes ise string'e çevirelim
        if isinstance(encoded_jwt, bytes):
            return encoded_jwt.decode('utf-8')
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token oluşturma hatası: {str(e)}")
        raise

def verify_token(token: str = Depends(oauth2_scheme)):
    """Token'ı doğrulama ve kullanıcı bilgilerini çıkarma işlemi"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token doğrulanırken hata oluştu",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # PyJWT 2.0+ uyumluluğu için token tipini kontrol edelim
        # Eğer token zaten bytes tipinde değilse dönüştürelim
        if isinstance(token, str):
            # Sadece decode işlemini sabit SECRET_KEY ile yapalım
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        else:
            logger.error(f"Token tipi beklenmeyen bir format: {type(token)}")
            raise credentials_exception
            
        user_id = payload.get("sub")
        role: str = payload.get("role")
        
        # Kullanıcı ID'si veya rolün olmaması durumunda hata fırlat
        if user_id is None or role is None:
            logger.error(f"Token içinde gerekli bilgiler eksik: user_id={user_id}, role={role}")
            raise credentials_exception
            
        # user_id string olarak gelecek, int'e dönüştür
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            logger.error(f"user_id tamsayıya dönüştürülemedi: {user_id}")
            raise credentials_exception
            
        # TokenData nesnesine çevir
        token_data = TokenData(user_id=user_id_int, role=role)
        return token_data
    except jwt.ExpiredSignatureError:
        logger.error("Token süresi dolmuş")
        raise HTTPException(
            status_code=401,
            detail="Token süresi dolmuş, lütfen yeniden giriş yapın",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Geçersiz token: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Token doğrulama hatası: {str(e)}")
        raise credentials_exception

# Kullanıcı doğrulama - Token kullanarak mevcut kullanıcıyı getir
def get_current_user(db: Session = Depends(get_db), token_data: TokenData = Depends(verify_token)):
    if token_data.role == "dietitian":
        user = get_dietitian_by_id(db, token_data.user_id)
    else:
        user = get_user_by_id(db, token_data.user_id)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
    return user

# Standart yanıt formatı
def format_response(success: bool, data=None, message=""):
    """Standart bir cevap formatı döndürür."""
    # JSON serileştirme sorunlarını önlemek için
    if data is not None:
        # SQLAlchemy nesneleri veya sözlükler için
        if hasattr(data, '__dict__'):
            # SQLAlchemy nesnesini sözlüğe çevir
            data_dict = {}
            for key, value in data.__dict__.items():
                if not key.startswith('_'):  # SQLAlchemy iç değişkenlerini atla
                    data_dict[key] = _make_json_serializable(value)
            data = data_dict
        elif isinstance(data, dict):
            # Sözlük ise içindeki değerleri kontrol et
            data = {k: _make_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            # Liste ise her öğeyi kontrol et
            data = [_make_json_serializable(item) for item in data]
    
    return JSONResponse(content={"success": success, "data": data, "message": message})

def _make_json_serializable(obj):
    """Herhangi bir nesneyi JSON'a dönüştürülebilir hale getirir."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        # İç içe nesneler için
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                result[key] = _make_json_serializable(value)
        return result
    elif isinstance(obj, list):
        return [_make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    else:
        return obj

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    error_detail = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(f"Beklenmeyen hata: {error_detail}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": f"Internal Server Error: {str(exc)}", "error_detail": error_detail if app.debug else None},
    )

# Token endpoint'i - kullanıcı kimlik doğrulama
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Önce kullanıcı olarak kontrol et
    user = authenticate_user(db, form_data.username, form_data.password)
    role = "user"
    
    # Kullanıcı bulunamadıysa diyetisyen olarak kontrol et
    if not user:
        user = authenticate_dietitian(db, form_data.username, form_data.password)
        role = "dietitian"
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Yanlış kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kullanıcı ID'sini ve rolünü tokena ekle
    user_id = user.user_id if role == "user" else user.dietitian_id
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "role": role}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Kullanıcı yönetimi
@app.post("/register/user", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Email kontrolü
    db_user = get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Bu email zaten kullanılıyor")
    
    # Kullanıcı verilerini hazırla
    user_dict = user_data.dict()
    
    # Kullanıcıyı oluştur
    new_user = create_user(db, user_dict)
    
    return UserResponse(
        user_id=new_user.user_id,
        name=new_user.name,
        email=new_user.email,
        role="user"
    )

@app.post("/register/dietitian", response_model=DietitianResponse)
async def register_dietitian(dietitian_data: DietitianCreate, db: Session = Depends(get_db)):
    # Email kontrolü
    db_dietitian = get_dietitian_by_email(db, dietitian_data.email)
    if db_dietitian:
        raise HTTPException(status_code=400, detail="Bu email zaten kullanılıyor")
    
    # Diyetisyen verilerini hazırla
    dietitian_dict = dietitian_data.dict()
    
    # Diyetisyeni oluştur
    new_dietitian = create_dietitian(db, dietitian_dict)
    
    return new_dietitian

@app.post("/login/")
async def login(credentials: UserAuth, db: Session = Depends(get_db)):
    """
    Kullanıcı giriş endpoint'i.
    """
    try:
        # Önce kullanıcı olarak kontrol et
        user = authenticate_user(db, credentials.email, credentials.password)
        role = "user"
        
        # Kullanıcı bulunamadıysa diyetisyen olarak kontrol et
        if not user:
            user = authenticate_dietitian(db, credentials.email, credentials.password)
            role = "dietitian"
        
        if not user:
            return format_response(False, None, "Kullanıcı bulunamadı veya şifre yanlış")
        
        # Kullanıcı ID'sini ve rolünü tokena ekle
        user_id = user.user_id if role == "user" else user.dietitian_id
        access_token = create_access_token(data={"sub": user_id, "role": role})
        
        return format_response(True, {"token": access_token, "role": role}, "Giriş başarılı.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Giriş yapmış kullanıcı bilgilerini döndürür."""
    return current_user

@app.put("/users/me")
async def update_user_me(user_data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Giriş yapmış kullanıcı bilgilerini günceller."""
    # token_data = verify_token() yerine current_user'ı kullan
    
    if hasattr(current_user, 'user_id'):  # Kullanıcı
        updated_user = update_user(db, current_user.user_id, user_data)
        return format_response(True, updated_user, "Kullanıcı bilgileri başarıyla güncellendi.")
    else:  # Diyetisyen
        updated_dietitian = update_dietitian(db, current_user.dietitian_id, user_data)
        return format_response(True, updated_dietitian, "Diyetisyen bilgileri başarıyla güncellendi.")

@app.delete("/users/me")
async def delete_user_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Giriş yapmış kullanıcıyı siler."""
    # current_user bilgilerinden rol kontrolü yapalım
    
    if hasattr(current_user, 'user_id'):  # Kullanıcı
        result = delete_user(db, current_user.user_id)
        return format_response(True, result, "Kullanıcı başarıyla silindi.")
    else:  # Diyetisyen
        result = delete_dietitian(db, current_user.dietitian_id)
        return format_response(True, result, "Diyetisyen başarıyla silindi.")

# Post işlemleri
@app.post("/post/", response_model=PostResponse)
async def create_new_post(
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni bir post oluşturur ve resmini yükler"""
    # current_user bilgilerinden kullanıcı doğrulaması yapıyoruz
    
    # Sadece normal kullanıcılar post oluşturabilir
    if not hasattr(current_user, 'user_id'):
        raise HTTPException(status_code=403, detail="Sadece kullanıcılar post oluşturabilir")
    
    try:
        post = create_post(db, current_user.user_id, content, image)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post oluşturulurken bir hata oluştu: {str(e)}")

# Yüklenen resimleri sunucu üzerinden görüntüleyebilmek için
@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    return FileResponse(file_path)

# Tarif isimlerini dönen endpoint
@app.post("/get-recipe-names/")
async def get_recipe_names(keyword: str = Form(...)):
    """
    Keyword'e göre tariflerin isimlerini dönen bir endpoint.
    """
    try:
        recipe_names = get_recipe_names_by_keyword(keyword)
        return format_response(True, {"keyword": keyword, "recipe_names": recipe_names}, "Tarif isimleri başarıyla alındı.")
    except Exception as e:
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.post("/comments/")
async def create_comment(
    comment_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Belirtilen post'a yorum ekler"""
    # Sadece normal kullanıcılar yorum ekleyebilir
    if not hasattr(current_user, 'user_id'):
        raise HTTPException(status_code=403, detail="Sadece kullanıcılar yorum ekleyebilir")
    
    try:
        comment = add_comment(db, comment_data["post_id"], current_user.user_id, comment_data["content"])
        return comment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum eklenirken bir hata oluştu: {str(e)}")

@app.delete("/comments/{comment_id}")
async def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bir yorumu siler"""
    try:
        result = delete_comment(db, comment_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum silinirken bir hata oluştu: {str(e)}")

@app.put("/post/{post_id}")
async def modify_post(
    post_id: int,
    content: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bir post'un içeriğini günceller"""
    try:
        post = update_post(db, post_id, content["content"])
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post güncellenirken bir hata oluştu: {str(e)}")

@app.delete("/post/{post_id}")
async def remove_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bir post'u tamamen siler"""
    try:
        result = delete_post(db, post_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post silinirken bir hata oluştu: {str(e)}")

# Yapay zeka endpointleri
@app.post("/predict/diet-list/")
async def predict_diet_list(request: DietRequest, db: Session = Depends(get_db)):
    try:
        # İstek tipine göre diyet listesi oluştur
        if request.diet_type.lower() == "turkish":
            diet_list = create_diet_list_turkish(request.calorie_limit)
        else:
            diet_list = create_diet_list(request.calorie_limit)
        
        # Eğer anahtar kelime belirtilmişse filtreleme yap
        if request.keyword:
            diet_list = filter_recipes_by_keyword(diet_list, request.keyword.value)
            if diet_list.empty:
                return format_response(False, None, f"'{request.keyword.value}' anahtar kelimesine uygun tarif bulunamadı")
            
        # Eğer tercihler belirtilmişse filtreleme yap
        if request.preferences:
            filtered_diet_list = []
            for _, recipe in diet_list.iterrows():
                # RecipeIngredientParts sütunu bir string olarak saklanıyorsa:
                ingredients = str(recipe.get('RecipeIngredientParts', ''))
                if any(pref.lower() in ingredients.lower() for pref in request.preferences):
                    filtered_diet_list.append(recipe.to_dict())
            
            if not filtered_diet_list:
                return format_response(False, None, "Belirtilen tercihlere uygun tarif bulunamadı")
                
            return format_response(True, {"diet_list": filtered_diet_list, "total_recipes": len(filtered_diet_list)}, "Diyet listesi başarıyla oluşturuldu.")
        
        # Tercihlere göre filtreleme yapılmadıysa tüm listeyi döndür
        return format_response(True, {"diet_list": diet_list.to_dict('records'), "total_recipes": len(diet_list)}, "Diyet listesi başarıyla oluşturuldu.")
    
    except Exception as e:
        return format_response(False, None, f"Diet listesi oluşturulurken bir hata oluştu: {str(e)}")

@app.post("/predict/recipe-recommendations/")
async def predict_recipe_recommendations(request: RecipeRequest, db: Session = Depends(get_db)):
    try:
        if request.is_turkish:
            recommendations = recommend_recipes_turkish(request.recipe_index, request.n_recommendations)
        else:
            recommendations = recommend_recipes(request.recipe_index, request.n_recommendations)
            
        return format_response(True, {"recommendations": recommendations.to_dict('records'), "total_recipes": len(recommendations)}, "Tarif önerileri başarıyla alındı.")
    
    except Exception as e:
        return format_response(False, None, f"Tarif önerileri alınırken bir hata oluştu: {str(e)}")

@app.post("/predict/nutrition/")
async def predict_nutrition(request: NutritionRequest):
    """
    Beslenme değerlerine göre yemek önerileri sunar.
    
    Parametreler:
    - kalori: Hedef kalori miktarı
    - yag: Yağ miktarı (gram)
    - doymus_yag: Doymuş yağ miktarı (gram)
    - kolesterol: Kolesterol miktarı (mg)
    - sodyum: Sodyum miktarı (mg)
    - karbonhidrat: Karbonhidrat miktarı (gram)
    - lif: Lif miktarı (gram)
    - seker: Şeker miktarı (gram)
    - protein: Protein miktarı (gram)
    - n_recommendations: Kaç öneri döndürüleceği (varsayılan 5)
    """
    try:
        # Model ve veriyi yükle
        model = model_yukle()
        veri = veri_yukle()
        
        if model is None or veri is None:
            return format_response(False, None, "Model veya veri yüklenemedi. Sunucu hatası.")
        
        # Girdi değerlerini al
        girdi = [
            request.kalori,
            request.yag,
            request.doymus_yag,
            request.kolesterol,
            request.sodyum,
            request.karbonhidrat,
            request.lif,
            request.seker,
            request.protein
        ]
        
        # Diyet önerisi oluştur
        oneriler = diyet_oner(model, veri, girdi, request.n_recommendations)
        
        if oneriler is None or len(oneriler) == 0:
            return format_response(False, None, "Öneri oluşturulamadı.")
        
        # Yanıt formatını hazırla
        sonuclar = []
        for _, oneri in oneriler.iterrows():
            # Malzemeleri düzenle
            try:
                malzemeler = str(oneri.get('RecipeIngredientParts', '')).strip('c()')
                malzemeler = malzemeler.replace('"', '').split(', ')
            except:
                malzemeler = []
                
            # Tarif adımlarını düzenle
            try:
                tarifler = str(oneri.get('RecipeInstructions', '')).strip('c()')
                tarifler = tarifler.replace('"', '').split(', ')
            except:
                tarifler = []
                
            sonuclar.append({
                'name': oneri.get('Name', ''),
                'calories': float(oneri.get('Calories', 0)),
                'protein': float(oneri.get('ProteinContent', 0)),
                'carbs': float(oneri.get('CarbohydrateContent', 0)),
                'fat': float(oneri.get('FatContent', 0)),
                'ingredients': malzemeler,
                'instructions': tarifler
            })
            
        return format_response(True, {
            'recommendations': sonuclar,
            'input': {
                'kalori': request.kalori,
                'yag': request.yag,
                'protein': request.protein,
                'karbonhidrat': request.karbonhidrat
            }
        }, "Diyet önerileri başarıyla oluşturuldu.")
            
    except Exception as e:
        logger.error(f"Diyet önerisi endpoint hatası: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.post("/predict/simple-nutrition/")
async def predict_simple_nutrition(data: dict, db: Session = Depends(get_db)):
    """
    Basit beslenme değerleri ile kalori tahmini yapar.
    
    Bu endpoint karbonhidrat, protein ve yağ değerlerine göre kalori tahmini yapar.
    """
    try:
        # Model dosyasının yolu
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'trained_model.pkl')
        
        print(f"Model dosya yolu: {model_path}")
        print(f"Dosya mevcut mu: {os.path.exists(model_path)}")
        
        # Modeli yükle
        model = joblib.load(model_path)
        
        # Gerekli özellikleri al
        features = pd.DataFrame({
            'carbs': [data.get('carbs', 0)],
            'protein': [data.get('protein', 0)],
            'fats': [data.get('fats', 0)]
        })
        
        print(f"Girdi özellikleri: {features}")
        
        # Tahmin yap
        prediction = model.predict(features)[0]
        
        return format_response(True, {
            "predicted_calories": float(prediction),
            "input_features": data
        }, "Kalori tahmini başarıyla yapıldı.")
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Hata detayı: {error_detail}")
        return format_response(False, None, f"Tahmin yapılırken bir hata oluştu: {str(e)}")

@app.post("/predict/nutrition-profile/")
async def predict_nutrition_profile(request: ProfileRequest):
    """
    Hazır beslenme profillerinden yemek önerileri sunar.
    
    Parametreler:
    - profile: Beslenme profili (dusuk_kalorili, yuksek_proteinli, dusuk_karbonhidratli, vejetaryen)
    - n_recommendations: Kaç öneri döndürüleceği (varsayılan 5)
    """
    try:
        # Model ve veriyi yükle
        model = model_yukle()
        veri = veri_yukle()
        
        if model is None or veri is None:
            return format_response(False, None, "Model veya veri yüklenemedi. Sunucu hatası.")
        
        # Profil değerlerini al
        girdi = hazir_profil_degerlerini_al(request.profile)
        
        if girdi is None:
            return format_response(False, None, "Geçersiz profil seçimi.")
        
        # Diyet önerisi oluştur
        oneriler = diyet_oner(model, veri, girdi, request.n_recommendations)
        
        if oneriler is None or len(oneriler) == 0:
            return format_response(False, None, "Öneri oluşturulamadı.")
        
        # Yanıt formatını hazırla
        sonuclar = []
        for _, oneri in oneriler.iterrows():
            # Malzemeleri düzenle
            try:
                malzemeler = str(oneri.get('RecipeIngredientParts', '')).strip('c()')
                malzemeler = malzemeler.replace('"', '').split(', ')
            except:
                malzemeler = []
                
            # Tarif adımlarını düzenle
            try:
                tarifler = str(oneri.get('RecipeInstructions', '')).strip('c()')
                tarifler = tarifler.replace('"', '').split(', ')
            except:
                tarifler = []
                
            sonuclar.append({
                'name': oneri.get('Name', ''),
                'calories': float(oneri.get('Calories', 0)),
                'protein': float(oneri.get('ProteinContent', 0)),
                'carbs': float(oneri.get('CarbohydrateContent', 0)),
                'fat': float(oneri.get('FatContent', 0)),
                'ingredients': malzemeler,
                'instructions': tarifler
            })
            
        return format_response(True, {
            'profile': request.profile,
            'recommendations': sonuclar
        }, "Diyet önerileri başarıyla oluşturuldu.")
            
    except Exception as e:
        logger.error(f"Profil bazlı diyet önerisi endpoint hatası: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.post("/predict/user-nutrition/")
async def predict_user_nutrition(
    goal: str = Body("maintenance"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcının bilgilerine göre kalori ihtiyacını ve öğün dağılımını hesaplar.
    
    Parametreler:
    - goal: Hedef ("maintenance", "weight_loss" veya "muscle_building")
    """
    try:
        # Kullanıcının kullanıcı tipi kontrolü
        if not hasattr(current_user, 'user_id'):
            return format_response(False, None, "Bu işlem için kullanıcı olarak giriş yapmalısınız")
        
        # Kullanıcı bilgilerini al
        weight = current_user.weight
        height = current_user.height
        age = current_user.age
        gender = current_user.gender
        
        # Gerekli alanların eksikliği kontrolü
        if not all([weight, height, age, gender]):
            missing_fields = []
            if not weight: missing_fields.append("kilo")
            if not height: missing_fields.append("boy")
            if not age: missing_fields.append("yaş")
            if not gender: missing_fields.append("cinsiyet")
            
            return format_response(False, None, f"Lütfen profil bilgilerinizi güncelleyin. Eksik bilgiler: {', '.join(missing_fields)}")
        
        # Aktivite seviyesi kontrolü
        activity_level = getattr(current_user, 'activity_level', "sedentary")
        if not activity_level:
            activity_level = "sedentary"
        
        # Günlük kalori ihtiyacı hesaplama
        total_calories, bke = daily_calorie_requirements(weight, height, age, gender, activity_level)
        
        # Hedef düzenleme (kilo verme ise %15 azalt, kas kazanma ise %10 arttır)
        if goal == "weight_loss":
            total_calories = total_calories * 0.85  # %15 azalt
        elif goal == "muscle_building":
            total_calories = total_calories * 1.10  # %10 arttır
        
        # Öğün dağılımı
        meals = meal_distribution(total_calories)
        
        # Makro besin dağılımı
        macros = calculate_macros(total_calories, weight, goal)
        
        # İdeal kilo
        ideal = ideal_weight(height, gender)
        
        return format_response(True, {
            "total_calories": round(total_calories, 2),
            "bke": round(bke, 2),
            "status": "Obez" if bke >= 30 else "Kilolu" if bke >= 25 else "Normal" if bke >= 18.5 else "Zayıf",
            "ideal_weight": round(ideal, 2),
            "weight_difference": round(weight - ideal, 2),
            "meals": {k: round(v, 2) for k, v in meals.items()},
            "macros": {
                "protein": round(macros["protein_g"], 2),
                "carbs": round(macros["carbs_g"], 2),
                "fat": round(macros["fat_g"], 2)
            }
        }, "Kalori ihtiyacınız ve öğün dağılımınız başarıyla hesaplandı.")
            
    except Exception as e:
        logger.error(f"Kullanıcı beslenme analizi hatası: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

@app.post("/predict/calorie-calculator/")
async def calculate_calories(request: CalorieRequest):
    """
    Formdan gelen verilerle kalori ihtiyacı ve öğün dağılımını hesaplar.
    
    Parametreler:
    - weight: Ağırlık (kg)
    - height: Boy (cm)
    - age: Yaş
    - gender: Cinsiyet ("male" veya "female")
    - activity_level: Aktivite seviyesi ("sedentary", "active", "very active")
    """
    try:
        # Günlük kalori ihtiyacı hesaplama
        total_calories, bke = daily_calorie_requirements(
            request.weight, request.height, request.age, request.gender, request.activity_level
        )
        
        # Öğün dağılımı
        meals = meal_distribution(total_calories)
        
        # Makro besin dağılımı
        macros = calculate_macros(total_calories, request.weight)
        
        # İdeal kilo
        ideal = ideal_weight(request.height, request.gender)
        
        return format_response(True, {
            "total_calories": round(total_calories, 2),
            "bke": round(bke, 2),
            "status": "Obez" if bke >= 30 else "Kilolu" if bke >= 25 else "Normal" if bke >= 18.5 else "Zayıf",
            "ideal_weight": round(ideal, 2),
            "weight_difference": round(request.weight - ideal, 2),
            "meals": {k: round(v, 2) for k, v in meals.items()},
            "macros": {
                "protein": round(macros["protein_g"], 2),
                "carbs": round(macros["carbs_g"], 2),
                "fat": round(macros["fat_g"], 2)
            }
        }, "Kalori ihtiyacınız ve öğün dağılımınız başarıyla hesaplandı.")
            
    except Exception as e:
        logger.error(f"Kalori hesaplama hatası: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(False, None, f"Bir hata oluştu: {str(e)}")

# Randevu işlemleri
@app.post("/appointments/")
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni bir randevu oluşturur"""
    # token_data yerine current_user kullan
    
    # Randevu oluştur
    db_appointment = Appointment(
        user_id=appointment_data.user_id,
        dietitian_id=appointment_data.dietitian_id,
        date_time=appointment_data.date_time,
        status=appointment_data.status
    )
    
    try:
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return format_response(True, db_appointment, "Randevu başarıyla oluşturuldu.")
    except Exception as e:
        db.rollback()
        return format_response(False, None, f"Randevu oluşturulurken bir hata oluştu: {str(e)}")

@app.get("/appointments/{appointment_id}")
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Belirli bir randevuyu getirir"""
    db_appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    
    if not db_appointment:
        return format_response(False, None, "Randevu bulunamadı")
    
    return format_response(True, db_appointment, "Randevu başarıyla getirildi.")

@app.get("/users/{user_id}/appointments/")
async def get_user_appointments(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının randevularını getirir"""
    db_appointments = db.query(Appointment).filter(Appointment.user_id == user_id).all()
    
    return format_response(True, db_appointments, "Kullanıcı randevuları başarıyla getirildi.")

@app.get("/dietitians/{dietitian_id}/appointments/")
async def get_dietitian_appointments(
    dietitian_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Diyetisyenin randevularını getirir"""
    db_appointments = db.query(Appointment).filter(Appointment.dietitian_id == dietitian_id).all()
    
    return format_response(True, db_appointments, "Diyetisyen randevuları başarıyla getirildi.")

@app.put("/appointments/{appointment_id}")
async def update_appointment_status(
    appointment_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Randevu durumunu günceller"""
    db_appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    
    if not db_appointment:
        return format_response(False, None, "Randevu bulunamadı")
    
    db_appointment.status = status
    
    try:
        db.commit()
        db.refresh(db_appointment)
        return format_response(True, db_appointment, "Randevu durumu başarıyla güncellendi.")
    except Exception as e:
        db.rollback()
        return format_response(False, None, f"Randevu durumu güncellenirken bir hata oluştu: {str(e)}")

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

# Debug modu ayarı
app.debug = True  # Geliştirme ortamında debug modu açık

# Uygulamayı başlatmak için (uvicorn ile çalıştırılabilir)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)