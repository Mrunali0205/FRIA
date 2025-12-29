
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

    return session_info.get("id") if session_info else None

def fetch_messages_by_session_id(db_client: DBClientDep, session_id: str) -> list:
    """
    Fetch messages from the database by session ID.
    """
    messages = db_client.fetch_all(
        query="SELECT * FROM messages WHERE session_id=:session_id ORDER BY created_at ASC",
        params={"session_id": session_id}
    )

    return messages

def create_session_id(db_client: DBClientDep, user_id: str, vehicle_id: str, user_name: str) -> str:
    """
    Create a new session ID for the user.
    """
    session_id = db_client.insert_returning_id(
        query="INSERT INTO sessions (user_id) VALUES (:user_id) RETURNING id",
        params={"user_id": user_id, "vehicle_id": vehicle_id, "user_name": user_name}
    )

    return session_id

def add_message(db_client: DBClientDep, session_id: str, user_id: str, role: str, content: str) -> None:
    """
    add a message in the database.
    """
    db_client.insert(
        query="INSERT INTO messages (session_id, user_id, role, content) VALUES (:session_id, :user_id, :role, :content)",
        values={"session_id": session_id, "user_id": user_id, "role": role, "content": content}
    )

