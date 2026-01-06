"""MongoDB models towing documents."""
from pydantic import BaseModel
from datetime import datetime

class UserDetailsModel(BaseModel):
    """Model for user details in towing document."""
    id: str
    name: str
    contact_number: str
    email: str
    gender: str

class VehicleInfoModel(BaseModel):
    """Model for vehicle information in towing document."""
    id: str
    vehicle_model: str
    vehicle_year: str

class TowingDocumentModel(BaseModel):
    """Model for towing document stored in MongoDB."""
    user_details: UserDetailsModel
    vehicle_info: VehicleInfoModel
    session_id: str
    incident_description: str
    operable_status: str
    vehicle_condition: str
    address: str
    is_completed: bool
    is_deleted: bool
    updated_time: int = int(datetime.timestamp(datetime.now()))
    creation_time: int = int(datetime.timestamp(datetime.now()))




    