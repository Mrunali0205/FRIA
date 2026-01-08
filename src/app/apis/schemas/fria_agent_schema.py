"""Schemas for Fria Agent API endpoints."""
import uuid
from typing import Optional
from pydantic import BaseModel

class AgentInitializeSchema(BaseModel):
    """Schema for initializing the agent."""
    user_id: uuid.UUID
    session_id: uuid.UUID
    mode: str
    recorded_transcription: Optional[str] = None
    vehicle_type: Optional[str] = None

class AgentContinueSchema(BaseModel):
    """Schema for continuing the agent interaction."""
    session_id: uuid.UUID
    user_id: uuid.UUID
    user_response: Optional[str] = None
    vehicle_type: Optional[str] = None
