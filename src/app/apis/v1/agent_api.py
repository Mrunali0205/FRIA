from fastapi import APIRouter
from src.app.services.agent_service import (initialize_agent, agent_continue)
from src.app.apis.deps import DBClientDep
from src.app.apis.schemas.fria_agent_schema import AgentInitializeSchema, AgentContinueSchema

from src.app.core.log_config import setup_logging

logger = setup_logging("AGENT API")

router = APIRouter(prefix="/agent", tags=["Agent Services"])

@router.post("/initialize", summary="Initialize FRIA Agent", tags=["Agent Service"])
def api_initialize_agent(agent_initialize_data: AgentInitializeSchema, db_client: DBClientDep):
    """
    Endpoint to initialize the FRIA agent for a specific user.
    """
    response = initialize_agent(db_client, 
                              user_id = agent_initialize_data.user_id,
                              session_id = agent_initialize_data.session_id,
                              mode = agent_initialize_data.mode,
                              recorded_transcription = agent_initialize_data.recorded_transcription,
                              vehicle_type = agent_initialize_data.vehicle_type
                             )
    return response

@router.post("/continue", summary="Continue FRIA Agent Interaction", tags=["Agent Service"])
def api_continue_agent_interaction(agent_continue_data: AgentContinueSchema, db_client: DBClientDep):
    """
    Endpoint to continue the FRIA agent interaction.
    """
    response = agent_continue(db_client, 
                              user_id = agent_continue_data.user_id,
                              session_id = agent_continue_data.session_id,
                              vehicle_type = agent_continue_data.vehicle_type,
                              user_response = agent_continue_data.user_response
                             )
    return response