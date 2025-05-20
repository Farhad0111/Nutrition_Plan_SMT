from typing import Optional, List, Dict, Union
from datetime import datetime
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    gender: str = Field(..., description="User's gender", example="male")
    age: int = Field(..., gt=0, lt=120, description="User's age", example=30)
    height: int = Field(..., gt=0, lt=300, description="Height in cm", example=175)
    weight: float = Field(..., gt=0, lt=500, description="Current weight in kg", example=75.5)
    desiredWeight: float = Field(..., gt=0, lt=500, description="Target weight in kg", example=70.0)
    weeklyWeightLossGoal: float = Field(..., gt=0, lt=2, description="Weekly weight loss goal in kg", example=0.5)
    trainingDay: int = Field(..., ge=0, le=7, description="Number of training days per week", example=3)
    workoutLocation: str = Field(..., description="Where user works out", example="gym")
    dietType: str = Field(..., description="Type of diet", example="balanced")
    reachingGoals: str = Field(..., description="Main fitness goal", example="weight loss")
    accomplish: str = Field("N/A", description="Additional goals", example="build muscle")

class FoodItem(BaseModel):
    name: str
    totalFood: float = 1.0
    unit: str = "serving"
    servingSize: float = 1.0

class NutrientInfo(BaseModel):
    value: float
    unit: str
    rdi_percent: Optional[float] = None

class NutritionResponse(BaseModel):
    calories: NutrientInfo
    protein: NutrientInfo
    carbs: NutrientInfo
    fat: NutrientInfo
    saturatedFat: NutrientInfo
    monounsaturatedFat: Optional[NutrientInfo] = None
    polyunsaturatedFat: Optional[NutrientInfo] = None
    sugar: Optional[NutrientInfo] = None
    fiber: Optional[NutrientInfo] = None
    cholesterol: Optional[NutrientInfo] = None
    sodium: Optional[NutrientInfo] = None
    potassium: Optional[NutrientInfo] = None
    calcium: Optional[NutrientInfo] = None
    iron: Optional[NutrientInfo] = None
    vitaminA: Optional[NutrientInfo] = None
    vitaminC: Optional[NutrientInfo] = None

class NutritionInfo(BaseModel):
    mealPlanType: str
    servingSize: float = 1.0
    nutritionalValues: Optional[NutritionResponse] = None

class MealItem(BaseModel):
    name: str
    portion: str
    nutrition: NutritionInfo

class DailyMeal(BaseModel):
    breakfast: List[MealItem]
    lunch: List[MealItem]
    dinner: List[MealItem]
    snacks: List[MealItem]

class MealPlan(BaseModel):
    id: str
    user_profile: UserProfile
    meal_plan_text: str
    response_time_seconds: float
    created_at: datetime = datetime.utcnow()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }