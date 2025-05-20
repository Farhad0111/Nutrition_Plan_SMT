from typing import List, Dict, Optional
import requests
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.shemas import FoodItem, NutrientInfo

# Token cache
token_data = {
    "access_token": None,
    "expires_at": None
}

# Helper function to get access token
def get_access_token():
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
    
    try:
        response = requests.post(settings.FAT_SECRET_AUTH_URL, data=auth_data)
        response.raise_for_status()
        token_info = response.json()
        
        # Save token with expiration time
        token_data["access_token"] = token_info["access_token"]
        # Set expiration 5 minutes before actual expiry for safety
        token_data["expires_at"] = current_time + timedelta(seconds=token_info["expires_in"] - 300)
        
        return token_data["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate with nutrition API")

# Search food in FatSecret API
def search_food(food_name):
    token = get_access_token()
    
    params = {
        'method': 'foods.search',
        'search_expression': food_name,
        'format': 'json',
        'max_results': 3
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(settings.FAT_SECRET_BASEURL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'foods' not in data or 'food' not in data['foods']:
            return None
            
        return data['foods']['food'][0]['food_id']  # Return the first match's ID
    except requests.exceptions.RequestException as e:
        print(f"Error searching food: {e}")
        return None

# Get food details from FatSecret API
def get_food_details(food_id):
    token = get_access_token()
    
    params = {
        'method': 'food.get.v2',
        'food_id': food_id,
        'format': 'json'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(settings.FAT_SECRET_BASEURL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting food details: {e}")
        return None

# Convert nutritional data based on quantity
def calculate_nutrition_for_item(food_data, totalFood, unit, servingSize):
    try:
        if 'food' not in food_data or 'servings' not in food_data['food']:
            return None
            
        servings = food_data['food']['servings']
        serving = None
        
        # Find the appropriate serving or use the first one
        if 'serving' in servings:
            if isinstance(servings['serving'], list):
                # Try to find a matching unit
                for s in servings['serving']:
                    if unit.lower() in s.get('measurement_description', '').lower():
                        serving = s
                        break
                if not serving:
                    serving = servings['serving'][0]  # Use first if no match
            else:
                serving = servings['serving']
        
        if not serving:
            return None
        
        # Calculate the multiplier based on serving size and total food
        serving_quantity = float(serving.get('number_of_units', 1))
        multiplier = (totalFood / serving_quantity) * (servingSize / serving_quantity)
        
        # Extract and convert nutrients
        nutrition = {}
        
        # Map API fields to our expected output fields
        nutrient_mapping = {
            'calories': 'calories',
            'protein': 'protein',
            'carbohydrate': 'carbs',
            'fat': 'fat',
            'saturated_fat': 'saturatedFat',
            'monounsaturated_fat': 'monounsaturatedFat',
            'polyunsaturated_fat': 'polyunsaturatedFat',
            'sugar': 'sugar',
            'fiber': 'fiber',
            'cholesterol': 'cholesterol',
            'sodium': 'sodium',
            'potassium': 'potassium',
            'calcium': 'calcium',
            'iron': 'iron',
            'vitamin_a': 'vitaminA',
            'vitamin_c': 'vitaminC'
        }
        
        # Default units for each nutrient
        default_units = {
            'calories': 'kcal',
            'protein': 'g',
            'carbs': 'g',
            'fat': 'g',
            'saturatedFat': 'g',
            'monounsaturatedFat': 'g',
            'polyunsaturatedFat': 'g',
            'sugar': 'g',
            'fiber': 'g',
            'cholesterol': 'mg',
            'sodium': 'mg',
            'potassium': 'mg',
            'calcium': 'mg',
            'iron': 'mg',
            'vitaminA': 'mcg',
            'vitaminC': 'mg'
        }
        
        # Extract each nutrient and apply the multiplier
        for api_field, output_field in nutrient_mapping.items():
            value = serving.get(api_field, '0')
            if value:
                try:
                    numeric_value = float(value)
                    nutrition[output_field] = numeric_value * multiplier
                except ValueError:
                    nutrition[output_field] = 0
            else:
                nutrition[output_field] = 0
        
        return {
            'nutrition': nutrition,
            'units': default_units
        }
        
    except Exception as e:
        print(f"Error calculating nutrition: {e}")
        return None

# Combine nutrition from multiple items
def combine_nutrition(nutrition_data_list):
    combined = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'saturatedFat': 0,
        'monounsaturatedFat': 0,
        'polyunsaturatedFat': 0,
        'sugar': 0,
        'fiber': 0,
        'cholesterol': 0,
        'sodium': 0,
        'potassium': 0,
        'calcium': 0,
        'iron': 0,
        'vitaminA': 0,
        'vitaminC': 0
    }
    
    units = {}
    
    for item in nutrition_data_list:
        if not item or 'nutrition' not in item:
            continue
            
        for nutrient, value in item['nutrition'].items():
            if nutrient in combined:
                combined[nutrient] += value
                
        if 'units' in item:
            for nutrient, unit in item['units'].items():
                if nutrient not in units:
                    units[nutrient] = unit
    
    # Calculate RDI percentages
    result = {}
    for nutrient, value in combined.items():
        rdi_percent = None
        if nutrient in settings.RDI_VALUES and settings.RDI_VALUES[nutrient] > 0:
            rdi_percent = (value / settings.RDI_VALUES[nutrient]) * 100
            
        result[nutrient] = NutrientInfo(
            value=round(value, 2),
            unit=units.get(nutrient, 'g'),
            rdi_percent=round(rdi_percent, 2) if rdi_percent is not None else None
        )
    
    return result

async def calculate_nutrition_for_foods(food_items: List[FoodItem]) -> Dict:
    nutrition_data_list = []
    
    for item in food_items:
        # Search for the food
        food_id = search_food(item.name)
        if not food_id:
            print(f"Food not found: {item.name}")
            continue
            
        # Get food details
        food_details = get_food_details(food_id)
        if not food_details:
            print(f"Could not get details for: {item.name}")
            continue
            
        # Calculate nutrition based on quantity
        nutrition_data = calculate_nutrition_for_item(
            food_details, 
            item.totalFood,
            item.unit,
            item.servingSize
        )
        
        if nutrition_data:
            nutrition_data_list.append(nutrition_data)
            
    # If we couldn't find any foods, return an error
    if not nutrition_data_list:
        raise HTTPException(status_code=404, detail="Could not find nutritional information for any of the provided foods")
            
    # Combine nutrition data from all foods
    result = combine_nutrition(nutrition_data_list)
    
    return result
