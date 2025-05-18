import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio

from app.routes import notifications
from app.notifier import process_notifications

app = FastAPI(title="Notification Service")

# Static directory path - assuming 'static' folder is in the same directory as main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")

# Enable CORS - update allow_origins to your deployed frontend URL on Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-production-66a2.up.railway.app"],  # Your Railway frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(notifications.router)

# Mount /static for serving JS, CSS, images, etc.
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve React index.html at root
@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Start async background task on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_notifications())

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "Notification service is running"}
