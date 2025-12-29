"""GPS location services."""
import requests
from typing import Optional, List, Dict
from geopy.geocoders import Nominatim

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

def ip_geolocation() -> tuple[Optional[float], Optional[float]]:
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        loc = res.json().get("loc")
        if not loc:
            return None, None

        lat_str, lon_str = loc.split(",")
        return float(lat_str), float(lon_str)

    except Exception:
        return None, None
