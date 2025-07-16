def build_messages(system_prompt, user_input, options, history):
    messages = [{"role": "system", "content": system_prompt}]
    
    if options:
        opt_str = " | ".join(f"{k}: {v}" for k, v in options.items() if v)
        user_input = f"{user_input}\n\nOptions: {opt_str}"
    
    messages.extend(history or [])
    messages.append({"role": "user", "content": user_input})
    return messages

def build_post_prompt(core, options, history):
    system = "You are a marketing copywriter."
    return build_messages(system, core, options, history)

def build_image_prompt(core, options, history):
    system = "You are an image generation assistant."
    return build_messages(system, core, options, history)

def build_caption_prompt(core, options, history):
    system = "You are a social media caption writer."
    return build_messages(system, core, options, history)
