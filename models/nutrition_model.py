"""
Diet App API - Nutrition Model

Diyet ve beslenme önerileri için model işlemleri
"""

import joblib
import numpy as np
import pandas as pd
import os
import logging
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel

# Loglama ayarları
logger = logging.getLogger(__name__)

# Yeni istek ve yanıt modelleri için sınıflar
class NutritionRequest(BaseModel):
    kalori: float
    yag: float
    doymus_yag: float
    kolesterol: float
    sodyum: float
    karbonhidrat: float
    lif: float
    seker: float
    protein: float
    n_recommendations: int = 5

class NutritionProfile(str, Enum):
    DUSUK_KALORILI = "dusuk_kalorili"
    YUKSEK_PROTEINLI = "yuksek_proteinli"
    DUSUK_KARBONHIDRATLI = "dusuk_karbonhidratli"
    VEJETARYEN = "vejetaryen"

class ProfileRequest(BaseModel):
    profile: NutritionProfile
    n_recommendations: int = 5

class CalorieRequest(BaseModel):
    weight: float  # kg cinsinden ağırlık
    height: float  # cm cinsinden boy
    age: int       # yaş
    gender: str    # "male" veya "female"
    activity_level: str  # "sedentary", "active", "very active"

class CalorieResponse(BaseModel):
    total_calories: float
    meals: Dict[str, float]
    bke: float
    ideal_weight: float
    protein_need: float
    carbs_need: float
    fat_need: float

# Kalori hesaplama fonksiyonları
def calculate_bke(weight, height):
    """Calculate Body Mass Index (BMI)"""
    height_m = height / 100  # Convert height to meters
    return weight / (height_m ** 2)

def mifflin_st_jeor(weight, height, age, gender):
    """Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor equation."""
    if gender == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def harris_benedict(weight, height, age, gender):
    """Calculate Basal Metabolic Rate (BMR) using Harris-Benedict equation."""
    if gender == "male":
        return 66 + (13.75 * weight) + (5 * height) - (6.8 * age)
    else:
        return 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)

def ideal_weight(height, gender):
    """Calculate ideal weight based on height and gender."""
    if gender == "male":
        return 50 + 0.91 * (height - 150)
    else:
        return 45.5 + 0.91 * (height - 150)

def daily_calorie_requirements(weight, height, age, gender, activity_level):
    """Calculate daily calorie requirements."""
    bke = calculate_bke(weight, height)
    
    if bke >= 25:  # Obez
        ideal_weight_value = ideal_weight(height, gender)
        adjusted_weight = weight - (weight - ideal_weight_value) * 0.25
        bmr = mifflin_st_jeor(adjusted_weight, height, age, gender)
    elif 18.5 <= bke < 25:  # Normal
        bmr = harris_benedict(weight, height, age, gender)
    else:  # Zayıf
        bmr = harris_benedict(weight, height, age, gender)

    # Adjust for activity level
    if activity_level == "sedentary":
        total_calories = bmr * 1.3
    elif activity_level == "active":
        total_calories = bmr * 1.7
    else:  # Very active
        total_calories = bmr * 2

    return total_calories, bke

def meal_distribution(total_calories):
    """Distribute total calories among meals."""
    return {
        "Breakfast": total_calories * 0.25,
        "Lunch": total_calories * 0.35,
        "Dinner": total_calories * 0.30,
        "Snacks": total_calories * 0.10
    }

def calculate_macros(total_calories, weight, goal="maintenance"):
    """Calculate macronutrient distribution based on goal."""
    # Protein ihtiyacı: 1.6-2.2 g/kg (weight) for muscle building, 1.2-1.6 for maintenance
    if goal == "muscle_building":
        protein_per_kg = 2.0
        fat_percentage = 0.25
    elif goal == "weight_loss":
        protein_per_kg = 1.8
        fat_percentage = 0.20
    else:  # maintenance
        protein_per_kg = 1.4
        fat_percentage = 0.30
    
    # Protein (gram)
    protein_g = weight * protein_per_kg
    protein_cal = protein_g * 4
    
    # Yağ (gram)
    fat_cal = total_calories * fat_percentage
    fat_g = fat_cal / 9
    
    # Karbonhidrat (gram)
    remaining_cal = total_calories - protein_cal - fat_cal
    carbs_g = remaining_cal / 4
    
    return {
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g
    }

