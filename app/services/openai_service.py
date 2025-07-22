from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(platform, model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return {
        "platform": platform,
        "model": model,
        "output": response.choices[0].message.content
    }
