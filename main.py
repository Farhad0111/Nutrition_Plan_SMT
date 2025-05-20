from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db.database import init_db
from app.core.config import settings

app = FastAPI(
    title="Meal Plan API",
    description="API for generating personalized meal plans with MongoDB integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def start_app():
    try:
        # Initialize Beanie
        client = await init_db()
        print("Successfully connected to MongoDB!")
        
        # Store the client for cleanup
        app.state.client = client
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    if hasattr(app.state, "client"):
        app.state.client.close()
        print("MongoDB connection closed")

# Include router with versioned prefix
app.include_router(router, prefix="/api/v1")
