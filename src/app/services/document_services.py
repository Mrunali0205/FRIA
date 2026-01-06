"""Document services for handling MongoDB interactions."""
from bson.objectid import ObjectId
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
    
async def get_towing_document_by_id(
    document_id: str,
    mongodb
):
    """Retrieve a towing document by its ID from MongoDB."""
    try:
        id = ObjectId(document_id)
        document = await mongodb.towing_documents.find_one({"_id": id})
        if document:
            logger.info(f"Towing document retrieved with ID: {document_id}")
            return TowingDocumentModel(**document)
        else:
            logger.warning(f"Towing document with ID {document_id} not found.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving towing document: {e}")
        return None
    
async def update_towing_document(
    document_id: str,
    update_data: dict,
    mongodb
):
    """Update a towing document in MongoDB."""
    try:
        id = ObjectId(document_id)
        if await get_towing_document_by_id(document_id, mongodb) is None:
            logger.warning(f"Towing document with ID {document_id} not found for update.")
            return False
        result = await mongodb.towing_documents.update_one(
            {"_id": id},
            {"$set": update_data}
        )
        if result.modified_count:
            logger.info(f"Towing document with ID {document_id} updated successfully.")
            return True
        else:
            logger.warning(f"No updates made to towing document with ID {document_id}.")
            return False
    except Exception as e:
        logger.error(f"Error updating towing document: {e}")
        return False