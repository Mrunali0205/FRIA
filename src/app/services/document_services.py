"""Document services for handling MongoDB interactions."""
from src.app.infrastructure.db.mongo_db_models import TowingDocumentModel
from src.app.core.log_config import setup_logging

logger = setup_logging(__name__)

async def insert_towing_document(
    document: TowingDocumentModel,
    mongodb
):
    """Insert a towing document into MongoDB."""
    try:
        doc_dict = document.dict()
        result = await mongodb.towing_documents.insert_one(dict(doc_dict))
        logger.info(f"Towing document inserted with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting towing document: {e}")
        return None