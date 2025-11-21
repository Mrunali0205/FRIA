"""
API Client for Tesla Towing Assistant
Uses:
  • FastAPI backend for LLM + reverse geocode
  • Direct file read/write for MCP tow_data.json
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
from dotenv import load_dotenv

# Load environment vars
load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TOW_DATA_FILE = PROJECT_ROOT / "src" / "mcp_servers" / "tow_data.json"


class APIClient:
    """Client for interacting with FastAPI backend + local tow_data.json."""

    # -----------------------------
    # FASTAPI BACKEND CALLS
    # -----------------------------

    async def start_agent_session(self) -> str:
        """GET /agent/start → returns session_id"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/agent/start")
            response.raise_for_status()
            return response.json().get("session_id", "")

    async def invoke_agent(
        self,
        session_id: str,
        user_message: str,
        chat_history: List[Dict[str, str]],
        current_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """POST /agent/invoke → LLM conversation"""
        payload = {
            "session_id": session_id,
            "user_message": user_message,
            "chat_history": chat_history,
            "current_data": current_data,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/agent/invoke",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        POST /location/reverse-geocode
        FIXED: Must send JSON (NOT params).
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/location/reverse-geocode",
                    json={"lat": lat, "lon": lon},   # FIXED
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            print(f"❌ reverse_geocode error: {e}")
            return {"success": False, "error": str(e)}

    # -----------------------------
    # LOCAL tow_data.json ACCESS
    # -----------------------------

    async def get_fields(self) -> Dict[str, Any]:
        """Load all fields from tow_data.json."""
        try:
            if TOW_DATA_FILE.exists():
                with open(TOW_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            else:
                print(f"⚠ tow_data.json missing at {TOW_DATA_FILE}")
                return {}
        except Exception as e:
            print(f"❌ get_fields error: {e}")
            return {}

    async def set_field(self, field: str, value: Optional[str]) -> Dict[str, Any]:
        """Write a single field to tow_data.json."""
        try:
            if not TOW_DATA_FILE.exists():
                return {"ok": False, "error": "tow_data.json missing"}

            with open(TOW_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            data[field] = value

            with open(TOW_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"→ Updated {field} = {value}")
            return {"ok": True}

        except Exception as e:
            print(f"❌ set_field error: {e}")
            return {"ok": False, "error": str(e)}

    async def reset_data(self) -> Dict[str, Any]:
        """
        Reset tow_data.json to default values.
        NOTE: You can edit defaults here anytime.
        """
        try:
            defaults = {
                "full_name": "Sarah Chen",
                "contact_number": "+1-312-555-2098",
                "email_address": "sarah.chen@tesla.com",
                "accident_location_address": None,
                "Tesla_model": "Model 3 Long Range",
                "VIN_number": "5YJ3E1EA7JF123456",
                "license_plate_number": "IL 93Z882",
                "insurance_company_name": "Tesla Insurance",
                "insurance_policy_number": "TI-882934",
                "is_vehicle_operable": None,
                "damage_description": None,
            }

            with open(TOW_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(defaults, f, indent=2, ensure_ascii=False)

            print("→ tow_data.json reset to defaults")
            return {"ok": True}

        except Exception as e:
            print(f"❌ reset_data error: {e}")
            return {"ok": False, "error": str(e)}


# Global instance
api_client = APIClient()
