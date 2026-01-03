"""Audio API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from src.app.services.audio_transcription_service import transcribe_mic, add_audio_transcription
from src.app.core.log_config import setup_logging

logger = setup_logging("AUDIO API")

router = APIRouter(prefix="/audio", tags=["Audio Endpoints"])

@router.get("/transcribe-mic", description="Transcribe audio from the default microphone.", tags=["Audio Service"])
def record_and_transcribe(language: str = "en-US"):
    """
    Record audio from the default microphone and transcribe it using Azure Speech-to-Text.
    """
    transcription = transcribe_mic(language)
    if transcription.startswith("Error:") or transcription.startswith("Exception:") or transcription == "No speech detected.":
        logger.error(f"Transcription failed: {transcription}")
        raise HTTPException(status_code=500, detail=transcription)
    return {"transcription": transcription}