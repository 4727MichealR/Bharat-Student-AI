
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GNANI_API_KEY = os.getenv("GNANI_API_KEY")
STT_URL = "https://api.vachana.ai/stt/v3"


def transcribe_audio(audio_bytes):
    if not GNANI_API_KEY:
        raise ValueError("GNANI_API_KEY is missing from .env")

    headers = {
        "X-API-Key-ID": GNANI_API_KEY
    }

    files = {
        "audio_file": (
            "recording.wav",
            audio_bytes,
            "audio/wav"
        )
    }

    data = {
        "model": "prisma-v3.0",
        "language_code": "indic-auto",
        "format": "transcribe"
    }

    try:
        response = requests.post(
            STT_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=60
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Gnani API request failed: {error}"
        ) from error
