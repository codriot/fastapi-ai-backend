from firebase import db, auth
from models.user import User
from fastapi import HTTPException
from datetime import datetime

def add_user(user: User):
    """ Kullanıcıyı Firestore veritabanına ekler ve token döndürür """
    try:
        # Firebase Authentication'da kullanıcı oluştur
        firebase_user = auth.create_user(email=user.email, password=user.password)

        # Kullanıcı UID'sini al
        user.uid = firebase_user.uid
        user.created_at = datetime.utcnow()

        # Firestore'a kaydet
        doc_ref = db.collection("user").document(user.uid)
        doc_ref.set(user.dict())

        # Kullanıcı için Firebase Custom Token oluştur
        token = auth.create_custom_token(user.uid)

        return {
            "message": "Kullanıcı başarıyla eklendi",
            "uid": user.uid,
            "token": token.decode("utf-8")  # Token döndür
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_user(uid: str):
    """ Kullanıcıyı Firestore'dan getir ve yeni bir token üret """
    doc_ref = db.collection("user").document(uid)
    doc = doc_ref.get()
    
    if doc.exists:
        # Kullanıcı bilgilerini al
        user_data = doc.to_dict()
        
        # Kullanıcı için yeni bir token üret
        token = auth.create_custom_token(uid)
        
        user_data["token"] = token.decode("utf-8")  # Token ekle
        return user_data

    return {"error": "Kullanıcı bulunamadı"}

def delete_user(uid: str):
    """ Kullanıcıyı Firestore'dan siler """
    db.collection("users").document(uid).delete()
    return {"message": "Kullanıcı başarıyla silindi"}
