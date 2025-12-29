import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CreateSessionSchema(BaseModel):
    user_id: uuid.UUID
    vehicle_id: uuid.UUID