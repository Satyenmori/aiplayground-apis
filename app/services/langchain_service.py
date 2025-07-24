# from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolNode
# from typing import List, Dict, TypedDict, Union # Import for state definition
# from .openai_service import ask_openai
# from .builders import build_post_prompt

# # 1. Define the State for your LangGraph
# # This tells LangGraph what keys to expect in its state and their types.
# class GraphState(TypedDict):
#     input: str
#     options: Dict
#     platforms: Dict
#     history: List[Dict]
#     posts: List[Dict]  # This is crucial: to store the text posts
#     images: List[Dict] # To store the image generation results

# # Node: Generate post text
# def generate_text_post(state: GraphState): # Add type hint for clarity
#     input_text = state["input"]
#     options = state.get("options", {})
#     platforms = state.get("platforms", {})
#     history = state.get("history", [])

#     all_outputs = []

#     for platform, models in platforms.items():
#         for model in models:
#             messages = build_post_prompt(input_text, options, history) # Build the messages for the AI
#             response = ask_openai(platform, model, messages) # Ask OpenAI for text, image generation
#             all_outputs.append(response)

#     print(f"Generated text posts: {all_outputs}") # Debug print
#     return {"posts": all_outputs} # Ensure this key matches the State definition

# # Node: Generate image using the first successful post
# def generate_image_from_post(state: GraphState): # Add type hint for clarity
#     posts = state.get("posts", []) # Retrieve posts from the state
#     print(f"Posts received for image generation: {posts}") # Debug print
#     options = state.get("options", {})
#     image_nodes = []

#     # Check if image generation is requested
#     # The error message "Skipping image generation as 'generate image' option is not true."
#     # strongly suggests that options.get("generate image") is NOT "true".
#     # Let's ensure the string comparison is robust (case-insensitive and trim spaces if any).
#     if str(options.get("generate image", "false")).strip().lower() != "true":
#         print("Skipping image generation as 'generate image' option is not true (checked with .lower() and .strip()).")
#         return {"images": []} # Return an empty list for images if skipped

#     # Find the first successful text post to use as an image prompt
#     image_prompt_text = None
#     for post in posts:
#         if post.get("output"): # Check if the 'output' key exists and has content
#             image_prompt_text = post["output"]
#             break # Use the first successful post's content

#     if image_prompt_text:
#         print(f"Attempting to generate image with prompt: {image_prompt_text[:400]}...") # Print first 100 chars
#         image_response = ask_openai(
#             platform="openai", # Assuming DALL-E is always from OpenAI
#             model="dall-e",
#             messages=None,
#             generate_image=True,
#             image_prompt=image_prompt_text
#         )
#         image_nodes.append(image_response)
#     else:
#         print("No suitable text post found in 'posts' to generate an image from.")

#     print(f"Generated image results: {image_nodes}") # Debug print
#     return {"images": image_nodes} # Ensure this key matches the State definition

# # LangGraph setup
# # Initialize the graph with the defined state
# graph = StateGraph(GraphState)

# graph.add_node("generate_post", generate_text_post)
# graph.add_node("generate_image", generate_image_from_post)

# graph.set_entry_point("generate_post")
# graph.add_edge("generate_post", "generate_image")
# graph.add_edge("generate_image", END)

# # Compile the graph
# flow = graph.compile()

# def run_generation_flow(payload: Dict): # Add type hint
#     result = flow.invoke(payload)
#     print(f"Final LangGraph flow result (from run_generation_flow): {result}") # Final debug print
#     return result

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import List, Dict, TypedDict, Union
from .openai_service import ask_openai
from .builders import build_post_prompt, build_image_prompt_creation_messages # Import the new builder

# 1. Define the State for your LangGraph
class GraphState(TypedDict):
    input: str # Original user input
    options: Dict
    platforms: Dict
    history: List[Dict]
    posts: List[Dict]  # To store the main text posts
    image_prompt_text: str # To store the LLM-generated image prompt text
    generated_image: Dict # To store the single image generation result


