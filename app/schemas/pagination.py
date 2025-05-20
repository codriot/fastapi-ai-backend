from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Sayfalanmış yanıt için genel model"""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
