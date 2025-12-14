import json
from sqlalchemy import text
from src.app.infrastructure.db.postgres import engine

def update_session_snapshot(session_id: str, snapshot: dict):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE sessions
                SET state_snapshot = :snapshot
                WHERE id = :session_id
            """),
            {
                "session_id": session_id,
                "snapshot": json.dumps(snapshot)  # 🔑 THIS
            }
        )
def create_session(session_id: str, user_name: str):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO sessions (id, user_name)
                VALUES (:id, :user_name)
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": session_id,
                "user_name": user_name
            }
        )


