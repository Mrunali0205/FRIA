import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class AgentInitializeSchema(BaseModel):
    user_id: uuid.UUID
    session_id: uuid.UUID
    mode: str
    recorded_transcription: Optional[str] = None
    vehicle_type: Optional[str] = None

class AgentContinueSchema(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    user_response: Optional[str] = None
    vehicle_type: Optional[str] = None