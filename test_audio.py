import requests
import json

AUDIO_FILE_PATH = "/Users/navikamaglani/Downloads/briskaudioclip_1.wav"
URL = "http://127.0.0.1:8000/agent/transcribe"   # Update if your FastAPI runs on another port

def test_transcription():
    print("=== AUDIO TRANSCRIPTION TEST ===")
    print("Uploading file to backend...\n")

    try:
        with open(AUDIO_FILE_PATH, "rb") as f:
            files = {"file": ("test.wav", f, "audio/wav")}
            response = requests.post(URL, files=files)

        print("STATUS:", response.status_code)

        try:
            data = response.json()
            print(json.dumps(data, indent=4))
        except Exception:
            print("Could not decode JSON")
            print("RAW RESPONSE:", response.text)

    except Exception as e:
        print("Error during request:", str(e))


if __name__ == "__main__":
    test_transcription()
