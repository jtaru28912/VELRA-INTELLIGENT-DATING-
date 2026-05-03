import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
print(f"Key exists: {bool(key)}")
if key:
    print(f"Key prefix: {key[:10]}")
    print(f"Key length: {len(key)}")
