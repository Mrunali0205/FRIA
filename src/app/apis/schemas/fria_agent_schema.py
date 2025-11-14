import uuid
from pydantic import BaseModel

class FriaAgentInvokeSchema(BaseModel):
    session_id: uuid.UUID
    user_message: str
    chat_history: list[dict[str, str]]  
    current_data: dict

class TowingGuideInvokeSchema(BaseModel):
    session_id: uuid.UUID
    towing_instruction: str