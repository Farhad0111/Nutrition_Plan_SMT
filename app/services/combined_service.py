import json
from typing import Dict, Union
from app.models.shemas import UserProfile, MealPlan, FoodItem, NutritionResponse
from app.services.openAI_services import get_meal_plan
from app.services.nutrition_service import calculate_nutrition_for_foods

async def get_meal_plan_with_nutrition(user: UserProfile) -> Dict[str, Union[MealPlan, NutritionResponse]]:
    """Generate a meal plan and calculate nutrition information for it"""
    # Get the meal plan
    meal_plan = await get_meal_plan(user)
    
    # Extract food items
    try:
        meal_plan_data = json.loads(meal_plan.meal_plan_text)
        food_items = []
        
        for item in meal_plan_data:
            food_item = FoodItem(
                name=item.get("name"),
                totalFood=item.get("totalFood", 1.0),
                unit=item.get("unit", "serving"),
                servingSize=item.get("servingSize", 1.0)
            )
            food_items.append(food_item)
        
        # Calculate nutrition
        nutrition = await calculate_nutrition_for_foods(food_items)
        
        return {
            "meal_plan": meal_plan,
            "nutrition": nutrition
        }
    except Exception as e:
        # If anything fails with nutrition calculation, just return the meal plan
        return {
            "meal_plan": meal_plan,
            "nutrition": None
        }