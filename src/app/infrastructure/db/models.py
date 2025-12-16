import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    contact_number = Column(String, nullable=True)
    birthdate = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    driver_license_state = Column(String, nullable=True)
    credit_score = Column(String, nullable=True)

class VehicleInfo(Base):
    __tablename__ = "vehicle_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    
    vehicle_make = Column(String, nullable=False)  # e.g., "Tesla"
    vehicle_model = Column(String, nullable=False)
    vehicle_year = Column(String, nullable=False)
    vehicle_vin_number = Column(String, unique=True, nullable=False)
    license_plate = Column(String, unique=True, nullable=False)
    vehicle_color = Column(String, nullable=True)
    odometer_reading = Column(String, nullable=True)
    usage_type = Column(String, nullable=True)  # e.g., "Business"
    ownership_status = Column(String, nullable=True)  # e.g., "Owned"
    telematics_opt_in = Column(Boolean, default=False)
    avg_speed_mph = Column(String, nullable=True)
    hard_brakes_per_100mi = Column(String, nullable=True)
    annual_mileage = Column(String, nullable=True)

    #relationships
    user = relationship("UserProfile", back_populates="vehicles_info")

class InsurancePolicyDetails(Base):
    __tablename__ = "insurance_policy_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicle_info.id"), nullable=False)

    policy_start_date = Column(DateTime, nullable=False)
    policy_end_date = Column(DateTime, nullable=False)
    coverage_types = Column(Text, nullable=True)  # e.g., "Liability,Collision"
    liability_limit = Column(String, nullable=True)
    deductible_amount = Column(String, nullable=True)
    annual_premium_usd = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)  # e.g., "Credit Card"
    last_payment_date = Column(DateTime, nullable=True)
    policy_status = Column(String, nullable=True)  # e.g., "Active", "Lapsed"
    claims_count = Column(String, nullable=True)
    claims_total_amount_usd = Column(String, nullable=True)
    last_claim_date = Column(DateTime, nullable=True)

    user = relationship("UserProfile", back_populates="insurance_policies")
    vehicle = relationship("VehicleInfo", back_populates="insurance_policies")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicle_info.id"), nullable=False)
    user_name = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="session")
    user = relationship("UserProfile", back_populates="sessions")
    vehicle = relationship("VehicleInfo", back_populates="sessions")
    #tow_request = relationship("TowRequest", back_populates="session", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)

    role = Column(String, nullable=False)  # "user" | "agent"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")
    user = relationship("UserProfile", back_populates="messages")


# class TowRequest(Base):
#     __tablename__ = "tow_requests"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))

#     damage_description = Column(Text)
#     accident_location_address = Column(Text)
#     is_vehicle_operable = Column(String)
#     reason_for_towing = Column(Text)

#     finalized_at = Column(DateTime, default=datetime.utcnow)

#     session = relationship("Session", back_populates="tow_request")
