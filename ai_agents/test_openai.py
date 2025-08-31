import os
from openai import OpenAI
from dotenv import load_dotenv

# Load keys from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# New API call style
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Hello OpenAI, is setup working?"}
    ]
)

print("✅ OpenAI says:", resp.choices[0].message.content)
