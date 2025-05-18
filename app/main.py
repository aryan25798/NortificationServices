import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio

from app.routes import notifications
from app.notifier import process_notifications

app = FastAPI(title="Notification Service")

# BASE_DIR points to root directory (parent of 'app' folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /project-root/app
ROOT_DIR = os.path.dirname(BASE_DIR)  # /project-root
static_dir = os.path.join(ROOT_DIR, "static")

if not os.path.exists(static_dir):
    raise RuntimeError(f"Static directory not found: {static_dir}")

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
