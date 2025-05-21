import time
import json
import requests
import uuid
from datetime import datetime
from fastapi import HTTPException
from app.core.config import settings
from app.models.shemas import UserProfile, MealPlan,WorkoutItem,WorkoutPlanDay,WorkoutPlan
def generate_meal_plan_prompt(user: UserProfile) -> str:
    return f"""
You are a professional nutritionist AI. Based on the following user profile, generate a simplified daily meal plan.

User Profile:
- Gender: {user.gender}
- Age: {user.age}
- Height: {user.height}cm
- Current Weight: {user.weight}kg
- Target Weight: {user.desiredWeight}kg
- Weekly Weight Goal: {user.weeklyWeightLossGoal}kg
- Training: {user.trainingDay} days/week at {user.workoutLocation}
- Diet Type: {user.dietType.upper()}
- Goals: {user.reachingGoals}, {user.accomplish}

Instructions:
-MOST IMPORTANT: FOOD MUST BE HALAL
- For each meal (BREAKFAST, LUNCH, DINNER, SNACK), suggest 3-5 healthy food items.
- For each food item, return a JSON object with EXACTLY the following format:
{{
  "mealPlanType": "BREAKFAST" | "LUNCH" | "DINNER" | "SNACK",
  "name": "Food Name",
  "totalFood": number,
  "unit": "unit of measurement",
  "servingSize": number
}}

- Return the full response as a list of JSON objects (not narrative text).
- Do NOT include any additional fields such as calories, protein, carbs, etc.
- Ensure the meal plan is balanced and appropriate for the user's profile and goals.
"""

def generate_workout_plan_prompt(user: UserProfile) -> str:
    # Determine split type based on training days
    split_type = ""
    if user.trainingDay == 6:
        split_type = "Push (chest/shoulders/triceps), Pull (back/biceps), Legs split, repeating twice weekly"
    elif user.trainingDay == 5:
        split_type = "Push, Pull, Legs, Upper, Lower split"
    elif user.trainingDay == 4:
        split_type = "Upper, Lower split, repeating twice weekly"
    elif user.trainingDay == 3:
        split_type = "Upper, Lower, Full Body split"
    else:
        split_type = "Full Body workouts"

    return f"""
You are a professional workout AI. Based on the following user profile, generate a detailed workout plan.

User Profile:
- Gender: {user.gender}
- Age: {user.age}
- Height: {user.height}cm
- Current Weight: {user.weight}kg
- Target Weight: {user.desiredWeight}kg
- Weekly Weight Goal: {user.weeklyWeightLossGoal}kg
- Training: {user.trainingDay} days/week
- Diet Type: {user.dietType.upper()}
- Goals: {user.reachingGoals}, {user.accomplish}

Instructions:
- Create a {user.trainingDay}-day workout plan using a {split_type}.
- Each muscle group should be trained twice per week.
- For each day (Day 1, Day 2, ... up to Day {user.trainingDay}), include 5-8 exercises.
- For each day, return a JSON object with EXACTLY the following format:
{{
  "day": "Day 1",
  "focus": "Upper Body", // The focus of this day's workout
  "workoutPlan": [
    {{
      "name": "Exercise Name",
      "sets": number,
      "reps": string, // Can be a range like "8-12" or fixed like "10"
      "rest": string, // Example: "60-90 sec between sets, 2 min after exercise"
    }},
    ... (5-8 exercises)
  ]
}}
- Return the full response as a list of JSON objects (not narrative text).
- Do NOT include any additional fields.
- Ensure the workout plan is safe, effective, and appropriate for the user's profile and goals.
"""

