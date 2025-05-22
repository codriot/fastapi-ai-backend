from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.recipe import Recipe
from app.services.recipe_service import get_breakfast_recipes, get_lunch_recipes, get_dinner_recipes

router = APIRouter()

@router.get("/breakfast", response_model=List[Recipe])
def get_breakfast(db: Session = Depends(get_db)):
    """Kahvaltı için tarif önerileri getirir"""
    return get_breakfast_recipes()

@router.get("/lunch", response_model=List[Recipe])
def get_lunch(db: Session = Depends(get_db)):
    """Öğle yemeği için tarif önerileri getirir"""
    return get_lunch_recipes()

@router.get("/dinner", response_model=List[Recipe])
def get_dinner(db: Session = Depends(get_db)):
    """Akşam yemeği için tarif önerileri getirir"""
    return get_dinner_recipes()
