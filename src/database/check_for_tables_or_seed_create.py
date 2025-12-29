from typing import Set
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.app.core.log_config import setup_logging
from src.app.core.database import engine
from src.app.utils.db import SessionLocal
from src.app.infrastructure.db.models import Base

from src.app.infrastructure.db.models import UserProfile, VehicleInfo, InsurancePolicyDetails

logger = setup_logging(__name__)

user_seed_data = [
    {
        "name": "Alex Smith",
        "email": "alex.smith@example.com",
        "contact_number": "+1234567890",
        "birthdate": "1990-01-01",
        "gender": "Male",
        "city": "Chicago",
        "state": "IL",
        "driver_license_state": "IL",
        "credit_score": "750"
    }

]

vehicle_seed_data = [
    {
        "user_id": "",
        "vehicle_make": "Tesla",
        "vehicle_model": "Model Y",
        "vehicle_year": "2023",
        "vehicle_vin_number": "VINM2HC1G1E22EU47",
        "license_plate": "ABC1234",
        "vehicle_color": "Red",
        "odometer_reading": "5000",
        "usage_type": "Bussiness",
        "ownership_status": "Owned",
        "telematics_opt_in": True,
        "avg_speed_mph": "55",
        "hard_brakes_per_100mi": "2",
        "annual_mileage": "12000"
    }
]

insurance_policy_seed_data = [
    {
        "user_id": "",
        "vehicle_id": "",
        "policy_start_date": "2023-01-01",
        "policy_end_date": "2026-05-01",
        "coverage_types": "Full",
        "liability_limit": "1000000",
        "deductible_amount": "500",
        "annual_premium_usd": "1200",
        "payment_method": "Credit Card",
        "last_payment_date": "2023-12-01",
        "policy_status": "Active",
        "claims_count": "0",
        "claims_total_amount_usd": "0",
        "last_claim_date": None
    }
]



def check_for_tables_or_seed_create():
    """
    Check if any tables defined in models exist in the database or not.
    If given tables doesn't exist, seed the database by creating specific tables.
    """
    inspector = inspect(engine)
    existing_tables: Set[str] = set(inspector.get_table_names())
    expected_tables: Set[str] = set(Base.metadata.tables.keys())

    missing = sorted(expected_tables - existing_tables)
    if not missing:
        logger.info("All tables exist. Nothing to create.")
        return []
    
    logger.info("Missing tables detected: %s. Creating...", missing)
    
    Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables[t] for t in missing])
    logger.info("Created tables: %s", missing)
    return missing 

def seed_data_to_tables(db: Session = SessionLocal()):
    """
    Seed initial data to tables.
    check if there is intial seed data in tables, if not seed the data.
    """
    try:
        user_id = None
        vehicle_id = None
        user_count = db.query(UserProfile).count()
        if user_count == 0:
            for user_data in user_seed_data:
                user = UserProfile(**user_data)
                db.add(user)
                db.flush()  
                user_id = user.id
            db.commit()

            logger.info("Seeded user_profiles table.")

        vehicle_count = db.query(VehicleInfo).count()
        if vehicle_count == 0:
            for vehicle_data in vehicle_seed_data:
                vehicle = VehicleInfo(**vehicle_data)
                if user_id:
                    vehicle.user_id = user_id
                db.add(vehicle)
                db.flush()  
                vehicle_id = vehicle.id
            db.commit()
            logger.info("Seeded vehicle_info table.")

        insurance_count = db.query(InsurancePolicyDetails).count()
        if insurance_count == 0:
            for insurance_data in insurance_policy_seed_data:
                if user_id:
                    insurance_data["user_id"] = user_id
                if vehicle_id:
                    insurance_data["vehicle_id"] = vehicle_id
                insurance = InsurancePolicyDetails(**insurance_data)
                db.add(insurance)
            db.commit()
            logger.info("Seeded insurance_policy_details table.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error seeding data: %s", e)
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Adding the tables to database")
    check_for_tables_or_seed_create()
    logger.info("Added the tables to database")
    logger.info("Seeding initial data to tables if not present")
    seed_data_to_tables()
    logger.info("Seeded initial data to tables if not present")