async def get_meal_plan(user: UserProfile):
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": settings.MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional nutritionist AI. You must respond with valid JSON data only, no other text. Your response must be a JSON array containing objects with ONLY the fields: mealPlanType, name, totalFood, unit, and servingSize."},
            {"role": "user", "content": generate_meal_plan_prompt(user)}
        ],
        "temperature": 0.8, 
        "max_tokens": 1024
    }

    start_time = time.time()
    response = requests.post(settings.API_URL, headers=headers, json=data)
    end_time = time.time()

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, 
                          detail=f"OpenAI API error: {response.json()}")

    result = response.json()
    elapsed_time = round(end_time - start_time, 2)    
    
    try:
        response_content = result["choices"][0]["message"]["content"]
        
        # Parse the response content to ensure it only has the required fields
        try:
            meal_data = json.loads(response_content)
            
            # Clean the data - keep only the required fields
            cleaned_data = []
            for item in meal_data:
                cleaned_item = {
                    "mealPlanType": item.get("mealPlanType", ""),
                    "name": item.get("name", ""),
                    "totalFood": item.get("totalFood", 1),
                    "unit": item.get("unit", "serving"),
                    "servingSize": item.get("servingSize", 100)
                }
                cleaned_data.append(cleaned_item)
            
            # Convert back to JSON string
            clean_response_content = json.dumps(cleaned_data, indent=2)
            
            # Create meal plan with cleaned data (without MongoDB)
            meal_plan = MealPlan(
                id=str(uuid.uuid4()),
                user_profile=user,
                meal_plan_text=clean_response_content,
                response_time_seconds=elapsed_time
            )
            
            return meal_plan
            
        except json.JSONDecodeError:
            # If parsing fails, return the original response
            meal_plan = MealPlan(
                id=str(uuid.uuid4()),
                user_profile=user,
                meal_plan_text=response_content,
                response_time_seconds=elapsed_time
            )
            
            return meal_plan
            
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing meal plan: {str(e)}"
        )
    

async def get_workout_plan(user: UserProfile):
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": settings.MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional workout planner AI. You must respond with valid JSON data only, no other text. Your response must be a JSON array containing objects with ONLY the fields: day, focus, and workoutPlan (which is a list of objects with name, sets, reps, and rest fields)."},
            {"role": "user", "content": generate_workout_plan_prompt(user)}
        ],
        "temperature": 0.8, 
        "max_tokens": 2048  # Increased token limit to handle larger responses
    }

    start_time = time.time()
    response = requests.post(settings.API_URL, headers=headers, json=data)
    end_time = time.time()

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, 
                          detail=f"OpenAI API error: {response.json()}")

    result = response.json()
    elapsed_time = round(end_time - start_time, 2)    
    
    try:
        response_content = result["choices"][0]["message"]["content"]
        try:
            workout_data = json.loads(response_content)
            
            # Clean the data to ensure it has the required fields
            cleaned_data = []
            for day_data in workout_data:
                cleaned_workout_plan = []
                for exercise in day_data.get("workoutPlan", []):
                    cleaned_exercise = {
                        "name": exercise.get("name", ""),
                        "sets": exercise.get("sets", 3),
                        "reps": exercise.get("reps", "8-12"),
                        "rest": exercise.get("rest", "60 sec")
                    }
                    cleaned_workout_plan.append(cleaned_exercise)
                
                cleaned_day = {
                    "day": day_data.get("day", ""),
                    "focus": day_data.get("focus", ""),
                    "workoutPlan": cleaned_workout_plan
                }
                cleaned_data.append(cleaned_day)
            
            clean_response_content = json.dumps(cleaned_data, indent=2)
            workout_plan = WorkoutPlan(
                id=str(uuid.uuid4()),
                user_profile=user,
                workout_plan_text=clean_response_content,
                response_time_seconds=elapsed_time
            )
            return workout_plan
        except json.JSONDecodeError:
            workout_plan = WorkoutPlan(
                id=str(uuid.uuid4()),
                user_profile=user,
                workout_plan_text=response_content,
                response_time_seconds=elapsed_time
            )
            return workout_plan
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing workout plan: {str(e)}"
        )