import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.app.agent.MruNav_agent import agent
from src.app.services.gps_location_service import reverse_geocode
from src.app.apis.schemas.fria_agent_schema import FriaAgentInvokeSchema, TowingGuideInvokeSchema
from src.app.services.audio_transcription_service import transcribe_audio_file
from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient

from langgraph.types import Command
from pydantic import BaseModel
import tempfile
import shutil
from fastapi import File, UploadFile

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


# GEOCODE MODEL
class GeoRequest(BaseModel):
    lat: float
    lon: float


# START AGENT SESSION
@app.get("/agent/start")
async def start_agent_session():
    session_id = str(uuid.uuid4())
    thread_config = {
        "configurable": {
            "thread_id": session_id
        }
    }
    final_state = await agent.ainvoke(
        {
            "user_name": "John Doe",   
        },
        config=thread_config
    )
    last_message = final_state["messages"][-1]
    return {
        "session_id": session_id,
        "last_message": last_message.content,
        "done": final_state.get("done", False)
    }


# MAIN AGENT INVOKE ENDPOINT
@app.post("/agent/continue")
async def agent_invoke(req: FriaAgentInvokeSchema):
    thread_config = {
        "configurable": {
            "thread_id": req.session_id
        }
    }
    resume_payload = {
        "user_message": req.user_message or "",
    }

    if req.lat is not None and req.lon is not None:
        resume_payload["lat"] = req.lat
        resume_payload["lon"] = req.lon

    if req.audio_transcript is not None:
        resume_payload["audio_transcript"] = req.audio_transcript

    final_state = await agent.ainvoke(
        Command(resume=resume_payload),
        config=thread_config
    )

    last_message = final_state["messages"][-1]

    return {
        "last_message": last_message.content,
        "done": final_state.get("done", False)
    }



# TOWING GUIDE ENDPOINT
#@app.post("/agent/invoke_towing_guide")
#def agent_towing_guide(req: TowingGuideInvokeSchema):
    #response = invoke_agent(
        #towing_instruction=req.towing_instruction
    #)
    #return {"session_id": req.session_id, "response": response}

# REVERSE GEOCODING
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


# AUDIO TRANSCRIPTION ENDPOINT
@app.post("/agent/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    text = transcribe_audio_file(tmp_path)

    return {"transcript": text}




