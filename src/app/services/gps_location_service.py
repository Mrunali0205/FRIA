"""GPS location services."""
import requests
import uuid
import datetime
from typing import Optional, List, Dict
from geopy.geocoders import Nominatim
from src.app.apis.deps import DBClientDep
from src.app.core.log_config import setup_logging

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
    user_id: str,
    session_id: str,
    address: str,
    latitude: float,
    longitude: float,
    db_client: DBClientDep
):
    """Insert GPS location into the database."""
    
    status = db_client.insert(
        query="INSERT INTO gps_locations (id, user_id, session_id, address, latitude, longitude, created_at) VALUES (:id, :user_id, :session_id, :address, :latitude, :longitude, :created_at)",
        values={
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
    )
    logger.info(f"Inserted GPS location for user_id={user_id}, session_id={session_id}, address={address}")
    if status.get("status") != "success":
        logger.error(f"Failed to insert GPS location for user_id={user_id}, session_id={session_id}")
        return {"insert_success": False, "message": "Failed to insert GPS location."}
    return {"insert_success": True, "message": "GPS location inserted successfully."}