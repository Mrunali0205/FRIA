import uuid
from fastapi import FastAPI
from app.agent.fria_agent import invoke_agent
from app.apis.schemas.fria_agent_schema import (
    FriaAgentInvokeSchema, TowingGuideInvokeSchema
)

app = FastAPI()

@app.get("/agent/start")
def start_agent_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@app.post("/agent/invoke")
def invoke_agent_session(req: FriaAgentInvokeSchema):
    response = invoke_agent(
        user_message=req.user_message,
        chat_history=req.chat_history,
        current_data=req.current_data
    )
    return {"session_id": req.session_id, "response": response}

@app.post("/agent/invoke_towing_guide")
def invoke_towing_guide(req: TowingGuideInvokeSchema):
    response = invoke_agent(
        towing_instruction=req.towing_instruction
    )
    return {"session_id": req.session_id, "response": response}