import uuid
from pydantic import BaseModel
from typing import List, Dict, Any

class FriaAgentInvokeSchema(BaseModel):
    session_id: uuid.UUID
    user_message: str
    chat_history: List[Dict[str, str]]  
    current_data: Dict[str, Any]

class TowingGuideInvokeSchema(BaseModel):
    session_id: uuid.UUID
    towing_instruction: str