from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import os

from app.routes import notifications
from app.notifier import process_notifications

# Initialize FastAPI app
app = FastAPI(title="Notification Service")

# Enable CORS (adjust allowed origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(notifications.router)

# Mount static folder to serve frontend files
# Since app/ and static/ are siblings, go up one level then into static/
app.mount(
    "/",
    StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"), html=True),
    name="static"
)

# Run the notification processor on startup
@app.on_event("startup")
async def startup():
    asyncio.create_task(process_notifications())

# Health check endpoint (optional)
@app.get("/health")
def health_check():
    return {"status": "Notification service is running"}
