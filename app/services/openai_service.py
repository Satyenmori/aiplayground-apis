# from openai import OpenAI
# import os

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def ask_openai(platform, model, messages, generate_image=False, image_prompt=None):
#     if generate_image:
#         try:
#             # ✅ Generate image using OpenAI DALL·E endpoint
#             response = client.images.generate(  # use `.generate` not `.create` if using latest SDK
#                 prompt=image_prompt,
#                 n=1,
#                 size="1024x1024"
#             )
#             image_url = response.data[0].url
#             print("✅ Image URL:", image_url)
#             return {
#                 "platform": platform,
#                 "model": "dall-e",  # This is just for tracking
#                 "image_url": image_url
#             }
#         except Exception as e:
#             print("❌ Image generation error:", e)
#             return {
#                 "platform": platform,
#                 "model": "dall-e",
#                 "error": str(e)
#             }

#     # 📝 Text generation using chat model
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=messages
#         )
#         content = response.choices[0].message.content
#         print("📝 image response:", content)
#         return {
#             "platform": platform,
#             "model": model,
#             "output": content
#         }
#     except Exception as e:
#         print("❌ Text generation error:", e)
#         return {
#             "platform": platform,
#             "model": model,
#             "error": str(e)
#         }


# openai_service.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(platform, model, messages, generate_image=False, image_prompt=None, image_quality="standard"):
    if generate_image:
        try:
            # ✅ Generate image using OpenAI DALL·E endpoint
            response = client.images.generate(
                prompt=image_prompt,
                n=1,
                size="1024x1024",
                model=model, # e.g., 'dall-e-3' or 'gpt-image-1'
                quality=image_quality # Pass the quality parameter
            )
            image_url = response.data[0].url
            # print("✅ Image URL:", image_url)
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

    # 📝 Text generation using chat model
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        content = response.choices[0].message.content
        # print("📝 Text response:", content) # Changed print for clarity
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