import azure.cognitiveservices.speech as speechsdk
from app.utils.config import settings

SPEECH_KEY = settings.AZURE_SPEECH_KEY if hasattr(settings, "AZURE_SPEECH_KEY") else None
SPEECH_REGION = settings.AZURE_SPEECH_REGION if hasattr(settings, "AZURE_SPEECH_REGION") else None


def transcribe_mic(language: str = "en-US"):
    """
    Transcribe audio from the default microphone using Azure Speech-to-Text.
    Used for voice intake on CCC First Responder UI.
    """

    if not SPEECH_KEY or not SPEECH_REGION:
        return "Missing AZURE_SPEECH_KEY or AZURE_SPEECH_REGION in environment."

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, 
            region=SPEECH_REGION
        )
        speech_config.speech_recognition_language = language

        audio_config = speechsdk.AudioConfig(use_default_microphone=True)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text

        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "No speech detected."

        else:
            details = result.cancellation_details
            return f"Error: {details.reason} — {details.error_details}"

    except Exception as e:
        return f"Exception: {str(e)}"
