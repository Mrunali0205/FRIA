from fastapi import APIRouter
from src.app.services.agent_service import (initialize_agent, agent_continue)
from src.app.apis.deps import DBClientDep
from src.app.apis.schemas.fria_agent_schema import AgentInvokeSchema

from src.app.core.log_config import setup_logging

logger = setup_logging("AGENT API")

router = APIRouter(prefix="/agent", tags=["Agent Services"])

@router.get("/initialize/{user_id}/{session_id}", summary="Initialize FRIA Agent", tags=["Agent Service"])
def api_initialize_agent(user_id: str, session_id: str):
    """
    Endpoint to initialize the FRIA agent for a specific user.
    """
    response = initialize_agent(user_id, session_id)
    return response

@router.post("/continue", summary="Continue FRIA Agent Interaction", tags=["Agent Service"])
def api_continue_agent_interaction(agent_invoke_data: AgentInvokeSchema, db_client: DBClientDep):
    """
    Endpoint to continue the FRIA agent interaction.
    """
    response = agent_continue(db_client, 
                              user_id = agent_invoke_data.user_id,
                              session_id = agent_invoke_data.session_id,
                              mode = agent_invoke_data.mode,
                              vehicle_type = agent_invoke_data.vehicle_type,
                              user_response = agent_invoke_data.user_response,
                              transcription = agent_invoke_data.recorded_transcription,
                             )
    return response