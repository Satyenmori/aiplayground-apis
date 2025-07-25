from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes.handler import generate_post, generate_image, generate_caption

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.post("/generate-post")(generate_post)
app.post("/generate-image")(generate_image)
app.post("/generate-caption")(generate_caption)

# Run with: uvicorn main:app --reload
