from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    uid: str
    email: str
    password: str  # Güvenlik için hashlenmeli
    apple_login: Optional[str] = None
    google_login: Optional[str] = None
    gender: str
    age: int
    weight: float
    height: float
    favorite_foods: List[str]
    goal: str
    dietitian_id: Optional[str] = None
