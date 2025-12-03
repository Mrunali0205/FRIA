from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from app.services.gps_location_service import (
    reverse_geocode,
    search_address,
    ip_geolocation,
)
router = APIRouter(prefix="/location", tags=["Location Services"])
# Pydantic Models
class ReverseGeocodeRequest(BaseModel):
    lat: float
    lon: float
class ForwardSearchRequest(BaseModel):
    query: str
class AddressCandidate(BaseModel):
    address: str
    lat: float
    lon: float
# Routes
@router.post("/reverse-geocode")
def api_reverse_geocode(payload: ReverseGeocodeRequest):
    """Convert coordinates → address."""
    address = reverse_geocode(payload.lat, payload.lon)
    return {"address": address}
@router.post("/search")
def api_search_address(payload: ForwardSearchRequest) -> List[AddressCandidate]:
    """Autocomplete / search address."""
    results = search_address(payload.query)
    return results
@router.get("/ip")
def api_ip_location():
    """Approximate location based on IP address."""
    lat, lon = ip_geolocation()
    return {"lat": lat, "lon": lon}
