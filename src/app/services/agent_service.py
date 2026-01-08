"""
Agent service module for initializing and managing the FRIA agent.
"""
from src.app.agent.fria_agent import friagent
from src.app.core.log_config import setup_logging
from src.app.apis.deps import DBClientDep
from src.app.services.messages import add_message
from src.app.apis.schemas.fria_agent_schema import AgentContinueSchema, AgentInitializeSchema

logger = setup_logging("AGENT SERVICE")

def initialize_agent(db: DBClientDep,
        agent_initialize_data: AgentInitializeSchema
        ) -> dict:
    """Initialize the FRIA agent for a specific user."""
    try:
        thread_config = {
            "configurable" : {
                "thread_id" : agent_initialize_data.session_id
            }
        }

        agent_state = friagent.invoke(
            {
                "agent_state": "initiate",
                "mode": agent_initialize_data.mode,
                "transcription": agent_initialize_data.recorded_transcription,
                "vehicle_type": agent_initialize_data.vehicle_type,
            },
            config=thread_config
        )

        if agent_initialize_data.mode == "chat" and agent_state["agent_query"]:
            add_message(
                db_client=db,
                session_id=agent_initialize_data.session_id,
                user_id=agent_initialize_data.user_id,
                role="agent",
                content=agent_state["agent_query"],
            )

        return {
            "status": "success",
            "agent_state": agent_state,
            "message": "Agent initialized successfully.",
            "session_id": agent_initialize_data.session_id,
        }
    except Exception as e:
        logger.error("Error initializing agent for user %s and session %s: %s", agent_initialize_data.user_id, agent_initialize_data.session_id, e)
        return {
            "status": "error",
            "message": str(e),
            "agent_state": None,
            "session_id": agent_initialize_data.session_id,
        }

def agent_continue(db: DBClientDep,
                   agent_continue_data: AgentContinueSchema) -> dict:
    """Continue the FRIA agent interaction for a specific user."""
    try:
        thread_config = {
            "configurable" : {
                "thread_id" : agent_continue_data.session_id
            }
        }

        if agent_continue_data.user_response:
            add_message(
                db_client=db,
                session_id=agent_continue_data.session_id,
                user_id=agent_continue_data.user_id,
                role="user",
                content=agent_continue_data.user_response
            )
        agent_state = friagent.invoke(
            {
                "agent_state": "in_progress",
                "vehicle_type": agent_continue_data.vehicle_type,
                "user_response": agent_continue_data.user_response,
            },
            config=thread_config
        )

        if agent_state["agent_query"]:
            add_message(
                db_client=db,
                session_id=agent_continue_data.session_id,
                user_id=agent_continue_data.user_id,
                role="agent",
                content=agent_state["agent_query"],
            )

        return {
            "status": "success",
            "agent_state": agent_state,
            "message": "Agent continued successfully.",
            "session_id": agent_continue_data.session_id,
        }
    except Exception as e:
        logger.error("Error continuing agent for user %s and session %s: %s", agent_continue_data.user_id, agent_continue_data.session_id, e)
        return {
            "status": "error",
            "message": str(e),
            "agent_state": None,
            "session_id": agent_continue_data.session_id,
        }
