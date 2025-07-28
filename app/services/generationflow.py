from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
from .openai_service import ask_openai
from .builders import build_post_prompt, build_image_prompt_creation_messages

# ---------------------------
# Step 1: Generate Text Posts
# ---------------------------
def generate_text_posts(input_text: str, options: Dict, platforms: Dict, history: List[Dict]) -> List[Dict]:
    results = []

    with ThreadPoolExecutor() as executor:
        futures = []    
        for platform, models in platforms.items():
            for model in models:
                messages = build_post_prompt(input_text, options, history)
                futures.append(
                    executor.submit(ask_openai, platform, model, messages)
                )

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results


# -----------------------------------
# Step 2a: Generate Image Prompt Text
# -----------------------------------
def generate_image_prompt(input_text: str, posts: List[Dict], platforms: Dict) -> str:
    base_text = next((p.get("output") for p in posts if p.get("output")), None)
    if base_text is None:
        base_text = input_text
    # print(f"Base text for image prompt: {base_text}")
    platform = next(iter(platforms.keys()), "openai")
    model = platforms.get(platform, ["gpt-3.5-turbo"])[0]

    messages = build_image_prompt_creation_messages(input_text, base_text)
    # print(f"Messages for image prompt: {messages}")
    response = ask_openai(platform, model, messages)
    # print(f"Generated image prompt: {response.get('output', input_text)}")
    return response.get("output", input_text)


# ------------------------------------------------
# Step 2b: Generate Realistic Image Prompt (Short)
# ------------------------------------------------
def generate_image_prompt_realistic(input_text: str, posts: List[Dict], platforms: Dict) -> str:
    base_text = next((p.get("output") for p in posts if p.get("output")), None)
    if base_text is None:
        base_text = input_text
    
    platform = next(iter(platforms.keys()), "openai")
    model = platforms.get(platform, ["gpt-3.5-turbo"])[0]
    # print(f"Base text for realistic image prompt: {base_text}")
    # print(f"Input text for realistic image prompt: {input_text}")
    messages = build_image_prompt_creation_messages(input_text, base_text, for_realistic_image=True)
    # print(f"Messages for realistic image prompt: {messages}")
    response = ask_openai(platform, model, messages)
    prompt = response.get("output", input_text)
    # print(f"Generated realistic image prompt: {prompt}")
    return prompt

# -------------------------------
# Step 3a: Generate Standard Image
# -------------------------------
def generate_image(prompt: str) -> Dict:
    if not prompt:
        return {}
    return ask_openai(
        platform="openai",
        model="dall-e-3",
        messages=None,
        generate_image=True,
        image_prompt=prompt,
        image_quality="hd",
        image_size="1024x1024",
        n=1
    )


# ---------------------------------
# Step 3b: Generate Realistic Image
# ---------------------------------
def generate_image_realistic(prompt: str) -> Dict:
    if not prompt:
        return {}
    return ask_openai(
        platform="openai",
        model="dall-e-3",
        messages=None,
        generate_image=True,
        image_prompt=prompt,
        image_quality="hd",
        image_size="1024x1024",
        n=1
    )


# ============================
# Master Function (Flow Runner)
# ============================
def run_generation_flow(payload: Dict) -> Dict:
    input_text = payload["input"]
    options = payload.get("options", {})
    platforms = payload.get("platforms", {})
    history = payload.get("history", [])

    # Step 1: Generate Text Posts
    posts = generate_text_posts(input_text, options, platforms, history)

    # Step 2: Generate Prompts (in parallel)
    image_prompt_text = None
    image_prompt_text_realistic = None

    if str(options.get("generate_image", "false")).lower() == "true":
        with ThreadPoolExecutor() as executor:
            future_standard = executor.submit(generate_image_prompt, input_text, posts, platforms)
            future_realistic = executor.submit(generate_image_prompt_realistic, input_text, posts, platforms)

            image_prompt_text = future_standard.result()
            # print(f"Generated image prompt text: {image_prompt_text}")
            image_prompt_text_realistic = future_realistic.result()
            # print(f"Generated realistic image prompt text: {image_prompt_text_realistic}")

        # Step 3: Generate Images (also in parallel)
        with ThreadPoolExecutor() as executor:
            future_image = executor.submit(generate_image, image_prompt_text)
            future_realistic_image = executor.submit(generate_image_realistic, image_prompt_text_realistic)

            generated_image = future_image.result()
            generated_image_realistic = future_realistic_image.result()
    else:
        generated_image = {}
        generated_image_realistic = {}

    return {
        "posts": posts, 
        "image_prompt_text": image_prompt_text,
        "image_prompt_text_realistic": image_prompt_text_realistic,
        "generated_image": generated_image,
        "generated_image_realistic": generated_image_realistic
    }
