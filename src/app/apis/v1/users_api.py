from fastapi import APIRouter, HTTPException, Depends
from src.app.core.log_config import setup_logging


router = APIRouter(prefix="/users", tags=["User Services"])