from flask import Flask
from app.routes.handler import handle_task
from flask_cors import CORS
from app.services.builders import (
    build_post_prompt,
    build_image_prompt,
    build_caption_prompt,
)

app = Flask(__name__)
CORS(app)

@app.post("/generate-post")
def generate_post():
    return handle_task("openai", build_post_prompt)

@app.post("/generate-image")
def generate_image():
    return handle_task("openai", build_image_prompt)

@app.post("/generate-caption")
def generate_caption():
    return handle_task("openai", build_caption_prompt)

if __name__ == "__main__":
    app.run(debug=True)
