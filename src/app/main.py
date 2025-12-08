import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# LangGraph agent
from src.app.agent.MruNav_agent import agent
from langgraph.types import Command

# Schemas
from app.apis.schemas.fria_agent_schema import (
    FriaAgentInvokeSchema,
    TowingGuideInvokeSchema
)

# Towing guide agent
from app.agent.fria_agent import invoke_agent

# GPS router
from src.app.routers.location_routers import router as location_router

# Audio
from app.services.audio_transcription_service import transcribe_mic

# Geocode model (only needed for the plain reverse-geocode endpoint)
from pydantic import BaseModel
class GeoRequest(BaseModel):
    lat: float
    lon: float


# CREATE FASTAPI APP
app = FastAPI()

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTER ROUTERS
app.include_router(location_router)

# START AGENT SESSION

@app.get("/agent/start")
async def start_agent_session():
    session_id = str(uuid.uuid4())
    final_state = await agent.ainvoke(
        {"user_name": "John Doe"},
        config={"configurable": {"thread_id": session_id}}
    )
    last_message = final_state["messages"][-1].content
    return {
        "session_id": session_id,
        "last_message": last_message
    }



@app.post("/agent/continue")
async def agent_invoke(req: FriaAgentInvokeSchema):

    final_state = await agent.ainvoke(
        Command(
            resume={
                "user_message": req.user_message,
            }
        ),
        config={"configurable": {"thread_id": req.session_id}}
    )

    last_message = final_state["messages"][-1].content
    return {"last_message": last_message}

# TOWING GUIDE ENDPOINT

@app.post("/agent/invoke_towing_guide")
def agent_towing_guide(req: TowingGuideInvokeSchema):
    response = invoke_agent(towing_instruction=req.towing_instruction)
    return {
        "session_id": req.session_id,
        "response": response
    }


# SIMPLE REVERSE-GEOCODE ENDPOINT
# delete this if location_router handles everything)
@app.post("/location/reverse-geocode")
def reverse_geocode_location(req: GeoRequest):
    from app.services.gps_location_service import reverse_geocode
    address = reverse_geocode(req.lat, req.lon)
    return {
        "success": True,
        "address": address,
        "lat": req.lat,
        "lon": req.lon
    }

# AUDIO TRANSCRIPTION
@app.post("/agent/transcribe")
def transcribe_audio():
    text = transcribe_mic()
    return {"transcript": text}




