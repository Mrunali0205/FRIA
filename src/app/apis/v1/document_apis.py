"""Document APIs for handling MongoDB interactions."""
from fastapi import APIRouter, Depends, HTTPException
from src.app.services.document_services import insert_towing_document
from src.app.core.database import get_mongo_db
from src.app.infrastructure.db.mongo_db_models import TowingDocumentModel
from src.app.core.log_config import setup_logging

logger = setup_logging(__name__)

router = APIRouter(prefix="/documents", tags=["Document APIs"])

@router.post("/insert-towing-documents", response_model=str)
async def create_towing_document(
    document: TowingDocumentModel,
    mongodb=Depends(get_mongo_db)
):
    """API endpoint to create a towing document in MongoDB."""
    
    document_id = await insert_towing_document(document, mongodb)
    if not document_id:
        logger.error(f"No document id is returned")
        raise HTTPException(status_code=500, detail="Failed to create towing document.")