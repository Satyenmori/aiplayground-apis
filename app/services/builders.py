from typing import List, Dict, Optional

def build_messages(system_prompt, user_input, options, history):
    messages = [{"role": "system", "content": system_prompt}]
    
    if options:
        opt_str = " | ".join(f"{k}: {v}" for k, v in options.items() if v)
        user_input = f"{user_input}\n\nOptions: {opt_str}"
    
    messages.extend(history or [])
    messages.append({"role": "user", "content": user_input})
    return messages

# def build_post_prompt(core, options, history):
#     system = "You are a marketing copywriter."
#     return build_messages(system, core, options, history)

def build_post_prompt(input_text: str, options: Dict, history: List[Dict]) -> List[Dict]:
    # Your existing build_post_prompt logic
    tone = options.get("tone", "neutral")
    length = options.get("length", "medium")
    system_message = f"You are a social media manager. Create a social media post with a {tone} tone and {length} length. Include relevant hashtags."
    user_message = f"Write a social media post about: {input_text}."

    messages = [{"role": "system", "content": system_message}]
    for chat_entry in history:
        messages.append({"role": chat_entry["role"], "content": chat_entry["content"]})
    messages.append({"role": "user", "content": user_message})
    return messages

def build_image_prompt_creation_messages(original_input: str, generated_text_post: str, for_realistic_image: bool = False) -> List[Dict]:
    """
    Builds a prompt to generate a concise image description (prompt)
    based on the original user input and the generated social media post.
    """
    if for_realistic_image:
        system_message = (
            "You are an expert prompt writer for photorealistic image models. "
            "Describe in detail a real-life scene that matches the user's topic and post, also use Real Humans with a real background, don't use any cartoonish background. "
            "Use concrete details (lighting, location, atmosphere, and the facial expression of the humans present) and stay under 100 words."
        )
    else:
        system_message = (
            "You are an AI assistant specialized in creating concise and effective prompts for image generation models like DALL-E. "
            "Your goal is to summarize the core visual concept from the given original request and the generated social media post into a short, descriptive image prompt. "
            "Focus on key elements that would make a compelling visual. "
            "The prompt should be specific, vivid, and less than 100 words."
        )

    # These lines should be OUTSIDE the if/else for system_message,
    # so they always execute after system_message is set.
    user_message = (
        f"Original user request: '{original_input}'\n\n"
        f"Generated social media post:\n---\n{generated_text_post}\n---\n\n"
        "Based on these, create a concise image generation prompt."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    # The return statement should also be at this level.
    return messages
    

def build_image_prompt(core, options, history):
    system = "You are an image generation assistant."
    return build_messages(system, core, options, history)

def build_caption_prompt(core, options, history):
    system = "You are a social media caption writer."
    return build_messages(system, core, options, history)
