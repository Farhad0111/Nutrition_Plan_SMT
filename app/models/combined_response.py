from pydantic import BaseModel
from typing import Dict, Optional, List
from app.models.schemas import MealPlan, NutritionResponse

class FoodNutrition(BaseModel):
    food_name: str
    meal_type: str
    quantity: float
    unit: str
    serving_size: float
    nutrition: NutritionResponse

class MealPlanWithNutrition(BaseModel):
    meal_plan: MealPlan
    foods_nutrition: List[FoodNutrition]
    total_nutrition: Optional[NutritionResponse] = None