from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes.handler import generate_post, generate_image, generate_caption
from app.social.oAuth import login, callback

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
app.get("/Xlogin")(login)
app.get("/Xcallback")(callback)
# Run with: uvicorn main:app --reload
