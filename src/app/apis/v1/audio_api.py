"""Audio API endpoints"""
from fastapi import APIRouter, HTTPException
from src.app.services.audio_transcription_service import AzureSpeechRecognizer, add_audio_transcription
from src.app.core.log_config import setup_logging
from src.app.apis.deps import DBClientDep
from src.app.apis.schemas.audio_schemas import RecordAudioSchema

logger = setup_logging("AUDIO API")
recognizer = AzureSpeechRecognizer()

router = APIRouter(prefix="/audio", tags=["Audio Endpoints"])

@router.get("/start_recording", description="Start transcription from the default microphone.")
def start_recording():
    """
    Record audio from the default microphone and transcribe it using Azure Speech-to-Text.
    """
    try:
        logger.info("Starting transcription...")
        recognizer.recognized_speech = ""
        recognizer.start()
    except Exception as e:
        logger.error("Error starting transcription: %s", e)
        raise HTTPException(status_code=500, detail="Failed to start transcription.")
    return {"status_code": 200, "message": "Transcription started. Speak into the microphone.", "transcription": ""}

@router.post("/stop_recording", description="Stop the ongoing transcription.")
def stop_recording(db_client: DBClientDep, record_audio_schema: RecordAudioSchema):
    """
    Stop the ongoing transcription process.
    """
    try:
        logger.info("Stopping transcription...")
        recognizer.stop()
    except Exception as e:
        logger.error("Error stopping transcription: %s", e)
        raise HTTPException(status_code=500, detail="Failed to stop transcription.")
    transcription = recognizer.recognized_speech.strip()
    if transcription:
        logger.info("Adding transcription to database")
        add_audio_transcription(db_client, record_audio_schema.session_id, record_audio_schema.user_id, transcription)
    logger.info("Transcription stopped.")
    return {"status_code": 200, "message": "Transcription stopped successfully.", "transcription": transcription}
