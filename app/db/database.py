from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.schemas import MealPlan

async def init_db():
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGO_URI)
    
    # Initialize beanie with the document models
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[MealPlan]
    )
    
    return client
