import uuid
from pydantic import BaseModel
from typing import Optional

class CreateSessionSchema(BaseModel):
    user_id: uuid.UUID
    vehicle_id: uuid.UUID
    user_name: Optional[str]