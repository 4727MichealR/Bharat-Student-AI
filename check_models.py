
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    models = client.models.list()

    print("\nAVAILABLE GROQ MODELS:\n")

    for model in sorted(models.data, key=lambda m: m.id):
        print(model.id)

except Exception as error:
    print("Error:", error)
