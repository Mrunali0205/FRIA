from sqlalchemy.orm import Session
from .models import Session as DBSession, Message, TowRequest

def create_session(
    db: Session,
    session_id: str,
    user_name: str | None = None
) -> DBSession:
    session = DBSession(
        id=session_id,      # 👈 critical
        user_name=user_name
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def save_message(
    db: Session,
    session_id,
    role: str,
    content: str,
):
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
    )
    db.add(msg)
    db.commit()


def save_tow_request(
    db: Session,
    session_id,
    damage_description: str,
    accident_location_address: str,
    is_vehicle_operable: str,
    reason_for_towing: str,
):
    tow = TowRequest(
        session_id=session_id,
        damage_description=damage_description,
        accident_location_address=accident_location_address,
        is_vehicle_operable=is_vehicle_operable,
        reason_for_towing=reason_for_towing,
    )
    db.add(tow)
    db.commit()
