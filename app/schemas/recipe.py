from pydantic import BaseModel
from typing import List, Optional

class Recipe(BaseModel):
    RecipeId: int
    Name: str
    CookTime: str
    PrepTime: str
    TotalTime: str
    RecipeIngredientParts: str
    Calories: float
    FatContent: float
    SaturatedFatContent: float
    CholesterolContent: float
    SodiumContent: float
    CarbohydrateContent: float
    FiberContent: float
    SugarContent: float
    ProteinContent: float
    RecipeInstructions: str
    
    class Config:
        from_attributes = True
