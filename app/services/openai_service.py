# from openai import OpenAI
# import os

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def ask_openai(platform, model, messages):
#     response = client.chat.completions.create(
#         model=model,
#         messages=messages
#     )
#     return {
#         "platform": platform,
#         "model": model,
#         "output": response.choices[0].message.content
#     }

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from openai import OpenAI
import os

# LangChain LLM for text
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")

# Raw OpenAI client for image
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(prompt, tone="professional", length="short"):
    system_msg = (
        f"You are a professional marketing copywriter. "
        f"Create a {length}, {tone}-tone post based on the given idea."
    )
    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=prompt)
    ]
    response = llm(messages)
    return response.content

def generate_image(prompt):
    response = client.images.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url
