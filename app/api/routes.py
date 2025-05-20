from fastapi import APIRouter, HTTPException, Body, Query
from app.models.shemas import UserProfile, MealPlan, FoodItem, NutritionResponse
from app.services.openAI_services import get_meal_plan
from app.services.nutrition_service import calculate_nutrition_for_foods
from app.services.combined_service import get_meal_plan_with_nutrition
from app.models.combined_response import MealPlanWithNutrition
from typing import List, Union, Dict

router = APIRouter()

# In-memory storage to replace MongoDB
meal_plans_db: Dict[str, MealPlan] = {}

@router.get("/health")
async def check_health():
    return {
        "status": "healthy",
        "message": f"Application is running. Total meal plans in memory: {len(meal_plans_db)}"
    }

@router.post("/meal-plans", response_model=Union[MealPlan, MealPlanWithNutrition])
async def create_meal_plan(user: UserProfile, include_nutrition: bool = Query(False, description="Include nutrition information for meal plan items")):
    """Create a new meal plan, optionally with nutrition information"""
    try:
        if include_nutrition:
            result = await get_meal_plan_with_nutrition(user)
            # Store the meal plan in our in-memory db
            if 'meal_plan' in result and hasattr(result['meal_plan'], 'id'):
                meal_plans_db[result['meal_plan'].id] = result['meal_plan']
            return result
        else:
            meal_plan = await get_meal_plan(user)
            # Store in our in-memory db
            meal_plans_db[meal_plan.id] = meal_plan
            return meal_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meal-plans/{meal_plan_id}", response_model=MealPlan)
async def get_meal_plan_by_id(meal_plan_id: str):
    """Get a specific meal plan by ID"""
    if meal_plan_id not in meal_plans_db:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plans_db[meal_plan_id]

@router.get("/meal-plans", response_model=List[MealPlan])
async def get_all_meal_plans(skip: int = 0, limit: int = 10):
    """Get all meal plans with pagination"""
    plans = list(meal_plans_db.values())
    start = min(skip, len(plans))
    end = min(skip + limit, len(plans))
    return plans[start:end]

@router.post("/calculate-nutrition", response_model=NutritionResponse)
async def calculate_nutrition(food_items: List[FoodItem] = Body(...)):
    """Calculate nutrition information for a list of food items"""
    try:
        result = await calculate_nutrition_for_foods(food_items)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))