# from flask import request, jsonify
# from app.services.langchain_service import run_generation_flow

# def handle_task(default_platform, prompt_builder):
#     data = request.get_json()
#     print(f"Received data: {data}")

#     try:
#         langgraph_result = run_generation_flow(data)
#         print(f"LangGraph flow result: {langgraph_result}")

#         # Initialize the response dictionary with platform keys
#         response_data = {p: [] for p in data.get("platforms", {}).keys()}
#         if not response_data and default_platform:
#              response_data = {default_platform: []}

#         # Get the generated image(s) - assuming one for DALL-E (OpenAI)
#         openai_image = None
#         for img in langgraph_result.get("images", []):
#             if img.get("platform") == "openai" and img.get("image_url"):
#                 openai_image = img
#                 break # Take the first OpenAI image found

#         # Populate with text posts and potentially associate the image
#         for post in langgraph_result.get("posts", []):
#             platform = post.get("platform")
#             if platform in response_data:
#                 post_entry = {
#                     "model": post.get("model"),
#                     "output": post.get("output")
#                 }
#                 # If this is an OpenAI text post AND an OpenAI image was generated,
#                 # you can choose to stick the image URL here.
#                 if platform == "openai" and openai_image:
#                     post_entry["image_url"] = openai_image["image_url"] # Add the image URL directly

#                 response_data[platform].append(post_entry)

#         # If you still want the image as a separate entry for OpenAI, you can add it
#         # You'll need to decide if you want duplicates or how to prioritize
#         # For your desired format, it seems you want it *within* the platform's list
#         # alongside the text outputs.

#         # If there are other platforms that might generate images in the future,
#         # you'd extend this logic. For now, assuming DALL-E is OpenAI only.
#         # If the image should ONLY appear as a standalone entry and not within the text posts,
#         # then you'd add it here if it hasn't been added with a text post.
#         # Given your desired format, adding it to the OpenAI list is the way to go.

#         # What you've printed for the desired response:
#         # "openai": [
#         # {"model": "gpt-4.1", "output": "...."},
#         # {"model": "gpt-4.0", "output": "...."}
#         # ],
#         # ... and then implicitly, an image entry for openai within the same list

#         # To match the exact example, where images are also in the platform list:
#         if openai_image and "openai" in response_data:
#             # Check if image is already added (if you did the above injection)
#             # If not, add it as a separate dictionary in the list
#             # We are currently injecting it into *each* text post, so adding it separately
#             # would cause duplication if you want distinct entries.
#             # If you want distinct entries, you should NOT inject it into text posts above.
#             # Let's assume you want it once per platform, alongside other outputs.
#             # So, if image was generated, ensure it's in the OpenAI list.
#             image_already_added = False
#             for item in response_data["openai"]:
#                 if "image_url" in item:
#                     image_already_added = True
#                     break
#             if not image_already_added:
#                  response_data["openai"].append({
#                     "model": openai_image.get("model"),
#                     "image_url": openai_image.get("image_url")
#                  })


#         return jsonify({"response": response_data})

#     except Exception as e:
#         print(f"Error running LangGraph flow: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

from flask import request, jsonify
from app.services.langchain_service import run_generation_flow

def handle_task(default_platform, prompt_builder): # prompt_builder is now mostly internal to LangGraph
    data = request.get_json()
    print(f"Received data: {data}")

    try:
        langgraph_result = run_generation_flow(data)
        print(f"Final LangGraph flow result: {langgraph_result}") # This is crucial for debugging

        # Initialize the response dictionary with platform keys
        response_data = {p: [] for p in data.get("platforms", {}).keys()}
        if not response_data and default_platform:
             response_data = {default_platform: []}

        # Retrieve the single generated image (if any)
        generated_image_info = langgraph_result.get("generated_image", {})
        image_url = generated_image_info.get("image_url")
        image_platform = generated_image_info.get("platform")
        image_model = generated_image_info.get("model")

        # Populate with text posts
        for post in langgraph_result.get("posts", []): # Use 'posts' directly
            platform = post.get("platform")
            if platform in response_data:
                post_entry = {
                    "model": post.get("model"),
                    "output": post.get("output")
                    # No caption_hashtags here unless you add another node for it later
                }
                # If you want to include the image URL with *each* text post that's for that platform
                # This makes sense since the image was generated based on the overall content.
                if image_url and platform == image_platform: # Check if image exists and belongs to this platform
                    post_entry["image_url"] = image_url

                response_data[platform].append(post_entry)

        # Add the image itself as a separate entry within the relevant platform's list
        # This ensures it explicitly appears if it wasn't duplicated into each post.
        if image_url and image_platform and image_platform in response_data:
            # Only add if not already part of an existing post object (if you chose that logic above)
            # Or if you want it as a distinct entry regardless
            image_added_as_distinct = False
            for item in response_data[image_platform]:
                if "image_url" in item and item.get("model") == image_model:
                    image_added_as_distinct = True
                    break
            if not image_added_as_distinct: # Avoid adding twice if already injected into each post
                response_data[image_platform].append({
                    "model": image_model,
                    "image_url": image_url,
                    "generated_prompt": generated_image_info.get("generated_prompt") # Include the prompt used for image
                })


        return jsonify({"response": response_data})

    except Exception as e:
        print(f"Error running LangGraph flow: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500