from typing import List, Set
from sqlalchemy import inspect
from src.app.core.log_config import setup_logging
from src.app.core.database import engine
from src.app.infrastructure.db.models import Base

logger = setup_logging(__name__)

def check_for_tables_or_seed_create():
    """
    Check if any tables exist in the database.
    If no tables exist, seed the database by creating all tables.
    """
    inspector = inspect(engine)
    existing_tables: Set[str] = set(inspector.get_table_names())
    expected_tables: Set[str] = set(Base.metadata.tables.keys())

    missing = sorted(expected_tables - existing_tables)
    if not missing:
        logger.info("All tables exist. Nothing to create.")
        return []

    logger.info("Missing tables detected: %s. Creating...", missing)
    # Create only the missing tables
    Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables[t] for t in missing])
    logger.info("Created tables: %s", missing)
    return missing 

if __name__ == "__main__":
    check_for_tables_or_seed_create()