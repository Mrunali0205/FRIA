"""Document APIs for handling MongoDB interactions."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from src.app.services.document_services import (insert_towing_document, get_towing_document_by_id, update_towing_document)
from src.app.core.database import get_mongo_db
from src.app.services.generate_pdf import create_pdf_from_json
from src.app.infrastructure.db.mongo_db_models import InsertTowingDocument
from src.app.core.log_config import setup_logging

logger = setup_logging(__name__)

router = APIRouter(prefix="/documents", tags=["Document Endpoints"])

@router.post("/insert-towing-documents", status_code=status.HTTP_201_CREATED)
async def create_towing_document(
    document: InsertTowingDocument,
    mongodb=Depends(get_mongo_db)
):
    """API endpoint to create a towing document in MongoDB."""
    document_id = await insert_towing_document(document, mongodb)
    if not document_id:
        logger.error("No document id is returned")
        raise HTTPException(status_code=500, detail="Failed to create towing document.")
    return {"status_code": 201, "message": "Towing document created successfully.", "document_id": document_id}

@router.get("/get-towing-document/{document_id}", status_code=status.HTTP_200_OK)
async def read_towing_document(
    document_id: str,
    mongodb=Depends(get_mongo_db)
):
    """API endpoint to retrieve a towing document by its ID from MongoDB."""
    document = await get_towing_document_by_id(document_id, mongodb)
    if not document:
        logger.error("Towing document with ID %s not found.", document_id)
        raise HTTPException(status_code=404, detail="Towing document not found.")
    return {"status_code": 200, "message": "Towing document retrieved successfully.", "document": document}

@router.put("/update-towing-document/{document_id}", status_code=status.HTTP_200_OK)
async def modify_towing_document(
    document_id: str,
    update_data: dict,
    mongodb=Depends(get_mongo_db)
):
    """API endpoint to update a towing document in MongoDB."""
    success = await update_towing_document(document_id, update_data, mongodb)
    if not success:
        logger.error("Failed to update towing document with ID %s.", document_id)
        raise HTTPException(status_code=500, detail="Failed to update towing document.")
    return {"status_code": 200, "message": "Towing document updated successfully."}

@router.post("/download-towing-pdf", status_code=status.HTTP_200_OK)
async def download_towing_pdf(towing_document: InsertTowingDocument):
    """
    Generate a PDF from the provided towing_document JSON and return it as a downloadable file.
    """
    try:
        pdf_buffer = create_pdf_from_json(towing_document.dict())
        if not pdf_buffer:
            logger.error("PDF generation returned no data")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
        pdf_buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="towing_report.pdf"'}
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating/downloading PDF: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
