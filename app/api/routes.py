from fastapi import APIRouter, HTTPException, Body, Query
from app.models.shemas import UserProfile, MealPlan, FoodItem, NutritionResponse
from app.services.openAI_services import get_meal_plan
from app.services.nutrition_service import calculate_nutrition_for_foods
from app.services.combined_service import get_meal_plan_with_nutrition
from app.models.combined_response import MealPlanWithNutrition
from typing import List, Union

router = APIRouter()

@router.get("/health")
async def check_health():
    try:
        # Try to count documents to check database connection
        count = await MealPlan.count()
        return {
            "status": "healthy",
            "database": "connected",
            "message": f"Application is running and connected to MongoDB. Total meal plans: {count}"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@router.post("/meal-plans", response_model=Union[MealPlan, MealPlanWithNutrition])
async def create_meal_plan(user: UserProfile, include_nutrition: bool = Query(False, description="Include nutrition information for meal plan items")):
    """Create a new meal plan, optionally with nutrition information"""
    try:
        if include_nutrition:
            result = await get_meal_plan_with_nutrition(user)
            return result
        else:
            meal_plan = await get_meal_plan(user)
            return meal_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meal-plans/{meal_plan_id}", response_model=MealPlan)
async def get_meal_plan_by_id(meal_plan_id: str):
    """Get a specific meal plan by ID"""
    try:
        meal_plan = await MealPlan.get(meal_plan_id)
        if meal_plan is None:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        return meal_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meal-plans", response_model=List[MealPlan])
async def get_all_meal_plans(skip: int = 0, limit: int = 10):
    """Get all meal plans with pagination"""
    try:
        meal_plans = await MealPlan.find_all().skip(skip).limit(limit).to_list()
        return meal_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-nutrition", response_model=NutritionResponse)
async def calculate_nutrition(food_items: List[FoodItem] = Body(...)):
    """Calculate nutrition information for a list of food items"""
    try:
        result = await calculate_nutrition_for_foods(food_items)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))