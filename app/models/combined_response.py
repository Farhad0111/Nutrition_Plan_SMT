from pydantic import BaseModel
from app.models.shemas import MealPlan, NutritionResponse

class MealPlanWithNutrition(BaseModel):
    meal_plan: MealPlan
    nutrition: NutritionResponse