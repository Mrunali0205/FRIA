import azure.cognitiveservices.speech as speechsdk
from src.app.utils.config import settings

SPEECH_KEY = settings.AZURE_SPEECH_KEY if hasattr(settings, "AZURE_SPEECH_KEY") else None
SPEECH_REGION = settings.AZURE_SPEECH_REGION if hasattr(settings, "AZURE_SPEECH_REGION") else None


def transcribe_mic(language: str = "en-US"):
    if not SPEECH_KEY or not SPEECH_REGION:
        return "Missing AZURE_SPEECH_KEY or AZURE_SPEECH_REGION in environment."

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY,
            region=SPEECH_REGION
        )
        speech_config.speech_recognition_language = language

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=speechsdk.AudioConfig(use_default_microphone=True)
        )
        result = recognizer.recognize_once()
        return result.text
    except Exception as e:
        return f"Exception: {str(e)}"


def transcribe_audio_file(file_path: str, language: str = "en-US"):
    if not SPEECH_KEY or not SPEECH_REGION:
        return "Missing AZURE_SPEECH_KEY or AZURE_SPEECH_REGION."

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, 
            region=SPEECH_REGION
        )
        speech_config.speech_recognition_language = language

        audio_input = speechsdk.AudioConfig(filename=file_path)

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_input
        )
        result = recognizer.recognize_once()
        return result.text
    except Exception as e:
        return f"Exception: {str(e)}"