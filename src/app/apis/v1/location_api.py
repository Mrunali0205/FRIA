"""
Location API endpoints.
""" 
from fastapi import APIRouter, HTTPException
from typing import List
from src.app.apis.schemas.location_routers_schema import (
    ForwardSearchRequest
)
from src.app.services.gps_location_service import (
    search_address,
    auto_detect_location,
)

router = APIRouter(prefix="/location", tags=["Location Endpoints"])


@router.post("/search", description="Autocomplete / search address.", tags=["Location Service"])
def api_search_address(payload: ForwardSearchRequest):
    """Autocomplete / search address."""
    results = search_address(payload.query)
    return {"status_code": 200, "results": results}

@router.post("/auto-detect-location", description="Get approximate location based on IP address.", tags=["Location Service"])
def api_auto_detect_location():
    """Approximate location based on IP address."""
    location = auto_detect_location()
    if not location:
        raise HTTPException(status_code=500, detail="IP geolocation lookup failed.")
    
    return {"status_code": 200, "address" : location}