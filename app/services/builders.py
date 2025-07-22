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

def build_post_prompt(core, options, history):
    tone = options.get("tone", "neutral")
    length = options.get("length", "medium")
    print(f"Building post prompt with tone: {tone}, length: {length}")
    # Instruction to the AI
    system = (
        "You are a professional marketing copywriter. "
        "Craft compelling, engaging social media posts. "
        f"Tone: {tone}. Length: {length}. Avoid hashtags unless essential."
    )

    user_prompt = f"Write a social media post about: {core.strip()}."
    print(f"User prompt: {user_prompt}")
    # Optional: Incorporate history if needed
    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    return messages


def build_image_prompt(core, options, history):
    system = "You are an image generation assistant."
    return build_messages(system, core, options, history)

def build_caption_prompt(core, options, history):
    system = "You are a social media caption writer."
    return build_messages(system, core, options, history)
