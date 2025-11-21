import requests
from typing import Optional
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="tesla_tow_app")
# Reverse Geocoding
def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """Convert coordinates → address."""
    try:
        location = geolocator.reverse((lat, lon), language="en")
        return location.address if location else None
    except Exception:
        return None

# Forward Geocoding (autocomplete)
def search_address(query: str):
    """Return top 5 addresses matching search query."""
    try:
        results = geolocator.geocode(query, exactly_one=False, language="en", limit=5)
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
# Device / IP Geolocation
def ip_geolocation():
    """Fallback IP-based approximate location."""
    try:
        res = requests.get("https://ipinfo.io/json")
        loc = res.json().get("loc", "")
        lat, lon = loc.split(",")
        return float(lat), float(lon)
    except:
        return None, None
