import asyncio
import aiohttp
from typing import List, Dict, Optional
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.schemas import FoodItem, NutrientInfo, NutritionResponse

# Token cache
token_data = {
    "access_token": None,
    "expires_at": None
}

async def get_access_token() -> str:
    """Get a valid access token for the FatSecret API"""
    global token_data
    
    current_time = datetime.now()
    
    # Check if we have a valid token
    if token_data["access_token"] and token_data["expires_at"] and current_time < token_data["expires_at"]:
        return token_data["access_token"]
    
    # Request new token
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': settings.FAT_SECRET_CLIENT_ID,
        'client_secret': settings.FAT_SECRET_CLIENT_SECRET,
        'scope': 'basic'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(settings.FAT_SECRET_AUTH_URL, data=auth_data) as response:
                if response.status != 200:
                    raise HTTPException(status_code=500, detail="Failed to authenticate with FatSecret API")
                token_info = await response.json()
                
                # Save token with expiration time
                token_data["access_token"] = token_info["access_token"]
                token_data["expires_at"] = current_time + timedelta(seconds=token_info["expires_in"] - 300)
                
                return token_data["access_token"]
        except Exception as e:
            print(f"Error getting access token: {e}")
            raise HTTPException(status_code=500, detail="Failed to authenticate with FatSecret API")

async def get_food_nutrition(item: FoodItem) -> Optional[Dict]:
    """Get nutrition data for a food item from FatSecret API"""
    token = await get_access_token()
    
    async with aiohttp.ClientSession() as session:
        # First, search for the food
        try:
            # Search for food
            search_params = {
                'method': 'foods.search',
                'search_expression': item.name,
                'format': 'json'
            }
            headers = {'Authorization': f'Bearer {token}'}
            
            async with session.get(settings.FAT_SECRET_BASEURL, params=search_params, headers=headers) as response:
                if response.status != 200:
                    print(f"Error searching for food {item.name}: {response.status}")
                    return None
                    
                search_data = await response.json()
                if 'foods' not in search_data or 'food' not in search_data['foods']:
                    print(f"No food found for {item.name}")
                    return None
                
                # Get the first matching food
                foods = search_data['foods']['food']
                food_id = foods[0]['food_id'] if isinstance(foods, list) else foods['food_id']
                
                # Get detailed nutrition data
                detail_params = {
                    'method': 'food.get.v2',
                    'food_id': food_id,
                    'format': 'json'
                }
                
                async with session.get(settings.FAT_SECRET_BASEURL, params=detail_params, headers=headers) as detail_response:
                    if detail_response.status != 200:
                        print(f"Error getting nutrition data for {item.name}: {detail_response.status}")
                        return None
                        
                    food_data = await detail_response.json()
                    if 'food' not in food_data or 'servings' not in food_data['food']:
                        print(f"No serving data for {item.name}")
                        return None
                    
                    servings = food_data['food']['servings']
                    serving = servings['serving'][0] if isinstance(servings['serving'], list) else servings['serving']
                    
                    # Create nutrition response
                    nutrition = {}
                    nutrient_mapping = {
                        'calories': ('calories', 'kcal'),
                        'protein': ('protein', 'g'),
                        'carbohydrate': ('carbs', 'g'),
                        'fat': ('fat', 'g'),
                        'saturated_fat': ('saturated_fat', 'g'),
                        'sugar': ('sugar', 'g'),
                        'fiber': ('fiber', 'g'),
                        'cholesterol': ('cholesterol', 'mg'),
                        'sodium': ('sodium', 'mg'),
                        'potassium': ('potassium', 'mg')
                    }
                    
                    for api_field, (output_field, unit) in nutrient_mapping.items():
                        try:
                            value = float(serving.get(api_field, 0))
                            nutrition[output_field] = NutrientInfo(
                                value=value,
                                unit=unit
                            )
                        except (ValueError, TypeError):
                            nutrition[output_field] = NutrientInfo(value=0, unit=unit)
                    
                    return NutritionResponse(**nutrition)
                    
        except Exception as e:
            print(f"Error processing nutrition data for {item.name}: {e}")
            return None

async def calculate_nutrition_for_foods(food_items: List[FoodItem]) -> NutritionResponse:
    """Get nutrition data for multiple food items concurrently"""
    # Process all food items concurrently
    tasks = [get_food_nutrition(item) for item in food_items]
    nutrition_data_list = await asyncio.gather(*tasks)
    
    # Filter out None results
    nutrition_data_list = [data for data in nutrition_data_list if data is not None]
    
    if not nutrition_data_list:
        raise HTTPException(
            status_code=404,
            detail="Could not find nutritional information for any of the provided foods"
        )
    
    # Combine nutrition data
    total_nutrition = {}
    for nutrient in ['calories', 'protein', 'carbs', 'fat', 'saturated_fat', 
                    'sugar', 'fiber', 'cholesterol', 'sodium', 'potassium']:
        total = sum(getattr(data, nutrient).value for data in nutrition_data_list if hasattr(data, nutrient))
        unit = next((getattr(data, nutrient).unit for data in nutrition_data_list 
                    if hasattr(data, nutrient)), 'g')
        total_nutrition[nutrient] = NutrientInfo(value=round(total, 2), unit=unit)
    
    return NutritionResponse(**total_nutrition)
