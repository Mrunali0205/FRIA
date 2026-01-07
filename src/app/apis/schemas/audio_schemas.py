import uuid
from pydantic import BaseModel
from typing import Optional

class RecordAudioSchema(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID