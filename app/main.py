from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import os

from app.routes import notifications
from app.notifier import process_notifications

app = FastAPI(title="Notification Service")

# Enable CORS (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your API routes
app.include_router(notifications.router)

# Mount /static to serve CSS, JS, images, etc.
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html at root "/"
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Run async notification processor on startup
@app.on_event("startup")
async def startup():
    asyncio.create_task(process_notifications())

# Optional health check
@app.get("/health")
def health_check():
    return {"status": "Notification service is running"}
