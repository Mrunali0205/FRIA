"""User and System related API endpoints."""
from fastapi import APIRouter, HTTPException
from src.app.core.log_config import setup_logging
from src.app.services.user_service import (
    fetch_user_by_name,
    fetch_insurance_details_by_vehicle_id,
    fetch_session_id_by_user_vechicle_id,
    create_session_id,
    fetch_vehicle_by_user_id,

)
from src.app.services.messages import fetch_messages_by_session_id
from src.app.apis.schemas.user_system_schema import CreateSessionSchema
from src.app.apis.deps import DBClientDep

logger = setup_logging("USERS & SYSTEM API")

router = APIRouter(prefix="/users_system", tags=["User & System endpoints"])

@router.get("/get_user_details/{user_name}", summary="Get User Details", tags=["User & System"])
def get_user_details(user_name: str, db_client: DBClientDep) -> dict:
    """
    Endpoint to get user details by user ID.
    """
    user_info = fetch_user_by_name(db_client, user_name)

    if not user_info:
        logger.error(f"User {user_name} not found.")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User {user_name} details retrieved successfully.")
    return user_info

@router.get("/get_vehicle_details/{user_id}", summary="Get Vehicle Details", tags=["User & System"])
def get_vehicle_details(user_id: str, db_client: DBClientDep) -> dict:
    """
    Endpoint to get vehicle details by user ID.
    """
    vehicle_info = fetch_vehicle_by_user_id(db_client, user_id)

    if not vehicle_info:
        logger.error(f"Vehicle for user ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    logger.info(f"Vehicle details for user ID {user_id} retrieved successfully.")
    return vehicle_info

@router.get("/get_insurance_by_vehicle/{vehicle_id}", summary="Get Insurance Details by Vehicle ID", tags=["User & System"])
def get_insurance_by_vehicle(vehicle_id: str, db_client: DBClientDep) -> dict:
    """
    Endpoint to get insurance details by vehicle ID.
    """
    insurance_info = fetch_insurance_details_by_vehicle_id(db_client, vehicle_id)

    if not insurance_info:
        logger.error(f"Insurance details for vehicle ID {vehicle_id} not found.")
        raise HTTPException(status_code=404, detail="Insurance details not found")
    
    logger.info(f"Insurance details for vehicle ID {vehicle_id} retrieved successfully.")
    return insurance_info

@router.post("/create_session", summary="Create Session", tags=["User & System"])
def create_session(session_data: CreateSessionSchema, db_client: DBClientDep) -> dict:
    """
    Endpoint to create a new session for a user and vehicle.
    """
    session_id = create_session_id(db_client, session_data.user_id, session_data.vehicle_id, session_data.user_name)
    if not session_id:
        logger.error("Failed to create session.")
        raise HTTPException(status_code=500, detail="Failed to create session")

    logger.info(f"Session created successfully with ID {session_id}.")
    return {"session_id": session_id}

@router.get("/get_session_id/{user_id}/{vehicle_id}", summary="Get Session ID", tags=["User & System"])
def get_user_session_id(user_id: str, vehicle_id: str, db_client: DBClientDep) -> dict:
    """
    Helper function to get session ID by user ID and vehicle ID.
    """
    session_id = fetch_session_id_by_user_vechicle_id(db_client, user_id, vehicle_id)
    return session_id

@router.get("/get_messages/{session_id}", summary="Get Messages by Session ID", tags=["User & System"])
def get_messages(session_id: str, db_client: DBClientDep) -> list:
    """
    Endpoint to get messages by session ID.
    """
    messages = fetch_messages_by_session_id(db_client, session_id)

    if messages is None:
        logger.error(f"No messages found for session ID {session_id}.")
        raise HTTPException(status_code=404, detail="No messages found for this session")

    logger.info(f"Messages for session ID {session_id} retrieved successfully.")
    return messages
