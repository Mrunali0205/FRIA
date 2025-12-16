"""
Main file to run FastAPI app for FRIA agent and services.
"""

import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command
from pydantic import BaseModel

from src.app.agent.MruNav_agent import agent
from src.app.apis.schemas.fria_agent_schema import (
    FriaAgentInvokeSchema,
)
# GPS router
from src.app.routers.location_routers import router as location_router
#database
from src.app.infrastructure.db.postgres import SessionLocal
from src.app.infrastructure.db.repository import (
    create_session,
    save_message,
    save_tow_request,
)
from src.app.infrastructure.db.session_repo import update_session_snapshot
from src.app.infrastructure.db.state_serializer import serialize_state

from src.app.services.audio_transcription_service import transcribe_mic

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(location_router)
class GeoRequest(BaseModel):
    lat: float
    lon: float

@app.get("/agent/start")
async def start_agent_session():
    session_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        create_session(db, session_id, "John Doe")
    finally:
        db.close()
    final_state = await agent.ainvoke(
        {"user_name": "John Doe"},
        config={"configurable": {"thread_id": session_id}},
    )
    snapshot = serialize_state(final_state)
    update_session_snapshot(session_id, snapshot)

    last_message = final_state["messages"][-1].content
    return {
        "session_id": session_id,
        "last_message": last_message,
    }



@app.post("/agent/continue")
async def agent_continue(req: FriaAgentInvokeSchema):
    resume_payload = {}

    if req.user_message is not None:
        resume_payload["user_message"] = req.user_message

    if req.lat is not None and req.lon is not None:
        resume_payload["lat"] = req.lat
        resume_payload["lon"] = req.lon

    final_state = await agent.ainvoke(
        Command(resume=resume_payload),
        config={"configurable": {"thread_id": str(req.session_id)}},
    )

    snapshot = serialize_state(final_state)
    update_session_snapshot(str(req.session_id), snapshot)

    last_message = final_state["messages"][-1].content
    return {"last_message": last_message}

@app.post("/location/reverse-geocode")
def reverse_geocode_location(req: GeoRequest):
    from src.app.services.gps_location_service import reverse_geocode
    address = reverse_geocode(req.lat, req.lon)
    return {
        "success": True,
        "address": address,
        "lat": req.lat,
        "lon": req.lon,
    }

@app.post("/agent/transcribe")
async def transcribe_audio():
    text = await transcribe_mic()
    return {"transcript": text}

