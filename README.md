# Diet App API

Bu proje, diyet ve beslenme takibi için geliştirilmiş bir FastAPI tabanlı backend uygulamasıdır. Yapay zeka destekli özellikler içerir ve kullanıcıların sağlıklı beslenme alışkanlıkları edinmelerine yardımcı olur.

## Özellikler

- **Kullanıcı Yönetimi**: Kayıt, giriş, JWT tabanlı kimlik doğrulama
- **Diyetisyen Entegrasyonu**: Diyetisyenler ve kullanıcılar arasında randevu sistemi
- **Besin Değeri Tahmini**: Karbonhidrat, protein ve yağ değerlerine göre kalori tahmini
- **Diyet Listesi Oluşturma**: Yapay zeka ile kişiselleştirilmiş diyet listeleri
- **Sosyal Platform**: Kullanıcıların paylaşım yapabildiği ve yorum yapabildiği post sistemi
- **İleri Veri Analitiği**: Beslenme verilerinin analizi ve raporlama

## Teknolojiler

- **FastAPI**: Yüksek performanslı REST API için
- **SQLAlchemy**: Veritabanı ORM
- **Poetry**: Bağımlılık yönetimi
- **JWT**: Kimlik doğrulama
- **Pandas & Scikit-learn**: Veri işleme ve makine öğrenme modelleri
- **Google Cloud Firestore**: Ek veri depolama (opsiyonel)

## Kurulum

### Poetry ile Kurulum (Önerilen)

```bash
# Poetry'i yükleyin
pip install -U poetry

# Bağımlılıkları yükleyin
poetry install

# Uygulamayı başlatın
poetry run uvicorn main:app --host 0.0.0.0
```

### Pip ile Kurulum

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
uvicorn main:app --host 0.0.0.0
```

## Proje Yapısı

- **main.py**: Ana uygulama ve API endpoint tanımları
- **database.py**: Veritabanı bağlantı yönetimi
- **models/**: Veritabanı modelleri ve şema tanımları
- **services/**: İş mantığı ve veritabanı işlemleri
- **script/**: Yardımcı script dosyaları ve diyet listesi algoritmaları
- **uploads/**: Kullanıcıların yüklediği dosyaların saklandığı klasör

## API Endpoints

### Kimlik Doğrulama
- `POST /token`: Token alma
- `POST /register/user`: Kullanıcı kaydı
- `POST /register/dietitian`: Diyetisyen kaydı
- `POST /login/`: Kullanıcı girişi

### Kullanıcı İşlemleri
- `GET /users/me`: Mevcut kullanıcı bilgilerini alma
- `PUT /users/me`: Kullanıcı bilgilerini güncelleme
- `DELETE /users/me`: Kullanıcı hesabını silme

### Beslenme ve Diyet
- `POST /predict/nutrition/`: Besin değerlerine göre kalori tahmini
- `POST /predict/diet-list/`: Kişiselleştirilmiş diyet listesi oluşturma
- `POST /predict/recipe-recommendations/`: Tarif önerileri

### Sosyal Platform
- `POST /post/`: Yeni gönderi oluşturma
- `POST /comments/`: Yorumlar
- `GET /uploads/{filename}`: Yüklenen dosyalara erişim

### Randevu Sistemi
- `POST /appointments/`: Randevu oluşturma
- `GET /appointments/{appointment_id}`: Randevu detayları
- `GET /users/{user_id}/appointments/`: Kullanıcı randevuları
- `GET /dietitians/{dietitian_id}/appointments/`: Diyetisyen randevuları

## Yapay Zeka Özellikleri

Projede entegre edilmiş yapay zeka özellikleri:
- Besin değeri analizi ve kalori tahmini
- Özelleştirilmiş diyet listeleri oluşturma
- Benzer tarifleri bulma ve önerme

## Geliştirme

API'yi geliştirme modunda çalıştırmak için:

```bash
poetry run uvicorn main:app --reload
```

API dokümantasyonuna erişmek için tarayıcınızda `http://localhost:8000/docs` adresini ziyaret edin.

## Lisans

Bu proje [LICENSE] altında lisanslanmıştır.

