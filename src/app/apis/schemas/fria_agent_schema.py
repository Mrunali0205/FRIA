import uuid
from pydantic import BaseModel
from typing import List, Dict, Any

class FriaAgentInvokeSchema(BaseModel):
    session_id: uuid.UUID
    user_message: str | None = None
    chat_history: List[Dict[str, str]] | None = None
    current_data: Dict[str, Any] | None = None
    lat: float | None = None
    lon: float | None = None
    audio_transcript: str | None = None
class TowingGuideInvokeSchema(BaseModel):
    session_id: uuid.UUID
    towing_instruction: str
