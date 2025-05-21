import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache
from typing import ClassVar, Dict

load_dotenv()

class Settings(BaseSettings):
    # OpenAI Settings
    API_KEY: str
    API_URL: str = "https://api.openai.com/v1/chat/completions"
    MODEL: str = "gpt-4.1"  # or "gpt-3.5-turbo"
    
    # FatSecret API Configuration
    FAT_SECRET_BASEURL: str = "https://platform.fatsecret.com/rest/server.api"
    FAT_SECRET_CLIENT_ID: str
    FAT_SECRET_CLIENT_SECRET: str
    FAT_SECRET_AUTH_URL: str = "https://oauth.fatsecret.com/connect/token"
    
    # RDI Values (based on 2000 calorie diet) - standard values
    RDI_VALUES: ClassVar[Dict[str, int]] = {
        "protein": 50,  # g
        "carbs": 300,  # g
        "fat": 65,  # g
        "saturatedFat": 20,  # g
        "fiber": 25,  # g
        "cholesterol": 300,  # mg
        "sodium": 2300,  # mg
        "potassium": 4700,  # mg
        "calcium": 1000,  # mg
        "iron": 18,  # mg
        "vitaminA": 900,  # mcg RAE
        "vitaminC": 90,  # mg
    }

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()