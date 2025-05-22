import json
import asyncio
from typing import Dict, Union, List
from fastapi import HTTPException
from app.models.schemas import UserProfile, MealPlan, FoodItem, NutritionResponse
from app.models.combined_response import FoodNutrition, MealPlanWithNutrition
from app.services.openAI_services import get_meal_plan
from app.services.nutrition_service import get_food_nutrition, calculate_nutrition_for_foods

def get_item_name(item: Dict) -> str:
    """Get item name from different possible formats"""
    return item.get("item") or item.get("name", "")

def get_meal_type(item: Dict) -> str:
    """Get meal type from different possible formats"""
    return item.get("meal") or item.get("mealPlanType", "SNACK")

def get_quantity(item: Dict) -> float:
    """Get quantity from different possible formats"""
    return float(item.get("quantity") or item.get("totalFood", 1.0))

async def get_meal_plan_with_nutrition(user: UserProfile) -> MealPlanWithNutrition:
    """Generate a meal plan and calculate nutrition information for each food item"""
    try:
        # Get the meal plan
        meal_plan = await get_meal_plan(user)
        
        # Parse the meal plan data
        try:
            meal_plan_data = json.loads(meal_plan.meal_plan_text)
            if not isinstance(meal_plan_data, list):
                raise ValueError("Meal plan data should be a list")
        except json.JSONDecodeError as e:
            print(f"Error parsing meal plan JSON: {e}")
            raise HTTPException(status_code=500, detail="Invalid meal plan format")
            
        foods_nutrition: List[FoodNutrition] = []
        food_items = []

        # Create FoodItems for nutrition calculation
        for item in meal_plan_data:
            # Validate required fields
            if not isinstance(item, dict):
                print(f"Skipping invalid item: {item}")
                continue
            
            item_name = get_item_name(item)
            if not item_name:
                print(f"Skipping item without name: {item}")
                continue
            
            try:
                quantity = get_quantity(item)
                food_item = FoodItem(
                    meal=get_meal_type(item),
                    name=item_name.strip(),
                    quantity=quantity,
                    unit=item.get("unit", "g").lower(),
                    serving_size=quantity
                )
                food_items.append(food_item)
                print(f"Successfully created food item: {food_item}")
            except (ValueError, AttributeError) as e:
                print(f"Error creating food item: {e}, item: {item}")
                continue

        if not food_items:
            print("No valid food items found in meal plan")
            return MealPlanWithNutrition(
                meal_plan=meal_plan,
                foods_nutrition=[],
                total_nutrition=None
            )

        print(f"Processing {len(food_items)} food items")
        # Process all food items concurrently
        nutrition_results = await asyncio.gather(*[get_food_nutrition(item) for item in food_items])
        
        # Create FoodNutrition objects for each item
        for item, nutrition_data in zip(food_items, nutrition_results):
            if not nutrition_data:
                print(f"No nutrition data found for {item.name}")
                continue
                
            try:
                food_nutrition = FoodNutrition(
                    food_name=item.name,
                    meal_type=item.meal,
                    quantity=item.quantity,
                    unit=item.unit,
                    serving_size=item.serving_size,
                    nutrition=nutrition_data
                )
                foods_nutrition.append(food_nutrition)
                print(f"Added nutrition data for {item.name}")
            except (ValueError, AttributeError) as e:
                print(f"Error creating food nutrition object: {e}, item: {item}")
                continue
        
        # Calculate total nutrition for all foods
        total_nutrition = await calculate_nutrition_for_foods(food_items) if food_items else None
        
        return MealPlanWithNutrition(
            meal_plan=meal_plan,
            foods_nutrition=foods_nutrition,
            total_nutrition=total_nutrition
        )
        
    except Exception as e:
        print(f"Error processing meal plan nutrition: {str(e)}")
        return MealPlanWithNutrition(
            meal_plan=meal_plan,
            foods_nutrition=[],
            total_nutrition=None
        )