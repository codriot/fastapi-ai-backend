from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.base import get_db
from app.models.nutrition_model import (
    NutritionRequest,
    ProfileRequest,
    CalorieRequest,
    CalorieResponse,
    NutritionProfile,
    calculate_bke,
    mifflin_st_jeor,
    harris_benedict,
    ideal_weight,
    daily_calorie_requirements,
    meal_distribution,
    calculate_macros,
    model_yukle,
    veri_yukle,
    diyet_oner,
    hazir_profil_degerlerini_al
)
from app.core.security import get_current_active_user
from app.models.user import User
import os
import pandas as pd
import joblib

router = APIRouter()

@router.post("/recommend", response_model=List[Dict[str, Any]])
def recommend_nutrition(request: NutritionRequest):
    """Besin değerlerine göre diyet önerisi yapar"""
    try:
        # Model yükleme
        model = model_yukle()
        if model is None:
            raise HTTPException(status_code=500, detail="Model yüklenemedi")
        
        # Veri yükleme
        data = veri_yukle()
        if data is None:
            raise HTTPException(status_code=500, detail="Veri seti yüklenemedi")
        
        # Diyet önerisi için girdi değerlerini al
        input_values = [
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
        
        # Diyet önerisi yap
        recommendations = diyet_oner(
            model=model,
            veri=data,
            girdi_degerleri=input_values,
            n_neighbors=request.n_recommendations
        )
        
        if recommendations is None or len(recommendations) == 0:
            raise HTTPException(status_code=404, detail="Uygun öneri bulunamadı")
        
        # Veriyi JSON formatına dönüştür
        result = recommendations.to_dict(orient="records")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diyet önerisi oluşturma hatası: {str(e)}")

@router.post("/recommend-by-profile", response_model=List[Dict[str, Any]])
def recommend_by_profile(request: ProfileRequest):
    """Hazır profillere göre diyet önerisi yapar"""
    try:
        # Profil değerlerini al
        profile_values = hazir_profil_degerlerini_al(request.profile)
        if profile_values is None:
            raise HTTPException(status_code=400, detail="Geçersiz profil tipi")
        
        # Model yükleme
        model = model_yukle()
        if model is None:
            raise HTTPException(status_code=500, detail="Model yüklenemedi")
        
        # Veri yükleme
        data = veri_yukle()
        if data is None:
            raise HTTPException(status_code=500, detail="Veri seti yüklenemedi")
        
        # Diyet önerisi yap
        recommendations = diyet_oner(
            model=model,
            veri=data,
            girdi_degerleri=profile_values,
            n_neighbors=request.n_recommendations
        )
        
        if recommendations is None or len(recommendations) == 0:
            raise HTTPException(status_code=404, detail="Uygun öneri bulunamadı")
        
        # Veriyi JSON formatına dönüştür
        result = recommendations.to_dict(orient="records")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diyet önerisi oluşturma hatası: {str(e)}")

@router.get("/calculate-calories", response_model=CalorieResponse)
def calculate_daily_calories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Giriş yapmış kullanıcının profil bilgilerine göre günlük kalori ihtiyacını hesaplar"""
    try:
        # Kullanıcı bilgilerini kontrol et
        if not current_user.weight or not current_user.height or not current_user.age or not current_user.gender or not current_user.activity_level:
            raise HTTPException(
                status_code=400, 
                detail="Kalori hesaplaması için kullanıcı profilinde eksik bilgiler var. Lütfen profil bilgilerinizi tamamlayın."
            )
        
        # Kullanıcı bilgilerini kullanarak kalori ihtiyacını hesapla
        total_calories, bke_value = daily_calorie_requirements(
            weight=current_user.weight,
            height=current_user.height,
            age=current_user.age,
            gender=current_user.gender.lower(),
            activity_level=current_user.activity_level.lower()
        )
        
        # Öğünlere dağılımı hesapla
        meals = meal_distribution(total_calories)
        
        # İdeal kiloyu hesapla
        ideal_weight_value = ideal_weight(current_user.height, current_user.gender.lower())
        
        # Makro besinleri hesapla - kullanıcının hedefine göre belirle
        goal = "maintenance"
        if current_user.goal:
            if "kas" in current_user.goal.lower() or "muscle" in current_user.goal.lower():
                goal = "muscle_building"
            elif "kilo verme" in current_user.goal.lower() or "weight loss" in current_user.goal.lower():
                goal = "weight_loss"
        
        macros = calculate_macros(total_calories, current_user.weight, goal)
        
        # Yanıtı oluştur
        response = {
            "total_calories": round(total_calories, 2),
            "meals": {k: round(v, 2) for k, v in meals.items()},
            "bke": round(bke_value, 2),
            "ideal_weight": round(ideal_weight_value, 2),
            "protein_need": round(macros["protein_g"], 2),
            "carbs_need": round(macros["carbs_g"], 2),
            "fat_need": round(macros["fat_g"], 2)
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kalori hesaplama hatası: {str(e)}")
        
# İstek gövdesiyle kalori hesaplaması için eski endpoint'i koruyalım
@router.post("/calculate-calories-by-request", response_model=CalorieResponse)
def calculate_daily_calories_by_request(request: CalorieRequest):
    """İstek gövdesindeki değerlere göre günlük kalori ihtiyacını hesaplar"""
    try:
        # Kalori ihtiyacını hesapla
        total_calories, bke_value = daily_calorie_requirements(
            weight=request.weight,
            height=request.height,
            age=request.age,
            gender=request.gender,
            activity_level=request.activity_level
        )
        
        # Öğünlere dağılımı hesapla
        meals = meal_distribution(total_calories)
        
        # İdeal kiloyu hesapla
        ideal_weight_value = ideal_weight(request.height, request.gender)
        
        # Makro besinleri hesapla
        macros = calculate_macros(total_calories, request.weight)
        
        # Yanıtı oluştur
        response = {
            "total_calories": round(total_calories, 2),
            "meals": {k: round(v, 2) for k, v in meals.items()},
            "bke": round(bke_value, 2),
            "ideal_weight": round(ideal_weight_value, 2),
            "protein_need": round(macros["protein_g"], 2),
            "carbs_need": round(macros["carbs_g"], 2),
            "fat_need": round(macros["fat_g"], 2)
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kalori hesaplama hatası: {str(e)}") 