"""Agent API Endpoints for FRIA Agent Initialization and Interaction."""
from fastapi import APIRouter, HTTPException
from src.app.services.agent_service import (initialize_agent, agent_continue)
from src.app.apis.deps import DBClientDep
from src.app.apis.schemas.fria_agent_schema import AgentInitializeSchema, AgentContinueSchema

from src.app.core.log_config import setup_logging

logger = setup_logging("AGENT API")

router = APIRouter(prefix="/agent", tags=["Agent Endpoints"])

@router.post("/initialize", summary="Initialize FRIA Agent")
def api_initialize_agent(agent_initialize_data: AgentInitializeSchema, db_client: DBClientDep):
    """
    Endpoint to initialize the FRIA agent for a specific user.
    """
    response = initialize_agent(db_client, agent_initialize_data=agent_initialize_data)
    if response["status"] == "error":
        logger.error("Failed to initialize agent: %s", response["message"])
        raise HTTPException(status_code=500, detail=response["message"])
    return {"status_code": 200, "data": response}

@router.post("/continue", summary="Continue FRIA Agent Interaction")
def api_continue_agent_interaction(agent_continue_data: AgentContinueSchema, db_client: DBClientDep):
    """
    Endpoint to continue the FRIA agent interaction.
    """
    response = agent_continue(db_client, agent_continue_data=agent_continue_data)
    if response["status"] == "error":
        logger.error("Failed to continue agent interaction: %s", response["message"])
        raise HTTPException(status_code=500, detail=response["message"])
    return {"status_code": 200, "data": response}
