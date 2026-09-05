import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GENAI_API_KEY")
)

print("\nModels available for your API key:\n")

for model in client.models.list():
    if "generateContent" in model.supported_actions:
        print(model.name)