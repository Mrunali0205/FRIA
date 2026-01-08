"""GPS location services."""
import uuid
import datetime
from typing import Optional, List, Dict
import requests
from geopy.geocoders import Nominatim
from src.app.apis.deps import DBClientDep
from src.app.core.log_config import setup_logging
from src.app.apis.schemas.location_routers_schema import InsertGPSLocationRequest

logger = setup_logging("GPS LOCATION SERVICE")

geolocator = Nominatim(user_agent="tesla_tow_app")

def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Convert latitude/longitude → human-readable address.
    Returns None if lookup fails.
    """
    try:
        location = geolocator.reverse((lat, lon), language="en")
        return location.address if location else None
    except Exception:
        return None

def search_address(query: str) -> List[Dict]:
    """
    Query partial address 
    """
    try:
        results = geolocator.geocode(
            query,
            exactly_one=False,
            language="en",
            limit=5
        )
        if not results:
            return []

        return [
            {
                "address": r.address,
                "lat": r.latitude,
                "lon": r.longitude
            }
            for r in results
        ]
    except Exception:
        return []

def auto_detect_location() -> dict:
    """
    Get approximate latitude/longitude based on IP address.
    Returns (None, None) if lookup fails."""
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        loc = res.json().get("loc")
        if not loc:
            return {}
        lat_str, lon_str = loc.split(",")
        lat, lon =float(lat_str), float(lon_str)
        location = geolocator.reverse((lat, lon), language="en")
        return {"address": location.address if location else None, "lat": lat, "lon": lon}

    except Exception:
        return {}

def insert_gps_location(
    gps_location_request: InsertGPSLocationRequest,
    db_client: DBClientDep
):
    """Insert GPS location into the database."""
    status = db_client.insert(
        query="""INSERT INTO gps_locations (id, user_id, session_id, address, latitude, longitude, created_at)
        VALUES (:id, :user_id, :session_id, :address, :latitude, :longitude, :created_at)""",
        values={
            "id": str(uuid.uuid4()),
            "user_id": gps_location_request.user_id,
            "session_id": gps_location_request.session_id,
            "address": gps_location_request.address,
            "latitude": gps_location_request.latitude,
            "longitude": gps_location_request.longitude,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
    )
    logger.info("Inserted GPS location for user_id=%s, session_id=%s, address=%s",
                gps_location_request.user_id, gps_location_request.session_id, gps_location_request.address)
    if status.get("status") != "success":
        logger.error("Failed to insert GPS location for user_id=%s, session_id=%s", gps_location_request.user_id, gps_location_request.session_id)
        return {"insert_success": False, "message": "Failed to insert GPS location."}
    return {"insert_success": True, "message": "GPS location inserted successfully."}
