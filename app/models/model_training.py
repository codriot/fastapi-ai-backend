import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import os

def load_model(model_path=None):
    """
    Eğitilmiş modeli yükler veya bulunamazsa yeni bir model eğitir
    """
    if model_path is None:
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained_model.pkl')
    
    try:
        # Eğitilmiş modeli yüklemeye çalış
        model = joblib.load(model_path)
        print("Model başarıyla yüklendi.")
        return model
    except:
        print("Model bulunamadı, yeni bir model eğitiliyor...")
        # Örnek veri oluştur (gerçek veri yoksa)
        data = generate_sample_data()
        
        # Modeli eğit
        model = train_model(data)
        
        # Modeli kaydet
        joblib.dump(model, model_path)
        print(f"Model eğitildi ve kaydedildi: {model_path}")
        return model

def generate_sample_data(n_samples=1000):
    """
    Test amaçlı örnek veri oluşturur
    """
    np.random.seed(42)
    
    # Beslenme değerleri için rastgele değerler oluştur
    carbs = np.random.uniform(0, 200, n_samples)
    protein = np.random.uniform(0, 100, n_samples)
    fats = np.random.uniform(0, 80, n_samples)
    
    # Kalori hesapla (gerçek bir formül ile)
    # Karbonhidrat: 4 kcal/g, Protein: 4 kcal/g, Yağ: 9 kcal/g
    calories = (carbs * 4) + (protein * 4) + (fats * 9)
    
    # Biraz rastgele gürültü ekle
    calories = calories + np.random.normal(0, 50, n_samples)
    
    # DataFrame oluştur
    data = pd.DataFrame({
        'carbs': carbs,
        'protein': protein,
        'fats': fats,
        'calories': calories
    })
    
    return data

def train_model(data):
    """
    Verilen verilerle bir tahmin modeli eğitir
    """
    # Özellikleri ve hedefi ayır
    X = data[['carbs', 'protein', 'fats']]
    y = data['calories']
    
    # Eğitim ve test verisi olarak ayır
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model oluştur ve eğit
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Model performansını değerlendir
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performansı - MAE: {mae:.2f}, R2: {r2:.2f}")
    
    return model

if __name__ == "__main__":
    # Model eğitimi ve değerlendirmesi için test
    data = generate_sample_data(2000)
    model = train_model(data)
    
    # Modeli kaydet
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model kaydedildi: {model_path}")