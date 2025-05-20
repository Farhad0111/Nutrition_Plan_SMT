from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="Meal Plan API",
    description="API for generating personalized meal plans",
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
    print("Application started!")

@app.on_event("shutdown")
async def shutdown_app():
    print("Application shutting down")

# Include router with versioned prefix
app.include_router(router, prefix="/api/v1")
