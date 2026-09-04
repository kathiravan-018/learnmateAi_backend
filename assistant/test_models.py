import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GENAI_API_KEY")
)

models = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-3.5-flash-lite",
]

for model in models:

    print("\n" + "=" * 60)
    print(f"Testing: {model}")
    print("=" * 60)

    try:
        response = client.models.generate_content(
            model=model,
            contents="Say hello in one short sentence."
        )

        print("✅ SUCCESS")
        print("Response:", response.text)

    except Exception as e:

        print("❌ FAILED")
        print("Error:", str(e))