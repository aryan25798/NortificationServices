from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import os

from app.routes import notifications
from app.notifier import process_notifications

app = FastAPI(title="Notification Service")

# Enable CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(notifications.router)

# Static directory path: ../static
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
static_dir = os.path.join(BASE_DIR, "static")

# Mount /static for JS, CSS, images
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html at root "/"
@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Start async background task on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_notifications())

# Optional health check route
@app.get("/health")
def health_check():
    return {"status": "Notification service is running"}
