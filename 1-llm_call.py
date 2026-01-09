from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Set Parameters
model_id = "gemini-3-flash-preview"

# Initialize Google Generative AI client
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or "your_gemini_api_key_here" in api_key:
    # Explicitly warn the user if they haven't set the key
    print(f"\n❌ ERROR: Invalid API Key. Found: '{api_key}'")
    print("Please open the .env file and replace 'your_gemini_api_key_here' with your actual API key.")
    print("Don't forget to SAVE the file (Ctrl+S)!")
    print("You can get a free key from: https://aistudio.google.com/app/apikey\n")
    exit(1)

client = genai.Client(api_key=api_key)

# Query to send to Gemini
query = input("👤 Enter your query: ")

# Make the API call
try:
    print("🤖 System call")
    response = client.models.generate_content(
        model=model_id,
        contents=query
    )
    
    # Extract and print the response
    output = response.text
    print(f"👤 Query: {query}")
    print(f"\nResponse:\n{output}")
    
except Exception as e:
    print(f"Error calling Gemini: {e}")
