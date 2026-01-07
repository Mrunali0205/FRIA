"""
Agent service module for initializing and managing the FRIA agent.
"""
from src.app.agent.fria_agent import friagent
from src.app.core.log_config import setup_logging
from src.app.apis.deps import DBClientDep
from src.app.services.messages import add_message

logger = setup_logging("AGENT SERVICE")

def initialize_agent(db: DBClientDep, user_id: str, session_id: str, mode: str, recorded_transcription: str = None, vehicle_type: str = None) -> dict:
    """Initialize the FRIA agent for a specific user."""
    try:
        thread_config = {
            "configurable" : {
                "thread_id" : session_id
            }
        }

        agent_state = friagent.invoke(
            {
                "agent_state": "initiate",
                "mode": mode,
                "transcription": recorded_transcription,
                "vehicle_type": vehicle_type,
            },
            config=thread_config
        )

        if mode == "chat" and agent_state["agent_query"]:
            add_message(
                db_client=db,
                session_id=session_id,
                user_id=user_id,
                role="agent",
                content=agent_state["agent_query"],
            )

        return {
            "status": "success",
            "agent_state": agent_state,
            "message": "Agent initialized successfully.",
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Error initializing agent for user {user_id} and session {session_id}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "agent_state": None,
            "session_id": session_id,
        }   

def agent_continue(db: DBClientDep, user_id: str, session_id: str, vehicle_type: str = None,
                   user_response: str = None) -> dict:
    """Continue the FRIA agent interaction for a specific user."""
    try:
        thread_config = {
            "configurable" : {
                "thread_id" : session_id
            }
        }

        if user_response:
            add_message(
                db_client=db,
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=user_response
            )
            
        agent_state = friagent.invoke(
            {
                "agent_state": "in_progress",
                "vehicle_type": vehicle_type,
                "user_response": user_response,
            },
            config=thread_config
        )

        if agent_state["agent_query"]:
            add_message(
                db_client=db,
                session_id=session_id,
                user_id=user_id,
                role="agent",
                content=agent_state["agent_query"],
            )

        return {
            "status": "success",
            "agent_state": agent_state,
            "message": "Agent continued successfully.",
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Error continuing agent for user {user_id} and session {session_id}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "agent_state": None,
            "session_id": session_id,
        }