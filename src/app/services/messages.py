"""Messages service module."""
import uuid
import datetime
from src.app.apis.deps import DBClientDep
from src.app.core.log_config import setup_logging

logger = setup_logging("MESSAGES SERVICE")

def add_message(db_client: DBClientDep, session_id: str, user_id: str, role: str, content: str) -> None:
    """
    add a message in the database.
    """
    message_id = str(uuid.uuid4())
    created_at = datetime.datetime.now(datetime.timezone.utc)
    db_client.insert(
        query="INSERT INTO messages (id, session_id, user_id, role, content, created_at) VALUES (:id, :session_id, :user_id, :role, :content, :created_at)",
        values={"id": message_id, "session_id": session_id, "user_id": user_id, "role": role, "content": content, "created_at": created_at}
    )

def fetch_messages_by_session_id(db_client: DBClientDep, session_id: str) -> list:
    """
    Fetch messages from the database by session ID.
    """
    messages = db_client.fetch_all(
        query="SELECT * FROM messages WHERE session_id=:session_id ORDER BY created_at ASC",
        params={"session_id": session_id}
    )

    return messages