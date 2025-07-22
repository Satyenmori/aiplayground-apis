# from flask import request, jsonify
# # from app.utils import run_parallel_tasks # You might not need this for the LangGraph flow
# # from app.services.openai_service import ask_openai # You won't directly call this anymore for the main flow

# # Import your LangChain service
# from app.services.langchain_service import run_generation_flow # Assuming the path is app/services/langchain_service.py

# # You might still need create_task and run_parallel_tasks if you want to support
# # *other* types of direct, non-LangGraph calls in the future, but for the
# # "generate post and image" flow, you'll use run_generation_flow.


# def handle_task(default_platform, prompt_builder): # prompt_builder might become less relevant if LangGraph handles prompt construction
#     data = request.get_json()
#     print(f"Received data: {data}")

#     # The input payload for run_generation_flow should directly match what flow.invoke expects.
#     # It seems your current data structure already aligns well with what run_generation_flow expects:
#     # {
#     #   "platforms": {"openai": ["gpt-4", "gpt-3.5-turbo"]},
#     #   "input": "benefits of meditation.",
#     #   "options": {"generate image": "true", "tone": "professional", "length": "short"},
#     #   "history": []
#     # }

#     try:
#         # Call the LangGraph flow directly with the entire payload
#         result = run_generation_flow(data)
#         print(f"LangGraph flow result: {result}")

#         # The 'result' from LangGraph will already be structured with 'posts' and 'images'
#         # You can then format this result as needed for your API response.
#         # For simplicity, let's just return the result from LangGraph directly for now,
#         # or structure it to match your desired API output.

#         # Example of structuring the response based on the LangGraph output
#         response_data = {
#             "text_posts": result.get("posts", []),
#             "generated_images": result.get("images", [])
#         }

#         return jsonify({"response": response_data})

#     except Exception as e:
#         print(f"Error running LangGraph flow: {e}")
#         return jsonify({"error": str(e)}), 500


# from flask import request, jsonify
# from app.services.langchain_service import run_generation_flow # Import your LangChain service

# # You might still need create_task and run_parallel_tasks if you want to support
# # *other* types of direct, non-LangGraph calls in the future, but for the
# # "generate post and image" flow, you'll use run_generation_flow.


# def handle_task(default_platform, prompt_builder): # prompt_builder is likely not needed now as LangGraph handles it
#     data = request.get_json()
#     print(f"Received data: {data}")

#     try:
#         # Call the LangGraph flow directly with the entire payload
#         langgraph_result = run_generation_flow(data)
#         print(f"LangGraph flow result: {langgraph_result}")

#         # Initialize the response dictionary with platform keys
#         # We need to get all platforms from the initial request data
#         response_data = {p: [] for p in data.get("platforms", {}).keys()}
#         if not response_data and default_platform: # Handle case where platforms might not be explicitly given but default exists
#              response_data = {default_platform: []}

#         # Populate with text posts
#         for post in langgraph_result.get("posts", []):
#             platform = post.get("platform")
#             if platform in response_data:
#                 # Remove the 'platform' key if it's redundant at this level
#                 post_data = {k: v for k, v in post.items() if k != 'platform'}
#                 response_data[platform].append(post_data)

#         # Populate with generated images
#         # Images are typically platform-specific (e.g., DALL-E is OpenAI)
#         for image in langgraph_result.get("images", []):
#             platform = image.get("platform")
#             if platform in response_data:
#                 # Remove 'platform' key, and rename 'image_url' to 'output' if desired for consistency,
#                 # or keep it as 'image_url' to distinguish. Let's keep it as 'image_url' for clarity.
#                 image_data = {k: v for k, v in image.items() if k != 'platform'}
#                 response_data[platform].append(image_data)

#         return jsonify({"response": response_data})

#     except Exception as e:
#         print(f"Error running LangGraph flow: {e}")
#         import traceback
#         traceback.print_exc() # Print full traceback for better debugging
#         return jsonify({"error": str(e)}), 500



from flask import request, jsonify
from app.services.langchain_service import run_generation_flow

def handle_task(default_platform, prompt_builder):
    data = request.get_json()
    print(f"Received data: {data}")

    try:
        langgraph_result = run_generation_flow(data)
        print(f"LangGraph flow result: {langgraph_result}")

        # Initialize the response dictionary with platform keys
        response_data = {p: [] for p in data.get("platforms", {}).keys()}
        if not response_data and default_platform:
             response_data = {default_platform: []}

        # Get the generated image(s) - assuming one for DALL-E (OpenAI)
        openai_image = None
        for img in langgraph_result.get("images", []):
            if img.get("platform") == "openai" and img.get("image_url"):
                openai_image = img
                break # Take the first OpenAI image found

        # Populate with text posts and potentially associate the image
        for post in langgraph_result.get("posts", []):
            platform = post.get("platform")
            if platform in response_data:
                post_entry = {
                    "model": post.get("model"),
                    "output": post.get("output")
                }
                # If this is an OpenAI text post AND an OpenAI image was generated,
                # you can choose to stick the image URL here.
                if platform == "openai" and openai_image:
                    post_entry["image_url"] = openai_image["image_url"] # Add the image URL directly

                response_data[platform].append(post_entry)

        # If you still want the image as a separate entry for OpenAI, you can add it
        # You'll need to decide if you want duplicates or how to prioritize
        # For your desired format, it seems you want it *within* the platform's list
        # alongside the text outputs.

        # If there are other platforms that might generate images in the future,
        # you'd extend this logic. For now, assuming DALL-E is OpenAI only.
        # If the image should ONLY appear as a standalone entry and not within the text posts,
        # then you'd add it here if it hasn't been added with a text post.
        # Given your desired format, adding it to the OpenAI list is the way to go.

        # What you've printed for the desired response:
        # "openai": [
        # {"model": "gpt-4.1", "output": "...."},
        # {"model": "gpt-4.0", "output": "...."}
        # ],
        # ... and then implicitly, an image entry for openai within the same list

        # To match the exact example, where images are also in the platform list:
        if openai_image and "openai" in response_data:
            # Check if image is already added (if you did the above injection)
            # If not, add it as a separate dictionary in the list
            # We are currently injecting it into *each* text post, so adding it separately
            # would cause duplication if you want distinct entries.
            # If you want distinct entries, you should NOT inject it into text posts above.
            # Let's assume you want it once per platform, alongside other outputs.
            # So, if image was generated, ensure it's in the OpenAI list.
            image_already_added = False
            for item in response_data["openai"]:
                if "image_url" in item:
                    image_already_added = True
                    break
            if not image_already_added:
                 response_data["openai"].append({
                    "model": openai_image.get("model"),
                    "image_url": openai_image.get("image_url")
                 })


        return jsonify({"response": response_data})

    except Exception as e:
        print(f"Error running LangGraph flow: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500