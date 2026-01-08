"""Module defining Pydantic schemas for location router requests."""
from pydantic import BaseModel

class ForwardSearchRequest(BaseModel):
    """Schema for forward address search request."""
    query: str

class InsertGPSLocationRequest(BaseModel):
    """Insert GPS location request schema."""
    user_id: str
    session_id: str
    address: str
    latitude: float
    longitude: float
