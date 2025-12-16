"""
Docstring for app.apis.v1.location_routers
""" 
from fastapi import APIRouter
from typing import List
from src.app.apis.schemas.location_routers_schema import (
    ReverseGeocodeRequest,
    ForwardSearchRequest,
    AddressCandidate,
)
from src.app.services.gps_location_service import (
    reverse_geocode,
    search_address,
    ip_geolocation,
)

router = APIRouter(prefix="/location", tags=["Location Services"])


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
