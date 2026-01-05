"""Audio API endpoints"""
from fastapi import APIRouter, HTTPException
from src.app.services.audio_transcription_service import AzureSpeechRecognizer, add_audio_transcription
from src.app.core.log_config import setup_logging
from src.app.apis.deps import DBClientDep
from src.app.apis.schemas.audio_schemas import RecordAudioSchema

logger = setup_logging("AUDIO API")
recognizer = AzureSpeechRecognizer()

router = APIRouter(prefix="/audio", tags=["Audio Endpoints"])

@router.get("/start_recording", description="Start transcription from the default microphone.", tags=["Audio Service"])
def start_recording(): 
    """
    Record audio from the default microphone and transcribe it using Azure Speech-to-Text.
    """
    recognizer.start()
    recognizer.recognized_speech = "" 
    return {"message": "Transcription started. Speak into the microphone.",
            "transcription": ""}

@router.post("/stop_recording", description="Stop the ongoing transcription.", tags=["Audio Service"])
def stop_recording(db_client: DBClientDep, record_audio_schema: RecordAudioSchema):
    """
    Stop the ongoing transcription process.
    """
    recognizer.stop()
    transcription = recognizer.recognized_speech.strip()
    if transcription:
        logger.info("adding transcription to database")
        add_audio_transcription(db_client, record_audio_schema.session_id, record_audio_schema.user_id, transcription)
    logger.info("Transcription stopped.")
    return {"message": "Transcription stopped successfully.",
            "transcription": transcription}