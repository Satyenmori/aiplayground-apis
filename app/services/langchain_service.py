# # langchain_service.py
# from langgraph.graph import StateGraph, END
# # from langgraph.prebuilt import ToolNode
# from .openai_service import ask_openai
# from .builders import build_post_prompt

# # Node: Generate post text
# def generate_text_post(state):
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

#     return {"posts": all_outputs}

# # Node: Generate image using the first successful post
# def generate_image_from_post(state):
#     posts = state.get("posts", [])
#     options = state.get("options", {})
#     image_nodes = []

#     # Check if image generation is requested
#     if options.get("generate image", "false").lower() != "true":
#         print("Skipping image generation as 'generate image' option is not true.")
#         return {"images": []}

#     # Find the first successful text post to use as an image prompt
#     image_prompt_text = None
#     for post in posts:
#         if post.get("output"):
#             image_prompt_text = post["output"]
#             break # Use the first successful post's content

#     if image_prompt_text:
#         print(f"Attempting to generate image with prompt: {image_prompt_text[:50]}...") # Print first 50 chars
#         image_response = ask_openai(
#             platform="openai", # Assuming DALL-E is always from OpenAI
#             model="dall-e", # Specifying the model if needed, though ask_openai handles it for images
#             messages=None,
#             generate_image=True,
#             image_prompt=image_prompt_text
#         )
#         image_nodes.append(image_response)
#     else:
#         print("No suitable text post found to generate an image from.")

#     return {"images": image_nodes}

# # LangGraph setup
# graph = StateGraph(dict)
# graph.add_node("generate_post", generate_text_post)
# graph.add_node("generate_image", generate_image_from_post)

# graph.set_entry_point("generate_post")
# graph.add_edge("generate_post", "generate_image")
# graph.set_finish_point("generate_image")

# # graph.set_finish_point(END)

# # Compile the graph
# flow = graph.compile()

# def run_generation_flow(payload):
#     result = flow.invoke(payload)
#     print(f"Flow result111111: {result}")
#     return result


# langchain_service.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import List, Dict, TypedDict, Union # Import for state definition
from .openai_service import ask_openai
from .builders import build_post_prompt

# 1. Define the State for your LangGraph
# This tells LangGraph what keys to expect in its state and their types.
class GraphState(TypedDict):
    input: str
    options: Dict
    platforms: Dict
    history: List[Dict]
    posts: List[Dict]  # This is crucial: to store the text posts
    images: List[Dict] # To store the image generation results

# Node: Generate post text
def generate_text_post(state: GraphState): # Add type hint for clarity
    input_text = state["input"]
    options = state.get("options", {})
    platforms = state.get("platforms", {})
    history = state.get("history", [])

    all_outputs = []

    for platform, models in platforms.items():
        for model in models:
            messages = build_post_prompt(input_text, options, history) # Build the messages for the AI
            response = ask_openai(platform, model, messages) # Ask OpenAI for text, image generation
            all_outputs.append(response)

    print(f"Generated text posts: {all_outputs}") # Debug print
    return {"posts": all_outputs} # Ensure this key matches the State definition

# Node: Generate image using the first successful post
def generate_image_from_post(state: GraphState): # Add type hint for clarity
    posts = state.get("posts", []) # Retrieve posts from the state
    options = state.get("options", {})
    image_nodes = []

    # Check if image generation is requested
    # The error message "Skipping image generation as 'generate image' option is not true."
    # strongly suggests that options.get("generate image") is NOT "true".
    # Let's ensure the string comparison is robust (case-insensitive and trim spaces if any).
    if str(options.get("generate image", "false")).strip().lower() != "true":
        print("Skipping image generation as 'generate image' option is not true (checked with .lower() and .strip()).")
        return {"images": []} # Return an empty list for images if skipped

    # Find the first successful text post to use as an image prompt
    image_prompt_text = None
    for post in posts:
        if post.get("output"): # Check if the 'output' key exists and has content
            image_prompt_text = post["output"]
            break # Use the first successful post's content

    if image_prompt_text:
        print(f"Attempting to generate image with prompt: {image_prompt_text[:100]}...") # Print first 100 chars
        image_response = ask_openai(
            platform="openai", # Assuming DALL-E is always from OpenAI
            model="dall-e",
            messages=None,
            generate_image=True,
            image_prompt=image_prompt_text
        )
        image_nodes.append(image_response)
    else:
        print("No suitable text post found in 'posts' to generate an image from.")

    print(f"Generated image results: {image_nodes}") # Debug print
    return {"images": image_nodes} # Ensure this key matches the State definition

# LangGraph setup
# Initialize the graph with the defined state
graph = StateGraph(GraphState)

graph.add_node("generate_post", generate_text_post)
graph.add_node("generate_image", generate_image_from_post)

graph.set_entry_point("generate_post")
graph.add_edge("generate_post", "generate_image")
graph.add_edge("generate_image", END)

# Compile the graph
flow = graph.compile()

def run_generation_flow(payload: Dict): # Add type hint
    result = flow.invoke(payload)
    print(f"Final LangGraph flow result (from run_generation_flow): {result}") # Final debug print
    return result