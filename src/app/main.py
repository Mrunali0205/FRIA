import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.fria_agent import invoke_agent
from app.services.gps_location_service import reverse_geocode
from app.apis.schemas.fria_agent_schema import (
    FriaAgentInvokeSchema, 
    TowingGuideInvokeSchema
)

app = FastAPI()

# ---------------------------------------------
# CORS for Reflex frontend
# ---------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # Reflex dev server = http://localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------
# Request Models
# ---------------------------------------------
class GeoRequest(BaseModel):
    lat: float
    lon: float


# ---------------------------------------------
# Agent Session
# ---------------------------------------------
@app.get("/agent/start")
def start_agent_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


# ---------------------------------------------
# Core Conversational Agent Endpoint
# ---------------------------------------------
@app.post("/agent/invoke")
def invoke_agent_session(req: FriaAgentInvokeSchema):
    response = invoke_agent(
        user_message=req.user_message,
        chat_history=req.chat_history,
        current_data=req.current_data
    )
    return {"session_id": req.session_id, "response": response}


# ---------------------------------------------
# Optional: Towing Guide Manual Summaries
# ---------------------------------------------
@app.post("/agent/invoke_towing_guide")
def invoke_towing_guide(req: TowingGuideInvokeSchema):
    response = invoke_agent(
        towing_instruction=req.towing_instruction
    )
    return {"session_id": req.session_id, "response": response}


# ---------------------------------------------
# FIXED: Reverse Geocoding (JSON Body)
# ---------------------------------------------
@app.post("/location/reverse-geocode")
def reverse_geocode_location(req: GeoRequest):
    """
    Convert GPS coordinates → human-readable address.
    Accepts JSON: {"lat": 00.000, "lon": 00.000}
    """
    try:
        address = reverse_geocode(req.lat, req.lon)

        if address:
            return {
                "success": True,
                "address": address,
                "lat": req.lat,
                "lon": req.lon
            }
        else:
            return {
                "success": False,
                "error": "Could not reverse geocode coordinates"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
