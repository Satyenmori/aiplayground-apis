# from openai import OpenAI
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))    
# print(f"OpenAI client initialized with API key: {os.getenv('OPENAI_API_KEY') is not None}")

# def ask_openai(platform, model, messages, generate_image=False, image_prompt=None, image_quality="standard"):
#     if generate_image:
#         try:
#             # ✅ Generate image using OpenAI DALL·E endpoint
#             response = client.images.generate(
#                 prompt=image_prompt,
#                 n=1,
#                 size="1024x1024",
#                 model=model, # e.g., 'dall-e-3' or 'gpt-image-1'
#                 quality=image_quality # Pass the quality parameter
#             )
#             image_url = response.data[0].url
#             # print("✅ Image URL:", image_url)
#             return {
#                 "platform": platform,
#                 "model": model,
#                 "image_url": image_url,
#                 "generated_prompt": image_prompt # Store the prompt that generated the image
#             }
#         except Exception as e:
#             # print(f"❌ Image generation error for prompt '{image_prompt}': {e}")
#             return {
#                 "platform": platform,
#                 "model": model,
#                 "error": str(e)
#             }

#     # 📝 Text generation using chat model
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=messages
#         )
#         content = response.choices[0].message.content
#         # print("📝 Text response:", content) # Changed print for clarity
#         return {
#             "platform": platform,
#             "model": model,
#             "output": content
#         }
#     except Exception as e:
#         # print("❌ Text generation error:", e)
#         return {
#             "platform": platform,
#             "model": model,
#             "error": str(e)
#         }


from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# print(f"OpenAI client initialized with API key: {os.getenv('OPENAI_API_KEY') is not None}")

# --- UPDATED FUNCTION SIGNATURE ---
def ask_openai(platform, model, messages, generate_image=False, image_prompt=None, image_quality="standard", image_size="1024x1024", n=1):
    """
    Generic function to call OpenAI for either text or image generation.
    Image parameters (quality, size, n) are now passed in.
    """
    if generate_image:
        try:
            # ✅ Generate image using parameters passed from the LangGraph node
            response = client.images.generate(
                prompt=image_prompt,
                model=model,          # e.g., 'dall-e-3'
                n=n,                  # <-- CHANGED: Use the 'n' parameter
                size=image_size,      # <-- CHANGED: Use the 'image_size' parameter
                quality=image_quality # Use the 'image_quality' parameter
            )
            image_url = response.data[0].url
            return {
                "platform": platform,
                "model": model,
                "image_url": image_url,
                "generated_prompt": image_prompt # Store the prompt that generated the image
            }
        except Exception as e:
            # print(f"❌ Image generation error for prompt '{image_prompt}': {e}")
            return {
                "platform": platform,
                "model": model,
                "error": str(e)
            }

    # 📝 Text generation using chat model (no changes here)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        content = response.choices[0].message.content
        return {
            "platform": platform,
            "model": model,
            "output": content
        }
    except Exception as e:
        # print("❌ Text generation error:", e)
        return {
            "platform": platform,
            "model": model,
            "error": str(e)
        }