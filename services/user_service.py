from firebase import db
from models.user import User

def add_user(user: User):
    """ Kullanıcıyı Firestore veritabanına ekler """
    doc_ref = db.collection("users").document(user.uid)
    doc_ref.set(user.dict())
    return {"message": "Kullanıcı başarıyla eklendi"}

def get_user(uid: str):
    """ Kullanıcıyı Firestore'dan getirir """
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {"error": "Kullanıcı bulunamadı"}

def delete_user(uid: str):
    """ Kullanıcıyı Firestore'dan siler """
    db.collection("users").document(uid).delete()
    return {"message": "Kullanıcı başarıyla silindi"}
