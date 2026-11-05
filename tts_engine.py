
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"

LANGUAGE_CODES = {
    "Telugu": "te-IN",
    "Hindi": "hi-IN",
    "English": "en-IN"
}

VOICE_NAMES = {
    "Telugu": "Shivani",
    "Hindi": "Shivani",
    "English": "Avinash"
}


def generate_speech(text, language="English", voice=None):
    api_key = os.getenv("GNANI_API_KEY")

    if not api_key:
        raise ValueError("GNANI_API_KEY is missing from .env")

    if not text or not text.strip():
        raise ValueError("Cannot generate speech from empty text")

    if language not in LANGUAGE_CODES:
        raise ValueError(f"Unsupported language: {language}")

    selected_voice = voice or VOICE_NAMES[language]

    payload = {
        "text": text.strip(),
        "voice": selected_voice,
        "model": "timbre-v3.0",
        "language": LANGUAGE_CODES[language],
        "audio_config": {
            "sample_rate": 48000,
            "encoding": "linear_pcm",
            "container": "wav"
        }
    }

    try:
        response = requests.post(
            TTS_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-Key-ID": api_key
            },
            json=payload,
            timeout=90
        )

        response.raise_for_status()

        if not response.content:
            raise RuntimeError("Gnani returned empty audio")

        return response.content

    except requests.RequestException as error:
        details = ""
        if error.response is not None:
            details = error.response.text[:500]

        raise RuntimeError(
            f"Gnani TTS failed: {error}. {details}"
        ) from error
