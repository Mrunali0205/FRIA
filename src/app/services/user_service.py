"""user service module for handling user-related database operations."""
import uuid
import datetime
from src.app.apis.deps import DBClientDep
from src.app.core.log_config import setup_logging

logger = setup_logging("USER SERVICE")

def fetch_user_by_name(db_client: DBClientDep, user_name: str) -> dict:
    """
    Fetch user details from the database by user name.
    """
    user_info = db_client.fetch_one(
        query="SELECT * FROM user_profiles WHERE name=:user_name",
        params={"user_name": user_name}
    )

    return user_info

def fetch_vehicle_by_user_id(db_client: DBClientDep, user_id: str) -> dict:
    """
    Fetch vehicle details from the database by user ID.
    """
    vehicle_info = db_client.fetch_one(
        query="SELECT * FROM vehicle_info WHERE user_id=:user_id",
        params={"user_id": user_id}
    )

    return vehicle_info

def fetch_insurance_details_by_user_id(db_client: DBClientDep, user_id: str, ) -> dict:
    """
    Fetch insurance details from the database by user ID.
    """
    insurance_info = db_client.fetch_one(
        query="SELECT * FROM insurance_policy_details WHERE user_id=:user_id",
        params={"user_id": user_id}
    )

    return insurance_info

def fetch_insurance_details_by_vehicle_id(db_client: DBClientDep, vehicle_id: str) -> dict:
    """
    Fetch insurance details from the database by vehicle ID.
    """
    insurance_info = db_client.fetch_one(
        query="SELECT * FROM insurance_policy_details WHERE vehicle_id=:vehicle_id",
        params={"vehicle_id": vehicle_id}
    )

    return insurance_info

def fetch_session_id_by_user_vechicle_id(db_client: DBClientDep, user_id: str, vehicle_id: str) -> str:
    """
    Fetch session ID from the database by user ID.
    """
    session_info = db_client.fetch_one(
        query="SELECT id FROM sessions WHERE user_id=:user_id AND vehicle_id=:vehicle_id",
        params={"user_id": user_id, "vehicle_id": vehicle_id}
    )

    if not session_info:
        return {"session_id": None}

    return {"session_id": session_info["id"]}

def create_session_id(db_client: DBClientDep, user_id: str, vehicle_id: str, user_name: str) -> str:
    """
    Create a new session ID for the user.
    """
    generated_session_id = str(uuid.uuid4())
    time = datetime.datetime.now(datetime.timezone.utc)
    session_id = db_client.insert_returning_id(
        query="INSERT INTO sessions (id, user_id, vehicle_id, user_name, started_at) VALUES (:id, :user_id, :vehicle_id, :user_name, :started_at) RETURNING id",
        values={"id": generated_session_id, "user_id": user_id, "vehicle_id": vehicle_id, "user_name": user_name, "started_at": time}
    )

    return session_id