# --- Node: Generate Post Text (Entry Point) ---
def generate_text_post(state: GraphState):
    input_text = state["input"]
    options = state.get("options", {})
    platforms = state.get("platforms", {})
    history = state.get("history", [])

    all_outputs = []

    for platform, models in platforms.items():
        for model in models:
            messages = build_post_prompt(input_text, options, history) # Build messages for the AI
            response = ask_openai(platform, model, messages) # Ask OpenAI for text generation
            all_outputs.append(response)

    # print(f"Generated text posts: {all_outputs}")
    return {"posts": all_outputs}

# --- New Node: Generate Image Prompt from Post + Input ---
def generate_image_prompt(state: GraphState):
    options = state.get("options", {})
    user_input = state["input"]
    posts = state.get("posts", [])

    # Only generate image prompt if image generation is requested
    if str(options.get("generate_image", "false")).strip().lower() != "true":
        # print("Skipping image prompt generation as 'generate image' option is not true.")
        return {"image_prompt_text": None}

    # Take the first successful text post to combine with original input
    image_prompt_base_text = None
    if posts:
        for post in posts:
            if post.get("output"):
                image_prompt_base_text = post["output"]
                break
    
    if not image_prompt_base_text:
        # print("No valid text post found to generate an image prompt from. Using original input only.")
        image_prompt_base_text = user_input # Fallback to original input if no post generated

    # Use an LLM to refine the image prompt
    # You might want to use a specific model for this (e.g., 'gpt-4o-mini' or 'gpt-3.5-turbo')
    # For now, let's use the first model from the 'platforms' list if available, or a default.
    preferred_platform = next(iter(state.get("platforms", {}).keys()), "openai")
    preferred_model_list = state.get("platforms", {}).get(preferred_platform, ["gpt-3.5-turbo"])
    llm_model_for_prompt = preferred_model_list[0] if preferred_model_list else "gpt-3.5-turbo"

    messages_for_image_prompt = build_image_prompt_creation_messages(user_input, image_prompt_base_text)
    
    image_prompt_llm_response = ask_openai(
        platform=preferred_platform,
        model=llm_model_for_prompt,
        messages=messages_for_image_prompt
    )

    generated_image_prompt = image_prompt_llm_response.get("output")
    if not generated_image_prompt:
        # print("Failed to generate image prompt from LLM. Falling back to original input.")
        generated_image_prompt = user_input # Critical fallback

    # print(f"LLM-generated image prompt: {generated_image_prompt[:100]}...")
    return {"image_prompt_text": generated_image_prompt}

# --- Node: Generate Image using the LLM-generated prompt ---
def generate_image(state: GraphState):
    options = state.get("options", {})
    image_prompt_text = state.get("image_prompt_text") # Get the LLM-generated prompt
    
    if not image_prompt_text:
        # print("No image prompt text available. Skipping image generation.")
        return {"generated_image": {}}

    # Define image generation parameters
    image_model_to_use = "dall-e-3" # Or "gpt-image-1" if you have access and prefer
    image_size = "1024x1024"
    image_quality = "hd" # Can be "standard" or "hd"
    num_images = 1 # DALL-E 3 only supports n=1

    # print(f"Attempting to generate image with LLM-refined prompt: {image_prompt_text[:400]}...")
    image_response = ask_openai(
        platform="openai",
        model=image_model_to_use,
        messages=None,
        generate_image=True,
        image_prompt=image_prompt_text,
        image_quality=image_quality
    )

    # print(f"Generated image result: {image_response}")
    return {"generated_image": image_response}


# LangGraph setup
graph = StateGraph(GraphState)

# Define the nodes
graph.add_node("generate_post", generate_text_post)
graph.add_node("generate_image_prompt", generate_image_prompt) # New node
graph.add_node("generate_image", generate_image) # Renamed from generate_image_from_post

# Define the sequence
graph.set_entry_point("generate_post") # Start by generating text posts
graph.add_edge("generate_post", "generate_image_prompt") # Then generate the image prompt
graph.add_edge("generate_image_prompt", "generate_image") # Then use that prompt to generate the image
graph.add_edge("generate_image", END) # Finally, end the graph

# Compile the graph
flow = graph.compile()

def run_generation_flow(payload: Dict):
    result = flow.invoke(payload)
    # print(f"Final LangGraph flow result (from run_generation_flow): {result}")
    return result