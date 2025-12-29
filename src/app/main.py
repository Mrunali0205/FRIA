"""
Main file to run FastAPI app for FRIA agent and services.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config import settings
from src.app.apis.v1 import location_api, users_api, agent_api, audio_api

app = FastAPI(
    root_path="/api/v1",
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

app.include_router(prefix="/api/v1", router=location_api.router)
app.include_router(prefix="/api/v1", router=users_api.router)
app.include_router(prefix="/api/v1", router=agent_api.router)
app.include_router(prefix="/api/v1", router=audio_api.router)