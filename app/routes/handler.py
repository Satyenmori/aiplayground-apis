from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.generationflow import run_generation_flow

# Shared handler function
# async def handle_task(request: Request, default_platform: str):
#     try:
#         data = await request.json()
#         print(f"Received data: {data}")

#         langgraph_result = run_generation_flow(data)
#         print(f"Final LangGraph flow result: {langgraph_result}")

#         # Initialize the response dictionary with platform keys
#         response_data = {p: [] for p in data.get("platforms", {}).keys()}
#         if not response_data and default_platform:
#             response_data = {default_platform: []}

#         # Retrieve the single generated image (if any)
#         generated_image_info = langgraph_result.get("generated_image", {})
#         image_url = generated_image_info.get("image_url")
#         image_platform = generated_image_info.get("platform")
#         image_model = generated_image_info.get("model")

#         # Populate with text posts
#         for post in langgraph_result.get("posts", []):
#             platform = post.get("platform")
#             if platform in response_data:
#                 post_entry = {
#                     "model": post.get("model"),
#                     "output": post.get("output"),
#                 }
#                 if image_url and platform == image_platform:
#                     post_entry["image_url"] = image_url

#                 response_data[platform].append(post_entry)

#         # Add image as distinct entry if needed
#         if image_url and image_platform and image_platform in response_data:
#             image_added_as_distinct = any(
#                 "image_url" in item and item.get("model") == image_model
#                 for item in response_data[image_platform]
#             )
#             if not image_added_as_distinct:
#                 response_data[image_platform].append({
#                     "model": image_model,
#                     "image_url": image_url,
#                     "generated_prompt": generated_image_info.get("generated_prompt"),
#                 })

#         return JSONResponse(content={"response": response_data})

#     except Exception as e:
#         print(f"Error running LangGraph flow: {e}")
#         import traceback
#         traceback.print_exc()
#         return JSONResponse(content={"error": str(e)}, status_code=500)
async def handle_task(request: Request, default_platform: str):
    try:
        data = await request.json()
        langgraph_result = run_generation_flow(data)

        # 1. prepare platform buckets
        response_data = {p: [] for p in data.get("platforms", {}).keys()}
        if not response_data and default_platform:
            response_data = {default_platform: []}

        # 2. add text posts (never include an image_url here)
        for post in langgraph_result.get("posts", []):
            platform = post.get("platform")
            if platform in response_data:
                response_data[platform].append({
                    "model": post.get("model"),
                    "output": post.get("output"),
                })

        # 3. add each generated image as a standalone entry
        def push_image(key: str):
            info = langgraph_result.get(key, {})
            url  = info.get("image_url")
            if not url:
                return
            platform = info.get("platform")
            if platform in response_data:
                response_data[platform].append({
                    "model": info.get("model"),
                    "image_url": url,
                    "generated_prompt": info.get("generated_prompt"),
                })

        push_image("generated_image")            # standard
        push_image("generated_image_realistic")  # realistic
        
        return JSONResponse(content={"response": response_data})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
# Individual route functions
async def generate_post(request: Request):
    return await handle_task(request, "openai")

async def generate_image(request: Request):
    return await handle_task(request, "openai")

async def generate_caption(request: Request):
    return await handle_task(request, "openai")
