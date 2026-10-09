import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"✓ API Key loaded: {api_key is not None}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash')
        response = model.generate_content("Say 'API working!'")
        print(f"✓ Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("✗ No API key in .env!")