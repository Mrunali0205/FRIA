import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.agent.MruNav_agent import agent
from pydantic import BaseModel

from app.agent.fria_agent import invoke_agent
from langgraph.types import Command
from app.services.gps_location_service import reverse_geocode
from app.apis.schemas.fria_agent_schema import (
    FriaAgentInvokeSchema, 
    TowingGuideInvokeSchema
)

# NEW: audio service import
from app.services.audio_transcription_service import transcribe_mic

app = FastAPI()

# ----------------------------------------------------
# CORS (allows frontend on localhost:3000 to connect)
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # during local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# GEOCODE MODEL
# ---------------------------
class GeoRequest(BaseModel):
    lat: float
    lon: float

# ---------------------------
# START AGENT SESSION
# ---------------------------
@app.get("/agent/start")
async def start_agent_session():
    session_id = str(uuid.uuid4())
    thread_config = {
        "configurable" : {
            "thread_id": session_id
        }
    }
    final_state = await agent.ainvoke(
         {
        "user_name" : "John Doe",
         },
         config=thread_config
    )
    last_message = final_state['messages'][-1]
    return {
        "session_id": session_id,
        "last_message": last_message.content
    }

# ---------------------------
# MAIN AGENT INVOKE ENDPOINT
# ---------------------------
@app.post("/agent/continue")
async def agent_invoke(req: FriaAgentInvokeSchema):
    thread_config = {
        "configurable" : {
            "thread_id": req.session_id
        }
    }
    final_state = await agent.ainvoke(
        Command(resume=
                {
                    "user_message": req.user_message,
                }),
         config=thread_config
    )
    last_message = final_state['messages'][-1]

    return  {"last_message": last_message.content}

# ---------------------------
# TOWING GUIDE ENDPOINT
# ---------------------------
@app.post("/agent/invoke_towing_guide")
def agent_towing_guide(req: TowingGuideInvokeSchema):
    response = invoke_agent(
        towing_instruction=req.towing_instruction
    )
    return {"session_id": req.session_id, "response": response}

# ---------------------------
# REVERSE GEOCODING
# ---------------------------
@app.post("/location/reverse-geocode")
def reverse_geocode_location(req: GeoRequest):
    try:
        address = reverse_geocode(req.lat, req.lon)
        if address:
            return {
                "success": True,
                "address": address,
                "lat": req.lat,
                "lon": req.lon
            }
        return {"success": False, "error": "Could not reverse geocode"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------------------------
# AUDIO TRANSCRIPTION ENDPOINT
# ---------------------------
@app.post("/agent/transcribe")
def transcribe_audio():
    """
    Trigger microphone-based audio transcription.
    """
    text = transcribe_mic()
    return {"transcript": text}
