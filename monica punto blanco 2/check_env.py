import os
from dotenv import load_dotenv

with open(".env", "rb") as f:
    content = f.read()
    print(f"Bytes en .env: {content}")

load_dotenv()
key = os.getenv("GROQ_API_KEY")
if key:
    print(f"Key loaded: '{key}'")
    print(f"Length: {len(key)}")
    print(f"Key bytes: {key.encode('utf-8')}")
else:
    print("No key found")
