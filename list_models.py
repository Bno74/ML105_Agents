from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing available models:")
with open("models.txt", "w") as f:
    for m in client.models.list(config={"page_size": 100}):
        f.write(f"{m.name}\n")
        print(f"Computed: {m.name}")
