import os
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get("GEMINI_API_KEY")
print("Key loaded:", "YES" if key else "NO")
print("Key (first 20 chars):", key[:20] if key else "NONE")


import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
r = client.models.generate_content(
    model="gemini-pro",
    contents="Say hello in one short sentence.",
)
print(r.text)