# Diyet önerisi için yardımcı fonksiyonlar
def model_yukle(model_yolu=None):
    """Eğitilmiş modeli yükler"""
    if model_yolu is None:
        model_yolu = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'trained_model.pkl')
    
    try:
        # Alternatif yolları da dene
        if not os.path.exists(model_yolu):
            alternative_paths = [
                '/opt/render/project/src/models/trained_model.pkl',
                '/app/models/trained_model.pkl',
                './models/trained_model.pkl'
            ]
            
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    model_yolu = alt_path
                    break
        
        logger.info(f"Model yükleniyor: {model_yolu}")
        logger.info(f"Dosya mevcut mu: {os.path.exists(model_yolu)}")
        
        if not os.path.exists(model_yolu):
            logger.error("Model dosyası bulunamadı!")
            return None
            
        model = joblib.load(model_yolu)
        logger.info(f"Model başarıyla yüklendi")
        return model
    except Exception as e:
        logger.error(f"Model yükleme hatası: {str(e)}")
        return None

def veri_yukle(veri_yolu=None):
    """Diyet listesi verilerini yükler"""
    if veri_yolu is None:
        veri_yolu = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'dataset.csv')
    
    try:
        # Alternatif yolları da dene
        if not os.path.exists(veri_yolu):
            alternative_paths = [
                '/opt/render/project/src/data/dataset.csv',
                '/app/data/dataset.csv',
                './data/dataset.csv',
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'processed_data', 'dataset.csv')
            ]
            
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    veri_yolu = alt_path
                    break
        
        logger.info(f"Veri yükleniyor: {veri_yolu}")
        logger.info(f"Dosya mevcut mu: {os.path.exists(veri_yolu)}")
        
        if not os.path.exists(veri_yolu):
            logger.error("Veri dosyası bulunamadı!")
            return None
            
        df = pd.read_csv(veri_yolu)
        logger.info(f"Veri başarıyla yüklendi: {len(df)} kayıt")
        return df
    except Exception as e:
        logger.error(f"Veri yükleme hatası: {str(e)}")
        return None

def diyet_oner(model, veri, girdi_degerleri, n_neighbors=5):
    """Girdi değerlerine göre diyet önerisi yapar"""
    try:
        # Girdiyi numpy dizisine çevir
        girdi = np.array([girdi_degerleri])
        
        # Model kontrolü
        if 'knn' not in model.named_steps or 'scaler' not in model.named_steps:
            logger.error("Model yapısı beklenen formatta değil")
            return None
            
        # Modeli kullanarak en yakın komşuları bul
        en_yakin_komsular = model.named_steps['knn'].kneighbors(
            model.named_steps['scaler'].transform(girdi),
            n_neighbors=n_neighbors,
            return_distance=False
        )
        
        # Önerileri getir
        oneriler = veri.iloc[en_yakin_komsular[0]]
        return oneriler
    except Exception as e:
        logger.error(f"Diyet önerisi oluşturma hatası: {str(e)}")
        return None

def hazir_profil_degerlerini_al(profil):
    """Hazır beslenme profili değerlerini döndürür"""
    profiller = {
        NutritionProfile.DUSUK_KALORILI: [300, 10, 2, 30, 500, 40, 8, 10, 25],
        NutritionProfile.YUKSEK_PROTEINLI: [600, 25, 8, 100, 700, 30, 5, 5, 50],
        NutritionProfile.DUSUK_KARBONHIDRATLI: [500, 35, 12, 150, 600, 20, 10, 5, 40],
        NutritionProfile.VEJETARYEN: [450, 15, 3, 0, 400, 70, 15, 20, 20]
    }
    
    return profiller.get(profil)