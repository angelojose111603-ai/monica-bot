import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": "Hola"}],
        max_tokens=10,
    )
    print("Groq OK:", completion.choices[0].message.content)
except Exception as e:
    print("Groq Error:", str(e))
