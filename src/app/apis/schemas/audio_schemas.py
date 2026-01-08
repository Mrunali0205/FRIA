"""Schemas for audio-related operations."""
import uuid
from pydantic import BaseModel

class RecordAudioSchema(BaseModel):
    """Schema for recording audio transcripts."""
    session_id: uuid.UUID
    user_id: uuid.UUID
