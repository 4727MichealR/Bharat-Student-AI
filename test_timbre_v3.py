
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GNANI_API_KEY")

if not api_key:
    raise ValueError("GNANI_API_KEY is missing")

url = "https://api.vachana.ai/api/v1/tts/inference"

headers = {
    "Content-Type": "application/json",
    "X-API-Key-ID": api_key
}

payload = {
    "text": "నమస్కారం! నేను భారత్ స్టూడెంట్ ఏఐ.",
    "voice": "Shivani",
    "model": "timbre-v3.0",
    "language": "te-IN",
    "audio_config": {
        "sample_rate": 48000,
        "encoding": "linear_pcm",
        "container": "wav"
    }
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code == 200:
        with open("telugu_test.wav", "wb") as file:
            file.write(response.content)

        print("SUCCESS: Telugu audio generated!")
        print("File: telugu_test.wav")

    else:
        print("API Error:", response.status_code)
        print(response.text[:1000])

except requests.RequestException as error:
    print("Connection error:", error)
