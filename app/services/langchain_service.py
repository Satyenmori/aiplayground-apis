from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import List, Dict, TypedDict, Union
from .openai_service import ask_openai
from .builders import build_post_prompt, build_image_prompt_creation_messages # Import the new builder


class GraphState(TypedDict):
    input: str # Original user input
    options: Dict
    platforms: Dict
    history: List[Dict]
    posts: List[Dict]  # To store the main text posts
    image_prompt_text: str # To store the LLM-generated image prompt text
    image_prompt_text_realistic: str     # ← already existed
    generated_image: Dict            # To store the single image generation result
    generated_image_realistic: Dict      # ← ADD THIS


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

def generate_image_prompt_realistic(state: GraphState):
    """
    Produces a short, highly-realistic image prompt (<100 words).
    """
    options = state.get("options", {})
    user_input = state["input"]
    posts = state.get("posts", [])

    if str(options.get("generate_image", "false")).strip().lower() != "true":
        return {"image_prompt_text_realistic": None}

    # Pick the first valid post text, else fall back to raw user input
    image_prompt_base_text = next(
        (p["output"] for p in posts if p.get("output")),
        user_input
    )

    platform = next(iter(state.get("platforms", {}).keys()), "openai")
    model   = state.get("platforms", {}).get(platform, ["gpt-3.5-turbo"])[0]

    messages = build_image_prompt_creation_messages(
        user_input,
        image_prompt_base_text,
        for_realistic_image=True   # tell the builder we want realism
    )

    prompt = ask_openai(platform=platform, model=model, messages=messages)["output"]
    if not prompt:
        prompt = user_input

    # Trim to <100 words if necessary
    prompt = " ".join(prompt.split()[:99])

    return {"image_prompt_text_realistic": prompt}

# # --- Node: Generate Image using the LLM-generated prompt ---
# def generate_image(state: GraphState):
#     options = state.get("options", {})
#     image_prompt_text = state.get("image_prompt_text") # Get the LLM-generated prompt
    
#     if not image_prompt_text:
#         # print("No image prompt text available. Skipping image generation.")
#         return {"generated_image": {}}

#     # Define image generation parameters
#     image_model_to_use = "dall-e-3" # Or "gpt-image-1" if you have access and prefer
#     image_size = "1024x1024"
#     image_quality = "hd" # Can be "standard" or "hd"
#     num_images = 1 # DALL-E 3 only supports n=1

#     # print(f"Attempting to generate image with LLM-refined prompt: {image_prompt_text[:400]}...")
#     image_response = ask_openai(
#         platform="openai",
#         model=image_model_to_use,
#         messages=None,
#         generate_image=True,
#         image_prompt=image_prompt_text,
#         image_quality=image_quality
#     )

#     # print(f"Generated image result: {image_response}")
#     return {"generated_image": image_response}


# --- Node: Generate Image using the LLM-generated prompt ---
def generate_image(state: GraphState):
    options = state.get("options", {})
    image_prompt_text = state.get("image_prompt_text") # Get the LLM-generated prompt
    
    if not image_prompt_text:
        # print("No image prompt text available. Skipping image generation.")
        return {"generated_image": {}}

    # Define image generation parameters
    image_model_to_use = "dall-e-3"
    image_size = "1024x1024"
    image_quality = "hd"
    num_images = 1 # DALL-E 3 only supports n=1

    # print(f"Attempting to generate image with LLM-refined prompt: {image_prompt_text[:400]}...")
    
    # --- UPDATED FUNCTION CALL ---
    image_response = ask_openai(
        platform="openai",
        model=image_model_to_use,
        messages=None,
        generate_image=True,
        image_prompt=image_prompt_text,
        image_quality=image_quality,
        image_size=image_size,      # <-- ADDED: Pass the size
        n=num_images                # <-- ADDED: Pass the number of images
    )

    # print(f"Generated image result: {image_response}")
    return {"generated_image": image_response}


def generate_image_realistic(state: GraphState):
    prompt = state.get("image_prompt_text_realistic")
    if not prompt:
        return {"generated_image_realistic": {}}

    response = ask_openai(
        platform="openai",
        model="dall-e-3",
        messages=None,
        generate_image=True,
        image_prompt=prompt,
        image_quality="hd",
        image_size="1024x1024",
        n=1
    )
    return {"generated_image_realistic": response}

# # LangGraph setup
# graph = StateGraph(GraphState)

# # Define the nodes
# graph.add_node("generate_post", generate_text_post)
# graph.add_node("generate_image_prompt", generate_image_prompt) # New node
# graph.add_node("generate_image_1", generate_image)
# graph.add_node("generate_image_2", generate_image)# Renamed from generate_image_from_post

# # Define the sequence
# graph.set_entry_point("generate_post") # Start by generating text posts
# graph.add_edge("generate_post", "generate_image_prompt") # Then generate the image prompt
# graph.add_edge("generate_image_prompt", "generate_image") # Then use that prompt to generate the image
# graph.add_edge("generate_image", END) # Finally, end the graph

# # Compile the graph
# flow = graph.compile()

graph = StateGraph(GraphState)

graph.add_node("generate_post",                generate_text_post)
graph.add_node("generate_image_prompt",        generate_image_prompt)
graph.add_node("generate_image_prompt_real",   generate_image_prompt_realistic)
graph.add_node("generate_image",               generate_image)            # standard
graph.add_node("generate_image_realistic",     generate_image_realistic)  # new

# Flow
graph.set_entry_point("generate_post")

# After the post is ready, create both prompts
graph.add_edge("generate_post", "generate_image_prompt")
graph.add_edge("generate_post", "generate_image_prompt_real")

# Fan-out: generate images in parallel
graph.add_edge("generate_image_prompt",      "generate_image")
graph.add_edge("generate_image_prompt_real", "generate_image_realistic")

# Both images lead to END
graph.add_edge("generate_image",          END)
graph.add_edge("generate_image_realistic", END)

flow = graph.compile()

def run_generation_flow(payload: Dict):
    result = flow.invoke(payload)  # type: ignore
    # print(f"Final LangGraph flow result (from run_generation_flow): {result}")
    return result