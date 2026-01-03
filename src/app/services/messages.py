"""Messages service module."""
from src.app.apis.deps import DBClientDep
from src.app.core.log_config import setup_logging

logger = setup_logging("MESSAGES SERVICE")

def add_message(db_client: DBClientDep, session_id: str, user_id: str, role: str, content: str) -> None:
    """
    add a message in the database.
    """
    db_client.insert(
        query="INSERT INTO messages (session_id, user_id, role, content) VALUES (:session_id, :user_id, :role, :content)",
        values={"session_id": session_id, "user_id": user_id, "role": role, "content": content}
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