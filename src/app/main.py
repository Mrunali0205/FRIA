"""Main application file for the FRIA Agent and Services API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from src.app.core.config import settings
from src.app.core.log_config import setup_logging
from src.app.apis.v1 import location_api, users_api, agent_api, audio_api, document_apis

mongo_db_uri = settings.MONGODB_URI or ""

logger = setup_logging(__name__)

app = FastAPI(
    title="FRIA Agent and Services API",
    description="Server for First Responder Intelligent Agent and related services.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL or "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {"message": "FRIA Agent and Services API is running."}

@app.get("/health/live", tags=["Health Check"])
def health_check():
    """Health check endpoint."""
    return {"status": "alive"}

@app.get("/health/startup", tags=["Startup"])
def health_startup():
    """Readiness check endpoint."""
    return {"status": "started"}

@app.on_event("startup")
async def startup_db_client():
    """Initialize MongoDB client on startup."""
    logger.info("Connecting to MongoDB...")
    app.state.mongodb_client = AsyncIOMotorClient(mongo_db_uri)
    app.state.mongodb = app.state.mongodb_client.fria_document_db
    logger.info("Connected to MongoDB.")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB client on shutdown."""
    logger.info("Closing MongoDB connection...")
    app.state.mongodb_client.close()
    logger.info("MongoDB connection closed.")

app.include_router(location_api.router, prefix="/api/v1")
app.include_router(users_api.router, prefix="/api/v1")
app.include_router(agent_api.router, prefix="/api/v1")
app.include_router(audio_api.router, prefix="/api/v1")
app.include_router(document_apis.router, prefix="/api/v1")
