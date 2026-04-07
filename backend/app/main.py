from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import video

app = FastAPI(title="Video Downloader API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, prefix="/api", tags=["video"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Video Downloader API is running"}
