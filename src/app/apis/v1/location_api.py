"""
Location API endpoints.
""" 
from fastapi import APIRouter, HTTPException
from typing import List
from src.app.apis.schemas.location_routers_schema import (
    ForwardSearchRequest, InsertGPSLocationRequest
)
from src.app.services.gps_location_service import insert_gps_location
from src.app.apis.deps import DBClientDep
from src.app.services.gps_location_service import (
    search_address,
    auto_detect_location,
)

router = APIRouter(prefix="/location", tags=["Location Endpoints"])


@router.post("/search", description="Autocomplete / search address.")
def api_search_address(payload: ForwardSearchRequest):
    """Autocomplete / search address."""
    results = search_address(payload.query)
    return {"status_code": 200, "results": results}

@router.post("/auto-detect-location", description="Get approximate location based on IP address.")
def api_auto_detect_location():
    """Approximate location based on IP address."""
    location = auto_detect_location()
    if not location:
        raise HTTPException(status_code=500, detail="IP geolocation lookup failed.")
    
    return {"status_code": 200, "address" : location}

@router.post("/insert-gps-location", description="Insert GPS location into the database.")
def api_insert_gps_location(payload: InsertGPSLocationRequest, db_client: DBClientDep):
    """Insert GPS location into the database."""
    is_insert_success = insert_gps_location(
        user_id=payload.user_id,
        session_id=payload.session_id,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        db_client=db_client
    )
    if not is_insert_success.get("insert_success"):
        raise HTTPException(status_code=500, detail="Failed to insert GPS location.")
    return {"status_code": 200, "message": is_insert_success["message"]}