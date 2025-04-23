from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any

class Dietitian(BaseModel):
    uid: str
    email: str
    password: str
    name: str
    experience: str
    specialization: str
    created_at: datetime

class DietitianCreate(BaseModel):
    email: str
    password: str
    name: str
    experience: str
    specialization: str

def dietitian_to_dict(dietitian: DietitianCreate) -> Dict[str, Any]:
    """Diyetisyen kayıt verilerini dict'e dönüştürür"""
    dietitian_data = {
        "email": dietitian.email,
        "name": dietitian.name,
        "role": "dietitian",
        "experience": dietitian.experience,
        "specialization": dietitian.specialization,
        "created_at": datetime.now()
    }
    return dietitian_data