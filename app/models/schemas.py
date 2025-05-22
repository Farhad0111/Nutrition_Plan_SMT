from typing import Optional, List, Dict, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

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
    meal: Literal["BREAKFAST", "LUNCH", "DINNER", "SNACK"]
    name: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    unit: Literal["g", "ml", "pcs", "serving"] = "serving"
    serving_size: Optional[float] = Field(None, gt=0)

class NutrientInfo(BaseModel):
    value: float = Field(..., ge=0)
    unit: Literal["g", "mg", "mcg", "IU", "kcal"] = "g"
    rdi_percent: Optional[float] = Field(None, ge=0)  # Removed le=100 constraint

class NutritionResponse(BaseModel):
    calories: NutrientInfo
    protein: NutrientInfo
    carbs: NutrientInfo
    fat: NutrientInfo
    saturated_fat: NutrientInfo
    monounsaturated_fat: Optional[NutrientInfo] = None
    polyunsaturated_fat: Optional[NutrientInfo] = None
    sugar: Optional[NutrientInfo] = None
    fiber: Optional[NutrientInfo] = None
    cholesterol: Optional[NutrientInfo] = None
    sodium: Optional[NutrientInfo] = None
    potassium: Optional[NutrientInfo] = None
    calcium: Optional[NutrientInfo] = None
    iron: Optional[NutrientInfo] = None
    vitamin_a: Optional[NutrientInfo] = None
    vitamin_c: Optional[NutrientInfo] = None

class NutritionInfo(BaseModel):
    meal_type: Literal["BREAKFAST", "LUNCH", "DINNER", "SNACK"]
    serving_size: float = Field(1.0, gt=0)
    nutritional_values: Optional[NutritionResponse] = None

class MealItem(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    unit: Literal["g", "ml", "pcs", "serving"] = "serving"
    nutrition: NutritionInfo

class DailyMeal(BaseModel):
    breakfast: List[MealItem] = Field(default_factory=list)
    lunch: List[MealItem] = Field(default_factory=list)
    dinner: List[MealItem] = Field(default_factory=list)
    snacks: List[MealItem] = Field(default_factory=list)

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

class WorkoutItem(BaseModel):
    name: str
    sets: int
    reps: str
    rest: str

class WorkoutPlanDay(BaseModel):
    day: str
    focus: str
    workoutPlan: List[WorkoutItem]

class WorkoutPlan(BaseModel):
    id: str = str(uuid.uuid4())
    user_profile: UserProfile
    workout_plan_text: str
    response_time_seconds: float
    created_at: datetime = datetime.utcnow()

class Config:
    json_encoders = {
        datetime: lambda v: v.isoformat()
        }

