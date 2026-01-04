import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class FriaAgentInvokeSchema(BaseModel):
    session_id: uuid.UUID
    user_message: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    audio_transcript: Optional[str] = None
    chat_history: List[Dict[str, str]] = Field(default_factory=list)
    current_data: Dict[str, Any] = Field(default_factory=dict)


class TowingGuideInvokeSchema(BaseModel):
    session_id: uuid.UUID
    towing_instruction: str

class AgentInvokeSchema(BaseModel):
    mode: str  # "chat" | "audio"
    session_id: uuid.UUID
    user_id: uuid.UUID
    user_response: Optional[str] = None
    vehicle_type: Optional[str] = None
    recorded_transcription: Optional[str] = None