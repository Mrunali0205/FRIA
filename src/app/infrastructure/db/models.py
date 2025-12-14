from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="session")
    tow_request = relationship("TowRequest", back_populates="session", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))

    role = Column(String, nullable=False)  # "user" | "agent"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class TowRequest(Base):
    __tablename__ = "tow_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))

    damage_description = Column(Text)
    accident_location_address = Column(Text)
    is_vehicle_operable = Column(String)
    reason_for_towing = Column(Text)

    finalized_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="tow_request")
