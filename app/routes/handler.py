from flask import request, jsonify
from app.utils import run_parallel_tasks
from app.services.openai_service import ask_openai
# from app.services.gemini_service import ask_gemini
# from app.services.anthropic_service import ask_anthropic

def create_task(platform, model, ask_fn, messages):
    def task():
        try:
            return ask_fn(platform, model, messages)
        except Exception as e:
            return {
                "platform": platform,
                "model": model,
                "error": str(e)
            }
    return task

def handle_task(default_platform, prompt_builder):
    data = request.get_json()
    platforms = data.get("platforms", {default_platform: ["gpt-4"]})
    core_input = data.get("input", "")
    options = data.get("options", {})
    history = data.get("history", [])

    tasks = []

    for platform, models in platforms.items():
        for model in models:
            ask_fn = {
                "openai": ask_openai,
                # "gemini": ask_gemini,
                # "anthropic": ask_anthropic
            }[platform]

            messages = prompt_builder(core_input, options, history)
            tasks.append(create_task(platform, model, ask_fn, messages))

    results = run_parallel_tasks(tasks)

    # Group by platform
    response = {p: [] for p in platforms}
    for r in results:
        if "platform" in r:
            response[r["platform"]].append(r)
        else:
            print("Warning: Missing platform in response", r)

    return jsonify({"response": response})
