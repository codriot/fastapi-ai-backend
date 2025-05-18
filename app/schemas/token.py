from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenResponse(BaseModel):
    user: dict
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None
    role: str | None = None 