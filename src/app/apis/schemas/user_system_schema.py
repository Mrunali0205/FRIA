"""Schema for creating a new session."""
import uuid
from typing import Optional
from pydantic import BaseModel

class CreateSessionSchema(BaseModel):
    """Schema for creating a new session."""
    user_id: uuid.UUID
    vehicle_id: uuid.UUID
    user_name: Optional[str]
