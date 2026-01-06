"""Audio transcription services."""
import uuid
import datetime
import azure.cognitiveservices.speech as speechsdk
from src.app.core.config import settings
from src.app.core.log_config import setup_logging
from src.app.apis.deps import DBClientDep

logger = setup_logging("AUDIO TRANSCRIPTION SERVICE")

SPEECH_KEY = settings.AZURE_SPEECH_KEY if hasattr(settings, "AZURE_SPEECH_KEY") else None
SPEECH_REGION = settings.AZURE_SPEECH_REGION if hasattr(settings, "AZURE_SPEECH_REGION") else None


class AzureSpeechRecognizer:
    """Azure Speech-to-Text recognizer using microphone input."""
    def __init__(
        self,
        language: str = "en-US"
    ):
        """Initialize speech recognizer + events."""
        self.speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY,
            region=SPEECH_REGION
        )
        self.speech_config.speech_recognition_language = language

        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config
        )

        self.recognizer.recognizing.connect(self._on_recognizing)
        self.recognizer.recognized.connect(self._on_recognized)
        self.recognizer.session_started.connect(self._on_session_started)
        self.recognizer.session_stopped.connect(self._on_session_stopped)
        self.recognizer.canceled.connect(self._on_canceled)
        self.recognized_speech = ""

    def _on_recognizing(self, evt):
        """Fires on partial recognition results."""
        logger.info(f"[INTERIM] {evt.result.text}")

    def _on_recognized(self, evt):
        """Fires on final recognition result."""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            self.recognized_speech += evt.result.text + " "
        else:
            logger.info("[NO MATCH] No speech recognized.")

    def _on_session_started(self, evt):
        logger.info("[SESSION STARTED]")
    
    def _on_session_stopped(self, evt):
        logger.info("[SESSION STOPPED]")

    def _on_canceled(self, evt):
        logger.error(f"[CANCELED] Reason: {evt.reason}")

    def start(self):
        """Asynchronously start continuous recognition."""
        logger.info("Starting continuous recognition...")
        start_future = self.recognizer.start_continuous_recognition_async()
        start_future.get()  
        logger.info("Continuous recognition started.")

    def stop(self):
        """Asynchronously stop continuous recognition."""
        logger.info("Stopping continuous recognition...")
        stop_future = self.recognizer.stop_continuous_recognition_async()
        stop_future.get()
        logger.info("Continuous recognition stopped.")



def add_audio_transcription(db_client: DBClientDep, session_id: str, user_id: str, transcription: str) -> None:
    """
    Add an audio transcription message to the database.
    """
    transcription_id = str(uuid.uuid4())
    recorded_at = datetime.datetime.now(datetime.timezone.utc)
    db_client.insert(
        query="INSERT INTO audio_transcripts (id, session_id, user_id, transcription_text, created_at) VALUES (:id, :session_id, :user_id, :transcription_text, :created_at)",
        values={"id": transcription_id, "session_id": session_id, "user_id": user_id, "transcription_text": transcription, "created_at": recorded_at}
    )