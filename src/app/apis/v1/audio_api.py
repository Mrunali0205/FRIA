"""Audio API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from src.app.services.audio_transcription_service import transcribe_mic, add_audio_transcription
from src.app.core.log_config import setup_logging
from src.app.apis.deps import DBClientDep

logger = setup_logging("AUDIO API")

router = APIRouter(prefix="/audio", tags=["Audio Endpoints"])

@router.post("/transcribe-mic", description="Transcribe audio from the default microphone.", tags=["Audio Service"])
def record_and_transcribe(language: str = "en-US", db_client: DBClientDep = Depends(), session_id: str = None, user_id: str = None):
    """
    Record audio from the default microphone and transcribe it using Azure Speech-to-Text.
    """
    transcription = transcribe_mic(language)
    if transcription.startswith("Error:") or transcription.startswith("Exception:") or transcription == "No speech detected.":
        logger.error(f"Transcription failed: {transcription}")
        raise HTTPException(status_code=500, detail=transcription)
    logger.info("Transcription successful.")
    if transcription:
        logger.info("adding transcription to database")
        # Assuming you have session_id and user_id available in this context
        # You might need to modify the function signature to accept these parameters
        add_audio_transcription(db_client, session_id, user_id, transcription)
    return {"transcription": transcription}