"""Document services for handling MongoDB interactions."""
import datetime
from bson.objectid import ObjectId
from src.app.infrastructure.db.mongo_db_models import ReadTowingDocument, InsertTowingDocument
from src.app.core.log_config import setup_logging

logger = setup_logging(__name__)

async def insert_towing_document(
    document: InsertTowingDocument,
    mongodb
):
    """Insert a towing document into MongoDB."""
    try:
        doc_dict = document.dict()
        doc_dict["is_completed"] = True
        doc_dict["is_deleted"] = False
        doc_dict["creation_time"] = int(datetime.datetime.timestamp(datetime.datetime.now()))
        doc_dict["updated_time"] = int(datetime.datetime.timestamp(datetime.datetime.now()))
        result = await mongodb.towing_documents.insert_one(dict(doc_dict))
        logger.info("Towing document inserted with ID: %s", result.inserted_id)
        return str(result.inserted_id)
    except Exception as e:
        logger.error("Error inserting towing document: %s", e)
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
            logger.info("Towing document retrieved with ID: %s", document_id)
            return ReadTowingDocument(**document)
        logger.warning("Towing document with ID %s not found.", document_id)
        return None
    except Exception as e:
        logger.error("Error retrieving towing document: %s", e)
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
            logger.warning("Towing document with ID %s not found for update.", document_id)
            return False
        result = await mongodb.towing_documents.update_one(
            {"_id": id},
            {"$set": update_data}
        )
        if result.modified_count:
            logger.info("Towing document with ID %s updated successfully.", document_id)
            return True
        logger.warning("No updates made to towing document with ID %s.", document_id)
        return False
    except Exception as e:
        logger.error("Error updating towing document: %s", e)
        return False
